// Data source: Indeed's public RSS feed (/rss) and job-detail pages (/viewjob).
// The RSS endpoint is unauthenticated and explicitly allowed by robots.txt.
// Job detail extracts JSON-LD structured data (schema.org JobPosting) from
// the server-rendered page — no JavaScript execution required.

export const SEARCH_URL = "https://www.indeed.com/rss"
export const DETAIL_URL = "https://www.indeed.com/viewjob"

export function writeError(error: string, code: string): void {
  process.stderr.write(JSON.stringify({ error, code }) + "\n")
}

const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

/** Fetch text with exponential backoff on 429/5xx. Returns "" on a 404. */
export async function fetchWithRetry(url: string): Promise<string> {
  const maxRetries = 6
  let delay = 500
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url, {
      headers: {
        "User-Agent": UA,
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
      },
      redirect: "follow",
      signal: AbortSignal.timeout(15000),
    })
    if (response.status === 429 || response.status >= 500) {
      if (attempt === maxRetries) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`)
      }
      const jitter = Math.floor(Math.random() * 500)
      await new Promise((r) => setTimeout(r, delay + jitter))
      delay = Math.min(delay * 2, 8000)
      continue
    }
    if (response.status === 404) return ""
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status} ${response.statusText}`)
    }
    return response.text()
  }
  throw new Error("Request failed after max retries")
}

export interface JobCard {
  id: string
  title: string
  company: string | null
  location: string | null
  date: string | null
  url: string
}

export interface JobDetail extends JobCard {
  description: string | null
  employmentType: string | null
  salary: string | null
  datePosted: string | null
}

/** Extract the Indeed job key (jk) from a URL or bare 16-char hex key. */
export function extractJobKey(input: string): string | null {
  // From URL query string: ?jk=abc123… or &jk=abc123…
  const fromUrl = input.match(/[?&]jk=([a-f0-9]{8,})/)
  if (fromUrl) return fromUrl[1]
  // Bare key: typically 16 hex chars
  if (/^[a-f0-9]{8,}$/.test(input)) return input
  return null
}

function decodeXmlEntities(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&#[xX]([0-9a-fA-F]+);/g, (_, h) => String.fromCodePoint(parseInt(h, 16)))
}

function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim()
}

function clean(raw: string): string {
  return decodeXmlEntities(stripTags(raw)).trim()
}

/**
 * Extract the inner text of the first XML/HTML element matching <tag>.
 * Handles CDATA sections and nested angle brackets inside CDATA.
 */
function extractElement(xml: string, tag: string): string | null {
  const re = new RegExp(`<${tag}(?:\\s[^>]*)?>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?<\\/${tag}>`, "i")
  const m = re.exec(xml)
  return m ? m[1] : null
}

/**
 * Parse Indeed RSS XML into job cards. Splits on <item> boundaries so one
 * malformed entry cannot corrupt the rest. Company comes from <source>,
 * location is extracted from the description HTML when Indeed includes it.
 */
export function parseRSSFeed(xml: string): JobCard[] {
  const results: JobCard[] = []
  // Split on opening <item> tag — slice(1) drops the channel header
  const items = xml.split(/<item[\s>]/).slice(1)

  for (const item of items) {
    // Job key: prefer <link> over <guid> because link carries more URL params
    const rawLink =
      extractElement(item, "link") ??
      extractElement(item, "guid") ??
      ""
    const id = extractJobKey(decodeXmlEntities(rawLink.trim()))
    if (!id) continue

    // Title
    const rawTitle = extractElement(item, "title")
    if (!rawTitle) continue
    const title = clean(rawTitle)
    if (!title) continue

    // Company from <source> (Indeed puts employer name here)
    const rawSource = extractElement(item, "source")
    const company = rawSource ? clean(rawSource) || null : null

    // Date
    const rawDate = extractElement(item, "pubDate")
    const date = rawDate ? clean(rawDate) || null : null

    // Location: Indeed sometimes embeds it in description HTML as
    // <b>Location:</b> City, State  or  class="location">City, State<
    let location: string | null = null
    const rawDesc = extractElement(item, "description")
    if (rawDesc) {
      const locMatch =
        rawDesc.match(/<b>Location:<\/b>\s*([^<]+)/i) ??
        rawDesc.match(/class="location"[^>]*>\s*([^<]+)/i) ??
        rawDesc.match(/Location:\s*([A-Z][^<\n,]+(?:,\s*[A-Z]{2})?)/i)
      if (locMatch) location = clean(locMatch[1]) || null
    }

    results.push({
      id,
      title,
      company,
      location,
      date,
      url: `${DETAIL_URL}?jk=${id}`,
    })
  }

  return results
}

/**
 * Parse the JSON-LD JobPosting schema from an Indeed job-detail page.
 * Returns partial JobDetail — description, location, employmentType, salary,
 * datePosted. Falls back to Open Graph meta tags for missing fields.
 */
export function parseJobPage(html: string, id: string): JobDetail {
  let company: string | null = null
  let location: string | null = null
  let description: string | null = null
  let employmentType: string | null = null
  let salary: string | null = null
  let datePosted: string | null = null
  let title = "(untitled)"

  // 1. Try JSON-LD blocks (schema.org/JobPosting)
  const ldRe = /<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi
  let m: RegExpExecArray | null
  while ((m = ldRe.exec(html)) !== null) {
    let data: Record<string, unknown>
    try {
      data = JSON.parse(m[1]) as Record<string, unknown>
    } catch {
      continue
    }
    if (data["@type"] !== "JobPosting") continue

    // Title
    if (typeof data.title === "string") title = data.title.trim()

    // Company
    const org = data.hiringOrganization as Record<string, unknown> | undefined
    if (typeof org?.name === "string") company = org.name.trim()

    // Location
    const loc = data.jobLocation as Record<string, unknown> | undefined
    const addr = (loc?.address ?? {}) as Record<string, unknown>
    const city = (addr.addressLocality as string | undefined)?.trim() ?? ""
    const region = (addr.addressRegion as string | undefined)?.trim() ?? ""
    if (city || region) location = [city, region].filter(Boolean).join(", ")

    // Description
    if (typeof data.description === "string") {
      const withBreaks = data.description
        .replace(/<br\s*\/?>/gi, "\n")
        .replace(/<\/(p|li|ul|ol|div|h\d)>/gi, "\n")
      description = stripTags(withBreaks).replace(/\n{3,}/g, "\n\n").trim() || null
    }

    // Employment type
    if (typeof data.employmentType === "string") {
      employmentType = data.employmentType.replace(/_/g, " ").toLowerCase()
    }

    // Salary (baseSalary.value.{minValue, maxValue, unitText} + baseSalary.currency)
    const bs = data.baseSalary as Record<string, unknown> | undefined
    if (bs) {
      const val = bs.value as Record<string, unknown> | undefined
      const currency = (bs.currency as string | undefined) ?? "USD"
      if (val) {
        const min = val.minValue
        const max = val.maxValue
        const unit = (val.unitText as string | undefined) ?? "year"
        if (min !== undefined && max !== undefined) {
          salary = `${currency} ${min}–${max} / ${unit}`
        } else if (min !== undefined) {
          salary = `${currency} ${min}+ / ${unit}`
        }
      }
    }

    // Date posted
    if (typeof data.datePosted === "string") datePosted = data.datePosted

    break // use first matching JobPosting block
  }

  // 2. Fallback: Open Graph / meta title for company/title when JSON-LD absent
  if (title === "(untitled)") {
    const ogTitle = html.match(/<meta[^>]+property="og:title"[^>]+content="([^"]+)"/i)
    if (ogTitle) title = ogTitle[1].trim()
  }

  return {
    id,
    title,
    company,
    location,
    date: null,
    url: `${DETAIL_URL}?jk=${id}`,
    description,
    employmentType,
    salary,
    datePosted,
  }
}

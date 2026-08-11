import { SEARCH_URL, fetchWithRetry, parseRSSFeed, writeError, type JobCard } from "../helpers.js"

export interface SearchOpts {
  query?: string
  location: string
  fromage: number   // days posted within
  radius: number    // miles
  remote: boolean   // prepend "remote" to query
  page: number
  limit?: number
  format: "json" | "table" | "plain"
}

function buildUrl(opts: SearchOpts): string {
  const params = new URLSearchParams()

  // Merge remote flag into query so it works with RSS (no dedicated remote param)
  const q = [opts.remote ? "remote" : "", opts.query ?? ""].filter(Boolean).join(" ")
  if (q) params.set("q", q)
  params.set("l", opts.location)
  if (opts.fromage > 0 && opts.fromage < 9999) params.set("fromage", String(opts.fromage))
  if (opts.radius > 0) params.set("radius", String(opts.radius))
  params.set("sort", "date")
  // RSS pagination: start= (0-based, 10 per page)
  if (opts.page > 1) params.set("start", String((opts.page - 1) * 10))

  return `${SEARCH_URL}?${params.toString()}`
}

function renderTable(cards: JobCard[]): string {
  if (cards.length === 0) return "No results."
  const rows = cards.map((c) => {
    const title = (c.title || "").slice(0, 42).padEnd(42)
    const company = (c.company || "—").slice(0, 26).padEnd(26)
    const loc = (c.location || "—").slice(0, 24).padEnd(24)
    const date = (c.date || "—").slice(0, 29)
    return `${c.id.padEnd(18)} ${title} ${company} ${loc} ${date}`
  })
  const header =
    "ID".padEnd(18) +
    " " +
    "TITLE".padEnd(42) +
    " " +
    "COMPANY".padEnd(26) +
    " " +
    "LOCATION".padEnd(24) +
    " DATE"
  return [header, "-".repeat(header.length), ...rows].join("\n")
}

export async function runSearch(opts: SearchOpts): Promise<number> {
  try {
    const url = buildUrl(opts)
    const xml = await fetchWithRetry(url)
    if (!xml) {
      writeError("No results returned from Indeed RSS", "EMPTY_RESPONSE")
      return 1
    }

    // Indeed occasionally returns an HTML error page instead of RSS
    if (!xml.trimStart().startsWith("<?xml") && !xml.includes("<rss")) {
      writeError(
        "Indeed returned an unexpected response (possible rate-limit or block). Try again in a moment.",
        "NOT_RSS",
      )
      return 1
    }

    let cards = parseRSSFeed(xml)
    if (opts.limit !== undefined && opts.limit >= 0) cards = cards.slice(0, opts.limit)

    if (opts.format === "table") {
      process.stdout.write(renderTable(cards) + "\n")
    } else if (opts.format === "plain") {
      process.stdout.write(
        cards
          .map(
            (c) =>
              `${c.title}\n  ${c.company || "—"} · ${c.location || "—"} · ${c.date || "—"}\n  id: ${c.id}\n  ${c.url}`,
          )
          .join("\n\n") + "\n",
      )
    } else {
      process.stdout.write(
        JSON.stringify({ meta: { count: cards.length, page: opts.page }, results: cards }, null, 2) + "\n",
      )
    }
    return 0
  } catch (e) {
    writeError(e instanceof Error ? e.message : String(e), "SEARCH_FAILED")
    return 1
  }
}

import { describe, test, expect } from "bun:test"
import { parseRSSFeed, parseJobPage, extractJobKey } from "../src/helpers"

// --- Helpers ---

function rssItem(opts: {
  id?: string
  title?: string
  company?: string
  date?: string
  location?: string
}): string {
  const id = opts.id ?? "abc123def4567890"
  const title = opts.title ?? "Senior Software Engineer"
  const company = opts.company ?? "Acme Corp"
  const date = opts.date ?? "Thu, 31 Jul 2025 12:00:00 GMT"
  const loc = opts.location ?? "New York, NY"
  return `<item>
    <title>${title}</title>
    <link>https://www.indeed.com/viewjob?jk=${id}&amp;from=rss</link>
    <guid isPermaLink="false">https://www.indeed.com/viewjob?jk=${id}</guid>
    <source>${company}</source>
    <pubDate>${date}</pubDate>
    <description><![CDATA[<table><tr><td><b>Location:</b> ${loc}</td></tr></table>]]></description>
  </item>`
}

function rssWrap(items: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Indeed RSS</title>
  ${items}
</channel>
</rss>`
}

// --- extractJobKey ---

describe("extractJobKey", () => {
  test("extracts key from full URL with jk param", () => {
    expect(extractJobKey("https://www.indeed.com/viewjob?jk=abc123def4567890&from=rss")).toBe("abc123def4567890")
  })

  test("extracts key from URL with jk not first param", () => {
    expect(extractJobKey("https://www.indeed.com/viewjob?from=rss&jk=abc123def4567890")).toBe("abc123def4567890")
  })

  test("accepts bare hex key", () => {
    expect(extractJobKey("abc123def4567890")).toBe("abc123def4567890")
  })

  test("accepts short (8-char) hex key", () => {
    expect(extractJobKey("abcdef12")).toBe("abcdef12")
  })

  test("returns null for non-hex string", () => {
    expect(extractJobKey("not-a-key")).toBeNull()
  })

  test("returns null for empty string", () => {
    expect(extractJobKey("")).toBeNull()
  })
})

// --- parseRSSFeed ---

describe("parseRSSFeed", () => {
  test("parses a single item", () => {
    const xml = rssWrap(rssItem({ id: "aabbccddeeff0011" }))
    const cards = parseRSSFeed(xml)
    expect(cards).toHaveLength(1)
    expect(cards[0].id).toBe("aabbccddeeff0011")
    expect(cards[0].title).toBe("Senior Software Engineer")
    expect(cards[0].company).toBe("Acme Corp")
  })

  test("parses multiple items", () => {
    const xml = rssWrap(
      rssItem({ id: "aaaa111122223333", title: "Data Scientist" }) +
      rssItem({ id: "bbbb444455556666", title: "ML Engineer" }),
    )
    const cards = parseRSSFeed(xml)
    expect(cards).toHaveLength(2)
    expect(cards[0].title).toBe("Data Scientist")
    expect(cards[1].title).toBe("ML Engineer")
  })

  test("extracts location from description HTML", () => {
    const xml = rssWrap(rssItem({ location: "San Francisco, CA" }))
    const cards = parseRSSFeed(xml)
    expect(cards[0].location).toBe("San Francisco, CA")
  })

  test("preserves date field", () => {
    const xml = rssWrap(rssItem({ date: "Fri, 01 Aug 2025 00:00:00 GMT" }))
    const cards = parseRSSFeed(xml)
    expect(cards[0].date).toBe("Fri, 01 Aug 2025 00:00:00 GMT")
  })

  test("skips items with no job key", () => {
    const bad = `<item><title>No ID</title><link>https://indeed.com/jobs</link></item>`
    const xml = rssWrap(bad + rssItem({ id: "aabb1122ccdd3344" }))
    const cards = parseRSSFeed(xml)
    expect(cards).toHaveLength(1)
    expect(cards[0].id).toBe("aabb1122ccdd3344")
  })

  test("decodes XML entities in title", () => {
    const xml = rssWrap(rssItem({ title: "Senior Engineer &amp; Architect" }))
    const cards = parseRSSFeed(xml)
    expect(cards[0].title).toBe("Senior Engineer & Architect")
  })

  test("returns empty array for empty channel", () => {
    const xml = rssWrap("")
    expect(parseRSSFeed(xml)).toHaveLength(0)
  })

  test("constructs correct viewjob URL", () => {
    const xml = rssWrap(rssItem({ id: "aabb1122ccdd3344" }))
    const cards = parseRSSFeed(xml)
    expect(cards[0].url).toBe("https://www.indeed.com/viewjob?jk=aabb1122ccdd3344")
  })
})

// --- parseJobPage (JSON-LD extraction) ---

function jobPageHtml(opts: {
  title?: string
  company?: string
  city?: string
  region?: string
  description?: string
  employmentType?: string
  salary?: { min: number; max: number; currency?: string; unit?: string }
  datePosted?: string
}): string {
  const ld = {
    "@context": "http://schema.org",
    "@type": "JobPosting",
    title: opts.title ?? "Software Engineer",
    hiringOrganization: { "@type": "Organization", name: opts.company ?? "Tech Co" },
    jobLocation: {
      "@type": "Place",
      address: {
        "@type": "PostalAddress",
        addressLocality: opts.city ?? "New York",
        addressRegion: opts.region ?? "NY",
      },
    },
    description: opts.description ?? "<p>We are looking for a Software Engineer.</p>",
    employmentType: opts.employmentType ?? "FULL_TIME",
    datePosted: opts.datePosted ?? "2025-07-31",
    ...(opts.salary
      ? {
          baseSalary: {
            "@type": "MonetaryAmount",
            currency: opts.salary.currency ?? "USD",
            value: {
              "@type": "QuantitativeValue",
              minValue: opts.salary.min,
              maxValue: opts.salary.max,
              unitText: opts.salary.unit ?? "YEAR",
            },
          },
        }
      : {}),
  }
  return `<html><head><script type="application/ld+json">${JSON.stringify(ld)}</script></head><body></body></html>`
}

describe("parseJobPage", () => {
  test("extracts title from JSON-LD", () => {
    const job = parseJobPage(jobPageHtml({ title: "Staff ML Engineer" }), "abc")
    expect(job.title).toBe("Staff ML Engineer")
  })

  test("extracts company name", () => {
    const job = parseJobPage(jobPageHtml({ company: "OpenAI" }), "abc")
    expect(job.company).toBe("OpenAI")
  })

  test("combines city and region into location", () => {
    const job = parseJobPage(jobPageHtml({ city: "Seattle", region: "WA" }), "abc")
    expect(job.location).toBe("Seattle, WA")
  })

  test("strips HTML from description", () => {
    const job = parseJobPage(jobPageHtml({ description: "<p>Join our <b>team</b>!</p>" }), "abc")
    expect(job.description).toContain("Join our")
    expect(job.description).toContain("team")
    expect(job.description).not.toContain("<p>")
    expect(job.description).not.toContain("<b>")
  })

  test("normalises employmentType (underscores → spaces, lowercase)", () => {
    const job = parseJobPage(jobPageHtml({ employmentType: "FULL_TIME" }), "abc")
    expect(job.employmentType).toBe("full time")
  })

  test("extracts salary range", () => {
    const job = parseJobPage(
      jobPageHtml({ salary: { min: 150000, max: 200000 } }),
      "abc",
    )
    expect(job.salary).toBe("USD 150000–200000 / YEAR")
  })

  test("extracts datePosted", () => {
    const job = parseJobPage(jobPageHtml({ datePosted: "2025-08-01" }), "abc")
    expect(job.datePosted).toBe("2025-08-01")
  })

  test("returns (untitled) when no JSON-LD present", () => {
    const job = parseJobPage("<html><body>nothing here</body></html>", "abc")
    expect(job.title).toBe("(untitled)")
  })

  test("skips non-JobPosting JSON-LD blocks", () => {
    const html = `<html><head>
      <script type="application/ld+json">{"@type":"Organization","name":"Acme"}</script>
      <script type="application/ld+json">${JSON.stringify({ "@type": "JobPosting", title: "Real Job", hiringOrganization: { name: "Acme" }, description: "desc" })}</script>
    </head></html>`
    const job = parseJobPage(html, "abc")
    expect(job.title).toBe("Real Job")
  })
})

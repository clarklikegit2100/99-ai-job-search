import { DETAIL_URL, fetchWithRetry, parseJobPage, extractJobKey, writeError } from "../helpers.js"

export interface DetailOpts {
  id: string
  format: "json" | "plain"
}

export async function runDetail(opts: DetailOpts): Promise<number> {
  const key = extractJobKey(opts.id)
  if (!key) {
    writeError(
      `Could not parse a job key from "${opts.id}". Pass a 16-char hex key or a full Indeed viewjob URL.`,
      "BAD_ID",
    )
    return 1
  }

  try {
    const url = `${DETAIL_URL}?jk=${key}`
    const html = await fetchWithRetry(url)
    if (!html) {
      writeError("Job not found", "NOT_FOUND")
      return 1
    }

    const job = parseJobPage(html, key)

    if (opts.format === "plain") {
      const lines = [
        job.title,
        `${job.company || "—"} · ${job.location || "—"}`,
        "",
        job.employmentType ? `Employment: ${job.employmentType}` : "",
        job.salary ? `Salary: ${job.salary}` : "",
        job.datePosted ? `Posted: ${job.datePosted}` : "",
        "",
        job.description || "(no description)",
        "",
        `URL: ${url}`,
      ].filter((l) => l !== "")
      process.stdout.write(lines.join("\n") + "\n")
    } else {
      process.stdout.write(JSON.stringify(job, null, 2) + "\n")
    }
    return 0
  } catch (e) {
    writeError(e instanceof Error ? e.message : String(e), "DETAIL_FAILED")
    return 1
  }
}

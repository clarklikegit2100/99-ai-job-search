---
name: indeed-search
version: 1.0.0
description: >
  Use this skill to search for jobs on Indeed in any US city, state, or
  remote. Invoke for open positions, vacancies, and hiring across any
  sector or role. Trigger phrases: find jobs on indeed, indeed search,
  search indeed, indeed jobs, jobs in <city>, job openings near me.
context: fork
enabled: true  # set to false to keep installed but have /scrape skip it
allowed-tools: Bash(bun run .agents/skills/indeed-search/cli/src/cli.ts *)
---

# Indeed Search Skill

Search live job listings from Indeed's public RSS feed for **any US city
or region** (and remote). No authentication, no API key, and **zero
runtime dependencies** — runs with just `bun`.

> Indeed's RSS feeds are public and machine-readable. Keep request volume
> low and use only for personal job searching. Respect robots.txt — this
> skill reads only the public RSS endpoint (`/rss`) and individual job
> pages (`/viewjob?jk=…`), both of which are listed as allowed.

## When to use this skill

- Search for job openings in a US city, state, or "remote"
- Filter by recency (posted within N days) or work type (remote/hybrid/onsite)
- Get the full description of a specific Indeed listing

## Commands

### Search job listings

```bash
bun run .agents/skills/indeed-search/cli/src/cli.ts search --location "<place>" [flags]
```

Key flags:
- `--location <text>` / `-l <text>` — **required.** City, state, or "remote". e.g. `"New York, NY"`, `"San Francisco, CA"`, `"Remote"`.
- `--query <text>` / `-q <text>` — keywords (job title, skill, role). Recommended.
- `--fromage <days>` — posted within N days: `1`, `7`, `14`, `30`. Default: 14.
- `--remote` — filter to remote-only listings (appends "remote" to query).
- `--radius <miles>` — search radius in miles: `5`, `10`, `25`, `50`, `100`. Default: 25.
- `--page <n>` — page number (1-indexed, 10 results/page). Default 1.
- `--limit <n>` / `-n <n>` — cap results emitted (client-side).
- `--format json|table|plain` — default `json`.

### Fetch full job detail

```bash
bun run .agents/skills/indeed-search/cli/src/cli.ts detail <id|url> [--format json|plain]
```

`id` is the job key from search results (16 hex chars, e.g. `abc123def4567890`).
You may also pass a full Indeed `viewjob?jk=…` URL. Returns the full
description, employment type, and salary range when available.

## Usage examples

```bash
# ML Engineer roles in New York, last 14 days
bun run .agents/skills/indeed-search/cli/src/cli.ts search -q "machine learning engineer" -l "New York, NY" --fromage 14 --format table

# Remote data scientist roles, last 7 days
bun run .agents/skills/indeed-search/cli/src/cli.ts search -q "data scientist" -l "Remote" --fromage 7 --format table

# Software engineer in San Francisco, 50-mile radius
bun run .agents/skills/indeed-search/cli/src/cli.ts search -q "software engineer" -l "San Francisco, CA" --radius 50 --format table

# Full details for a specific job
bun run .agents/skills/indeed-search/cli/src/cli.ts detail abc123def4567890 --format plain
```

## Output formats

| Format | Best for |
|--------|----------|
| `json` | Default — programmatic use, passing IDs to `detail` |
| `table` | Quick human-readable scanning |
| `plain` | Reading a single job's full detail (`detail` command) |

All errors are written to **stderr** as `{ "error": "...", "code": "..." }` and
the process exits with code `1`.

## Notes

- Results come from Indeed's RSS endpoint — no credentials required.
- Page size is fixed at 10 results per page.
- Indeed may rate-limit; the CLI retries 429/5xx with exponential backoff.
- Job IDs are 16 hex characters (e.g. `abc123def4567890`) — pass as-is to `detail`.
- The `detail` command extracts structured data from JSON-LD on the job page.

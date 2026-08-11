# Search Queries for Job Scraper — Jian Zhao

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first.
Installed CLIs: `linkedin-search` (global), `indeed-search` (US), `freehire-search` (multi-market, tech-focused).

The `site:` query templates below are **WebSearch fallbacks** for company career pages or when a CLI is rate-limited.

**Sponsorship filter:** When using WebSearch fallbacks, add `"H-1B" OR "visa sponsorship"` to filter results
to companies more likely to sponsor.

## Query Categories

### Priority 1: AI Research Scientist / Applied Scientist (Healthcare AI / NLP / LLMs)

Core target — matches strongest experience and career direction.

```
# CLI (linkedin-search)
-q "AI research scientist healthcare" -l "Philadelphia, PA" --jobage 14
-q "applied scientist NLP healthcare" -l "Remote" --jobage 14
-q "research scientist LLM clinical" -l "New York, NY" --jobage 14
-q "applied scientist machine learning" -l "Philadelphia, PA" --jobage 14
-q "research scientist biomedical AI" -l "Remote" --jobage 14

# CLI (indeed-search)
-q "AI research scientist healthcare" -l "Philadelphia, PA" --fromage 14
-q "applied scientist NLP" -l "Remote" --fromage 14 --remote
-q "clinical NLP scientist" -l "New York, NY" --fromage 14
-q "research scientist LLM" -l "Philadelphia, PA" --fromage 14

# WebSearch fallback
site:linkedin.com/jobs "AI research scientist" "healthcare" ("H-1B" OR "sponsorship") "Philadelphia" OR "remote"
site:indeed.com "applied scientist" NLP healthcare "visa sponsorship"
```

### Priority 2: Machine Learning Engineer / AI Engineer (Healthcare / Biomedical)

Strong technical match — less research-focused but uses core ML skillset.

```
# CLI (linkedin-search)
-q "machine learning engineer healthcare" -l "Philadelphia, PA" --jobage 14
-q "AI engineer biomedical" -l "Remote" --jobage 14
-q "ML engineer NLP clinical" -l "New York, NY" --jobage 14
-q "senior ML engineer LLM" -l "Remote" --jobage 14

# CLI (indeed-search)
-q "machine learning engineer healthcare" -l "Philadelphia, PA" --fromage 14
-q "AI engineer LLM" -l "Remote" --fromage 14 --remote
-q "senior ML engineer biomedical" -l "New York, NY" --fromage 14

# CLI (freehire-search)
--query "machine learning healthcare" --remote --country us
```

### Priority 3: Research Scientist — Graph ML / Computer Vision / GNN

Matches PhD research directly — niche but high fit.

```
# CLI (linkedin-search)
-q "research scientist graph neural network" -l "Remote" --jobage 14
-q "computer vision research scientist" -l "Philadelphia, PA" --jobage 14
-q "graph machine learning scientist" -l "Remote" --jobage 14
-q "biomedical AI researcher" -l "Remote" --jobage 14

# WebSearch fallback
site:linkedin.com/jobs "graph neural network" "research scientist" remote
site:indeed.com "computer vision" "biomedical" "research scientist"
```

### Priority 4: Broader AI / Data Science (Adjacent Roles, Wider Net)

```
# CLI (linkedin-search)
-q "data scientist healthcare" -l "Philadelphia, PA" --jobage 14
-q "NLP engineer clinical" -l "Remote" --jobage 14
-q "AI scientist pharma" -l "Philadelphia, PA" --jobage 14
-q "computational scientist biomedical" -l "Remote" --jobage 14

# Target company career pages (via WebSearch):
site:amazon.jobs "applied scientist" NLP OR LLM
site:jobs.google.com "research scientist" "health"
site:microsoft.com/en-us/about/careers "research scientist" health AI
site:careers.pfizer.com "AI scientist" OR "ML scientist"
site:jobs.ibm.com "research scientist" healthcare NLP
```

## Target Companies (Known H-1B Sponsors in Healthcare AI)

High priority — known to sponsor H-1B and operate in healthcare AI:
- **Amazon (AWS Health, Alexa Health):** Applied Scientist, Senior Applied Scientist
- **Microsoft Research / Health AI:** Research Scientist
- **Google Health / DeepMind Health:** Research Scientist
- **IBM Research (Watson Health):** Research Scientist
- **Tempus AI:** AI Research Scientist
- **Flatiron Health:** Data Scientist / Research Scientist
- **Veeva Systems:** ML Engineer
- **Epic Systems:** AI / NLP Research roles
- **IQVIA:** AI / Data Scientist
- **Philips:** AI Research Scientist
- **GE HealthCare:** AI Scientist
- **Abridge:** ML Scientist (NLP / clinical notes)
- **Collate / PathAI / Paige.AI:** Biomedical AI Research
- **IFM Therapeutics / Recursion Pharma:** AI/ML Research Scientist

## Location Filter

Evaluate results against these tiers:
- **Ideal:** Philadelphia PA, Delaware, remote (anywhere US)
- **Acceptable:** NYC metro, Boston, DC area, Pittsburgh
- **Requires discussion:** Relocation to West Coast (San Francisco, Seattle)
- **Flag:** Requires in-person only without relocation support
- **H-1B:** Must always verify sponsorship — use myvisajobs.com or h1bdata.info

## Date Filter

Only include jobs posted within the last 14 days, or with deadline not yet passed.
Flag as "date unknown" if posting date cannot be determined.

---
framework_version: 1.1.0
---

# Job Evaluation Framework

## Eligibility Gate — run FIRST, before scoring

### H-1B Sponsorship (CRITICAL — run before any other gate)

Jian Zhao requires H-1B transfer sponsorship. This is a hard filter that must be checked before scoring any role.

**How to check:**
1. Look for explicit sponsorship language in the posting: "We sponsor visas," "H-1B sponsorship available," "international candidates welcome"
2. If silent: search the company name + "H-1B sponsorship" via WebSearch; check myvisajobs.com or h1bdata.info for the company's H-1B filing history
3. If the company has no H-1B filing history and no explicit statement, **flag as UNVERIFIED** — do not hard-fail, but note prominently

| Sponsorship status | Verdict |
|--------------------|---------|
| Company explicitly sponsors H-1B transfers | **PASS** — note as positive |
| Company has documented H-1B filings on record | **PROCEED** — likely fine, mention in application |
| Company is silent — no filing history found | **FLAG** — raise with user before applying |
| Company explicitly states "no sponsorship" | **FAIL — hard stop** |
| Government/federal agency (most cannot sponsor) | **FAIL unless explicitly noted otherwise** |

### Work Authorization Gate (standard)

Read the posting's eligibility section verbatim:

| Posting wording | Verdict |
|-----------------|---------|
| Requires US citizen or permanent resident | **FAIL — hard stop** |
| Requires security clearance | **FAIL** (clearance requires citizenship) |
| "H-1B sponsorship available" or "we sponsor" | **PASS** |
| Silent on work authorization | **PROCEED, verify H-1B separately above** |

---

## Scoring Dimensions

### 1. Technical Skills Match (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Core requirements are primary skills |
| 60–79 | Most requirements match, 1–2 learnable gaps |
| 40–59 | Partial match, significant upskilling needed |
| 0–39 | Fundamental mismatch |

**Strong match areas:** Biomedical AI, GNNs (PyTorch Geometric), LLMs (LLaMA, ChatGPT, Hugging Face), RAG, PEFT, Python, PyTorch, TensorFlow, Scikit-learn, clinical NLP, healthcare AI, computer vision (cell segmentation/tracking), HPC (MPI, OpenMP, GPU), graph databases (Neo4j, Milvus), Java, SQL

**Moderate match areas:** MLOps/production deployment, cloud platforms (AWS/Azure), Docker/Kubernetes, agentic AI workflows, large-scale distributed ML training, Spark/data engineering pipelines

**Weak match areas:** Reinforcement learning, robotics, financial ML, recommendation systems, pure frontend engineering

### 2. Experience Match (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Direct experience in same domain and role type |
| 60–79 | Related experience, transferable skills clear |
| 40–59 | Adjacent experience, would need to make the case |
| 0–39 | Unrelated experience |

**Strong:** Healthcare AI research (Temple), biomedical computer vision + GNN (DSU PhD), LLM application development (EMMA), enterprise software engineering (PetroChina), cross-institution research collaboration (Princeton/UCLA/LLNL)
**Moderate:** Clinical data analysis, public health ML, startup/entrepreneurship (Good Future LLC), project management (CAS)
**Entry-level:** Formal ML publications at top venues (ICML, NeurIPS, AAAI), production-scale ML systems, MLOps pipelines

### 3. Behavioral / Culture Fit (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Culture strongly matches behavioral preferences |
| 60–79 | Mixed signals but mostly compatible |
| 40–59 | Some friction areas |
| 0–39 | Significant culture mismatch |

**Strong behavioral fit:** Research-to-application roles, interdisciplinary teams, healthcare/biomedical focus, cross-functional collaboration with clinicians/domain experts, technically rigorous environments, roles where industry experience is valued alongside research

**Potential friction:** Pure product-velocity engineering cultures with no research component, highly specialized narrow-domain teams (Jian's breadth is a strength but may read as unfocused to some), environments that devalue non-top-tier PhD credentials

**Red flags to research:** Companies that don't value the industry + research combination, environments requiring US citizenship or clearance, cultures where academic pedigree (MIT/Stanford) dominates hiring decisions over actual skill and experience

### 4. Location & Logistics (Pass/Fail + Notes)

- Philadelphia metro / Delaware area: **PASS** (current base)
- NYC metro (2h or less): **PASS**
- Boston, DC area: **PASS** (with relocation consideration)
- Fully remote: **PASS** (strongly preferred)
- Requires relocation to West Coast without strong package: **FLAG** (discuss with user)
- Requires security clearance: **FAIL**

### 5. Career Alignment & Motivation (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Strongly aligned with career direction, clear growth path |
| 60–79 | Good role but only partially aligned |
| 40–59 | Decent but doesn't build toward goals |
| 0–39 | Dead end or backwards step |

**Career goals:**
- Secure a full-time research scientist or applied scientist role in healthcare AI, clinical NLP, or LLM applications
- Leverage the interdisciplinary background (biomedical + graph ML + LLMs + engineering) in a production-impact environment
- Progress toward senior/staff research scientist, building publications and industry impact in parallel
- Establish green card process post-hire

**Motivation filter — energizing tasks:**
- Building LLM/RAG systems for real-world healthcare applications
- Graph neural network research on biomedical data
- Multi-institution research collaborations
- Translating research prototypes into deployable systems

**Motivation filter — draining tasks:**
- Pure software engineering with no research component
- Bureaucratic academic environments with slow publication cycles and no product impact
- Roles without a clear path to meaningful AI research contribution

### 6. Salary Benchmark (Optional)

If `salary_data.json` is configured, run:
```bash
python salary_lookup.py "<Company Name>" --json
```

If unconfigured, skip. Target salary context: $150K–$200K base for Research Scientist / Applied Scientist level.

---

## Output Format

```
## Job Fit Evaluation: [Role] at [Company]

### H-1B / Work Authorization
[PASS / FAIL / FLAG — with specific evidence]

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical Skills | XX/100 | [brief note] |
| Experience Match | XX/100 | [brief note] |
| Behavioral Fit | XX/100 | [brief note] |
| Location | PASS/FAIL | [brief note] |
| Career Alignment | XX/100 | [brief note] |

**Overall Score: XX/100**

### Verdict: [Strong Fit / Good Fit / Moderate Fit / Weak Fit / Poor Fit]

### Key Strengths for This Role
- [bullet points]

### Gaps to Address
- [bullet points]

### Recommendation
[1–2 sentences: apply/skip/apply with caveats, including H-1B note]
```

## Weighting
- Technical Skills: 30%
- Experience Match: 25%
- Behavioral Fit: 15%
- Career Alignment: 30%

(Location and H-1B are pass/fail gates, not weighted)

## Thresholds
- **Strong Fit** (75+): Definitely apply
- **Good Fit** (60–74): Apply, address gaps in cover letter
- **Moderate Fit** (45–59): Consider carefully
- **Weak Fit** (30–44): Probably skip
- **Poor Fit** (<30): Skip

## Hard Deal-breakers (auto-fail regardless of score)
- Company does not sponsor H-1B and no exception route exists
- Requires US citizenship or security clearance
- Role is pure non-AI software engineering (Java/backend only, no ML/AI component)
- Location requires relocation without willingness to discuss

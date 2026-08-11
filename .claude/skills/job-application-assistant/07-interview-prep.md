---
framework_version: 1.0.0
---

# Interview Preparation — Jian Zhao

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome). Keep to 1–2 minutes. End with what you learned.

## Ready-Made STAR Examples

### 1. EMMA Healthcare Assistant — Temple University (LLM / RAG / Healthcare AI)
**S:** Temple's public health team needed a tool to connect postpartum-depression patients with locally relevant mental health resources — a fragmented landscape where patients often couldn't navigate to the right services.
**T:** As the AI research scientist on the project, I was responsible for the full system design and implementation of an LLM-based conversational assistant.
**A:** Built EMMA using LLaMA and ChatGPT with PEFT (parameter-efficient fine-tuning) for domain adaptation, RAG with Milvus and Neo4j for knowledge retrieval, and Flowise for workflow orchestration. Front-end via Gradio and Streamlit for clinical staff to interact with. Designed the data pipeline from EHR sources, environmental data, and public health repositories.
**R:** Delivered a working prototype used in the research setting; contributed to manuscripts and grant proposals for continued funding. The system demonstrated how LLM + RAG architecture can serve healthcare navigation tasks with locally-grounded knowledge.
**Use for:** "Tell me about an LLM/RAG project you built," "Healthcare AI experience," "Full-stack AI system design"

---

### 2. Biomedical Cell Tracking — Delaware State University (GNN / Computer Vision)
**S:** Biomedical researchers at DSU needed automated tools to segment, track, and quantify cells in microscopy images — a labor-intensive manual process that limited experiment throughput.
**T:** As PhD researcher, I led the development of CNN/GNN-based approaches for automated cell segmentation, tracking, and quantification.
**A:** Applied CNNs for image segmentation (watershed methods, diffusion-tensor imaging concepts), developed GNN architectures to model cell relationships across time frames, and built a rapid-tuning approach for CSTQ parameters to make workflows reproducible and accessible to domain scientists without deep ML expertise.
**R:** Produced a rapid-tuning framework that supports reproducible biomedical image-analysis workflows; work contributed to PhD research output and disease-research applications. Demonstrates practical ML deployment in a specialized scientific domain.
**Use for:** "Graph neural network experience," "Computer vision research," "Tell me about your PhD research"

---

### 3. HPC Cluster Build and Research — Delaware State University (Infrastructure / Scale)
**S:** The nano-bio spectroscopy research group at DSU had no dedicated compute infrastructure for large-scale plasma and molecular simulations, limiting the scope and speed of experiments.
**T:** As graduate research assistant, I was responsible for procuring, building, and administering the group's research HPC cluster.
**A:** Designed and built a cluster with 1 head node, 8 compute nodes, 320 CPUs, and 512 GB RAM. Configured job scheduling, LUSTRE distributed storage, and inter-node MPI communication. Ran large-scale OSIRIS and GROMACS simulations in collaborations with Princeton, UCLA, and Lawrence Livermore National Laboratory.
**R:** Enabled research collaborations with three national-caliber institutions. The cluster supported several years of simulation research that would not have been feasible on shared university resources.
**Use for:** "Experience with large-scale computation," "Infrastructure for research," "Cross-institution collaboration"

---

### 4. Hypertension Prediction ML — Temple University (Healthcare ML / Analytics)
**S:** Public health researchers at Temple had ambulatory-visit data from a diverse patient population and suspected significant gaps in blood-pressure and A1C monitoring, but lacked a systematic way to identify and quantify these gaps.
**T:** I was responsible for the ML modeling and analysis to surface these patterns and build predictive models.
**A:** Applied Random Forest, XGBoost, and SVM to the ambulatory-visit dataset. Designed the feature engineering pipeline, ran model comparison experiments, and produced interpretable outputs that could inform clinical recommendations.
**R:** Identified concrete monitoring gaps in the patient population; results contributed to research manuscripts and grant proposals for continued public health research.
**Use for:** "Healthcare data analysis," "Applied ML experience," "Clinical ML without PhD publications yet"

---

### 5. PetroChina Energy Forecasting — Industry ML Before Academia (Business Impact)
**S:** PetroChina's planning institute needed accurate energy-consumption forecasting for natural-gas pipeline operations to support strategic capacity planning.
**T:** As senior software engineer, I was asked to build an ML-based forecasting system to replace manual estimation methods.
**A:** Developed BP neural-network and decision-tree models (using MATLAB, Java, SQL, and Weka) trained on historical pipeline operational data. Built and validated an M/M/C queuing model for vehicle fleet allocation optimization alongside the forecasting models.
**R:** Achieved approximately 90% forecasting accuracy on the test set, significantly above the manual baseline. The model was used for strategic planning analyses across the institute.
**Use for:** "You have industry ML experience before your PhD," "How does your industry background inform your research?"

---

## STAR Candidates (Complete Manually)

### Publications and Manuscripts
**Source:** Temple University research (2023–2025) — contributed to manuscripts
**What happened:** Participated in writing research results from EMMA and hypertension research
**Why it matters:** Demonstrates research writing, scientific rigor, contribution to the academic record
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result: (add specific paper titles, venues, and your contribution)

---

## Common Tough Questions

### "Your PhD is from Delaware State — how does that compare to stronger research programs?"
> The credential that matters for my positioning is Tsinghua University for my M.E. — a top-3 university in China — alongside two U.S. master's and a U.S. Ph.D. More importantly, the work speaks for itself: multi-institution HPC collaborations with Princeton, UCLA, and Lawrence Livermore; a healthcare AI system built and deployed at Temple; and industry experience shipping production software at PetroChina. I'm positioned as an interdisciplinary AI researcher with engineering depth, not as a traditional academic.

### "You have an H-1B — does that create risk for us?"
> H-1B transfer is a straightforward process that takes 2–4 weeks for a premium processing petition. Many top AI research companies regularly sponsor H-1B transfers. I've done this before and it's a standard transition. Happy to walk through the specifics of how it works.

### "Your experience spans a lot of domains — what do you actually specialize in?"
> The through-line is AI for complex systems with real-world constraints — specifically biomedical AI and healthcare NLP. Whether it's GNNs for cell tracking, LLMs for postpartum-depression support, or ML for clinical monitoring gaps, the application domain is healthcare and life sciences. The breadth in CV/HPC is a toolset that came from the research, not a lack of focus.

### "Why did you go back to PhD after 10+ years in industry?"
> I had always wanted to work on AI research problems with real scientific depth. After building production software at PetroChina and CAS, I came to the U.S. specifically to pursue research at the frontier of biomedical AI and machine learning. The combination of industry and research is intentional — I can build things that actually work, not just publish theoretical results.

---

## Questions to Ask Interviewers

### Role / Team
- What does the research-to-production pipeline look like for applied scientists here?
- How does the team balance publications/research with product delivery?
- What are the most important ML problems the team is working on in the next 12 months?

### Culture / Growth
- How are applied scientists and engineers expected to collaborate?
- What does mentorship and career development look like for research-track roles?
- Does the company sponsor H-1B / green card for international employees?

### Domain
- What clinical or healthcare data does the team have access to?
- How does the organization handle data privacy and IRB considerations for research?

## Salary Expectations
Target: $150,000–$200,000 base depending on role level (Research Scientist vs. Senior / Staff). Total compensation including equity/bonus: $180,000+. Flexible for the right research environment.

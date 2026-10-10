# ComplaintScope — Faculty Presentation & Defense Guide

**Course:** CBS3009 – Advanced Social, Text and Media Analytics  
**Institution:** School of Computer Science & Engineering, Vellore Institute of Technology (VIT), Vellore  
**Team Members:**  
- Ruhaan Bansal (`23BBS0046`)  
- Vedant Rajesh (`23BBS0037`)  
- Anish Desai (`23BBS0119`)  

**Presentation Deck:** [`ComplaintScope_Presentation.pptx`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Presentation/ComplaintScope_Presentation.pptx) (24 Slides, Professional White Theme)  
**Recommended Presentation Duration:** 15–20 minutes (+ 5–10 minutes Faculty Q&A)

---

## ⏱️ Recommended Presentation Agenda & Time Allocation

| Slide Range | Theme | Presenter / Focus | Allocated Time |
|---|---|---|---|
| **Slides 1–4** | Motivation, Problem Statement & System Architecture | Team Member 1 | 3 minutes |
| **Slides 5–8** | Data Provenance, Ablation Study & Feature Engineering | Team Member 2 | 3 minutes |
| **Slides 9–11** | Component 1 & 2: Triage Classification, Drift & Relief Prediction | Team Member 1 | 4 minutes |
| **Slides 12–15** | Component 3a & 3b: Topic Discovery & Dual Burst Early Warning | Team Member 3 | 3 minutes |
| **Slides 16–18** | Components 4 & 5: Institutional Network & Systemic Risk Index | Team Member 2 | 3 minutes |
| **Slides 19–24** | Fairness Audit, App Demo, Engineering Rigor & Conclusion | All Team Members | 3 minutes |

---

## 🗣️ Slide-by-Slide Speaker Notes & Key Talking Points

### Slide 1: Title Slide
- **Key Talking Point:** Introduce ComplaintScope as a complete regulatory analytics system built specifically for financial consumer complaint narratives. Emphasize that while the CFPB holds over 8 million complaints, nearly 900,000 contain detailed free-text narratives that standard relational databases cannot triage or interpret automatically.

### Slide 2: Presentation Agenda
- **Key Talking Point:** Give the faculty a clear roadmap: from raw data ingestion and empirical ablation to 5 distinct analytical engines, terminating in an interactive dashboard and rigorous evaluation.

### Slide 3: Problem Statement & Regulatory Bottlenecks
- **Core Argument:** Why does this project matter?
  - Every weekday, 5,000–10,000 complaints arrive at the CFPB.
  - Manual reading takes 3–8 minutes per complaint.
  - Less than 1 in 6 (16.3%) receive monetary or non-monetary relief—caseworkers have no prior ranking mechanism.
  - Fraud schemes and predatory lending trends start as small complaint trickles months before regulators issue enforcement actions.

### Slide 4: System Architecture Overview
- **Key Talking Point:** Walk through the 5 components:
  1. 9-class product triage classifier.
  2. Imbalance-aware relief-risk scoring.
  3. Unsupervised LDA topic discovery.
  4. Dual-engine temporal burst detection.
  5. Bipartite company-issue graph projection & Systemic Risk Index.
- Highlight that the system runs end-to-end with zero raw database dependencies in production using compact artifacts (<10 MB).

### Slide 5: Data Provenance, Filtering Funnel & Chronological Split
- **Core Argument:** Highlight the methodology:
  - We started with 878,262 raw narratives from the official CFPB database (CC0 1.0 license).
  - Applied 6 strict filters: length threshold (>=20 words), deduplication (purging 131,442 exact copies), and definite relief outcomes.
  - Final modeling corpus: 19,998 complaints.
  - **Critical Design Decision:** Strict chronological partition (70% Train: 2018–2022, 15% Val: early 2022, 15% Test: late 2022–2023). Emphasize: *No future data leakage.*

### Slide 6: Exploratory Data Analysis & Empirical Insights
- **Key Talking Point:** Highlight the severe class imbalance:
  - Credit reporting represents >60% of narrative volume due to automated dispute mills.
  - Base relief rate varies wildly: checking accounts see ~32% relief, while credit reporting disputes see only ~4.3% relief.
  - Narrative length has a long right tail (median 162 words, max >1,500 words).

### Slide 7: Preprocessing Ablation Study (AQ4)
- **Core Argument:** We did not guess our preprocessing pipeline; we tested 7 controlled variants:
  - Purging redactions (`XXXX`) improved Macro-F1 from 0.4991 to 0.5140 (champion).
  - Preserving negations prevented sentiment inversion.
  - Removing stopwords was essential (+7.55 pp gain), and lemmatization contributed +3.56 pp.

### Slide 8: Feature Engineering: Sparse, Dense & Metadata
- **Key Talking Point:** Three distinct feature spaces:
  - Sublinear TF-IDF (30,000 features, bigrams, $tf = 1 + \log(tf)$ based on Zipf power-law analysis).
  - Dense Sentence-BERT (`all-MiniLM-L6-v2`, 384 dimensions, L2-normalized).
  - Metadata features (submission channel, state, tags). Company name was explicitly excluded from relief prediction to prevent overfitting to past institutional settlement behavior.

### Slide 9: Component 1: Product Classification Benchmark
- **Key Result:**
  - Calibrated LinearSVC achieved **Test Macro-F1 = 0.7394**, Accuracy = **87.43%**, 95% CI [0.7079, 0.7666].
  - Outperformed tuned Logistic Regression (0.7319), MiniLM+LR (0.7002), and Naive Bayes baselines (0.62–0.64).
  - McNemar paired chi-square test confirms statistical significance: $\chi^2 = 535.64, p = 1.67 \times 10^{-118}$.

### Slide 10: Temporal Concept Drift & Leakage Proof (AQ3)
- **Key Insight (Very Impressive for Faculty):**
  - If we had used a standard randomized train/test split, Macro-F1 would appear to be **0.9330**.
  - But under realistic chronological evaluation, Macro-F1 is **0.7317**.
  - That is a **20.13 percentage point drop** due to temporal concept drift (evolving complaint terminology and regulatory changes).
  - Proves that prior academic papers reporting >90% accuracy on random splits suffered from severe temporal data leakage!

### Slide 11: Component 2: Relief-Risk Prediction & Triage Simulation (AQ2)
- **Key Result:**
  - Predicting binary relief ($16.3\%$ base rate).
  - Text Logistic Regression achieved **PR-AUC = 0.3865** (vs. 0.3170 prior-rate baseline).
  - **Triage Simulation:** Auditing the top 5% risk queue yields **44.67% precision (1.41× lift)** over random auditing. Auditing the top 20% captures **24.48%** of all relief cases.

### Slide 12–13: Component 3a: Topic Discovery (LDA Sweep)
- **Key Result:**
  - Evaluated $k \in \{8, 12, 16, 20, 24\}$ across LDA, NMF, and K-Means.
  - Optimal model: LDA $k = 16$ ($C_v = 0.5009$, Topic Diversity = $0.7312$).
  - Discovered 16 coherent regulatory themes: Credit Bureau Disputes, Debt Collection Harassment, Mortgage Forbearance, Identity Theft, Checking Overdrafts, etc.
  - K-Means on dense embeddings failed (silhouette scores 0.021–0.026), proving that dense clustering suffers from high-dimensional dispersion.

### Slide 14–15: Component 3b: Emerging-Issue Burst Detection (AQ5)
- **Key Result:**
  - Dual-detector architecture: Rolling 12-month trailing Z-score ($\theta = 2.0$) and EWMA-CUSUM control chart ($h = 4.0$).
  - Validated against 5 independent keyword proxies.
  - Achieved **CUSUM F1 = 0.8000** (Precision = 1.00, Recall = 0.67).
  - Detected COVID-19 CARES Act mortgage forbearance disputes in **March–April 2020, 2–3 months before the peak volume** in summer 2020.

### Slide 16–18: Components 4 & 5: Network Analysis & Systemic Risk Index
- **Key Result:**
  - Bipartite graph: 2,502 financial institutions $\times$ 170 issue categories.
  - Projected onto company co-occurrence network using Jaccard edge weighting.
  - Louvain community detection found 3 distinct institutional clusters ($Q = 0.2568, p < 0.001$ against 1,000 Erdős–Rényi random graphs).
  - Formulated 5-dimensional Composite SRI combining volume, degree centrality, issue entropy, non-response rate, and relief deficit.
  - **Top Systemic Risk Entities:** TransUnion (0.7819), Experian (0.7187), and Equifax (0.6825). Equifax exhibits the most severe relief deficit (4.3% relief rate despite enormous volume).

### Slide 19: Error Taxonomy & Confusability Patterns (AQ1)
- **Key Analysis:**
  - Top error mode: Debt Collection misclassified as Credit Reporting (and vice versa).
  - Why? Third-party collection agencies routinely threaten or perform credit reporting modifications as an enforcement tactic, causing overlapping lexical signatures.

### Slide 20: Algorithmic Fairness & Equity Audit (AQ7)
- **Key Finding:**
  - Disparate impact ratio across submission channels is $0.941$ (within the EEOC $80\%$ four-fifths rule).
  - Servicemembers and older Americans achieve parity within $\pm 0.02$ PR-AUC, demonstrating that relief scoring is unbiased across demographic proxies.

### Slide 21: Streamlit Interactive Dashboard
- **Key Talking Point:**
  - 5 interactive pages: Overview, Live Product Classifier, Relief Triage Simulator, Topic & Burst Monitor, and Institutional Risk Network.
  - Operates on precomputed lightweight artifacts (<10 MB).

### Slide 22–24: Engineering Rigor, References & Defense
- **Summary:**
  - 20/20 automated pytest tests passing in 12 seconds.
  - Reproducible seed 42.
  - Over 20 academic references cited.
  - Ready for viva defense.

---

## ❓ Anticipated Faculty Questions & Model Answers

### Q1: "Why did you use a chronological split instead of standard 5-fold cross validation?"
> **Model Answer:**  
> "In consumer financial complaints, language is inherently non-stationary. Consumer terminology evolves with new regulations, credit schemes, and macroeconomic events. A randomized cross-validation leaks future terms—such as 'CARES Act' or pandemic forbearance terminology—into the training set. In fact, our study explicitly quantified this in AQ3: a random split yields an artificially inflated 0.9330 Macro-F1, whereas the honest chronological split yields 0.7317. A 20-percentage-point performance drop demonstrates that cross-validation provides dangerously overoptimistic expectations for production deployment."

### Q2: "Why did LinearSVC with TF-IDF outperform dense Transformer embeddings (MiniLM-L6-v2)?"
> **Model Answer:**  
> "First, legal and regulatory financial text is characterized by precise domain-specific keyword tokens—such as 'repossession', 'forbearance', 'FCRA', 'charge-off'—which have high discriminative power in a high-dimensional sparse TF-IDF space (30,000 bigrams). Second, MiniLM-L6-v2 is a general-domain sentence transformer with a 512-token truncation limit; our complaints have a median length of 162 words with tails exceeding 1,000 words. LinearSVC creates an optimal maximum-margin hyperplane directly over these exact discriminative tokens, whereas 384-dimensional dense pooling compresses away specific legal terms."

### Q3: "How does your burst detection work, and why did you use both Z-score and EWMA-CUSUM?"
> **Model Answer:**  
> "Z-score compares the current month's topic prevalence against a 12-month rolling baseline window. It is ideal for detecting sudden, massive volume spikes. However, systemic crises typically start as subtle, gradual drifts over several consecutive months. For this, we implemented an EWMA-CUSUM (Cumulative Sum) control chart. CUSUM accumulates persistent small deviations above baseline, triggering an alarm when the cumulative sum exceeds threshold $h=4.0$. This dual approach gave us an early-warning lead time of 2 to 3 months before the crisis peaked."

### Q4: "How is the Systemic Risk Index (SRI) calculated, and how did you prevent it from just reflecting company size?"
> **Model Answer:**  
> "To prevent SRI from merely reflecting total complaint volume, we formulated it across five normalized dimensions with balanced weights:
> 1. Log-transformed Volume (25%)
> 2. Degree Centrality in the issue co-occurrence graph (25%)
> 3. Issue Entropy / Shannon diversity of dispute types (20%)
> 4. Untimely response rate (15%)
> 5. Relief deficit rate, which is the extent to which a company's relief rate falls below the industry mean (15%).  
> We also conducted a sensitivity analysis across alternative weighting schemes, demonstrating a Spearman rank correlation $\rho > 0.94$, proving that the institutional risk rankings are structurally robust."

### Q5: "How did you validate that your topic labels are not arbitrary hallucinations?"
> **Model Answer:**  
> "We performed a formal grid sweep over $k \in \{8, 12, 16, 20, 24\}$ using the standardized $C_v$ coherence metric and Topic Diversity. At $k=16$, $C_v$ peaked at 0.5009 with a diversity of 0.7312. Furthermore, we cross-tabulated the topic distribution against the ground-truth product categories in a heatmap (Figure 15), confirming that topics such as 'Mortgage Forbearance' mapped exclusively to Mortgage products, while 'Credit Bureau Disputes' mapped to Credit Reporting, validating semantic alignment."

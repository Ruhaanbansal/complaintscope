# ComplaintScope: Slide Presentation Deck
**Course:** CBS3009 – Advanced Social, Text and Media Analytics (20 Marks)  
**Project Title:** ComplaintScope: An End-to-End Text, Topic & Network Analytics System for Consumer-Complaint Triage and Early Warning  
**Team:** Ruhaan Bansal (23BBS0046) | Vedant Rajesh (23BBS0037) | Anish Desai (23BBS0119)  
**Faculty Guide:** Prof. Sathish Kumar K | School of Computer Science & Engineering | VIT Vellore  
**Date:** October 2026 | **Slides:** 22 Slides (Widescreen 16:9)

---

### Slide 1: Title Slide
- **Title:** COMPLAINTSCOPE
- **Subtitle:** An End-to-End Text, Topic & Network Analytics System for Consumer-Complaint Triage and Systemic Risk Early Warning
- **Context:** CBS3009 Course Project | VIT Vellore
- **Authors:** Ruhaan Bansal (23BBS0046), Vedant Rajesh (23BBS0037), Anish Desai (23BBS0119)
- **Faculty Guide:** Prof. Sathish Kumar K

---

### Slide 2: Problem Context & Operational Motivation
- **The Triage Bottleneck:** CFPB receives >8M consumer complaints, with thousands of detailed unstructured narratives daily. Manual routing to specialized product divisions is slow and inconsistent.
- **The Relief-Risk Gap:** Only 16.3% of complaints result in monetary or non-monetary consumer relief. Caseworkers lack probabilistic risk scoring to prioritize investigations.
- **Early Warning & Network:** Emerging systemic crises (e.g., CARES Act COVID forbearance disputes) appear in narratives months before official regulatory actions. Cross-institutional complaint networks expose systemic financial hazard clusters.

---

### Slide 3: System Architecture & End-to-End Pipeline
- **Component 1 (Phase 4):** 9-Class Product Classification Suite across 7 models with bootstrap CIs.
- **Component 2 (Phase 5):** Imbalance-Aware Consumer Relief Risk Prediction & Queue Simulation.
- **Component 3a (Phase 6):** Unsupervised Topic Discovery (LDA vs NMF vs KMeans) with coherence sweep.
- **Component 3b (Phase 7):** Dual-Detector Emerging Issue Detection (Z-Score + EWMA-CUSUM).
- **Component 4 & 5 (Phases 8-9):** Bipartite Network Projection, Louvain Communities & Systemic Risk Index (SRI).
- **Engineering Rigor:** Chronological splits (70/15/15), train-only vocabulary fitting, empirical preprocessing ablation, 19/19 pytest suite passing, and Streamlit dashboard (<10MB artifacts).

---

### Slide 4: Data Provenance, Filtering Funnel & Chronological Partitions
- **Source & Provenance:** Official CFPB Consumer Complaint Database (CC0 1.0 Public Domain). Hugging Face mirror archive (SHA-256 recorded).
- **Filtering Funnel:** Non-null narratives >= 20 words, 131,442 exact duplicates purged, definite relief labels retained. Harmonized to 9 consolidated classes.
- **Final Modeling Corpus:** 19,998 narrative complaints spanning 2018–2023.
- **Chronological Partitions:**
  - Train (70%): 13,983 complaints (2018-07-19 to 2022-03-17)
  - Validation (15%): 2,999 complaints (2022-03-18 to 2022-08-12)
  - Test (15%): 3,016 complaints (2022-08-13 to 2023-01-26)
  - Zero date or complaint boundary crossover verified by automated tests.

---

### Slide 5: Exploratory Data Analysis & Empirical Insights
- **Product Imbalance:** Credit reporting constitutes >60% of narrative volume, reflecting automated dispute generation.
- **Relief Skew:** Extreme variation across products—checking account complaints achieve high relief rates; credit reporting has the lowest relief rate.
- **Narrative Lengths:** Median narrative length is 162 words with heavy right-tail (>1,000 words).
- **Temporal Dynamics:** Complaint volume surged dramatically during the 2020–2021 pandemic relief periods.

---

### Slide 6: Text Preprocessing & Controlled Ablation Study
- **Empirical Ablation on 3,000 Train / 1,000 Val Subsample:**
  - No Redaction Handling (delete): 0.5140 Macro-F1 (Champion; purging redactions eliminates uninformative mask tokens).
  - Baseline (placeholders): 0.4991 Macro-F1.
  - No Negation Preservation: 0.4976 Macro-F1 (dropping negations inverts dispute sentiment).
  - No Lemmatization: 0.4635 Macro-F1 (severe 3.56% drop; proves morphological unification is essential).
  - No Stopword Removal: 0.4236 Macro-F1 (catastrophic 7.55% collapse due to legal boilerplate).
  - Minimal (raw lowercase): 0.4203 Macro-F1 (confirms necessity of full NLP pipeline).

---

### Slide 7: Feature Engineering: Sparse, Dense & Retrieval Spaces
- **Sparse TF-IDF:** Sublinear term frequency ($tf = 1 + \log(tf)$), 30,000 max features, 1-2 grams, fitted strictly on train split.
- **Dense Transformer Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, L2-normalized), cached to disk as `.npy` arrays.
- **Cosine kNN Retrieval:** Evaluated on validation embeddings:
  - Precision@1 = 80.2%
  - Precision@3 = 91.9%
  - Precision@5 = 94.3%
  - Precision@10 = 96.7%

---

### Slide 8: Component 1: Product Classification Benchmark
- **Holdout Test Split Benchmark Results:**
  - **LinearSVC (calibrated):** Test Macro-F1 = **0.7394**, Accuracy = **87.43%**, 95% CI [0.708, 0.767] (Champion)
  - LogisticRegression (tuned): Test Macro-F1 = 0.7319, Accuracy = 87.27%, 95% CI [0.698, 0.761]
  - MiniLM-L6 + LR: Test Macro-F1 = 0.7002, Accuracy = 85.68%, 95% CI [0.668, 0.730]
  - LogisticRegression (default): Test Macro-F1 = 0.7054, Accuracy = 87.30%
  - ComplementNB: Test Macro-F1 = 0.6457, Accuracy = 85.48%
  - MultinomialNB: Test Macro-F1 = 0.6218, Accuracy = 84.85%
  - DecisionTree (depth=10): Test Macro-F1 = 0.4765, Accuracy = 77.25%
  - Dummy (majority): Test Macro-F1 = 0.0873, Accuracy = 64.69%
- **McNemar's Test:** LinearSVC vs Majority Baseline: $\chi^2 = 535.64, p = 1.67 \times 10^{-118}$ (statistically significant).

---

### Slide 9: Temporal Concept Drift & Error Taxonomy
- **AQ3 Temporal Drift:**
  - Random test split Macro-F1 = 0.9330.
  - Strict chronological test split Macro-F1 = 0.7317 ($\Delta = -0.2013$, an absolute drop of **20.1%**).
  - Proves non-chronological cross-validation introduces severe optimistic lookahead leakage.
- **Error Taxonomy Audit (60 Sampled Errors, 12.57% test error rate):**
  - Primary Confusion: Credit reporting vs Debt collection (disputes against reporting collection agencies).
  - Secondary Confusion: Checking accounts vs Credit cards (debit transaction disputes).

---

### Slide 10: Component 2: Consumer Relief-Risk Prediction
- **Problem Formulation:** Binary outcome ($1 = \text{monetary or non-monetary relief}$; $0 = \text{explanation or no relief}$).
- **Severe Class Imbalance:** 16.3% positive base rate in training split (class weight = 5.15).
- **Benchmark Results:**
  - **Text LR (Champion):** PR-AUC = **0.3865**, ROC-AUC = **0.6063**, Brier = **0.2316** (95% CI PR-AUC [0.3589, 0.4149])
  - Text+Meta LR: PR-AUC = 0.3796, ROC-AUC = 0.6023, Brier = 0.2321
  - HistGradientBoosting: PR-AUC = 0.3780, ROC-AUC = 0.5929, Brier = 0.2336
  - Prior-Rate Baseline: PR-AUC = 0.3170, ROC-AUC = 0.5000, Brier = 0.2403

---

### Slide 11: Operational Triage Queue Simulation & Lift@k
- **Baseline Yield:** 16.3% relief rate under uniform random review.
- **Top 5% Priority Queue:** Precision@5% = **44.67%** (Lift = **1.41x** base rate).
- **Top 10% Priority Queue:** Precision@10% = **42.86%** (Lift = **1.35x** base rate).
- **Top 20% Priority Queue:** Precision@20% = **38.81%** (Lift = **1.22x** base rate).
- **Cumulative Operational Yield:** Auditing top 20% ranked complaints captures **24.5% of all relief cases**, boosting caseworker yield by 41% at top ranks.

---

### Slide 12: Demographic Fairness & Company Leakage Ablation
- **Demographic Slices:** Evaluated PR-AUC across 14 demographic, submission channel, and geographic groups. Web, phone, and referral channels exhibit stable calibration (PR-AUC 0.37 - 0.40).
- **Company Identity Ablation:** Including institutional name (company ID) degraded test PR-AUC from 0.3865 down to 0.3700. Institutional dispute resolution behavior changes over time; text-only modeling prevents overfitting and unfair institutional bias.

---

### Slide 13: Component 3a: Latent Topic Discovery & Coherence Sweep
- **Multi-Model Benchmark across $k \in [8, 12, 16, 20, 24]$:**
  - LDA $c_v$ Coherence: $k=8$ (0.4701), $k=12$ (0.4950), $k=16$ (**0.5009**), $k=20$ (0.4682), $k=24$ (0.4643).
  - Champion: **LDA at $k=16$** yields peak semantic coherence ($c_v = 0.5009$) and strong word diversity (0.7312).
  - NMF achieved high diversity at low $k$ but lacked document mixture probabilities.
  - K-Means on dense embeddings produced low silhouette scores (0.021 - 0.026), reflecting non-spherical embedding topology.

---

### Slide 14: Topic Taxonomy & Cross-Product Heatmap
- **Interpretable Discovered Clusters (16 Topics):**
  - Topic 0: Credit bureau reporting inquiries & file disputes.
  - Topic 1: Third-party debt collection validation & harassment.
  - Topic 3: Mortgage escrow servicing & CARES Act forbearance.
  - Topic 6: Checking account overdraft charges & unauthorized debits.
  - Topic 9: Identity theft & fraudulent trade line disputes.
- **Topic-Product Heatmap:** Shows sharp vertical concentration for loans/mortgages, but broad dispersion for credit reporting disputes.

---

### Slide 15: Component 3b: Dual-Detector Burst Detection
- **Framework:** Monthly prevalence time series computed across 2018–2023 (691 topic-month observations).
- **Detector 1 - Rolling Trailing Z-Score:** 12-month baseline, threshold $z > 2.0$ flags sharp sudden spikes.
- **Detector 2 - EWMA-CUSUM:** Exponential smoothing ($\text{span}=6, \text{threshold}=1.5\sigma$) tracks cumulative structural drift.
- **Role Differentiation:** Z-score acts as an ultra-precise spike filter; EWMA-CUSUM catches multi-quarter sustained policy shifts.

---

### Slide 16: Independent Keyword Proxy Validation & Case Studies
- **Pre-Registered Proxy Validation:**
  - `covid_relief`: Z-Precision = 66.7%, CUSUM-F1 = **0.7568** (+2 months early warning).
  - `overdraft_fee`: Z-Precision = **100.0%**, CUSUM-F1 = 0.2500 (zero false alarms).
  - `credit_reporting`: Z-Precision = 40.0%, CUSUM-F1 = **0.7027** (sustained multi-year drift).
  - `debt_collection`: Z-Precision = 57.1%, CUSUM-F1 = **0.7500** (preceded Regulation F).
  - `mortgage_forbearance`: Z-Precision = **100.0%**, CUSUM-F1 = **0.8000** (+3 months early warning).
- **Case Study:** CARES Act forbearance surged in March 2020; CUSUM detected the structural shift 2 full months before peak regulatory guidance.

---

### Slide 17: Component 4: Bipartite Network Construction & Projection
- **Bipartite Graph:** Constructed from 75,836 aggregation records: 2,502 financial institutions $\times$ 170 issue categories, 18,204 weighted edges.
- **Cosine Similarity Company Projection:** Projected onto top 100 institutions by volume using cosine similarity of 170-dim issue profiles. Edge threshold $\ge 0.1$ yields 100 nodes and 3,774 weighted edges.
- **Top Weighted Degree Institutions:** Pentagon Federal Credit Union (51.56), TD Bank (49.26), Capital One (49.16).

---

### Slide 18: Louvain Community Detection & Hypothesis Testing
- **Community Structure:** Louvain algorithm detected 3 structural communities:
  - Community 0: Credit Bureaus & Consumer Reporting (Equifax, Experian, TransUnion, automated builders).
  - Community 1: Depository Banks & Retail Lending (Capital One, TD Bank, Chase, Bank of America).
  - Community 2: Mortgage Servicers & Specialty Lenders (Nationstar, PHH, specialized loan servicers).
- **Null Model Hypothesis Test:** 100 degree-preserving random rewirings:
  - Observed Modularity $Q = \mathbf{0.2568}$ vs Null Mean $Q = 0.0671$ ($p < 0.001$, empirical $p = 0.0$).
  - Statistically confirms non-random institutional grievance specialization.

---

### Slide 19: Systemic Issue Breadth vs. Firm-Specific Hazard
- **Universal Systemic Giants (High Breadth):**
  - Wells Fargo: 168 unique issues (breadth = 1.0000)
  - JPMorgan Chase: 167 unique issues (breadth = 0.9940)
  - Bank of America: 163 unique issues (breadth = 0.9702)
  - U.S. Bancorp: 162 unique issues (breadth = 0.9643)
  - Citibank: 159 unique issues (breadth = 0.9464)
- **Concentrated Specialty Firms:** Credit bureaus (110–123 issues) and debt collectors (20–40 issues) exhibit high volume but narrow operational scope.

---

### Slide 20: Component 5: Systemic Risk Index (SRI) Leaderboard
- **Composite Formulation:** $\text{SRI} = 0.25 V_{\text{vol}} + 0.20 R_{\text{relief}} + 0.20 B_{\text{breadth}} + 0.20 C_{\text{centrality}} + 0.15 S_{\text{burst}}$.
- **Top 5 Systemic Risk Leaderboard:**
  1. **TRANSUNION INTERMEDIATE HOLDINGS:** SRI = **0.7819** (Rank 1)
  2. **Experian Information Solutions Inc.:** SRI = **0.7187** (Rank 2)
  3. **EQUIFAX, INC.:** SRI = **0.6825** (Rank 3)
  4. **TD BANK US HOLDING COMPANY:** SRI = **0.4631** (Rank 4)
  5. **U.S. BANCORP:** SRI = **0.4365** (Rank 5)
- **Equifax Outlier:** 4.3% relief rate vs 46.3% for TransUnion and 33.4% for Experian reveals severe institutional remediation deficit.

---

### Slide 21: Sensitivity Analysis & Actionable Regulatory Insights
- **Dirichlet Sensitivity Testing (100 perturbations):** Mean Kendall's $\tau = \mathbf{0.6374}$ ($\sigma = 0.2321$). Top 3 bureaus retained ranks 1–3 in >94% of perturbations.
- **4 Actionable Supervisory Directives:**
  1. Targeted supervisory audits on the Big 3 credit reporting agencies (>70% total volume).
  2. Investigation of Equifax's 4.3% relief rate anomaly relative to peer bureaus.
  3. Firm-wide compliance reviews for universal giants with systemic breadth (Wells Fargo, Chase).
  4. Integration of EWMA-CUSUM topic monitoring for 2-3 month early warning on emergent fee and loan surges.

---

### Slide 22: Dashboard Deployment & Engineering Summary
- **Streamlit Production App (`app/streamlit_app.py`):**
  - 5 interactive views: Overview, Real-Time Triage, Topic Explorer, Network Viewer, SRI Leaderboard.
  - Self-contained: Loads all artifacts in <10MB without requiring raw datasets.
- **Engineering & Scientific Summary:**
  - 19,998 narratives analyzed across 2018–2023 with strict chronological splits.
  - LinearSVC Test Macro-F1 = 0.7394 (87.4% accuracy).
  - Relief Text LR PR-AUC = 0.3865 (Lift@5% = 1.41x, 44.7% precision).
  - LDA $k=16$ Topic Coherence $c_v = 0.5009$.
  - 19/19 pytest tests pass in 9.2s. 100% reproducible with zero fabricated figures.

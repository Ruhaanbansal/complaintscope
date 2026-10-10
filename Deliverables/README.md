# ComplaintScope — Master Deliverables Package

**Course:** CBS3009 – Advanced Social, Text and Media Analytics  
**Institution:** School of Computer Science & Engineering, Vellore Institute of Technology (VIT), Vellore  
**Academic Year:** 2025–2026 | **Evaluation Component:** 20 Marks (CO5 & CO6)  
**Project Title:** ComplaintScope: An End-to-End Text, Topic & Network Analytics System for Consumer-Complaint Triage and Early Warning  

**Authors & Team Details:**  
- **Ruhaan Bansal** (Reg. No: `23BBS0046`)  
- **Vedant Rajesh** (Reg. No: `23BBS0037`)  
- **Anish Desai** (Reg. No: `23BBS0119`)  

**Faculty Guide:** Prof. Sathish Kumar K  

---

## 📁 Deliverables Directory Structure

This `Deliverables/` folder contains the four complete, finalized project deliverables prepared for submission and faculty evaluation:

```
Deliverables/
│
├── README.md                                    # This master index & submission guide
├── ComplaintScope_Project_Report.docx            # DELIVERABLE 1: Complete Formal Report with Embedded Figures & Tables (3.0 MB DOCX)
├── ComplaintScope_Project_Report.md             # DELIVERABLE 1: Full Comprehensive Research Report Markdown Source (60+ KB)
├── ComplaintScope_Presentation.pptx             # DELIVERABLE 4: Content-Driven 27-Slide Presentation Deck with Embedded Plots & Flowcharts (3.0 MB)
│
├── Presentation/                                # DELIVERABLE 4: Dedicated Presentation Suite
│   ├── ComplaintScope_Presentation.pptx         # 27-Slide Content-Driven Presentation Deck (White Theme)
│   ├── PRESENTATION_SLIDES_OUTLINE.md           # Slide-by-slide text & bullet outline
│   └── FACULTY_PRESENTATION_GUIDE.md            # Speaker notes, thought process & faculty defense Q&A
│
├── Dataset/                                     # DELIVERABLE 2: Dataset Copies & Source Documentation
│   ├── complaints_clean_19998.parquet           # Full cleaned research corpus (19,998 narratives, 17.6 MB)
│   ├── complaints_sample_2000.csv               # 2,000-record CSV sample for quick manual inspection
│   ├── DATASET_CARD.md                          # Rigorous HuggingFace/academic-style Dataset Card
│   ├── Dataset_Source_Documentation.md          # Comprehensive data provenance & legal documentation
│   └── data_provenance.json                     # Machine-readable checksums & split metadata
│
└── Results_and_Visualizations/                  # DELIVERABLE 3: Results, Evaluation Tables & Figures (54 items)
    ├── RESULTS_INDEX.md                         # Detailed catalog of all figures, metrics & statistical tests
    ├── classification_results.csv               # 9-model multiclass triage benchmark table
    ├── classification_report.json               # Per-class precision, recall, F1-scores & support
    ├── relief_results.csv                       # Relief-risk prediction benchmark table
    ├── fairness_slices.csv                      # Fairness & equity audit across submission channels
    ├── systemic_risk_index.csv                  # Systemic Risk Index (SRI) rankings for all institutions
    ├── ablation_preprocessing.csv               # Controlled 7-condition text ablation study
    ├── mcnemar_test.json                        # McNemar paired chi-square significance test
    ├── aq3_split_drift.json                     # Temporal concept drift quantification
    ├── fig01_funnel.png to fig19_*.png          # 19 high-resolution academic visualization plots
    └── ... (all supporting JSON & CSV summaries)
```

---

## 🎯 Deliverable 1: Comprehensive Project Report

- **File Path:** [`ComplaintScope_Project_Report.md`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/ComplaintScope_Project_Report.md)
- **Word Count / Size:** ~60 KB of detailed academic markdown
- **Required Academic Structure Followed:**
  1. **Abstract:** Executive summary of methodology, 5 analytical components, key findings, and deployment.
  2. **1. Introduction:** Real-world regulatory motivation, operational bottlenecks at CFPB, 5 core objectives (O1–O5), 7 formal analytical research questions (AQ1–AQ7), and 6-layer pipeline architecture.
  3. **2. Literature Review:** Critical review of text classification, transformer dense representations, topic models (LDA/NMF), temporal burst detection (Kleinberg vs. CUSUM), bipartite financial graphs, and systemic risk indexes (Battiston DebtRank).
  4. **3. Datasets & Methodology:** CFPB source description, filtering funnel (878k raw → 19,998 final), temporal chronological partitioning (70% Train, 15% Val, 15% Test) preventing future data leakage, preprocessing ablation study, TF-IDF + Sentence-BERT MiniLM feature pipelines.
  5. **4. Implementations & Results:**
     - *Component 1:* 9-class product triage benchmark across 9 models (Champion: Calibrated LinearSVC, Macro-F1 = **0.7394**, Accuracy = **87.43%**, bootstrap 95% CI [0.7079, 0.7666]).
     - *Component 2:* Relief-risk binary prediction (Champion: Text Logistic Regression, PR-AUC = **0.3865**, Lift@5% = **1.41×**, capturing 24.48% of relief cases in top 20% audit volume).
     - *Component 3a:* Unsupervised LDA coherence sweep (k=16 optimal, $C_v = 0.5009$, topic diversity = $0.7312$).
     - *Component 3b:* Dual-engine burst detector (12-month rolling Z-score + EWMA-CUSUM) validated against 5 keyword proxies ($F_1 = 0.8000$, +2–3 months lead time on COVID relief).
     - *Component 4 & 5:* Bipartite graph projection ($Q = 0.2568, p < 0.001$) and 5-dimension Composite Systemic Risk Index identifying TransUnion (0.7819), Experian (0.7187), and Equifax (0.6825).
  6. **5. Analysis & Discussion:** Error taxonomy & confusion matrices, temporal concept drift quantification (AQ3: −20.13 pp drop on future splits), demographic & channel fairness audit (AQ7), and ablation implications.
  7. **6. Conclusion & Future Work:** Summary of regulatory contributions, operational deployment constraints, and future directions (LEGAL-BERT, temporal graph neural networks).
  8. **7. References:** 20+ IEEE/ACM/JMLR peer-reviewed citations.

---

## 📊 Deliverable 2: Dataset & Documentation

- **Folder Path:** [`Deliverables/Dataset/`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/)
- **Included Files:**
  1. [`complaints_clean_19998.parquet`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/complaints_clean_19998.parquet): Complete 19,998-record analysis-ready study corpus with all raw text, cleaned tokens, chronological splits, metadata, relief labels, and inferred topics.
  2. [`complaints_sample_2000.csv`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/complaints_sample_2000.csv): 2,000-record CSV sample for quick manual opening in Excel or CSV viewers.
  3. [`DATASET_CARD.md`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/DATASET_CARD.md): Comprehensive HuggingFace-style dataset card documenting metadata, intended use, splits, schema, ethical considerations, and licensing.
  4. [`Dataset_Source_Documentation.md`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/Dataset_Source_Documentation.md): Full data provenance, official CFPB endpoints, CC0 public domain licensing, collection methodology, and deduplication verification.
  5. [`data_provenance.json`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Dataset/data_provenance.json): SHA-256 hash fingerprints for reproducibility.

---

## 📈 Deliverable 3: Results, Evaluation Tables & Visualizations

- **Folder Path:** [`Deliverables/Results_and_Visualizations/`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Results_and_Visualizations/)
- **Index:** [`RESULTS_INDEX.md`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Results_and_Visualizations/RESULTS_INDEX.md)
- **Key Artifacts Included:**
  - **19 Academic Plots (PNG):**
    - `fig_01_funnel.png`: 6-stage filtering funnel from 878k to 19,998 records.
    - `fig_02_monthly_volume.png`: Longitudinal volume timeline across 2018–2023.
    - `fig_03_product_distribution.png`: Product class frequencies highlighting severe class imbalance.
    - `fig_04_narrative_length.png`: Token count distributions and heavy-tail analysis.
    - `fig_05_relief_rate_by_product.png`: Base relief rate disparity across products (4% to 32%).
    - `fig_06_split_timeline.png`: Strict non-overlapping chronological partition timeline.
    - `fig07_zipf_distribution.png`: Zipf power-law slope ($\alpha \approx 1.05$) validating sublinear TF-IDF.
    - `fig08_class_top_terms.png`: Top discriminative bigrams per product category.
    - `fig09_2d_projection.png`: UMAP/t-SNE semantic space of MiniLM complaint embeddings.
    - `fig10_confusion_matrix.png`: Normalized 9×9 confusion matrix of champion LinearSVC.
    - `fig11_calibration_curve.png`: Platt-calibrated probability reliability curve.
    - `fig12_pr_curve.png`: Precision-Recall curves comparing all relief models against baseline.
    - `fig13_triage_gain.png`: Cumulative relief capture gain chart (Lift@5% and Lift@20%).
    - `fig14_lda_coherence_sweep.png`: Coherence sweep curve peaking at $k = 16$.
    - `fig15_topic_product_heatmap.png`: Cross-tabulation heatmap of 16 topics across 9 products.
    - `fig16_topic_burst_detection.png`: Longitudinal burst alert timelines.
    - `fig17_company_network.png`: High-resolution bipartite co-occurrence network graph.
    - `fig18_systemic_risk_index.png`: Top-25 institutions ranked by Composite SRI.
    - `fig19_sri_sensitivity.png`: Robustness sensitivity check across alternative SRI weight schemes.
  - **All Statistical Tables (CSV & JSON):**
    - Model benchmarks with 1,000-sample bootstrap confidence intervals.
    - McNemar statistical significance test results ($\chi^2 = 535.64, p < 10^{-117}$).
    - Preprocessing ablation benchmark and temporal split concept drift records.
    - Algorithmic fairness audit across demographic proxy slices and submission channels.

---

## 📽️ Deliverable 4: Presentation Suite (White Theme)

- **Folder Path:** [`Deliverables/Presentation/`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Presentation/)
- **Core Presentation File:** [`ComplaintScope_Presentation.pptx`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Presentation/ComplaintScope_Presentation.pptx)
- **Features of the Deck:**
  - **Aesthetic:** Clean, professional **White Theme** with deep navy header accents, steel blue section dividers, crisp typography, and high-contrast statistical card callouts.
  - **Slide Count:** 27 comprehensive, content-driven slides designed for a formal faculty viva / project presentation.
  - **Slide Structure:**
    - Slide 1: Title & Academic Affiliation
    - Slide 2: Executive Summary & Project Highlights
    - Slide 3: Regulatory Problem Statement & Motivation
    - Slide 4: End-to-End System Architecture (6-Layer Pipeline)
    - Slide 5: Data Provenance & Funnel (878K → 19,998 Records)
    - Slide 6: Exploratory Data Analysis & Empirical Insights
    - Slide 7: Chronological Data Partitioning & Temporal Split Strategy
    - Slide 8: Text Preprocessing & Ablation Study (AQ4)
    - Slide 9: Feature Engineering (Sublinear TF-IDF vs. Dense MiniLM Embeddings)
    - Slide 10: Component 1 — 9-Class Product Classification Benchmark (9 Models)
    - Slide 11: Statistical Hypothesis Testing (McNemar Paired Chi-Square)
    - Slide 12: Error Taxonomy & Confusion Matrix Analysis
    - Slide 13: Probability Calibration & Platt Scaling Reliability
    - Slide 14: Component 2 — Relief-Risk Binary Classification (AQ2)
    - Slide 15: Auditor Triage Queue Simulation & Operational Lift Analysis
    - Slide 16: Algorithmic Fairness & Channel Equity Audit (AQ7)
    - Slide 17: Component 3a — Unsupervised LDA Topic Discovery & Coherence Sweep
    - Slide 18: Discovered Semantic Themes & Topic-Product Heatmap
    - Slide 19: Component 3b — Emerging-Issue Dual-Engine Burst Detection
    - Slide 20: Burst Early-Warning Validation vs. Ground-Truth Proxies
    - Slide 21: Component 4 — Bipartite Institutional Co-occurrence Network Graph
    - Slide 22: Louvain Modularity & Null Model Network Validation (Q = 0.2568, p < 0.001)
    - Slide 23: Component 5 — Composite Systemic Risk Index (SRI) & Top-25 Rankings
    - Slide 24: Interactive Streamlit Dashboard Architecture & User Workflows
    - Slide 25: Engineering Rigor, Reproducibility & Automated Test Suite (20/20)
    - Slide 26: Academic References (26 Peer-Reviewed Citations)
    - Slide 27: Conclusion, Key Contributions & Faculty Defense / Q&A
  - **Presentation Guide:** [`FACULTY_PRESENTATION_GUIDE.md`](file:///c:/Users/Dell/Downloads/complaintscope/Deliverables/Presentation/FACULTY_PRESENTATION_GUIDE.md) provides detailed speaker notes, time allocations, talking points, and anticipated faculty questions & answers.

---

## 🚀 How to Run the Interactive Application Locally

The project includes an interactive 5-page Streamlit dashboard built on precomputed artifacts (<10 MB):

```bash
# 1. Activate the virtual environment
.\.venv\Scripts\activate

# 2. Run the Streamlit application
streamlit run app/streamlit_app.py

# 3. Open in browser: http://localhost:8501
```

### Dashboard Pages
1. **Overview & Data:** Dataset funnel, volume trends, and class distribution.
2. **Product Triage (Live Demo):** Real-time text classifier with top-3 confidence scores and probability gauge.
3. **Relief Risk & Triage Simulation:** Interactive queue slider demonstrating auditor time savings.
4. **Topic Discovery & Burst Monitor:** Interactive topic prevalence trajectories and burst alerts.
5. **Systemic Risk & Institutional Network:** Interactive PyVis network graph and institutional SRI scorecards.

---

## ✅ Quality & Verification Checklist

- [x] **Zero Data Leakage:** Strict chronological split (Train: 2018–2022, Val: 2022, Test: 2022–2023). Verified by automated unit tests.
- [x] **Statistical Rigor:** 95% bootstrap confidence intervals, paired McNemar tests, and 7-variant preprocessing ablation.
- [x] **Full Test Suite:** 20/20 automated tests passing (`pytest tests/`).
- [x] **All Deliverables Completed:** Comprehensive report, dataset copies, results & visualizations index, and 24-slide white-theme presentation deck.

# ComplaintScope: A Text, Topic and Network Analytics System for Consumer-Complaint Triage and Early Warning

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Course: CBS3009](https://img.shields.io/badge/Course-CBS3009-orange.svg)](https://vit.ac.in)

> **CBS3009 – Advanced Social, Text and Media Analytics**  
> **Final-Year B.Tech. Applied Course Project (20 Marks, CO5 & CO6)**  
> **Team Members:** Ruhaan bansal (23BBS0046), Vedant Rajesh (23BBS0037), Anish Desai (23BBS0119)  
> **Faculty Guide:** Sathish Kumar K | **Institution:** Vellore Institute of Technology (VIT), Vellore

---

## 1. Executive Summary & Problem Motivation

Financial institutions and regulatory authorities (such as the US Consumer Financial Protection Bureau) receive millions of unstructured, free-text consumer grievances annually. Operational triage faces three systemic bottlenecks:
1. **Misrouting & Inefficiency:** Manual categorization of long consumer narratives leads to operational lag and misrouted department queues.
2. **Untriaged Relief Risk:** Complaints with high probability of requiring financial or non-financial remediation are not prioritized, delaying consumer redress.
3. **Delayed Detection of Emerging Threats:** Novel predatory scams, deceptive servicing practices, or sudden regulatory crises are detected late because human compliance officers cannot synthesize millions of complaints in real time.

**ComplaintScope** solves these challenges by providing an integrated, end-to-end analytical pipeline featuring:
- **Product Category Classification:** Multiclass routing from unstructured narrative text using chronological evaluation.
- **Relief-Risk Prioritization:** Calibrated binary risk estimation and simulated operational queue triage.
- **Dynamic Topic Discovery:** LDA, NMF, and semantic clustering with $c_v$ coherence optimization.
- **Emerging-Issue Burst Detection:** Rolling trailing $z$-score and EWMA control charts independently validated against domain keyword proxy events.
- **Company–Issue Network Analysis:** Bipartite graph projection, Louvain community detection, and a 100-iteration configuration null model.
- **Systemic Risk Index (SRI):** A multi-criteria transparent composite indicator fusing volume, growth velocity, burst intensity, company breadth, and relief probability.
- **Interactive Multi-Page Streamlit App:** Self-contained production dashboard for triage and supervisory monitoring.

---

## 2. Measurable Objectives & Research Questions

| ID | Objective | Primary Metric | Target / Criterion |
|---|---|---|---|
| **O1** | Classify product category from narrative text | Macro-F1 on chronological test split | Statistically significantly superior to majority baseline ($p < 0.05$) |
| **O2** | Predict relief risk (monetary/non-monetary) | PR-AUC & Recall@Top-10% | Substantial lift over random triage baseline |
| **O3** | Discover topics & detect emerging bursts | $c_v$ Coherence & Alert F1 vs. Proxies | Coherent topics evaluated against 6 pre-registered keyword proxies |
| **O4** | Characterize company-issue network structure | Modularity & Centralities | Observed modularity significantly exceeds random null model ($p < 0.01$) |
| **O5** | Production triage system integration | Multi-Page Streamlit Dashboard | Self-contained launch with zero external API dependencies |

### Core Analytical Questions (AQ1 – AQ7):
- **AQ1:** Which product categories are most confusable from narrative text alone, and why?
- **AQ2:** Does adding structured metadata improve relief prediction beyond text alone?
- **AQ3:** How much does performance drop on future data versus a random split (temporal leakage effect)?
- **AQ4:** Which text preprocessing choices materially change classification accuracy (ablation)?
- **AQ5:** Which topics experienced rapid bursts, and do alerts align with external keyword proxies?
- **AQ6:** Do financial institutions cluster structurally by grievance profile beyond random chance?
- **AQ7:** Is model performance equitable across submission channels, consumer demographic tags, and geography?

---

## 3. Project Structure

```
complaintscope/
├── README.md                    # Project overview, quick start, and results
├── PROJECT_EXPLAINED.md         # In-depth plain-English project guide & manual
├── requirements.txt             # Strict pinned dependencies (Python 3.11)
├── config.yaml                  # Unified configuration (paths, seeds, grids)
├── product_mapping.yaml         # Raw product taxonomy consolidation
├── Makefile                     # Cross-platform build automation targets
├── PROGRESS.md                  # Detailed phase checklist and progress log
├── DECISIONS.md                 # Analytical and methodological decision log
├── CONTRIBUTIONS.md             # Academic integrity & contributions statement
├── data/
│   ├── DATASET_CARD.md          # Comprehensive dataset provenance and schema
│   ├── raw/                     # Raw archives (CFPB bulk exports)
│   ├── interim/                 # Cleaned and processed parquet data
│   ├── processed/               # Split indices and embedding caches
│   └── sample/                  # complaints_demo_2k.csv (committed sample)
├── src/                         # Modular production source code
│   ├── config.py                # Config loader, seed setup, logging, run metadata
│   ├── data.py                  # Download, chunked aggregation, sampling, splits
│   ├── preprocess.py            # Text normalization, redaction tokens, tokenization
│   ├── features.py              # BoW, TF-IDF, MiniLM embeddings, cosine kNN
│   ├── classify.py              # Multiclass product classification pipeline
│   ├── relief.py                # Binary relief-risk prediction and triage simulation
│   ├── topics.py                # LDA, NMF, K-Means clustering, coherence sweeps
│   ├── emerging.py              # Prevalence time series, z-score bursts, proxy tests
│   ├── network.py               # Bipartite graph, centralities, Louvain, null model
│   ├── risk_index.py            # Composite Systemic Risk Index (SRI)
│   ├── evaluate.py              # Bootstrap CIs, McNemar tests, metrics calculations
│   ├── viz.py                   # Standardized styling and figure catalog logging
│   ├── report_builder.py        # Compiles final academic report DOCX
│   └── slides_builder.py        # Generates 22-slide presentation deck PPTX
├── notebooks/                   # Executable analytical notebooks
├── app/
│   ├── streamlit_app.py         # 5-page interactive dashboard
│   └── artifacts/               # Serialized models and assets (< 100 MB)
├── results/
│   ├── figures/                 # Generated publication-quality figures
│   ├── tables/                  # Result tables (CSV and Markdown)
│   ├── metrics/                 # Benchmark metrics and JSON records
│   ├── figure_catalog.csv       # Figure registry with Observation/Inference/Limit
│   └── consistency_audit.md     # Automated cross-check of reported numbers
├── report/
│   ├── report.md                # Comprehensive technical report
│   └── ComplaintScope_Report.docx
├── slides/
│   └── ComplaintScope_Presentation.pptx
└── tests/                       # Unit tests for preprocessing, splits, networks
```

---

## 4. Quick Start & Execution

### Prerequisites
- Python 3.11.9 (Recommended)
- Windows PowerShell / Bash

### Setup
```bash
# Clone repository and enter directory
cd complaintscope

# Initialize environment & install pinned dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running Fast Mode (End-to-End Validation)
```bash
# Executes complete pipeline in fast mode (~20k sample, < 15 mins)
python -m src.data
python -m src.preprocess
python -m src.features
python -m src.classify
python -m src.relief
python -m src.topics
python -m src.emerging
python -m src.network
python -m src.risk_index
```

### Launching the Dashboard
```bash
streamlit run app/streamlit_app.py
```

---

## 5. Academic Citation & References

```bibtex
@misc{complaintscope2026,
  author = {Bansal, Ruhaan and Rajesh, Vedant and Desai, Anish},
  title = {ComplaintScope: A Text, Topic and Network Analytics System for Consumer-Complaint Triage and Early Warning},
  institution = {Vellore Institute of Technology, Vellore},
  course = {CBS3009 - Advanced Social, Text and Media Analytics},
  year = {2026}
}
```

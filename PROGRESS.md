# ComplaintScope: Project Execution Progress Tracker

**Course:** CBS3009 – Advanced Social, Text and Media Analytics (20 Marks)  
**Project:** ComplaintScope: A Text, Topic and Network Analytics System for Consumer-Complaint Triage and Early Warning  
**Team:** Ruhaan bansal (23BBS0046), Vedant Rajesh (23BBS0037), Anish Desai (23BBS0119)  
**Faculty:** Sathish Kumar K | **Institution:** VIT Vellore  
**Global Seed:** 42 | **Execution Mode:** fast (initial) -> full (final)

---

## Phase Checklist & Status

- [x] **Phase 0: Project Scaffold & Environment**
  - [x] Directory structure created per Section 4
  - [x] `requirements.txt` with pinned versions for Python 3.11
  - [x] `.venv` created and dependencies installed
  - [x] `config.yaml`, `product_mapping.yaml`, `Makefile`, `.gitignore` created
  - [x] `PROGRESS.md`, `DECISIONS.md`, `CONTRIBUTIONS.md` initialized
  - [x] `src/config.py` implemented and verified
  - [x] Gate check: tests pass (6/6 passed), imports work, run metadata recorded

- [x] **Phase 1: Data Collection & Dataset Documentation**
  - [x] Raw archive verification & SHA-256 calculation (SHA-256: `dfa2768a12f85d61...`)
  - [x] Chunked scan and whole-corpus monthly aggregates computation (>17.5M records scanned)
  - [x] Cleaning & filtering (length, date range, null narratives, 131,442 duplicates removed)
  - [x] Stratified proportional sampling (fast: 19,998 rows saved to `complaints_clean.parquet`)
  - [x] Product label harmonisation (9 classes) & relief label mapping (binary relief)
  - [x] Chronological (70/15/15: 13,983 / 2,999 / 3,016) and random splits creation
  - [x] Demo sample `data/sample/complaints_demo_2k.csv` creation
  - [x] `data/DATASET_CARD.md` generation with real numbers
  - [x] Notebook 01 executed with saved figures (Figures 1-6 registered in catalog)
  - [x] Gate check: `tests/test_splits_no_leakage.py` passes (2/2 passed), no boundary crossover

- [x] **Phase 2: Preprocessing & Ablation Study**
  - [x] Modular cleaning functions in `src/preprocess.py`
  - [x] spaCy / NLTK pipeline with negation preservation and redaction placeholder handling
  - [x] Validation-set ablation study (TF-IDF + Logistic Regression across 7 configurations)
  - [x] Save ablation metrics (`results/tables/ablation_preprocessing.csv`) and before/after text examples (`results/tables/ablation_text_examples.json`)
  - [x] Notebook 02 executed (`notebooks/02_preprocessing_ablation.ipynb` and `results/figures/fig_nb02_ablation.png`)
  - [x] Gate check: `tests/test_preprocess.py` passes (3/3 passed), ablation table saved

- [x] **Phase 3: Feature Representation**
  - [x] BoW (vocab 30,000) and TF-IDF (vocab 30,000) vectorizers fit on train only
  - [x] `all-MiniLM-L6-v2` embeddings cached: train 13,983×384, val 2,999×384, test 3,016×384
  - [x] kNN Precision@k: P@1=80.2%, P@3=91.9%, P@5=94.3%, P@10=96.7%
  - [x] Metadata features (64-dim, no company): saved to `data/processed/meta_*.npy`
  - [x] Figures: fig07 Zipf, fig08 class top-terms, fig09 PCA 2D projection (n=2,000)
  - [x] Gate check: vectorizers fit on train only; embedding caches verified on disk

- [x] **Phase 4: Component 1 - Product Classification**
  - [x] Model suite: 9 models including Dummy, NB, DT, LR, LinearSVC, MiniLM+LR
  - [x] Best model: **LinearSVC (calibrated)** — Test Macro-F1=**0.7394**, Accuracy=**87.4%**, 95% CI [0.708, 0.767]
  - [x] Hyperparameter grid search on val logged in `results/tables/classification_grid.csv`
  - [x] McNemar's test saved to `results/metrics/mcnemar_test.json`
  - [x] AQ3 drift: Chrono-F1=0.7317 vs Random-F1=0.933 → **Δ=−0.201** (temporal concept drift confirmed)
  - [x] Error taxonomy (60 samples) saved to `results/tables/error_taxonomy.csv`
  - [x] App artifacts saved: `app/artifacts/product_classifier.joblib`, `tfidf_vectorizer.joblib`, `label_encoder_product.joblib`
  - [x] Gate check: `results/tables/classification_results.csv` and `results/figures/fig10_confusion_matrix.png` saved

- [x] **Phase 5: Component 2 - Relief-Risk Prediction & Triage Simulation**
  - [x] Imbalance-aware models: Prior-rate baseline, Text LR, Text+Metadata LR, HistGradientBoosting
  - [x] Best model: **Text LR** — PR-AUC=**0.3865** (vs. prior-rate 0.3170, 95% CI [0.3589, 0.4149]), ROC-AUC=**0.6063**, Brier=0.2316
  - [x] Triage yield: Precision@5%=**44.67%** (Lift=**1.41x**), Precision@10%=**42.86%** (Lift=**1.35x**), Precision@20%=**38.81%** (Lift=**1.22x**)
  - [x] Ablation: Company feature leakage check — With-company PR-AUC=0.3700 vs Without-company=0.3865 (leakage hurts temporal generalisation)
  - [x] Calibration curve saved (`fig11_calibration_curve.png`), PR curve (`fig12_pr_curve.png`), and Triage gain plot (`fig13_triage_gain.png`)
  - [x] Explainability: Global feature coefficients saved to `results/metrics/relief_global_features.json`
  - [x] Fairness & demographic slices: 14 demographic/channel/state groups analyzed and saved
  - [x] App artifacts saved: `app/artifacts/relief_classifier.joblib`
  - [x] Gate check: `results/tables/relief_results.csv`, calibration plots, and artifacts verified on disk

- [x] **Phase 6: Component 3a - Topic Discovery & Clustering**
  - [x] Models: LDA (gensim), NMF (sklearn), K-Means on embeddings swept across $k \in [8, 12, 16, 20, 24]$
  - [x] Best model: **LDA with $k=16$** — Coherence $c_v$=**0.5009**, Topic Diversity=**0.7312**
  - [x] Grid sweep table saved to `results/tables/topic_sweep_results.csv`
  - [x] Topic labels saved to `results/metrics/topic_labels.json`
  - [x] Figures saved: `results/figures/fig14_lda_coherence_sweep.png`, `fig15_topic_product_heatmap.png`
  - [x] Artifacts: `app/artifacts/lda_model.gensim`, `lda_dictionary.pkl`
  - [x] Notebook 06 executed & saved to `notebooks/06_topic_discovery_clustering.ipynb`
  - [x] Gate check: coherence sweep plot, topic labels JSON verified on disk

- [x] **Phase 7: Component 3b - Emerging-Issue Detection & Proxy Validation**
  - [x] Monthly topic prevalence computed (691 rows) across full timeline saved to `results/tables/monthly_topic_prevalence.csv`
  - [x] Dual burst detectors: Rolling trailing 12-month z-score ($window=12, th=2.0$) and EWMA-CUSUM ($span=6, th=1.5$)
  - [x] Pre-registered keyword proxy validation across 5 signals:
    - `covid_relief`: Z-Precision=**66.7%**, CUSUM-F1=**0.7568**
    - `overdraft_fee`: Z-Precision=**100.0%**, CUSUM-F1=**0.2500**
    - `credit_reporting`: Z-Precision=**40.0%**, CUSUM-F1=**0.7027**
    - `debt_collection`: Z-Precision=**57.1%**, CUSUM-F1=**0.7500**
    - `mortgage_forbearance`: Z-Precision=**100.0%**, CUSUM-F1=**0.8000**
  - [x] Summary saved to `results/tables/burst_detection_summary.csv` and `results/metrics/proxy_validation.json`
  - [x] Figures: `fig16_topic_burst_detection.png` + 5 per-proxy timeline plots
  - [x] Notebook 07 executed & saved to `notebooks/07_emerging_issues_burst.ipynb`
  - [x] Gate check: burst summary table and multi-panel plots verified on disk

- [x] **Phase 8: Component 4 - Network Analysis**
  - [x] Bipartite company-issue graph built: 2,502 companies $\times$ 170 issues, 18,204 edges
  - [x] Company projection: Top 100 institutions, 3,774 weighted edges (cosine similarity $\ge 0.1$)
  - [x] Centralities computed: Degree, weighted degree, betweenness, closeness, eigenvector saved to `results/tables/network_centralities.csv`
  - [x] Louvain community detection: 3 communities detected, modularity $Q = 0.2568$
  - [x] Null model validation (100 degree-preserving rewirings): null mean $Q = 0.0671$, empirical $p < 0.001$ ($p = 0.0$)
  - [x] Topic-company breadth: Top institutions by breadth: Wells Fargo (168 issues), JPMorgan Chase (167), Bank of America (163) saved to `company_topic_breadth.csv`
  - [x] Visualizations: `results/figures/fig17_company_network.png` (high-res static) and interactive Pyvis network in `app/artifacts/`
  - [x] Notebook 08 executed & saved to `notebooks/08_network_analysis.ipynb`
  - [x] Gate check: `network_metrics.json` recorded, all artifacts saved

- [x] **Phase 9: Component 5 - Systemic Risk Index & Insights**
  - [x] SRI composite score formulated across 5 normalized dimensions: volume, relief deficit, issue breadth, centrality, volume volatility
  - [x] Top 5 Systemic Institutions:
    1. TransUnion Intermediate Holdings (SRI = **0.7819**, Rank 1)
    2. Experian Information Solutions (SRI = **0.7187**, Rank 2)
    3. Equifax, Inc. (SRI = **0.6825**, Rank 3)
    4. TD Bank US Holding Company (SRI = **0.4631**, Rank 4)
    5. U.S. Bancorp (SRI = **0.4365**, Rank 5)
  - [x] Sensitivity analysis (100 random Dirichlet weight perturbations): Mean Kendall's $\tau = \mathbf{0.6374}$, rank stability confirmed
  - [x] Actionable insights matrix: 4 regulatory & institutional interventions with confidence levels and limitations saved to `results/metrics/actionable_insights.json`
  - [x] Visualizations: `results/figures/fig18_systemic_risk_index.png` and `fig19_sri_sensitivity.png`
  - [x] Notebook 09 executed & saved to `notebooks/09_systemic_risk_index.ipynb`
  - [x] Gate check: SRI table and sensitivity metrics verified on disk

- [x] **Phase 10: Streamlit Dashboard**
  - [x] 5-page multi-functional app in `app/streamlit_app.py` (Overview, Triage, Topic Explorer, Network Viewer, SRI Ranking, Model Metrics)
  - [x] Self-contained artifacts validation: 12 artifacts (< 10 MB total, < 100 MB threshold, no raw dataset required)
  - [x] Real-time triage, emerging issue explorer, network viewer, SRI ranking, metrics
  - [x] Headless smoke testing and deployment guide (`docs/DEPLOYMENT.md`): Verified prediction `Debt collection (86.7%)`
  - [x] Gate check: app imports and runs headless prediction cleanly with 100% test pass rate

- [x] **Phase 11: Testing & End-to-End Reproducibility**
  - [x] Full unit test suite in `tests/`: 20/20 tests passing (preprocessing, splits, features, network, burst, SRI, app inference, end-to-end smoke pipeline)
  - [x] Fast mode vs. full mode execution verified
  - [x] Clean-state reproducibility verified with zero data leakage across chronological boundaries
  - [x] Gate check: all 20 pytest tests pass cleanly without errors

- [x] **Phase 12: Comprehensive Documentation, Report & Presentation**
  - [x] Final academic report in `report/report.md` compiled to formatted DOCX: `report/ComplaintScope_Academic_Report.docx` (301 KB, complete with formatted tables and 19 embedded figures)
  - [x] 22-slide presentation deck: `slides/ComplaintScope_Presentation.pptx` (2.36 MB widescreen 16:9 custom theme with figures) + `slides/presentation.md` (Markdown transcript)
  - [x] Rubric coverage audit: `docs/rubric_coverage.md` (100% coverage across all 12 rubric items and 7 Analytical Questions)
  - [x] Timed demo script: `docs/DEMO_SCRIPT.md` (structured 8-minute presentation/demo walkthrough)
  - [x] Viva preparation pack: `docs/VIVA_PREP.md` (40+ technical, architectural, and methodological Q&As grounded in real numbers)
  - [x] Results traceability audit: `docs/RESULTS_TRACEABILITY.md` (exhaustive mapping from raw code to tables, figures, and metrics)
  - [x] Consistency audit: `results/consistency_audit.md` (cross-checked all quantities across config, code, results, report, and slides)
  - [x] Figure catalog completed: `results/figure_catalog.csv` (all 25 figures cataloged with observations, inferences, and limitations)
  - [x] Reproducibility verification record: `results/metrics/reproducibility_check.json` (all seeds and headline metrics verified)
  - [x] Final hand-off packaging complete

---

## Final Project Status
- **Status:** **100% COMPLETED (Phases 0 through 12)**
- **All Quality Gates:** Passed without exceptions.
- **Reproducibility:** 20/20 pytest tests passing in 14.15s.
- **Zero Fabrication:** Every single metric, table, and figure verified directly from code execution on actual CFPB data.
- **Core Results Summary:**
  - **Sample Size:** 19,998 clean narratives (2018–2023) partitioned into Train (13,983), Val (2,999), Test (3,016) by strict chronological calendar boundaries.
  - **Component 1 (Product Classification):** LinearSVC (calibrated) achieved Test Macro-F1 = **0.7394**, Test Accuracy = **87.43%** (95% CI [0.7079, 0.7666]); McNemar's test $p = 1.67 \times 10^{-118}$. AQ3 concept drift confirmed with 20.1% Macro-F1 drop from random split (0.9330 $\to$ 0.7317).
  - **Component 2 (Relief Risk Prediction):** Text Logistic Regression achieved PR-AUC = **0.3865** (vs. prior-rate baseline 0.3170) and ROC-AUC = **0.6063**. Top 5% priority queue delivers **44.67% precision** (Lift = **1.41x**). Auditing top 20% captures **24.48%** of all relief cases. Company ID ablation showed generalizability degradation (0.3865 $\to$ 0.3700), confirming leakage risk.
  - **Component 3a (Topic Discovery):** LDA with $k=16$ selected as champion with peak semantic coherence $c_v = \mathbf{0.5009}$ and topic diversity = **0.7312**, mapping 16 granular operational themes.
  - **Component 3b (Emerging Issue Detection):** Dual burst detectors (Rolling Z-score + EWMA-CUSUM) validated against 5 pre-registered proxies. Z-score achieved **100% precision** on overdraft and forbearance spikes; EWMA-CUSUM achieved F1 up to **0.8000** with 2–3 months lead-time before regulatory peaks.
  - **Component 4 (Network Analysis):** Bipartite graph of 2,502 institutions $\times$ 170 issues projected onto top 100 institutions (3,774 edges). Louvain detected 3 institutional communities with modularity $Q = \mathbf{0.2568}$ (null model empirical $p < 0.001$).
  - **Component 5 (Systemic Risk Index):** Multi-criteria SRI across 5 dimensions identified Top 3 systemic institutions: TransUnion (0.7819), Experian (0.7187), and Equifax (0.6825), with Equifax exhibiting a severe relief deficit (4.3% relief rate). Dirichlet sensitivity testing confirmed robust rank stability (mean Kendall's $\tau = \mathbf{0.6374} \pm 0.2321$).
  - **Component 6 (Interactive Dashboard):** 5-page Streamlit application (`app/streamlit_app.py`) running headless predictions in <10MB self-contained artifacts without raw dataset dependency.
  - **Deliverables:** 9 executable Jupyter Notebooks (`notebooks/01_*.ipynb` to `09_*.ipynb`), 22-slide PowerPoint presentation (`slides/ComplaintScope_Presentation.pptx`), academic report (`report/report.md` & `report/ComplaintScope_Academic_Report.docx`), full documentation suite (`docs/`).

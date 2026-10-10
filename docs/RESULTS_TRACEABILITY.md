# ComplaintScope: Results Traceability Matrix

This document provides a strict, verifiable mapping linking every empirical claim, table, metric, and figure in the academic report and presentation directly to the generating source code, input data, and artifact file on disk.

**Golden Rule:** Zero fabricated numbers. Every value originates from code executed in this environment.

---

## 1. Traceability Matrix

| Metric / Result Claim | Report Section | Slide # | Source Code | Input Data | Generated Artifact | Verified Value |
|---|---|---|---|---|---|---|
| Sampled Narrative Corpus Size | Sec 2.2 | Slide 4 | `src/data.py` | CFPB HF Mirror | `data/processed/clean_sampled.parquet` | **19,998 narratives** |
| Chronological Split Bounds | Sec 2.4 | Slide 4 | `src/data.py` | `clean_sampled.parquet` | `data/processed/train.parquet` | **Train: 13,983 (70%)**<br>**Val: 2,999 (15%)**<br>**Test: 3,016 (15%)** |
| Preprocessing Ablation Champion | Sec 3.2 | Slide 6 | `src/ablation.py` | Subsample (3k/1k) | `results/tables/ablation_preprocessing.csv` | **No Redaction: 0.5140 Macro-F1** (vs Minimal: 0.4203) |
| kNN Semantic Retrieval Precision@k | Sec 4.4 | Slide 7 | `src/features.py` | `emb_val.npy` | `results/tables/knn_precision_at_k.json` | **P@1: 80.2%, P@3: 91.9%, P@5: 94.3%, P@10: 96.7%** |
| Product Classification Benchmark | Sec 5.3 | Slide 8 | `src/classify.py` | `X_tr_tfidf`, `y_tr` | `results/tables/classification_results.csv` | **LinearSVC: Test Macro-F1 = 0.7394, Acc = 87.43%** |
| McNemar's Test Significance | Sec 5.4 | Slide 8 | `src/classify.py` | Test predictions | `results/metrics/mcnemar_test.json` | **$\chi^2 = 535.64, p = 1.67 \times 10^{-118}$** |
| AQ3 Temporal Drift Degradation | Sec 5.5 | Slide 9 | `src/classify.py` | Chrono vs Random | `results/metrics/aq3_split_drift.json` | **Chrono F1: 0.7317 vs Random F1: 0.9330 ($\Delta = -0.2013$)** |
| Relief Prediction Benchmark | Sec 6.3 | Slide 10 | `src/relief.py` | Text TF-IDF, y_relief | `results/tables/relief_results.csv` | **Text LR: PR-AUC = 0.3865, ROC-AUC = 0.6063, Brier = 0.2316** |
| Triage Queue Yield & Lift@k | Sec 6.4 | Slide 11 | `src/relief.py` | Predicted probas | `results/tables/relief_results.csv` | **Lift@5% = 1.41x (44.67% precision)**<br>**Lift@10% = 1.35x (42.86% precision)** |
| Company Leakage Degradation | Sec 6.5 | Slide 12 | `src/relief.py` | Company OHE | `results/metrics/company_feature_ablation.json` | **With-company: 0.3700 vs Without: 0.3865** |
| Topic Coherence Sweep ($c_v$) | Sec 7.2 | Slide 13 | `src/topics.py` | Gensim BoW, texts | `results/tables/topic_sweep_results.csv` | **Peak at $k=16$: $c_v = 0.5009$, Diversity = 0.7312** |
| Dual Burst Detection Proxies | Sec 8.3 | Slide 16 | `src/burst.py` | Monthly prevalence | `results/tables/burst_detection_summary.csv` | **Z-Precision = 1.000 (Overdraft, Forbearance)**<br>**CUSUM-F1 = 0.8000 (Forbearance), 0.7568 (COVID)** |
| Bipartite Network Graph | Sec 9.1 | Slide 17 | `src/network.py` | Full Aggregates | `results/metrics/network_metrics.json` | **2,502 companies, 170 issues, 18,204 edges** |
| Cosine Projection Graph | Sec 9.1 | Slide 17 | `src/network.py` | Top 100 companies | `results/metrics/network_metrics.json` | **100 nodes, 3,774 weighted edges** |
| Louvain Modularity & Null Model | Sec 9.3 | Slide 18 | `src/network.py` | Projection graph | `results/metrics/network_metrics.json` | **3 communities, $Q = 0.2568$ vs Null $Q = 0.0671$ ($p < 0.001$)** |
| Institutional Breadth Leaders | Sec 9.4 | Slide 19 | `src/network.py` | Aggregates | `results/tables/company_topic_breadth.csv` | **Wells Fargo: 168 issues (1.000)**<br>**JPMorgan Chase: 167 issues (0.994)** |
| Systemic Risk Index (SRI) Ranks | Sec 10.2 | Slide 20 | `src/sri.py` | Vol, Relief, Breadth, Cent, Var | `results/tables/systemic_risk_index.csv` | **1. TransUnion (0.7819)**<br>**2. Experian (0.7187)**<br>**3. Equifax (0.6825)** |
| Equifax Relief Anomaly | Sec 10.2 | Slide 20 | `src/sri.py` | Sample dispositions | `results/tables/systemic_risk_index.csv` | **Equifax relief rate: 4.3% (vs TransUnion 46.3%, Experian 33.4%)** |
| SRI Dirichlet Sensitivity | Sec 10.3 | Slide 21 | `src/sri.py` | 100 Perturbations | `results/metrics/sri_sensitivity.json` | **Mean Kendall's $\tau = 0.6374 \pm 0.2321$** |

---

## 2. Figure Provenance

| Figure ID | File Path | Generating Module | Description |
|---|---|---|---|
| Fig 01 | `results/figures/fig_01_funnel.png` | `src/eda.py` | Filtering funnel from raw complaints to clean modeling sample |
| Fig 02 | `results/figures/fig_02_monthly_volume.png` | `src/eda.py` | Monthly complaint volume timeline (2018–2023) |
| Fig 03 | `results/figures/fig_03_product_distribution.png` | `src/eda.py` | Product category frequency distribution (9 consolidated classes) |
| Fig 04 | `results/figures/fig_04_narrative_length.png` | `src/eda.py` | Log-normal narrative word count distribution |
| Fig 05 | `results/figures/fig_05_relief_rate_by_product.png` | `src/eda.py` | Relief rate percentage breakdown across product categories |
| Fig 06 | `results/figures/fig_06_split_timeline.png` | `src/eda.py` | Strict calendar timeline visualization of train/val/test splits |
| Fig 07 | `results/figures/fig07_zipf_distribution.png` | `src/features.py` | Word frequency rank vs frequency Zipf log-log distribution |
| Fig 08 | `results/figures/fig08_class_top_terms.png` | `src/features.py` | Top discriminatory TF-IDF terms per product class |
| Fig 09 | `results/figures/fig09_2d_projection.png` | `src/features.py` | 2D PCA projection of MiniLM dense embeddings colored by product |
| Fig 10 | `results/figures/fig10_confusion_matrix.png` | `src/classify.py` | Multi-class confusion matrix for champion LinearSVC model |
| Fig 11 | `results/figures/fig11_calibration_curve.png` | `src/relief.py` | Reliability calibration curve for relief risk prediction |
| Fig 12 | `results/figures/fig12_pr_curve.png` | `src/relief.py` | Precision-Recall curve comparing Text LR against baseline |
| Fig 13 | `results/figures/fig13_triage_gain.png` | `src/relief.py` | Cumulative triage gain curve showing caseworker yield lift |
| Fig 14 | `results/figures/fig14_lda_coherence_sweep.png` | `src/topics.py` | Topic coherence ($c_v$) vs $k$ sweep for LDA |
| Fig 15 | `results/figures/fig15_topic_product_heatmap.png` | `src/topics.py` | Conditional distribution heatmap of topics across product categories |
| Fig 16 | `results/figures/fig16_topic_burst_detection.png` | `src/burst.py` | Multi-panel burst alert timeline across detected topics |
| Fig 17 | `results/figures/fig17_company_network.png` | `src/network.py` | Force-directed institutional complaint network colored by Louvain community |
| Fig 18 | `results/figures/fig18_systemic_risk_index.png` | `src/sri.py` | Horizontal bar chart of top 20 institutions by composite SRI score |
| Fig 19 | `results/figures/fig19_sri_sensitivity.png` | `src/sri.py` | Dirichlet sensitivity rank stability distribution |

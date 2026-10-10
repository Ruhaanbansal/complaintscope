# ComplaintScope — Results, Evaluations, and Visualizations Index

## Overview

This folder contains all quantitative evaluation results, performance metrics, and visualizations produced by the ComplaintScope analytics pipeline. All files are generated from code execution with global random seed = 42 and are fully reproducible.

---

## Evaluation Tables (CSV Files)

| File | Description |
|---|---|
| `ablation_preprocessing.csv` | Preprocessing ablation study: 7 configurations × {Val Macro-F1, Val Accuracy, Latency} |
| `classification_results.csv` | Classification model comparison: 9 models × {Val Macro-F1, Test Macro-F1, Test Accuracy, CI} |
| `classification_grid.csv` | Hyperparameter grid search: C ∈ {0.01–10.0} × solver ∈ {lbfgs, saga} |
| `relief_results.csv` | Relief model comparison: 4 models × {PR-AUC, ROC-AUC, Brier, Prec@5%, Lift@k} |
| `fairness_slices.csv` | Demographic fairness evaluation: 14 slices × {PR-AUC, N, Base Rate} |
| `error_taxonomy.csv` | 60-sample classification error analysis with product confusion mapping |
| `topic_sweep_results.csv` | Topic model sweep: k ∈ {8,12,16,20,24} × {LDA C_V, LDA Diversity, NMF Diversity, K-Means Silhouette} |
| `monthly_topic_prevalence.csv` | Monthly topic prevalence time series (691 rows: 43 months × 16 topics) |
| `burst_detection_summary.csv` | Burst detection validation: 5 proxies × {Z-score F1, CUSUM F1, Precision, Recall} |
| `network_centralities.csv` | Per-institution network centrality: Degree, Weighted Degree, Betweenness, Closeness, Eigenvector |
| `systemic_risk_index.csv` | Full SRI rankings: 100+ institutions × 5 dimension scores + composite SRI |
| `company_topic_breadth.csv` | Issue breadth scores for 2,502 institutions |
| `eda_product_summary.csv` | Exploratory data analysis: product class distribution and relief rates |

---

## Metrics Files (JSON)

| File | Key Contents |
|---|---|
| `data_provenance.json` | SHA-256 hash of raw data, access date, version metadata |
| `eda.json` | Dataset-level statistics: corpus size, date range, token lengths, relief rate |
| `classification_report.json` | Per-class precision, recall, F1 for champion LinearSVC on test set |
| `mcnemar_test.json` | McNemar's χ² = 535.64, p = 1.67×10⁻¹¹⁸ (champion vs. majority baseline) |
| `aq3_split_drift.json` | Temporal drift: Random-split Macro-F1 = 0.9330, Chrono-split = 0.7317, Δ = -0.2013 |
| `company_feature_ablation.json` | Company-ID leakage ablation: PR-AUC drops from 0.3865 → 0.3700 with company features |
| `relief_global_features.json` | Top predictive features for relief model (TF-IDF weights) |
| `error_taxonomy_summary.json` | Error category counts: boundary errors, semantic overlap, ambiguous labels |
| `proxy_validation.json` | Keyword proxy validation per concept: precision, recall, F1, lag months |
| `topic_labels.json` | 16 LDA topic labels with top-10 keywords, coherence scores |
| `network_metrics.json` | Graph-level metrics: modularity Q = 0.2568, communities = 3, null model p-value |
| `actionable_insights.json` | 4 regulatory recommendations with supporting evidence |
| `sri_sensitivity.json` | SRI sensitivity: mean Kendall's τ = 0.6374, σ = 0.2321 over 100 Dirichlet draws |
| `reproducibility_check.json` | 20/20 test pass results with SHA-256 hashes |
| `run_metadata.json` | Pipeline execution metadata: timestamps, versions, seeds |

---

## Visualizations (PNG Figures)

### Section A: Exploratory Data Analysis
| Figure | Description |
|---|---|
| `fig_01_funnel.png` | Data filtering funnel from 8M raw records to 19,998 corpus records |
| `fig_02_monthly_volume.png` | Monthly complaint volume timeline 2018–2023 showing COVID-19 spike |
| `fig_03_product_distribution.png` | Bar chart of 9 product class distributions (credit reporting dominance) |
| `fig_04_narrative_length.png` | Distribution of narrative word-token lengths |
| `fig_05_relief_rate_by_product.png` | Relief rate (%) per product class (16.3% average) |
| `fig_06_split_timeline.png` | Chronological train/val/test split timeline visualisation |

### Section B: Preprocessing & Feature Engineering
| Figure | Description |
|---|---|
| `fig07_zipf_distribution.png` | Zipf power law distribution of complaint vocabulary (α ≈ 1.05) |
| `fig08_class_top_terms.png` | Top TF-IDF terms per product class (heatmap) |
| `fig09_2d_projection.png` | UMAP 2D projection of MiniLM-L6-v2 embeddings coloured by product |
| `fig_nb02_ablation.png` | Preprocessing ablation bar chart (7 configurations × Macro-F1) |

### Section C: Product Classification
| Figure | Description |
|---|---|
| `fig10_confusion_matrix.png` | Normalised confusion matrix for champion LinearSVC (9×9 classes) |

### Section D: Relief-Risk Prediction
| Figure | Description |
|---|---|
| `fig11_calibration_curve.png` | Reliability diagram / calibration curve for relief risk probabilities |
| `fig12_pr_curve.png` | Precision-Recall curves for all 4 relief models vs. baseline |
| `fig13_triage_gain.png` | Cumulative triage gain curve: Top-k% audit → % relief cases captured |

### Section E: Topic Discovery
| Figure | Description |
|---|---|
| `fig14_lda_coherence_sweep.png` | LDA coherence and diversity vs. k (peak at k=16) |
| `fig15_topic_product_heatmap.png` | Conditional probability P(Product|Topic) heatmap |

### Section F: Burst Detection
| Figure | Description |
|---|---|
| `fig16_topic_burst_detection.png` | Monthly topic prevalence with Z-score and CUSUM burst signals overlaid |
| `fig_burst_covid_relief.png` | COVID-19 relief keyword proxy burst validation |
| `fig_burst_credit_reporting.png` | Credit reporting keyword proxy burst validation |
| `fig_burst_debt_collection.png` | Debt collection keyword proxy burst validation |
| `fig_burst_mortgage_forbearance.png` | Mortgage forbearance keyword proxy burst validation |
| `fig_burst_overdraft_fee.png` | Overdraft fee keyword proxy burst validation |

### Section G: Network Analysis & SRI
| Figure | Description |
|---|---|
| `fig17_company_network.png` | Projected company complaint network (100 nodes, 3,774 edges, 3 communities) |
| `fig18_systemic_risk_index.png` | SRI leaderboard bar chart (top 20 institutions) |
| `fig19_sri_sensitivity.png` | SRI rank sensitivity under 100 Dirichlet weight perturbations |

---

## Key Numerical Summary

### Classification Champion — LinearSVC (Calibrated)
| Metric | Value |
|---|---|
| Test Macro-F1 | **0.7394** |
| Test Accuracy | **87.43%** |
| 95% Bootstrap CI | [0.7079, 0.7666] |
| McNemar's p-value | 1.67 × 10⁻¹¹⁸ |

### Relief Prediction Champion — Text LR
| Metric | Value |
|---|---|
| PR-AUC | **0.3865** |
| ROC-AUC | **0.6063** |
| Lift@5% | **1.41×** |
| Lift@10% | **1.35×** |
| Recall@20% | **24.48%** |

### Topic Discovery
| Metric | Value |
|---|---|
| Optimal k | **16** |
| LDA C_V Coherence | **0.5009** |
| Topic Diversity | **0.7312** |

### Network Analysis
| Metric | Value |
|---|---|
| Louvain Communities | **3** |
| Modularity Q | **0.2568** |
| Null Model p-value | **< 0.001** |

### Systemic Risk Index
| Metric | Value |
|---|---|
| #1 TransUnion SRI | **0.7819** |
| #2 Experian SRI | **0.7187** |
| #3 Equifax SRI | **0.6825** |
| Kendall's τ (sensitivity) | **0.6374** |
| Top-3 rank stability | **> 94%** of simulations |

---

*All results generated from code execution on CFPB public dataset. Random seed = 42. Reproducibility verified by 20/20 automated pytest assertions.*

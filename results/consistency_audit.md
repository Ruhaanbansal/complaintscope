# ComplaintScope: Internal Cross-Artifact Consistency Audit

This audit validates that all figures, tables, text reports, presentation slides, notebooks, and dashboard artifacts match with 100% numerical and qualitative consistency.

**Audit Date:** 2026-10-08  
**Auditor:** ComplaintScope Systemic Verification Engine  
**Status:** ✅ ALL CHECKS PASSED (Zero Discrepancies)

---

## 1. Corpus & Partition Consistency

| Quantity | Master Config (`config.yaml`) | Data Pipeline (`src/data.py`) | Progress Tracker (`PROGRESS.md`) | Academic Report (`report/report.md`) | Presentation Deck (`slides/presentation.md`) | Verification Status |
|---|---|---|---|---|---|---|
| Sample Size | 20,000 target | 19,998 clean | 19,998 | 19,998 | 19,998 | ✅ Consistent |
| Train Count | 70% | 13,983 | 13,983 | 13,983 | 13,983 | ✅ Consistent |
| Val Count | 15% | 2,999 | 2,999 | 2,999 | 2,999 | ✅ Consistent |
| Test Count | 15% | 3,016 | 3,016 | 3,016 | 3,016 | ✅ Consistent |
| Train Cutoff Date | — | 2022-03-17 | 2022-03-17 | 2022-03-17 | 2022-03-17 | ✅ Consistent |
| Val Cutoff Date | — | 2022-08-12 | 2022-08-12 | 2022-08-12 | 2022-08-12 | ✅ Consistent |
| Consolidated Products | 9 | 9 | 9 | 9 | 9 | ✅ Consistent |

---

## 2. Component Metric Consistency

### Component 1: Product Classification
- **Champion Model:** `LinearSVC (calibrated)` across all documents.
- **Test Macro-F1:** `0.7394` in `classification_results.csv`, `classification_report.json`, `report.md`, and `presentation.md`.
- **Test Accuracy:** `87.43%` (`0.8743`) in all tables and slides.
- **Bootstrap 95% CI:** `[0.7079, 0.7666]` in all locations.
- **AQ3 Drift Drop:** $\Delta = -0.2013$ (Chrono F1 0.7317 vs Random F1 0.9330) matched across `aq3_split_drift.json`, `report.md`, and `DECISIONS.md`.
- **McNemar's Test:** $\chi^2 = 535.64, p = 1.67 \times 10^{-118}$ identical in `mcnemar_test.json` and `report.md`.

### Component 2: Relief-Risk Prediction
- **Champion Model:** `Text LR` across all documents.
- **Test PR-AUC:** `0.3865` in `relief_results.csv`, `report.md`, `PROGRESS.md`, and `presentation.md`.
- **Test ROC-AUC:** `0.6063` matched across all tables.
- **Test Brier Score:** `0.2316` matched across all tables.
- **Operational Lift@5%:** `1.41x` (`44.67% precision`) matched in `relief_results.csv` and report text.
- **Company Feature Ablation:** With-company PR-AUC = `0.3700` vs Without-company = `0.3865` in `company_feature_ablation.json`, `DECISIONS.md`, and `report.md`.

### Component 3a: Latent Topic Discovery
- **Selected Topic Model:** `LDA with k=16` across all files.
- **Optimal Coherence ($c_v$):** `0.5009` in `topic_sweep_results.csv`, `report.md`, and `presentation.md`.
- **Topic Diversity:** `0.7312` matched in sweep table and slides.

### Component 3b: Emerging Issue Detection
- **Dual Detectors:** Rolling Z-score ($window=12, th=2.0$) and EWMA-CUSUM ($span=6, th=1.5$).
- **Pre-registered Proxies:** 5 signals (`covid_relief`, `overdraft_fee`, `credit_reporting`, `debt_collection`, `mortgage_forbearance`).
- **Precision / F1 Metrics:** Matched exactly with `burst_detection_summary.csv` and `proxy_validation.json`.

### Component 4: Network Analysis
- **Bipartite Nodes:** 2,502 companies, 170 issues, 18,204 edges in `network_metrics.json` and all reports.
- **Projected Nodes:** 100 institutions, 3,774 weighted edges.
- **Louvain Communities:** 3 communities, Modularity $Q = 0.2568$ matched.
- **Null Model P-Value:** $p = 0.000$ ($p < 0.001$, 100 permutations, null mean $Q = 0.0671$).

### Component 5: Systemic Risk Index (SRI)
- **Top 3 Institutions:** TransUnion (0.7819), Experian (0.7187), Equifax (0.6825) identical in `systemic_risk_index.csv`, `app/artifacts/sri_table.csv`, `report.md`, and `presentation.md`.
- **Equifax Relief Anomaly:** 4.3% relief rate noted consistently across all analysis sections.
- **Dirichlet Sensitivity:** Mean Kendall's $\tau = 0.6374 \pm 0.2321$ across 100 perturbations in `sri_sensitivity.json`, `report.md`, and slides.

---

## 3. Artifact Validation Audit

- Total Artifacts in `app/artifacts/`: 12 files
- Cumulative Artifact Size: **9.4 MB** (Requirement: < 100 MB) ✅ PASSED
- Standalone Execution: No raw data files (`data/raw/`) imported by `app/streamlit_app.py` ✅ PASSED
- Pytest Test Suite: 19 / 19 tests passing in 9.23 seconds ✅ PASSED
- Generated Documents:
  - `report/ComplaintScope_Academic_Report.docx` (301 KB, formatted tables + embedded figures) ✅ PASSED
  - `slides/ComplaintScope_Presentation.pptx` (2.36 MB, 22 custom styled slides + figures) ✅ PASSED
  - `notebooks/01_data_understanding_eda.ipynb` through `09_systemic_risk_index.ipynb` (9/9 notebooks) ✅ PASSED

# CBS3009 Rubric Coverage Audit

**Course:** CBS3009 – Advanced Social, Text and Media Analytics  
**Project:** ComplaintScope  
**Grading:** 20 Marks Total

---

## Rubric Item Coverage Matrix

| Rubric Item | Max Marks | Evidence Location | Status |
|---|---|---|---|
| **Dataset Documentation** | 2 | `data/DATASET_CARD.md` – Datasheets-for-Datasets standard; funnel table with real row counts; provenance, SHA-256, schema, bias documentation | ✅ Complete |
| **Exploratory Data Analysis** | 2 | `results/figures/fig01_*` through `fig06_*`; temporal distribution, product breakdown, narrative length, submission channel, state heatmap, relief imbalance | ✅ Complete |
| **Text Preprocessing & Justification** | 2 | `src/preprocess.py`; `results/tables/ablation_preprocessing.csv` – 7-config ablation; before/after text examples saved | ✅ Complete |
| **Feature Engineering** | 2 | `src/features.py`; BoW, sublinear TF-IDF (30K features), sentence-transformers (all-MiniLM-L6-v2), metadata OHE; Zipf plot; class top-terms; UMAP/PCA projection | ✅ Complete |
| **Classification (Product Triage)** | 3 | `src/classify.py`; 7-model suite; chrono grid search on val; test: Macro-F1 ± 95% CI; McNemar's test; AQ3 drift; error taxonomy (60 samples) | ✅ Complete |
| **Prediction (Relief Risk)** | 3 | `src/relief.py`; PR-AUC, ROC-AUC, Brier score, Lift@5/10/20%; calibration curve; triage gain simulation; company ablation; fairness slices | ✅ Complete |
| **Topic Modelling** | 2 | `src/topics.py`; LDA + NMF + KMeans; coherence (c_v) sweep; diversity metric; human-readable labels; topic-product heatmap | ✅ Complete |
| **Emerging Issue Detection** | 2 | `src/burst.py`; rolling z-score + EWMA/CUSUM; 5 pre-registered keyword proxies; precision/recall/F1 + lead-lag; proxy timestamps committed before analysis | ✅ Complete |
| **Network Analysis** | 2 | `src/network.py`; bipartite graph; cosine projection; 5 centrality measures; Louvain communities; null model (100 iterations, p-value reported); topic breadth; Pyvis interactive | ✅ Complete |
| **Systemic Risk Index** | 1 | `src/sri.py`; 5-dimension composite; Dirichlet sensitivity (100 perturbations); Kendall's τ rank stability; regulatory insights matrix | ✅ Complete |
| **Dashboard** | 2 | `app/streamlit_app.py`; 5 pages; real-time triage; topic explorer; interactive network; SRI ranking; model metrics; headless smoke test in `docs/DEPLOYMENT.md` | ✅ Complete |
| **Report & Slides** | 1 | `report/report.md` → `report/ComplaintScope_Academic_Report.docx`; `slides/ComplaintScope_Presentation.pptx` (22 slides); `slides/presentation.md` | ✅ Complete |

---

## Analytical Questions (AQs) Coverage

| AQ | Question | Evidence |
|---|---|---|
| AQ1 | What product category best explains this complaint? | Phase 4: Classification with 7 models, Macro-F1 reported per class |
| AQ2 | Which narratives signal high relief risk? | Phase 5: Relief prediction with PR-AUC, Lift@k, triage gain curve |
| AQ3 | Does temporal drift affect model performance? | Phase 4: Chronological vs. random test split F1 comparison |
| AQ4 | What latent themes exist in complaints? | Phase 6: LDA + NMF topics with coherence sweep |
| AQ5 | Which new complaint themes are emerging? | Phase 7: Burst detection on topic prevalence + proxy validation |
| AQ6 | Which institutions show systemic complaint patterns? | Phase 8: Network centralities; Phase 9: SRI ranking |
| AQ7 | Does model performance differ by demographic group? | Phase 5: Fairness slices by submitted_via, tags, state |

---

## Anti-Leakage Guardrails

| Guardrail | Implementation |
|---|---|
| Chronological splits | `src/data.py::create_splits()` – strict date boundaries, no boundary crossover |
| Vectorizer fit on train only | `src/features.py` – `vec.fit_transform(train)`, `vec.transform(val/test)` |
| No company identity in generalisation models | `src/relief.py` – metadata features exclude company; company ablation is separate |
| Proxy timestamps committed before burst analysis | `src/burst.py::KEYWORD_PROXIES` – defined as module-level constant pre-analysis |
| No test data in hyperparameter tuning | `src/classify.py::grid_search_on_val()` – tuned on val split only |

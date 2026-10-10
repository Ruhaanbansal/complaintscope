# MASTER PROMPT: ComplaintScope
### Build the complete CBS3009 course project, end to end, production-ready

---

## 0. YOUR ROLE AND HOW YOU MUST WORK

You are a senior applied-data-science engineer and research mentor. You will build, **autonomously and completely**, a final-year B.Tech. course project for **CBS3009 – Advanced Social, Text and Media Analytics** (20 marks, CO5 & CO6). The project will be graded by faculty against a fixed rubric (Section 3). Your goal is that a strict expert reviewer would award **full marks on every rubric line**.

Operating rules for you, the agent:

1. **Work in phases (Section 6).** Finish a phase, run its quality gate, then update `PROGRESS.md` before starting the next. If your context fills up, the user will tell you to "read PROGRESS.md and continue". `PROGRESS.md` must therefore always be accurate enough for you to resume with no other memory.
2. **Never fabricate.** Every number, metric, figure, table, dataset statistic, or claim in the report, slides, dashboard, or README must come from code you actually executed, saved in `results/`. If a result is weaker than hoped, report it honestly and analyse *why*. Honest analysis scores higher than inflated numbers.
3. **Never skip a failing step.** Debug it, fix it, and record the fix in `DECISIONS.md`.
4. **Record analytical decisions.** Every non-trivial choice (sampling, label mapping, preprocessing, hyperparameters, thresholds, model choice) is logged in `DECISIONS.md` as: *Decision, Alternatives considered, Evidence/Reason, Date*. The rubric rewards analytical decision-making, not just execution.
5. **Everything free.** Use only free, open-source software and free tiers. No paid APIs, no API keys, no scraped data.
6. **Keep the structure simple** (Section 4). Do not create extra layers of folders or frameworks.
7. **Explain as you go.** Notebook markdown cells must explain *why* each step is done, not just what.
8. **When something is ambiguous, choose the most defensible option, log it in `DECISIONS.md`, and continue.** Do not stop to ask unless you are blocked by something only the human can do (see Section 12).
9. **Verify before relying on external facts.** The dataset URL, column names, category labels, and any literature references must be checked against the live source or actual file. If web access is unavailable, say so and use the fallback in Phase 1.

---

## 1. PROJECT CONTEXT (the human fills this in before running)

```
PROJECT_TITLE        : ComplaintScope: A Text, Topic and Network Analytics System for Consumer-Complaint Triage and Early Warning
TEAM_MEMBERS         : Ruhaan bansal - 23BBS0046, Vedant Rajesh - 23BBS0037, Anish Desai - 23BBS0119
INSTITUTION          : VIT Vellore
COURSE               : CBS3009 – Advanced Social, Text and Media Analytics
FACULTY              : Sathish Kumar K
SUBMISSION_DATE      : 11/10/2026
OWN_CONTRIBUTION_NOTES: [Optional: anything the team has already done]
HARDWARE             : [e.g. 16 GB RAM, 4-core CPU, no GPU]   <- sets default mode (fast/full)
```

If any field is still in `[brackets]`, use the placeholder text, keep it clearly marked `[TO BE FILLED BY TEAM]` in the report/slides, and list it in the final hand-off.

---

## 2. THE PROJECT IN ONE PARAGRAPH

Regulators and financial institutions receive very large volumes of free-text consumer complaints. Three operational problems follow: **(a)** complaints are routed to the wrong team or category, **(b)** complaints likely to end in consumer relief are not prioritised, and **(c)** systemic or emerging issues (a new fraud pattern, a policy-driven spike) are noticed late because humans must read thousands of narratives. **ComplaintScope** is an integrated analytics pipeline over the public **US CFPB Consumer Complaint Database** that: (1) classifies a complaint's product category from its narrative, (2) estimates the risk the complaint ends in relief to support prioritisation, (3) discovers topics and detects emerging issues over time, validated against independent keyword-based proxy signals, (4) builds a company–issue network to find structural clusters and shared systemic problems, and (5) fuses these into a transparent **Systemic Risk Index** and a Streamlit dashboard for demonstration.

### 2.1 Measurable objectives (report these exactly; fill thresholds after baselines are run)

| ID | Objective | Primary metric | Success criterion |
|----|-----------|----------------|-------------------|
| O1 | Classify product category from narrative text | Macro-F1 on chronologically held-out test set | Best model beats majority and dummy baselines by a statistically significant margin (bootstrap 95% CI non-overlapping or McNemar p < 0.05); target set after baseline |
| O2 | Predict whether a complaint ends in relief (monetary or non-monetary) | PR-AUC (average precision), Recall@Top-10% | Beats prior-rate baseline; Recall@10% lift > 1.0 over random, with CI |
| O3 | Discover coherent topics and detect emerging issues | c_v coherence; alert precision/recall against proxy series | Coherence reported for k sweep; alerts evaluated against ≥ 4 keyword proxy events |
| O4 | Reveal structure among companies and issues | Modularity, centralities, null-model comparison | Communities significantly more modular than a degree-preserving random null |
| O5 | Integrate into an actionable system | Working dashboard + Systemic Risk Index | Dashboard runs from a clean checkout in ≤ 10 minutes using saved artifacts |

### 2.2 Analytical questions the project must answer explicitly (each gets a "Finding" in the report)

- AQ1: Which product categories are most confusable from narrative text alone, and why?
- AQ2: Does adding structured metadata (issue, channel, tags) improve relief prediction beyond text alone? By how much?
- AQ3: How much does performance drop when evaluated on *future* data versus a random split (temporal-leakage effect)?
- AQ4: Which preprocessing choices materially change performance (ablation)?
- AQ5: Which topics grew fastest, and do detected bursts align with independent keyword proxies?
- AQ6: Do companies cluster by complaint profile, and are those clusters more than chance?
- AQ7: Is model performance equitable across submission channels, consumer tags (e.g. Older American, Servicemember), and state groups?

---

## 3. RUBRIC ALIGNMENT CONTRACT (this is the grading standard; satisfy every cell)

Source: *CBS3009 Course Project Guidelines*. 20 marks. Excellent = top descriptor.

| Rubric component | Marks | What "Excellent" requires | Where you will deliver it |
|---|---|---|---|
| Problem Definition & Objectives | 2 | Clear, relevant, well-motivated; specific, measurable objectives; explicit analytical questions | Report §1, slide 2–4, README, Section 2 above |
| Data Collection & Preprocessing | 3 | Appropriate and justified; dataset documented (source, size, attributes, format, limitations); WHY for every step | `data/DATASET_CARD.md`, notebooks 01–03, report §3 |
| Methodology & Algorithm Selection | 4 | Technically sound, justified; ≥ 3 major analytical components; method comparison with justified final choice | Notebooks 04–08, report §3, architecture diagram |
| Implementation & Experimental Analysis | 4 | Complete and reproducible; executable notebooks; experiments, ablations, baselines | `src/`, `notebooks/`, `Makefile`, `tests/`, report §4 |
| Results, Evaluation & Interpretation | 3 | Thorough interpretation; correct metrics; observation vs inference; limitations | `results/`, report §4–5, `results/figure_catalog.csv` |
| Innovation / Problem-Solving | 2 | Strong originality/application | Proxy-validated emerging-issue detector, leakage-aware temporal evaluation, Systemic Risk Index, fairness slices, triage simulation |
| Presentation & Demonstration | 2 | Clear technical demonstration | Slides, Streamlit app, `docs/DEMO_SCRIPT.md` |

Course-specific requirements you must also satisfy (from the guideline deck):
- ≥ 3 major analytical components (we deliver **five**).
- Pipeline: Data Collection → Preprocessing → Feature Representation → Analytics/ML → Evaluation → Visualization → Insights, with rationale at each stage.
- Text preprocessing: tokenization, stop-word handling, lemmatization/normalization **where justified**; features: BoW, TF-IDF, cosine similarity.
- Classification: Naïve Bayes, Decision Tree and other suitable classifiers; metrics: Accuracy, Precision, Recall, F1, confusion matrix.
- Clustering/Topic: K-Means or hierarchical clustering **and** LDA/topic modelling; Silhouette score with interpretation.
- Social-network analysis: nodes, edges, direction, weights, attributes; degree, betweenness, closeness, eigenvector centrality, community analysis.
- Compare ≥ 2 methods wherever appropriate and justify the final choice.
- Visualisations: titles, labelled axes, a stated key finding per figure, observation separated from inference, limitations and actionable insights.
- Deliverables: Final Report; Source code/Notebooks; Dataset or documented source; Results/evaluation tables/visualisations; Presentation slides; Working demonstration.
- Academic integrity: cite datasets, papers, libraries, pretrained models; identify the team's own contribution; respect privacy and licensing; never expose personal information unnecessarily.
- Submission must be internally consistent and reproducible.

---

## 4. REPOSITORY STRUCTURE (simple; create exactly this)

```
complaintscope/
├── README.md                    # What, why, quick start, structure, results headline, citations
├── requirements.txt             # Pinned versions (after tested install)
├── config.yaml                  # ALL parameters: paths, seeds, dates, sample sizes, grids, thresholds
├── product_mapping.yaml         # Raw product label -> consolidated class (documented)
├── Makefile                     # make setup | data | all | app | report | slides | test | clean | fast
├── PROGRESS.md                  # Phase checklist and resume notes (you maintain this)
├── DECISIONS.md                 # Analytical decision log (you maintain this)
├── CONTRIBUTIONS.md             # Team's own contribution + reused resources (academic integrity)
│
├── data/
│   ├── DATASET_CARD.md          # Datasheet: source, licence, size, schema, collection, limits, ethics
│   ├── raw/                     # Downloaded files (git-ignored; script re-downloads)
│   ├── interim/                 # Filtered/cleaned parquet (git-ignored)
│   ├── processed/               # Splits, features metadata (small files only)
│   └── sample/                  # complaints_demo_2k.csv  (committed; for tests and demo)
│
├── src/
│   ├── __init__.py
│   ├── config.py                # load config.yaml, set seeds, path helpers, logging
│   ├── data.py                  # download, verify, chunked load, filter, sample, split
│   ├── preprocess.py            # cleaning, redaction handling, tokenisation, lemmatisation
│   ├── features.py              # BoW, TF-IDF, embeddings, metadata encoders, cosine kNN
│   ├── classify.py              # product classification (train/eval/compare)
│   ├── relief.py                # relief-risk prediction, top-k, calibration, fairness slices
│   ├── topics.py                # LDA/NMF/K-Means, coherence, silhouette, topic labelling
│   ├── emerging.py              # prevalence series, burst detection, proxy validation
│   ├── network.py               # bipartite/projection graphs, centralities, communities, null model
│   ├── risk_index.py            # Systemic Risk Index (fusion of components)
│   ├── evaluate.py              # metrics, bootstrap CI, McNemar, plotting helpers
│   ├── viz.py                   # shared plotting style, figure saving + catalog registration
│   ├── report_builder.py        # builds DOCX (and PDF if possible) from report/report.md
│   └── slides_builder.py        # builds PPTX from results
│
├── notebooks/                   # Thin, narrative, executable; logic lives in src/
│   ├── 01_data_understanding_eda.ipynb
│   ├── 02_preprocessing_and_ablation.ipynb
│   ├── 03_feature_representation.ipynb
│   ├── 04_product_classification.ipynb
│   ├── 05_relief_risk_prediction.ipynb
│   ├── 06_topic_modelling_and_clustering.ipynb
│   ├── 07_emerging_issue_detection.ipynb
│   ├── 08_network_analysis.ipynb
│   └── 09_integration_systemic_risk_and_insights.ipynb
│
├── app/
│   ├── streamlit_app.py         # Dashboard (5 pages)
│   └── artifacts/               # Small saved models/data for the app (<100 MB total)
│
├── results/
│   ├── figures/                 # fig_<nn>_<slug>.png (200 dpi)
│   ├── tables/                  # CSV + Markdown versions of every result table
│   ├── metrics/                 # JSON: single source of truth for every reported number
│   ├── figure_catalog.csv       # fig id, title, file, notebook, Observation, Inference, Limitation
│   └── consistency_audit.md     # Final cross-check of report/slides numbers vs results/
│
├── report/
│   ├── report.md                # Final report (source)
│   ├── references.bib or references.md
│   └── ComplaintScope_Report.docx  (+ .pdf if conversion available)
│
├── slides/
│   └── ComplaintScope_Presentation.pptx
│
├── docs/
│   ├── rubric_coverage.md       # Rubric line -> evidence file mapping (a checklist the reviewer can follow)
│   ├── DEMO_SCRIPT.md           # Timed 8–10 min demo and presentation script
│   ├── VIVA_PREP.md             # 40+ likely viva questions with grounded answers
│   ├── RESULTS_TRACEABILITY.md  # Each report claim -> notebook/figure/metrics file
│   └── DEPLOYMENT.md            # Streamlit Community Cloud / Hugging Face Spaces steps
│
└── tests/
    ├── test_preprocess.py
    ├── test_splits_no_leakage.py
    ├── test_network.py
    └── test_smoke_pipeline.py
```

---

## 5. ENVIRONMENT AND TOOLING

- Python 3.10–3.12; create `.venv`. Tooling must run on CPU and 8–16 GB RAM.
- Core libraries (install, test imports, then pin exact working versions in `requirements.txt`): `pandas, numpy, scipy, scikit-learn, pyarrow, nltk, spacy (+ en_core_web_sm), gensim, networkx, python-louvain, pyvis, matplotlib, seaborn, plotly, wordcloud, sentence-transformers (CPU torch), statsmodels, joblib, pyyaml, tqdm, requests, jupyter, nbconvert, nbformat, ipykernel, pytest, streamlit, python-pptx, python-docx, pypandoc_binary, jinja2`.
- **Compatibility warning:** `gensim` constrains `numpy`/`scipy` versions. Resolve this at install time and verify `import gensim` works before proceeding. Log the pinned set in `DECISIONS.md`.
- **Two modes in `config.yaml`:** `mode: fast` (≈ 20k-complaint sample; whole pipeline in < 15 minutes; used for smoke tests and CI) and `mode: full` (≈ 150k sample or as hardware allows). Always run `fast` first end to end, then `full`. Reported results must come from `full`.
- Global seed = 42, set for numpy, random, sklearn, gensim, torch. All stochastic components take `random_state`.
- Logging via `logging`, not `print`, in `src/`. Save run metadata (`results/metrics/run_metadata.json`: date, git hash if any, library versions, mode, seed, sample sizes, runtime per phase).
- Initialise git, create `.gitignore` (raw/interim data, `.venv`, large artifacts, notebook checkpoints).
- Notebooks must run top-to-bottom with `jupyter nbconvert --execute`, with outputs saved. `make all` executes them in order. Notebooks import from `src/`; they contain explanations, calls, plots, and interpretation (Observation / Inference / Limitation), not duplicated logic.

---

## 6. PHASES (execute in order; each ends with a QUALITY GATE)

### PHASE 0: Project scaffold
Create the structure in Section 4, `config.yaml`, `Makefile`, `PROGRESS.md` (phase checklist), `DECISIONS.md`, `CONTRIBUTIONS.md` (initial), `.gitignore`, `requirements.txt`, and `src/config.py`.
`config.yaml` must include: paths, seed, mode, `date_start` (default `2018-01-01`), `date_end` (latest complete month found in data), `sample_size_fast`, `sample_size_full`, `min_narrative_words` (default 20), split ratios (chronological 70/15/15), vectoriser parameters, model grids, bootstrap `n_boot` (default 1000), top-k fractions `[0.05, 0.10, 0.20]`, LDA k-range, burst parameters, network thresholds, figure dpi/palette.
**Gate:** `make test` passes (even if trivially), imports work, `PROGRESS.md` updated.

### PHASE 1: Data collection and dataset documentation (Rubric: Data Collection 3)
**Source:** US CFPB *Consumer Complaint Database* (public, US government open data). Expected bulk file: `https://files.consumerfinance.gov/ccdb/complaints.csv.zip`. Alternative: the official search API documented on the CFPB website. **Verify the URL, current column names, licence/terms statement, and update frequency on the live site** and record them with the access date in `DATASET_CARD.md`.

Steps:
1. `src/data.py::download()`: stream the zip with progress, verify size > 0, store SHA-256 in `results/metrics/data_provenance.json`, retry on failure. If the network is blocked or the download fails, **do not invent data**. Print exact manual instructions (URL to open, where to place the file, expected filename) and continue using `data/sample/` only for smoke tests; mark the full run as BLOCKED in `PROGRESS.md` and tell the user.
2. **Chunked loading** (`chunksize` ~200k rows, `usecols` limited to the needed columns): Date received, Product, Sub-product, Issue, Sub-issue, Consumer complaint narrative, Company public response, Company, State, ZIP code (read but **drop before saving**; privacy), Tags, Consumer consent provided?, Submitted via, Date sent to company, Company response to consumer, Timely response?, Complaint ID. Column names may differ; map and log.
3. Whole-corpus aggregates (computed in the same chunked pass, over **all** rows, including those without narratives): monthly counts by product; monthly counts by company; monthly counts by (product, issue); monthly counts of narrative-bearing complaints; monthly counts of keyword-proxy hits (Section Phase 7). Save to `data/interim/aggregates_*.parquet`. These support trends and the network using full data cheaply.
4. Modelling corpus: keep rows with non-null narrative, `date_start ≤ date < date_end`, narrative ≥ `min_narrative_words`. Drop exact-duplicate narratives (log the count). Drop the dangerous or unusable labels (see below). Save to `data/interim/complaints_clean.parquet`.
5. **Sampling:** draw a random sample **proportional to month** (preserves time distribution so topic-prevalence proportions remain unbiased). Size from `config` by mode. Record the sampling procedure, seed, and counts in `DECISIONS.md`.
6. **Product label harmonisation:** the CFPB product taxonomy changed over the years (e.g. credit-reporting, payday-loan, prepaid-card categories were merged or renamed). Inspect `value_counts()` of the actual Product column; build `product_mapping.yaml` mapping raw labels to **7–10 consolidated classes**. Expected consolidated classes (verify against actual data): *Credit reporting & repair; Debt collection; Mortgage; Credit/prepaid card; Checking/savings account; Student loan; Vehicle/consumer loan; Money transfer/virtual currency; Payday/personal loan.* Merge or drop classes with < 1,000 sampled complaints. Document the mapping table in the report.
7. **Relief label (O2):** derived from *Company response to consumer*. `relief = 1` for labels indicating monetary relief, non-monetary relief, or "closed with relief"; `relief = 0` for "closed with explanation", "closed without relief", "closed"; **exclude** "In progress" and "Untimely response". Verify the real label set; document the mapping. Note in limitations that the label is the *company's* decision, not an objective measure of merit.
8. **Chronological split:** train = earliest 70% of the dates, validation = next 15%, test = latest 15%, split by **date boundaries** (not random rows); make no complaint cross a boundary. Save split indicators and the boundary dates. Also create a *random* 70/15/15 split solely for AQ3 (leakage-effect comparison).
9. **Demo sample:** write `data/sample/complaints_demo_2k.csv` (2,000 narrative rows, random, columns reduced to what the app/tests need, no ZIP, no company names removed; they are public, but strip anything that looks like a personal identifier such as emails or phone numbers via regex before saving).
10. **`data/DATASET_CARD.md`** (datasheet): name, publisher, URL, access date, licence/terms (quote what the site says), update frequency, total rows at download, rows with narratives, rows after each filtering step (a funnel table), date range, schema table (column, type, description, use in project, missing %), class distributions, known biases (voluntary submission, narrative-consent selection, company-reported outcomes, redaction), privacy handling (redaction by CFPB, ZIP dropped, no re-identification attempt), ethical statement, reproducibility instructions.
**Notebook 01** (EDA): funnel; missingness; product and issue distribution; monthly volume trend; narrative length distribution; share of narratives with redaction tokens; top companies; duplicates; relief rate by product and over time; a short list of "data quality findings" and what each implies for preprocessing.
**Gate:** `DATASET_CARD.md` complete with real numbers; split-leakage test passes (`tests/test_splits_no_leakage.py`: max(train date) < min(val date) < ... , no ID overlap); `PROGRESS.md` updated.

### PHASE 2: Preprocessing and ablation (Rubric: Preprocessing, "explain WHY")
Implement `src/preprocess.py` as small, individually testable functions, each with a docstring stating the **reason** for the step:
- **Normalisation:** lowercase; Unicode normalise; collapse whitespace.
- **Redaction handling:** CFPB masks personal details as `XXXX`, `XX/XX/XXXX`, `{$123.45}`. Variants: (a) delete, (b) replace with a placeholder token (`<redacted>`, `<date>`, `<amt>`). Ablate.
- **Noise removal:** URLs, emails, phone numbers (also a privacy safeguard), repeated punctuation, stray HTML.
- **Tokenisation:** spaCy (disable parser/NER for speed) or NLTK; keep alphabetic tokens ≥ 2 chars.
- **Stop-words:** NLTK English list; add domain stop-words (e.g. `account, company, would, called, told`) **for topic modelling only**, justified by topic-word inspection. Keep negations (`not, no, never`) for classification: justify.
- **Lemmatisation** (spaCy) vs. stemming (Porter): compare.
- **N-grams:** unigram vs. uni+bigram.
- Process in batches with `nlp.pipe(..., n_process=...)`; cache outputs to parquet (`data/interim/complaints_prepped.parquet`).
**Ablation study (Notebook 02):** fixed classifier (Logistic Regression on TF-IDF), fixed split, vary one factor at a time: raw-lower baseline → + redaction handling variants → + stop-word removal → + lemmatisation vs stemming → + bigrams → + negation retention. Evaluate on the **validation** set (never test). Table: configuration, macro-F1, accuracy, vocabulary size, fit time. State the chosen pipeline and the evidence (AQ4). Include before/after text examples.
**Gate:** `tests/test_preprocess.py` passes (cases for each function, including redaction and negation); ablation table saved to `results/tables/`; `DECISIONS.md` updated.

### PHASE 3: Feature representation (Notebook 03)
- **BoW** (`CountVectorizer`) for Naïve Bayes and LDA; **TF-IDF** (`TfidfVectorizer`, sublinear TF, `min_df`≥5, `max_df`≤0.5, ngram range from ablation, `max_features` from config). **Fit vectorisers on train only**; transform val/test.
- **Sentence embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (free, CPU). Truncate to 256 tokens, batch encode, cache `.npy`. Use for (a) a comparison classifier, (b) nearest-neighbour search, (c) K-Means topic clustering comparison. Record encoding time. Cite the model.
- **Cosine similarity:** implement kNN retrieval on TF-IDF and embeddings (`features.py::nearest_neighbours`); evaluate qualitatively (show 5 queries with their top-3 neighbours) and quantitatively (does the neighbour share the product label? precision@k for both representations). This supports the dashboard's "similar complaints" feature and near-duplicate analysis.
- **Metadata encoders** for relief prediction: one-hot for submission channel, tags (Older American / Servicemember / none), top-N states + "other", issue (top-N + "other"). **Company is excluded from the primary model** (company identity acts as a proxy and limits generalisation to new firms); evaluate it only in an ablation.
- Visualise: vocabulary frequency (Zipf plot), top TF-IDF terms per class, 2-D projection (TruncatedSVD or UMAP-free alternative: TruncatedSVD→t-SNE on a 5k subsample) coloured by product.
**Gate:** features reproducible from config; no fit on val/test (assert in code and in the test file).

### PHASE 4: Component 1, Product classification (Notebook 04; Rubric: Methodology 4, Results 3)
**Features:** text only (never the Issue/Sub-product columns; they leak the label).
**Models (all with identical splits):**
1. Dummy baselines: most-frequent, stratified.
2. Multinomial Naïve Bayes and Complement Naïve Bayes (BoW/TF-IDF).
3. Decision Tree (depth-limited, on TF-IDF with chi² feature selection to keep it tractable); show it as the interpretable baseline.
4. Logistic Regression (`saga`/`liblinear`, class-weighted).
5. Linear SVM (`LinearSVC`, class-weighted).
6. Sentence-embedding + Logistic Regression.
Hyperparameters via a **chronological** validation procedure (use the validation split; or `TimeSeriesSplit` on train), small grids from `config`. Record every trial in `results/tables/classification_grid.csv`.
**Evaluation (test set, once, after model selection):** Accuracy, macro and weighted Precision/Recall/F1, per-class report, normalised confusion matrix, **95% bootstrap CIs** for macro-F1 (n_boot from config), **McNemar's test** between the top two models, training time and inference latency per 1,000 complaints.
**AQ3 experiment:** train/evaluate the best configuration on the *random* split and the *chronological* split; report the gap and explain (vocabulary drift, new categories, topical shift).
**Error analysis:** top-10 confused class pairs; most discriminative terms of the confused classes; **read 60 actual misclassified examples** (stratified over confused pairs), assign each an error type from a taxonomy you derive from them (e.g. multi-product narrative, label ambiguity after taxonomy merge, short narrative, boilerplate-dominated), and report the counts. Base this only on printed examples; save them to `results/tables/error_examples.csv` (narratives truncated, no identifiers).
**Gate:** all tables/figures saved; selected model + vectoriser saved with `joblib` to `app/artifacts/`; final choice justified in prose with numbers drawn from `results/metrics/classification.json`.

### PHASE 5: Component 2, Relief-risk prediction and triage simulation (Notebook 05)
**Task:** binary `relief`. **Class imbalance** is expected; do not use accuracy as the headline metric.
**Models:** prior-rate baseline; LR on TF-IDF (text only); LR on TF-IDF + metadata; `HistGradientBoostingClassifier` on metadata + SVD(≈200) of TF-IDF; ablation adding Company (to quantify the proxy effect, AQ2).
**Metrics:** PR-AUC (average precision), ROC-AUC, Brier score, calibration curve (reliability diagram; calibrate with isotonic/Platt on validation if needed), **Precision@k, Recall@k and Lift@k for k ∈ {5%, 10%, 20%}** with bootstrap CIs.
**Triage simulation:** "If a reviewer team can examine the top-k% of incoming complaints, what share of eventual-relief complaints are captured versus random ordering?" Plot cumulative gain and lift curves on the test set, chronologically.
**Explainability:** top positive/negative terms from LR coefficients (with a note that these show association, not causation), permutation importance for metadata features, 5 worked local explanations (per-complaint contribution of terms).
**Fairness and robustness slices (AQ7):** ROC-AUC, PR-AUC, and Recall@10% by submission channel, by consumer tag, by top-10 states vs rest, by product. Report gaps with CIs; flag any slice with materially worse recall; discuss what an operator should do (monitoring, threshold review, human oversight). State clearly that ZIP code was dropped and that the model must not be used to deny service, only to prioritise review.
**Gate:** all metrics JSON saved; calibration, gain, and fairness figures saved; limitations paragraph drafted from results.

### PHASE 6: Component 3a, Topic discovery and clustering (Notebook 06)
- **Models:** LDA (gensim) on the BoW with domain stop-words; NMF (sklearn) on TF-IDF; K-Means on TF-IDF-SVD and on sentence embeddings (hierarchical clustering on a 10k subsample, as a required comparison technique).
- **Model selection:** sweep k (e.g. 8–40, step 4 or per config) and compute **c_v coherence** (gensim `CoherenceModel`) and topic diversity (fraction of unique words in top-10 across topics); pick k by coherence/diversity and interpretability (justify, log). For K-Means: **Silhouette score** (on a subsample) and elbow inertia; **interpret** the discovered clusters (top terms, dominant product, size), do not just report the score.
- **Compare** LDA vs NMF vs K-Means(embeddings): coherence, diversity, silhouette (where applicable), runtime, interpretability. Choose the primary topic model and justify.
- **Topic labelling:** propose short human-readable labels from actual top words and representative documents; save `app/artifacts/topic_labels.json`. Show topic-word bar charts, word clouds (supplementary only), intertopic distance via 2-D projection, topic × product heatmap, and topic prevalence over time (static view for now).
- Assign each complaint its dominant topic and topic mixture; save for downstream use.
**Gate:** coherence sweep figure; labelled topic table with top-words, size, dominant product, relief rate; comparison table saved.

### PHASE 7: Component 3b, Emerging-issue detection with independent validation (Notebook 07; **core innovation**)
**Idea:** If topics are only descriptive, they are not an early-warning system. We test whether bursts in topic prevalence are real by comparing them with **independent keyword proxies** computed from the *full* corpus aggregates (not from the topic model).
1. **Series:** monthly prevalence (share) of each topic (from the sample; proportions are unbiased because sampling is proportional) with smoothing.
2. **Detectors (compare two):** (a) rolling z-score against the trailing 12-month baseline with threshold (`z ≥ 3`, minimum monthly count, minimum 2 consecutive months configurable); (b) EWMA/CUSUM control chart. Report parameter choices and sensitivity (z-threshold sweep).
3. **Proxy signals (define in `config.yaml` *before* running any detector; this is pre-registration):** at least four keyword families searched in the full narrative corpus counts per month, for example *pandemic/forbearance* (`covid|coronavirus|pandemic|forbearance|cares act|stimulus`), *scam/fraud transfers* (`zelle|scam|scammed|fraud(ulent)? transfer`), *identity theft* (`identity theft|stolen identity`), *credit-report errors* (`not my account|incorrect information|inaccurate`), *student-loan servicing* (`forbearance|servicer|repayment pause`), *virtual currency* (`bitcoin|crypto|coinbase`). Adjust keywords after inspecting the data, but **log every change before looking at detector output**. Proxy "event" months are those where the proxy series itself bursts (same detector on the proxy series).
4. **Evaluation:** for each matched (topic, proxy) pair, compute **alert precision, recall, F1, and median detection lead/lag in months**, and correlation between the topic series and the proxy series. Also show a **false-alarm analysis**: alerts with no proxy match, inspected via representative narratives to decide whether they are plausible real issues or noise (observation vs inference).
5. **Context check (optional but valuable):** if web access is available, find 2–3 well-documented public events (regulatory actions, CFPB reports, widely reported scams) that correspond to detected bursts and cite them with URLs and dates. Include only sources you actually opened and verified; otherwise omit.
6. **Figures:** topic prevalence with alert markers; proxy-vs-topic overlay; lead/lag histogram; detector sensitivity curve.
**Gate:** proxy definitions committed with timestamps in `DECISIONS.md` before the evaluation run; evaluation table saved; limitations written (proxy is imperfect ground truth, regex ambiguity, sampling noise in small months).

### PHASE 8: Component 4, Network analysis (Notebook 08)
Use the **full-corpus aggregates** for company–issue counts (more edges, better structure).
1. **Bipartite graph** B: company nodes (companies with ≥ `min_complaints` in the window; attributes: total complaints, dominant product, state-count if available) × **issue nodes** (consolidated product + issue); edge weight = complaint count, with a normalised weight (company share). **Directed/weighted details:** document explicitly that the bipartite graph is undirected-weighted and the company-company projection is undirected-weighted; also build a **directed** issue-transition graph if data support (e.g. issue → sub-issue hierarchy) or, at minimum, justify why direction is not meaningful here (rubric asks for direction).
2. **Company–company projection:** cosine similarity between companies' issue-share vectors; keep edges with similarity ≥ τ or each node's top-k neighbours (justify, run sensitivity); remove isolates; report graph size, density, components.
3. **Centralities:** degree, weighted degree, closeness, betweenness, eigenvector (with `max_iter` handled). Table of top-15 companies per measure; interpret each measure for this problem (e.g. betweenness = bridge companies spanning issue families; eigenvector = companies embedded in the busiest issue clusters). Correlate centralities with complaint volume to show whether structure adds information beyond volume.
4. **Community detection:** Louvain (python-louvain) with resolution sweep; report modularity, number and size of communities; compare against greedy modularity or label propagation. Characterise each community by dominant product/issue mix and example firms. 
5. **Null model:** generate ≥ 100 randomised graphs (degree-preserving rewiring or shuffled issue shares) and test whether observed modularity exceeds the null distribution (z-score / empirical p). This turns the picture into evidence.
6. **Topic–company link:** build company × topic matrix from Phase 6; compute **breadth** per topic (normalised entropy over companies and share of top-3 companies). Low-breadth topics = firm-specific problem; high-breadth topics = sector-wide systemic issue.
7. **Visuals:** static layout (spring/Kamada-Kawai) coloured by community and sized by weighted degree with labelled top nodes; interactive `pyvis` HTML saved to `app/artifacts/company_network.html`; community × product heatmap.
**Gate:** `tests/test_network.py` passes on a toy graph with known centralities; null-model figure saved.

### PHASE 9: Integration: Systemic Risk Index and insights (Notebook 09; **innovation**)
Define `risk_index.py::systemic_risk_index()` for each topic, over a recent window (e.g. the last 6 full months), as a **transparent, rank-based composite**:
`SRI = mean( rank(burst intensity), rank(recent growth), rank(company breadth), rank(relief rate), rank(complaint volume) )` scaled to 0–100.
State explicitly that it is a **heuristic prioritisation aid, not a validated predictor**; run a **sensitivity analysis** (alternative weights, leave-one-component-out) and report rank stability (Spearman correlation). List the top-5 topics with narrative interpretation and a recommended action for a regulator and for a firm (actionable insights). Add an "insights" table: Insight, Evidence (file/figure), Confidence, Recommended action, Limitation.
**Gate:** `results/tables/systemic_risk_index.csv`, sensitivity figure, insights table.

### PHASE 10: Streamlit dashboard (**working demonstration**)
`app/streamlit_app.py` must run with `streamlit run app/streamlit_app.py` using only `app/artifacts/` and `data/sample/` (**no raw data download required**). Total artifacts < 100 MB (reduce `max_features`, compress with joblib `compress=3`; store topic-month series as small CSV/parquet).
Pages:
1. **Triage:** text box (with 3 example complaints preloaded) → predicted product (top-3 with probabilities), relief-risk score as calibrated probability and **percentile versus reference distribution**, top influencing terms (highlighted in the text), dominant topic and mixture, three most similar complaints (cosine) from the demo sample. Show a visible notice: "Decision support only; not for denying service."
2. **Emerging issues:** topic selector, prevalence line chart with alert markers, alert table, proxy overlay toggle.
3. **Network explorer:** embedded pyvis network; centrality table; community filter.
4. **Systemic Risk Index:** ranked table, component breakdown chart, sensitivity note.
5. **Model performance and about:** key metrics tables/figures, dataset card summary, ethics and limitations, team and course info.
Requirements: cached model loading (`st.cache_resource`), input validation (empty/short text), graceful errors, no external calls, consistent theme, clear labels. Provide `docs/DEPLOYMENT.md` for Streamlit Community Cloud and Hugging Face Spaces (free). Add `app/requirements.txt` if deployment needs a lighter dependency set.
**Gate:** headless smoke test (import app module; call the prediction function on sample text; assert output schema); manual run documented.

### PHASE 11: Testing and reproducibility
- `tests/`: preprocessing units; split no-leakage; network toy graph; smoke test that runs the `fast` pipeline end to end on `data/sample/`.
- `make fast` runs everything on the demo sample in minutes; `make all` runs the full pipeline (data → notebooks → app artifacts → report → slides).
- Run the **entire** pipeline twice from a clean state (delete `interim/`, `results/`, `app/artifacts/`) with the same seed and verify the headline metrics match (store a `results/metrics/reproducibility_check.json`).
- Provide `README.md` quick start: clone → `make setup` → `make data` → `make all` → `make app`, with expected runtimes per phase from `run_metadata.json`.
**Gate:** all tests green; reproducibility check recorded.

### PHASE 12: Report, slides, viva pack, audit (Rubric: all lines + Presentation 2)

**12.1 Final report: `report/report.md` → DOCX (+PDF if possible).** Professional academic style, 35–50 pages, numbered figures/tables with captions that include the key finding, table of contents, list of figures/tables, consistent IEEE-style citations, British or American spelling used consistently. Structure follows the course guideline:
- **Title page** (project title, team, reg. numbers, institution, course, faculty, date); **Certificate/Declaration of originality and Acknowledgements** (placeholders for team to sign); **Abstract** (≤ 250 words, with real headline numbers) and **Keywords**.
- **1. Introduction:** background, problem statement, motivation (with operational examples), objectives O1–O5, analytical questions AQ1–AQ7, scope and out-of-scope, contributions of the team.
- **2. Literature Review:** 15–25 sources across (i) consumer complaint/short-text classification, (ii) topic models (LDA, NMF) and coherence, (iii) burst/trend detection in text streams, (iv) network analysis and community detection, (v) text-classification evaluation under temporal drift, (vi) fairness in triage models. Each source summarised in 2–4 sentences with a **gap table** (existing work vs what this project adds). **Include only references that you have verified exist** (via web search or the source's DOI page). Do not invent citations. Mark any unverifiable item `[VERIFY]` and list them for the team. Foundational works you may use if verified: Blei, Ng & Jordan (2003) LDA; Lee & Seung (1999) NMF; Röder, Both & Hinneburg (2015) coherence measures; Blondel et al. (2008) Louvain; Newman (2006) modularity; Kleinberg (2003) bursty streams; Reimers & Gurevych (2019) Sentence-BERT; Pedregosa et al. (2011) scikit-learn; Řehůřek & Sojka (2010) gensim; Hagberg et al. (2008) NetworkX; Saito & Rehmsmeier (2015) precision-recall vs ROC; McNemar (1947); Efron (1979) bootstrap; Salton & Buckley (1988) term weighting.
- **3. Dataset and Methodology:** dataset (funnel table, schema, limitations), harmonisation, split design (with a timeline diagram), preprocessing (with ablation evidence), features, algorithms per component with *why chosen vs alternatives*, evaluation protocol, system architecture diagram (draw with matplotlib or Mermaid-to-PNG; save as a figure), ethics and privacy.
- **4. Implementation and Results:** experimental setup (hardware, versions, runtimes, seeds); per-component results with tables and figures: classification (comparison table with CIs, confusion matrix, error taxonomy), relief (PR-AUC, gain/lift, calibration, fairness slices), topics (coherence sweep, labelled topics, comparison), emerging issues (alerts vs proxies, lead/lag), network (centralities, communities, null model), integration (SRI).
- **5. Analysis and Discussion:** answer **AQ1–AQ7** one by one with *Finding / Evidence / Interpretation / Caveat*. Separate **Observation** from **Inference** everywhere (use those labels in figure captions). Method comparison and final choices. Actionable insights for regulators and firms. Threats to validity (internal, external, construct), limitations (label noise, redaction, voluntary sampling, company-defined outcome, keyword proxy imperfection), ethical considerations.
- **6. Conclusion and Future Work:** conclusions traceable to results, contributions, realistic enhancements (transformer fine-tuning on GPU, multilingual, streaming deployment, human-in-the-loop evaluation, causal analysis, additional regulators' datasets).
- **References**; **Appendices:** A dataset card, B product mapping, C hyperparameter grids, D full per-class metrics, E additional figures, F reproducibility guide, G team contribution statement (what is original vs reused libraries/models), H glossary.
- Numbers in tables are generated from `results/` by `report_builder.py`; narrative numbers must match (verified in 12.4).
- Build `ComplaintScope_Report.docx` with `pypandoc` (embed figures; use a reference doc for consistent fonts/heading styles, e.g. 11 pt serif body, numbered headings); try PDF via LibreOffice if available. Check the output opens and figures render.

**12.2 Presentation: `slides/ComplaintScope_Presentation.pptx`** (python-pptx, 16:9, 20–22 slides, consistent theme, ≤ 40 words of body text per slide, every slide has a figure/table or a clear diagram, speaker notes with the talk track, slide numbers). Slide plan: 1 Title; 2 Why it matters; 3 Problem and objectives; 4 Analytical questions; 5 Dataset (funnel, schema, limits); 6 Pipeline/architecture; 7 Preprocessing and ablation; 8 Features; 9 Classification setup and comparison; 10 Classification results and errors; 11 Relief-risk results and triage gain; 12 Fairness slices; 13 Topics and clustering; 14 Emerging-issue detection and proxy validation; 15 Network analysis; 16 Systemic Risk Index and insights; 17 Dashboard demo (screenshots; live demo planned); 18 Limitations and ethics; 19 Conclusions and future work; 20 Team contributions and references; 21 Rubric-coverage map; 22 Q&A. Render slides to images to check layout (no overflow/overlap).

**12.3 `docs/` pack:**
- `rubric_coverage.md`: table of each rubric criterion and each checklist item (Section 3 and the 9-point submission checklist) → exact file/section as evidence, with status.
- `DEMO_SCRIPT.md`: minute-by-minute 8–10 minute script (problem → pipeline → 3 key results → live dashboard → limitations → Q&A), the three example complaints to paste, expected outputs, and a fallback plan if the live demo fails (screenshots).
- `VIVA_PREP.md`: **40+ questions with concise, accurate answers grounded in this project's actual results**, covering: why chronological split; why macro-F1; why PR-AUC; what TF-IDF is and why sublinear TF; why NB vs LR vs SVM behave as they do; what LDA assumes; what coherence measures; why z-score vs EWMA; what modularity is and why a null model; what each centrality means here; leakage risks; fairness; limitations; what is the team's own contribution; how to reproduce; what you would do with more time. Include a "numbers to memorise" table from the real results.
- `RESULTS_TRACEABILITY.md`: every claim in the report's abstract/conclusions → figure/table ID → notebook → results file.
- `DEPLOYMENT.md`.

**12.4 Consistency audit (`results/consistency_audit.md`):** programmatically extract headline numbers from `results/metrics/*.json` and check they match report, slides, README, and dashboard text. List every mismatch found and fixed. Verify: all figures referenced exist; every figure appears in `figure_catalog.csv` with Observation/Inference/Limitation; no placeholder like `TODO`, `lorem`, `XXX` (other than the intentional `[TO BE FILLED BY TEAM]` markers) remains; all citations resolve to verified sources.

---

## 7. VISUALISATION STANDARDS (apply to every figure)

- One shared style in `viz.py`: colour-blind-safe palette, font sizes ≥ 10 pt, 200 dpi, tight layout.
- Every figure has: informative **title**, **labelled axes with units**, legend where needed, and a source/seed note in the filename or caption.
- Register every figure with `viz.save_figure(fig, name, title, notebook, observation, inference, limitation)` → writes the PNG and appends to `results/figure_catalog.csv`.
- Required figure set (minimum): funnel; monthly volume; product distribution; length distribution; ablation bar chart; Zipf; class-term bars; embedding projection; model comparison with CIs; normalised confusion matrix; random-vs-chronological gap; gain/lift; calibration; fairness slice chart; coherence sweep; topic-word bars; topic × product heatmap; topic prevalence with alerts; proxy overlay; lead/lag; network (static); centrality bars; community × product heatmap; null-model distribution; SRI components; SRI sensitivity; architecture diagram; split timeline.
- Word clouds are supplementary, never the sole evidence.

---

## 8. QUALITY BAR: DEFINITION OF DONE

The project is complete only when **all** are true:
1. All 12 phases passed their gates and `PROGRESS.md` shows 12/12 complete.
2. `make all` regenerates every result, figure, table, app artifact, report, and slide deck from a clean checkout (documented runtime), and the reproducibility check passed.
3. The nine-item **Final Submission Checklist** from the course deck is satisfied: problem/objectives stated; dataset source/size/attributes documented; preprocessing justified; ≥ 3 analytical components demonstrated; metrics reported and interpreted; visualisations clear; notebooks reproduce results; references and reused resources acknowledged; report, presentation, and demo consistent.
4. Each of the seven rubric rows maps to concrete evidence in `docs/rubric_coverage.md`.
5. No claim without evidence; no citation unverified; no personal data exposed; ZIP dropped; privacy and ethics stated.
6. Tests pass; the app launches from `app/artifacts/` alone; the report DOCX opens correctly; the PPTX renders without overflow.
7. `CONTRIBUTIONS.md` and report Appendix G clearly state what the team built (pipeline design, temporal evaluation, ablations, proxy-validated detector, SRI, fairness analysis, dashboard) versus what comes from libraries/pretrained models (scikit-learn, gensim, spaCy, NetworkX, sentence-transformers MiniLM, etc.), with citations.

---

## 9. ETHICS, PRIVACY AND INTEGRITY GUARDRAILS

- Data are public and already redacted by the publisher. Do not attempt re-identification. Drop ZIP; strip emails/phones/URLs; avoid displaying long narratives verbatim in the report (≤ 2 short illustrative excerpts, truncated).
- State clearly: relief-risk scores support **prioritisation of human review**, never denial of service; discuss automation bias and proxy discrimination.
- Cite everything reused (dataset, libraries, pretrained model, any adapted code snippet). Do not copy public notebooks; write original code.
- Respect licences; record them in `DATASET_CARD.md` and `README.md`.

---

## 10. HOW YOU REPORT PROGRESS

After each phase, print a short checkpoint: *Phase done / key numbers (from files) / decisions logged / issues / next phase.* Keep `PROGRESS.md` current (checkbox per phase and sub-task, timestamp, blockers, exact resume instructions).

## 11. FINAL HAND-OFF MESSAGE (when everything is complete)

Provide: (1) a tree of the final repository; (2) the headline results table; (3) how to run (`make setup`, `make all`, `make app`); (4) runtime and hardware used; (5) known limitations; (6) a checklist of **items only the human can do**; and (7) any `[VERIFY]` references.

## 12. ITEMS ONLY THE HUMAN CAN DO (list these in your hand-off; do not block on them)

- Fill team names, registration numbers, faculty name, institution, date (placeholders).
- Review and, where needed, correct unverified references marked `[VERIFY]`.
- Create the GitHub repository, push, and deploy the dashboard to Streamlit Community Cloud or Hugging Face Spaces following `docs/DEPLOYMENT.md`.
- Place the dataset manually if the automated download is blocked.
- Rehearse the demo using `docs/DEMO_SCRIPT.md` and personally review the report so every team member can explain every section (the course requires it).

---

**BEGIN NOW with Phase 0. Do not ask for confirmation to start; proceed autonomously through the phases, and stop only for a genuine blocker.**

# ComplaintScope: Statement of Original Contributions & Reused Resources

**Course:** CBS3009 – Advanced Social, Text and Media Analytics  
**Academic Integrity Statement:** In compliance with course project guidelines, this document explicitly delineates original analytical and software contributions designed and developed by the project team versus third-party libraries, datasets, and pretrained artifacts reused.

---

## 1. Original Contributions by the Team

The following components represent original design, formulation, and implementation engineered by the student team:

1. **System Architecture & End-to-End Orchestration:**
   - Multi-stage pipeline integrating text classification, relief risk estimation, dynamic topic burst detection, bipartite network projection, and a unified Systemic Risk Index.
   - Modular, configuration-driven engineering (`src/` architecture with strict YAML parameters and execution gates).

2. **Temporal Evaluation & Leakage-Aware Split Protocol:**
   - Strict chronological validation (70% train / 15% validation / 15% test) partitioned by strict calendar boundaries.
   - Empirical quantification of temporal vocabulary drift vs. standard random cross-validation (addressing Analytical Question AQ3).

3. **Preprocessing Ablation Framework:**
   - Controlled validation-set ablation quantifying the individual impacts of token normalization, domain-aware stopword filtering, redaction placeholder preservation (`<redacted>`, `<date>`, `<amt>`), and lemmatization vs. stemming.

4. **Emerging-Issue Detection with Independent Keyword Proxy Validation (Core Innovation):**
   - Formulation of a dual-detector streaming architecture (trailing 12-month rolling $z$-score vs. EWMA control chart) applied to monthly topic prevalence.
   - Pre-registered keyword proxy validation framework using full-corpus aggregates to empirically benchmark detection lead/lag, alert precision, recall, and false alarms without circular topic dependency.

5. **Company-Issue Bipartite Network & Structural Significance Null Model:**
   - Construction of bipartite financial institution $\times$ grievance issue graph and cosine-projected inter-firm similarity manifold.
   - 100-iteration degree-preserving randomized configuration null model to mathematically prove community modularity significance beyond random chance.

6. **Systemic Risk Index (SRI) Formulation:**
   - Mathematical formulation of a 5-dimensional rank-based composite risk metric integrating burst intensity, recent growth velocity, company breadth (entropy), relief probability, and complaint volume.
   - Rank stability sensitivity analysis under perturbation.

7. **Interactive 5-Page Dashboard:**
   - Streamlit analytical dashboard featuring real-time grievance triage, dynamic burst alerts, interactive Pyvis network graph, SRI rankings, and demographic fairness slices.

---

## 2. Reused Resources, Open-Source Libraries & Datasets

### A. Dataset
- **US Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database:**
  - Source: US Government Public Open Data (`https://files.consumerfinance.gov/ccdb/complaints.csv.zip`).
  - Licence: Creative Commons Zero / US Public Domain.
  - Used strictly for educational and research analytics; all personally identifiable information redacted by CFPB prior to publication.

### B. Open-Source Python Libraries
- **Data Manipulation & Scientific Computing:** `numpy`, `scipy`, `pandas`, `pyarrow`, `statsmodels`.
- **Natural Language Processing & Topic Modelling:**
  - `scikit-learn` (Pedregosa et al., 2011) – TF-IDF vectorization, classifiers, NMF, evaluation metrics.
  - `spacy` (Honnibal et al.) – Efficient tokenization and lemmatization (`en_core_web_sm`).
  - `nltk` (Bird et al., 2009) – Stopword corpora and token processing.
  - `gensim` (Řehůřek & Sojka, 2010) – Latent Dirichlet Allocation (LDA) and $c_v$ topic coherence calculation.
- **Deep Learning / Pretrained Embeddings:**
  - `sentence-transformers` (Reimers & Gurevych, 2019) – `all-MiniLM-L6-v2` lightweight sentence transformer hosted via HuggingFace for dense semantic representations and cosine kNN retrieval.
- **Graph & Network Analytics:**
  - `networkx` (Hagberg et al., 2008) – Graph construction, path algorithms, and centrality computation.
  - `python-louvain` (Blondel et al., 2008) – Louvain modularity optimization for community detection.
  - `pyvis` – Interactive HTML network visualization.
- **Visualization:** `matplotlib` (Hunter, 2007), `seaborn` (Waskom, 2021), `plotly`, `wordcloud`.
- **Application & Reporting:** `streamlit`, `python-docx`, `python-pptx`, `pytest`, `pyyaml`.

---

## 3. Team Member Specific Contributions
*(To be detailed in final report Appendix G upon project completion)*
- **Ruhaan bansal (23BBS0046):** Text preprocessing, classification modeling, temporal evaluation & ablation studies.
- **Vedant Rajesh (23BBS0037):** Topic modeling (LDA/NMF), emerging issue burst detection & keyword proxy validation.
- **Anish Desai (23BBS0119):** Network analysis, community detection, null model evaluation, Systemic Risk Index & Streamlit dashboard.

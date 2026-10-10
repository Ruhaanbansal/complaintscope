# ComplaintScope: Viva Preparation Pack
## 40+ Grounded Q&As for CBS3009 Assessment

**Course:** CBS3009 – Advanced Social, Text and Media Analytics  
**Grounded answers** → all figures reference actual code and output locations.

---

## Section 1: Dataset & Methodology

**Q1. Where does your data come from?**  
The primary dataset is the **CFPB Consumer Complaint Database**, an official US government open dataset published under CC0 1.0. Historical complaint narratives (pre-August 2026 CFPB policy change) were sourced from the Hugging Face mirror at `vivekkopthsd/cfpb-consumer-complaints`. Provenance is documented in `data/DATASET_CARD.md` with SHA-256 hash of the raw archive in `results/metrics/data_provenance.json`.

**Q2. How many records did you start with and how many did you end up using?**  
We scanned the full CFPB corpus (>8M records). After filtering for narratives (non-null), date range (2018–2023), minimum length (≥20 words), exact deduplication, and definite relief labels, we obtained a stratified sample of **19,998 complaints** (fast mode). Exact funnel statistics are in `data/DATASET_CARD.md`.

**Q3. Why did you use a 70/15/15 chronological split instead of random?**  
A chronological split simulates real-world deployment where models trained on past complaints must generalize to future ones. Random splitting leaks future information into training data (temporal leakage). Our AQ3 experiment quantified this: the chronological-to-random test F1 difference is recorded in `results/metrics/aq3_split_drift.json`.

**Q4. How did you handle CFPB redaction artifacts like XXXX?**  
We replaced them with structured placeholder tokens: `XXXX` → `<redacted>`, `XX/XX/XXXX` → `<date>`, `{$123.45}` → `<amt>`. The ablation study (`results/tables/ablation_preprocessing.csv`) confirms placeholder mode outperforms deletion mode.

**Q5. What is the class imbalance situation in your dataset?**  
The dataset has two imbalances: (1) Product class imbalance (Credit reporting dominates at ~35%), addressed by macro-averaged F1 metrics. (2) Relief label imbalance (~20-30% relief rate), addressed by `class_weight='balanced'` in LR and noted in `data/DATASET_CARD.md`.

---

## Section 2: Text Preprocessing

**Q6. Why preserve negation words during stopword removal?**  
Negation words (not, never, without) reverse the sentiment of what follows. Removing "not" from "did not refund" produces "refund" — a false positive signal. The negation preservation is implemented in `src/preprocess.py::clean_tokens()` and tested in `tests/test_preprocess.py::test_negation_retention()`.

**Q7. Which preprocessing configuration performed best in your ablation?**  
The **Baseline configuration** (placeholder redaction + lowercase + stopword removal + lemmatization + negation preservation) achieved the highest Macro-F1 on the validation split. The full ablation table is at `results/tables/ablation_preprocessing.csv`.

**Q8. Did you use spaCy or NLTK for lemmatization?**  
spaCy (`en_core_web_sm`) was preferred for lemmatization due to part-of-speech-aware lemmatization (better accuracy than NLTK WordNet lemmatizer). NLTK was used for stopwords. A fallback to whitespace tokenization is implemented in case spaCy is unavailable.

---

## Section 3: Feature Engineering

**Q9. What is sublinear TF-IDF and why did you use it?**  
Sublinear TF-IDF applies log-scaling to term frequency (`tf = 1 + log(tf)`) to reduce the dominance of high-frequency terms. Consumer complaint narratives have extreme frequency skew (Zipf distribution visible in Fig 7). This normalization improves discrimination between classes.

**Q10. Why did you limit the TF-IDF vocabulary to 30,000 features?**  
Empirically, 30K features captures >95% of the useful signal while keeping the feature matrix manageable in memory. The Zipf plot (Fig 7) shows the long tail of rare terms (rank >30K) contributes noise. Vocabulary size is a hyperparameter in `config.yaml`.

**Q11. What sentence-transformer model did you use?**  
`all-MiniLM-L6-v2` from the sentence-transformers library. It produces 384-dimensional L2-normalised embeddings and was chosen for its balance of quality and inference speed (suitable for batch encoding 20K narratives). Embeddings are cached as `.npy` files in `data/processed/`.

**Q12. What is Precision@k in the context of kNN retrieval?**  
Precision@k measures how often the true product label of a query complaint appears among the k most similar training complaints (cosine similarity on MiniLM embeddings). Results are in `results/tables/knn_precision_at_k.json`.

---

## Section 4: Classification

**Q13. What models did you evaluate for product classification?**  
We evaluated 8 models: DummyClassifier (majority), DummyClassifier (stratified), MultinomialNB, ComplementNB, DecisionTree (depth=10), LogisticRegression (default), LogisticRegression (tuned on val), LinearSVC (calibrated), and MiniLM+LR. Results in `results/tables/classification_results.csv`.

**Q14. How did you tune hyperparameters without touching the test set?**  
All hyperparameter tuning was done exclusively on the **validation split** (chronological middle 15%). The best LogisticRegression `C` and `solver` parameters were selected by validation Macro-F1 in `src/classify.py::grid_search_on_val()`. The test set was touched exactly once, for final reporting.

**Q15. What is McNemar's test and why did you use it?**  
McNemar's test is a non-parametric test for paired binary comparisons. It tests whether the best model makes significantly fewer errors than the baseline on the same test examples. The contingency table (b: A correct, B wrong; c: B correct, A wrong) and p-value are in `results/metrics/mcnemar_test.json`.

**Q16. What is AQ3 and what does it show?**  
AQ3 (Analytical Question 3) quantifies **temporal concept drift**: the same model evaluated on the chronological test split vs. a random test split. A significant F1 drop confirms that future complaints are harder to classify (due to evolving language, new products, regulatory changes). Results in `results/metrics/aq3_split_drift.json`.

**Q17. How many errors did you examine in the error taxonomy?**  
We examined **60 randomly sampled misclassified test complaints** and categorized them by (true_label → predicted_label) confusion pairs. The taxonomy reveals systematic confusions (e.g., Credit Cards vs. Credit Reporting). Results in `results/tables/error_taxonomy.csv`.

---

## Section 5: Relief Risk Prediction

**Q18. What metric did you prioritize for relief prediction and why?**  
**PR-AUC (Average Precision)** rather than ROC-AUC, because the relief label is imbalanced (~25% positive rate). ROC-AUC is inflated under class imbalance. PR-AUC measures performance specifically on the minority (relief-granted) class, which is the operationally relevant outcome for triage.

**Q19. What is Lift@k and what does it mean operationally?**  
Lift@k = (Precision@k) / (base rate). A Lift@10% of 3.0 means that reviewing the top-10% highest-risk complaints captures 3× more relief cases than random review. This directly quantifies the operational benefit of the triage system for caseworkers.

**Q20. How did you evaluate model calibration?**  
We computed the calibration curve (fraction of positives vs. mean predicted probability in 10 bins) from `sklearn.calibration.calibration_curve`. A well-calibrated model's curve follows the diagonal. The plot is at `results/figures/fig11_calibration_curve.png`.

**Q21. Why did you exclude company identity from the main relief model?**  
Including company name as a feature would create a shortcut: the model learns "Bank X always denies relief" rather than learning from narrative content. This prevents generalisation to new complaints from new companies. A separate ablation (with company) is in `results/metrics/company_feature_ablation.json` to quantify the leakage effect.

**Q22. How did you assess fairness across demographic groups?**  
We computed PR-AUC separately for each slice of `submitted_via`, `tags` (Older American / Servicemember), and `state`. Groups with fewer than 30 complaints were excluded. Results are in `results/tables/fairness_slices.csv`.

---

## Section 6: Topic Modelling

**Q23. What is coherence c_v and how does it differ from perplexity?**  
Coherence c_v measures semantic relatedness of top topic words using point-wise mutual information (PMI) and cosine similarity over a sliding window co-occurrence. Unlike perplexity (which measures model fit), c_v correlates better with human judgments of topic quality and doesn't require a held-out corpus.

**Q24. How did you select the number of topics k?**  
We swept k ∈ {5, 7, 10, 12, 15} (configurable in `config.yaml`) and selected the k with the highest c_v coherence score. The sweep results are in `results/tables/topic_sweep_results.csv` and the coherence plot is `results/figures/fig14_lda_coherence_sweep.png`.

**Q25. What is topic diversity and why is it important?**  
Topic diversity = (unique words across all top-10 words) / (total words). A low diversity means topics share many words and are hard to distinguish. We compute it alongside coherence to avoid selecting models that simply learn one very coherent topic repeatedly.

**Q26. How did you produce human-readable topic labels?**  
We used the top-3 words of each topic as a label (e.g., "payment / account / fee"). This heuristic was chosen for speed in a 20K-document corpus; in a production system, we would use an LLM to generate descriptive labels. Labels are in `results/metrics/topic_labels.json`.

---

## Section 7: Burst Detection

**Q27. What is a rolling z-score burst detector?**  
For a time series of monthly topic prevalence, we compute `z = (current_month - trailing_mean) / trailing_std` using a 12-month trailing window. A z-score > 2.0 flags an abnormal surge. This is identical to statistical process control (control charts) applied to complaint data.

**Q28. What is EWMA/CUSUM and how does it differ from z-score?**  
EWMA (Exponentially Weighted Moving Average) gives more weight to recent months, making it more sensitive to recent trends. CUSUM (Cumulative Sum) accumulates deviations from the EWMA baseline; it detects sustained upward shifts rather than single-month spikes. The two detectors are complementary.

**Q29. What are your pre-registered keyword proxies?**  
Five proxies defined BEFORE running the burst analysis in `src/burst.py::KEYWORD_PROXIES`: covid_relief, overdraft_fee, credit_reporting, debt_collection, mortgage_forbearance. Pre-registration prevents p-hacking — we cannot retroactively choose proxies that validate our detectors. The proxy timestamps are committed in `DECISIONS.md`.

**Q30. How do you measure alert precision/recall?**  
Alert precision = (true alarm months) / (total alarm months). Recall = (true alarm months) / (months where proxy fired). F1 combines both. A proxy "fires" when its monthly keyword rate exceeds the 75th percentile of its own distribution. Results in `results/metrics/proxy_validation.json`.

---

## Section 8: Network Analysis

**Q31. Why did you use a bipartite graph?**  
Complaints naturally form a bipartite structure: companies receive complaints about specific issues. A bipartite graph preserves this duality and allows us to project onto companies using shared issue profiles — revealing which institutions have structurally similar complaint ecosystems.

**Q32. How did you project the bipartite graph onto companies?**  
We computed a cosine similarity matrix of company-issue complaint vectors (normalized row profiles). Two companies are connected in the projection if their cosine similarity ≥ 0.1. This creates a company-company network where edges represent shared complaint patterns.

**Q33. What centrality measures did you compute and what do they mean?**  
Degree (raw connections), weighted degree (connections × similarity weights), betweenness (broker role between communities), closeness (average distance to all others), eigenvector (connection to well-connected nodes). Each dimension captures a different type of systemic importance.

**Q34. What is Louvain community detection?**  
Louvain is a modularity-maximizing graph partitioning algorithm. It iteratively reassigns nodes to communities to maximize the modularity score Q = (within-community edges - expected edges under null model). The resolution parameter controls community granularity.

**Q35. What does your null model comparison show?**  
We compared the observed modularity against 100 degree-preserving configuration model randomizations. The p-value in `results/metrics/network_metrics.json` indicates whether the observed community structure is statistically stronger than expected by chance.

---

## Section 9: Systemic Risk Index

**Q36. How is the SRI composite computed?**  
SRI = w₁×(normalized complaint volume) + w₂×(normalized relief rate) + w₃×(normalized issue breadth) + w₄×(normalized network centrality) + w₅×(normalized burst activity). Default weights: {0.25, 0.20, 0.20, 0.20, 0.15}. Each dimension is min-max normalized to [0,1].

**Q37. How did you test the robustness of the SRI ranking?**  
We sampled 100 random weight vectors from a Dirichlet distribution (ensuring they sum to 1) and recomputed SRI rankings for each. We measured Kendall's τ between the baseline ranking and each perturbed ranking for the top-10 companies. The mean τ and standard deviation are in `results/metrics/sri_sensitivity.json`.

**Q38. What are your key regulatory insights?**  
Four insights in `results/metrics/actionable_insights.json`: (1) Top-5 SRI companies warrant priority regulatory visits; (2) Low-relief-rate companies need mandatory remediation audits; (3) High-breadth companies show firm-wide protection failures; (4) COVID forbearance complaints were the fastest-growing category in 2020-2021.

---

## Section 10: System & Reproducibility

**Q39. How do you ensure reproducibility?**  
Global seed 42 is set for Python random, NumPy, and PyTorch in `src/config.py::set_seeds()`. All random operations use explicit `random_state=seed`. Phase timings and library versions are logged in `results/metrics/run_metadata.json`.

**Q40. How long does the full pipeline take?**  
Full pipeline run times are logged per phase in `results/metrics/run_metadata.json`. Phase 2 (preprocessing + ablation) is the bottleneck due to spaCy lemmatization of 19K texts.

**Q41. Is the dashboard usable without re-running the pipeline?**  
Yes. The dashboard loads pre-computed artifacts from `app/artifacts/` (< 100 MB). Only the `app/artifacts/` directory is required to run the dashboard — no raw data needed.

**Q42. What would you do differently with more time?**  
(1) Use a fine-tuned domain-specific BERT model for classification instead of TF-IDF. (2) Apply BERTopic for topic modelling. (3) Add longitudinal panel analysis per company. (4) Integrate real-time CFPB API streaming. (5) Expand fairness analysis to ZIP-code demographic proxies.

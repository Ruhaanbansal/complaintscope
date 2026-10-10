"""
ComplaintScope: Topic Discovery & Clustering module.
Phase 6 - LDA (gensim), NMF (sklearn), K-Means on embeddings,
           coherence/diversity/silhouette sweep, topic labelling.
"""
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd

logger = logging.getLogger("complaintscope.topics")


def build_gensim_corpus(texts: pd.Series) -> Tuple:
    """Build gensim Dictionary and corpus from a text series."""
    try:
        from gensim.corpora import Dictionary
        from gensim.utils import simple_preprocess
        tokenized = [simple_preprocess(str(t), deacc=True) for t in texts.fillna("")]
        dictionary = Dictionary(tokenized)
        dictionary.filter_extremes(no_below=5, no_above=0.5)
        corpus = [dictionary.doc2bow(t) for t in tokenized]
        return dictionary, corpus, tokenized
    except ImportError:
        raise ImportError("gensim not installed.")


def compute_coherence(lda_model, tokenized, dictionary, coherence="c_v") -> float:
    try:
        from gensim.models.coherencemodel import CoherenceModel
        cm = CoherenceModel(
            model=lda_model, texts=tokenized,
            dictionary=dictionary, coherence=coherence
        )
        return float(cm.get_coherence())
    except Exception as e:
        logger.warning(f"Coherence computation failed: {e}")
        return float("nan")


def compute_topic_diversity(topic_words_list: List[List[str]]) -> float:
    """Topic diversity = fraction of unique words across all top-10 words of each topic."""
    all_words = [w for topic in topic_words_list for w in topic]
    if not all_words:
        return 0.0
    return len(set(all_words)) / len(all_words)


def run_lda_sweep(dictionary, corpus, tokenized, k_range: List[int], seed: int = 42) -> List[Dict]:
    """Run LDA for each k and compute coherence."""
    from gensim.models import LdaModel
    sweep_results = []
    for k in k_range:
        logger.info(f"  LDA k={k}...")
        try:
            lda = LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=k,
                random_state=seed,
                passes=5,
                alpha="auto",
                eta="auto",
                minimum_probability=0.0
            )
            coh = compute_coherence(lda, tokenized, dictionary)
            topic_words = [
                [w for w, _ in lda.show_topic(t, topn=10)]
                for t in range(k)
            ]
            diversity = compute_topic_diversity(topic_words)
            sweep_results.append({
                "k": k, "model": "LDA",
                "coherence_cv": round(coh, 4),
                "diversity": round(diversity, 4),
                "model_obj": lda,
                "topic_words": topic_words,
            })
        except Exception as e:
            logger.warning(f"  LDA k={k} failed: {e}")
    return sweep_results


def run_nmf_sweep(texts: pd.Series, k_range: List[int], seed: int = 42) -> List[Dict]:
    """Run NMF for each k and compute diversity."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF

    vec = TfidfVectorizer(max_features=20000, min_df=3, ngram_range=(1, 1))
    X = vec.fit_transform(texts.fillna(""))
    feature_names = vec.get_feature_names_out()

    sweep_results = []
    for k in k_range:
        logger.info(f"  NMF k={k}...")
        try:
            nmf = NMF(n_components=k, init="nndsvda", random_state=seed, max_iter=200)
            W = nmf.fit_transform(X)
            H = nmf.components_
            topic_words = [
                [feature_names[i] for i in H[t].argsort()[-10:][::-1]]
                for t in range(k)
            ]
            diversity = compute_topic_diversity(topic_words)
            sweep_results.append({
                "k": k, "model": "NMF",
                "coherence_cv": float("nan"),  # NMF doesn't use gensim coherence
                "diversity": round(diversity, 4),
                "model_obj": nmf,
                "vectorizer": vec,
                "W": W,
                "H": H,
                "topic_words": topic_words,
            })
        except Exception as e:
            logger.warning(f"  NMF k={k} failed: {e}")
    return sweep_results


def run_kmeans_sweep(embeddings: np.ndarray, k_range: List[int], seed: int = 42) -> List[Dict]:
    """Run K-Means on embeddings for each k, compute silhouette."""
    from sklearn.cluster import KMeans, MiniBatchKMeans
    from sklearn.metrics import silhouette_score

    sweep_results = []
    n_sample = min(2000, len(embeddings))
    sample_idx = np.random.RandomState(seed).choice(len(embeddings), n_sample, replace=False)
    emb_sample = embeddings[sample_idx]

    for k in k_range:
        logger.info(f"  KMeans k={k}...")
        try:
            km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=5, batch_size=512)
            km.fit(embeddings)
            labels_sample = km.predict(emb_sample)
            sil = silhouette_score(emb_sample, labels_sample, sample_size=min(1000, n_sample))
            sweep_results.append({
                "k": k, "model": "KMeans",
                "coherence_cv": float("nan"),
                "silhouette": round(float(sil), 4),
                "model_obj": km,
            })
        except Exception as e:
            logger.warning(f"  KMeans k={k} failed: {e}")
    return sweep_results


def label_topics(topic_words_list: List[List[str]]) -> List[str]:
    """
    Heuristically label topics from their top words.
    Returns a human-readable label per topic.
    """
    labels = []
    for words in topic_words_list:
        top3 = " / ".join(words[:3])
        labels.append(top3)
    return labels


def run_phase_6():
    """Run Phase 6: Topic Discovery & Clustering."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    setup_logger("complaintscope.topics")
    t0 = time.time()
    cfg = load_config()
    seed = set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 6: Topic Discovery & Clustering ===")

    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    df_train = df[df["chronological_split"] == "train"].copy().reset_index(drop=True)

    text_col = "narrative_clean" if "narrative_clean" in df_train.columns else "narrative"
    texts_train = df_train[text_col]

    tables_dir  = Path("results/tables")
    figs_dir    = Path("results/figures")
    metrics_dir = Path("results/metrics")
    for d in [tables_dir, figs_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    k_range_topics = cfg.get("topics", {}).get("k_range", [5, 7, 10, 12, 15])

    # --- LDA sweep ---
    lda_results = []
    try:
        logger.info("Building gensim corpus for LDA...")
        dictionary, corpus, tokenized = build_gensim_corpus(texts_train)
        logger.info(f"Dictionary size: {len(dictionary):,}, Corpus docs: {len(corpus):,}")
        logger.info("Running LDA sweep...")
        lda_sweep = run_lda_sweep(dictionary, corpus, tokenized, k_range_topics, seed=seed)
        lda_results = [{k: v for k, v in r.items() if k not in ["model_obj", "topic_words"]}
                       for r in lda_sweep]
    except Exception as e:
        logger.warning(f"LDA sweep failed: {e}")
        lda_sweep = []

    # --- NMF sweep ---
    nmf_results = []
    try:
        logger.info("Running NMF sweep...")
        nmf_sweep = run_nmf_sweep(texts_train, k_range_topics, seed=seed)
        nmf_results = [{k: v for k, v in r.items() if k not in ["model_obj", "vectorizer", "W", "H", "topic_words"]}
                       for r in nmf_sweep]
    except Exception as e:
        logger.warning(f"NMF sweep failed: {e}")
        nmf_sweep = []

    # --- KMeans sweep ---
    km_results = []
    emb_train_path = Path("data/processed/emb_train.npy")
    if emb_train_path.exists():
        emb_train = np.load(str(emb_train_path))
        try:
            logger.info("Running K-Means sweep...")
            km_sweep = run_kmeans_sweep(emb_train[:len(df_train)], k_range_topics, seed=seed)
            km_results = [{k: v for k, v in r.items() if k != "model_obj"} for r in km_sweep]
        except Exception as e:
            logger.warning(f"KMeans sweep failed: {e}")
            km_sweep = []
    else:
        logger.info("No embeddings found; skipping KMeans.")
        km_sweep = []

    # Combine sweep results
    all_sweep = lda_results + nmf_results + km_results
    df_sweep = pd.DataFrame(all_sweep)
    sweep_path = tables_dir / "topic_sweep_results.csv"
    df_sweep.to_csv(sweep_path, index=False)
    logger.info(f"Saved topic sweep results to {sweep_path}")

    # Select best k for LDA (by coherence)
    best_lda = None
    best_k_lda = cfg.get("topics", {}).get("n_topics", cfg.get("topic_model", {}).get("n_topics", 10))
    if lda_sweep:
        best_lda_idx = max(range(len(lda_sweep)), key=lambda i: lda_sweep[i].get("coherence_cv", -1))
        best_lda = lda_sweep[best_lda_idx]
        best_k_lda = best_lda["k"]
        logger.info(f"Best LDA k={best_k_lda} (coherence={best_lda.get('coherence_cv', 'N/A')})")

    # Label topics
    topic_labels = {}
    if best_lda and "topic_words" in best_lda:
        labels = label_topics(best_lda["topic_words"])
        topic_labels["lda"] = {
            str(i): {
                "label": labels[i],
                "top_words": best_lda["topic_words"][i]
            }
            for i in range(best_k_lda)
        }

    if nmf_sweep:
        best_nmf = nmf_sweep[-1]  # use last k for NMF (usually largest diverse)
        if "topic_words" in best_nmf:
            nmf_labels = label_topics(best_nmf["topic_words"])
            topic_labels["nmf"] = {
                str(i): {
                    "label": nmf_labels[i],
                    "top_words": best_nmf["topic_words"][i]
                }
                for i in range(best_nmf["k"])
            }

    labels_path = metrics_dir / "topic_labels.json"
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(topic_labels, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved topic labels to {labels_path}")

    # --- Figures ---
    # Coherence sweep plot
    if lda_results:
        df_lda_sweep = pd.DataFrame(lda_results)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(df_lda_sweep["k"], df_lda_sweep["coherence_cv"], marker="o", color="#1f77b4", lw=2, label="Coherence (c_v)")
        ax.set_xlabel("Number of Topics (k)", fontsize=12)
        ax.set_ylabel("Coherence Score (c_v)", fontsize=12)
        ax.set_title("Fig 14: LDA Topic Model – Coherence Sweep", fontsize=13)
        ax.axvline(x=best_k_lda, color="orange", linestyle="--", label=f"Best k={best_k_lda}")
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        coh_path = figs_dir / "fig14_lda_coherence_sweep.png"
        fig.savefig(str(coh_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved coherence sweep to {coh_path}")

    # Topic-product heatmap (if best LDA available)
    if best_lda and "model_obj" in best_lda:
        try:
            lda_model = best_lda["model_obj"]
            # Compute topic distributions for each doc
            topic_dists = np.array([
                [p for _, p in lda_model.get_document_topics(bow, minimum_probability=0)]
                for bow in corpus
            ])
            df_train["dominant_topic"] = topic_dists.argmax(axis=1)

            # Topic-product cross-tab
            pivot = (
                df_train.groupby(["dominant_topic", "product_consolidated"])
                .size()
                .unstack(fill_value=0)
            )
            # Normalize per topic
            pivot_norm = pivot.div(pivot.sum(axis=1), axis=0)

            fig, ax = plt.subplots(figsize=(14, max(6, best_k_lda)))
            sns.heatmap(
                pivot_norm, annot=False, cmap="YlOrRd",
                linewidths=0.3, ax=ax, cbar_kws={"label": "Proportion"}
            )
            ax.set_title("Fig 15: Topic-Product Distribution Heatmap", fontsize=13)
            ax.set_xlabel("Product Category", fontsize=10)
            ax.set_ylabel("Dominant Topic", fontsize=10)
            plt.xticks(rotation=45, ha="right", fontsize=8)
            plt.tight_layout()
            heatmap_path = figs_dir / "fig15_topic_product_heatmap.png"
            fig.savefig(str(heatmap_path), dpi=150, bbox_inches="tight")
            plt.close(fig)
            logger.info(f"Saved topic-product heatmap to {heatmap_path}")

            # Save dominant topic column back to interim for Phase 7
            df_topic = df.copy()
            train_indices = df_train.index
            topic_col = pd.Series(index=df.index, dtype="Int64")
            topic_col.loc[train_indices] = df_train["dominant_topic"].values
            df_topic["dominant_topic"] = topic_col
            df_topic.to_parquet(str(get_path("interim_clean")), index=False)
            logger.info("Saved dominant_topic column back to clean parquet.")
        except Exception as e:
            logger.warning(f"Topic-product heatmap failed: {e}")

    # Save LDA model
    if best_lda and "model_obj" in best_lda:
        import joblib
        app_dir = Path("app/artifacts")
        app_dir.mkdir(parents=True, exist_ok=True)
        try:
            best_lda["model_obj"].save(str(app_dir / "lda_model.gensim"))
            import pickle
            with open(str(app_dir / "lda_dictionary.pkl"), "wb") as f:
                pickle.dump(dictionary, f)
            logger.info("Saved LDA model and dictionary to app/artifacts/")
        except Exception as e:
            logger.warning(f"LDA save failed: {e}")

    duration = time.time() - t0
    save_run_metadata("Phase_6_Topics", duration_sec=duration, extra_meta={
        "best_k_lda": best_k_lda,
        "lda_sweep_k_range": k_range_topics,
        "topic_labels_saved": str(labels_path),
    })
    logger.info(f"=== Phase 6 completed in {duration:.1f}s ===")
    return topic_labels


if __name__ == "__main__":
    run_phase_6()

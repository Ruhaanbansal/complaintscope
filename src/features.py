"""
ComplaintScope: Feature Representation module.
Phase 3 - BoW, sublinear TF-IDF, sentence-transformer embeddings, cosine kNN,
           metadata encoders, Zipf plot, class top terms, 2D UMAP projections.
"""
import time
import json
import logging
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("complaintscope.features")


# ---------------------------------------------------------------------------
# Vectorizers
# ---------------------------------------------------------------------------

def build_bow_vectorizer(
    train_texts: pd.Series,
    max_features: int = 30_000,
    min_df: int = 2
) -> Tuple[CountVectorizer, Any]:
    """Fit and return a CountVectorizer (BoW) on training texts only."""
    effective_min_df = min_df if len(train_texts) >= 10 else 1
    vec = CountVectorizer(
        max_features=max_features,
        min_df=effective_min_df,
        ngram_range=(1, 2),
        strip_accents="unicode",
        token_pattern=r"\b[a-z][a-z0-9_]{1,}\b"
    )
    X = vec.fit_transform(train_texts.fillna(""))
    logger.info(f"BoW vocabulary size: {len(vec.vocabulary_):,}")
    return vec, X


def build_tfidf_vectorizer(
    train_texts: pd.Series,
    max_features: int = 30_000,
    min_df: int = 2
) -> Tuple[TfidfVectorizer, Any]:
    """Fit and return a sublinear TF-IDF vectorizer on training texts only."""
    effective_min_df = min_df if len(train_texts) >= 10 else 1
    vec = TfidfVectorizer(
        max_features=max_features,
        min_df=effective_min_df,
        sublinear_tf=True,
        ngram_range=(1, 2),
        strip_accents="unicode",
        token_pattern=r"\b[a-z][a-z0-9_]{1,}\b"
    )
    X = vec.fit_transform(train_texts.fillna(""))
    logger.info(f"TF-IDF vocabulary size: {len(vec.vocabulary_):,}")
    return vec, X


# ---------------------------------------------------------------------------
# Sentence-transformer embeddings
# ---------------------------------------------------------------------------

def get_embeddings(
    texts: pd.Series,
    model_name: str = "all-MiniLM-L6-v2",
    cache_path: Path = None,
    batch_size: int = 128,
    max_seq_length: int = 128,
    device: str = "cpu"
) -> np.ndarray:
    """
    Compute sentence-transformer embeddings. Uses a cache file if available.
    Saves to cache_path (numpy .npy) after computation.
    """
    if cache_path is not None and Path(cache_path).exists():
        logger.info(f"Loading cached embeddings from {cache_path}")
        return np.load(str(cache_path))

    logger.info(f"Computing embeddings with {model_name} (n={len(texts):,}, max_seq={max_seq_length})...")
    try:
        import os
        import torch
        from sentence_transformers import SentenceTransformer
        n_threads = min(8, os.cpu_count() or 4)
        torch.set_num_threads(n_threads)
    except ImportError:
        raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")

    t0 = time.time()
    model = SentenceTransformer(model_name, device=device)
    model.max_seq_length = max_seq_length
    text_list = texts.fillna("").astype(str).tolist()
    embeddings = model.encode(
        text_list,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    logger.info(f"Embeddings shape: {embeddings.shape}, elapsed: {time.time()-t0:.1f}s")

    if cache_path is not None:
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        np.save(str(cache_path), embeddings)
        logger.info(f"Saved embeddings cache to {cache_path}")

    return embeddings


# ---------------------------------------------------------------------------
# Cosine kNN retrieval engine
# ---------------------------------------------------------------------------

def cosine_knn_retrieve(
    query_embs: np.ndarray,
    corpus_embs: np.ndarray,
    k: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute cosine similarities between query and corpus embeddings.
    Returns top-k indices and scores for each query.
    Assumes embeddings are L2-normalised.
    """
    sims = cosine_similarity(query_embs, corpus_embs)
    top_k_idx = np.argsort(-sims, axis=1)[:, :k]
    top_k_scores = np.take_along_axis(sims, top_k_idx, axis=1)
    return top_k_idx, top_k_scores


def evaluate_knn_precision_at_k(
    query_df: pd.DataFrame,
    corpus_df: pd.DataFrame,
    query_embs: np.ndarray,
    corpus_embs: np.ndarray,
    label_col: str = "product_consolidated",
    k_values: list = [1, 3, 5, 10]
) -> Dict[str, float]:
    """Evaluate Precision@k of cosine kNN retrieval."""
    results = {}
    sims = cosine_similarity(query_embs, corpus_embs)

    for k in k_values:
        top_k_idx = np.argsort(-sims, axis=1)[:, :k]
        correct = 0
        for i, row in enumerate(top_k_idx):
            query_label = query_df[label_col].iloc[i]
            retrieved_labels = corpus_df[label_col].iloc[row].values
            if query_label in retrieved_labels:
                correct += 1
        precision_k = correct / len(query_df)
        results[f"Precision@{k}"] = round(precision_k, 4)
        logger.info(f"  Precision@{k}: {precision_k:.4f}")

    return results


# ---------------------------------------------------------------------------
# Metadata encoders
# ---------------------------------------------------------------------------

def build_metadata_features(
    df: pd.DataFrame,
    cat_cols: list = None
) -> Tuple[np.ndarray, list]:
    """
    One-hot encode categorical metadata columns (excluding company identity).
    Returns feature matrix and feature names.
    """
    if cat_cols is None:
        cat_cols = ["submitted_via", "tags", "state"]

    dummies_list = []
    feat_names = []
    for col in cat_cols:
        if col not in df.columns:
            continue
        dummies = pd.get_dummies(
            df[col].fillna("Unknown").astype(str),
            prefix=col,
            drop_first=False,
            dtype=np.float32
        )
        dummies_list.append(dummies)
        feat_names.extend(dummies.columns.tolist())

    if dummies_list:
        meta_matrix = np.hstack([d.values for d in dummies_list])
    else:
        meta_matrix = np.zeros((len(df), 1), dtype=np.float32)

    logger.info(f"Metadata feature matrix shape: {meta_matrix.shape}")
    return meta_matrix, feat_names


# ---------------------------------------------------------------------------
# Phase 3 runner
# ---------------------------------------------------------------------------

def run_phase_3():
    """Run Phase 3: Feature Representation."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    setup_logger("complaintscope.features")
    t0 = time.time()
    cfg = load_config()
    set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 3: Feature Representation ===")

    # Load data
    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    df_train = df[df["chronological_split"] == "train"].copy().reset_index(drop=True)
    df_val   = df[df["chronological_split"] == "val"].copy().reset_index(drop=True)
    df_test  = df[df["chronological_split"] == "test"].copy().reset_index(drop=True)

    text_col = "narrative_clean" if "narrative_clean" in df.columns else "narrative"
    logger.info(f"Using text column: {text_col}")

    # --- BoW & TF-IDF (fit ONLY on train) ---
    logger.info("Building BoW vectorizer...")
    bow_vec, X_train_bow = build_bow_vectorizer(df_train[text_col])
    X_val_bow  = bow_vec.transform(df_val[text_col].fillna(""))
    X_test_bow = bow_vec.transform(df_test[text_col].fillna(""))

    logger.info("Building TF-IDF vectorizer...")
    tfidf_vec, X_train_tfidf = build_tfidf_vectorizer(df_train[text_col])
    X_val_tfidf  = tfidf_vec.transform(df_val[text_col].fillna(""))
    X_test_tfidf = tfidf_vec.transform(df_test[text_col].fillna(""))

    # Save vectorizers
    processed_dir = get_path("processed_dir") if "processed_dir" in (cfg.get("paths") or {}) else (get_path("interim_clean").parent.parent / "data/processed")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(bow_vec,   processed_dir / "bow_vectorizer.joblib")
    joblib.dump(tfidf_vec, processed_dir / "tfidf_vectorizer.joblib")
    logger.info("Saved BoW and TF-IDF vectorizers.")

    # --- Sentence-transformer embeddings ---
    emb_dir = Path("data/processed")
    emb_train_path = emb_dir / "emb_train.npy"
    emb_val_path   = emb_dir / "emb_val.npy"
    emb_test_path  = emb_dir / "emb_test.npy"

    emb_cfg = cfg.get("features", {}).get("embeddings", {})
    emb_model = emb_cfg.get("model_name", "all-MiniLM-L6-v2")
    emb_batch = emb_cfg.get("batch_size", 128)
    emb_max_seq = emb_cfg.get("max_seq_length", 128)

    try:
        emb_train = get_embeddings(df_train["narrative"], model_name=emb_model, cache_path=emb_train_path, batch_size=emb_batch, max_seq_length=emb_max_seq)
        emb_val   = get_embeddings(df_val["narrative"],   model_name=emb_model, cache_path=emb_val_path,   batch_size=emb_batch, max_seq_length=emb_max_seq)
        emb_test  = get_embeddings(df_test["narrative"],  model_name=emb_model, cache_path=emb_test_path,  batch_size=emb_batch, max_seq_length=emb_max_seq)
        emb_available = True
    except Exception as e:
        logger.warning(f"Embeddings unavailable: {e}. Skipping kNN evaluation.")
        emb_train = emb_val = emb_test = None
        emb_available = False

    # --- kNN evaluation ---
    knn_results = {}
    if emb_available and emb_train is not None:
        logger.info("Evaluating cosine kNN retrieval Precision@k...")
        knn_results = evaluate_knn_precision_at_k(
            df_val, df_train,
            emb_val, emb_train,
            label_col="product_consolidated",
            k_values=[1, 3, 5, 10]
        )
        tables_dir = Path("results/tables")
        tables_dir.mkdir(parents=True, exist_ok=True)
        with open(tables_dir / "knn_precision_at_k.json", "w") as f:
            json.dump(knn_results, f, indent=2)
        logger.info(f"kNN Precision@k results: {knn_results}")

    # --- Metadata features ---
    logger.info("Building metadata features...")
    meta_train, meta_feat_names = build_metadata_features(df_train)
    meta_val,   _              = build_metadata_features(df_val)
    meta_test,  _              = build_metadata_features(df_test)
    np.save(str(emb_dir / "meta_train.npy"), meta_train)
    np.save(str(emb_dir / "meta_val.npy"),   meta_val)
    np.save(str(emb_dir / "meta_test.npy"),  meta_test)
    with open(emb_dir / "meta_feat_names.json", "w") as f:
        json.dump(meta_feat_names, f)

    # --- Figures ---
    figs_dir = Path("results/figures")
    figs_dir.mkdir(parents=True, exist_ok=True)

    # Figure: Zipf term frequency distribution
    logger.info("Generating Zipf distribution figure...")
    term_freqs = np.asarray(X_train_bow.sum(axis=0)).ravel()
    sorted_freqs = np.sort(term_freqs)[::-1]
    ranks = np.arange(1, len(sorted_freqs) + 1)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(ranks[:5000], sorted_freqs[:5000], linewidth=1.5, color="#1f77b4")
    ax.set_xlabel("Token Rank (log scale)", fontsize=12)
    ax.set_ylabel("Frequency (log scale)", fontsize=12)
    ax.set_title("Fig 7: Zipf Distribution of Complaint Token Frequencies", fontsize=13)
    ax.grid(True, which="both", alpha=0.3)
    zipf_path = figs_dir / "fig07_zipf_distribution.png"
    fig.savefig(str(zipf_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved Zipf figure to {zipf_path}")

    # Figure: Top-15 terms per class (TF-IDF)
    logger.info("Generating top class terms figure...")
    classes = df_train["product_consolidated"].unique()[:6]  # first 6 for readability
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    feature_names = tfidf_vec.get_feature_names_out()

    for ax_i, cls in enumerate(classes[:6]):
        cls_mask = df_train["product_consolidated"] == cls
        cls_texts = df_train.loc[cls_mask, text_col].fillna("")
        if len(cls_texts) == 0:
            continue
        cls_vec = tfidf_vec.transform(cls_texts).mean(axis=0)
        cls_scores = np.asarray(cls_vec).ravel()
        top_idx = cls_scores.argsort()[-15:][::-1]
        top_terms = [feature_names[i] for i in top_idx]
        top_vals  = cls_scores[top_idx]

        axes[ax_i].barh(top_terms[::-1], top_vals[::-1], color="#2ca02c", alpha=0.8)
        axes[ax_i].set_title(cls[:35], fontsize=10)
        axes[ax_i].set_xlabel("Mean TF-IDF", fontsize=9)

    fig.suptitle("Fig 8: Top-15 TF-IDF Terms per Product Class", fontsize=13)
    plt.tight_layout()
    terms_path = figs_dir / "fig08_class_top_terms.png"
    fig.savefig(str(terms_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved class top terms figure to {terms_path}")

    # Figure: 2D projection (UMAP or PCA fallback)
    logger.info("Generating 2D embedding projection...")
    sample_n = min(2000, len(emb_train)) if emb_available and emb_train is not None else 0

    if emb_available and sample_n > 0:
        try:
            import umap
            reducer = umap.UMAP(n_components=2, random_state=cfg.get("seed", 42), n_jobs=1)
            emb_2d = reducer.fit_transform(emb_train[:sample_n])
            reducer_name = "UMAP"
        except ImportError:
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2, random_state=cfg.get("seed", 42))
            emb_2d = reducer.fit_transform(emb_train[:sample_n])
            reducer_name = "PCA"

        labels_sample = df_train["product_consolidated"].values[:sample_n]
        unique_labels = list(set(labels_sample))
        try:
            import matplotlib
            colors = matplotlib.colormaps["tab10"].resampled(len(unique_labels))
        except AttributeError:
            colors = plt.cm.get_cmap("tab10", len(unique_labels))
        label_to_color = {lb: colors(i) for i, lb in enumerate(unique_labels)}

        fig, ax = plt.subplots(figsize=(12, 8))
        for lb in unique_labels:
            mask = labels_sample == lb
            ax.scatter(
                emb_2d[mask, 0], emb_2d[mask, 1],
                label=lb[:30], alpha=0.5, s=10,
                color=label_to_color[lb]
            )
        ax.legend(fontsize=7, markerscale=3, loc="best", ncol=2)
        ax.set_title(f"Fig 9: {reducer_name} 2D Projection of Complaint Embeddings (n={sample_n:,})", fontsize=12)
        ax.set_xlabel(f"{reducer_name} 1", fontsize=10)
        ax.set_ylabel(f"{reducer_name} 2", fontsize=10)
        proj_path = figs_dir / "fig09_2d_projection.png"
        fig.savefig(str(proj_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved 2D projection to {proj_path}")

    duration = time.time() - t0
    save_run_metadata("Phase_3_Features", duration_sec=duration, extra_meta={
        "bow_vocab_size": len(bow_vec.vocabulary_),
        "tfidf_vocab_size": len(tfidf_vec.vocabulary_),
        "embeddings_available": emb_available,
        "knn_results": knn_results,
    })
    logger.info(f"=== Phase 3 completed in {duration:.1f}s ===")
    return {
        "bow_vec": bow_vec,
        "tfidf_vec": tfidf_vec,
        "emb_train": emb_train,
        "emb_val": emb_val,
        "emb_test": emb_test,
        "meta_train": meta_train,
        "meta_val": meta_val,
        "meta_test": meta_test,
    }


if __name__ == "__main__":
    run_phase_3()

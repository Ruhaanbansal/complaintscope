"""
ComplaintScope: Relief-Risk Prediction & Triage Simulation module.
Phase 5 - Imbalance-aware models, PR-AUC, ROC-AUC, calibration,
           lift@k, fairness slices, explainability.
"""
import time
import json
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("complaintscope.relief")


def get_relief_features(df_train, df_val, df_test, tfidf_vec, meta_feat_names_path=None):
    """Prepare text + optional metadata features for relief prediction.
    
    Metadata columns are one-hot encoded using training-set categories only
    to prevent feature dimension mismatches across splits.
    """
    from scipy.sparse import hstack, csr_matrix
    import pandas as pd
    import numpy as np

    text_col = "narrative_clean" if "narrative_clean" in df_train.columns else "narrative"
    X_tr_text = tfidf_vec.transform(df_train[text_col].fillna(""))
    X_va_text = tfidf_vec.transform(df_val[text_col].fillna(""))
    X_te_text = tfidf_vec.transform(df_test[text_col].fillna(""))

    # Metadata features: fit OHE on train, align val/test to same columns
    cat_cols = [c for c in ["submitted_via", "tags", "state"] if c in df_train.columns]
    meta_dummies_train = pd.get_dummies(
        df_train[cat_cols].fillna("Unknown").astype(str),
        drop_first=False, dtype=np.float32
    )
    train_meta_cols = meta_dummies_train.columns.tolist()

    def _align_meta(df_split):
        dm = pd.get_dummies(
            df_split[[c for c in cat_cols if c in df_split.columns]].fillna("Unknown").astype(str),
            drop_first=False, dtype=np.float32
        )
        # Add missing columns as zeros, drop extras
        for col in train_meta_cols:
            if col not in dm.columns:
                dm[col] = 0.0
        return dm[train_meta_cols].values

    meta_tr = meta_dummies_train.values
    meta_va = _align_meta(df_val)
    meta_te = _align_meta(df_test)

    X_tr_combined = hstack([X_tr_text, csr_matrix(meta_tr)])
    X_va_combined = hstack([X_va_text, csr_matrix(meta_va)])
    X_te_combined = hstack([X_te_text, csr_matrix(meta_te)])

    return {
        "text": (X_tr_text, X_va_text, X_te_text),
        "combined": (X_tr_combined, X_va_combined, X_te_combined),
    }


def precision_recall_at_k(y_true, y_score, k_frac=0.10) -> Dict[str, float]:
    """Compute Precision, Recall, and Lift at top-k% of scores."""
    n = len(y_true)
    k = max(1, int(n * k_frac))
    sorted_idx = np.argsort(-y_score)
    top_k_true = y_true[sorted_idx[:k]]
    precision_k = float(top_k_true.mean())
    recall_k    = float(top_k_true.sum() / max(y_true.sum(), 1))
    base_rate   = float(y_true.mean())
    lift_k      = precision_k / base_rate if base_rate > 0 else float("nan")
    return {
        "precision_k": round(precision_k, 4),
        "recall_k": round(recall_k, 4),
        "lift_k": round(lift_k, 4),
        "k_fraction": k_frac,
        "k": k,
    }


def bootstrap_ci_metric(y_true, y_score, metric_fn, n_bootstrap=500, seed=42):
    rng = np.random.RandomState(seed)
    n = len(y_true)
    scores = []
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, n)
        try:
            scores.append(metric_fn(y_true[idx], y_score[idx]))
        except Exception:
            pass
    if not scores:
        return float("nan"), float("nan")
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


def run_phase_5():
    """Run Phase 5: Relief-Risk Prediction & Triage Simulation."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import (
        roc_auc_score, average_precision_score, brier_score_loss,
        precision_recall_curve
    )
    try:
        from sklearn.calibration import calibration_curve
    except ImportError:
        from sklearn.metrics import calibration_curve
    from sklearn.dummy import DummyClassifier
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    setup_logger("complaintscope.relief")
    t0 = time.time()
    cfg = load_config()
    seed = set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 5: Relief-Risk Prediction & Triage Simulation ===")

    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    df_train = df[df["chronological_split"] == "train"].copy().reset_index(drop=True)
    df_val   = df[df["chronological_split"] == "val"].copy().reset_index(drop=True)
    df_test  = df[df["chronological_split"] == "test"].copy().reset_index(drop=True)

    y_train = df_train["relief"].astype(int).values
    y_val   = df_val["relief"].astype(int).values
    y_test  = df_test["relief"].astype(int).values

    # Load TF-IDF
    tfidf_path = Path("data/processed/tfidf_vectorizer.joblib")
    if tfidf_path.exists():
        tfidf_vec = joblib.load(tfidf_path)
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf_vec = TfidfVectorizer(max_features=30000, sublinear_tf=True, ngram_range=(1,2), min_df=2)
        text_col = "narrative_clean" if "narrative_clean" in df_train.columns else "narrative"
        tfidf_vec.fit(df_train[text_col].fillna(""))

    feat = get_relief_features(df_train, df_val, df_test, tfidf_vec)
    X_tr_text, X_va_text, X_te_text = feat["text"]
    X_tr_comb, X_va_comb, X_te_comb = feat["combined"]

    tables_dir  = Path("results/tables")
    figs_dir    = Path("results/figures")
    metrics_dir = Path("results/metrics")
    for d in [tables_dir, figs_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Imbalance ratio
    pos_rate = y_train.mean()
    class_weight_ratio = {0: 1.0, 1: (1 - pos_rate) / max(pos_rate, 1e-9)}
    logger.info(f"Relief base rate (train): {pos_rate:.3f}. Class weight 1: {class_weight_ratio[1]:.2f}")

    # Model suite
    n_bootstrap = cfg.get("bootstrap", {}).get("n_bootstrap", 500)

    # For tree-based HistGradientBoosting, build dense features using TruncatedSVD + aligned metadata
    from sklearn.decomposition import TruncatedSVD
    _cat_cols = [c for c in ["submitted_via", "tags", "state"] if c in df_train.columns]
    _meta_tr_df = pd.get_dummies(
        df_train[_cat_cols].fillna("Unknown").astype(str),
        drop_first=False, dtype=np.float32
    )
    _dense_cols = _meta_tr_df.columns.tolist()
    def _get_dense_meta(df_split):
        dm = pd.get_dummies(
            df_split[[c for c in _cat_cols if c in df_split.columns]].fillna("Unknown").astype(str),
            drop_first=False, dtype=np.float32
        )
        for col in _dense_cols:
            if col not in dm.columns:
                dm[col] = 0.0
        return dm[_dense_cols].values
    svd = TruncatedSVD(n_components=50, random_state=seed)
    X_tr_svd = svd.fit_transform(X_tr_text)
    X_te_svd = svd.transform(X_te_text)
    X_tr_dense = np.hstack([X_tr_svd, _meta_tr_df.values])
    X_te_dense = np.hstack([X_te_svd, _get_dense_meta(df_test)])

    model_configs = [
        ("Prior-Rate Baseline",      DummyClassifier(strategy="prior", random_state=seed), X_tr_text, X_te_text),
        ("Text LR",                  LogisticRegression(C=1.0, max_iter=500, class_weight="balanced", random_state=seed, n_jobs=-1), X_tr_text, X_te_text),
        ("Text+Meta LR",             LogisticRegression(C=1.0, max_iter=500, class_weight="balanced", random_state=seed, n_jobs=-1), X_tr_comb, X_te_comb),
        ("HistGradientBoosting",     HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=seed), X_tr_dense, X_te_dense),
    ]

    results = []
    best_model_name = None
    best_pr_auc = -1
    best_clf = None
    best_X_te = None
    test_scores_dict = {}

    for name, clf, X_tr, X_te in model_configs:
        logger.info(f"  Training {name}...")
        try:
            clf.fit(X_tr, y_train)
            if hasattr(clf, "predict_proba"):
                y_score = clf.predict_proba(X_te)[:, 1]
            else:
                y_score = clf.decision_function(X_te)

            roc_auc  = roc_auc_score(y_test, y_score)
            pr_auc   = average_precision_score(y_test, y_score)
            brier    = brier_score_loss(y_test, y_score)

            # Lift@k metrics
            lift_metrics = {}
            for k_frac in [0.05, 0.10, 0.20]:
                kd = precision_recall_at_k(y_test, y_score, k_frac=k_frac)
                lift_metrics.update({f"precision@{int(k_frac*100)}pct": kd["precision_k"],
                                      f"recall@{int(k_frac*100)}pct": kd["recall_k"],
                                      f"lift@{int(k_frac*100)}pct": kd["lift_k"]})

            # CIs
            roc_ci = bootstrap_ci_metric(y_test, y_score, roc_auc_score, n_bootstrap, seed)
            pr_ci  = bootstrap_ci_metric(y_test, y_score, average_precision_score, n_bootstrap, seed)

            row = {
                "model": name,
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "brier_score": round(brier, 4),
                "roc_ci_lo": round(roc_ci[0], 4), "roc_ci_hi": round(roc_ci[1], 4),
                "pr_ci_lo": round(pr_ci[0], 4),   "pr_ci_hi": round(pr_ci[1], 4),
                **lift_metrics
            }
            results.append(row)
            test_scores_dict[name] = y_score

            if pr_auc > best_pr_auc:
                best_pr_auc = pr_auc
                best_model_name = name
                best_clf = clf
                best_X_te = X_te
        except Exception as e:
            logger.warning(f"  {name} failed: {e}")

    df_results = pd.DataFrame(results).sort_values("pr_auc", ascending=False)
    df_results.to_csv(tables_dir / "relief_results.csv", index=False)
    logger.info(f"\nRelief Results:\n{df_results.to_string(index=False)}")

    # Ablation: company feature (use company name to demonstrate leakage risk)
    logger.info("AQ: Company feature ablation (leakage risk)...")
    if "company" in df_train.columns:
        from sklearn.preprocessing import LabelEncoder
        from scipy.sparse import hstack, csr_matrix
        le_company = LabelEncoder()
        # Include 'Unknown' in training classes explicitly for OOV handling
        all_companies_train = list(df_train["company"].fillna("Unknown").unique()) + ["Unknown"]
        le_company.fit(list(set(all_companies_train)))
        company_tr = le_company.transform(df_train["company"].fillna("Unknown"))
        # Map unseen test companies to 'Unknown'
        test_companies = df_test["company"].fillna("Unknown").apply(
            lambda x: x if x in le_company.classes_ else "Unknown"
        )
        company_te = le_company.transform(test_companies)
        X_company_tr = hstack([X_tr_text, csr_matrix(company_tr.reshape(-1,1))])
        X_company_te = hstack([X_te_text, csr_matrix(company_te.reshape(-1,1))])
        clf_company = LogisticRegression(C=1.0, max_iter=500, class_weight="balanced", random_state=seed, n_jobs=-1)
        try:
            clf_company.fit(X_company_tr, y_train)
            y_score_company = clf_company.predict_proba(X_company_te)[:, 1]
            pr_auc_company = average_precision_score(y_test, y_score_company)
            without_pr = results[1].get("pr_auc", 0) if len(results) > 1 else results[0].get("pr_auc", 0)
            logger.info(f"  With-company PR-AUC: {pr_auc_company:.4f} vs without: {without_pr:.4f}")
            with open(metrics_dir / "company_feature_ablation.json", "w") as f:
                json.dump({"with_company_pr_auc": round(pr_auc_company, 4),
                           "without_company_pr_auc": without_pr}, f, indent=2)
        except Exception as e:
            logger.warning(f"  Company ablation failed: {e}")

    # Calibration curve + figures for best model
    if best_model_name and best_model_name in test_scores_dict:
        y_score_best = test_scores_dict[best_model_name]

        # Calibration curve
        frac_pos, mean_pred = calibration_curve(y_test, y_score_best, n_bins=10)
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(mean_pred, frac_pos, marker="o", label=best_model_name, lw=2, color="#1f77b4")
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect calibration")
        ax.set_xlabel("Mean Predicted Probability", fontsize=12)
        ax.set_ylabel("Fraction Positives", fontsize=12)
        ax.set_title("Fig 11: Calibration Curve – Relief Prediction", fontsize=13)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        fig.savefig(str(figs_dir / "fig11_calibration_curve.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)

        # PR curve
        precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_score_best)
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(recall_vals, precision_vals, lw=2, color="#d62728")
        ax.axhline(y=y_test.mean(), linestyle="--", color="gray", label=f"Baseline (prior={y_test.mean():.2f})")
        ax.set_xlabel("Recall", fontsize=12)
        ax.set_ylabel("Precision", fontsize=12)
        ax.set_title(f"Fig 12: PR Curve – {best_model_name}", fontsize=13)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        fig.savefig(str(figs_dir / "fig12_pr_curve.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)

        # Triage gain simulation
        logger.info("Running triage gain simulation...")
        sorted_idx = np.argsort(-y_score_best)
        n = len(y_test)
        cumulative_gains = np.cumsum(y_test[sorted_idx]) / y_test.sum()
        fractions = np.arange(1, n + 1) / n

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fractions * 100, cumulative_gains * 100, lw=2, color="#2ca02c", label="Relief Risk Model")
        ax.plot([0, 100], [0, 100], "--", color="gray", label="Random")
        ax.axvline(x=20, color="orange", linestyle=":", label="Top 20% reviewed")
        gain_20pct = float(cumulative_gains[int(n * 0.20)])
        ax.annotate(f"{gain_20pct*100:.1f}% gains\nat 20% review",
                    xy=(20, gain_20pct * 100), xytext=(30, gain_20pct * 100 - 10),
                    arrowprops=dict(arrowstyle="->"))
        ax.set_xlabel("% Complaints Reviewed", fontsize=12)
        ax.set_ylabel("% Relief Cases Captured", fontsize=12)
        ax.set_title("Fig 13: Operational Triage Gain Curve", fontsize=13)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        fig.savefig(str(figs_dir / "fig13_triage_gain.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)

        # Fairness slices
        logger.info("Computing fairness/demographic slices...")
        fairness_results = []
        for col in ["submitted_via", "tags", "state"]:
            if col not in df_test.columns:
                continue
            slices = df_test[col].fillna("Unknown").unique()
            for sl in slices[:10]:  # top 10 per dimension
                mask = df_test[col].fillna("Unknown") == sl
                if mask.sum() < 30:
                    continue
                try:
                    sl_pr_auc = average_precision_score(y_test[mask], y_score_best[mask])
                    fairness_results.append({
                        "dimension": col, "slice": sl,
                        "n": int(mask.sum()),
                        "base_rate": round(float(y_test[mask].mean()), 4),
                        "pr_auc": round(sl_pr_auc, 4)
                    })
                except Exception:
                    pass

        pd.DataFrame(fairness_results).to_csv(tables_dir / "fairness_slices.csv", index=False)
        logger.info(f"Saved fairness slices for {len(fairness_results)} groups.")

        # Global feature importance (LR coefficients)
        if "Text LR" in test_scores_dict:
            for mname, mclf, mX_tr, mX_te in model_configs:
                if mname == "Text LR":
                    try:
                        coefs = mclf.coef_[0]  # binary: class 1 coefficients
                        tfidf_path2 = Path("data/processed/tfidf_vectorizer.joblib")
                        if tfidf_path2.exists():
                            tv = joblib.load(tfidf_path2)
                            feat_names = tv.get_feature_names_out()
                        else:
                            feat_names = [f"feat_{i}" for i in range(len(coefs))]

                        top_pos_idx = np.argsort(coefs)[-20:][::-1]
                        top_neg_idx = np.argsort(coefs)[:20]

                        global_feat = {
                            "top_positive_features": [
                                {"feature": str(feat_names[i]), "coef": float(coefs[i])}
                                for i in top_pos_idx
                            ],
                            "top_negative_features": [
                                {"feature": str(feat_names[i]), "coef": float(coefs[i])}
                                for i in top_neg_idx
                            ],
                        }
                        with open(metrics_dir / "relief_global_features.json", "w") as f:
                            json.dump(global_feat, f, indent=2)
                        logger.info("Saved global feature importance for Text LR.")
                    except Exception as e:
                        logger.warning(f"Feature importance failed: {e}")
                    break

    # Save best relief model
    if best_clf is not None:
        app_dir = Path("app/artifacts")
        app_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_clf, app_dir / "relief_classifier.joblib")
        logger.info(f"Saved best relief model ({best_model_name}) to app/artifacts/")

    duration = time.time() - t0
    save_run_metadata("Phase_5_Relief", duration_sec=duration, extra_meta={
        "best_model": best_model_name,
        "best_pr_auc": round(best_pr_auc, 4),
        "n_models": len(results),
    })
    logger.info(f"=== Phase 5 completed in {duration:.1f}s ===")
    return df_results


if __name__ == "__main__":
    run_phase_5()

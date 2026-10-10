"""
ComplaintScope: Classification module.
Phase 4 - Product category classification with model suite, grid search,
           bootstrap CIs, McNemar's test, AQ3 drift experiment, error taxonomy.
"""
import time
import json
import logging
import joblib
from pathlib import Path
from typing import Dict, Tuple, List, Any

import numpy as np
import pandas as pd
from scipy.stats import binom

logger = logging.getLogger("complaintscope.classify")


# ---------------------------------------------------------------------------
# Model suite
# ---------------------------------------------------------------------------

def build_model_suite(seed: int = 42) -> List[Tuple[str, Any]]:
    """Return list of (name, estimator) for classification."""
    from sklearn.dummy import DummyClassifier
    from sklearn.naive_bayes import MultinomialNB, ComplementNB
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV

    models = [
        ("DummyClassifier (majority)",  DummyClassifier(strategy="most_frequent", random_state=seed)),
        ("DummyClassifier (stratified)", DummyClassifier(strategy="stratified",    random_state=seed)),
        ("MultinomialNB",               MultinomialNB(alpha=0.1)),
        ("ComplementNB",                ComplementNB(alpha=0.1)),
        ("DecisionTree (depth=10)",     DecisionTreeClassifier(max_depth=10, random_state=seed)),
        ("LogisticRegression",          LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs",
            multi_class="multinomial", random_state=seed, n_jobs=-1
        )),
        ("LinearSVC (calibrated)",      CalibratedClassifierCV(
            LinearSVC(max_iter=2000, C=0.5, random_state=seed), cv=3
        )),
    ]
    return models


# ---------------------------------------------------------------------------
# Hyperparameter grid (chronological CV on val)
# ---------------------------------------------------------------------------

def grid_search_on_val(
    X_train, y_train, X_val, y_val,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Evaluate a parameter grid for LogisticRegression on the val split.
    Returns best params and grid results DataFrame.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score

    param_grid = {
        "C": [0.01, 0.1, 0.5, 1.0, 5.0, 10.0],
        "solver": ["lbfgs", "saga"],
    }
    grid_results = []
    best_f1, best_params = -1, {}

    for C in param_grid["C"]:
        for solver in param_grid["solver"]:
            try:
                clf = LogisticRegression(
                    C=C, solver=solver, max_iter=1000,
                    multi_class="multinomial", random_state=seed, n_jobs=-1
                )
                clf.fit(X_train, y_train)
                preds = clf.predict(X_val)
                f1 = f1_score(y_val, preds, average="macro")
                grid_results.append({"C": C, "solver": solver, "val_macro_f1": round(f1, 4)})
                if f1 > best_f1:
                    best_f1 = f1
                    best_params = {"C": C, "solver": solver}
            except Exception as e:
                logger.warning(f"Grid search error C={C} solver={solver}: {e}")

    df_grid = pd.DataFrame(grid_results).sort_values("val_macro_f1", ascending=False)
    return best_params, df_grid


# ---------------------------------------------------------------------------
# Bootstrap confidence intervals
# ---------------------------------------------------------------------------

def bootstrap_ci(y_true, y_pred, metric_fn, n_bootstrap: int = 1000, seed: int = 42) -> Tuple[float, float]:
    """Compute 95% bootstrap CI for a metric."""
    rng = np.random.RandomState(seed)
    n = len(y_true)
    scores = []
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, n)
        scores.append(metric_fn(y_true[idx], y_pred[idx]))
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


# ---------------------------------------------------------------------------
# McNemar's test
# ---------------------------------------------------------------------------

def mcnemar_test(y_true, preds_a, preds_b) -> Dict[str, float]:
    """
    McNemar's test between two classifiers.
    Returns the chi-square statistic and p-value.
    """
    from statsmodels.stats.contingency_tables import mcnemar
    correct_a = (preds_a == y_true)
    correct_b = (preds_b == y_true)
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))
    table = np.array([[0, b], [c, 0]])
    try:
        result = mcnemar(table, exact=(b + c) < 25)
        return {"statistic": float(result.statistic), "pvalue": float(result.pvalue), "b": b, "c": c}
    except Exception as e:
        logger.warning(f"McNemar test failed: {e}")
        return {"statistic": float("nan"), "pvalue": float("nan"), "b": b, "c": c}


# ---------------------------------------------------------------------------
# Error taxonomy
# ---------------------------------------------------------------------------

def error_taxonomy(
    df_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    label_encoder,
    n_sample: int = 60
) -> Dict[str, Any]:
    """
    Sample and categorize misclassified test examples.
    Returns taxonomy counts and sampled error rows.
    """
    wrong_mask = y_true != y_pred
    wrong_idx = np.where(wrong_mask)[0]

    rng = np.random.RandomState(42)
    sample_size = min(n_sample, len(wrong_idx))
    sampled_idx = rng.choice(wrong_idx, size=sample_size, replace=False)

    errors_df = df_test.iloc[sampled_idx].copy()
    errors_df["true_label"]  = label_encoder.inverse_transform(y_true[sampled_idx])
    errors_df["pred_label"]  = label_encoder.inverse_transform(y_pred[sampled_idx])
    errors_df["narrative_snippet"] = errors_df["narrative"].astype(str).str[:200]

    # Taxonomy: group by (true, pred) pair
    taxonomy = (
        errors_df.groupby(["true_label", "pred_label"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    return {
        "taxonomy_df": taxonomy,
        "n_errors_total": int(wrong_mask.sum()),
        "n_sampled": sample_size,
        "error_rate": float(wrong_mask.mean()),
    }


# ---------------------------------------------------------------------------
# Phase 4 runner
# ---------------------------------------------------------------------------

def run_phase_4():
    """Run Phase 4: Product Classification."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    from sklearn.metrics import (
        f1_score, accuracy_score, confusion_matrix,
        classification_report
    )
    from sklearn.preprocessing import LabelEncoder
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    setup_logger("complaintscope.classify")
    t0 = time.time()
    cfg = load_config()
    seed = set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 4: Product Classification ===")

    # Load data and features
    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    df_train = df[df["chronological_split"] == "train"].copy().reset_index(drop=True)
    df_val   = df[df["chronological_split"] == "val"].copy().reset_index(drop=True)
    df_test  = df[df["chronological_split"] == "test"].copy().reset_index(drop=True)

    # Random split for AQ3 comparison
    df_rand_train = df[df["random_split"] == "train"].copy().reset_index(drop=True)
    df_rand_test  = df[df["random_split"] == "test"].copy().reset_index(drop=True)

    label_col = "product_consolidated"
    le = LabelEncoder()
    y_train = le.fit_transform(df_train[label_col].astype(str))
    y_val   = le.transform(df_val[label_col].astype(str))
    y_test  = le.transform(df_test[label_col].astype(str))

    y_rand_train = le.transform(df_rand_train[label_col].astype(str))
    y_rand_test  = le.transform(df_rand_test[label_col].astype(str))

    # Load / build TF-IDF vectorizer
    tfidf_path = Path("data/processed/tfidf_vectorizer.joblib")
    if tfidf_path.exists():
        tfidf_vec = joblib.load(tfidf_path)
        text_col = "narrative_clean" if "narrative_clean" in df.columns else "narrative"
        X_train = tfidf_vec.transform(df_train[text_col].fillna(""))
        X_val   = tfidf_vec.transform(df_val[text_col].fillna(""))
        X_test  = tfidf_vec.transform(df_test[text_col].fillna(""))
        X_rand_train = tfidf_vec.transform(df_rand_train[text_col].fillna(""))
        X_rand_test  = tfidf_vec.transform(df_rand_test[text_col].fillna(""))
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        text_col = "narrative_clean" if "narrative_clean" in df.columns else "narrative"
        tfidf_vec = TfidfVectorizer(max_features=30000, sublinear_tf=True,
                                    ngram_range=(1,2), min_df=2)
        X_train = tfidf_vec.fit_transform(df_train[text_col].fillna(""))
        X_val   = tfidf_vec.transform(df_val[text_col].fillna(""))
        X_test  = tfidf_vec.transform(df_test[text_col].fillna(""))
        X_rand_train = tfidf_vec.transform(df_rand_train[text_col].fillna(""))
        X_rand_test  = tfidf_vec.transform(df_rand_test[text_col].fillna(""))

    tables_dir = Path("results/tables")
    figs_dir   = Path("results/figures")
    metrics_dir = Path("results/metrics")
    tables_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    # --- Grid search on val split for LogisticRegression ---
    logger.info("Running hyperparameter grid search on validation split...")
    best_lr_params, df_grid = grid_search_on_val(X_train, y_train, X_val, y_val, seed=seed)
    df_grid.to_csv(tables_dir / "classification_grid.csv", index=False)
    logger.info(f"Best LR params: {best_lr_params}. Grid saved.")

    # --- Train full model suite on train, evaluate on val, final eval on test ---
    models = build_model_suite(seed=seed)

    # Add best LR
    from sklearn.linear_model import LogisticRegression
    best_lr = LogisticRegression(
        C=best_lr_params.get("C", 1.0),
        solver=best_lr_params.get("solver", "lbfgs"),
        max_iter=1000, multi_class="multinomial", random_state=seed, n_jobs=-1
    )
    models.append(("LogisticRegression (tuned)", best_lr))

    # Attempt MiniLM + LR if embeddings available
    emb_train_path = Path("data/processed/emb_train.npy")
    emb_test_path  = Path("data/processed/emb_test.npy")
    emb_train = np.load(str(emb_train_path)) if emb_train_path.exists() else None
    emb_test  = np.load(str(emb_test_path))  if emb_test_path.exists()  else None

    if emb_train is not None:
        emb_lr = LogisticRegression(C=1.0, max_iter=1000, random_state=seed, n_jobs=-1)
        models.append(("MiniLM-L6 + LR", emb_lr))

    results = []
    val_preds_dict = {}
    test_preds_dict = {}
    n_bootstrap = cfg.get("bootstrap", {}).get("n_bootstrap", 500)

    for name, clf in models:
        logger.info(f"  Training {name}...")
        try:
            if name == "MiniLM-L6 + LR" and emb_train is not None:
                clf.fit(emb_train, y_train)
                val_preds  = clf.predict(np.load(str(Path("data/processed/emb_val.npy"))))
                test_preds = clf.predict(emb_test)
            else:
                clf.fit(X_train, y_train)
                val_preds  = clf.predict(X_val)
                test_preds = clf.predict(X_test)

            val_f1  = f1_score(y_val,  val_preds,  average="macro")
            test_f1 = f1_score(y_test, test_preds, average="macro")
            test_acc = accuracy_score(y_test, test_preds)

            # Bootstrap CI on test
            ci_lo, ci_hi = bootstrap_ci(
                y_test, test_preds,
                lambda yt, yp: f1_score(yt, yp, average="macro", zero_division=0),
                n_bootstrap=n_bootstrap, seed=seed
            )

            results.append({
                "model": name,
                "val_macro_f1": round(val_f1, 4),
                "test_macro_f1": round(test_f1, 4),
                "test_accuracy": round(test_acc, 4),
                "ci_lo_95": round(ci_lo, 4),
                "ci_hi_95": round(ci_hi, 4),
            })
            val_preds_dict[name]  = val_preds
            test_preds_dict[name] = test_preds

        except Exception as e:
            logger.warning(f"  Model {name} failed: {e}")

    df_results = pd.DataFrame(results).sort_values("test_macro_f1", ascending=False)
    df_results.to_csv(tables_dir / "classification_results.csv", index=False)
    logger.info(f"\nClassification Results:\n{df_results.to_string(index=False)}")

    # --- Best model: McNemar's test vs. baseline ---
    best_model_name = df_results.iloc[0]["model"]
    worst_model_name = df_results.iloc[-1]["model"]
    if best_model_name in test_preds_dict and worst_model_name in test_preds_dict:
        mcnemar_result = mcnemar_test(y_test, test_preds_dict[best_model_name],
                                      test_preds_dict[worst_model_name])
        logger.info(f"McNemar's test ({best_model_name} vs {worst_model_name}): {mcnemar_result}")
        with open(metrics_dir / "mcnemar_test.json", "w") as f:
            json.dump({"best": best_model_name, "vs": worst_model_name, **mcnemar_result}, f, indent=2)

    # --- AQ3: Chronological vs. random split drift ---
    logger.info("AQ3: Evaluating chronological vs. random split drift...")
    from sklearn.linear_model import LogisticRegression
    aq3_clf = LogisticRegression(C=best_lr_params.get("C", 1.0), max_iter=1000,
                                  random_state=seed, n_jobs=-1)
    aq3_clf.fit(X_train, y_train)
    chrono_test_f1 = f1_score(y_test, aq3_clf.predict(X_test), average="macro")
    rand_test_f1   = f1_score(y_rand_test, aq3_clf.predict(X_rand_test), average="macro")

    aq3_result = {
        "chronological_test_macro_f1": round(chrono_test_f1, 4),
        "random_test_macro_f1": round(rand_test_f1, 4),
        "f1_drop": round(rand_test_f1 - chrono_test_f1, 4),
    }
    with open(metrics_dir / "aq3_split_drift.json", "w") as f:
        json.dump(aq3_result, f, indent=2)
    logger.info(f"AQ3 Split Drift: {aq3_result}")

    # --- Best model: Confusion matrix & classification report ---
    if best_model_name in test_preds_dict:
        best_preds = test_preds_dict[best_model_name]
        cm = confusion_matrix(y_test, best_preds)
        class_report = classification_report(
            y_test, best_preds,
            target_names=le.classes_, output_dict=True
        )
        with open(metrics_dir / "classification_report.json", "w") as f:
            json.dump(class_report, f, indent=2)

        # Confusion matrix figure
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(
            pd.DataFrame(cm, index=le.classes_, columns=le.classes_),
            annot=True, fmt="d", cmap="Blues", ax=ax,
            linewidths=0.3, cbar_kws={"shrink": 0.8}
        )
        ax.set_title(f"Fig 10: Confusion Matrix – {best_model_name}", fontsize=12)
        ax.set_xlabel("Predicted Product", fontsize=10)
        ax.set_ylabel("True Product", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        cm_path = figs_dir / "fig10_confusion_matrix.png"
        fig.savefig(str(cm_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved confusion matrix to {cm_path}")

        # --- Error taxonomy ---
        logger.info("Running error taxonomy analysis...")
        err_tax = error_taxonomy(df_test, y_test, best_preds, le, n_sample=60)
        err_tax["taxonomy_df"].to_csv(tables_dir / "error_taxonomy.csv", index=False)
        err_tax_summary = {k: v for k, v in err_tax.items() if k != "taxonomy_df"}
        with open(metrics_dir / "error_taxonomy_summary.json", "w") as f:
            json.dump(err_tax_summary, f, indent=2)
        logger.info(f"Error taxonomy: {err_tax_summary}")

    # --- Save best classifier + vectorizer for app ---
    best_clf_obj = None
    for name, clf in models:
        if name == best_model_name:
            best_clf_obj = clf
            break
    if best_clf_obj is not None:
        app_artifacts_dir = Path("app/artifacts")
        app_artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_clf_obj,  app_artifacts_dir / "product_classifier.joblib")
        joblib.dump(tfidf_vec,     app_artifacts_dir / "tfidf_vectorizer.joblib")
        joblib.dump(le,            app_artifacts_dir / "label_encoder_product.joblib")
        logger.info(f"Saved app artifacts for {best_model_name}.")

    duration = time.time() - t0
    save_run_metadata("Phase_4_Classification", duration_sec=duration, extra_meta={
        "best_model": best_model_name,
        "best_test_macro_f1": float(df_results.iloc[0]["test_macro_f1"]),
        "aq3_result": aq3_result,
    })
    logger.info(f"=== Phase 4 completed in {duration:.1f}s ===")
    return df_results


if __name__ == "__main__":
    run_phase_4()

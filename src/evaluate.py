"""
ComplaintScope: Evaluation & Statistical Testing Helpers.
Provides bootstrap confidence intervals, McNemar's test, and ranking metrics.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Callable
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss


def bootstrap_ci(
    y_true: np.ndarray,
    y_score: np.ndarray,
    metric_fn: Callable,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42
) -> Tuple[float, float]:
    """Calculate non-parametric bootstrap confidence interval for any metric."""
    rng = np.random.RandomState(seed)
    n = len(y_true)
    scores = []
    alpha = (1.0 - ci_level) / 2.0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, n)
        try:
            val = metric_fn(y_true[idx], y_score[idx])
            if not np.isnan(val):
                scores.append(val)
        except Exception:
            pass
    if not scores:
        return float("nan"), float("nan")
    lo = float(np.percentile(scores, alpha * 100))
    hi = float(np.percentile(scores, (1.0 - alpha) * 100))
    return lo, hi


def mcnemar_test(y_true: np.ndarray, pred_a: np.ndarray, pred_b: np.ndarray) -> Dict[str, Any]:
    """Compute exact or continuity-corrected McNemar's test between two models."""
    from scipy.stats import chi2
    correct_a = (pred_a == y_true)
    correct_b = (pred_b == y_true)

    # b: A correct, B incorrect; c: A incorrect, B correct
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))

    if b + c == 0:
        return {"statistic": 0.0, "pvalue": 1.0, "b": b, "c": c}

    # Continuity-corrected chi-squared statistic
    stat = float(((abs(b - c) - 1.0) ** 2) / (b + c))
    pval = float(1.0 - chi2.cdf(stat, df=1))
    return {"statistic": stat, "pvalue": pval, "b": b, "c": c}


def precision_recall_at_k(y_true: np.ndarray, y_score: np.ndarray, k_frac: float = 0.10) -> Dict[str, float]:
    """Calculate Precision@k, Recall@k, and Lift@k for top fraction k."""
    n = len(y_true)
    k = max(1, int(n * k_frac))
    top_indices = np.argsort(y_score)[::-1][:k]

    positives_captured = y_true[top_indices].sum()
    total_positives = y_true.sum()

    precision_k = float(positives_captured / k)
    recall_k = float(positives_captured / total_positives) if total_positives > 0 else 0.0
    base_rate = float(total_positives / n)
    lift_k = float(precision_k / base_rate) if base_rate > 0 else 0.0

    return {
        "precision_k": round(precision_k, 4),
        "recall_k": round(recall_k, 4),
        "lift_k": round(lift_k, 4),
        "k": k,
        "k_frac": k_frac,
    }

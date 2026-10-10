"""
Unit tests for SRI, burst detection, and feature modules.
"""
import pytest
import numpy as np
import pandas as pd


# ─── SRI tests ────────────────────────────────────────────────────────────────

def test_sri_normalization():
    """Verify SRI scores are in [0, 1]."""
    from src.sri import compute_sri, normalize_0_1

    s = pd.Series([1.0, 5.0, 10.0, 2.0])
    normalized = normalize_0_1(s)
    assert normalized.min() >= 0.0
    assert normalized.max() <= 1.0
    assert abs(normalized.max() - 1.0) < 1e-9


def test_sri_ranking_reproducible():
    """SRI ranking is deterministic given same data."""
    from src.sri import compute_sri, DEFAULT_WEIGHTS

    df_agg_company = pd.DataFrame({
        "company": ["A", "A", "B", "B"],
        "count": [1000, 500, 200, 100],
        "month": ["2020-01", "2020-02", "2020-01", "2020-02"]
    })
    df_agg_ci = pd.DataFrame({
        "company": ["A", "A", "B"],
        "issue": ["I1", "I2", "I1"],
        "count": [500, 300, 100]
    })
    df_cent = pd.DataFrame({"node": ["A", "B"], "weighted_degree": [10.0, 2.0]})
    df_clean = pd.DataFrame({
        "company": ["A", "A", "B"],
        "relief": [1, 0, 1]
    })

    r1 = compute_sri(df_agg_company, df_agg_ci, df_cent, df_clean, top_n=5)
    r2 = compute_sri(df_agg_company, df_agg_ci, df_cent, df_clean, top_n=5)
    pd.testing.assert_frame_equal(r1.reset_index(drop=True), r2.reset_index(drop=True))


# ─── Burst detection tests ──────────────────────────────────────────────────

def test_rolling_zscore_detects_spike():
    """Verify rolling z-score flags an obvious spike."""
    from src.burst import rolling_zscore_burst

    # A flat series with a large spike at the end
    values = [0.10] * 20 + [0.80]
    series = pd.Series(values)
    alerts = rolling_zscore_burst(series, window=10, threshold=2.0)
    assert alerts.iloc[-1] == True


def test_ewma_cusum_detects_upward_trend():
    """Verify EWMA CUSUM detects sustained upward trend."""
    from src.burst import ewma_cusum_burst

    # Gradual increase
    values = list(np.linspace(0.1, 0.9, 25))
    series = pd.Series(values)
    alerts = ewma_cusum_burst(series, span=4, threshold=0.5)
    # At least some alert months
    assert alerts.sum() >= 1


def test_proxy_validation_output_keys():
    """Verify proxy evaluation returns all required keys."""
    from src.burst import evaluate_burst_alerts

    alert_series = pd.Series([True, False, True, False, True], index=range(5))
    proxy_series = pd.Series([0.1, 0.2, 0.8, 0.1, 0.9], index=range(5))
    result = evaluate_burst_alerts(alert_series, proxy_series)

    assert "precision" in result
    assert "recall" in result
    assert "f1" in result


# ─── Feature module tests ────────────────────────────────────────────────────

def test_metadata_features_no_company():
    """Verify metadata encoding does not include company."""
    from src.features import build_metadata_features

    df = pd.DataFrame({
        "submitted_via": ["Web", "Phone", "Web"],
        "tags": ["Servicemember", None, "Older American"],
        "state": ["CA", "TX", "NY"],
        "company": ["Bank A", "Bank B", "Bank A"],  # should not appear in feature names
    })
    matrix, feat_names = build_metadata_features(df)

    # Feature names should not contain 'company'
    for fn in feat_names:
        assert "company" not in fn.lower()

    assert matrix.shape[0] == 3


def test_bow_vectorizer_fit_on_train_only():
    """Verify BoW vectorizer fitted on train does not include val vocabulary."""
    from src.features import build_bow_vectorizer
    import numpy as np

    train_texts = pd.Series(["bank account overdraft fee", "credit report dispute error"])
    val_texts   = pd.Series(["mortgage forbearance servicer"])

    vec, X_train = build_bow_vectorizer(train_texts, max_features=100)
    X_val = vec.transform(val_texts)

    # Vocabulary only contains train words
    vocab = set(vec.vocabulary_.keys())
    assert "forbearance" not in vocab

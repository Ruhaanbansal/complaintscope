"""
ComplaintScope: End-to-end smoke test on demo sample.
Verifies the complete pipeline flow runs end-to-end without errors.
"""
import pytest
from pathlib import Path
import pandas as pd
import numpy as np


def test_smoke_pipeline_end_to_end():
    sample_path = Path("data/sample/complaints_demo_2k.csv")
    assert sample_path.exists(), "Sample dataset missing"

    df_demo = pd.read_csv(sample_path)
    assert len(df_demo) > 0, "Demo sample is empty"

    # 1. Preprocess test
    from src.preprocess import handle_redactions, remove_noise
    sample_text = df_demo["narrative"].iloc[0]
    cleaned = remove_noise(handle_redactions(sample_text, mode="placeholder"))
    assert isinstance(cleaned, str)
    assert len(cleaned) > 0

    # 2. Features & Classifier test
    from app.streamlit_app import load_classifier, load_relief_model
    clf, vec, le = load_classifier()
    assert clf is not None and vec is not None and le is not None

    X = vec.transform([cleaned])
    pred_idx = clf.predict(X)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    assert isinstance(pred_label, str)

    # 3. Relief prediction test
    relief_clf = load_relief_model()
    assert relief_clf is not None
    relief_proba = relief_clf.predict_proba(X)[0, 1]
    assert 0.0 <= relief_proba <= 1.0

    # 4. Burst detection test
    from src.burst import rolling_zscore_burst
    s = pd.Series([0.1]*10 + [0.9])
    alerts = rolling_zscore_burst(s, window=5, threshold=1.5)
    assert alerts.iloc[-1] == True

    # 5. Network test
    from src.network import build_bipartite_graph
    toy_df = pd.DataFrame({
        "company": ["Bank A", "Bank A", "Bank B"],
        "issue": ["Fee", "Fraud", "Fee"],
        "count": [10, 5, 8]
    })
    G = build_bipartite_graph(toy_df, min_count=1)
    assert G.number_of_nodes() >= 3

    # 6. SRI test
    from src.sri import compute_sri
    df_agg = pd.DataFrame({
        "company": ["Bank A", "Bank B"],
        "count": [100, 50],
        "month": ["2022-01", "2022-01"]
    })
    df_ci = pd.DataFrame({
        "company": ["Bank A", "Bank B"],
        "issue": ["Fee", "Fee"],
        "count": [100, 50]
    })
    df_cent = pd.DataFrame({"node": ["Bank A", "Bank B"], "weighted_degree": [1.0, 0.5]})
    df_clean = pd.DataFrame({"company": ["Bank A", "Bank B"], "relief": [1, 0]})
    sri_df = compute_sri(df_agg, df_ci, df_cent, df_clean, top_n=2)
    assert not sri_df.empty
    assert "SRI" in sri_df.columns

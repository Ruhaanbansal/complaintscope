"""
Smoke tests for Streamlit application artifacts and prediction pipeline.
"""
import pytest
from pathlib import Path
import pandas as pd
import numpy as np


def test_artifacts_exist_and_load():
    from app.streamlit_app import (
        load_classifier, load_relief_model, load_sri,
        load_topic_labels, load_demo_data
    )

    clf, vec, le = load_classifier()
    assert clf is not None, "Product classifier failed to load"
    assert vec is not None, "TF-IDF vectorizer failed to load"
    assert le is not None, "Label encoder failed to load"

    relief_clf = load_relief_model()
    assert relief_clf is not None, "Relief classifier failed to load"

    df_sri = load_sri()
    assert not df_sri.empty, "SRI table is empty"
    assert "SRI" in df_sri.columns

    topics = load_topic_labels()
    assert isinstance(topics, dict)
    assert len(topics) > 0, "Topic labels empty"

    demo_df = load_demo_data()
    assert not demo_df.empty, "Demo complaints empty"


def test_end_to_end_prediction():
    from app.streamlit_app import load_classifier, load_relief_model

    clf, vec, le = load_classifier()
    relief_clf = load_relief_model()

    test_narrative = "There is an inaccurate collection account on my credit report from a debt collector that I never opened."

    # Product prediction
    X_vec = vec.transform([test_narrative])
    pred_idx = clf.predict(X_vec)[0]
    pred_product = le.inverse_transform([pred_idx])[0]
    proba = clf.predict_proba(X_vec)[0]

    assert isinstance(pred_product, str)
    assert len(pred_product) > 0
    assert 0.0 <= proba.max() <= 1.0

    # Relief prediction
    relief_proba = relief_clf.predict_proba(X_vec)[0, 1]
    assert 0.0 <= relief_proba <= 1.0

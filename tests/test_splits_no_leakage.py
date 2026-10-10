"""
Unit tests for chronological and random dataset splits:
Ensures zero temporal leakage, strict boundary monotonicity, and zero ID overlap.
"""
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

def verify_chronological_splits(df_train: pd.DataFrame, df_val: pd.DataFrame, df_test: pd.DataFrame, date_col: str = "date_received", id_col: str = "complaint_id"):
    """
    Asserts strict chronological separation and zero ID leakage between splits.
    """
    train_dates = pd.to_datetime(df_train[date_col])
    val_dates = pd.to_datetime(df_val[date_col])
    test_dates = pd.to_datetime(df_test[date_col])
    
    max_train = train_dates.max()
    min_val = val_dates.min()
    max_val = val_dates.max()
    min_test = test_dates.min()
    
    # Assert temporal boundaries do not cross
    assert max_train <= min_val, f"Leakage detected: max train date ({max_train}) > min val date ({min_val})"
    assert max_val <= min_test, f"Leakage detected: max val date ({max_val}) > min test date ({min_test})"
    
    # Assert zero ID overlap
    train_ids = set(df_train[id_col])
    val_ids = set(df_val[id_col])
    test_ids = set(df_test[id_col])
    
    overlap_train_val = train_ids.intersection(val_ids)
    overlap_val_test = val_ids.intersection(test_ids)
    overlap_train_test = train_ids.intersection(test_ids)
    
    assert len(overlap_train_val) == 0, f"Found {len(overlap_train_val)} overlapping IDs between train and val"
    assert len(overlap_val_test) == 0, f"Found {len(overlap_val_test)} overlapping IDs between val and test"
    assert len(overlap_train_test) == 0, f"Found {len(overlap_train_test)} overlapping IDs between train and test"

def test_toy_chronological_split():
    """Verify split verification logic on synthetic date-ordered data."""
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "complaint_id": range(100),
        "date_received": dates,
        "narrative": [f"Complaint narrative number {i}" for i in range(100)],
        "product": ["Mortgage"] * 50 + ["Debt collection"] * 50
    })
    
    # 70 / 15 / 15 split
    n = len(df)
    train_end_idx = int(n * 0.70)
    val_end_idx = int(n * 0.85)
    
    train_df = df.iloc[:train_end_idx]
    val_df = df.iloc[train_end_idx:val_end_idx]
    test_df = df.iloc[val_end_idx:]
    
    verify_chronological_splits(train_df, val_df, test_df)

def test_actual_interim_splits_if_available():
    """Verify real data splits if data/interim/complaints_clean.parquet exists."""
    clean_path = Path("data/interim/complaints_clean.parquet")
    if not clean_path.exists():
        pytest.skip("complaints_clean.parquet not yet generated.")
        
    df = pd.read_parquet(clean_path)
    if "chronological_split" not in df.columns:
        pytest.skip("chronological_split column not present.")
        
    train_df = df[df["chronological_split"] == "train"]
    val_df = df[df["chronological_split"] == "val"]
    test_df = df[df["chronological_split"] == "test"]
    
    assert len(train_df) > 0, "Train split is empty"
    assert len(val_df) > 0, "Val split is empty"
    assert len(test_df) > 0, "Test split is empty"
    
    verify_chronological_splits(train_df, val_df, test_df)

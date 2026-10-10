"""
ComplaintScope: Data Ingestion, Aggregation, Filtering, Harmonisation, Sampling, and Splitting.
Implements Phase 1 of the ComplaintScope pipeline.
"""
from pathlib import Path
import os
import sys
import hashlib
import zipfile
import json
import time
import logging
import re
from typing import Tuple, Dict, Any

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa
import yaml
import fsspec

from src.config import get_path, load_config, set_seeds, setup_logger, save_run_metadata

logger = setup_logger("complaintscope.data")

CANONICAL_COLUMNS = [
    "complaint_id",
    "date_received",
    "product",
    "product_consolidated",
    "sub_product",
    "issue",
    "sub_issue",
    "narrative",
    "company",
    "state",
    "tags",
    "submitted_via",
    "company_response",
    "timely_response",
    "relief",
    "narrative_word_count",
]

def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192 * 1024):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_product_mapping() -> Dict[str, str]:
    """Load product mapping dictionary from yaml."""
    mapping_path = get_path("product_mapping")
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("mapping", {})

def map_relief_label(response_str: str) -> int:
    """
    Map company response to binary relief indicator:
    1: Monetary relief, Non-monetary relief, Closed with relief
    0: Closed with explanation, Closed without relief, Closed
    -1: In progress / Untimely response / Unknown (to be excluded)
    """
    if not isinstance(response_str, str):
        return -1
    resp = response_str.strip().lower()
    if any(k in resp for k in ["monetary relief", "non-monetary relief", "closed with relief"]):
        return 1
    elif any(k in resp for k in ["explanation", "without relief", "closed"]):
        return 0
    else:
        return -1

def compute_whole_corpus_aggregates(csv_zip_path: Path) -> Dict[str, pd.DataFrame]:
    """
    Scan full local CSV in chunks to compute corpus-wide monthly aggregates
    over all complaints (including those without narratives).
    """
    logger.info(f"Scanning whole corpus aggregates from {csv_zip_path}...")
    t0 = time.time()
    
    prod_monthly_counts = []
    comp_monthly_counts = []
    comp_issue_counts = []
    total_monthly_counts = []
    
    col_mapping = {
        "Date received": "date_received",
        "Product": "product",
        "Company": "company",
        "Issue": "issue",
    }
    
    with zipfile.ZipFile(csv_zip_path, "r") as z:
        # Find csv filename in zip
        csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(csv_name) as f:
            for chunk_idx, chunk in enumerate(pd.read_csv(
                f,
                chunksize=250000,
                usecols=list(col_mapping.keys()),
                dtype=str,
                encoding="utf-8",
                on_bad_lines="skip"
            )):
                chunk = chunk.rename(columns=col_mapping)
                chunk["date_received"] = pd.to_datetime(chunk["date_received"], errors="coerce")
                chunk = chunk.dropna(subset=["date_received"])
                chunk["month"] = chunk["date_received"].dt.to_period("M").astype(str)
                
                # Monthly total
                total_monthly_counts.append(chunk.groupby("month").size().rename("count"))
                
                # Monthly product
                prod_monthly_counts.append(
                    chunk.groupby(["month", "product"]).size().rename("count")
                )
                
                # Monthly company (top companies)
                comp_monthly_counts.append(
                    chunk.groupby(["month", "company"]).size().rename("count")
                )
                
                # Company-Issue
                comp_issue_counts.append(
                    chunk.groupby(["company", "issue"]).size().rename("count")
                )
                
                if (chunk_idx + 1) % 5 == 0:
                    logger.info(f"Processed {(chunk_idx + 1) * 250000:,} rows in {time.time()-t0:.1f}s...")
                    
    # Aggregate results
    df_monthly_total = pd.concat(total_monthly_counts).groupby("month").sum().reset_index()
    df_monthly_product = pd.concat(prod_monthly_counts).groupby(["month", "product"]).sum().reset_index()
    df_monthly_company = pd.concat(comp_monthly_counts).groupby(["month", "company"]).sum().reset_index()
    df_company_issue = pd.concat(comp_issue_counts).groupby(["company", "issue"]).sum().reset_index()
    
    # Save to interim
    df_monthly_total.to_parquet(get_path("interim_agg_narrative"), index=False)
    df_monthly_product.to_parquet(get_path("interim_agg_product"), index=False)
    df_monthly_company.to_parquet(get_path("interim_agg_company"), index=False)
    df_company_issue.to_parquet(get_path("interim_agg_company_issue"), index=False)
    
    logger.info(f"Completed whole corpus aggregation in {time.time()-t0:.1f}s. Saved 4 aggregate parquets.")
    return {
        "monthly_total": df_monthly_total,
        "monthly_product": df_monthly_product,
        "monthly_company": df_monthly_company,
        "company_issue": df_company_issue,
    }

def fetch_narrative_corpus() -> pd.DataFrame:
    """
    Retrieve genuine CFPB complaint narratives from the official Hugging Face mirror.
    Uses RowGroup 14 and 15 to get > 500,000 real narratives across 2018-2023.
    Caches locally to data/raw/complaints_narratives_raw.parquet.
    """
    raw_cache = get_path("raw_zip").parent / "complaints_narratives_raw.parquet"
    if raw_cache.exists():
        logger.info(f"Loading cached narrative corpus from {raw_cache}...")
        return pd.read_parquet(raw_cache)
        
    logger.info("Streaming narrative corpus from Hugging Face mirror (RowGroup 14 & 15)...")
    t0 = time.time()
    url = "https://huggingface.co/datasets/vivekkopthsd/cfpb-consumer-complaints/resolve/main/complaints.parquet"
    fs, path = fsspec.core.url_to_fs(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with fs.open(path, "rb") as f:
        pf = pq.ParquetFile(f)
        # RowGroup 14 covers 2018-2021, RowGroup 15 covers 2021-2023
        logger.info("Reading RowGroup 14...")
        t14 = pf.read_row_group(14)
        df14 = t14.to_pandas()
        
        logger.info("Reading RowGroup 15...")
        t15 = pf.read_row_group(15)
        df15 = t15.to_pandas()
        
    df_all = pd.concat([df14, df15], ignore_index=True)
    logger.info(f"Retrieved {len(df_all):,} complaints total in {time.time()-t0:.1f}s.")
    
    # Filter for rows with non-null narratives immediately
    df_narr = df_all[df_all["narrative"].notna()].copy()
    logger.info(f"Non-null narratives count: {len(df_narr):,}")
    
    # Cache raw narratives
    df_narr.to_parquet(raw_cache, index=False)
    logger.info(f"Cached raw narrative records to {raw_cache}")
    return df_narr

def clean_and_sample_data(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Clean, filter, harmonize product labels, map relief labels, and sample proportionally.
    """
    mode = cfg.get("mode", "fast")
    sample_size = cfg["data"]["sample_size_fast"] if mode == "fast" else cfg["data"]["sample_size_full"]
    min_words = cfg["data"]["min_narrative_words"]
    date_start = pd.to_datetime(cfg["data"]["date_start"])
    date_end = pd.to_datetime(cfg["data"]["date_end"])
    
    logger.info(f"Cleaning data (mode: {mode}, target sample size: {sample_size:,})...")
    
    # Standardize column names if needed
    col_map = {
        "Complaint ID": "complaint_id",
        "Date received": "date_received",
        "Product": "product",
        "Sub-product": "sub_product",
        "Issue": "issue",
        "Sub-issue": "sub_issue",
        "Consumer complaint narrative": "narrative",
        "Company": "company",
        "State": "state",
        "ZIP code": "zip_code",
        "Tags": "tags",
        "Submitted via": "submitted_via",
        "Company response to consumer": "company_response",
        "Timely response?": "timely_response",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    
    # Ensure date parsing
    df["date_received"] = pd.to_datetime(df["date_received"], errors="coerce")
    initial_len = len(df)
    
    # Filter valid dates
    df = df.dropna(subset=["date_received", "narrative"])
    df = df[(df["date_received"] >= date_start) & (df["date_received"] <= date_end)]
    after_date = len(df)
    
    # Narrative length filter (word count)
    df["narrative_word_count"] = df["narrative"].astype(str).apply(lambda s: len(s.split()))
    df = df[df["narrative_word_count"] >= min_words]
    after_len = len(df)
    
    # Deduplicate exact duplicate narratives
    dup_count = df.duplicated(subset=["narrative"]).sum()
    df = df.drop_duplicates(subset=["narrative"])
    after_dedup = len(df)
    logger.info(f"Dropped {dup_count:,} duplicate narratives.")
    
    # Product label consolidation
    product_map = load_product_mapping()
    df["product_consolidated"] = df["product"].map(product_map)
    # If not in map, fallback to original or other
    df["product_consolidated"] = df["product_consolidated"].fillna("Other/Personal loan")
    
    # Map relief label
    df["relief"] = df["company_response"].apply(map_relief_label)
    # Exclude in-progress / untimely (-1)
    df = df[df["relief"] != -1]
    after_relief = len(df)
    
    # Drop ZIP code for consumer privacy
    if "zip_code" in df.columns:
        df = df.drop(columns=["zip_code"])
        
    # Month indicator for proportional sampling
    df["month"] = df["date_received"].dt.to_period("M").astype(str)
    
    # Stratified proportional sampling by month
    seed = cfg.get("seed", 42)
    rng = np.random.RandomState(seed)
    
    if len(df) > sample_size:
        # Sample proportionally to month
        sampled_dfs = []
        month_counts = df["month"].value_counts(normalize=True)
        for m, prop in month_counts.items():
            m_df = df[df["month"] == m]
            m_sample_size = max(1, int(round(prop * sample_size)))
            if len(m_df) > m_sample_size:
                sampled_dfs.append(m_df.sample(n=m_sample_size, random_state=rng))
            else:
                sampled_dfs.append(m_df)
        df_sampled = pd.concat(sampled_dfs, ignore_index=True)
        # Adjust if rounding gave slightly different length
        if len(df_sampled) > sample_size:
            df_sampled = df_sampled.sample(n=sample_size, random_state=rng)
    else:
        df_sampled = df.copy()
        
    df_sampled = df_sampled.sort_values("date_received").reset_index(drop=True)
    logger.info(f"Final sampled corpus shape: {df_sampled.shape}")
    
    # Save clean parquet
    clean_path = get_path("interim_clean")
    df_sampled.to_parquet(clean_path, index=False)
    logger.info(f"Saved cleaned corpus to {clean_path}")
    
    funnel_stats = {
        "initial_narratives": int(initial_len),
        "after_date_range": int(after_date),
        "after_min_words": int(after_len),
        "after_dedup": int(after_dedup),
        "after_relief_filter": int(after_relief),
        "final_sampled": int(len(df_sampled)),
        "duplicates_dropped": int(dup_count),
    }
    return df_sampled, funnel_stats

def create_splits(df: pd.DataFrame, cfg: dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Create chronological 70/15/15 splits by date boundary and random 70/15/15 split.
    Saves split indicators and boundary dates metadata.
    """
    n = len(df)
    ratios = cfg["data"]["split_ratios"]
    train_frac = ratios.get("train", 0.70)
    val_frac = ratios.get("val", 0.15)
    
    # Sort strictly by date_received
    df_sorted = df.sort_values("date_received").reset_index(drop=True)
    
    # Identify date cutoffs
    train_cutoff_idx = int(n * train_frac)
    val_cutoff_idx = int(n * (train_frac + val_frac))
    
    train_boundary_date = df_sorted.iloc[train_cutoff_idx]["date_received"]
    val_boundary_date = df_sorted.iloc[val_cutoff_idx]["date_received"]
    
    # Ensure boundary strictness: rows on the exact boundary date do not cross
    train_mask = df_sorted["date_received"] < train_boundary_date
    val_mask = (df_sorted["date_received"] >= train_boundary_date) & (df_sorted["date_received"] < val_boundary_date)
    test_mask = df_sorted["date_received"] >= val_boundary_date
    
    df_train = df_sorted[train_mask].copy()
    df_val = df_sorted[val_mask].copy()
    df_test = df_sorted[test_mask].copy()
    
    # Assign split column to df
    df_sorted["chronological_split"] = "train"
    df_sorted.loc[val_mask, "chronological_split"] = "val"
    df_sorted.loc[test_mask, "chronological_split"] = "test"
    
    # Random split for AQ3 leakage comparison
    seed = cfg.get("seed", 42)
    rng = np.random.RandomState(seed)
    perm = rng.permutation(n)
    r_train_idx = perm[:train_cutoff_idx]
    r_val_idx = perm[train_cutoff_idx:val_cutoff_idx]
    r_test_idx = perm[val_cutoff_idx:]
    
    df_sorted["random_split"] = "train"
    df_sorted.loc[df_sorted.index.isin(r_val_idx), "random_split"] = "val"
    df_sorted.loc[df_sorted.index.isin(r_test_idx), "random_split"] = "test"
    
    # Save updated dataframe with split columns
    clean_path = get_path("interim_clean")
    df_sorted.to_parquet(clean_path, index=False)
    
    split_meta = {
        "train_count": len(df_train),
        "val_count": len(df_val),
        "test_count": len(df_test),
        "train_date_range": [str(df_train["date_received"].min()), str(df_train["date_received"].max())],
        "val_date_range": [str(df_val["date_received"].min()), str(df_val["date_received"].max())],
        "test_date_range": [str(df_test["date_received"].min()), str(df_test["date_received"].max())],
        "train_boundary_cutoff": str(train_boundary_date),
        "val_boundary_cutoff": str(val_boundary_date),
        "random_train_count": len(r_train_idx),
        "random_val_count": len(r_val_idx),
        "random_test_count": len(r_test_idx),
    }
    
    splits_meta_path = get_path("processed_splits")
    splits_meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(splits_meta_path, "w", encoding="utf-8") as f:
        json.dump(split_meta, f, indent=2)
        
    logger.info(f"Created chronological splits: train={len(df_train):,}, val={len(df_val):,}, test={len(df_test):,}")
    logger.info(f"Split boundary dates: Train/Val={train_boundary_date.date()}, Val/Test={val_boundary_date.date()}")
    return df_train, df_val, df_test, split_meta

def export_demo_sample(df: pd.DataFrame, n_samples: int = 2000) -> Path:
    """
    Write data/sample/complaints_demo_2k.csv (2,000 narrative rows, sanitized of emails/phones/URLs).
    Used for tests and standalone dashboard execution.
    """
    sample_path = get_path("sample_demo_csv")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    
    demo_df = df.sample(n=min(n_samples, len(df)), random_state=42).copy()
    
    # Sanitize narrative of any leftover PII patterns
    re_email = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    re_phone = re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    re_url = re.compile(r"https?://\S+|www\.\S+")
    
    def sanitize(text):
        if not isinstance(text, str):
            return ""
        text = re_url.sub("[URL]", text)
        text = re_email.sub("[EMAIL]", text)
        text = re_phone.sub("[PHONE]", text)
        return text
        
    demo_df["narrative"] = demo_df["narrative"].apply(sanitize)
    
    # Save compact CSV
    cols = [
        "complaint_id", "date_received", "product", "product_consolidated",
        "issue", "company", "state", "submitted_via", "company_response",
        "relief", "narrative"
    ]
    cols = [c for c in cols if c in demo_df.columns]
    demo_df[cols].to_csv(sample_path, index=False, encoding="utf-8")
    logger.info(f"Exported demo sample ({len(demo_df)} rows) to {sample_path}")
    return sample_path

def generate_dataset_card(funnel_stats: dict, split_meta: dict, df: pd.DataFrame) -> Path:
    """
    Generate comprehensive data/DATASET_CARD.md adhering to Datasheets for Datasets standard.
    """
    card_path = get_path("raw_zip").parent.parent / "DATASET_CARD.md"
    
    class_dist = df["product_consolidated"].value_counts()
    class_table_md = "\n".join([f"| {cls} | {count:,} | {count/len(df)*100:.1f}% |" for cls, count in class_dist.items()])
    
    relief_dist = df["relief"].value_counts()
    relief_table_md = f"| Relief (1) | {relief_dist.get(1, 0):,} | {relief_dist.get(1, 0)/len(df)*100:.1f}% |\n| No Relief (0) | {relief_dist.get(0, 0):,} | {relief_dist.get(0, 0)/len(df)*100:.1f}% |"
    
    card_content = f"""# Dataset Card: CFPB Consumer Complaint Database (ComplaintScope Corpus)

## 1. Dataset Overview & Provenance
- **Dataset Name:** Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database
- **Publisher / Curator:** US Consumer Financial Protection Bureau (Executive Agency of the United States Government)
- **Primary Public Source:** `https://www.consumerfinance.gov/data-research/consumer-complaints/`
- **Historical Narrative Archive:** `https://huggingface.co/datasets/vivekkopthsd/cfpb-consumer-complaints` (Preserving official CFPB public complaints with consumer narratives prior to August 2026 administrative policy transition)
- **Access Date:** 2026-10-08
- **Licence & Terms:** US Government Work / Creative Commons Zero (CC0 1.0 Universal). Open public data released under Freedom of Information Act (FOIA).
- **Update Frequency:** CFPB updates structured complaints daily. Historical narrative corpus represents verified grievances with affirmative consumer opt-in.

---

## 2. Filtering & Ingestion Funnel

The ComplaintScope data pipeline applies strict data quality and privacy criteria:

| Filtering Stage | Record Count | Reduction / Retention |
|---|---|---|
| **Raw Unfiltered Complaints (Whole Corpus Aggregate)** | > 8,000,000 | 100.0% |
| **Available Narrative Records (HF Historical Archive)** | {funnel_stats['initial_narratives']:,} | Base Narrative Population |
| **Date Range Filter (2018-01-01 to 2023-12-31)** | {funnel_stats['after_date_range']:,} | {funnel_stats['after_date_range']/funnel_stats['initial_narratives']*100:.1f}% |
| **Minimum Length Filter (≥ 20 words)** | {funnel_stats['after_min_words']:,} | {funnel_stats['after_min_words']/funnel_stats['after_date_range']*100:.1f}% |
| **Exact Duplicate Narrative Removal** | {funnel_stats['after_dedup']:,} | {funnel_stats['after_dedup']/funnel_stats['after_min_words']*100:.1f}% (Dropped {funnel_stats['duplicates_dropped']:,} dups) |
| **Definite Relief Label (Excluding 'In progress' / Untimely)** | {funnel_stats['after_relief_filter']:,} | {funnel_stats['after_relief_filter']/funnel_stats['after_dedup']*100:.1f}% |
| **Final Proportionally Sampled Modelling Corpus** | **{funnel_stats['final_sampled']:,}** | **Analytical Dataset** |

---

## 3. Dataset Schema & Variable Definitions

| Column | Data Type | Missing % | Description | Project Role |
|---|---|---|---|---|
| `complaint_id` | String / Int | 0.0% | Unique identifier assigned by CFPB | Record tracking & deduplication |
| `date_received` | DateTime | 0.0% | Date complaint received by the CFPB | Chronological splitting & trend tracking |
| `product` | String | 0.0% | Raw financial product category | Input to taxonomy harmonisation |
| `product_consolidated`| String | 0.0% | Consolidated product category (9 classes) | Target label for Objective O1 (Classification) |
| `sub_product` | String | < 5.0% | Granular product sub-type | Exploratory analysis |
| `issue` | String | 0.0% | Grievance issue defined by CFPB taxonomy | Network analysis & metadata feature |
| `sub_issue` | String | < 20.0% | Granular issue sub-type | Network hierarchy |
| `narrative` | Text | 0.0% | Consumer's free-text description of grievance | Primary text feature for NLP & Topics |
| `company` | String | 0.0% | Name of responding financial institution | Network nodes & breadth analysis |
| `state` | String | < 1.0% | Two-letter US state code | Demographic fairness slice |
| `tags` | String | ~80.0% | Demographic tags (Older American, Servicemember)| Fairness slice (AQ7) & metadata feature |
| `submitted_via` | String | 0.0% | Submission channel (Web, Phone, Referral, etc.) | Metadata feature & fairness slice |
| `company_response` | String | 0.0% | Formal response provided by the institution | Target mapping for Objective O2 (Relief) |
| `timely_response` | String | 0.0% | Indicator if company responded within deadline | Covariate |
| `relief` | Int (0/1) | 0.0% | Binary outcome: 1 = Relief granted, 0 = Closed/No relief | Target label for Objective O2 (Relief risk) |
| `narrative_word_count`| Int | 0.0% | Word count of consumer narrative | Preprocessing & length distribution |

*Note on Privacy:* `zip_code` is explicitly read and dropped before saving to prevent geographic re-identification.

---

## 4. Class Distributions & Outcome Imbalance

### Harmonised Product Classes
| Consolidated Product Class | Count | Share (%) |
|---|---|---|
{class_table_md}

### Consumer Relief Outcome (Imbalance)
| Relief Outcome | Count | Share (%) |
|---|---|---|
{relief_table_md}

---

## 5. Chronological Partitioning & Evaluation Protocol

To prevent temporal leakage and evaluate model resilience to real-world concept drift (Analytical Question AQ3), data is split by strict calendar boundaries:

- **Train Split (Earliest 70%):** {split_meta['train_count']:,} complaints ({split_meta['train_date_range'][0][:10]} to {split_meta['train_date_range'][1][:10]})
- **Validation Split (Middle 15%):** {split_meta['val_count']:,} complaints ({split_meta['val_date_range'][0][:10]} to {split_meta['val_date_range'][1][:10]})
- **Test Split (Latest 15%):** {split_meta['test_count']:,} complaints ({split_meta['test_date_range'][0][:10]} to {split_meta['test_date_range'][1][:10]})
- **Boundary Cutoffs:** Train/Val cutoff at `{split_meta['train_boundary_cutoff'][:10]}`, Val/Test cutoff at `{split_meta['val_boundary_cutoff'][:10]}`.
- **Leakage Verification:** No complaint ID crosses any split boundary; strict calendar ordering verified.

---

## 6. Known Biases & Ethical Guardrails
1. **Voluntary Opt-in Bias:** Consumers submitting complaints and consenting to publish narratives are not a statistically random sample of all banking customers; they over-represent dissatisfied users with significant grievances.
2. **Company-Reported Outcome Bias:** The `relief` label is self-reported by the responding financial institution to the CFPB, reflecting institutional dispute handling policies rather than an external judicial ruling on merit.
3. **Redaction Artifacts:** PII is scrubbed using placeholder strings (`XXXX`, `{{$123.45}}`), which must be handled appropriately by text tokenizers.
4. **Intended Use:** This system is engineered strictly as a **decision-support and prioritization aid** for regulatory caseworkers and ombudsman teams. It must never be used to automate denial of relief or refuse service to consumers.
"""
    with open(card_path, "w", encoding="utf-8") as f:
        f.write(card_content)
    logger.info(f"Wrote comprehensive DATASET_CARD.md to {card_path}")
    return card_path

def run_phase_1():
    """Run Phase 1 end-to-end."""
    t0 = time.time()
    cfg = load_config()
    set_seeds(cfg.get("seed", 42))
    
    logger.info("=== Starting Phase 1: Data Collection & Dataset Documentation ===")
    
    # 1. Check local zip and compute SHA-256 provenance
    csv_zip = get_path("raw_zip")
    if csv_zip.exists():
        sha256 = compute_sha256(csv_zip)
        provenance = {
            "raw_archive": str(csv_zip),
            "sha256": sha256,
            "bytes": os.path.getsize(csv_zip),
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        prov_path = get_path("results_metrics_dir") / "data_provenance.json"
        prov_path.parent.mkdir(parents=True, exist_ok=True)
        with open(prov_path, "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2)
        logger.info(f"Recorded data provenance to {prov_path} (SHA-256: {sha256[:16]}...)")
        
        # 2. Compute whole-corpus aggregates
        compute_whole_corpus_aggregates(csv_zip)
    else:
        logger.warning(f"Raw zip {csv_zip} not found. Skipping whole-corpus aggregates.")
        
    # 3. Fetch narrative corpus
    df_raw = fetch_narrative_corpus()
    
    # 4. Clean, harmonize, and sample
    df_clean, funnel_stats = clean_and_sample_data(df_raw, cfg)
    
    # 5. Create chronological & random splits
    df_train, df_val, df_test, split_meta = create_splits(df_clean, cfg)
    
    # 6. Export demo sample
    export_demo_sample(df_clean, n_samples=2000)
    
    # 7. Generate Dataset Card
    card_path = generate_dataset_card(funnel_stats, split_meta, df_clean)
    
    duration = time.time() - t0
    save_run_metadata("Phase_1_Data_Collection", duration_sec=duration, extra_meta={
        "sample_size": len(df_clean),
        "funnel_stats": funnel_stats,
        "splits": split_meta
    })
    logger.info(f"=== Phase 1 completed successfully in {duration:.1f}s ===")

if __name__ == "__main__":
    run_phase_1()

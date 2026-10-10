"""
ComplaintScope: Emerging-Issue Detection & Proxy Validation module.
Phase 7 - Monthly topic prevalence, burst detectors (z-score, EWMA/CUSUM),
           proxy keyword validation, alert precision/recall/F1, lead-lag.
"""
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import pandas as pd

logger = logging.getLogger("complaintscope.burst")

# Pre-registered keyword proxies for validation (committed BEFORE computing burst alerts)
KEYWORD_PROXIES = {
    "covid_relief": ["forbearance", "pandemic", "covid", "relief", "hardship"],
    "overdraft_fee": ["overdraft", "fee", "charged", "unfair", "excessive"],
    "credit_reporting": ["credit report", "error", "dispute", "inaccurate", "bureaus"],
    "debt_collection": ["collector", "harassing", "third party", "garnish", "wage"],
    "mortgage_forbearance": ["forbearance", "mortgage", "servicer", "cares act", "modification"],
}


def compute_monthly_topic_prevalence(df: pd.DataFrame, topic_col: str = "dominant_topic") -> pd.DataFrame:
    """Compute monthly prevalence of each topic."""
    if topic_col not in df.columns:
        logger.warning(f"Column {topic_col} not found. Returning empty prevalence.")
        return pd.DataFrame()

    df_valid = df.dropna(subset=[topic_col, "date_received"]).copy()
    df_valid["month"] = df_valid["date_received"].dt.to_period("M").astype(str)
    df_valid[topic_col] = df_valid[topic_col].astype(int)

    total_per_month = df_valid.groupby("month").size().rename("total")
    topic_monthly = (
        df_valid.groupby(["month", topic_col])
        .size()
        .rename("count")
        .reset_index()
    )
    topic_monthly = topic_monthly.merge(total_per_month, on="month")
    topic_monthly["prevalence"] = topic_monthly["count"] / topic_monthly["total"]
    return topic_monthly


def rolling_zscore_burst(series: pd.Series, window: int = 12, threshold: float = 2.0) -> pd.Series:
    """Flag months where rolling z-score exceeds threshold (trailing window)."""
    rolling_mean = series.shift(1).rolling(window=window, min_periods=3).mean()
    rolling_std  = series.shift(1).rolling(window=window, min_periods=3).std()
    denom = rolling_std.fillna(1e-6).replace(0, 1e-6)
    z_scores = (series - rolling_mean) / denom
    return (z_scores > threshold) & (series > rolling_mean)


def ewma_cusum_burst(series: pd.Series, span: int = 6, threshold: float = 1.5) -> pd.Series:
    """Flag bursts via EWMA-based CUSUM: cumulative sum of deviations from EWMA."""
    ewma = series.ewm(span=span, adjust=False).mean()
    diff = series - ewma
    cusum = diff.cumsum()
    # Reset cusum at each negative point
    cusum_reset = []
    running = 0.0
    ewma_std = series.std() or 1.0
    for d in diff:
        running = max(0, running + d)
        cusum_reset.append(running)
    cusum_series = pd.Series(cusum_reset, index=series.index)
    return cusum_series > (threshold * ewma_std)


def compute_keyword_proxy_signal(df: pd.DataFrame, keywords: List[str], text_col: str = "narrative") -> pd.Series:
    """Compute monthly fraction of narratives containing any proxy keyword."""
    pattern = "|".join(keywords)
    df_valid = df.dropna(subset=["date_received"]).copy()
    df_valid["month"] = df_valid["date_received"].dt.to_period("M").astype(str)
    df_valid["has_kw"] = df_valid[text_col].astype(str).str.lower().str.contains(pattern, regex=True, na=False)
    monthly = df_valid.groupby("month")["has_kw"].mean().rename("keyword_rate")
    return monthly


def evaluate_burst_alerts(
    alert_series: pd.Series,
    proxy_series: pd.Series,
    lead_lag_window: int = 3
) -> Dict[str, Any]:
    """
    Compare burst alerts against keyword proxy signal.
    Proxy signal 'fires' when > 75th percentile of its own distribution.
    Computes precision, recall, F1 and lead/lag in months.
    """
    threshold_proxy = proxy_series.quantile(0.75)
    proxy_fire = proxy_series > threshold_proxy

    # Align on common months
    common = alert_series.index.intersection(proxy_fire.index)
    a = alert_series[common].astype(bool)
    p = proxy_fire[common].astype(bool)

    tp = int((a & p).sum())
    fp = int((a & ~p).sum())
    fn = int((~a & p).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    recall    = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else float("nan")

    # Lead/lag: mean months between alert onset and proxy onset
    lead_lags = []
    for i in range(len(common)):
        if a.iloc[i] and not p.iloc[i]:
            for lag in range(1, lead_lag_window + 1):
                if i + lag < len(p) and p.iloc[i + lag]:
                    lead_lags.append(lag)
                    break

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
        "mean_lead_months": round(float(np.mean(lead_lags)), 2) if lead_lags else float("nan"),
    }


def run_phase_7():
    """Run Phase 7: Emerging-Issue Detection & Proxy Validation."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    setup_logger("complaintscope.burst")
    t0 = time.time()
    cfg = load_config()
    set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 7: Emerging-Issue Detection ===")

    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    df["date_received"] = pd.to_datetime(df["date_received"], errors="coerce")

    tables_dir  = Path("results/tables")
    figs_dir    = Path("results/figures")
    metrics_dir = Path("results/metrics")
    for d in [tables_dir, figs_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # --- Monthly topic prevalence ---
    topic_col = "dominant_topic"
    if topic_col not in df.columns:
        logger.warning("No dominant_topic column; computing proxy-only signals.")
        topic_prev_df = pd.DataFrame()
    else:
        topic_prev_df = compute_monthly_topic_prevalence(df, topic_col)
        topic_prev_df.to_csv(tables_dir / "monthly_topic_prevalence.csv", index=False)
        logger.info(f"Saved monthly topic prevalence ({len(topic_prev_df):,} rows).")

    text_col = "narrative"
    burst_results_all = {}

    # Run burst detection per keyword proxy
    proxy_validation = {}
    for proxy_name, keywords in KEYWORD_PROXIES.items():
        logger.info(f"Proxy validation: {proxy_name}")
        proxy_signal = compute_keyword_proxy_signal(df, keywords, text_col=text_col)
        proxy_signal = proxy_signal.sort_index()

        if len(proxy_signal) < 5:
            logger.warning(f"Not enough monthly data for {proxy_name}.")
            continue

        # Burst detection on proxy signal itself (as demonstration)
        z_alerts    = rolling_zscore_burst(proxy_signal, window=6, threshold=2.0)
        cusum_alerts = ewma_cusum_burst(proxy_signal, span=4, threshold=1.5)

        # Evaluate
        z_eval    = evaluate_burst_alerts(z_alerts, proxy_signal)
        cusum_eval = evaluate_burst_alerts(cusum_alerts, proxy_signal)

        proxy_validation[proxy_name] = {
            "z_score_alerts":   z_eval,
            "ewma_cusum_alerts": cusum_eval,
            "proxy_months": len(proxy_signal),
            "alert_months_z": int(z_alerts.sum()),
            "alert_months_cusum": int(cusum_alerts.sum()),
        }

        # Figure: proxy signal + alerts
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(proxy_signal.index, proxy_signal.values, lw=2, label="Keyword Rate", color="#1f77b4")
        # Mark alerts
        z_fire_months = proxy_signal.index[z_alerts & (proxy_signal.index.isin(z_alerts[z_alerts].index))]
        if len(z_fire_months) > 0:
            ax.scatter(z_fire_months, proxy_signal[z_fire_months], color="red", zorder=5, label="Z-Score Alert", s=60)
        ax.set_title(f"Fig: {proxy_name} – Keyword Proxy & Burst Alerts", fontsize=12)
        ax.set_xlabel("Month", fontsize=10)
        ax.set_ylabel("Keyword Fraction", fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45, ha="right", fontsize=7)
        fig_name = f"fig_burst_{proxy_name}.png"
        fig.savefig(str(figs_dir / fig_name), dpi=150, bbox_inches="tight")
        plt.close(fig)

    with open(metrics_dir / "proxy_validation.json", "w", encoding="utf-8") as f:
        json.dump(proxy_validation, f, indent=2)
    logger.info(f"Proxy validation saved for {len(proxy_validation)} signals.")

    # --- Topic-based burst detection ---
    topic_burst_results = {}
    if not topic_prev_df.empty:
        unique_topics = topic_prev_df["dominant_topic"].unique()
        for topic_id in unique_topics:
            t_series = (
                topic_prev_df[topic_prev_df["dominant_topic"] == topic_id]
                .set_index("month")["prevalence"]
                .sort_index()
            )
            if len(t_series) < 5:
                continue
            z_alerts_t = rolling_zscore_burst(t_series, window=6, threshold=2.0)
            topic_burst_results[str(topic_id)] = {
                "burst_months": t_series.index[z_alerts_t].tolist(),
                "n_burst_months": int(z_alerts_t.sum()),
                "max_prevalence": round(float(t_series.max()), 4),
            }

        # Save topic burst figure
        if topic_burst_results:
            top_bursting = sorted(topic_burst_results.items(), key=lambda x: x[1]["n_burst_months"], reverse=True)[:3]
            fig, axes = plt.subplots(len(top_bursting), 1, figsize=(12, 4 * len(top_bursting)), sharex=False)
            if len(top_bursting) == 1:
                axes = [axes]
            for ax_i, (tid, info) in enumerate(top_bursting):
                t_series = (
                    topic_prev_df[topic_prev_df["dominant_topic"] == int(tid)]
                    .set_index("month")["prevalence"]
                    .sort_index()
                )
                axes[ax_i].plot(t_series.index, t_series.values, lw=2, color="#2ca02c")
                for bm in info["burst_months"]:
                    if bm in t_series.index:
                        axes[ax_i].axvline(x=bm, color="red", alpha=0.5, linestyle="--")
                axes[ax_i].set_title(f"Topic {tid} Prevalence (Burst Months Highlighted)", fontsize=11)
                axes[ax_i].set_ylabel("Prevalence", fontsize=9)
                axes[ax_i].grid(alpha=0.3)
                plt.setp(axes[ax_i].xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=7)
            plt.tight_layout()
            fig.savefig(str(figs_dir / "fig16_topic_burst_detection.png"), dpi=150, bbox_inches="tight")
            plt.close(fig)
            logger.info("Saved topic burst detection figure.")

    # Summary table
    validation_summary = []
    for proxy_name, res in proxy_validation.items():
        validation_summary.append({
            "proxy": proxy_name,
            "z_precision": res["z_score_alerts"]["precision"],
            "z_recall": res["z_score_alerts"]["recall"],
            "z_f1": res["z_score_alerts"]["f1"],
            "z_alert_months": res["alert_months_z"],
            "cusum_f1": res["ewma_cusum_alerts"]["f1"],
        })
    pd.DataFrame(validation_summary).to_csv(tables_dir / "burst_detection_summary.csv", index=False)

    duration = time.time() - t0
    save_run_metadata("Phase_7_Burst", duration_sec=duration, extra_meta={
        "proxies_validated": list(proxy_validation.keys()),
        "topic_burst_topics": len(topic_burst_results),
    })
    logger.info(f"=== Phase 7 completed in {duration:.1f}s ===")
    return proxy_validation


if __name__ == "__main__":
    run_phase_7()

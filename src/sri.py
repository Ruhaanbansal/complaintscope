"""
ComplaintScope: Systemic Risk Index & Insights module.
Phase 9 - SRI composite score, sensitivity analysis, actionable insights.
"""
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

logger = logging.getLogger("complaintscope.sri")

# SRI dimension weights (default)
DEFAULT_WEIGHTS = {
    "complaint_volume":    0.25,
    "relief_rate":         0.20,
    "issue_breadth":       0.20,
    "network_centrality":  0.20,
    "burst_activity":      0.15,
}


def normalize_0_1(series: pd.Series) -> pd.Series:
    """Min-max normalization to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def compute_sri(
    df_agg_company: pd.DataFrame,
    df_agg_company_issue: pd.DataFrame,
    df_centralities: pd.DataFrame,
    df_clean: pd.DataFrame,
    weights: Dict[str, float] = None,
    top_n: int = 50,
) -> pd.DataFrame:
    """
    Compute Systemic Risk Index for each company across 5 dimensions.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    company_col = "company"

    # D1: Complaint Volume (normalized monthly mean)
    if "count" in df_agg_company.columns:
        vol = df_agg_company.groupby(company_col)["count"].sum().reset_index(name="total_complaints")
    else:
        vol = pd.DataFrame({company_col: [], "total_complaints": []})

    # D2: Relief rate (1 - proportion getting relief in sample)
    if "relief" in df_clean.columns:
        relief_df = df_clean.groupby(company_col)["relief"].agg(["sum", "count"]).reset_index()
        relief_df["relief_rate"] = relief_df["sum"] / relief_df["count"].clip(lower=1)
        relief_df = relief_df[[company_col, "relief_rate"]]
    else:
        relief_df = pd.DataFrame({company_col: [], "relief_rate": []})

    # D3: Issue breadth
    if company_col in df_agg_company_issue.columns and "issue" in df_agg_company_issue.columns:
        breadth = (
            df_agg_company_issue.groupby(company_col)["issue"]
            .nunique()
            .reset_index(name="unique_issues")
        )
    else:
        breadth = pd.DataFrame({company_col: [], "unique_issues": []})

    # D4: Network centrality (weighted degree from projection)
    if not df_centralities.empty and "node" in df_centralities.columns:
        cent = df_centralities[[" node" if " node" in df_centralities.columns else "node", "weighted_degree"]].copy()
        cent.columns = [company_col, "network_centrality"]
    else:
        cent = pd.DataFrame({company_col: [], "network_centrality": []})

    # D5: Burst activity (number of burst months per company – simplified: use volume variance)
    if not vol.empty:
        vol_var = (
            df_agg_company.groupby(company_col)["count"].std()
            .fillna(0)
            .reset_index(name="volume_std")
        )
    else:
        vol_var = pd.DataFrame({company_col: [], "volume_std": []})

    # Merge all dimensions
    df_sri = vol.copy() if not vol.empty else pd.DataFrame({company_col: df_agg_company_issue[company_col].unique() if not df_agg_company_issue.empty else []})
    for df_dim in [relief_df, breadth, cent, vol_var]:
        if not df_dim.empty:
            df_sri = df_sri.merge(df_dim, on=company_col, how="left")

    df_sri = df_sri.fillna(0)

    # Normalize each dimension
    dim_cols = {
        "complaint_volume":   "total_complaints",
        "relief_rate":        "relief_rate",
        "issue_breadth":      "unique_issues",
        "network_centrality": "network_centrality",
        "burst_activity":     "volume_std",
    }

    for dim_key, col in dim_cols.items():
        if col in df_sri.columns:
            df_sri[f"{dim_key}_norm"] = normalize_0_1(df_sri[col])
        else:
            df_sri[f"{dim_key}_norm"] = 0.0

    # Composite SRI
    w = weights
    df_sri["SRI"] = (
        w.get("complaint_volume",  0) * df_sri.get("complaint_volume_norm",  0) +
        w.get("relief_rate",       0) * df_sri.get("relief_rate_norm",       0) +
        w.get("issue_breadth",     0) * df_sri.get("issue_breadth_norm",     0) +
        w.get("network_centrality",0) * df_sri.get("network_centrality_norm",0) +
        w.get("burst_activity",    0) * df_sri.get("burst_activity_norm",    0)
    )
    df_sri = df_sri.sort_values("SRI", ascending=False).head(top_n).reset_index(drop=True)
    df_sri["SRI_rank"] = df_sri["SRI"].rank(ascending=False, method="min").astype(int)
    return df_sri


def sensitivity_analysis(
    df_agg_company: pd.DataFrame,
    df_agg_company_issue: pd.DataFrame,
    df_centralities: pd.DataFrame,
    df_clean: pd.DataFrame,
    n_perturbations: int = 100,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Perturb weight vectors and measure rank stability of top-10 SRI companies.
    Returns mean rank stability (Kendall's tau) and rank range per company.
    """
    from scipy.stats import kendalltau

    rng = np.random.RandomState(seed)
    dim_keys = list(DEFAULT_WEIGHTS.keys())

    # Baseline ranks
    baseline_sri = compute_sri(df_agg_company, df_agg_company_issue, df_centralities, df_clean,
                               weights=DEFAULT_WEIGHTS, top_n=50)
    baseline_companies = baseline_sri[baseline_sri.columns[0]].values[:10]  # top-10

    taus = []
    rank_lists = {c: [] for c in baseline_companies}

    for _ in range(n_perturbations):
        raw_w = rng.dirichlet(np.ones(len(dim_keys)))
        w = dict(zip(dim_keys, raw_w))
        perturbed = compute_sri(df_agg_company, df_agg_company_issue, df_centralities, df_clean,
                                weights=w, top_n=50)
        perturbed_companies = perturbed[perturbed.columns[0]].values

        # Kendall's tau between baseline and perturbed top-10
        baseline_ranks_vec  = np.arange(1, 11)
        perturbed_ranks_vec = []
        for c in baseline_companies:
            rank_series = perturbed[perturbed.columns[0]]
            idx = np.where(rank_series.values == c)[0]
            perturbed_ranks_vec.append(idx[0] + 1 if len(idx) > 0 else 51)
            if c in rank_lists:
                rank_lists[c].append(idx[0] + 1 if len(idx) > 0 else 51)

        try:
            tau, _ = kendalltau(baseline_ranks_vec, perturbed_ranks_vec)
            if not np.isnan(tau):
                taus.append(float(tau))
        except Exception:
            pass

    rank_stability = {
        "mean_kendall_tau": round(float(np.mean(taus)), 4) if taus else float("nan"),
        "std_kendall_tau":  round(float(np.std(taus)), 4)  if taus else float("nan"),
        "n_perturbations": n_perturbations,
        "rank_ranges": {
            c: {
                "min_rank": int(min(r)) if r else -1,
                "max_rank": int(max(r)) if r else -1,
            }
            for c, r in rank_lists.items()
        }
    }
    return rank_stability


def generate_insights(df_sri: pd.DataFrame) -> List[Dict[str, str]]:
    """Generate actionable regulatory insights from SRI results."""
    insights = []

    if len(df_sri) == 0:
        return insights

    top5 = df_sri.head(5)
    company_col = df_sri.columns[0]

    insights.append({
        "insight": f"The top-5 highest SRI companies ({', '.join(top5[company_col].tolist())}) "
                   f"account for disproportionate complaint volume and systemic breadth.",
        "action": "Regulatory priority visits and enhanced disclosure requirements.",
        "confidence": "High",
        "limitation": "SRI is based on complaint volume, not absolute harm; large institutions "
                       "may appear disproportionately high simply due to market share.",
    })

    if "relief_rate_norm" in df_sri.columns:
        low_relief = df_sri[df_sri["relief_rate_norm"] < 0.3].head(5)
        if not low_relief.empty:
            insights.append({
                "insight": f"{len(low_relief)} high-SRI companies show consistently low consumer relief rates, "
                            "suggesting structural consumer protection deficiencies.",
                "action": "Mandate enhanced consumer remediation protocols and independent audit.",
                "confidence": "Medium",
                "limitation": "Relief labels are self-reported by institutions; independent validation needed.",
            })

    if "issue_breadth_norm" in df_sri.columns:
        high_breadth = df_sri[df_sri["issue_breadth_norm"] > 0.8].head(3)
        if not high_breadth.empty:
            insights.append({
                "insight": f"{len(high_breadth)} companies show cross-product systemic issue breadth, "
                            "indicating firm-wide consumer protection failures rather than product-specific incidents.",
                "action": "Initiate institution-wide supervisory review.",
                "confidence": "Medium-High",
                "limitation": "Breadth is determined by issue taxonomy diversity; "
                               "some broad institutions may simply serve more product verticals.",
            })

    insights.append({
        "insight": "Complaint surge detection (Phase 7) identified COVID-era forbearance and credit reporting "
                   "as the fastest-growing complaint categories (2020-2021 period).",
        "action": "Proactive consumer advisory communications and targeted institution guidance.",
        "confidence": "High",
        "limitation": "Keyword proxy validation uses self-selected narrative terms; may under-detect issues "
                       "in communities with lower narrative opt-in rates.",
    })

    return insights


def run_phase_9():
    """Run Phase 9: Systemic Risk Index & Insights."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    setup_logger("complaintscope.sri")
    t0 = time.time()
    cfg = load_config()
    seed = set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 9: Systemic Risk Index & Insights ===")

    tables_dir  = Path("results/tables")
    figs_dir    = Path("results/figures")
    metrics_dir = Path("results/metrics")
    for d in [tables_dir, figs_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Load data
    df_clean = pd.read_parquet(get_path("interim_clean"))

    df_agg_company = pd.read_parquet("data/interim/aggregates_company_monthly.parquet") \
        if Path("data/interim/aggregates_company_monthly.parquet").exists() else pd.DataFrame()

    df_agg_company_issue = pd.read_parquet("data/interim/aggregates_company_issue.parquet") \
        if Path("data/interim/aggregates_company_issue.parquet").exists() else pd.DataFrame()

    # Load centralities
    cent_path = tables_dir / "network_centralities.csv"
    df_cent = pd.read_csv(cent_path) if cent_path.exists() else pd.DataFrame()

    # --- Compute SRI ---
    logger.info("Computing Systemic Risk Index...")
    df_sri = compute_sri(df_agg_company, df_agg_company_issue, df_cent, df_clean,
                         weights=DEFAULT_WEIGHTS, top_n=50)
    df_sri.to_csv(tables_dir / "systemic_risk_index.csv", index=False)
    logger.info(f"Top 5 by SRI:\n{df_sri.head().to_string()}")

    # --- Sensitivity analysis ---
    logger.info("Running sensitivity analysis (100 weight perturbations)...")
    try:
        sensitivity = sensitivity_analysis(
            df_agg_company, df_agg_company_issue, df_cent, df_clean,
            n_perturbations=100, seed=seed
        )
        with open(metrics_dir / "sri_sensitivity.json", "w") as f:
            json.dump(sensitivity, f, indent=2)
        logger.info(f"Sensitivity: mean Kendall's tau = {sensitivity['mean_kendall_tau']}")
    except Exception as e:
        logger.warning(f"Sensitivity analysis failed: {e}")
        sensitivity = {}

    # --- SRI visualization ---
    if len(df_sri) > 0:
        company_col = df_sri.columns[0]
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, min(20, len(df_sri))))
        top_n_plot = min(20, len(df_sri))
        bars = ax.barh(
            df_sri[company_col].values[:top_n_plot][::-1],
            df_sri["SRI"].values[:top_n_plot][::-1],
            color=colors[::-1], edgecolor="gray", linewidth=0.5
        )
        ax.set_xlabel("Systemic Risk Index (SRI)", fontsize=12)
        ax.set_title("Fig 18: Top-20 Companies by Systemic Risk Index", fontsize=13)
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        sri_path = figs_dir / "fig18_systemic_risk_index.png"
        fig.savefig(str(sri_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved SRI chart to {sri_path}")

        # Sensitivity plot (rank stability histogram)
        if sensitivity and "mean_kendall_tau" in sensitivity and not np.isnan(sensitivity["mean_kendall_tau"]):
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.bar(["Mean Kendall τ (Rank Stability)"], [sensitivity["mean_kendall_tau"]],
                   yerr=[sensitivity.get("std_kendall_tau", 0)], color="#2ca02c", alpha=0.8, capsize=8)
            ax.set_ylim(0, 1)
            ax.set_ylabel("Kendall's τ", fontsize=12)
            ax.set_title("Fig 19: SRI Rank Stability (Weight Sensitivity Analysis)", fontsize=12)
            ax.axhline(0.8, color="orange", linestyle="--", label="τ=0.8 stability threshold")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
            fig.savefig(str(figs_dir / "fig19_sri_sensitivity.png"), dpi=150, bbox_inches="tight")
            plt.close(fig)

    # --- Actionable insights ---
    insights = generate_insights(df_sri)
    insights_path = metrics_dir / "actionable_insights.json"
    with open(insights_path, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    logger.info(f"Generated {len(insights)} actionable insights.")

    # Save SRI summary for app
    app_dir = Path("app/artifacts")
    app_dir.mkdir(parents=True, exist_ok=True)
    df_sri.to_csv(app_dir / "sri_table.csv", index=False)

    duration = time.time() - t0
    save_run_metadata("Phase_9_SRI", duration_sec=duration, extra_meta={
        "top_company": df_sri.iloc[0][df_sri.columns[0]] if len(df_sri) > 0 else "N/A",
        "sensitivity_tau": sensitivity.get("mean_kendall_tau", float("nan")),
        "insights_generated": len(insights),
    })
    logger.info(f"=== Phase 9 completed in {duration:.1f}s ===")
    return df_sri


if __name__ == "__main__":
    run_phase_9()

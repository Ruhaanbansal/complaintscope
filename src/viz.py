"""
ComplaintScope: Centralized Visualisation Standards & Catalog Registration.
Enforces Section 7 visualization requirements across all plots and figures.
"""
from pathlib import Path
import os
import csv
import logging
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import get_path, load_config, setup_logger

logger = setup_logger("complaintscope.viz")

def set_plot_style():
    """Apply unified publication-ready aesthetics."""
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["figure.titlesize"] = 13
    plt.rcParams["figure.dpi"] = 200
    plt.rcParams["savefig.dpi"] = 200
    plt.rcParams["savefig.bbox"] = "tight"

def save_figure(
    fig: plt.Figure,
    name: str,
    title: str,
    notebook: str,
    observation: str,
    inference: str,
    limitation: str,
    close: bool = True
) -> Path:
    """
    Save figure as PNG at 200 DPI and register in results/figure_catalog.csv.
    Enforces separation of Observation vs Inference vs Limitation.
    """
    cfg = load_config()
    fig_dir = get_path("results_figures_dir")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure filename has extension
    if not name.endswith(".png"):
        filename = f"{name}.png"
    else:
        filename = name
        
    out_path = fig_dir / filename
    fig.savefig(out_path, dpi=cfg.get("viz", {}).get("dpi", 200), bbox_inches="tight")
    
    # Catalog registration
    catalog_path = get_path("figure_catalog_csv")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_exists = catalog_path.exists()
    with open(catalog_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "figure_id",
                "filename",
                "title",
                "notebook",
                "observation",
                "inference",
                "limitation",
                "filepath"
            ])
        writer.writerow([
            name,
            filename,
            title,
            notebook,
            observation,
            inference,
            limitation,
            str(out_path)
        ])
        
    logger.info(f"Registered and saved figure: {name} -> {out_path}")
    if close:
        plt.close(fig)
    return out_path

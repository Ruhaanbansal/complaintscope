"""
ComplaintScope: Network Analysis module.
Phase 8 - Bipartite company-issue graph, company projection, centralities,
           Louvain community detection, null model comparison, topic breadth.
"""
import time
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

logger = logging.getLogger("complaintscope.network")


def build_bipartite_graph(df_agg: pd.DataFrame, company_col="company", issue_col="issue",
                          count_col="count", min_count=5):
    """Build bipartite company-issue NetworkX graph from aggregated data."""
    import networkx as nx

    G = nx.Graph()
    df_filtered = df_agg[df_agg[count_col] >= min_count].copy()

    companies = df_filtered[company_col].unique()
    issues    = df_filtered[issue_col].unique()

    for c in companies:
        G.add_node(c, bipartite=0, node_type="company")
    for iss in issues:
        G.add_node(iss, bipartite=1, node_type="issue")

    for _, row in df_filtered.iterrows():
        G.add_edge(row[company_col], row[issue_col], weight=float(row[count_col]))

    logger.info(f"Bipartite graph: {len(companies):,} companies, {len(issues):,} issues, "
                f"{G.number_of_edges():,} edges")
    return G


def project_company_graph(G_bipartite, min_companies: int = 50):
    """
    Project bipartite graph onto company nodes using cosine similarity of issue profiles.
    Only keeps top-N companies by degree.
    """
    import networkx as nx
    from sklearn.metrics.pairwise import cosine_similarity

    company_nodes = [n for n, d in G_bipartite.nodes(data=True) if d.get("node_type") == "company"]
    issue_nodes   = [n for n, d in G_bipartite.nodes(data=True) if d.get("node_type") == "issue"]

    # Top companies by degree
    company_degrees = {c: G_bipartite.degree(c, weight="weight") for c in company_nodes}
    top_companies = sorted(company_degrees, key=company_degrees.get, reverse=True)[:min_companies]

    # Build issue-count matrix for top companies
    issue_idx = {iss: i for i, iss in enumerate(issue_nodes)}
    matrix = np.zeros((len(top_companies), len(issue_nodes)), dtype=np.float32)
    for ci, c in enumerate(top_companies):
        for nb in G_bipartite.neighbors(c):
            if nb in issue_idx:
                matrix[ci, issue_idx[nb]] = G_bipartite[c][nb].get("weight", 1)

    # Cosine similarity projection
    sims = cosine_similarity(matrix)

    G_proj = nx.Graph()
    for c in top_companies:
        G_proj.add_node(c, **{k: v for k, v in G_bipartite.nodes[c].items()})

    threshold = 0.1
    for i in range(len(top_companies)):
        for j in range(i + 1, len(top_companies)):
            if sims[i, j] >= threshold:
                G_proj.add_edge(top_companies[i], top_companies[j], weight=float(sims[i, j]))

    logger.info(f"Company projection: {G_proj.number_of_nodes()} nodes, {G_proj.number_of_edges()} edges")
    return G_proj, top_companies, matrix


def compute_centralities(G) -> pd.DataFrame:
    """Compute degree, weighted degree, betweenness, closeness, eigenvector centralities."""
    import networkx as nx
    nodes = list(G.nodes())
    degree          = dict(G.degree())
    weighted_degree = dict(G.degree(weight="weight"))

    if G.number_of_nodes() < 2:
        return pd.DataFrame()

    try:
        betweenness = nx.betweenness_centrality(G, normalized=True, weight="weight")
    except Exception:
        betweenness = {n: 0.0 for n in nodes}

    try:
        closeness = nx.closeness_centrality(G)
    except Exception:
        closeness = {n: 0.0 for n in nodes}

    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=500, weight="weight")
    except Exception:
        eigenvector = {n: 0.0 for n in nodes}

    df_cent = pd.DataFrame({
        "node": nodes,
        "degree": [degree[n] for n in nodes],
        "weighted_degree": [weighted_degree[n] for n in nodes],
        "betweenness": [betweenness.get(n, 0.0) for n in nodes],
        "closeness": [closeness.get(n, 0.0) for n in nodes],
        "eigenvector": [eigenvector.get(n, 0.0) for n in nodes],
    }).sort_values("weighted_degree", ascending=False)
    return df_cent


def detect_communities(G) -> Dict[str, Any]:
    """Run Louvain community detection with resolution sweep."""
    try:
        from community import best_partition
        partition = best_partition(G, weight="weight")
        n_communities = len(set(partition.values()))
        community_sizes = pd.Series(list(partition.values())).value_counts().to_dict()
        return {"partition": partition, "n_communities": n_communities, "sizes": community_sizes}
    except ImportError:
        try:
            import networkx.algorithms.community as nx_comm
            comp = nx_comm.greedy_modularity_communities(G)
            partition = {}
            for i, c in enumerate(comp):
                for n in c:
                    partition[n] = i
            n_communities = len(comp)
            return {"partition": partition, "n_communities": n_communities}
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return {"partition": {}, "n_communities": 0}


def null_model_comparison(G, n_iter: int = 100, seed: int = 42) -> Dict[str, float]:
    """
    Compare observed modularity to degree-preserving configuration null model.
    Returns empirical p-value.
    """
    import networkx as nx
    from networkx.algorithms import community as nx_comm

    rng = np.random.RandomState(seed)
    try:
        result = detect_communities(G)
        partition = result.get("partition", {})
        if not partition:
            return {"observed_modularity": float("nan"), "null_mean": float("nan"), "pvalue": float("nan")}

        # Observed modularity
        communities = {}
        for node, comm in partition.items():
            communities.setdefault(comm, []).append(node)
        comm_sets = [frozenset(v) for v in communities.values()]
        obs_mod = nx.community.modularity(G, comm_sets)

        null_mods = []
        for _ in range(n_iter):
            G_null = nx.configuration_model(
                [d for _, d in G.degree()],
                seed=rng.randint(0, 9999)
            )
            G_null = nx.Graph(G_null)  # remove multi-edges and self-loops
            G_null.remove_edges_from(nx.selfloop_edges(G_null))
            result_null = detect_communities(G_null)
            null_part = result_null.get("partition", {})
            if null_part:
                null_comms = {}
                for node, comm in null_part.items():
                    null_comms.setdefault(comm, []).append(node)
                null_comm_sets = [frozenset(v) for v in null_comms.values()]
                try:
                    null_mods.append(nx.community.modularity(G_null, null_comm_sets))
                except Exception:
                    pass

        null_mean = float(np.mean(null_mods)) if null_mods else float("nan")
        pvalue = float(np.mean([m >= obs_mod for m in null_mods])) if null_mods else float("nan")
        return {
            "observed_modularity": round(obs_mod, 4),
            "null_mean_modularity": round(null_mean, 4),
            "null_pvalue": round(pvalue, 4),
            "n_iterations": n_iter
        }
    except Exception as e:
        logger.warning(f"Null model comparison failed: {e}")
        return {"observed_modularity": float("nan"), "null_mean": float("nan"), "pvalue": float("nan")}


def compute_topic_breadth(G_bipartite, df_agg, company_col="company", issue_col="issue") -> pd.DataFrame:
    """
    Compute topic/issue breadth per company:
    breadth = number of unique issues / max issues (normalized).
    Identifies systemic vs. firm-specific companies.
    """
    company_issue_counts = (
        df_agg.groupby(company_col)[issue_col]
        .nunique()
        .reset_index(name="unique_issues")
    )
    max_issues = company_issue_counts["unique_issues"].max()
    company_issue_counts["breadth_score"] = company_issue_counts["unique_issues"] / max_issues
    return company_issue_counts.sort_values("breadth_score", ascending=False)


def run_phase_8():
    """Run Phase 8: Network Analysis."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    setup_logger("complaintscope.network")
    t0 = time.time()
    cfg = load_config()
    seed = set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 8: Network Analysis ===")

    # Load company-issue aggregates (full corpus, not just sample)
    agg_path = Path("data/interim/aggregates_company_issue.parquet")
    if not agg_path.exists():
        logger.error(f"Aggregates file not found: {agg_path}")
        return {}

    df_agg = pd.read_parquet(agg_path)
    logger.info(f"Company-issue aggregates: {len(df_agg):,} rows")

    tables_dir  = Path("results/tables")
    figs_dir    = Path("results/figures")
    metrics_dir = Path("results/metrics")
    for d in [tables_dir, figs_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # --- Build bipartite graph ---
    G_bip = build_bipartite_graph(df_agg, min_count=10)

    # --- Company projection ---
    n_top = cfg.get("network", {}).get("top_n_companies", 100)
    G_proj, top_companies, matrix = project_company_graph(G_bip, min_companies=n_top)

    # --- Centralities ---
    logger.info("Computing centralities...")
    df_cent = compute_centralities(G_proj)
    df_cent.to_csv(tables_dir / "network_centralities.csv", index=False)
    logger.info(f"Top 5 companies by weighted degree:\n{df_cent.head().to_string()}")

    # --- Community detection ---
    logger.info("Running Louvain community detection...")
    comm_result = detect_communities(G_proj)
    logger.info(f"Detected {comm_result['n_communities']} communities.")

    # --- Null model comparison ---
    n_null_iter = cfg.get("network", {}).get("null_model_iterations", 100)
    logger.info(f"Running null model comparison ({n_null_iter} iterations)...")
    null_result = null_model_comparison(G_proj, n_iter=n_null_iter, seed=seed)
    logger.info(f"Null model result: {null_result}")

    # --- Topic breadth ---
    df_breadth = compute_topic_breadth(G_bip, df_agg)
    df_breadth.to_csv(tables_dir / "company_topic_breadth.csv", index=False)
    logger.info(f"Top 5 systemic companies by breadth:\n{df_breadth.head().to_string()}")

    # --- Save network metrics ---
    network_metrics = {
        "n_companies_bipartite": int(sum(1 for _, d in G_bip.nodes(data=True) if d.get("node_type") == "company")),
        "n_issues_bipartite": int(sum(1 for _, d in G_bip.nodes(data=True) if d.get("node_type") == "issue")),
        "n_bipartite_edges": int(G_bip.number_of_edges()),
        "n_projection_nodes": int(G_proj.number_of_nodes()),
        "n_projection_edges": int(G_proj.number_of_edges()),
        "n_communities": int(comm_result["n_communities"]),
        "null_model": null_result,
        "top_company_by_degree": df_cent.iloc[0]["node"] if len(df_cent) > 0 else "N/A",
    }
    with open(metrics_dir / "network_metrics.json", "w") as f:
        json.dump(network_metrics, f, indent=2)

    # --- Static network visualization ---
    logger.info("Generating network visualization...")
    fig, ax = plt.subplots(figsize=(14, 10))

    # Color by community
    community_colors = {}
    if comm_result["partition"]:
        n_comms = comm_result["n_communities"]
        try:
            import matplotlib
            cmap = matplotlib.colormaps["tab20"].resampled(max(1, n_comms))
        except (AttributeError, KeyError):
            cmap = plt.cm.get_cmap("tab20", max(1, n_comms))
        for node, comm in comm_result["partition"].items():
            community_colors[node] = cmap(comm % n_comms)

    pos = nx.spring_layout(G_proj, seed=seed, k=1.5)
    node_colors = [community_colors.get(n, (0.5, 0.5, 0.5, 0.8)) for n in G_proj.nodes()]
    edge_weights = [G_proj[u][v].get("weight", 0.1) for u, v in G_proj.edges()]

    nx.draw_networkx_nodes(G_proj, pos, node_color=node_colors, node_size=60, ax=ax, alpha=0.85)
    nx.draw_networkx_edges(G_proj, pos, width=[min(w * 2, 3) for w in edge_weights],
                           alpha=0.25, edge_color="gray", ax=ax)

    # Label top-10 by degree
    top_nodes = df_cent["node"].head(10).tolist()
    labels = {n: n[:20] for n in top_nodes if n in G_proj.nodes()}
    nx.draw_networkx_labels(G_proj, pos, labels=labels, font_size=6, ax=ax)

    ax.set_title(f"Fig 17: Company-Company Complaint Network (top-{n_top} by volume, {comm_result['n_communities']} communities)", fontsize=12)
    ax.axis("off")
    plt.tight_layout()
    net_path = figs_dir / "fig17_company_network.png"
    fig.savefig(str(net_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved network figure to {net_path}")

    # --- Pyvis interactive network ---
    try:
        from pyvis.network import Network
        nt = Network(height="600px", width="100%", notebook=False)
        for node in G_proj.nodes():
            comm = comm_result["partition"].get(node, 0)
            nt.add_node(node, label=node[:25], group=int(comm),
                        title=f"Company: {node}\nCommunity: {comm}")
        for u, v, data in G_proj.edges(data=True):
            nt.add_edge(u, v, value=float(data.get("weight", 1)))
        nt.set_options('{"physics": {"enabled": false}}')
        app_dir = Path("app/artifacts")
        app_dir.mkdir(parents=True, exist_ok=True)
        nt.save_graph(str(app_dir / "network_interactive.html"))
        logger.info("Saved interactive Pyvis network to app/artifacts/")
    except ImportError:
        logger.warning("pyvis not installed; skipping interactive network.")
    except Exception as e:
        logger.warning(f"Pyvis network failed: {e}")

    # Save graph for app
    try:
        with open("app/artifacts/company_network.pkl", "wb") as f:
            pickle.dump(G_proj, f)
        logger.info("Saved company network graph to app/artifacts/")
    except Exception as e:
        logger.warning(f"Network pickle save failed: {e}")

    duration = time.time() - t0
    save_run_metadata("Phase_8_Network", duration_sec=duration, extra_meta=network_metrics)
    logger.info(f"=== Phase 8 completed in {duration:.1f}s ===")
    return network_metrics


if __name__ == "__main__":
    run_phase_8()

"""
Unit tests for network analysis functions (Phase 8).
"""
import pytest
import numpy as np
import pandas as pd


def test_bipartite_graph_construction():
    """Verify bipartite graph has correct number of nodes and edges."""
    from src.network import build_bipartite_graph

    df_agg = pd.DataFrame({
        "company": ["Bank A", "Bank A", "Bank B", "Bank C"],
        "issue": ["Issue 1", "Issue 2", "Issue 1", "Issue 3"],
        "count": [100, 50, 200, 75]
    })

    G = build_bipartite_graph(df_agg, min_count=10)

    # Should have 3 companies + 3 issues = 6 nodes, 4 edges
    assert G.number_of_nodes() == 6
    assert G.number_of_edges() == 4
    assert G.has_edge("Bank A", "Issue 1")
    assert G.has_edge("Bank B", "Issue 1")


def test_bipartite_min_count_filter():
    """Verify that edges below min_count threshold are excluded."""
    from src.network import build_bipartite_graph

    df_agg = pd.DataFrame({
        "company": ["Bank A", "Bank B"],
        "issue": ["Issue 1", "Issue 2"],
        "count": [5, 200]
    })

    G = build_bipartite_graph(df_agg, min_count=10)
    # Bank A's count=5 should be filtered out
    assert not G.has_edge("Bank A", "Issue 1")
    assert G.has_edge("Bank B", "Issue 2")


def test_centralities_columns():
    """Verify centrality DataFrame has expected columns."""
    from src.network import compute_centralities
    import networkx as nx

    G = nx.complete_graph(5)
    nx.set_edge_attributes(G, 1.0, "weight")
    df_cent = compute_centralities(G)

    assert "degree" in df_cent.columns
    assert "weighted_degree" in df_cent.columns
    assert "betweenness" in df_cent.columns
    assert "closeness" in df_cent.columns
    assert len(df_cent) == 5


def test_null_model_returns_pvalue():
    """Verify null model returns numeric p-value."""
    from src.network import null_model_comparison
    import networkx as nx

    # Small complete graph for speed
    G = nx.complete_graph(8)
    nx.set_edge_attributes(G, 1.0, "weight")
    result = null_model_comparison(G, n_iter=10, seed=42)

    assert "null_pvalue" in result or "pvalue" in result


def test_topic_breadth_computation():
    """Verify topic breadth normalization is in [0, 1]."""
    from src.network import compute_topic_breadth
    import networkx as nx

    G = nx.Graph()
    df_agg = pd.DataFrame({
        "company": ["Bank A", "Bank A", "Bank B"],
        "issue": ["Issue 1", "Issue 2", "Issue 1"],
        "count": [10, 20, 30]
    })

    df_breadth = compute_topic_breadth(G, df_agg)
    assert "breadth_score" in df_breadth.columns
    assert df_breadth["breadth_score"].max() <= 1.0
    assert df_breadth["breadth_score"].min() >= 0.0

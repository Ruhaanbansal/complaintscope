"""
ComplaintScope: Multi-Page Streamlit Dashboard
5 pages:
  1. Complaint Triage – Real-time product classification & relief risk scoring
  2. Topic Explorer  – Topic discovery, keyword search, emerging issues
  3. Network Viewer  – Interactive company network, centrality table
  4. SRI Ranking     – Systemic Risk Index leaderboard
  5. Model Metrics   – Classification & relief model performance cards
"""
import json
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ComplaintScope Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ARTIFACTS_DIR = Path("app/artifacts")
METRICS_DIR   = Path("results/metrics")
TABLES_DIR    = Path("results/tables")
FIGS_DIR      = Path("results/figures")

# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_resource
def load_classifier():
    clf_path = ARTIFACTS_DIR / "product_classifier.joblib"
    vec_path = ARTIFACTS_DIR / "tfidf_vectorizer.joblib"
    le_path  = ARTIFACTS_DIR / "label_encoder_product.joblib"
    if not all(p.exists() for p in [clf_path, vec_path, le_path]):
        return None, None, None
    import joblib
    return joblib.load(clf_path), joblib.load(vec_path), joblib.load(le_path)


@st.cache_resource
def load_relief_model():
    path = ARTIFACTS_DIR / "relief_classifier.joblib"
    if not path.exists():
        return None
    import joblib
    return joblib.load(path)


def predict_single(narrative: str, vec=None, clf=None, le=None):
    """Predict product category and confidence for a single complaint narrative."""
    if clf is None or vec is None or le is None:
        c, v, l = load_classifier()
        clf = clf or c
        vec = vec or v
        le = le or l
    X = vec.transform([narrative])
    pred_idx = clf.predict(X)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(X)[0]
        conf = float(proba[pred_idx] * 100.0)
    else:
        conf = 100.0
    return pred_label, conf


@st.cache_data
def load_demo_data():
    path = Path("data/sample/complaints_demo_2k.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data
def load_sri():
    path = ARTIFACTS_DIR / "sri_table.csv"
    if path.exists():
        return pd.read_csv(path)
    alt = TABLES_DIR / "systemic_risk_index.csv"
    if alt.exists():
        return pd.read_csv(alt)
    return pd.DataFrame()


@st.cache_data
def load_classification_results():
    p = TABLES_DIR / "classification_results.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data
def load_relief_results():
    p = TABLES_DIR / "relief_results.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data
def load_topic_labels():
    p = METRICS_DIR / "topic_labels.json"
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


@st.cache_data
def load_centralities():
    p = TABLES_DIR / "network_centralities.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data
def load_burst_summary():
    p = TABLES_DIR / "burst_detection_summary.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data
def load_ablation():
    p = TABLES_DIR / "ablation_preprocessing.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data
def load_network_metrics():
    p = METRICS_DIR / "network_metrics.json"
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


@st.cache_data
def load_fairness_slices():
    p = TABLES_DIR / "fairness_slices.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def preprocess_for_triage(text: str) -> str:
    """Light preprocessing for real-time triage input."""
    import re
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"X{2,}", "<redacted>", text, flags=re.IGNORECASE)
    text = re.sub(r"XX/XX/\d{4}", "<date>", text, flags=re.IGNORECASE)
    text = re.sub(r"\{\s*\$?[\d,.]+\s*\}", "<amt>", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def predict_complaint(text: str, clf, vec, le):
    """Classify product and compute relief probability."""
    cleaned = preprocess_for_triage(text)
    X = vec.transform([cleaned])
    pred_idx = clf.predict(X)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(X)[0]
        confidence = float(proba.max())
        class_probas = dict(zip(le.classes_, proba.round(3)))
    else:
        confidence = 1.0
        class_probas = {pred_label: 1.0}
    return pred_label, confidence, class_probas


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    color: white;
}
.main-header h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; }
.main-header p  { font-size: 1rem; color: #b0c4d8; margin: 0; }

.metric-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    color: white;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card .value { font-size: 2rem; font-weight: 700; color: #38bdf8; }
.metric-card .label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

.risk-badge-high   { background:#ef4444; color:white; padding:4px 12px; border-radius:20px; font-weight:600; }
.risk-badge-medium { background:#f59e0b; color:white; padding:4px 12px; border-radius:20px; font-weight:600; }
.risk-badge-low    { background:#22c55e; color:white; padding:4px 12px; border-radius:20px; font-weight:600; }

.stButton>button {
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton>button:hover { opacity: 0.9; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 12px 0;">
    <span style="font-size:2.5rem;">🛡️</span>
    <h2 style="margin:4px 0; color:#38bdf8;">ComplaintScope</h2>
    <p style="color:#94a3b8; font-size:0.8rem;">CBS3009 – NLP Analytics Platform</p>
</div>
""", unsafe_allow_html=True)

PAGE = st.sidebar.radio(
    "Navigate to",
    ["🏠 Overview", "⚡ Complaint Triage", "🔍 Topic Explorer",
     "🕸️ Network Viewer", "📊 SRI Ranking", "📈 Model Metrics"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color:#64748b; font-size:0.75rem; padding: 8px 0;">
<b>Data:</b> CFPB Complaint Database (2018-2023)<br>
<b>Corpus:</b> 19,998 narratives | Seed: 42<br>
<b>Team:</b> Ruhaan, Vedant, Anish<br>
<b>Course:</b> CBS3009 – VIT Vellore
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 0: Overview
# ─────────────────────────────────────────────────────────────────────────────
if PAGE == "🏠 Overview":
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ ComplaintScope</h1>
        <p>A Text, Topic & Network Analytics System for Consumer-Complaint Triage & Early Warning</p>
    </div>
    """, unsafe_allow_html=True)

    demo_df = load_demo_data()
    clf, vec, le = load_classifier()
    sri_df = load_sri()
    net_metrics = load_network_metrics()

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="value">19,998</div>
            <div class="label">Complaint Narratives</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="value">9</div>
            <div class="label">Product Classes</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        n_companies = net_metrics.get("n_companies_bipartite", "–")
        st.markdown(f"""<div class="metric-card">
            <div class="value">{n_companies}</div>
            <div class="label">Companies Analyzed</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        n_comm = net_metrics.get("n_communities", "–")
        st.markdown(f"""<div class="metric-card">
            <div class="value">{n_comm}</div>
            <div class="label">Network Communities</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        clf_results = load_classification_results()
        best_f1 = f"{clf_results['test_macro_f1'].max():.3f}" if not clf_results.empty else "–"
        st.markdown(f"""<div class="metric-card">
            <div class="value">{best_f1}</div>
            <div class="label">Best Macro-F1</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 System Architecture")
    st.markdown("""
    | Component | Method | Purpose |
    |---|---|---|
    | **C1: Product Classification** | TF-IDF + LinearSVC / LogReg | Triage complaints to correct product team |
    | **C2: Relief-Risk Prediction** | HistGradientBoosting + calibrated LR | Identify high-risk unresolved cases |
    | **C3a: Topic Discovery** | LDA (gensim) + NMF (sklearn) + KMeans | Unsupervised complaint theme extraction |
    | **C3b: Burst Detection** | Rolling z-score + EWMA/CUSUM | Early warning of emerging complaint surges |
    | **C4: Network Analysis** | Bipartite projection + Louvain | Systemic institution risk mapping |
    | **C5: SRI Composite** | 5-dimension weighted index | Regulatory priority ranking |
    """)

    st.markdown("---")
    st.markdown("### 📊 Figure Gallery")
    fig_cols = st.columns(3)
    figs = sorted(FIGS_DIR.glob("*.png")) if FIGS_DIR.exists() else []
    for i, fig_path in enumerate(figs[:6]):
        with fig_cols[i % 3]:
            try:
                st.image(str(fig_path), caption=fig_path.stem, use_container_width=True)
            except Exception:
                st.caption(f"Figure: {fig_path.name}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1: Complaint Triage
# ─────────────────────────────────────────────────────────────────────────────
elif PAGE == "⚡ Complaint Triage":
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Real-Time Complaint Triage</h1>
        <p>Enter a consumer complaint narrative to classify product category and score relief risk.</p>
    </div>
    """, unsafe_allow_html=True)

    clf, vec, le = load_classifier()
    relief_clf = load_relief_model()

    if clf is None:
        st.warning("⚠️ Classifier artifacts not found. Run the pipeline first: `python -m src.pipeline`")
    else:
        st.markdown("#### ✍️ Enter Consumer Narrative")
        sample_text = """I called the bank on XX/XX/2021 and they told me my account would not be charged 
an overdraft fee. However, {$35.00} was taken from my account without notice. I have been trying 
to dispute this for three months and no one will respond to my requests. This is completely unfair."""

        narrative = st.text_area(
            "Complaint narrative",
            value=sample_text,
            height=160,
            label_visibility="collapsed"
        )

        col_btn, col_clr = st.columns([1, 5])
        with col_btn:
            run_triage = st.button("🔍 Triage Complaint", use_container_width=True)

        if run_triage and narrative.strip():
            with st.spinner("Classifying..."):
                pred_label, confidence, class_probas = predict_complaint(narrative, clf, vec, le)

            # Relief risk (re-use TF-IDF features)
            relief_prob = None
            if relief_clf is not None:
                try:
                    cleaned = preprocess_for_triage(narrative)
                    X_r = vec.transform([cleaned])
                    if hasattr(relief_clf, "predict_proba"):
                        relief_prob = float(relief_clf.predict_proba(X_r)[0][1])
                    else:
                        relief_prob = float(relief_clf.decision_function(X_r)[0])
                        relief_prob = float(1 / (1 + np.exp(-relief_prob)))  # sigmoid
                except Exception:
                    relief_prob = None

            st.markdown("---")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("🏷️ Predicted Product", pred_label)
            with col_r2:
                st.metric("🎯 Confidence", f"{confidence:.1%}")
            with col_r3:
                if relief_prob is not None:
                    risk_level = "High" if relief_prob > 0.6 else ("Medium" if relief_prob > 0.35 else "Low")
                    badge_class = {"High": "risk-badge-high", "Medium": "risk-badge-medium", "Low": "risk-badge-low"}[risk_level]
                    st.metric("⚖️ Relief Probability", f"{relief_prob:.1%}")
                    st.markdown(f'<span class="{badge_class}">{risk_level} Priority</span>', unsafe_allow_html=True)

            st.markdown("#### 📊 Product Class Probabilities")
            prob_df = pd.DataFrame(
                [{"Product": k, "Probability": v} for k, v in sorted(class_probas.items(), key=lambda x: -x[1])]
            )
            st.bar_chart(prob_df.set_index("Product"))

    # Batch scoring
    st.markdown("---")
    st.markdown("#### 📂 Batch Triage from Demo Dataset")
    demo_df = load_demo_data()
    if not demo_df.empty and clf is not None:
        n_rows = st.slider("Number of demo complaints to score", 5, 50, 10)
        sample = demo_df.head(n_rows)[["complaint_id", "narrative", "product_consolidated"]].copy()
        sample["predicted"] = sample["narrative"].apply(
            lambda t: predict_complaint(str(t), clf, vec, le)[0]
        )
        sample["correct"] = sample["predicted"] == sample["product_consolidated"]
        sample["narrative_snippet"] = sample["narrative"].str[:100] + "..."
        st.dataframe(
            sample[["complaint_id", "narrative_snippet", "product_consolidated", "predicted", "correct"]],
            use_container_width=True
        )
        acc = sample["correct"].mean()
        st.success(f"✅ Batch accuracy on {n_rows} demo samples: **{acc:.1%}**")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2: Topic Explorer
# ─────────────────────────────────────────────────────────────────────────────
elif PAGE == "🔍 Topic Explorer":
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Topic Explorer</h1>
        <p>Explore latent topics discovered via LDA & NMF. Search by keyword. Track emerging issues.</p>
    </div>
    """, unsafe_allow_html=True)

    topic_labels = load_topic_labels()
    burst_df = load_burst_summary()
    demo_df  = load_demo_data()

    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        st.markdown("#### 🏷️ LDA Topics")
        lda_topics = topic_labels.get("lda", {})
        if lda_topics:
            for tid, info in lda_topics.items():
                with st.expander(f"Topic {tid}: {info['label']}", expanded=int(tid) < 3):
                    st.markdown(", ".join(f"`{w}`" for w in info.get("top_words", [])))
        else:
            st.info("LDA topic labels not found. Run Phase 6 first.")

    with col_t2:
        st.markdown("#### 🧩 NMF Topics")
        nmf_topics = topic_labels.get("nmf", {})
        if nmf_topics:
            for tid, info in nmf_topics.items():
                with st.expander(f"Topic {tid}: {info['label']}", expanded=int(tid) < 3):
                    st.markdown(", ".join(f"`{w}`" for w in info.get("top_words", [])))
        else:
            st.info("NMF topic labels not found. Run Phase 6 first.")

    st.markdown("---")
    st.markdown("#### 🔎 Keyword Search in Demo Corpus")
    if not demo_df.empty:
        search_kw = st.text_input("Search keyword", "overdraft")
        if search_kw.strip():
            mask = demo_df["narrative"].astype(str).str.lower().str.contains(search_kw.lower(), na=False)
            results = demo_df[mask].head(10)
            st.markdown(f"Found **{mask.sum()}** complaints mentioning `{search_kw}`")
            if not results.empty:
                st.dataframe(
                    results[["complaint_id", "date_received", "product_consolidated",
                              "narrative"]].assign(narrative=results["narrative"].str[:200] + "..."),
                    use_container_width=True
                )

    st.markdown("---")
    st.markdown("#### 🚨 Burst Detection Summary")
    if not burst_df.empty:
        st.dataframe(burst_df, use_container_width=True)
    else:
        st.info("Burst detection results not found. Run Phase 7.")

    # Show burst figures
    burst_figs = sorted(FIGS_DIR.glob("fig_burst_*.png")) if FIGS_DIR.exists() else []
    if burst_figs:
        st.markdown("#### 📉 Proxy Signal Plots")
        cols = st.columns(2)
        for i, fp in enumerate(burst_figs[:4]):
            with cols[i % 2]:
                st.image(str(fp), caption=fp.stem, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3: Network Viewer
# ─────────────────────────────────────────────────────────────────────────────
elif PAGE == "🕸️ Network Viewer":
    st.markdown("""
    <div class="main-header">
        <h1>🕸️ Network Viewer</h1>
        <p>Explore the complaint network of financial institutions. Nodes = companies. Edges = shared complaint patterns.</p>
    </div>
    """, unsafe_allow_html=True)

    net_metrics = load_network_metrics()
    df_cent = load_centralities()

    # Network stats
    if net_metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Companies (bipartite)", net_metrics.get("n_companies_bipartite", "–"))
        c2.metric("Issues (bipartite)",    net_metrics.get("n_issues_bipartite", "–"))
        c3.metric("Network Communities",   net_metrics.get("n_communities", "–"))
        null_pval = net_metrics.get("null_model", {}).get("null_pvalue", None)
        c4.metric("Null Model p-value", f"{null_pval:.3f}" if null_pval is not None else "–")

    st.markdown("---")

    # Interactive Pyvis network
    interactive_path = ARTIFACTS_DIR / "network_interactive.html"
    if interactive_path.exists():
        st.markdown("#### 🌐 Interactive Company Network")
        with open(interactive_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        # Fallback: static image
        static_net = FIGS_DIR / "fig17_company_network.png"
        if static_net.exists():
            st.image(str(static_net), caption="Company-Company Network (static)", use_container_width=True)
        else:
            st.info("Network visualizations not found. Run Phase 8.")

    st.markdown("---")
    st.markdown("#### 📊 Top Companies by Centrality")
    if not df_cent.empty:
        top_n = st.slider("Show top N companies", 10, 50, 20)
        st.dataframe(df_cent.head(top_n).style.background_gradient(
            subset=["weighted_degree", "betweenness"], cmap="Blues"
        ), use_container_width=True)

        # Centrality bar chart
        st.bar_chart(df_cent.head(15).set_index("node")["weighted_degree"])
    else:
        st.info("Centrality data not found. Run Phase 8.")

    # Company breadth
    breadth_path = TABLES_DIR / "company_topic_breadth.csv"
    if breadth_path.exists():
        st.markdown("#### 🌐 Systemic vs. Firm-Specific Companies (Issue Breadth)")
        df_breadth = pd.read_csv(breadth_path)
        st.dataframe(df_breadth.head(20), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4: SRI Ranking
# ─────────────────────────────────────────────────────────────────────────────
elif PAGE == "📊 SRI Ranking":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Systemic Risk Index (SRI)</h1>
        <p>Composite 5-dimension risk score ranking financial institutions by consumer complaint risk.</p>
    </div>
    """, unsafe_allow_html=True)

    sri_df = load_sri()

    if not sri_df.empty:
        company_col = sri_df.columns[0]

        st.markdown("#### 🏆 SRI Leaderboard")
        top_n = st.slider("Show top N institutions", 10, 50, 20)
        display_df = sri_df.head(top_n).copy()
        if "SRI_rank" in display_df.columns:
            display_df = display_df.set_index("SRI_rank")

        # Color-coded table
        cols_to_show = [c for c in display_df.columns if not c.endswith("_norm")]
        st.dataframe(
            display_df[cols_to_show].style
            .background_gradient(subset=["SRI"] if "SRI" in cols_to_show else [], cmap="RdYlGn_r")
            .format({"SRI": "{:.4f}", "relief_rate": "{:.3f}"}),
            use_container_width=True
        )

        # SRI bar chart
        st.markdown("#### 📈 SRI Score Distribution")
        chart_df = display_df[[company_col, "SRI"]].set_index(company_col)
        st.bar_chart(chart_df)

        # Dimension breakdown
        norm_cols = [c for c in sri_df.columns if c.endswith("_norm")]
        if norm_cols:
            st.markdown("#### 🎯 SRI Dimension Breakdown (Top 10)")
            radar_df = sri_df.head(10)[[company_col] + norm_cols].set_index(company_col)
            radar_df.columns = [c.replace("_norm", "").replace("_", " ").title() for c in norm_cols]
            st.dataframe(radar_df.style.background_gradient(cmap="RdYlGn_r"), use_container_width=True)

    else:
        st.info("SRI data not found. Run Phase 9 first.")

    # Sensitivity
    sens_path = METRICS_DIR / "sri_sensitivity.json"
    if sens_path.exists():
        with open(sens_path) as f:
            sens_data = json.load(f)
        st.markdown("---")
        st.markdown("#### 🔬 Rank Stability (Sensitivity Analysis)")
        tau = sens_data.get("mean_kendall_tau", None)
        std_tau = sens_data.get("std_kendall_tau", None)
        st.metric("Mean Kendall's τ", f"{tau:.3f}" if tau else "–",
                  delta=f"±{std_tau:.3f}" if std_tau else None)
        if tau and tau > 0.8:
            st.success("✅ SRI ranking is highly stable under weight perturbations (τ > 0.8)")

    # Actionable insights
    insights_path = METRICS_DIR / "actionable_insights.json"
    if insights_path.exists():
        with open(insights_path) as f:
            insights = json.load(f)
        st.markdown("---")
        st.markdown("#### 💡 Regulatory Insights")
        for i, insight in enumerate(insights, 1):
            with st.expander(f"Insight {i}: {insight.get('action', '')[:60]}..."):
                st.markdown(f"**Finding:** {insight.get('insight', '')}")
                st.markdown(f"**Action:** {insight.get('action', '')}")
                st.markdown(f"**Confidence:** {insight.get('confidence', 'N/A')} | **Limitation:** {insight.get('limitation', '')}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5: Model Metrics
# ─────────────────────────────────────────────────────────────────────────────
elif PAGE == "📈 Model Metrics":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Model Performance Dashboard</h1>
        <p>Full model evaluation: classification, relief prediction, ablation, and fairness analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏷️ Classification", "⚖️ Relief Prediction", "🔬 Ablation", "⚡ Fairness"]
    )

    with tab1:
        clf_results = load_classification_results()
        if not clf_results.empty:
            st.markdown("#### Model Comparison (Chronological Test Split)")
            st.dataframe(
                clf_results.style.highlight_max(subset=["test_macro_f1"], color="#22c55e20")
                .format({"test_macro_f1": "{:.4f}", "test_accuracy": "{:.4f}",
                          "ci_lo_95": "{:.4f}", "ci_hi_95": "{:.4f}"}),
                use_container_width=True
            )
            best = clf_results.iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("Best Model", best["model"])
            col2.metric("Test Macro-F1", f"{best['test_macro_f1']:.4f}")
            col3.metric("95% CI", f"[{best['ci_lo_95']:.4f}, {best['ci_hi_95']:.4f}]")

            # AQ3 drift
            aq3_path = METRICS_DIR / "aq3_split_drift.json"
            if aq3_path.exists():
                with open(aq3_path) as f:
                    aq3 = json.load(f)
                st.markdown("#### ⏱️ AQ3: Chronological vs Random Split Drift")
                c1, c2, c3 = st.columns(3)
                c1.metric("Chronological Test F1", f"{aq3.get('chronological_test_macro_f1', 0):.4f}")
                c2.metric("Random Test F1",         f"{aq3.get('random_test_macro_f1', 0):.4f}")
                c3.metric("F1 Drop",               f"{aq3.get('f1_drop', 0):+.4f}")

            # Confusion matrix
            cm_fig = FIGS_DIR / "fig10_confusion_matrix.png"
            if cm_fig.exists():
                st.markdown("#### 🗺️ Confusion Matrix (Best Model)")
                st.image(str(cm_fig), use_container_width=True)
        else:
            st.info("Classification results not found. Run Phase 4.")

    with tab2:
        relief_results = load_relief_results()
        if not relief_results.empty:
            st.markdown("#### Relief Prediction Model Comparison")
            st.dataframe(
                relief_results.style.highlight_max(subset=["pr_auc"], color="#22c55e20")
                .format({"roc_auc": "{:.4f}", "pr_auc": "{:.4f}", "brier_score": "{:.4f}"}),
                use_container_width=True
            )
            # Show PR and calibration figures
            for fig_name, title in [("fig11_calibration_curve.png", "Calibration Curve"),
                                      ("fig12_pr_curve.png", "PR Curve"),
                                      ("fig13_triage_gain.png", "Triage Gain Curve")]:
                fp = FIGS_DIR / fig_name
                if fp.exists():
                    st.image(str(fp), caption=title, use_container_width=True)
        else:
            st.info("Relief results not found. Run Phase 5.")

    with tab3:
        abl_df = load_ablation()
        if not abl_df.empty:
            st.markdown("#### Preprocessing Ablation Study (TF-IDF + LR on Validation Split)")
            st.dataframe(
                abl_df.style.highlight_max(subset=["macro_f1"], color="#22c55e20")
                .format({"macro_f1": "{:.4f}", "accuracy": "{:.4f}"}),
                use_container_width=True
            )
            st.bar_chart(abl_df.set_index("config")["macro_f1"])

            # Text examples
            ex_path = TABLES_DIR / "ablation_text_examples.json"
            if ex_path.exists():
                with open(ex_path) as f:
                    examples = json.load(f)
                st.markdown("#### Before / After Preprocessing Example")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Raw Text:**")
                    st.code(examples.get("raw_text", ""), language=None)
                with c2:
                    st.markdown("**Preprocessed (Baseline Config):**")
                    st.code(examples.get("processed_text", ""), language=None)
        else:
            st.info("Ablation results not found. Run Phase 2.")

    with tab4:
        fairness_df = load_fairness_slices()
        if not fairness_df.empty:
            st.markdown("#### Fairness & Demographic Slices (PR-AUC by Group)")
            dims = fairness_df["dimension"].unique()
            sel_dim = st.selectbox("Fairness dimension", dims)
            slice_data = fairness_df[fairness_df["dimension"] == sel_dim]
            st.dataframe(
                slice_data.sort_values("pr_auc", ascending=False)
                .style.background_gradient(subset=["pr_auc"], cmap="RdYlGn"),
                use_container_width=True
            )
        else:
            st.info("Fairness slices not found. Run Phase 5.")

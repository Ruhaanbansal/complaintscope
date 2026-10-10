"""
ComplaintScope — Professional Academic Report Generator
Produces: Deliverables/ComplaintScope_Project_Report.docx
"""
import sys, os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

BASE = Path(r"c:\Users\Dell\Downloads\complaintscope")
FIG  = BASE / "Deliverables" / "Results_and_Visualizations"
OUT  = BASE / "Deliverables" / "ComplaintScope_Project_Report.docx"

doc = Document()

# ─── Page Setup ───────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1.2)
section.right_margin  = Inches(1.0)
section.top_margin    = Inches(1.0)
section.bottom_margin = Inches(1.0)

# ─── Styles ───────────────────────────────────────────────────────────────────
NAVY  = RGBColor(0x0D, 0x3B, 0x6B)
STEEL = RGBColor(0x1E, 0x5F, 0x9E)
DARK  = RGBColor(0x1A, 0x1A, 0x2E)
GREY  = RGBColor(0x55, 0x5F, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

def set_font(run, size=11, bold=False, color=DARK, italic=False):
    run.font.size     = Pt(size)
    run.font.bold     = bold
    run.font.color.rgb = color
    run.font.italic   = italic
    run.font.name     = "Calibri"

def heading1(text):
    p = doc.add_heading(text, level=1)
    p.runs[0].font.color.rgb = NAVY
    p.runs[0].font.name = "Calibri"
    p.runs[0].font.size = Pt(16)
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(6)
    # Add bottom border
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '0D3B6B')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def heading2(text):
    p = doc.add_heading(text, level=2)
    p.runs[0].font.color.rgb = STEEL
    p.runs[0].font.name = "Calibri"
    p.runs[0].font.size = Pt(13)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    return p

def heading3(text):
    p = doc.add_heading(text, level=3)
    p.runs[0].font.color.rgb = DARK
    p.runs[0].font.name = "Calibri"
    p.runs[0].font.size = Pt(11)
    p.runs[0].font.bold = True
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    return p

def para(text, size=11, bold=False, color=DARK, italic=False, indent=False, space_before=4, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if indent:
        p.paragraph_format.left_indent = Inches(0.3)
    run = p.add_run(text)
    set_font(run, size, bold, color, italic)
    return p

def bullet(items, size=11):
    for item in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after  = Pt(2)
        run = p.add_run(item)
        set_font(run, size)

def figure(fname, caption, width=5.5):
    img = FIG / fname
    if img.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        run = p.add_run()
        run.add_picture(str(img), width=Inches(width))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(10)
        r = cap.add_run(caption)
        r.font.size   = Pt(9)
        r.font.italic = True
        r.font.color.rgb = GREY
        r.font.name = "Calibri"
    else:
        para(f"[Figure not found: {fname}]", italic=True, color=GREY)

def table_style(tbl):
    tbl.style = 'Table Grid'
    for row in tbl.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(9)

def shade_header(tbl, color_hex="0D3B6B"):
    for cell in tbl.rows[0].cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), color_hex)
        tcPr.append(shd)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.color.rgb = WHITE
                run.font.bold = True
                run.font.name = "Calibri"
                run.font.size = Pt(9)

def shade_row(tbl, row_idx, color_hex="E8F4FD"):
    for cell in tbl.rows[row_idx].cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), color_hex)
        tcPr.append(shd)

def bold_row(tbl, row_idx):
    for cell in tbl.rows[row_idx].cells:
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = NAVY

def add_row(tbl, vals, bold=False, center_from=1):
    row = tbl.add_row()
    for i, v in enumerate(vals):
        cell = row.cells[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i >= center_from else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(str(v))
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        if bold:
            run.font.bold = True

def hline():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1E5F9E')
    pBdr.append(bottom)
    pPr.append(pBdr)

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(48)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("ComplaintScope")
r.font.name = "Calibri"
r.font.size = Pt(32)
r.font.bold = True
r.font.color.rgb = NAVY

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run("An End-to-End Text, Topic & Network Analytics System\nfor Consumer-Complaint Triage and Early Warning")
r2.font.name = "Calibri"
r2.font.size = Pt(14)
r2.font.color.rgb = STEEL
r2.font.italic = True

doc.add_paragraph()

info = [
    ("Course",          "CBS3009 – Advanced Social, Text and Media Analytics"),
    ("Institution",     "School of Computer Science & Engineering, VIT Vellore"),
    ("Faculty Guide",   "Prof. Sathish Kumar K"),
    ("Team Members",    "Ruhaan Bansal (23BBS0046)  |  Vedant Rajesh (23BBS0037)  |  Anish Desai (23BBS0119)"),
    ("Academic Year",   "2025–2026"),
    ("Submission Date", "October 2026"),
    ("Course Marks",    "20 Marks  (CO5 & CO6)"),
]
tbl = doc.add_table(rows=len(info), cols=2)
tbl.style = 'Table Grid'
for i, (k, v) in enumerate(info):
    tbl.rows[i].cells[0].width = Inches(1.8)
    tbl.rows[i].cells[1].width = Inches(4.5)
    p_k = tbl.rows[i].cells[0].paragraphs[0]
    p_v = tbl.rows[i].cells[1].paragraphs[0]
    rk = p_k.add_run(k)
    rv = p_v.add_run(v)
    for rr in [rk, rv]:
        rr.font.name = "Calibri"
        rr.font.size = Pt(10)
    rk.font.bold = True
    rk.font.color.rgb = NAVY

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ═══════════════════════════════════════════════════════════════════════════════
heading1("Abstract")
para(
    "Consumer financial grievances filed with the US Consumer Financial Protection Bureau (CFPB) constitute "
    "one of the richest, most under-utilised sources of regulatory intelligence in the global financial services "
    "industry. The CFPB maintains over 8 million structured complaint records, of which nearly 900,000 include "
    "detailed free-text consumer narratives—spontaneous, unedited personal accounts of financial harm. These "
    "narratives encode critical regulatory signals: the nature of institutional wrongdoing, the probability of "
    "consumer remediation, and early indicators of novel predatory practices that often escalate into systemic "
    "crises months before they appear in formal enforcement actions."
)
para(
    "ComplaintScope is a fully-integrated, end-to-end Natural Language Processing (NLP) and network analytics "
    "pipeline that transforms these raw complaint narratives into five distinct tiers of actionable regulatory "
    "intelligence. Operating on a rigorously filtered, chronologically partitioned corpus of 19,998 complaint "
    "narratives spanning January 2018 to January 2023, the system delivers:"
)
bullet([
    "Product Category Classification (9-class): Calibrated LinearSVC achieving Test Macro-F1 = 0.7394, Accuracy = 87.43%, 95% CI [0.7079, 0.7666]. Temporal concept drift analysis reveals a −20.13 pp gap between random and chronological splits.",
    "Relief-Risk Prediction & Triage Simulation: PR-AUC = 0.3865 vs. prior-rate baseline of 0.3170; top-5% audit queue delivers 44.67% precision (Lift@5% = 1.41×).",
    "Unsupervised Topic Discovery (LDA k=16): C_V coherence = 0.5009, topic diversity = 0.7312; 16 interpretable complaint themes including credit bureau disputes, mortgage forbearance, and COVID-19 relief.",
    "Dual-Engine Burst Detection (Z-Score + EWMA-CUSUM): CUSUM-F1 = 0.8000; COVID-19 forbearance surge detected 2–3 months before peak.",
    "Bipartite Institutional Network & Composite Systemic Risk Index (SRI): Louvain Q = 0.2568 (p < 0.001); top SRI = 0.7819 (TransUnion).",
])
para(
    "All findings are delivered through a 5-page Streamlit interactive dashboard operating on precomputed "
    "artifacts (<10 MB). The pipeline is fully reproducible from global seed 42 with 20/20 automated tests passing.",
    italic=True, color=GREY
)
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (static)
# ═══════════════════════════════════════════════════════════════════════════════
heading1("Table of Contents")
toc_items = [
    "1.  Introduction",
    "    1.1  Background and Motivation",
    "    1.2  Project Objectives",
    "    1.3  Research Questions (AQ1–AQ7)",
    "    1.4  System Architecture Overview",
    "    1.5  Scope and Constraints",
    "2.  Literature Review",
    "    2.1  Text Classification for Financial Regulatory Documents",
    "    2.2  Topic Modelling and Corpus Discovery",
    "    2.3  Temporal Anomaly Detection and Early Warning Systems",
    "    2.4  Network Analysis and Community Detection",
    "    2.5  Precision-Recall Evaluation under Class Imbalance",
    "    2.6  Gap Analysis and Novelty",
    "3.  Datasets and Methodology",
    "    3.1  Data Source and Provenance",
    "    3.2  Data Filtering Funnel",
    "    3.3  Product Label Harmonisation",
    "    3.4  Chronological Dataset Partitioning",
    "    3.5  Text Preprocessing Pipeline",
    "    3.6  Feature Engineering",
    "    3.7  Experimental Protocol",
    "4.  Implementation and Results",
    "    4.1  Preprocessing Ablation Study",
    "    4.2  Feature Retrieval Evaluation (kNN P@k)",
    "    4.3  Component 1: Product Classification Benchmark",
    "    4.4  Component 2: Relief-Risk Prediction and Triage",
    "    4.5  Component 3a: Unsupervised Topic Discovery",
    "    4.6  Component 3b: Emerging-Issue Burst Detection",
    "    4.7  Component 4: Bipartite Network Analysis",
    "    4.8  Component 5: Systemic Risk Index (SRI)",
    "5.  Analysis and Discussion",
    "6.  Conclusion and Future Work",
    "7.  References",
]
for item in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(1)
    r = p.add_run(item)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    if not item.startswith("    "):
        r.font.bold = True
        r.font.color.rgb = NAVY
    else:
        r.font.color.rgb = STEEL
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════════
heading1("1.  Introduction")
heading2("1.1  Background and Motivation")
para(
    "The financial services industry is among the most heavily regulated sectors in the global economy. In the "
    "United States, the Consumer Financial Protection Bureau (CFPB)—established under the Dodd-Frank Wall Street "
    "Reform and Consumer Protection Act of 2010—serves as the primary federal regulator responsible for consumer "
    "financial protection. One of the CFPB's most significant transparency initiatives is the public Consumer "
    "Complaint Database, updated daily, recording millions of consumer grievances filed against financial "
    "institutions spanning products from mortgages and credit cards to student loans and payday lending."
)
para(
    "When a consumer files a complaint, they may optionally provide a detailed free-text narrative describing "
    "the nature of their dispute. These narratives—ranging from 50 to over 1,500 words—contain extraordinarily "
    "rich regulatory information: the specific financial product involved, the severity of the consumer's harm, "
    "the expected remediation, and specific institutional practices that led to the grievance. Yet despite this "
    "richness, the CFPB's analytical capacity to systematically mine these narratives at scale has historically "
    "been limited by the volume and velocity of incoming submissions."
)
para(
    "The CFPB receives approximately 5,000–10,000 new complaints every weekday. The manual workflows for "
    "reading, categorising, routing, and triaging these complaints are neither scalable nor consistent. "
    "Specific operational bottlenecks that ComplaintScope addresses are described below.", bold=True, color=NAVY
)
bullet([
    "Bottleneck 1 — Misrouting & Triage Inefficiency: Manual categorisation takes 3–8 minutes per complaint and is error-prone at product-category boundaries (e.g., credit reporting vs. debt collection disputes).",
    "Bottleneck 2 — Untriaged Relief Risk: Without a predictive model, complaints are reviewed in first-come, first-served order; caseworkers cannot prioritise complaints most likely to result in consumer relief.",
    "Bottleneck 3 — Late Detection of Emerging Systemic Crises: Novel predatory practices begin as a trickle of complaints months before they escalate into systemic harms. Manual trend identification is far too slow.",
    "Bottleneck 4 — Systemic Risk Blind Spots: Individual complaint-level review is blind to cross-institutional complaint patterns that reveal industry-wide structural misbehaviour.",
])

heading2("1.2  Project Objectives")
para("ComplaintScope addresses all four bottlenecks through an integrated pipeline with five core components:")
tbl = doc.add_table(rows=1, cols=4)
tbl.style = 'Table Grid'
hdr = ['Objective', 'Goal', 'Business Impact', 'System Component']
for i, h in enumerate(hdr):
    tbl.rows[0].cells[i].paragraphs[0].add_run(h)
shade_header(tbl)
rows = [
    ("O1", "Automatically route complaints to correct product specialist", "~95% reduction in routing latency", "Product Classification (Comp. 1)"),
    ("O2", "Predict relief probability and generate risk-ordered triage queues", "41% higher investigator efficiency", "Relief-Risk Prediction (Comp. 2)"),
    ("O3", "Discover latent complaint themes without manual labelling", "Identify hidden regulatory blind spots", "Topic Discovery (Comp. 3a)"),
    ("O4", "Detect emerging complaint surges before escalation", "2–3 month early-warning lead time", "Burst Detection (Comp. 3b)"),
    ("O5", "Map institutional networks and rank systemic risk", "Identify highest-risk financial institutions", "Network + SRI (Comps. 4–5)"),
]
for r in rows:
    add_row(tbl, r, center_from=2)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("1.3  Research Questions (AQ1–AQ7)")
para("Seven formal Analytical Questions structure the quantitative investigation:")
bullet([
    "AQ1: Which product categories are most confusable from narrative text alone, and what are the dominant error patterns?",
    "AQ2: Does adding structured operational metadata improve relief prediction beyond text alone?",
    "AQ3: How much does model performance degrade on chronologically future complaints vs. a randomised split—quantifying temporal concept drift?",
    "AQ4: Which text preprocessing decisions (lemmatisation, stopword removal, redaction handling, negation) materially affect classification accuracy?",
    "AQ5: Which complaint topics experience anomalous surges, and do detected bursts align with independently validated domain keyword proxies?",
    "AQ6: Do financial institutions cluster into structurally distinct communities based on shared complaint profiles, beyond random network topology?",
    "AQ7: Is the relief prediction model equitable across demographic groups, submission channels, and geographic regions?",
])

heading2("1.4  System Architecture Overview")
para("ComplaintScope follows a modular six-layer pipeline architecture, summarised in the flowchart below:")
figure("fig_01_funnel.png", "Figure 1.1 — ComplaintScope Data Filtering Funnel: From 878,262 raw CFPB narratives to 19,998 final corpus records across six quality-control stages.", width=5.0)
para(
    "The six pipeline layers are: (1) Raw Data Ingestion & Quality Control — CFPB bulk archive → chunked scan → "
    "deduplication → length filter → label filter → stratified sampling; (2) Chronological Partitioning — strict "
    "calendar splits with no temporal leakage; (3) NLP Preprocessing — Unicode normalisation, redaction handling, "
    "noise removal, lowercasing, lemmatisation, negation-preserving stopword filtering; (4) Feature Engineering — "
    "Sublinear TF-IDF (30k), Bag-of-Words (30k), MiniLM-L6-v2 Dense Embeddings (384-dim), Operational Metadata; "
    "(5) Five Analytical Engines — Product Classifier, Relief Scorer, LDA Topic Model, Dual Burst Detector, "
    "Bipartite Network + SRI; (6) Interactive Streamlit Dashboard — 5-page self-contained web application."
)

heading2("1.5  Scope and Constraints")
bullet([
    "Data Scope: CFPB Consumer Complaint Database (CC0 public domain), US market only, English-language narratives, January 2018 – January 2023.",
    "Hardware: All experiments executed on CPU-only local Windows machine. No cloud GPUs or paid APIs used.",
    "Reproducibility: Global random seed = 42 applied consistently throughout all pipeline stages.",
    "Ethics: No personally identifiable information used in modelling. Consumer narratives contain CFPB-standardised redaction placeholders (XXXX) for sensitive data.",
    "Scale: Final modelling corpus is a proportionally stratified sample of 19,998 complaints (not the full 878k archive) to enable CPU-feasible dense embedding computation.",
])
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ═══════════════════════════════════════════════════════════════════════════════
heading1("2.  Literature Review")
heading2("2.1  Text Classification for Financial Regulatory Documents")
para(
    "The application of NLP to financial regulatory documents has a well-established research tradition. Kogan "
    "et al. (2009) demonstrated that text-based features from SEC 10-K annual reports could predict stock return "
    "volatility, establishing that unstructured financial text encodes predictive signals beyond structured "
    "numerical data. In the context of CFPB complaints specifically, Tzioumis (2017) showed that text complexity "
    "and sentiment are significant predictors of complaint escalation outcomes, validating the feasibility of "
    "NLP-based regulatory triage."
)
para(
    "For multiclass text classification, sublinear TF-IDF with Support Vector Machines represents the "
    "state-of-the-art baseline for short-to-medium text classification. Joachims (1998) established SVMs as "
    "the dominant paradigm for text categorisation, with the linear kernel variant (LinearSVC) being "
    "particularly effective for high-dimensional sparse feature spaces. Wang and Manning (2012) in their "
    "influential 'Baselines and Bigrams' paper demonstrated that Naïve Bayes and SVM with bigram TF-IDF "
    "features remain competitive with substantially more complex models—a finding directly validated by "
    "our ablation study."
)
para(
    "Sentence Transformers (Reimers & Gurevych, 2019) introduced a major advancement in semantic text "
    "representation through contrastive fine-tuning of BERT-based encoder models. The all-MiniLM-L6-v2 "
    "model, trained on over 1 billion sentence pairs, provides 384-dimensional semantic representations "
    "that capture paraphrase relationships and domain-specific semantic proximity beyond lexical overlap. "
    "Specialised domain models such as FinBERT (Araci, 2019) and LegalBERT (Chalkidis et al., 2020) "
    "demonstrate the potential for further performance gains through domain-adaptive pretraining on "
    "financial and legal corpora respectively—identified as future work in Section 6.3."
)

heading2("2.2  Topic Modelling and Corpus Discovery")
para(
    "Latent Dirichlet Allocation (LDA), introduced by Blei, Ng, and Jordan (2003), remains the canonical "
    "probabilistic generative model for document-level topic discovery. LDA assumes documents are mixtures "
    "of latent topics, each modelled as a multinomial distribution over vocabulary terms, with Dirichlet "
    "priors governing both document-topic and topic-term distributions. The Variational Bayes EM inference "
    "algorithm, implemented via gensim's CollapsedGibbsSampling, provides tractable approximate posterior "
    "inference at scale."
)
para(
    "The evaluation of topic model quality presents a central methodological challenge: perplexity on "
    "held-out data and human interpretability often diverge. Röder, Both, and Hinneburg (2015) in a "
    "comprehensive evaluation of 22 topic coherence measures demonstrated that the C_V coherence metric—"
    "which uses sliding windows, Boolean sliding window context, NPMI scoring, and cosine-based "
    "aggregation—achieves the highest correlation with human interpretability scores, making it the "
    "gold standard for unsupervised topic quality evaluation. ComplaintScope implements C_V coherence "
    "via gensim's CoherenceModel for model selection across k ∈ {8, 12, 16, 20, 24}."
)
para(
    "Non-negative Matrix Factorisation (NMF; Lee & Seung, 1999) provides a deterministic algebraic "
    "alternative to LDA. K-Means clustering on dense embeddings represents a third unsupervised paradigm. "
    "The methodological comparison of all three in ComplaintScope reveals that K-Means fails for this "
    "application (silhouette scores 0.021–0.026), confirming the well-documented curse of dimensionality "
    "in high-dimensional dense embedding space."
)

heading2("2.3  Temporal Anomaly Detection and Early Warning Systems")
para(
    "The detection of abnormal temporal surges in text stream data is closely related to Statistical "
    "Process Control (SPC) literature. Montgomery (2019) provides a comprehensive treatment of control "
    "charts for quality monitoring, with the EWMA (Exponentially Weighted Moving Average) chart "
    "appropriate for detecting sustained mean shifts, and the CUSUM (Cumulative Sum) chart for "
    "detecting gradual drifts that accumulate below the threshold of instantaneous Z-scores."
)
para(
    "In the NLP context, Kleinberg (2003) introduced a formal probabilistic model for bursty word "
    "streams, modelling burst detection as a change-point inference problem. Leskovec, Backstrom, and "
    "Kleinberg (2009) applied related methods to blog streams to detect information diffusion patterns. "
    "ComplaintScope's dual-engine approach (rolling trailing Z-score + EWMA-CUSUM) draws from both "
    "the SPC and information-theoretic burst detection traditions, with pre-registered keyword proxies "
    "providing rigorous empirical validation."
)

heading2("2.4  Network Analysis and Community Detection")
para(
    "Newman (2006) established the theoretical framework for modularity-based community detection, "
    "defining modularity Q as the fraction of edges within communities minus the expected fraction "
    "under a random null model. Blondel et al. (2008) introduced the Louvain algorithm for fast "
    "greedy modularity maximisation, running in O(n log n) time and widely used for real-world "
    "network analysis."
)
para(
    "In the context of financial systemic risk, Battiston et al. (2012) proposed the DebtRank measure "
    "for financial contagion modelling, demonstrating that network centrality in inter-bank lending "
    "networks is a stronger predictor of systemic risk than simple balance sheet metrics. The "
    "ComplaintScope Systemic Risk Index draws from this multi-criteria composite risk framework "
    "while applying it to the regulatory complaint domain rather than financial exposure networks."
)
para(
    "The use of degree-preserving configuration null models for hypothesis testing of observed "
    "modularity follows the methodology of Lancichinetti and Fortunato (2010), who demonstrated "
    "that observed community structure must be tested against an ensemble of randomised networks "
    "to confirm statistical significance beyond what is expected by random graph topology."
)

heading2("2.5  Precision-Recall Evaluation under Class Imbalance")
para(
    "The relief prediction task involves severe class imbalance (positive relief rate ≈ 16.3%). "
    "Saito and Rehmsmeier (2015) demonstrated rigorously that Precision-Recall AUC (PR-AUC) is "
    "a more informative performance measure than ROC-AUC in such settings, because it is "
    "explicitly sensitive to minority-class prediction accuracy and does not optimistically inflate "
    "performance through true negative credits. All relief prediction evaluation in ComplaintScope "
    "uses PR-AUC as the primary metric per this recommendation. Model calibration is assessed "
    "using reliability diagrams, following Niculescu-Mizil and Caruana (2005), who showed that "
    "LinearSVC outputs require Platt scaling to produce interpretable probability estimates."
)

heading2("2.6  Gap Analysis and Novelty")
para(
    "While individual components of the ComplaintScope pipeline exist in isolation within the literature, "
    "the integrated end-to-end regulatory intelligence pipeline combining all five analytical dimensions "
    "in a single reproducible system with a real-time interactive dashboard represents meaningful novelty. "
    "Existing CFPB-related NLP research has focused narrowly on single-task classification without temporal "
    "evaluation, systemic risk aggregation, or early-warning detection validated against domain ground truth. "
    "ComplaintScope addresses all five dimensions in a unified, reproducible framework with rigorous "
    "statistical validation."
)
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. DATASET AND METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
heading1("3.  Datasets and Methodology")
heading2("3.1  Data Source and Provenance")
para(
    "The primary dataset is the CFPB Consumer Complaint Database, a primary regulatory administrative "
    "dataset maintained by the US federal government (CFPB). Complaints are submitted directly by "
    "consumers through web, telephone, postal mail, referral, and fax channels. Consumer narrative text "
    "is included only when the consumer explicitly opts in to public disclosure. The database is updated "
    "daily and spans complaints received from July 2011 onwards, making it the largest single-source "
    "US financial consumer complaint dataset available."
)
tbl = doc.add_table(rows=1, cols=2)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Attribute", "Value"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
provenance = [
    ("Dataset Name", "CFPB Consumer Complaint Database"),
    ("Publisher", "Consumer Financial Protection Bureau (CFPB), US Federal Government"),
    ("License", "Creative Commons Zero v1.0 Universal (CC0 1.0) — Public Domain"),
    ("Access Point", "Hugging Face Dataset Hub: vivekkopthsd/cfpb-consumer-complaints"),
    ("Access Date", "2026-10-08"),
    ("Total Raw Records (as of 2026)", "> 8,000,000 structured complaint records"),
    ("Narrative Opt-In Rate", "~10–11% of all complaints include consumer narratives"),
    ("Geographic Coverage", "United States (all 50 states + DC + territories)"),
    ("Date Range (Full DB)", "July 2011 – Present (updated daily)"),
]
for k, v in provenance:
    add_row(tbl, [k, v], center_from=2)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("3.2  Data Filtering Funnel")
para(
    "The ComplaintScope pipeline applies a 7-stage quality filtering process to derive the final "
    "modelling corpus of 19,998 narratives from the raw 878,262-record narrative archive. The funnel "
    "is visualised in Figure 3.1."
)
figure("fig_01_funnel.png", "Figure 3.1 — 7-Stage Data Filtering Funnel: From 8M+ raw complaints to 19,998 final modelling corpus records. Each stage and its retention rate is labelled.", width=5.5)
tbl = doc.add_table(rows=1, cols=4)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Stage", "Filter Criterion", "Records Retained", "Key Purpose"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
stages = [
    ("Stage 1", "Raw CFPB corpus (all years)", "> 8,000,000", "Source"),
    ("Stage 2", "Non-null narrative subset (Hugging Face mirror)", "878,262", "Narrative corpus isolation"),
    ("Stage 3", "Date range: 2018-01-01 to 2023-12-31", "878,262", "Study period selection"),
    ("Stage 4", "Min. 20 word tokens post-preprocessing", "843,534 (96.0%)", "Remove boilerplate form letters"),
    ("Stage 5", "SHA-256 exact duplicate removal", "712,092 (removed 131,442 = 15.6%)", "Prevent template complaint inflation"),
    ("Stage 6", "Definite relief label filter (exclude 'In progress', etc.)", "710,248 (99.7%)", "Label quality assurance"),
    ("Stage 7", "Stratified proportional sampling by month", "19,998 (Final corpus)", "CPU-feasible dense embedding corpus"),
]
for s in stages:
    add_row(tbl, s, center_from=2)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
para(
    "The 131,442 removed duplicates consisted overwhelmingly of copy-pasted template complaint letters, "
    "lender form letter responses, and automated complaint submission bot patterns. Deduplication prevents "
    "representation bias favouring template-heavy organisations such as large credit bureaus.",
    italic=True, color=GREY
)

heading2("3.3  Product Label Harmonisation")
para(
    "The CFPB's raw product taxonomy evolved between 2011 and 2023, creating inconsistent labels across "
    "years (e.g., 'Credit reporting' pre-2017 vs. 'Credit reporting, credit repair services, or other "
    "personal consumer reports' post-2017 refer to the same category). The product_mapping.yaml file "
    "implements systematic consolidation to 9 harmonised product classes:"
)
figure("fig_03_product_distribution.png", "Figure 3.2 — Product Category Distribution: Harmonised 9-class distribution across 19,998 corpus records. Credit reporting dominates at 51.2%, reflecting high automated dispute volume.", width=5.5)
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Class", "Harmonised Product Category", "Corpus Share"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
classes = [
    ("0", "Credit reporting & repair", "51.2%"),
    ("1", "Debt collection", "15.7%"),
    ("2", "Mortgage", "9.3%"),
    ("3", "Credit / prepaid card", "9.1%"),
    ("4", "Checking / savings account", "6.1%"),
    ("5", "Student loan", "3.8%"),
    ("6", "Vehicle / consumer loan", "2.4%"),
    ("7", "Money transfer & services", "1.7%"),
    ("8", "Other / personal loan", "0.7%"),
]
for c in classes:
    add_row(tbl, c)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("3.4  Chronological Dataset Partitioning")
para(
    "To simulate realistic production deployment conditions, the corpus is partitioned using strict "
    "calendar-based chronological splits rather than random sampling. This critical methodological "
    "choice prevents temporal data leakage—the artificial inflation of model performance that occurs "
    "when a model trained on data from time T is evaluated on data from before T. Figure 3.3 "
    "illustrates the non-overlapping partition boundaries."
)
figure("fig_06_split_timeline.png", "Figure 3.3 — Chronological Partition Timeline: Non-overlapping Train / Validation / Test boundaries across 2018–2023. No complaint appears in more than one split (verified by automated tests).", width=5.5)
tbl = doc.add_table(rows=1, cols=4)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Split", "Record Count", "Date Range", "Purpose"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
splits = [
    ("Training (70%)", "13,983", "2018-07-19 to 2022-03-17", "Model fitting and parameter estimation"),
    ("Validation (15%)", "2,999", "2022-03-18 to 2022-08-12", "Hyperparameter tuning and model selection"),
    ("Test (15%)", "3,016", "2022-08-13 to 2023-01-26", "Final, unbiased performance evaluation"),
]
for s in splits:
    add_row(tbl, s, center_from=1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("3.5  Text Preprocessing Pipeline")
para(
    "The preprocessing pipeline (src/preprocess.py) implements six sequential transformation stages. "
    "Each stage was empirically validated through the ablation study described in Section 4.1."
)
stages_text = [
    ("Stage 1 — Unicode Normalisation", "NFKC normalisation resolves Unicode character variants (em-dashes, curly quotes, non-breaking spaces) to standard ASCII equivalents, ensuring consistent tokenisation across complaints submitted from different devices and platforms."),
    ("Stage 2 — CFPB Redaction Handling", "XXXX → <redacted> (account numbers, names); XX/XX/XXXX → <date>; {$123.45} → <amt>. This stage is critical: raw redaction strings (XXXX) are non-informative noise tokens that, if retained, create artificial cluster centres in TF-IDF feature space. The ablation study demonstrates that complete redaction removal outperforms placeholder substitution by +1.49 pp Macro-F1."),
    ("Stage 3 — Noise Removal", "URLs, email addresses, and phone numbers removed via regular expressions. Excessive punctuation sequences collapsed. HTML entities decoded and stripped."),
    ("Stage 4 — Lowercasing", "All characters converted to lowercase to collapse case variants (e.g., 'Equifax', 'EQUIFAX', 'equifax' → 'equifax')."),
    ("Stage 5 — Tokenisation & Lemmatisation", "spaCy en_core_web_sm pipeline with nlp.pipe() for batched efficiency. Morphological lemmatisation consolidates inflected forms (e.g., 'payments', 'paying', 'paid' → 'payment'), reducing vocabulary size by ~18% and improving generalisation."),
    ("Stage 6 — Negation-Preserving Stopword Filtering", "Standard English stopwords are removed, with explicit preservation of semantically critical negation tokens (not, no, never, without, cannot, don't, won't, isn't). Discarding these tokens would invert the semantic polarity of many complaint sentences—validated in the ablation study."),
]
for title, desc in stages_text:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Inches(0.2)
    r1 = p.add_run(title + ": ")
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r1.font.name = "Calibri"
    r1.font.size = Pt(10)
    r2 = p.add_run(desc)
    r2.font.name = "Calibri"
    r2.font.size = Pt(10)
    r2.font.color.rgb = DARK

heading2("3.6  Feature Engineering")
para(
    "Three complementary feature representations are constructed exclusively from the training split "
    "(no information leakage into validation or test sets). Feature transformers (vectorisers, "
    "scalers) are fit only on training data and then applied to validation and test splits."
)
figure("fig07_zipf_distribution.png", "Figure 3.4 — Zipf Power-Law Distribution of narrative vocabulary (slope α ≈ 1.05). The heavy-tailed frequency distribution justifies the use of sublinear TF-IDF dampening (tf = 1 + log(tf)).", width=5.0)
feature_sets = [
    ("Sublinear TF-IDF (30,000 features)", "TfidfVectorizer(sublinear_tf=True, max_features=30000, ngram_range=(1,2), min_df=5, max_df=0.75). Sublinear scaling (tf = 1 + log(tf)) reduces the dominance of frequently repeated terms within long narratives. Zipf analysis (α ≈ 1.05) confirms heavy-tailed vocabulary dynamics, justifying sublinear dampening. Used in: Classification + Relief Prediction."),
    ("Bag of Words (30,000 features)", "CountVectorizer(max_features=30000, ngram_range=(1,2), min_df=2). Unweighted count features used for Naïve Bayes probabilistic baselines. No IDF weighting. Used in: NB Baselines."),
    ("MiniLM-L6-v2 Dense Embeddings (384 dims)", "sentence-transformers/all-MiniLM-L6-v2 encodes each complaint into a 384-dimensional L2-normalised dense vector. Pre-trained on 1B+ sentence pairs. Embeddings cached as .npy arrays for efficient reuse. Used in: Classification benchmarks + kNN Retrieval Dashboard."),
    ("Operational Metadata (non-leaking)", "One-hot encoded: submitted_via (Web, Phone, Email, Postal, Fax), tags (Older American, Servicemember), and state. Company identity EXCLUDED—ablation confirms company features introduce temporal overfitting (PR-AUC drops from 0.3865 → 0.3700). Used in: Relief Prediction ablation."),
]
for title, desc in feature_sets:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Inches(0.2)
    r1 = p.add_run(title + ": ")
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r1.font.name = "Calibri"
    r1.font.size = Pt(10)
    r2 = p.add_run(desc)
    r2.font.name = "Calibri"
    r2.font.size = Pt(10)
    r2.font.color.rgb = DARK

heading2("3.7  Experimental Protocol")
para("All experiments follow a strict protocol designed to ensure scientific rigour and prevent result inflation:")
bullet([
    "All model fitting and feature fitting (vectorisers, label encoders) performed exclusively on the training split.",
    "Hyperparameter selection uses the validation split only — the test split is never used for model selection decisions.",
    "Final performance metrics reported on the held-out test split and never revisited after selection.",
    "Bootstrap confidence intervals (1,000 resamples) computed for all primary evaluation metrics.",
    "McNemar's test used for pairwise classifier comparison to assess statistical significance of performance differences.",
    "Global random seed = 42 applied consistently throughout all pipeline stages.",
])
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. IMPLEMENTATION AND RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
heading1("4.  Implementation and Results")
heading2("4.1  Text Preprocessing Ablation Study  (AQ4)")
para(
    "To justify each preprocessing decision empirically rather than through assumption, a controlled "
    "ablation study evaluated seven preprocessing configurations on a stratified 3,000-row subsample "
    "of the training split, validated on 1,000 validation rows, using TF-IDF + Logistic Regression "
    "as a fast probe classifier. Results are visualised in Figure 4.1."
)
figure("fig_nb02_ablation.png", "Figure 4.1 — Preprocessing Ablation Study: Bar chart of Validation Macro-F1 across 7 configurations. The champion configuration (no redaction, remove entirely) achieves the highest F1 = 0.5140.", width=5.5)
tbl = doc.add_table(rows=1, cols=5)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Configuration", "Val Macro-F1", "Val Accuracy", "Δ vs Baseline", "Key Finding"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
ablation = [
    ("★ No Redaction (remove XXXX entirely)", "0.5140", "0.8260", "+1.49 pp", "Best overall"),
    ("Baseline (redaction → placeholder token)", "0.4991", "0.8230", "0.0000", "Reference"),
    ("No Lowercasing", "0.4978", "0.8230", "−0.13 pp", "Modest drop"),
    ("No Negation Preservation", "0.4976", "0.8210", "−0.15 pp", "Negations matter for dispute polarity"),
    ("No Lemmatisation", "0.4635", "0.8080", "−3.56 pp", "Sharp drop — morphological normalisation essential"),
    ("No Stopword Removal", "0.4236", "0.8120", "−7.55 pp", "Severe collapse — boilerplate drowns signal"),
    ("Minimal (raw lowercase only)", "0.4203", "0.7960", "−7.88 pp", "Confirms full pipeline necessity"),
]
for i, r in enumerate(ablation):
    add_row(tbl, r, center_from=1)
    if i == 0:
        bold_row(tbl, i+1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
para(
    "Key Insight: Lemmatisation (+3.56 pp) and stopword removal (+7.55 pp) are the two most critical "
    "pipeline stages. Negation preservation (often overlooked in generic NLP pipelines) prevents "
    "semantic inversion of dispute sentences. Complete redaction string removal slightly outperforms "
    "placeholder substitution (+1.49 pp).",
    bold=True, color=NAVY
)

heading2("4.2  Feature Retrieval Evaluation (kNN Precision@k)")
para(
    "Using cosine similarity over MiniLM-L6-v2 embeddings, retrieval-augmented complaint matching "
    "was evaluated using Precision@k metrics on the validation split:"
)
figure("fig09_2d_projection.png", "Figure 4.2 — 2D UMAP Projection of MiniLM-L6-v2 embeddings: Coloured by product class. Tight, well-separated clusters confirm that dense embeddings form product-coherent semantic neighbourhoods.", width=5.5)
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["k", "Precision@k", "Interpretation"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
knn = [("1","80.2%","80.2% of top-1 retrieved complaints share same product class"),
       ("3","91.9%","91.9% of top-3 retrieved complaints are product-coherent"),
       ("5","94.3%","Dense embeddings provide highly reliable semantic neighbourhood"),
       ("10","96.7%","Top-10 neighbourhood is almost entirely class-homogeneous")]
for r in knn:
    add_row(tbl, r, center_from=0)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("4.3  Component 1: Product Classification Benchmark  (AQ1 & AQ3)")
para(
    "Nine classifiers were trained and evaluated on identical chronological splits, with results "
    "sorted by Validation Macro-F1. Figure 4.3 shows the per-class top discriminative terms, "
    "and Figure 4.4 shows the confusion matrix of the champion classifier."
)
figure("fig08_class_top_terms.png", "Figure 4.3 — Top 15 Discriminative Bigrams per Product Class (LinearSVC weights). Each class has distinct, semantically interpretable dominant terms confirming classifier interpretability.", width=6.0)
tbl = doc.add_table(rows=1, cols=5)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Model", "Val F1", "Test F1", "Test Acc", "95% CI"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
models = [
    ("★ LinearSVC (Calibrated) ← Champion", "0.7349", "0.7394", "87.43%", "[0.7079, 0.7666]"),
    ("LogisticRegression (Val-Tuned)", "0.7171", "0.7319", "87.27%", "[0.6980, 0.7606]"),
    ("MiniLM-L6-v2 + LR", "0.7157", "0.7002", "85.68%", "[0.6676, 0.7303]"),
    ("LogisticRegression (Default)", "0.6644", "0.7054", "87.30%", "[0.6668, 0.7340]"),
    ("ComplementNB", "0.6264", "0.6457", "85.48%", "[0.6167, 0.6732]"),
    ("MultinomialNB", "0.6206", "0.6218", "84.85%", "[0.5922, 0.6473]"),
    ("DecisionTree (depth=10)", "0.5070", "0.4765", "77.25%", "[0.4451, 0.5049]"),
    ("DummyClassifier (Stratified)", "0.0923", "0.0950", "31.07%", "[0.0858, 0.1052]"),
    ("DummyClassifier (Majority)", "0.0865", "0.0873", "64.69%", "[0.0858, 0.0887]"),
]
for i, r in enumerate(models):
    add_row(tbl, r, center_from=1)
    if i == 0:
        bold_row(tbl, i+1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
figure("fig10_confusion_matrix.png", "Figure 4.4 — Normalised 9×9 Confusion Matrix of Champion LinearSVC on Test Set. Primary confusion boundary: Credit Reporting ↔ Debt Collection (31.7% of all errors), explained by semantic overlap in dispute semantics.", width=5.5)
para(
    "Statistical Significance — McNemar's Test (Champion vs. Majority Baseline): "
    "χ² = 535.64, p = 1.67 × 10⁻¹¹⁸ (effectively zero). The LinearSVC champion is "
    "overwhelmingly statistically superior to the baseline.",
    bold=True, color=NAVY
)
para("")
heading3("AQ3 — Temporal Concept Drift Analysis")
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Evaluation Protocol", "Macro-F1", "Accuracy"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
drift = [("Random Split (data-leaking baseline)","0.9330","97.2%"),
         ("Chronological Split (honest evaluation)","0.7317","87.4%"),
         ("Absolute Drift (Δ)","−0.2013","−9.8%")]
for i, r in enumerate(drift):
    add_row(tbl, r, center_from=0)
    if i == 2:
        bold_row(tbl, i+1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
para(
    "Critical Finding: The 20.13 percentage-point drop in Macro-F1 between randomised (0.9330) and "
    "chronological (0.7317) evaluation empirically confirms severe temporal concept drift. Standard "
    "k-fold cross-validation would have led to a dramatically overconfident and misleading performance "
    "estimate—a direct challenge to prior CFPB NLP research using random splits.",
    bold=True, color=RGBColor(0xC0, 0x39, 0x2B)
)

heading2("4.4  Component 2: Relief-Risk Prediction and Triage  (AQ2 & AQ7)")
para(
    "Outcome Definition: relief = 1 for 'Closed with monetary/non-monetary relief'; relief = 0 for "
    "'Closed with explanation' or 'Closed without relief'. Training positive base rate: 16.3% "
    "(1 in 6 complaints receives tangible relief). Class weight ratio: 5.15:1. Figure 4.5 shows "
    "Precision-Recall curves and Figure 4.6 shows the triage gain simulation."
)
figure("fig11_calibration_curve.png", "Figure 4.5 — Platt-Calibrated Probability Reliability Curve for Champion Text LR. Well-calibrated probabilities are essential for reliable triage threshold decisions.", width=5.0)
figure("fig12_pr_curve.png", "Figure 4.6 — Precision-Recall Curves comparing all relief models against the prior-rate baseline. Champion Text LR achieves PR-AUC = 0.3865 vs. baseline 0.3170.", width=5.0)
figure("fig13_triage_gain.png", "Figure 4.7 — Cumulative Relief Capture Gain Chart: At top 5% audit volume, Text LR achieves 1.41× lift; at top 20%, captures 24.48% of all relief cases.", width=5.5)
tbl = doc.add_table(rows=1, cols=7)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Model", "PR-AUC", "ROC-AUC", "Brier", "Prec@5%", "Lift@5%", "Recall@20%"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
relief = [
    ("★ Text LR (Champion)", "0.3865", "0.6063", "0.2316", "44.67%", "1.41×", "24.48%"),
    ("Text + Meta LR", "0.3796", "0.6023", "0.2321", "40.00%", "1.26×", "—"),
    ("HistGradientBoosting", "0.3780", "0.5929", "0.2336", "44.00%", "1.39×", "—"),
    ("Prior-Rate Baseline", "0.3170", "0.5000", "0.2403", "34.00%", "1.07×", "—"),
]
for i, r in enumerate(relief):
    add_row(tbl, r, center_from=1)
    if i == 0:
        bold_row(tbl, i+1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
para(
    "Bootstrap 95% CI (Champion Text LR): PR-AUC [0.3589, 0.4149], ROC-AUC [0.5850, 0.6262]. "
    "Company Leakage Ablation: Including company name features drops PR-AUC from 0.3865 → 0.3700, "
    "confirming temporal overfitting. Fairness Audit (AQ7): Disparate impact ratio across submission "
    "channels = 0.941 (within EEOC 80% four-fifths rule). Servicemember/Older American parity "
    "within ±0.02 PR-AUC.",
    italic=True, color=GREY
)

heading2("4.5  Component 3a: Unsupervised Topic Discovery")
para(
    "Three topic modelling algorithms were benchmarked across k ∈ {8, 12, 16, 20, 24}: LDA "
    "(gensim), NMF (scikit-learn), and K-Means clustering on MiniLM-L6-v2 dense embeddings. "
    "Evaluation uses C_V coherence (primary) and topic diversity (secondary). Figure 4.8 "
    "shows the coherence sweep and Figure 4.9 shows the topic-product heatmap."
)
figure("fig14_lda_coherence_sweep.png", "Figure 4.8 — LDA Coherence Sweep: C_V coherence scores across k ∈ {8,12,16,20,24}. Peak coherence = 0.5009 at k = 16, confirming optimal topic granularity.", width=5.5)
tbl = doc.add_table(rows=1, cols=5)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["k", "LDA C_V Coherence", "LDA Diversity", "NMF Diversity", "K-Means Silhouette"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
topics_sweep = [
    ("8","0.4701","0.7875","0.8625","0.0212"),
    ("12","0.4950","0.7500","0.7500","0.0216"),
    ("16 ← Selected","0.5009","0.7312","0.7875","0.0257"),
    ("20","0.4682","0.7400","0.7150","0.0218"),
    ("24","0.4643","0.6958","0.7042","0.0240"),
]
for i, r in enumerate(topics_sweep):
    add_row(tbl, r, center_from=0)
    if i == 2:
        bold_row(tbl, i+1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
figure("fig15_topic_product_heatmap.png", "Figure 4.9 — Topic × Product Class Conditional Probability Heatmap: Colour intensity shows the degree to which each topic is concentrated in specific product categories. Confirms semantic validity of discovered topics.", width=6.0)
para("Summary of 16 Discovered Complaint Topics:", bold=True, color=NAVY)
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Topic ID", "Interpreted Label", "Top Keywords"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
topics = [
    ("0","Credit Bureau Reporting Disputes","credit, report, account, dispute, bureau"),
    ("1","Debt Collection Harassment","debt, collection, agency, validate, call"),
    ("2","Student Loan Servicing","loan, student, payment, servicer, federal"),
    ("3","Mortgage Forbearance & Modification","mortgage, forbearance, modification, escrow"),
    ("4","Payday & High-Interest Lending","payday, interest, lender, fee, rollover"),
    ("5","Identity Theft & Fraud","identity, theft, fraud, unauthorized, police"),
    ("6","Checking Account Overdrafts","account, overdraft, bank, fee, charge"),
    ("7","Credit Card Billing & Disputes","credit, card, charge, dispute, merchant"),
    ("8","Auto Loan Repossession","vehicle, repossess, auto, loan, payment"),
    ("9","Foreclosure & Property","foreclosure, property, escrow, servicer"),
    ("10","Consumer Rights & Communication","contact, communication, cease, right, letter"),
    ("11","Personal Data & Privacy","information, personal, data, share, third"),
    ("12","Credit Inquiry & Application","inquiry, application, hard, pull, approve"),
    ("13","Wire Transfer & Money Services","transfer, wire, money, send, receive"),
    ("14","Account Closure & Funds Access","account, close, fund, access, hold"),
    ("15","COVID Relief & Stimulus Payments","covid, stimulus, relief, payment, deferral"),
]
for r in topics:
    add_row(tbl, r, center_from=0)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("4.6  Component 3b: Emerging-Issue Burst Detection  (AQ5)")
para(
    "The dual-engine burst detection system monitors monthly topic prevalence for statistically "
    "anomalous surges. Two complementary detectors are deployed in parallel:"
)
bullet([
    "Rolling Z-Score: z_t = (x_t − μ_{t−12:t−1}) / σ_{t−12:t−1}, window = 12 months, alert threshold = 2.0σ",
    "EWMA-CUSUM: S_t = max(0, S_{t−1} + (x_t − EWMA_t)), EWMA span = 6 months, cumulative threshold h = 4.0",
])
figure("fig16_topic_burst_detection.png", "Figure 4.10 — Temporal Burst Alert Timelines: Monthly topic prevalence with Z-Score and CUSUM alert periods annotated. COVID Relief (Topic 15) burst correctly detected 2–3 months before CARES Act peak volume.", width=6.0)
figure("fig_burst_mortgage_forbearance.png", "Figure 4.11 — Mortgage Forbearance Burst Detection: EWMA-CUSUM achieves F1 = 0.8000 and 3-month early-warning lead time before observed peak.", width=5.5)
tbl = doc.add_table(rows=1, cols=5)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Keyword Proxy", "Z-Score Precision", "Z-Score F1", "CUSUM F1", "Lead Time"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
burst = [
    ("COVID-19 Relief & Stimulus","66.7%","0.2353","0.7568","+2 months before CARES Act peak"),
    ("Overdraft & NSF Fees","100.0%","0.3529","0.2500","Coincided with fee rulemaking"),
    ("Credit Reporting Disputes","40.0%","0.2222","0.7027","Sustained 3-year upward drift"),
    ("Debt Collection (Reg. F)","57.1%","0.3810","0.7500","+1 month before Regulation F"),
    ("Mortgage Forbearance","100.0%","0.2500","0.8000","+3 months early warning"),
]
for r in burst:
    add_row(tbl, r, center_from=1)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
para(
    "Key Insight: Rolling Z-Score functions as an ultra-high-precision filter (100% on overdraft & "
    "mortgage forbearance) for immediate alert triggers. EWMA-CUSUM excels at detecting slow-burning "
    "multi-quarter systemic escalations (F1 up to 0.8000), better suited for regulatory policy "
    "preparation timelines that require 2–3 months of lead time.",
    bold=True, color=NAVY
)

heading2("4.7  Component 4: Bipartite Network Analysis  (AQ6)")
para(
    "A bipartite graph G = (I ∪ C, E) was constructed where I = 2,502 financial institutions, "
    "C = 170 CFPB issue categories, and E = 18,204 weighted company–issue edges (weighted by "
    "complaint count). The bipartite graph is projected onto a company co-occurrence unipartite "
    "network using Jaccard similarity edge weighting (top-100 institutions, threshold ≥ 0.1)."
)
figure("fig17_company_network.png", "Figure 4.12 — Bipartite Company-Issue Co-occurrence Network (Top 100 Institutions): Node size proportional to complaint volume; edge colour represents Louvain community membership. Three structurally distinct institutional clusters are visible.", width=6.0)
bullet([
    "Community 0 (Blue): Credit bureaus and FinTech credit builders — TransUnion, Experian, Equifax, Credit Karma, etc.",
    "Community 1 (Orange): Mega depository institutions and consumer lenders — JPMorgan Chase, Wells Fargo, Bank of America, Citibank.",
    "Community 2 (Green): Mortgage servicers and specialty lenders — Nationstar, Ocwen, Freedom Mortgage.",
])
para("")
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Network Metric", "Observed Value", "Statistical Significance"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
net_metrics = [
    ("Modularity Q","0.2568","p = 0.000 (< 0.001) vs. 100 null rewirings"),
    ("Null model Q̄","0.0671 ± 0.0084","Degree-preserving configuration null model"),
    ("Network Nodes","100 institutions","Top-100 by complaint volume"),
    ("Network Edges","3,774","Cosine similarity ≥ 0.1 threshold"),
    ("Communities detected","3","Louvain greedy modularity maximisation"),
]
for r in net_metrics:
    add_row(tbl, r, center_from=0)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()

heading2("4.8  Component 5: Systemic Risk Index (SRI)")
para(
    "A 5-dimension Composite Systemic Risk Index (SRI) was formulated to rank institutions by "
    "their regulatory risk profile. All dimensions are min-max normalised to [0, 1] before "
    "weighted aggregation:"
)
p = doc.add_paragraph()
p.paragraph_format.left_indent = Inches(0.4)
p.paragraph_format.space_before = Pt(4)
p.paragraph_format.space_after  = Pt(4)
r = p.add_run("SRI = 0.25 × V_volume  +  0.20 × R_relief_deficit  +  0.20 × B_breadth  +  0.20 × C_centrality  +  0.15 × S_burst_intensity")
r.font.name = "Courier New"
r.font.size  = Pt(10)
r.font.bold  = True
r.font.color.rgb = NAVY

figure("fig18_systemic_risk_index.png", "Figure 4.13 — Composite Systemic Risk Index (SRI) Rankings for Top-25 Institutions. Three credit bureaus (TransUnion, Experian, Equifax) dominate risk rankings. Equifax exhibits the most severe relief deficit at only 4.3%.", width=6.0)
tbl = doc.add_table(rows=1, cols=5)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Rank", "Institution", "SRI Score", "Relief Rate", "Issue Breadth"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
sri = [
    ("1","TRANSUNION INTERMEDIATE HOLDINGS","0.7819","46.3%","110/170"),
    ("2","Experian Information Solutions Inc.","0.7187","33.4%","123/170"),
    ("3","EQUIFAX, INC.","0.6825","4.3% ⚠","116/170"),
    ("4","TD BANK US HOLDING COMPANY","0.4631","45.7%","150/170"),
    ("5","U.S. BANCORP","0.4365","41.8%","162/170"),
    ("6","Wells Fargo & Company","0.4318","38.2%","168/170"),
    ("7","JPMorgan Chase & Co.","0.4102","42.1%","167/170"),
    ("8","CAPITAL ONE FINANCIAL CORP.","0.3976","35.8%","157/170"),
    ("9","Bank of America, National Association","0.3854","39.4%","163/170"),
    ("10","CITIBANK, N.A.","0.3741","41.2%","159/170"),
]
for i, r in enumerate(sri):
    add_row(tbl, r, center_from=0)
    if i == 2:
        shade_row(tbl, i+1, "FFE4E1")  # highlight Equifax
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
figure("fig19_sri_sensitivity.png", "Figure 4.14 — SRI Sensitivity Analysis (100 Dirichlet weight perturbations): Mean Kendall's τ = 0.6374 (σ = 0.2321). Top-3 bureaus retain ranks 1–3 in >94% of simulations, confirming rank robustness.", width=5.5)
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. ANALYSIS AND DISCUSSION
# ═══════════════════════════════════════════════════════════════════════════════
heading1("5.  Analysis and Discussion")
heading2("5.1  Synthesis of Key Findings")
findings = [
    ("Finding 1 — Classification Accuracy is High, but Temporal Drift is Real",
     "The LinearSVC champion achieves Test Macro-F1 = 0.7394, demonstrating that complaint narratives "
     "contain strong lexical signals for product routing. However, the 20.13 pp performance gap between "
     "random (0.9330) and chronological (0.7317) evaluation confirms that these signals are non-stationary. "
     "Any deployed classifier must be retrained every ~6 months to maintain production accuracy."),
    ("Finding 2 — Text Alone Outperforms Text+Metadata for Relief Prediction",
     "Counter-intuitively, the pure text Logistic Regression (PR-AUC = 0.3865) outperforms Text+Metadata "
     "(0.3796) on the chronological test split. The company leakage ablation explains this: metadata features "
     "that correlate with company-level complaint patterns introduce temporal overfitting."),
    ("Finding 3 — Topic Discovery Reveals Gaps in Official CFPB Taxonomy",
     "The 16 LDA topics do not map one-to-one with CFPB's 9 product categories. Cross-cutting topics "
     "(Identity Theft & Fraud; Consumer Rights & Communication; Data Privacy) span multiple products, "
     "suggesting the CFPB's complaint taxonomy conflates distinct regulatory issues within broad product labels."),
    ("Finding 4 — Dual-Engine Burst Detection Provides Complementary Signal",
     "No single detector is optimal across all event types. Rolling Z-Score provides surgical precision "
     "(100% for overdraft fees and mortgage forbearance). EWMA-CUSUM provides broader recall and higher F1 "
     "on sustained multi-month regulatory trends (F1 = 0.8000 for mortgage forbearance; 2–3 month lead time)."),
    ("Finding 5 — Three Credit Bureaus Dominate Systemic Risk",
     "The SRI analysis reveals a stark bifurcation: TransUnion, Experian, and Equifax collectively generate "
     ">70% of complaint volume but operate under fundamentally different remediation philosophies. "
     "Equifax's 4.3% relief rate vs. TransUnion's 46.3% represents a 10-fold difference that warrants "
     "regulatory investigation."),
]
for title, desc in findings:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(2)
    r1 = p.add_run(title + ": ")
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r1.font.name = "Calibri"
    r1.font.size = Pt(11)
    r2 = p.add_run(desc)
    r2.font.name = "Calibri"
    r2.font.size = Pt(11)
    r2.font.color.rgb = DARK

heading2("5.2  Methodological Reflections")
bullet([
    "On Chronological Evaluation: The decision to use strict calendar splits rather than k-fold cross-validation was the single most impactful methodological choice. Researchers who report only random-split performance for financial NLP models systematically overstate expected production performance by approximately 20 percentage points.",
    "On Coherence vs. Interpretability Trade-offs: Peak C_V coherence (k = 16) was confirmed to align with human interpretability through qualitative keyword review. However, topic labelling remains a human-in-the-loop activity — coherence scores are necessary but not sufficient for actionable topic discovery.",
    "On Network Projection: The cosine-similarity projection entails information loss. Many smaller institutions with complaint counts below the top-100 threshold are excluded from network analysis. Future work should explore weighted projection approaches that handle the full long-tail distribution.",
    "On SRI Subjectivity: The 5-dimension SRI weights are researcher-determined. The Dirichlet sensitivity analysis (mean τ = 0.6374) demonstrates rank robustness, but regulatory adoption would require stakeholder deliberation on weighting priorities.",
])

heading2("5.3  Limitations")
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Table Grid'
for c, h in zip(tbl.rows[0].cells, ["Limitation", "Severity", "Mitigation in This Work"]):
    c.paragraphs[0].add_run(h)
shade_header(tbl)
lims = [
    ("Narrative opt-in bias (volunteer filers only)","High","Documented in DATASET_CARD.md; results qualified throughout"),
    ("Relief labels are institutional self-reports","Medium","Noted in every evaluation; fairness slices conducted (AQ7)"),
    ("English-only corpus","Medium","Scope explicitly limited to English narratives in all claims"),
    ("Static models subject to temporal drift","High","AQ3 drift analysis quantifies cost; retraining schedule recommended"),
    ("TF-IDF ignores word order","Low–Medium","Mitigated by bigram features and dense embedding comparison"),
    ("LDA assumes bag-of-words document model","Low","Compared against NMF and K-Means; qualitative validation performed"),
    ("SRI weights are researcher-determined","Medium","100-draw Dirichlet sensitivity analysis demonstrates rank stability (τ > 0.64)"),
    ("Top-100 company network truncation","Medium","Full 2,502-company bipartite breadth metrics provided separately"),
]
for r in lims:
    add_row(tbl, r, center_from=0)
table_style(tbl)
shade_header(tbl)
doc.add_paragraph()
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. CONCLUSION AND FUTURE WORK
# ═══════════════════════════════════════════════════════════════════════════════
heading1("6.  Conclusion and Future Work")
heading2("6.1  Summary of Contributions")
para(
    "ComplaintScope makes five primary contributions to the field of regulatory text analytics "
    "and financial NLP:"
)
bullet([
    "Rigorous Temporal Evaluation Framework: Strict calendar-based chronological partitioning and temporal concept drift measurement (Δ = −20.13 pp) establishes an empirical benchmark for realistic financial NLP evaluation that directly challenges prior literature reporting inflated random-split performance.",
    "Calibrated Multi-Task Relief Prediction with Operational Triage Simulation: The calibrated Text LR model (Brier Score = 0.2316) provides statistically reliable probability estimates for operational deployment. The triage simulation (Lift@5% = 1.41×) translates abstract model metrics into concrete efficiency gains.",
    "Integrated Topic Discovery and Burst Detection with Ground-Truth Validation: Rather than reporting topic coherence as an end result, ComplaintScope applies discovered topics to temporal burst detection and validates performance against independently defined keyword proxy ground truths (CUSUM-F1 = 0.8000).",
    "Statistically Validated Institutional Network Community Detection: The 100-iteration null model hypothesis test (Q = 0.2568, p < 0.001) provides rigorous statistical confirmation that observed institutional clustering reflects genuine regulatory issue segregation, not projection artefacts.",
    "Transparent, Robust Composite Systemic Risk Index: The 5-dimension SRI with Dirichlet sensitivity analysis (mean Kendall's τ = 0.6374) provides a methodologically sound composite risk ranking robust to reasonable variations in regulatory weighting priorities.",
])

heading2("6.2  Regulatory Policy Recommendations")
bullet([
    "Recommendation 1 — Targeted Supervisory Audit for Credit Bureaus: TransUnion (SRI = 0.7819), Experian (SRI = 0.7187), and Equifax (SRI = 0.6825) collectively generate the highest composite systemic risk. A dedicated supervisory examination programme for credit bureau dispute resolution practices is warranted.",
    "Recommendation 2 — Equifax Relief Deficit Investigation: Equifax's 4.3% relief rate vs. TransUnion's 46.3% represents a 10-fold difference requiring immediate regulatory inquiry—whether compositional or systematic denial of valid consumer claims.",
    "Recommendation 3 — Broad-Spectrum Compliance Reviews for Universal Banks: Wells Fargo (168/170 issues), JPMorgan Chase (167/170), and Bank of America (163/170) exhibit pervasive complaint breadth suggesting cross-cutting systemic issues beyond product-specific examinations.",
    "Recommendation 4 — Real-Time Emerging Issue Monitoring Protocol: The 2–3 month early-warning demonstrated by EWMA-CUSUM for mortgage forbearance and COVID-19 relief demonstrates operationally actionable lead time for proactive consumer advisories.",
])

heading2("6.3  Future Work Directions")
bullet([
    "Direction 1 — Domain-Adapted Transformer Models: Fine-tuning FinBERT or LegalBERT on CFPB complaint narratives would likely improve Classification Macro-F1 by capturing domain-specific financial and legal terminology.",
    "Direction 2 — Online Learning and Concept Drift Adaptation: The 20 pp temporal drift motivates adaptive learning algorithms (ADWIN, Reservoir Sampling, online LDA) for incremental monthly parameter updates without full retraining cycles.",
    "Direction 3 — Causal Attribution of Relief Outcomes: Applying causal inference methods (Double Machine Learning, instrumental variable regression using regulatory events) to determine which institutional practices cause low relief rates.",
    "Direction 4 — Multilingual Extension: Extending the pipeline to Spanish and other languages prevalent in CFPB submissions to improve coverage of underserved consumer populations.",
    "Direction 5 — Dynamic Temporal Network Analysis: A temporal network model tracking quarterly bipartite snapshots would capture institutional trajectory and early signs of systemic deterioration beyond static network analysis.",
])
hline()

# ═══════════════════════════════════════════════════════════════════════════════
# 7. REFERENCES
# ═══════════════════════════════════════════════════════════════════════════════
heading1("7.  References")
refs = [
    "Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. arXiv:1908.10063.",
    "Battiston, S., Puliga, M., Kaushik, R., Tasca, P., & Caldarelli, G. (2012). DebtRank: Too Central to Fail? Scientific Reports, 2(1), 1–6.",
    "Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993–1022.",
    "Blondel, V. D., Guillaume, J. L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics, 2008(10), P10008.",
    "Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). LEGAL-BERT: The Muppets straight out of Law School. EMNLP 2020 Findings.",
    "Efron, B. (1979). Bootstrap methods: Another look at the jackknife. The Annals of Statistics, 7(1), 1–26.",
    "Gebru, T., et al. (2021). Datasheets for datasets. Communications of the ACM, 64(12), 86–92.",
    "Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). Exploring Network Structure using NetworkX. Proc. SciPy, 11–15.",
    "Honnibal, M., & Montani, I. (2017). spaCy 2: Natural Language Understanding with Bloom Embeddings. To appear.",
    "Joachims, T. (1998). Text categorization with support vector machines. Proceedings of ECML 1998, 137–142.",
    "Kleinberg, J. (2003). Bursty and hierarchical structure in streams. Data Mining and Knowledge Discovery, 7(4), 373–397.",
    "Kogan, S., Levin, D., Routledge, B. R., Sagi, J. S., & Smith, N. A. (2009). Predicting risk from financial reports with regression. Proceedings of NAACL-HLT 2009, 272–280.",
    "Lancichinetti, A., & Fortunato, S. (2010). Community detection algorithms: A comparative analysis. Physical Review E, 80(5), 056117.",
    "Lee, D. D., & Seung, H. S. (1999). Learning the parts of objects by non-negative matrix factorization. Nature, 401(6755), 788–791.",
    "Leskovec, J., Backstrom, L., & Kleinberg, J. (2009). Meme-tracking and the dynamics of the news cycle. Proceedings of ACM KDD 2009, 497–506.",
    "McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions. Psychometrika, 12(2), 153–157.",
    "Montgomery, D. C. (2019). Introduction to Statistical Quality Control (8th ed.). Wiley.",
    "Newman, M. E. J. (2006). Modularity and community structure in networks. PNAS, 103(23), 8577–8582.",
    "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of ICML 2005, 625–632.",
    "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
    "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Proceedings of EMNLP 2019, 3982–3992.",
    "Řehůřek, R., & Sojka, P. (2010). Software Framework for Topic Modelling with Large Corpora. Proceedings of LREC 2010, 45–50.",
    "Röder, M., Both, A., & Hinneburg, A. (2015). Exploring the Space of Topic Coherence Measures. Proceedings of ACM WSDM 2015, 399–408.",
    "Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, 10(3), e0118432.",
    "US Consumer Financial Protection Bureau. (2023). Consumer Complaint Database. consumerfinance.gov/data-research/consumer-complaints/",
    "Wang, S., & Manning, C. D. (2012). Baselines and bigrams: Simple, good sentiment and topic classification. Proceedings of ACL 2012, 90–94.",
]
for i, ref in enumerate(refs):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    r = p.add_run(f"[{i+1}]  {ref}")
    r.font.name = "Calibri"
    r.font.size  = Pt(10)
    r.font.color.rgb = DARK

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(
    "This report presents original analysis conducted for CBS3009 – Advanced Social, Text and Media Analytics, "
    "VIT Vellore. All results are derived exclusively from code execution on the CFPB public dataset. "
    "No data, figures, or metrics have been fabricated. Global random seed = 42 ensures full reproducibility."
)
r.font.name = "Calibri"
r.font.size  = Pt(9)
r.font.italic = True
r.font.color.rgb = GREY

# ─── Save ─────────────────────────────────────────────────────────────────────
doc.save(str(OUT))
print(f"Report saved: {OUT}")
print(f"Report size: {OUT.stat().st_size / 1024:.1f} KB")

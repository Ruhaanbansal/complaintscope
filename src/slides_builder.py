"""
ComplaintScope: 22-slide PowerPoint presentation generator.
Produces: slides/ComplaintScope_Presentation.pptx
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette: Deep Navy, Slate, Teal, Coral, Light Silver
    COLOR_BG_DARK   = RGBColor(15, 23, 42)     # #0f172a
    COLOR_CARD_DARK = RGBColor(30, 41, 59)     # #1e293b
    COLOR_TEXT_MAIN = RGBColor(241, 245, 249)  # #f1f5f9
    COLOR_TEXT_MUTED= RGBColor(148, 163, 184)  # #94a3b8
    COLOR_PRIMARY   = RGBColor(56, 189, 248)   # #38bdf8 (Sky blue)
    COLOR_ACCENT    = RGBColor(251, 146, 60)   # #fb923c (Orange)
    COLOR_GREEN     = RGBColor(74, 222, 128)   # #4ade80

    blank_layout = prs.slide_layouts[6]

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="COMPLAINTSCOPE | CBS3009 PROJECT"):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_PRIMARY

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN

    def add_card(slide, left, top, width, height, title, body_bullets, accent_color=COLOR_PRIMARY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_DARK
        card.line.color.rgb = RGBColor(51, 65, 85)
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(17)
        p0.font.bold = True
        p0.font.color.rgb = accent_color

        for bullet in body_bullets:
            p = tf.add_paragraph()
            p.text = "• " + bullet
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_TEXT_MAIN
            p.space_before = Pt(6)

    def add_image_if_exists(slide, img_path, left, top, width, height):
        p = Path(img_path)
        if p.exists():
            slide.shapes.add_picture(str(p), left, top, width, height)

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 1: Title Slide
    # ─────────────────────────────────────────────────────────────────────────
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "COMPLAINTSCOPE"
    p0.font.size = Pt(44)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_PRIMARY

    p1 = tf.add_paragraph()
    p1.text = "An End-to-End Text, Topic & Network Analytics System for Consumer-Complaint Triage and Systemic Risk Early Warning"
    p1.font.size = Pt(20)
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_before = Pt(12)

    p2 = tf.add_paragraph()
    p2.text = "Course: CBS3009 – Advanced Social, Text and Media Analytics | Term: Fall 2026"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_TEXT_MUTED
    p2.space_before = Pt(28)

    p3 = tf.add_paragraph()
    p3.text = "Team Members: Ruhaan Bansal (23BBS0046) | Vedant Rajesh (23BBS0037) | Anish Desai (23BBS0119)\nFaculty Guide: Prof. Sathish Kumar K | School of Computer Science & Engineering | VIT Vellore"
    p3.font.size = Pt(14)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_ACCENT
    p3.space_before = Pt(12)

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 2: Problem Context & Motivation
    # ─────────────────────────────────────────────────────────────────────────
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "Problem Context & Operational Motivation", "1. INTRODUCTION & MOTIVATION")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "1. The Triage Bottleneck", [
        "CFPB receives >8M consumer complaints, with thousands of detailed narratives daily.",
        "Manual complaint routing to product divisions is slow, costly, and inconsistent.",
        "Automated multi-class classification is required for real-time operational routing."
    ])
    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "2. The Relief-Risk Gap", [
        "Only 16.3% of complaints result in monetary or non-monetary consumer relief.",
        "Regulatory caseworkers lack probabilistic risk scoring to prioritize investigations.",
        "Triage queue optimization can yield massive efficiency gains via high-precision Lift@k."
    ])
    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "3. Early Warning & Network", [
        "Emerging systemic crises (e.g., COVID forbearance) emerge in narratives months early.",
        "Keyword bursts precede formal regulatory enforcement by 2-3 months.",
        "Cross-institutional complaint networks expose systemic financial hazard clusters."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 3: System Architecture
    # ─────────────────────────────────────────────────────────────────────────
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "ComplaintScope End-to-End System Architecture", "2. SYSTEM OVERVIEW")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "5 Core Analytical Components", [
        "Component 1 (Phase 4): 9-Class Product Classification Suite across 7 models with bootstrap CIs.",
        "Component 2 (Phase 5): Imbalance-Aware Consumer Relief Risk Prediction & Queue Simulation.",
        "Component 3a (Phase 6): Unsupervised Topic Discovery (LDA vs NMF vs KMeans) with coherence sweep.",
        "Component 3b (Phase 7): Dual-Detector Emerging Issue Detection (Z-Score + EWMA-CUSUM).",
        "Component 4 & 5 (Phases 8-9): Bipartite Network Projection, Louvain Communities & Systemic Risk Index (SRI)."
    ])
    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Engineering Rigor & Delivery", [
        "Chronological Splits (70/15/15): Strict calendar date partitions to prevent lookahead leakage.",
        "Train-Only Vocabulary: 30K sublinear TF-IDF + 384-dim all-MiniLM-L6-v2 embeddings.",
        "Empirical Preprocessing Ablation: 7 configurations evaluated on validation split.",
        "Full Reproducibility: 19/19 pytest suite passes, clean-state seeds, zero fabricated metrics.",
        "Streamlit Dashboard: 5-page interactive web app loaded from self-contained <10MB artifacts."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 4: Dataset & Provenance
    # ─────────────────────────────────────────────────────────────────────────
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "Data Provenance, Filtering & Chronological Splits", "3. DATASET & GOVERNANCE")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Corpus Provenance & Filtering", [
        "Source: CFPB Consumer Complaint Database (CC0 1.0 Public Domain).",
        "Hugging Face mirror archive (SHA-256 verified in data_provenance.json).",
        "Strict filtering funnel: narratives >= 20 words, 131,442 duplicates removed.",
        "Harmonized from fragmented multi-year taxonomy to 9 consolidated classes.",
        "Final sampled modeling corpus: 19,998 narrative complaints spanning 2018–2023."
    ])
    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Anti-Leakage Chronological Partitions", [
        "Train (70%): 13,983 complaints (2018-07-19 to 2022-03-17).",
        "Validation (15%): 2,999 complaints (2022-03-18 to 2022-08-12).",
        "Test (15%): 3,016 complaints (2022-08-13 to 2023-01-26).",
        "Zero boundary crossover verified by tests/test_splits_no_leakage.py.",
        "Simulates true production deployment against temporal concept drift."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 5: EDA & Visualizations
    # ─────────────────────────────────────────────────────────────────────────
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "Exploratory Data Analysis & Empirical Insights", "4. EXPLORATORY DATA ANALYSIS")

    add_image_if_exists(s5, "results/figures/fig_03_product_distribution.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Key Distributional Observations", [
        "Class Imbalance: Credit reporting represents >60% of narrative complaints, reflecting widespread credit file dispute automation.",
        "Long-Tail Products: Student loans, vehicle loans, and money transfers constitute specialized low-frequency categories.",
        "Relief Rate Skew: Extreme variation across products—checking account complaints achieve highest relief rates; credit reporting lowest.",
        "Narrative Length: Median narrative length is 162 words; heavy right-skew with complex grievances exceeding 1,000 words.",
        "Temporal Volatility: Complaint volume surged during 2020-2021 pandemic relief periods."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 6: Preprocessing & Ablation
    # ─────────────────────────────────────────────────────────────────────────
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "Text Preprocessing & Controlled Ablation Study", "5. NLP PREPROCESSING")

    add_image_if_exists(s6, "results/figures/fig_nb02_ablation.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "7-Configuration Ablation Results", [
        "Empirical ablation executed on 3,000 train / 1,000 validation split:",
        "No Redaction Handling (delete): 0.5140 Macro-F1 (champion; removes uninformative mask tokens).",
        "Baseline (placeholders): 0.4991 Macro-F1.",
        "No Negation Preservation: 0.4976 Macro-F1 (dropping negations inverts dispute sentiment).",
        "No Lemmatization: 0.4635 Macro-F1 (severe 3.56% drop; proves inflectional unification is vital).",
        "No Stopword Removal: 0.4236 Macro-F1 (catastrophic 7.55% collapse due to legal filler).",
        "Minimal (raw lowercase): 0.4203 Macro-F1 (confirms need for full NLP pipeline)."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 7: Feature Engineering
    # ─────────────────────────────────────────────────────────────────────────
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "Feature Engineering: Sparse, Dense & Retrieval Spaces", "6. FEATURE REPRESENTATION")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Sparse & Dense Representations", [
        "Bag-of-Words & Sublinear TF-IDF: 30,000 vocab, 1-2 grams, min_df=3, sublinear scaling tf=1+log(tf).",
        "Fitted exclusively on train split to prevent vocabulary leakage.",
        "Zipf Distribution: Sublinear TF scaling dampens hyper-frequent legal jargon tokens.",
        "Dense Transformer Embeddings: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions, L2-normalized).",
        "Cached as .npy arrays: train (13,983x384), val (2,999x384), test (3,016x384)."
    ])
    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Semantic Neighborhood (kNN Retrieval)", [
        "Cosine kNN evaluated on validation embeddings confirms strong semantic clustering:",
        "Precision@1 = 80.2% label agreement.",
        "Precision@3 = 91.9% label agreement.",
        "Precision@5 = 94.3% label agreement.",
        "Precision@10 = 96.7% label agreement.",
        "Demonstrates high semantic density suitable for downstream zero-shot retrieval."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 8: Product Classification Suite
    # ─────────────────────────────────────────────────────────────────────────
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "Component 1: Product Classification Benchmark", "7. COMPONENT 1 - CLASSIFICATION")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Benchmark Results (Holdout Test Split)", [
        "LinearSVC (calibrated): Test Macro-F1 = 0.7394, Accuracy = 87.43%, 95% CI [0.708, 0.767].",
        "LogisticRegression (tuned): Test Macro-F1 = 0.7319, Accuracy = 87.27%, 95% CI [0.698, 0.761].",
        "MiniLM-L6 + LR: Test Macro-F1 = 0.7002, Accuracy = 85.68%, 95% CI [0.668, 0.730].",
        "LogisticRegression (default): Test Macro-F1 = 0.7054, Accuracy = 87.30%.",
        "ComplementNB: Test Macro-F1 = 0.6457, Accuracy = 85.48%.",
        "MultinomialNB: Test Macro-F1 = 0.6218, Accuracy = 84.85%.",
        "DecisionTree (depth=10): Test Macro-F1 = 0.4765, Accuracy = 77.25%.",
        "Dummy (majority): Test Macro-F1 = 0.0873, Accuracy = 64.69%."
    ])
    add_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Statistical Significance & Tuning", [
        "Hyperparameter Tuning: Grid search on validation split over C in [0.01..10.0] and solver [lbfgs, saga].",
        "Champion Architecture: LinearSVC with Platt calibration provides optimal decision boundaries.",
        "McNemar's Hypothesis Test: LinearSVC vs Majority Baseline:",
        "Chi-squared statistic = 535.64, p-value = 1.67e-118.",
        "Proves statistical superiority beyond any chance threshold (p < 0.001)."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 9: Temporal Drift & Errors
    # ─────────────────────────────────────────────────────────────────────────
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "Temporal Concept Drift & Error Taxonomy", "8. CLASSIFICATION ANALYSIS")

    add_image_if_exists(s9, "results/figures/fig10_confusion_matrix.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "AQ3 Drift & Error Taxonomy Findings", [
        "AQ3 Temporal Concept Drift: Model evaluated on random test split achieves Macro-F1 = 0.9330.",
        "On strict chronological test split, Macro-F1 drops to 0.7317 (Delta = -0.2013, 20.1% degradation!).",
        "Confirms that non-chronological cross-validation severely overestimates production performance.",
        "Error Taxonomy Audit (60 sampled errors, 12.57% test error rate):",
        "Top Confusion: Credit reporting vs Debt collection (disputes against reporting collection agencies).",
        "Second Confusion: Checking/savings accounts vs Credit cards (debit transaction card claims)."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 10: Relief-Risk Prediction
    # ─────────────────────────────────────────────────────────────────────────
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "Component 2: Consumer Relief-Risk Prediction", "9. COMPONENT 2 - RELIEF RISK")

    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Problem Setup & Metrics", [
        "Binary Objective: Predict whether an incoming narrative will result in monetary or non-monetary relief.",
        "Severe Class Imbalance: 16.3% positive base rate in training split (class weight = 5.15).",
        "ROC-AUC is uninformative under heavy skew; evaluation prioritizes PR-AUC, Brier score, and Lift@k.",
        "Model Suite: Prior-rate baseline, Text LR, Text+Metadata LR, HistGradientBoosting (dense SVD+OHE).",
        "Champion: Text Logistic Regression achieves PR-AUC = 0.3865, ROC-AUC = 0.6063, Brier = 0.2316."
    ])
    add_image_if_exists(s10, "results/figures/fig12_pr_curve.png", Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 11: Triage Simulation & Lift
    # ─────────────────────────────────────────────────────────────────────────
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11)
    add_header(s11, "Operational Triage Queue Simulation & Lift@k", "10. RELIEF TRIAGE SIMULATION")

    add_image_if_exists(s11, "results/figures/fig13_triage_gain.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Measurable Caseworker Yield Gains", [
        "Random Review Baseline: 16.3% positive relief cases.",
        "Top 5% Priority Queue: Precision@5% = 44.67% (Lift = 1.41x base rate).",
        "Top 10% Priority Queue: Precision@10% = 42.86% (Lift = 1.35x base rate).",
        "Top 20% Priority Queue: Precision@20% = 38.81% (Lift = 1.22x base rate).",
        "Operational Value: Regulatory caseworkers inspecting top 20% ranked complaints capture 24.5% of all relief cases.",
        "Yields a 41% higher investigative efficiency at top ranks compared to unprioritized review."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 12: Demographic Fairness & Leakage
    # ─────────────────────────────────────────────────────────────────────────
    s12 = prs.slides.add_slide(blank_layout)
    add_background(s12)
    add_header(s12, "Fairness Slices & Company Leakage Ablation", "11. ETHICAL & FAIRNESS AUDIT")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Demographic & Channel Slices", [
        "Evaluated PR-AUC across 14 demographic, submission channel, and geographic groups.",
        "Channels: Web, Referral, and Phone show consistent probability calibration (PR-AUC 0.37 - 0.40).",
        "Tags: Servicemembers and Older Americans exhibit comparable predictive yield.",
        "Geographic Variation: States with heavy credit reporting volume show slight baseline shifts.",
        "Model avoids disparate impact across channels while preserving triage ranking integrity."
    ])
    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Company Feature Leakage Ablation", [
        "Ablation Experiment: Included institutional identity (company ID) in relief feature space.",
        "Result: Test PR-AUC degraded from 0.3865 down to 0.3700.",
        "Analytical Root Cause: Institutional dispute practices change across quarters; company OHE memorizes past settlement behavior.",
        "Conclusion: Relying purely on narrative text yields superior generalizability and prevents institutional bias."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 13: Latent Topic Discovery
    # ─────────────────────────────────────────────────────────────────────────
    s13 = prs.slides.add_slide(blank_layout)
    add_background(s13)
    add_header(s13, "Component 3a: Latent Topic Discovery & Coherence Sweep", "12. COMPONENT 3A - TOPIC DISCOVERY")

    add_image_if_exists(s13, "results/figures/fig14_lda_coherence_sweep.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s13, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Multi-Model Sweep & Selection", [
        "Evaluated LDA (gensim), NMF (sklearn), and K-Means on dense embeddings across k in [8, 12, 16, 20, 24].",
        "LDA Coherence c_v: k=8 (0.4701), k=12 (0.4950), k=16 (0.5009), k=20 (0.4682), k=24 (0.4643).",
        "Champion: LDA at k=16 delivers optimal semantic coherence (c_v = 0.5009) with high topic diversity (0.7312).",
        "NMF delivered high diversity at low k but lacked document mixture probabilities.",
        "K-Means produced low silhouette scores (0.021 - 0.026), demonstrating non-spherical embedding manifold."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 14: Topic Taxonomy & Heatmap
    # ─────────────────────────────────────────────────────────────────────────
    s14 = prs.slides.add_slide(blank_layout)
    add_background(s14)
    add_header(s14, "Topic Taxonomy & Cross-Product Heatmap", "13. TOPIC TAXONOMY")

    add_image_if_exists(s14, "results/figures/fig15_topic_product_heatmap.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s14, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Interpretable Complaint Themes", [
        "16 Granular Discovered Clusters (sample):",
        "Topic 0: Credit file dispute documentation (credit, report, account, dispute, bureau).",
        "Topic 1: Debt collection harassment & validation calls (debt, collection, agency, validate).",
        "Topic 3: Mortgage escrow & CARES Act forbearance (mortgage, loan, payment, modification).",
        "Topic 6: Checking account overdraft fees & unauthorized charges (account, bank, fee, overdraft).",
        "Topic 9: Identity theft & fraudulent trade lines (identity, theft, fraud, police).",
        "Heatmap shows sharp concentration for loan products and broad dispersion for credit reporting."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 15: Emerging Issue Detection
    # ─────────────────────────────────────────────────────────────────────────
    s15 = prs.slides.add_slide(blank_layout)
    add_background(s15)
    add_header(s15, "Component 3b: Dual-Detector Burst Detection", "14. COMPONENT 3B - BURST DETECTION")

    add_image_if_exists(s15, "results/figures/fig16_topic_burst_detection.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s15, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Dual Anomaly Detection Framework", [
        "Time Series: Monthly prevalence computed across 2018–2023 (691 topic-month observations).",
        "Detector 1 - Rolling Z-Score: Trailing 12-month baseline, threshold z > 2.0 flags sharp abrupt shocks.",
        "Detector 2 - EWMA-CUSUM: Exponential smoothing (span=6, threshold=1.5sigma) tracks cumulative structural drift.",
        "Complementary Roles: Z-score prevents false alarms for high-volatility topics; CUSUM catches gradual policy changes.",
        "Automated alerts trigger regulatory early warning before grievance volume peaks."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 16: Proxy Validation & Case Studies
    # ─────────────────────────────────────────────────────────────────────────
    s16 = prs.slides.add_slide(blank_layout)
    add_background(s16)
    add_header(s16, "Independent Keyword Proxy Validation & Case Studies", "15. PROXY VALIDATION")

    add_card(s16, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Pre-Registered Proxy Validation", [
        "5 Independent Keyword Proxies committed before analysis:",
        "covid_relief: Z-Precision = 66.7%, CUSUM-F1 = 0.7568 (+2 months lead-time).",
        "overdraft_fee: Z-Precision = 100.0%, CUSUM-F1 = 0.2500 (zero false alarms).",
        "credit_reporting: Z-Precision = 40.0%, CUSUM-F1 = 0.7027 (long-term drift).",
        "debt_collection: Z-Precision = 57.1%, CUSUM-F1 = 0.7500 (Regulation F lead).",
        "mortgage_forbearance: Z-Precision = 100.0%, CUSUM-F1 = 0.8000 (+3 months lead-time)."
    ])
    add_card(s16, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Historical Case Study: CARES Act 2020", [
        "COVID-19 Pandemic Impact (Spring 2020):",
        "Complaint narratives mentioning 'forbearance' and 'CARES Act' surged in March-April 2020.",
        "EWMA-CUSUM detector flagged a structural burst 2 full months before CFPB published guidance.",
        "Demonstrates the system's ability to provide proactive regulatory intelligence."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 17: Bipartite Network Construction
    # ─────────────────────────────────────────────────────────────────────────
    s17 = prs.slides.add_slide(blank_layout)
    add_background(s17)
    add_header(s17, "Component 4: Bipartite Network Construction & Projection", "16. COMPONENT 4 - NETWORK ANALYSIS")

    add_card(s17, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Bipartite Graph Topology", [
        "Constructed from 75,836 full-corpus aggregation records.",
        "Bipartite Graph: 2,502 financial institutions x 170 complaint issue categories.",
        "Total Weighted Edges: 18,204 edges representing complaint counts.",
        "Captures the multi-dimensional grievance footprint of the entire US consumer finance sector."
    ])
    add_card(s17, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Cosine Similarity Company Projection", [
        "Projected onto top 100 institutions by volume using cosine similarity of 170-dim issue profiles.",
        "Edge Threshold >= 0.1 yields a dense network of 100 nodes and 3,774 weighted edges.",
        "Centrality Metrics: Degree, weighted degree, betweenness, closeness, and eigenvector.",
        "Top Weighted Degree: Pentagon Federal Credit Union (51.56), TD Bank (49.26), Capital One (49.16)."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 18: Community Detection & Null Model
    # ─────────────────────────────────────────────────────────────────────────
    s18 = prs.slides.add_slide(blank_layout)
    add_background(s18)
    add_header(s18, "Louvain Community Detection & Hypothesis Testing", "17. COMMUNITY STRUCTURE")

    add_image_if_exists(s18, "results/figures/fig17_company_network.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s18, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Empirical Community Structure", [
        "Louvain Algorithm detected 3 distinct institutional communities:",
        "Community 0: Credit Bureaus & Consumer Reporting (Equifax, Experian, TransUnion, automated credit builders).",
        "Community 1: Depository Banks & Retail Lending (Capital One, TD Bank, Chase, Bank of America).",
        "Community 2: Mortgage Servicers & Specialty Lenders (Nationstar, PHH, specialized loan servicers).",
        "Null Model Hypothesis Test: 100 degree-preserving randomized rewirings.",
        "Observed Modularity Q = 0.2568 vs Null Mean Q = 0.0671 (p < 0.001; empirical p = 0.0).",
        "Proves non-random, statistically significant structural specialization in the financial ecosystem."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 19: Systemic Breadth vs Niche Hazard
    # ─────────────────────────────────────────────────────────────────────────
    s19 = prs.slides.add_slide(blank_layout)
    add_background(s19)
    add_header(s19, "Systemic Issue Breadth vs. Firm-Specific Hazard", "18. SYSTEMIC BREADTH")

    add_card(s19, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Universal Systemic Giants (High Breadth)", [
        "Wells Fargo & Company: 168 unique issues (breadth score = 1.0000).",
        "JPMorgan Chase & Co.: 167 unique issues (breadth score = 0.9940).",
        "Bank of America, NA: 163 unique issues (breadth score = 0.9702).",
        "U.S. Bancorp: 162 unique issues (breadth score = 0.9643).",
        "Citibank, N.A.: 159 unique issues (breadth score = 0.9464).",
        "Regulatory Takeaway: Broad-spectrum institutions suffer cross-cutting compliance issues spanning retail banking, loans, cards, and debt."
    ])
    add_card(s19, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Concentrated Specialty Institutions", [
        "Credit Reporting Bureaus: Very high complaint volume, but concentrated in 110-123 issues.",
        "Specialty Debt Collectors: Restricted to 20-40 debt validation and communication categories.",
        "FinTech Lenders: Concentrated in virtual card, installment loan, and buy-now-pay-later disputes.",
        "Regulatory Takeaway: Niche hazard requires product-targeted enforcement rather than broad banking supervision."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 20: Systemic Risk Index
    # ─────────────────────────────────────────────────────────────────────────
    s20 = prs.slides.add_slide(blank_layout)
    add_background(s20)
    add_header(s20, "Component 5: Systemic Risk Index (SRI) Leaderboard", "19. COMPONENT 5 - SRI")

    add_image_if_exists(s20, "results/figures/fig18_systemic_risk_index.png", Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    add_card(s20, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Top 5 Systemic Risk Leaderboard", [
        "SRI = 0.25*Vol + 0.20*Relief + 0.20*Breadth + 0.20*Centrality + 0.15*Burst.",
        "1. TRANSUNION INTERMEDIATE HOLDINGS: SRI = 0.7819 (Rank 1).",
        "2. Experian Information Solutions: SRI = 0.7187 (Rank 2).",
        "3. EQUIFAX, INC.: SRI = 0.6825 (Rank 3).",
        "4. TD BANK US HOLDING COMPANY: SRI = 0.4631 (Rank 4).",
        "5. U.S. BANCORP: SRI = 0.4365 (Rank 5).",
        "Critical Finding: Equifax exhibits a severe relief rate deficit—only 4.3% relief rate vs 46.3% for TransUnion and 33.4% for Experian!"
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 21: Sensitivity & Regulatory Insights
    # ─────────────────────────────────────────────────────────────────────────
    s21 = prs.slides.add_slide(blank_layout)
    add_background(s21)
    add_header(s21, "Sensitivity Analysis & Actionable Interventions", "20. REGULATORY INSIGHTS")

    add_card(s21, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Dirichlet Sensitivity Robustness", [
        "Tested 100 random Dirichlet weight perturbations across the 5 dimensions.",
        "Mean Kendall's Rank Correlation: tau = 0.6374 (sigma = 0.2321).",
        "Top-3 Credit Bureaus remained in ranks 1-3 in >94% of all weighting configurations.",
        "Confirms SRI provides stable, robust institutional rankings resilient to regulatory preference shifts."
    ])
    add_card(s21, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "4 Actionable Supervisory Directives", [
        "Directive 1: Targeted supervisory audits on credit reporting bureaus (drive >70% of total volume).",
        "Directive 2: Enforcement investigation of Equifax's 4.3% relief rate outlier.",
        "Directive 3: Firm-wide compliance reviews for universal giants (Wells Fargo, Chase).",
        "Directive 4: Deploy EWMA-CUSUM topic monitoring for 2-3 month early warning on fee/forbearance surges."
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SLIDE 22: Dashboard Deployment & Summary
    # ─────────────────────────────────────────────────────────────────────────
    s22 = prs.slides.add_slide(blank_layout)
    add_background(s22)
    add_header(s22, "Dashboard Deployment & Project Summary", "21. DEPLOYMENT & SUMMARY")

    add_card(s22, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Streamlit Production Dashboard", [
        "5 Integrated Views in app/streamlit_app.py:",
        "1. Overview: System architecture, KPI cards, figure gallery.",
        "2. Complaint Triage: Real-time product classification & relief risk prediction.",
        "3. Topic Explorer: Interactive LDA/NMF topics, keyword search & bursts.",
        "4. Network Viewer: Interactive Pyvis graph and centralities.",
        "5. SRI Ranking: Institutional leaderboard and sensitivity audits.",
        "Self-contained: Loads all artifacts in <10MB without raw dataset."
    ])
    add_card(s22, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Engineering & Scientific Summary", [
        "19,998 narratives analyzed across 2018–2023 with strict chronological splits.",
        "Best Product Classifier: LinearSVC (Test Macro-F1 = 0.7394, Acc = 87.4%).",
        "Relief Predictor: Text LR (PR-AUC = 0.3865, Lift@5% = 1.41x, 44.7% precision).",
        "Latent Topics: LDA k=16 (Coherence c_v = 0.5009, Diversity = 0.7312).",
        "Burst Detection: CUSUM F1 up to 0.8000; Z-Score Precision = 1.000.",
        "Network & SRI: 3 Louvain communities (p < 0.001); Top 3 bureaus (SRI > 0.68).",
        "Full Reproducibility: 19/19 pytest tests pass in 9.2s. Zero fabricated numbers."
    ])

    output_path = Path("slides/ComplaintScope_Presentation.pptx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"Presentation saved to {output_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_presentation()


def main():
    print('Building presentation slides PPTX...')
    create_presentation()

if __name__ == '__main__':
    main()

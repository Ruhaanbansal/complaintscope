"""
ComplaintScope — Improved Professional Presentation Generator
White Theme | Content-Driven | With Embedded Figures/Charts/Graphs
24+ Slides | CBS3009 — VIT Vellore
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import copy

BASE = Path(r"c:\Users\Dell\Downloads\complaintscope")
FIG  = BASE / "Deliverables" / "Results_and_Visualizations"
OUT  = BASE / "Deliverables" / "Presentation" / "ComplaintScope_Presentation.pptx"

# ── Colour Palette ─────────────────────────────────────────────────────────────
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK  = RGBColor(0x1A, 0x1A, 0x2E)
C_NAVY   = RGBColor(0x0D, 0x3B, 0x6B)
C_STEEL  = RGBColor(0x1E, 0x5F, 0x9E)
C_ACCENT = RGBColor(0x23, 0x8B, 0xC8)
C_LIGHT  = RGBColor(0xE8, 0xF4, 0xFD)
C_GREY   = RGBColor(0x6C, 0x75, 0x7D)
C_GREEN  = RGBColor(0x19, 0x87, 0x54)
C_ORANGE = RGBColor(0xE6, 0x7E, 0x22)
C_RED    = RGBColor(0xC0, 0x39, 0x2B)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def rect(slide, left, top, width, height, fill=None, line=None, lw=Pt(0)):
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    shp = slide.shapes.add_shape(1,
        Inches(left), Inches(top), Inches(width), Inches(height))
    if fill:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = line; shp.line.width = lw
    else:
        shp.line.fill.background()
    return shp

def tb(slide, text, left, top, width, height,
       size=Pt(13), bold=False, color=C_BLACK,
       align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    txb.word_wrap = wrap
    tf = txb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.size = size; run.font.bold = bold
    run.font.color.rgb = color; run.font.italic = italic
    run.font.name = "Calibri"
    return txb

def para(tf, text, size=Pt(13), bold=False, color=C_BLACK,
         align=PP_ALIGN.LEFT, italic=False, sp=Pt(4)):
    p = tf.add_paragraph(); p.alignment = align; p.space_before = sp
    run = p.add_run(); run.text = text
    run.font.size = size; run.font.bold = bold
    run.font.color.rgb = color; run.font.italic = italic
    run.font.name = "Calibri"
    return p

def header(slide, title, sub=None):
    rect(slide, 0, 0, 13.33, 1.2, fill=C_NAVY)
    rect(slide, 0, 1.2, 13.33, 0.05, fill=C_ACCENT)
    tb(slide, title, 0.4, 0.08, 11.5, 0.72,
       size=Pt(24), bold=True, color=C_WHITE)
    if sub:
        tb(slide, sub, 0.4, 0.73, 11.5, 0.40,
           size=Pt(12), color=RGBColor(0xB8, 0xD4, 0xF0), italic=True)
    tb(slide, "CBS3009 | ComplaintScope | VIT Vellore",
       0.3, 7.12, 12.7, 0.30,
       size=Pt(8), color=C_GREY, align=PP_ALIGN.RIGHT, italic=True)

def kpi(slide, left, top, w, h, value, label, vcol=C_NAVY):
    rect(slide, left, top, w, h, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1.5))
    tb(slide, value, left+0.1, top+0.1, w-0.2, h*0.55,
       size=Pt(26), bold=True, color=vcol, align=PP_ALIGN.CENTER)
    tb(slide, label, left+0.1, top+h*0.57, w-0.2, h*0.4,
       size=Pt(10), color=C_GREY, align=PP_ALIGN.CENTER, wrap=True)

def bullet_box(slide, items, left, top, width, height,
               title=None, icon="▸ ", fsize=Pt(13)):
    txb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    txb.word_wrap = True; tf = txb.text_frame; tf.word_wrap = True
    first = True
    if title:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_before = Pt(2)
        r = p.add_run(); r.text = title
        r.font.size = Pt(15); r.font.bold = True
        r.font.color.rgb = C_NAVY; r.font.name = "Calibri"
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False; p.space_before = Pt(3)
        r = p.add_run(); r.text = icon + item
        r.font.size = fsize; r.font.color.rgb = C_BLACK
        r.font.name = "Calibri"

def img(slide, fname, left, top, width):
    path = FIG / fname
    if path.exists():
        slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(width))
    else:
        rect(slide, left, top, width, 3.0, fill=C_LIGHT, line=C_GREY, lw=Pt(0.5))
        tb(slide, f"[{fname}]", left+0.1, top+1.3, width-0.2, 0.5,
           size=Pt(9), color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

def section_divider(slide, section_num, section_title, section_desc):
    rect(slide, 0, 0, 13.33, 7.5, fill=C_NAVY)
    rect(slide, 0, 3.5, 13.33, 0.06, fill=C_ACCENT)
    tb(slide, f"Section {section_num}", 1.0, 1.8, 11.3, 0.6,
       size=Pt(16), color=RGBColor(0xB8, 0xD4, 0xF0), align=PP_ALIGN.CENTER, italic=True)
    tb(slide, section_title, 1.0, 2.5, 11.3, 1.2,
       size=Pt(36), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    tb(slide, section_desc, 1.0, 4.0, 11.3, 0.8,
       size=Pt(14), color=RGBColor(0xB8, 0xD4, 0xF0), italic=True, align=PP_ALIGN.CENTER)
    tb(slide, "CBS3009 | ComplaintScope | VIT Vellore",
       0.3, 7.12, 12.7, 0.30, size=Pt(8), color=RGBColor(0x55, 0x65, 0x80),
       align=PP_ALIGN.RIGHT, italic=True)

def add_table(slide, headers, rows, left, top, width, height,
              col_widths=None):
    """Add a formatted table to slide."""
    n_cols = len(headers)
    n_rows = len(rows)
    total_w = Inches(width)
    total_h = Inches(height)
    row_h   = total_h / (n_rows + 1)

    if col_widths is None:
        col_widths = [width / n_cols] * n_cols

    # Header row
    cum_x = left
    for j, (h, cw) in enumerate(zip(headers, col_widths)):
        rect(slide, cum_x, top, cw - 0.02, height/(n_rows+1), fill=C_NAVY)
        tb(slide, h, cum_x+0.05, top+0.04, cw-0.12, height/(n_rows+1)-0.08,
           size=Pt(10), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        cum_x += cw

    # Data rows
    for i, row in enumerate(rows):
        row_top = top + height/(n_rows+1) * (i+1)
        bg = C_LIGHT if i % 2 == 0 else C_WHITE
        cum_x = left
        for j, (val, cw) in enumerate(zip(row, col_widths)):
            rect(slide, cum_x, row_top, cw-0.02, height/(n_rows+1)-0.01,
                 fill=bg, line=RGBColor(0xCE, 0xD4, 0xDA), lw=Pt(0.3))
            aln = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            bold = (i == 0 and "★" in str(val))
            col = C_NAVY if j == 0 else C_BLACK
            if "★" in str(val):
                col = C_GREEN
            tb(slide, str(val), cum_x+0.06, row_top+0.04, cw-0.14,
               height/(n_rows+1)-0.12, size=Pt(9), bold=bold, color=col, align=aln)
            cum_x += cw


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
rect(slide, 0, 0, 13.33, 2.6, fill=C_NAVY)
rect(slide, 0, 2.6, 13.33, 0.07, fill=C_ACCENT)

tb(slide, "ComplaintScope", 0.5, 0.20, 12.3, 1.15,
   size=Pt(56), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
tb(slide, "An End-to-End Text, Topic & Network Analytics System\nfor Consumer-Complaint Triage and Systemic Risk Early Warning",
   0.5, 1.25, 12.3, 1.2,
   size=Pt(16), color=RGBColor(0xB8, 0xD4, 0xF0), italic=True, align=PP_ALIGN.CENTER)

rect(slide, 1.8, 2.9, 9.73, 3.65, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
info = [
    ("Course:",   "CBS3009 – Advanced Social, Text and Media Analytics"),
    ("Team:",     "Ruhaan Bansal (23BBS0046)  |  Vedant Rajesh (23BBS0037)  |  Anish Desai (23BBS0119)"),
    ("Faculty:",  "Prof. Sathish Kumar K"),
    ("Institute:","Vellore Institute of Technology (VIT), Vellore"),
    ("Date:",     "October 2026"),
    ("Marks:",    "20 Marks — CO5 & CO6"),
]
for i, (lbl, val) in enumerate(info):
    y = 3.05 + i * 0.52
    tb(slide, lbl, 2.1, y, 1.6, 0.45, size=Pt(12), bold=True, color=C_NAVY)
    tb(slide, val, 3.75, y, 7.5, 0.45, size=Pt(12), color=C_BLACK)

tb(slide, "CBS3009 | ComplaintScope | VIT Vellore", 0.3, 7.12, 12.7, 0.30,
   size=Pt(8), color=C_GREY, align=PP_ALIGN.RIGHT, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Presentation Agenda", "A structured walkthrough from problem to deployed solution")

sections = [
    ("01", "Problem Statement & Motivation",   "Why does this project exist?"),
    ("02", "Dataset & Methodology",            "CFPB data, filtering, preprocessing, feature engineering"),
    ("03", "Component 1: Product Classification","9-class triage system — Models, Results, Drift Analysis"),
    ("04", "Component 2: Relief-Risk Prediction","Probability scoring & triage queue simulation"),
    ("05", "Component 3a: Topic Discovery",    "LDA vs NMF vs K-Means — coherence sweep & themes"),
    ("06", "Component 3b: Burst Detection",    "Dual-engine early-warning system — CUSUM & Z-Score"),
    ("07", "Components 4 & 5: Network & SRI",  "Institutional risk network & Systemic Risk Index"),
    ("08", "Results, Discussion & Conclusions","Key findings, limitations, future work"),
    ("09", "Interactive Dashboard & Deployment","Streamlit 5-page app demo"),
    ("10", "References",                        "Academic sources and citations"),
]
for i, (num, title, desc) in enumerate(sections):
    col = i % 2; row = i // 2
    lx = 0.4 + col * 6.47; ty = 1.38 + row * 1.18
    rect(slide, lx, ty, 6.17, 1.02, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
    tb(slide, num, lx+0.10, ty+0.05, 0.65, 0.52,
       size=Pt(22), bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)
    tb(slide, title, lx+0.82, ty+0.06, 5.1, 0.40,
       size=Pt(13), bold=True, color=C_NAVY)
    tb(slide, desc, lx+0.82, ty+0.54, 5.1, 0.40,
       size=Pt(10), color=C_GREY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM STATEMENT
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Problem Statement", "The CFPB receives 5,000–10,000 consumer financial complaints every weekday")

tb(slide, "The US Consumer Financial Protection Bureau (CFPB) maintains the world's largest public database of "
   "financial grievances. Consumer narratives within this database encode critical regulatory intelligence — "
   "yet manual triage at this scale is impossible. Four critical bottlenecks demand automation:",
   0.5, 1.30, 12.3, 0.72, size=Pt(12), color=C_BLACK, italic=True)

problems = [
    ("🗂️  Triage Bottleneck",
     "5,000–10,000 complaints arrive daily. Manual routing to product specialists takes 3–8 min each, "
     "is inconsistent across reviewers, and error-prone at category boundaries (credit reporting vs. debt collection)."),
    ("⚠️  Relief Risk Blindness",
     "Only 16.3% of complaints result in consumer relief. Without predictive scoring, caseworkers review "
     "complaints in random order—systematically missing high-priority cases."),
    ("📡  Late Crisis Detection",
     "Emerging fraud schemes and regulatory crises (e.g., COVID-19 forbearance disputes) appear in complaint "
     "narratives months before official enforcement actions. Manual trend analysis is far too slow."),
    ("🕸️  Systemic Risk Blind Spots",
     "Individual case review misses institution-wide complaint patterns and cross-institutional networks of "
     "shared regulatory issues—invisible to complaint-by-complaint analysis."),
]
for i, (title, desc) in enumerate(problems):
    ty = 2.18 + i * 1.18
    rect(slide, 0.4, ty, 12.5, 1.05, fill=C_LIGHT, line=C_NAVY, lw=Pt(1.5))
    tb(slide, title, 0.6, ty+0.08, 3.8, 0.42, size=Pt(14), bold=True, color=C_NAVY)
    tb(slide, desc,  0.6, ty+0.52, 12.0, 0.48, size=Pt(11.5), color=C_BLACK)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — SOLUTION ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "ComplaintScope: System Architecture",
       "Five analytical engines transforming unstructured complaints into actionable regulatory intelligence")

# Pipeline flow boxes
pipeline = [
    ("Raw CFPB Data\n878K Narratives", "Layer 1\nIngestion"),
    ("19,998 Clean\nNarratives", "Layer 2\nFiltering"),
    ("TF-IDF + MiniLM\nEmbeddings", "Layer 3–4\nPreprocessing\n& Features"),
    ("5 Analytical\nEngines", "Layer 5\nAnalysis"),
    ("Streamlit\nDashboard", "Layer 6\nDeployment"),
]
for i, (main, sub) in enumerate(pipeline):
    lx = 0.35 + i * 2.55
    rect(slide, lx, 1.38, 2.35, 1.48, fill=C_NAVY if i % 2 == 0 else C_STEEL)
    tb(slide, main, lx+0.1, 1.42, 2.15, 0.82,
       size=Pt(12), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    tb(slide, sub,  lx+0.1, 2.22, 2.15, 0.58,
       size=Pt(9), color=RGBColor(0xB8, 0xD4, 0xF0), italic=True, align=PP_ALIGN.CENTER)
    if i < 4:
        tb(slide, "→", lx+2.35, 1.85, 0.2, 0.55,
           size=Pt(22), bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)

# 5 Components
components = [
    ("Component 1", "Product\nClassification", "9-class NLP Triage\nMacro-F1 = 0.7394\nAccuracy = 87.43%", C_NAVY),
    ("Component 2", "Relief-Risk\nPrediction", "Binary Risk Scoring\nPR-AUC = 0.3865\nLift@5% = 1.41×", C_STEEL),
    ("Component 3a", "Topic\nDiscovery", "LDA k=16\nC_V = 0.5009\n16 Complaint Themes", C_NAVY),
    ("Component 3b", "Burst\nDetection", "EWMA-CUSUM\nF1 = 0.8000\n+2–3 months lead", C_STEEL),
    ("Comps. 4–5", "Network\nAnalysis + SRI", "Q=0.2568, p<0.001\nTop SRI = 0.7819\n3 Institutions Flagged", C_NAVY),
]
for i, (comp, name, result, col) in enumerate(components):
    lx = 0.35 + i * 2.55
    rect(slide, lx, 3.15, 2.35, 3.8, fill=C_LIGHT, line=col, lw=Pt(2))
    rect(slide, lx, 3.15, 2.35, 0.45, fill=col)
    tb(slide, comp, lx+0.1, 3.18, 2.15, 0.38,
       size=Pt(10), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER, italic=True)
    tb(slide, name, lx+0.1, 3.65, 2.15, 0.72,
       size=Pt(14), bold=True, color=col, align=PP_ALIGN.CENTER)
    tb(slide, result, lx+0.1, 4.40, 2.15, 1.60,
       size=Pt(11), color=C_BLACK, align=PP_ALIGN.CENTER)
    # Arrow up to pipeline
    tb(slide, "↑", lx+1.0, 2.86, 0.4, 0.28,
       size=Pt(16), bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — DATA: CFPB SOURCE & FILTERING FUNNEL
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Dataset: CFPB Consumer Complaint Database",
       "The world's largest public financial grievance dataset — CC0 Public Domain")

# Left: Key stats
kpi(slide, 0.35, 1.35, 2.8, 1.4, ">8 Million",  "Total CFPB complaints\n(as of 2026)")
kpi(slide, 0.35, 2.88, 2.8, 1.4, "878,262",      "Complaints with\nconsumer narratives")
kpi(slide, 0.35, 4.41, 2.8, 1.4, "19,998",       "Final filtered study\ncorpus (2018–2023)", vcol=C_GREEN)

# Right: The figure
img(slide, "fig_01_funnel.png", 3.40, 1.32, 5.8)

# Far right: Filtering steps
rect(slide, 9.45, 1.32, 3.68, 5.55, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
tb(slide, "7-Stage Filtering Pipeline", 9.55, 1.38, 3.50, 0.38,
   size=Pt(12), bold=True, color=C_NAVY)
stages = [
    "1. All CFPB records: >8M",
    "2. Non-null narratives: 878K",
    "3. Date: 2018–2023",
    "4. Length ≥ 20 tokens",
    "5. SHA-256 deduplicate −131K",
    "6. Definite relief labels only",
    "7. Stratified sample → 19,998",
]
txb = slide.shapes.add_textbox(Inches(9.55), Inches(1.85), Inches(3.45), Inches(4.8))
txb.word_wrap = True; tf = txb.text_frame; tf.word_wrap = True
for i, s in enumerate(stages):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_before = Pt(3)
    r = p.add_run()
    r.text = s
    r.font.size = Pt(11); r.font.name = "Calibri"
    r.font.color.rgb = C_NAVY if i == 6 else C_BLACK
    r.font.bold = (i == 6)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — EDA: TEMPORAL TRENDS & CLASS DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Exploratory Data Analysis",
       "Understanding the complaint corpus: temporal trends, class imbalance, and narrative characteristics")

img(slide, "fig_02_monthly_volume.png",  0.35, 1.35, 6.0)
img(slide, "fig_03_product_distribution.png", 6.55, 1.35, 6.45)

img(slide, "fig_04_narrative_length.png", 0.35, 4.35, 6.0)
img(slide, "fig_05_relief_rate_by_product.png", 6.55, 4.35, 6.45)

# Caption row
captions = [
    (0.35, "Fig: Monthly complaint volume (2018–2023). COVID-19 surge clearly visible in 2020–2021."),
    (6.55, "Fig: 9-class product distribution. Credit Reporting = 51.2% (severe imbalance)."),
]
for lx, cap in captions:
    tb(slide, cap, lx, 4.18, 6.0, 0.20, size=Pt(8), color=C_GREY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — CHRONOLOGICAL SPLIT & TEMPORAL STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Chronological Data Partitioning",
       "The single most critical methodological decision — preventing temporal data leakage")

img(slide, "fig_06_split_timeline.png", 0.35, 1.35, 7.8)

rect(slide, 8.45, 1.35, 4.58, 5.72, fill=C_LIGHT, line=C_NAVY, lw=Pt(1.5))
tb(slide, "Why Chronological Splits?", 8.60, 1.43, 4.30, 0.42,
   size=Pt(13), bold=True, color=C_NAVY)

reasons = [
    "Financial complaint language is non-stationary — it evolves with new products, regulations, and events",
    "COVID-19, CARES Act, and new fintech products create novel terminology in 2020–2023",
    "Random splits leak future terms into training data → artificially inflated accuracy",
    "AQ3 Evidence: Random split = 0.9330 F1 vs. Chronological = 0.7317 F1 (Δ = −20.13 pp)",
    "Any CFPB complaint classifier evaluated with random splits overstates real performance by ~20 pp",
]
txb = slide.shapes.add_textbox(Inches(8.60), Inches(1.92), Inches(4.25), Inches(4.9))
txb.word_wrap = True; tf = txb.text_frame; tf.word_wrap = True
for i, r_text in enumerate(reasons):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_before = Pt(5)
    r = p.add_run()
    r.text = "▸ " + r_text
    r.font.size = Pt(11); r.font.name = "Calibri"
    r.font.color.rgb = C_RED if "AQ3" in r_text else C_BLACK
    r.font.bold = ("AQ3" in r_text)

tb(slide, "Split Summary:", 0.35, 5.35, 7.5, 0.35, size=Pt(11), bold=True, color=C_NAVY)
split_hdrs = ["Split", "Records", "Date Range"]
split_rows = [
    ("Train (70%)", "13,983", "2018-07-19 → 2022-03-17"),
    ("Val (15%)",   "2,999",  "2022-03-18 → 2022-08-12"),
    ("Test (15%)",  "3,016",  "2022-08-13 → 2023-01-26"),
]
add_table(slide, split_hdrs, split_rows, 0.35, 5.75, 7.8, 1.50,
          col_widths=[1.8, 1.8, 4.2])


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — PREPROCESSING & ABLATION STUDY
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Text Preprocessing & Ablation Study (AQ4)",
       "Every preprocessing decision is empirically justified — not assumed")

img(slide, "fig_nb02_ablation.png", 0.35, 1.35, 6.2)

rect(slide, 6.75, 1.35, 6.25, 5.72, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
tb(slide, "Ablation Results (7 Configurations)", 6.90, 1.43, 5.95, 0.42,
   size=Pt(13), bold=True, color=C_NAVY)

configs = [
    ("★ No Redaction (remove XXXX)", "0.5140", "+1.49pp", True),
    ("Baseline (placeholder tokens)", "0.4991", "—", False),
    ("No Lowercasing", "0.4978", "−0.13pp", False),
    ("No Negation Preservation", "0.4976", "−0.15pp", False),
    ("No Lemmatisation", "0.4635", "−3.56pp", False),
    ("No Stopword Removal", "0.4236", "−7.55pp", False),
    ("Minimal (raw lowercase only)", "0.4203", "−7.88pp", False),
]
for i, (cfg, f1, delta, champ) in enumerate(configs):
    ty = 1.95 + i * 0.72
    bg = RGBColor(0xE8, 0xF8, 0xEE) if champ else (C_WHITE if i % 2 else RGBColor(0xF0, 0xF4, 0xF8))
    rect(slide, 6.80, ty, 5.85, 0.66, fill=bg, line=RGBColor(0xCE, 0xD4, 0xDA), lw=Pt(0.3))
    tb(slide, ("★ " if champ else "   ") + cfg, 6.88, ty+0.10, 3.60, 0.46,
       size=Pt(10), bold=champ, color=C_GREEN if champ else C_BLACK)
    tb(slide, f1, 10.52, ty+0.10, 0.70, 0.46, size=Pt(10), bold=champ,
       color=C_GREEN if champ else C_NAVY, align=PP_ALIGN.CENTER)
    tb(slide, delta, 11.28, ty+0.10, 1.30, 0.46, size=Pt(10),
       color=C_GREEN if champ else (C_RED if "−" in delta else C_GREY),
       align=PP_ALIGN.CENTER)

tb(slide, "Key Takeaway: Stopword removal (+7.55pp) and lemmatisation (+3.56pp) are the two most critical "
   "preprocessing steps. Negation preservation prevents semantic inversion in dispute sentences.",
   6.80, 7.05, 6.20, 0.38, size=Pt(10), color=C_NAVY, bold=True, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Feature Engineering",
       "Three complementary representations — ALL fitted strictly on training data only")

img(slide, "fig07_zipf_distribution.png", 0.35, 1.35, 5.0)

features = [
    ("Sublinear TF-IDF",
     "30,000 features, bigrams (1–2)\nSublinear tf = 1 + log(tf)\nZipf α≈1.05 justifies dampening\nFor: Classification & Relief"),
    ("MiniLM-L6-v2 Embeddings",
     "384-dim dense vectors\nPre-trained on 1B+ sentence pairs\nL2-normalised, cached to .npy\nFor: kNN Retrieval & Classification"),
    ("Bag of Words",
     "30,000 features, raw counts\nBigrams (1–2), min_df=2\nNo IDF weighting\nFor: Naïve Bayes baselines"),
    ("Operational Metadata",
     "One-hot: channel, tags, state\nCompany ID EXCLUDED (prevents drift)\nAblation shows company overfits\nFor: Relief Prediction experiment"),
]
for i, (name, desc) in enumerate(features):
    col = i % 2; row = i // 2
    lx = 5.55 + col * 3.85; ty = 1.38 + row * 2.85
    rect(slide, lx, ty, 3.70, 2.62, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1.5))
    rect(slide, lx, ty, 3.70, 0.46, fill=C_STEEL)
    tb(slide, name, lx+0.15, ty+0.07, 3.40, 0.32,
       size=Pt(13), bold=True, color=C_WHITE)
    tb(slide, desc, lx+0.15, ty+0.55, 3.40, 1.98,
       size=Pt(11), color=C_BLACK)

tb(slide, "P@k Retrieval (MiniLM embeddings): P@1=80.2%  P@3=91.9%  P@5=94.3%  P@10=96.7%",
   5.55, 7.12, 7.55, 0.32, size=Pt(10), bold=True, color=C_NAVY)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — SECTION DIVIDER: CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
section_divider(slide, "01", "Product Classification",
                "9-Class Complaint Routing — Benchmark Results & Temporal Concept Drift Analysis")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — CLASSIFICATION RESULTS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 1: Product Classification Benchmark",
       "9 models trained on identical chronological splits — champion selected by Validation Macro-F1")

hdrs = ["Model", "Val F1", "Test F1", "Test Acc", "95% Bootstrap CI"]
rows = [
    ("★ LinearSVC (Calibrated) ← Champion", "0.7349", "0.7394", "87.43%", "[0.708, 0.767]"),
    ("LogisticRegression (Val-Tuned)",      "0.7171", "0.7319", "87.27%", "[0.698, 0.761]"),
    ("MiniLM-L6-v2 + LR",                  "0.7157", "0.7002", "85.68%", "[0.668, 0.730]"),
    ("LogisticRegression (Default)",        "0.6644", "0.7054", "87.30%", "[0.667, 0.734]"),
    ("ComplementNB",                        "0.6264", "0.6457", "85.48%", "[0.617, 0.673]"),
    ("MultinomialNB",                       "0.6206", "0.6218", "84.85%", "[0.592, 0.647]"),
    ("DecisionTree (depth=10)",             "0.5070", "0.4765", "77.25%", "[0.445, 0.505]"),
    ("Dummy (Stratified Baseline)",         "0.0923", "0.0950", "31.07%", "[0.086, 0.105]"),
]
add_table(slide, hdrs, rows, 0.35, 1.35, 12.65, 4.70,
          col_widths=[4.50, 1.65, 1.65, 1.70, 3.15])

kpi(slide, 0.35, 6.15, 3.0, 1.18, "0.7394", "Test Macro-F1\n(Champion LinearSVC)", vcol=C_GREEN)
kpi(slide, 3.65, 6.15, 3.0, 1.18, "87.43%", "Test Accuracy\n(Champion)", vcol=C_NAVY)
kpi(slide, 6.95, 6.15, 3.0, 1.18, "χ²=535.64\np<10⁻¹¹⁸", "McNemar Significance\nvs. Baseline", vcol=C_NAVY)
kpi(slide, 10.0, 6.15, 3.0, 1.18, "20/20", "Automated Tests\nPassing ✓", vcol=C_GREEN)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — CONFUSION MATRIX & CLASS TERMS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Classification Results: Confusion Matrix & Top Terms (AQ1)",
       "Primary error boundary: Credit Reporting ↔ Debt Collection (31.7% of all misclassifications)")

img(slide, "fig10_confusion_matrix.png", 0.35, 1.35, 6.3)
img(slide, "fig08_class_top_terms.png",  6.85, 1.35, 6.15)

tb(slide, "Error Analysis: Credit Reporting ↔ Debt Collection confusion arises because third-party debt collectors "
   "routinely threaten credit bureau filings as enforcement tactics, creating overlapping lexical signatures in both categories.",
   0.35, 7.05, 12.65, 0.38, size=Pt(10), color=C_NAVY, bold=True, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — TEMPORAL CONCEPT DRIFT
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Temporal Concept Drift Analysis (AQ3)",
       "Why random train/test splits are dangerously misleading for financial NLP models")

kpi(slide, 0.35, 1.38, 3.85, 2.00, "0.9330",
    "Macro-F1\nRandom Split\n(data-leaking — INVALID)", vcol=C_GREY)
kpi(slide, 4.55, 1.38, 3.85, 2.00, "0.7317",
    "Macro-F1\nChronological Split\n(honest evaluation)", vcol=C_NAVY)
kpi(slide, 8.75, 1.38, 4.25, 2.00, "−20.13 pp",
    "Absolute Performance Drop\n(Temporal Concept Drift)\nΔ = −0.2013", vcol=C_RED)

tb(slide, "What this means — and why it matters:",
   0.35, 3.58, 12.65, 0.42, size=Pt(14), bold=True, color=C_NAVY)

implications = [
    "Random k-fold cross-validation would report 93.3% Macro-F1 — a dangerously overconfident and misleading estimate",
    "Real production performance is only 73.2% Macro-F1 — 20 percentage points lower than what random splits show",
    "The gap is caused by temporal concept drift: COVID-19 terminology, CARES Act language, and new fintech products post-2022",
    "Operational implication: Any deployed CFPB complaint classifier MUST be retrained every 6 months to maintain accuracy",
    "Academic implication: Prior CFPB NLP papers reporting >90% accuracy with random splits are systematically overstating performance",
]
for i, impl in enumerate(implications):
    ty = 4.12 + i * 0.56
    bg = RGBColor(0xFD, 0xED, 0xEA) if i in [0, 4] else (C_LIGHT if i % 2 == 0 else C_WHITE)
    rect(slide, 0.35, ty, 12.65, 0.50, fill=bg, line=C_ACCENT, lw=Pt(0.5))
    tb(slide, "▸  " + impl, 0.52, ty+0.06, 12.35, 0.38, size=Pt(12), color=C_BLACK)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — SECTION DIVIDER: RELIEF PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
section_divider(slide, "02", "Relief-Risk Prediction",
                "Prioritising the 16.3% of complaints that result in consumer remediation")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — RELIEF PREDICTION RESULTS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 2: Relief-Risk Prediction & Triage Simulation (AQ2 & AQ7)",
       "Predicting consumer relief probability to prioritise investigator workload")

tb(slide, "relief = 1: 'Closed with monetary/non-monetary relief'  |  Base rate = 16.3%  |  Class weight ratio = 5.15:1  |  Metric: PR-AUC (class-imbalance robust)",
   0.35, 1.30, 12.65, 0.38, size=Pt(11), color=C_GREY, italic=True)

img(slide, "fig12_pr_curve.png",    0.35, 1.75, 4.55)
img(slide, "fig13_triage_gain.png", 5.10, 1.75, 4.55)

rect(slide, 9.88, 1.75, 3.10, 5.55, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
tb(slide, "Triage Simulation", 10.0, 1.82, 2.80, 0.42, size=Pt(12), bold=True, color=C_NAVY)
triage_facts = [
    ("Random review rate:", "16.3%\n(base rate)"),
    ("Top 5% audit queue:", "44.67% precision\n1.41× lift"),
    ("Top 20% audit queue:", "Captures 24.48%\nof ALL relief cases"),
    ("Brier Score:", "0.2316\n(well-calibrated)"),
    ("PR-AUC 95% CI:", "[0.359, 0.415]"),
]
for i, (lbl, val) in enumerate(triage_facts):
    ty = 2.35 + i * 1.0
    tb(slide, lbl, 9.95, ty, 1.55, 0.40, size=Pt(10), bold=True, color=C_STEEL)
    tb(slide, val, 9.95, ty+0.38, 2.80, 0.52, size=Pt(11), color=C_NAVY, bold=True)

r_hdrs = ["Model", "PR-AUC", "ROC-AUC", "Prec@5%", "Lift@5%"]
r_rows = [
    ("★ Text LR (Champion)", "0.3865", "0.6063", "44.67%", "1.41×"),
    ("Text + Meta LR",       "0.3796", "0.6023", "40.00%", "1.26×"),
    ("HistGradientBoosting", "0.3780", "0.5929", "44.00%", "1.39×"),
    ("Prior-Rate Baseline",  "0.3170", "0.5000", "34.00%", "1.07×"),
]
add_table(slide, r_hdrs, r_rows, 0.35, 5.48, 9.30, 1.85,
          col_widths=[3.60, 1.50, 1.55, 1.55, 1.10])


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — SECTION DIVIDER: TOPIC DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
section_divider(slide, "03", "Topic Discovery",
                "What hidden complaint themes exist in 19,998 narratives? — LDA, NMF & K-Means benchmarked")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — LDA TOPIC MODEL RESULTS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 3a: Topic Discovery — LDA Coherence Sweep",
       "k ∈ {8, 12, 16, 20, 24} evaluated for LDA, NMF, and K-Means on dense embeddings")

img(slide, "fig14_lda_coherence_sweep.png", 0.35, 1.35, 6.2)
img(slide, "fig15_topic_product_heatmap.png", 6.75, 1.35, 6.25)

kpi(slide, 0.35, 6.15, 2.8, 1.18, "k = 16", "Optimal Topics\n(LDA)", vcol=C_NAVY)
kpi(slide, 3.35, 6.15, 2.8, 1.18, "0.5009", "C_V Coherence\n(semantic quality)", vcol=C_NAVY)
kpi(slide, 6.35, 6.15, 2.8, 1.18, "0.7312", "Topic Diversity\n(non-redundancy)", vcol=C_NAVY)
kpi(slide, 9.35, 6.15, 3.65, 1.18, "K-Means Failed\n0.021–0.026", "Silhouette Score\n(too low to use)", vcol=C_RED)

tb(slide, "Heatmap confirms semantic validity: discovered topics map specifically to known CFPB product categories (e.g., Topic 3 = Mortgage only; Topic 0 = Credit Reporting only).",
   0.35, 7.08, 12.65, 0.35, size=Pt(10), color=C_NAVY, bold=True, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — 16 DISCOVERED TOPICS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "16 Discovered Complaint Themes",
       "LDA k=16 reveals interpretable regulatory complaint categories beyond CFPB's official taxonomy")

topics = [
    ("T0",  "Credit Bureau\nDisputes",         "credit, report, dispute, bureau"),
    ("T1",  "Debt Collection\nHarassment",      "debt, collection, validate, call"),
    ("T2",  "Student Loan\nServicing",          "loan, student, servicer, federal"),
    ("T3",  "Mortgage\nForbearance",            "mortgage, forbearance, escrow"),
    ("T4",  "Payday & High-\nInterest Lending", "payday, interest, lender, fee"),
    ("T5",  "Identity Theft\n& Fraud",          "identity, theft, fraud, police"),
    ("T6",  "Checking Account\nOverdrafts",     "account, overdraft, bank, fee"),
    ("T7",  "Credit Card\nBilling",             "card, charge, dispute, merchant"),
    ("T8",  "Auto Loan\nRepossession",          "vehicle, repossess, auto, loan"),
    ("T9",  "Foreclosure\n& Property",          "foreclosure, escrow, servicer"),
    ("T10", "Consumer Rights\n& Communication", "contact, cease, right, letter"),
    ("T11", "Personal Data\n& Privacy",         "information, personal, data, share"),
    ("T12", "Credit Inquiry\n& Application",    "inquiry, hard pull, approve"),
    ("T13", "Wire Transfer\n& Money Services",  "transfer, wire, money, send"),
    ("T14", "Account Closure\n& Funds Access",  "account, close, fund, hold"),
    ("T15", "COVID Relief\n& Stimulus",         "covid, stimulus, relief, deferral"),
]
for i, (tid, label, kwords) in enumerate(topics):
    col = i % 8; row = i // 8
    lx = 0.32 + col * 1.60; ty = 1.38 + row * 2.7
    accent = C_NAVY if row == 0 else C_STEEL
    rect(slide, lx, ty, 1.52, 2.45, fill=C_LIGHT, line=accent, lw=Pt(1))
    rect(slide, lx, ty, 1.52, 0.36, fill=accent)
    tb(slide, tid, lx+0.06, ty+0.05, 1.40, 0.26,
       size=Pt(10), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    tb(slide, label, lx+0.06, ty+0.42, 1.40, 1.0,
       size=Pt(10), bold=True, color=accent, align=PP_ALIGN.CENTER)
    tb(slide, kwords, lx+0.06, ty+1.46, 1.40, 0.88,
       size=Pt(8.5), color=C_GREY, italic=True, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — SECTION DIVIDER: BURST DETECTION
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
section_divider(slide, "04", "Burst Detection",
                "Dual-Engine Early-Warning System — Detecting crises 2–3 months before they peak")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — BURST DETECTION MECHANICS & RESULTS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 3b: Emerging-Issue Burst Detection (AQ5)",
       "Validated against 5 pre-registered keyword-proxy ground truths — 2–3 month early-warning lead time")

# Two detectors
rect(slide, 0.35, 1.35, 5.8, 2.3, fill=C_LIGHT, line=C_NAVY, lw=Pt(1.5))
tb(slide, "Detector A: Rolling Z-Score", 0.50, 1.42, 5.50, 0.42,
   size=Pt(13), bold=True, color=C_NAVY)
tb(slide, "Formula: z_t = (x_t − μ_{t−12:t−1}) / σ_{t−12:t−1}\n"
   "Window: 12-month trailing baseline\nAlert threshold: z > 2.0σ\n"
   "Strength: Ultra-high precision (100% on overdraft & mortgage forbearance)\n"
   "Use case: Immediate sharp-spike alerts",
   0.50, 1.90, 5.60, 1.65, size=Pt(11), color=C_BLACK)

rect(slide, 6.45, 1.35, 6.55, 2.3, fill=C_LIGHT, line=C_STEEL, lw=Pt(1.5))
tb(slide, "Detector B: EWMA-CUSUM Control Chart", 6.60, 1.42, 6.20, 0.42,
   size=Pt(13), bold=True, color=C_STEEL)
tb(slide, "EWMA span = 6 months  |  CUSUM threshold h = 4.0\n"
   "S_t = max(0, S_{t−1} + (x_t − EWMA_t))\n"
   "Strength: Detects slow-burning multi-month regulatory escalations\n"
   "Achieves F1 = 0.8000 (Mortgage Forbearance), 0.7568 (COVID-19)\n"
   "Use case: Policy preparation with 2–3 month lead time",
   6.60, 1.90, 6.30, 1.65, size=Pt(11), color=C_BLACK)

img(slide, "fig16_topic_burst_detection.png", 0.35, 3.80, 7.8)

# Validation table on right
rect(slide, 8.40, 3.80, 4.60, 3.55, fill=C_LIGHT, line=C_ACCENT, lw=Pt(1))
tb(slide, "Validation Results (5 Proxies)", 8.55, 3.87, 4.30, 0.38,
   size=Pt(12), bold=True, color=C_NAVY)
results = [
    ("COVID-19 Relief", "0.24", "0.757", "+2 mo"),
    ("Overdraft Fees",  "0.35", "0.250", "≈0"),
    ("Credit Disputes", "0.22", "0.703", "3yr drift"),
    ("Debt Coll. Reg F","0.38", "0.750", "+1 mo"),
    ("Mortgage Forbear.","0.25","0.800", "+3 mo"),
]
hdrs_b = ["Proxy", "Z F1", "CUSUM F1", "Lead"]
add_table(slide, hdrs_b, results, 8.45, 4.35, 4.50, 2.90,
          col_widths=[1.60, 0.85, 1.10, 0.95])


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 21 — SECTION DIVIDER: NETWORK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
section_divider(slide, "05", "Network Analysis & Systemic Risk Index",
                "Bipartite Institutional Graph Projection → Louvain Community Detection → Composite SRI")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 22 — NETWORK GRAPH & COMMUNITY DETECTION (AQ6)
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 4: Bipartite Network Analysis & Community Detection (AQ6)",
       "2,502 institutions × 170 CFPB issues → projected co-occurrence network → Louvain communities")

img(slide, "fig17_company_network.png", 0.35, 1.35, 7.5)

rect(slide, 8.10, 1.35, 4.90, 5.72, fill=C_LIGHT, line=C_NAVY, lw=Pt(1.5))
tb(slide, "Network Metrics", 8.25, 1.42, 4.60, 0.42, size=Pt(13), bold=True, color=C_NAVY)

net_stats = [
    ("Bipartite nodes:", "2,502 companies + 170 issues"),
    ("Bipartite edges:", "18,204 weighted"),
    ("Projected nodes:", "Top-100 institutions"),
    ("Projected edges:", "3,774 (Jaccard sim ≥ 0.1)"),
    ("Communities:", "3 (Louvain algorithm)"),
    ("Modularity Q:", "0.2568"),
    ("Null model Q̄:", "0.0671 ± 0.0084"),
    ("Significance:", "p = 0.000 (< 0.001)"),
]
txb = slide.shapes.add_textbox(Inches(8.25), Inches(1.92), Inches(4.60), Inches(3.80))
tf = txb.text_frame; tf.word_wrap = True
for i, (k, v) in enumerate(net_stats):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_before = Pt(5)
    r1 = p.add_run(); r1.text = k + " "; r1.font.bold = True; r1.font.size = Pt(10)
    r1.font.color.rgb = C_NAVY; r1.font.name = "Calibri"
    r2 = p.add_run(); r2.text = v; r2.font.size = Pt(10)
    r2.font.color.rgb = C_BLACK if "0.000" not in v else C_GREEN
    r2.font.bold = ("0.000" in v or "0.2568" in v)
    r2.font.name = "Calibri"

communities = [
    (C_NAVY,  "Community 0 (Blue)", "Credit bureaus & FinTech credit builders\nTransUnion, Experian, Equifax"),
    (C_STEEL, "Community 1 (Orange)","Mega-banks & consumer lenders\nJPMorgan, Wells Fargo, BofA"),
    (RGBColor(0x19, 0x87, 0x54), "Community 2 (Green)", "Mortgage servicers & specialty lenders\nNationstar, Ocwen, Freedom"),
]
for i, (col, name, desc) in enumerate(communities):
    ty = 5.85 + i * 0.0  # stack horizontally
    lx = 8.10 + i * 1.60
    rect(slide, lx, 5.88, 1.55, 1.12, fill=C_LIGHT, line=col, lw=Pt(2))
    tb(slide, name, lx+0.08, 5.92, 1.40, 0.34, size=Pt(9), bold=True, color=col)
    tb(slide, desc, lx+0.08, 6.30, 1.40, 0.64, size=Pt(8.5), color=C_BLACK)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 23 — SYSTEMIC RISK INDEX
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Component 5: Composite Systemic Risk Index (SRI)",
       "5-dimension normalised risk ranking — robust to weight variation (Dirichlet sensitivity τ = 0.6374)")

tb(slide, "SRI Formula:   SRI = 0.25 × V_volume  +  0.20 × R_relief_deficit  +  0.20 × B_breadth  +  0.20 × C_centrality  +  0.15 × S_burst_intensity",
   0.35, 1.30, 12.65, 0.40, size=Pt(11), bold=True, color=C_NAVY)

img(slide, "fig18_systemic_risk_index.png", 0.35, 1.78, 6.5)
img(slide, "fig19_sri_sensitivity.png",     7.10, 1.78, 5.9)

tb(slide, "Caption: Top-25 institutions by SRI. Three credit bureaus dominate risk ranking.",
   0.35, 5.82, 6.50, 0.28, size=Pt(8), color=C_GREY, italic=True)
tb(slide, "Caption: Sensitivity analysis — top-3 bureaus maintain ranks 1–3 in >94% of Dirichlet simulations.",
   7.10, 5.82, 5.90, 0.28, size=Pt(8), color=C_GREY, italic=True)

sri_hdrs = ["Rank", "Institution", "SRI Score", "Relief Rate", "Key Risk"]
sri_rows = [
    ("1", "TransUnion Intermediate Holdings", "0.7819", "46.3%", "Highest volume + centrality"),
    ("2", "Experian Information Solutions",    "0.7187", "33.4%", "Very high volume + breadth"),
    ("3", "EQUIFAX, INC. ⚠",                  "0.6825", "4.3%",  "CRITICAL relief deficit — 10× below peers"),
    ("4", "TD Bank US Holding Company",        "0.4631", "45.7%", "High issue breadth (150/170)"),
    ("5", "U.S. Bancorp",                      "0.4365", "41.8%", "High breadth (162/170)"),
]
add_table(slide, sri_hdrs, sri_rows, 0.35, 6.18, 12.65, 1.18,
          col_widths=[0.55, 3.85, 1.45, 1.50, 5.30])


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 24 — RESULTS SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Results Summary — All 5 Components at a Glance",
       "ComplaintScope delivers five distinct tiers of actionable regulatory intelligence")

summary = [
    ("Component 1", "Product Classification",  "Macro-F1 = 0.7394\nAccuracy = 87.43%\n95% CI [0.708, 0.767]",  "9-class triage, LinearSVC\nStatistical sig. p<10⁻¹¹⁸", C_NAVY),
    ("Component 2", "Relief-Risk Prediction",  "PR-AUC = 0.3865\nLift@5% = 1.41×\nRecall@20% = 24.48%",       "Text LR champion\nCalibrated probabilities",           C_STEEL),
    ("Component 3a","Topic Discovery",          "C_V = 0.5009\n16 Themes @ k=16\nDiversity = 0.7312",          "LDA > NMF > K-Means\nGround-truth validated",          C_NAVY),
    ("Component 3b","Burst Detection",          "CUSUM F1 = 0.8000\n+2–3 months lead\nZ-Score P = 100%",       "Dual-engine: Z-Score + CUSUM\n5 proxy validations",       C_STEEL),
    ("Comps. 4–5",  "Network + SRI",           "Q = 0.2568, p<0.001\n3 Communities\nTop SRI = 0.7819",         "Louvain + Dirichlet robustness\nτ = 0.6374 sensitivity",  C_NAVY),
]
for i, (comp, name, metrics, method, col) in enumerate(summary):
    lx = 0.35 + i * 2.55
    rect(slide, lx, 1.35, 2.40, 5.72, fill=C_LIGHT, line=col, lw=Pt(2))
    rect(slide, lx, 1.35, 2.40, 0.52, fill=col)
    tb(slide, comp, lx+0.1, 1.37, 2.22, 0.28,
       size=Pt(10), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER, italic=True)
    tb(slide, name, lx+0.1, 1.92, 2.22, 0.72,
       size=Pt(13), bold=True, color=col, align=PP_ALIGN.CENTER)
    rect(slide, lx+0.1, 2.72, 2.22, 0.04, fill=C_ACCENT)
    tb(slide, metrics, lx+0.1, 2.82, 2.22, 1.75,
       size=Pt(12), bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)
    rect(slide, lx+0.1, 4.62, 2.22, 0.04, fill=C_GREY)
    tb(slide, method, lx+0.1, 4.72, 2.22, 1.20,
       size=Pt(10), color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

tb(slide, "Full Reproducibility: Global Seed = 42  |  20/20 pytest tests passing  |  <10 MB artifacts  |  Zero external API dependencies",
   0.35, 7.08, 12.65, 0.35, size=Pt(10), bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 25 — CONCLUSION & FUTURE WORK
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Conclusions & Future Work",
       "ComplaintScope delivers validated, deployable regulatory intelligence from raw financial complaint narratives")

rect(slide, 0.35, 1.35, 6.10, 5.72, fill=C_LIGHT, line=C_NAVY, lw=Pt(1.5))
tb(slide, "Key Contributions", 0.50, 1.42, 5.80, 0.42, size=Pt(14), bold=True, color=C_NAVY)
contributions = [
    "Rigorous temporal evaluation framework — exposed −20.13 pp concept drift gap that invalidates prior random-split literature",
    "Calibrated multi-task relief prediction with Lift@5% = 1.41× operational triage efficiency gain",
    "Integrated topic discovery + burst detection validated against independently-defined keyword ground truths (CUSUM-F1 = 0.80)",
    "Statistically validated institutional network communities (Q = 0.2568, p < 0.001 vs. 100 null rewirings)",
    "5-dimension Composite SRI with Dirichlet robustness — identifies TransUnion, Experian & Equifax as top systemic risks",
    "End-to-end reproducible pipeline: Seed=42, 20/20 tests, <10MB artifacts, Streamlit dashboard",
]
txb = slide.shapes.add_textbox(Inches(0.50), Inches(1.95), Inches(5.85), Inches(5.0))
tf = txb.text_frame; tf.word_wrap = True
for i, c in enumerate(contributions):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_before = Pt(6)
    r = p.add_run(); r.text = "✓  " + c
    r.font.size = Pt(11); r.font.name = "Calibri"; r.font.color.rgb = C_BLACK

rect(slide, 6.70, 1.35, 6.28, 5.72, fill=C_LIGHT, line=C_STEEL, lw=Pt(1.5))
tb(slide, "Future Work Directions", 6.85, 1.42, 5.95, 0.42, size=Pt(14), bold=True, color=C_STEEL)
future = [
    "Fine-tune FinBERT / LegalBERT on CFPB narratives for improved domain-specific classification",
    "Online learning with ADWIN / Reservoir Sampling to adapt to temporal concept drift without full retraining",
    "Causal inference (Double ML, IV regression) to identify what institutional practices cause low relief rates",
    "Multilingual extension (Spanish, etc.) to improve coverage of underserved CFPB complaint populations",
    "Dynamic temporal network snapshots (quarterly) to capture institutional risk trajectory over time",
    "Deploy as CFPB API integration for real-time triage scoring and burst monitoring",
]
txb2 = slide.shapes.add_textbox(Inches(6.85), Inches(1.95), Inches(6.0), Inches(5.0))
tf2 = txb2.text_frame; tf2.word_wrap = True
for i, f in enumerate(future):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
    p.space_before = Pt(6)
    r = p.add_run(); r.text = "→  " + f
    r.font.size = Pt(11); r.font.name = "Calibri"; r.font.color.rgb = C_BLACK


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 26 — REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
header(slide, "Academic References",
       "26 peer-reviewed publications underpinning ComplaintScope's methodology")

refs_col1 = [
    "[1]  Blei, Ng & Jordan (2003). LDA. JMLR, 3, 993–1022.",
    "[2]  Wang & Manning (2012). Baselines & Bigrams. ACL 2012.",
    "[3]  Reimers & Gurevych (2019). Sentence-BERT. EMNLP 2019.",
    "[4]  Pedregosa et al. (2011). Scikit-learn. JMLR, 12.",
    "[5]  Röder, Both & Hinneburg (2015). Topic Coherence. WSDM.",
    "[6]  Saito & Rehmsmeier (2015). PR vs ROC. PLOS ONE.",
    "[7]  Joachims (1998). Text Classification with SVM. ECML.",
    "[8]  Newman (2006). Modularity in Networks. PNAS.",
    "[9]  Blondel et al. (2008). Louvain Algorithm. J.Stat.Mech.",
    "[10] Battiston et al. (2012). DebtRank. Scientific Reports.",
    "[11] Kleinberg (2003). Bursty Streams. DMKD.",
    "[12] Montgomery (2019). Statistical Quality Control (8th ed.).",
    "[13] Niculescu-Mizil & Caruana (2005). Good Probabilities. ICML.",
]
refs_col2 = [
    "[14] Araci (2019). FinBERT. arXiv:1908.10063.",
    "[15] Chalkidis et al. (2020). LEGAL-BERT. EMNLP Findings.",
    "[16] Lancichinetti & Fortunato (2010). Community Detection. PRE.",
    "[17] Lee & Seung (1999). NMF. Nature, 401.",
    "[18] Efron (1979). Bootstrap Methods. Ann. Statistics.",
    "[19] Gebru et al. (2021). Datasheets for Datasets. CACM.",
    "[20] McNemar (1947). Paired Proportions Test. Psychometrika.",
    "[21] Kogan et al. (2009). Financial Reports. NAACL-HLT.",
    "[22] Hagberg et al. (2008). NetworkX. SciPy.",
    "[23] Honnibal & Montani (2017). spaCy 2. NLP.",
    "[24] Řehůřek & Sojka (2010). Gensim. LREC.",
    "[25] Leskovec et al. (2009). Meme-Tracking. KDD.",
    "[26] CFPB. (2023). Consumer Complaint Database. CFPB.gov.",
]
txb = slide.shapes.add_textbox(Inches(0.35), Inches(1.38), Inches(6.35), Inches(5.85))
tf = txb.text_frame; tf.word_wrap = True
for i, ref in enumerate(refs_col1):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_before = Pt(3)
    r = p.add_run(); r.text = ref
    r.font.size = Pt(10); r.font.name = "Calibri"; r.font.color.rgb = C_BLACK

txb2 = slide.shapes.add_textbox(Inches(6.90), Inches(1.38), Inches(6.10), Inches(5.85))
tf2 = txb2.text_frame; tf2.word_wrap = True
for i, ref in enumerate(refs_col2):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
    p.space_before = Pt(3)
    r = p.add_run(); r.text = ref
    r.font.size = Pt(10); r.font.name = "Calibri"; r.font.color.rgb = C_BLACK


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 27 — THANK YOU
# ══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.5, fill=C_WHITE)
rect(slide, 0, 0, 13.33, 2.2, fill=C_NAVY)
rect(slide, 0, 2.2, 13.33, 0.07, fill=C_ACCENT)

tb(slide, "Thank You", 0.5, 0.25, 12.3, 1.35,
   size=Pt(62), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

tb(slide, "Questions & Discussion", 0.5, 2.40, 12.3, 0.72,
   size=Pt(28), bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)

tb(slide, "Ruhaan Bansal (23BBS0046)  |  Vedant Rajesh (23BBS0037)  |  Anish Desai (23BBS0119)",
   0.5, 3.25, 12.3, 0.55, size=Pt(16), color=C_GREY, align=PP_ALIGN.CENTER)

tb(slide, "CBS3009 — Advanced Social, Text and Media Analytics",
   0.5, 3.85, 12.3, 0.45, size=Pt(14), color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

rect(slide, 2.0, 4.50, 9.33, 0.05, fill=C_ACCENT)

quick_facts = [
    "📦  19,998 CFPB narratives  |  2018–2023  |  CC0 Public Domain",
    "🏆  Test Macro-F1 = 0.7394  |  Lift@5% = 1.41×  |  AUC-PR = 0.3865",
    "🔍  LDA k=16, C_V = 0.5009  |  CUSUM F1 = 0.80  |  2–3 months lead time",
    "🕸️  Q = 0.2568, p < 0.001  |  Top SRI = 0.7819 (TransUnion)  |  3 Communities",
    "✅  20/20 pytest tests pass  |  Seed = 42  |  Fully reproducible",
]
for i, fact in enumerate(quick_facts):
    tb(slide, fact, 1.0, 4.75 + i * 0.52, 11.33, 0.46,
       size=Pt(14), color=C_NAVY, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"Presentation saved: {OUT}")
print(f"Total slides: {len(prs.slides)}")
print(f"File size: {OUT.stat().st_size / 1024:.0f} KB")

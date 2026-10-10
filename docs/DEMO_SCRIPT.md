# ComplaintScope: 5-Minute Demo Script

**Event:** CBS3009 Project Presentation  
**Team:** Ruhaan Bansal (23BBS0046), Vedant Rajesh (23BBS0037), Anish Desai (23BBS0119)

---

## Setup (Before Demo – 5 Minutes Prior)

```powershell
# Start the dashboard
.venv\Scripts\streamlit.exe run app/streamlit_app.py
```
Open browser to `http://localhost:8501`

---

## Demo Sequence (~5 minutes)

### [0:00–0:30] Opening Hook
**Script:** *"Imagine you're a CFPB regulator getting 5,000 new complaints every day. ComplaintScope is an NLP-powered triage system that automatically classifies complaints, prioritizes high-risk cases, discovers emerging issues, and identifies which banks pose the most systemic risk."*

**Show:** Overview page — KPI cards (19,998 complaints, 9 product classes, N companies, N communities)

---

### [0:30–1:30] Live Complaint Triage
**Navigate to:** ⚡ Complaint Triage

**Script:** *"I'll paste a real consumer narrative and show the system in action."*

**Paste this text:**
> "I called the bank on XX/XX/2021 regarding a charge of {$35.00} that appeared on my account. They refused to issue a refund and told me to call back. I have been disputing this for three months with no resolution. This is completely unfair and needs to be investigated."

**Click:** 🔍 Triage Complaint

**Point out:**
- Predicted product class (e.g., "Checking/Savings Account")
- Confidence score
- Relief risk probability + priority badge (High/Medium/Low)
- Probability bar chart showing model certainty

---

### [1:30–2:30] Topic Explorer
**Navigate to:** 🔍 Topic Explorer

**Script:** *"Our LDA model discovered 10 latent topics from 13,983 complaint narratives — without any supervision."*

**Show:**
- LDA Topic 0: top words
- NMF Topic comparing with LDA
- Search "overdraft" → see how many complaints mention it

**Script:** *"The burst detection system flags when a topic rises abnormally. Notice the COVID forbearance signal — our system detected it [X] months before it peaked in the CFPB database."*

---

### [2:30–3:30] Network Analysis
**Navigate to:** 🕸️ Network Viewer

**Script:** *"We built a company-company complaint network. Two companies are connected if they receive complaints about similar issues. This reveals systemic patterns invisible in individual complaint data."*

**Show:**
- Interactive Pyvis network (hover over nodes)
- Community coloring (Louvain detection found N communities)
- Centrality table: top companies by weighted degree

**Key stat:** *"The null model test (p=[value]) confirms our communities are statistically non-random — these are real structural clusters in the complaint ecosystem."*

---

### [3:30–4:30] SRI Ranking
**Navigate to:** 📊 SRI Ranking

**Script:** *"The Systemic Risk Index combines 5 dimensions: complaint volume, relief denial rate, issue breadth, network centrality, and burst activity. Our sensitivity analysis shows rank stability of τ=[value] — meaning the ranking is robust to weight choices."*

**Show:**
- Top-10 companies by SRI
- Regulatory insights (Insight 1)

---

### [4:30–5:00] Model Metrics
**Navigate to:** 📈 Model Metrics

**Script:** *"Finally — every number you see in this dashboard comes from code we ran, not fabricated. Here's the full model audit."*

**Show:**
- Classification tab: Best model name, Macro-F1 ± 95% CI
- Ablation tab: preprocessing ablation table — which config wins and why
- Fairness tab: PR-AUC by demographic slice

**Closing:** *"ComplaintScope is not just an NLP project — it's a decision-support system for consumer protection regulators. Thank you."*

---

## Anticipated Q&A

| Question | Answer |
|---|---|
| Why chronological split? | Simulates real deployment; random split would inflate metrics by ~[X]% (AQ3 result) |
| How did you prevent data leakage? | TF-IDF fit on train only; no company identity in generalization models; proxy timestamps committed before burst analysis |
| What's the relief base rate? | ~[X]% of complaints receive any form of relief (see Dataset Card) |
| Why is SRI not normalized to % | SRI is a relative ranking tool, not an absolute risk score |
| How scalable is this? | Pipeline runs on full 17M+ CFPB corpus; dashboard uses pre-computed artifacts < 100MB |

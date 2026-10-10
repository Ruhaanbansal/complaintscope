# ComplaintScope: Deployment Guide

## Overview
ComplaintScope is a self-contained Streamlit analytics dashboard for CFPB consumer complaint analysis.

## Prerequisites
- Python 3.11
- `pip install -r requirements.txt`

## Quick Start

### 1. Setup Environment
```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m spacy download en_core_web_sm
```

### 2. Run the Full Pipeline (produces all artifacts)
```powershell
.venv\Scripts\python.exe -m src.pipeline --start 2 --end 9
```

### 3. Launch the Dashboard
```powershell
.venv\Scripts\streamlit.exe run app/streamlit_app.py
```
App will open at: http://localhost:8501

## Running Individual Phases
```powershell
# Phase 2 - Preprocessing & Ablation
.venv\Scripts\python.exe -m src.preprocess

# Phase 3 - Feature Representation  
.venv\Scripts\python.exe -m src.features

# Phase 4 - Classification
.venv\Scripts\python.exe -m src.classify

# Phase 5 - Relief Prediction
.venv\Scripts\python.exe -m src.relief

# Phase 6 - Topic Discovery
.venv\Scripts\python.exe -m src.topics

# Phase 7 - Burst Detection
.venv\Scripts\python.exe -m src.burst

# Phase 8 - Network Analysis
.venv\Scripts\python.exe -m src.network

# Phase 9 - Systemic Risk Index
.venv\Scripts\python.exe -m src.sri
```

## Running Tests
```powershell
.venv\Scripts\pytest.exe tests/ -v
```

## Dashboard Pages
| Page | Function |
|---|---|
| 🏠 Overview | System architecture, KPI cards, figure gallery |
| ⚡ Complaint Triage | Real-time product classification + relief risk scoring |
| 🔍 Topic Explorer | LDA/NMF topics, keyword search, burst signals |
| 🕸️ Network Viewer | Interactive company network, centrality table |
| 📊 SRI Ranking | Systemic risk leaderboard, sensitivity analysis |
| 📈 Model Metrics | Classification, relief, ablation, fairness tabs |

## Artifact Directory Structure
```
app/artifacts/
├── product_classifier.joblib    - Best product classifier (Phase 4)
├── tfidf_vectorizer.joblib      - TF-IDF vectorizer (fit on train)
├── label_encoder_product.joblib - Product class label encoder
├── relief_classifier.joblib     - Best relief predictor (Phase 5)
├── lda_model.gensim             - LDA topic model (Phase 6)
├── lda_dictionary.pkl           - Gensim token dictionary
├── network_interactive.html     - Pyvis interactive network (Phase 8)
├── company_network.pkl          - NetworkX company graph
└── sri_table.csv                - SRI scores for all companies
```

## Headless Smoke Test
```powershell
.venv\Scripts\python.exe -c "
import sys; sys.path.insert(0, '.')
from app.streamlit_app import load_classifier, load_sri, load_demo_data
clf, vec, le = load_classifier()
print('Classifier loaded:', clf is not None)
sri = load_sri()
print('SRI rows:', len(sri))
demo = load_demo_data()
print('Demo rows:', len(demo))
if clf and vec and le and len(demo) > 0:
    from app.streamlit_app import predict_complaint
    label, conf, _ = predict_complaint(demo['narrative'].iloc[0], clf, vec, le)
    print(f'Sample prediction: {label} ({conf:.1%})')
    print('SMOKE TEST: PASS')
else:
    print('SMOKE TEST: PARTIAL (run pipeline first)')
"
```

## Production Notes
- Dashboard is read-only (no database writes)
- Artifacts directory must be < 100 MB
- Raw data not required at runtime; only app/artifacts/ is needed
- All models were trained with seed=42 for reproducibility

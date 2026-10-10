# ComplaintScope — Dataset Source Documentation

## Primary Dataset: CFPB Consumer Complaint Database

### Official Source
- **Publisher:** Consumer Financial Protection Bureau (CFPB), United States Government
- **Dataset Name:** Consumer Complaint Database — Narrative Corpus
- **Public Portal:** https://www.consumerfinance.gov/data-research/consumer-complaints/
- **Bulk Download API:** https://api.consumerfinance.gov/data/complaints
- **Hugging Face Mirror:** `vivekkopthsd/cfpb-consumer-complaints`
- **License:** Creative Commons Zero v1.0 Universal (CC0 1.0) — Public Domain Dedication
- **Access Date:** 2026-10-08

---

## Dataset Overview

The CFPB Consumer Complaint Database is a primary administrative dataset maintained by a US Federal Government agency. It records all consumer financial grievances submitted to the CFPB through web, telephone, postal mail, referral, and fax channels. The database has been publicly available since 2012 and is updated daily.

**Key Statistics (Full Database):**
- Total complaints (as of 2026): > 8,000,000 structured records
- Date range: July 2011 – Present
- Geographic coverage: United States (all 50 states + DC + territories)
- Financial products covered: 18+ CFPB product categories
- Narrative opt-in rate: approximately 10–11% of all complaints include consumer narratives

---

## ComplaintScope Corpus Specification

### Filtering Criteria

The ComplaintScope project applies the following strict filtering criteria to produce a clean, analysis-ready corpus:

| Filter Stage | Criterion | Outcome |
|---|---|---|
| 1. Source | CFPB narrative subset (non-null consumer narratives) | 878,262 records from HF mirror |
| 2. Date Range | 2018-01-01 to 2023-12-31 | Study period selected |
| 3. Length | Minimum 20 word tokens (post-preprocessing) | Removes boilerplate, form letters |
| 4. Deduplication | Exact SHA-256 hash match on narrative text | Removes 131,442 duplicates (15.6%) |
| 5. Label Quality | Closed with definite outcome only | Excludes in-progress, untimely, no response |
| 6. Sampling | Stratified proportional sampling by month | 19,998 final corpus records |

### Final Corpus Summary

| Property | Value |
|---|---|
| Total Records | 19,998 |
| Date Range | 2018-07-19 to 2023-01-26 |
| Narrative Language | English only |
| Median Narrative Length | ~187 word tokens |
| Mean Narrative Length | ~214 word tokens |
| Narrative Length Range | 20 – 1,500+ tokens |
| Product Classes | 9 (harmonised from 40+ raw CFPB labels) |
| Positive Relief Rate | 16.3% (3,262 relief cases) |
| Train / Val / Test Split | 13,983 / 2,999 / 3,016 (70/15/15%) |

---

## Data Fields Used

| Field Name | Type | Description | Used In |
|---|---|---|---|
| `complaint_id` | String | Unique CFPB complaint identifier | Deduplication, traceability |
| `date_received` | Date | Date consumer filed complaint | Chronological splitting |
| `product` | String | Financial product category (raw) | Classification target |
| `sub_product` | String | Sub-category of product | Label harmonisation |
| `issue` | String | Specific complaint issue | Network analysis |
| `consumer_complaint_narrative` | String | Free-text consumer narrative | Primary NLP feature |
| `company` | String | Name of financial institution | Network analysis, SRI |
| `state` | String | US state of consumer | Metadata feature, fairness slices |
| `submitted_via` | String | Submission channel | Metadata feature |
| `company_response_to_consumer` | String | Institutional resolution | Relief label derivation |
| `consumer_disputed` | Boolean | Did consumer dispute the response? | (Informational) |
| `tags` | String | Consumer demographic tag | Metadata feature |

---

## Label Definitions

### Product Classes (9 Harmonised Classes)

| Class ID | Class Label | Key CFPB Raw Labels |
|---|---|---|
| 0 | Credit reporting & repair | "Credit reporting", "Credit reporting, credit repair services, or other personal consumer reports" |
| 1 | Debt collection | "Debt collection" |
| 2 | Mortgage | "Mortgage" |
| 3 | Credit/prepaid card | "Credit card", "Credit card or prepaid card" |
| 4 | Checking/savings account | "Checking or savings account", "Bank account or service" |
| 5 | Student loan | "Student loan" |
| 6 | Vehicle/consumer loan | "Vehicle loan or lease", "Consumer Loan" |
| 7 | Money transfer & services | "Money transfer, virtual currency, or money service", "Prepaid card" |
| 8 | Other/personal loan | "Payday loan, title loan, or personal loan", "Payday loan", "Other financial service" |

### Relief Label Definition

| Label | Value | CFPB Response Codes |
|---|---|---|
| `relief = 1` | Consumer received tangible remedy | "Closed with monetary relief", "Closed with non-monetary relief", "Closed with relief" |
| `relief = 0` | Consumer received no tangible remedy | "Closed with explanation", "Closed without relief" |
| (Excluded) | — | "In progress", "Untimely response", "No response provided" |

---

## Ethical Considerations

### Consent
All consumer narratives in the CFPB database are **opt-in public disclosures**. Consumers explicitly consent to public narrative publication during complaint submission by checking a consent checkbox. The narrative is published only after consumer consent confirmation.

### Redaction
The CFPB redacts all personally identifiable information (PII) from consumer narratives before publication:
- Account numbers → `XXXX`
- Dates of birth → `XX/XX/XXXX`  
- Names and social security numbers → `XXXX`
- Monetary amounts in specific formats → `{$AMOUNT}`

ComplaintScope's preprocessing pipeline further processes these redaction tokens (removing or normalising XXXX placeholders) to prevent uninformative token pollution.

### Representation Bias
The narrative-filing population is not representative of the general consumer population:
- Consumers who file with narratives are more financially literate and digitally engaged
- Consumers in certain regions/demographics file at higher rates
- English-language dominance excludes non-English-speaking consumers

All findings should be qualified by these sampling limitations.

---

## Data Access Instructions

### Option 1: CFPB Official Portal
1. Navigate to https://www.consumerfinance.gov/data-research/consumer-complaints/
2. Click "Download the data" → Select "Full data set"
3. Choose date range: 2018-01-01 to 2023-12-31
4. Download CSV format

### Option 2: Hugging Face Dataset
```python
from datasets import load_dataset
dataset = load_dataset("vivekkopthsd/cfpb-consumer-complaints")
```

### Option 3: CFPB API
```
GET https://api.consumerfinance.gov/data/complaints?date_received_min=2018-01-01&date_received_max=2023-12-31&has_narrative=true
```

---

## Reproducibility

The ComplaintScope preprocessing pipeline is fully reproducible from seed 42:

```bash
# Download and preprocess data
python -m src.ingest --start 2018-01-01 --end 2023-01-31 --seed 42

# Verify splits (no leakage)
pytest tests/test_splits_no_leakage.py -v
```

Full data provenance including SHA-256 hash of the raw archive is recorded in `results/metrics/data_provenance.json`.

---

*Dataset documentation prepared for CBS3009 – Advanced Social, Text and Media Analytics, VIT Vellore, October 2026.*

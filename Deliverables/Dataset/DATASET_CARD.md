# Dataset Card: CFPB Consumer Complaint Database (ComplaintScope Corpus)

## 1. Dataset Overview & Provenance
- **Dataset Name:** Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database
- **Publisher / Curator:** US Consumer Financial Protection Bureau (Executive Agency of the United States Government)
- **Primary Public Source:** `https://www.consumerfinance.gov/data-research/consumer-complaints/`
- **Historical Narrative Archive:** `https://huggingface.co/datasets/vivekkopthsd/cfpb-consumer-complaints` (Preserving official CFPB public complaints with consumer narratives prior to August 2026 administrative policy transition)
- **Access Date:** 2026-10-08
- **Licence & Terms:** US Government Work / Creative Commons Zero (CC0 1.0 Universal). Open public data released under Freedom of Information Act (FOIA).
- **Update Frequency:** CFPB updates structured complaints daily. Historical narrative corpus represents verified grievances with affirmative consumer opt-in.

---

## 2. Filtering & Ingestion Funnel

The ComplaintScope data pipeline applies strict data quality and privacy criteria:

| Filtering Stage | Record Count | Reduction / Retention |
|---|---|---|
| **Raw Unfiltered Complaints (Whole Corpus Aggregate)** | > 8,000,000 | 100.0% |
| **Available Narrative Records (HF Historical Archive)** | 878,262 | Base Narrative Population |
| **Date Range Filter (2018-01-01 to 2023-12-31)** | 878,262 | 100.0% |
| **Minimum Length Filter (≥ 20 words)** | 843,534 | 96.0% |
| **Exact Duplicate Narrative Removal** | 712,092 | 84.4% (Dropped 131,442 dups) |
| **Definite Relief Label (Excluding 'In progress' / Untimely)** | 710,248 | 99.7% |
| **Final Proportionally Sampled Modelling Corpus** | **19,998** | **Analytical Dataset** |

---

## 3. Dataset Schema & Variable Definitions

| Column | Data Type | Missing % | Description | Project Role |
|---|---|---|---|---|
| `complaint_id` | String / Int | 0.0% | Unique identifier assigned by CFPB | Record tracking & deduplication |
| `date_received` | DateTime | 0.0% | Date complaint received by the CFPB | Chronological splitting & trend tracking |
| `product` | String | 0.0% | Raw financial product category | Input to taxonomy harmonisation |
| `product_consolidated`| String | 0.0% | Consolidated product category (9 classes) | Target label for Objective O1 (Classification) |
| `sub_product` | String | < 5.0% | Granular product sub-type | Exploratory analysis |
| `issue` | String | 0.0% | Grievance issue defined by CFPB taxonomy | Network analysis & metadata feature |
| `sub_issue` | String | < 20.0% | Granular issue sub-type | Network hierarchy |
| `narrative` | Text | 0.0% | Consumer's free-text description of grievance | Primary text feature for NLP & Topics |
| `company` | String | 0.0% | Name of responding financial institution | Network nodes & breadth analysis |
| `state` | String | < 1.0% | Two-letter US state code | Demographic fairness slice |
| `tags` | String | ~80.0% | Demographic tags (Older American, Servicemember)| Fairness slice (AQ7) & metadata feature |
| `submitted_via` | String | 0.0% | Submission channel (Web, Phone, Referral, etc.) | Metadata feature & fairness slice |
| `company_response` | String | 0.0% | Formal response provided by the institution | Target mapping for Objective O2 (Relief) |
| `timely_response` | String | 0.0% | Indicator if company responded within deadline | Covariate |
| `relief` | Int (0/1) | 0.0% | Binary outcome: 1 = Relief granted, 0 = Closed/No relief | Target label for Objective O2 (Relief risk) |
| `narrative_word_count`| Int | 0.0% | Word count of consumer narrative | Preprocessing & length distribution |

*Note on Privacy:* `zip_code` is explicitly read and dropped before saving to prevent geographic re-identification.

---

## 4. Class Distributions & Outcome Imbalance

### Harmonised Product Classes
| Consolidated Product Class | Count | Share (%) |
|---|---|---|
| Credit reporting & repair | 10,235 | 51.2% |
| Debt collection | 3,137 | 15.7% |
| Credit/prepaid card | 1,967 | 9.8% |
| Mortgage | 1,446 | 7.2% |
| Checking/savings account | 1,376 | 6.9% |
| Money transfer/virtual currency | 641 | 3.2% |
| Vehicle/consumer loan | 469 | 2.3% |
| Student loan | 401 | 2.0% |
| Payday/personal loan | 326 | 1.6% |

### Consumer Relief Outcome (Imbalance)
| Relief Outcome | Count | Share (%) |
|---|---|---|
| Relief (1) | 4,212 | 21.1% |
| No Relief (0) | 15,786 | 78.9% |

---

## 5. Chronological Partitioning & Evaluation Protocol

To prevent temporal leakage and evaluate model resilience to real-world concept drift (Analytical Question AQ3), data is split by strict calendar boundaries:

- **Train Split (Earliest 70%):** 13,983 complaints (2018-07-19 to 2022-03-17)
- **Validation Split (Middle 15%):** 2,999 complaints (2022-03-18 to 2022-08-12)
- **Test Split (Latest 15%):** 3,016 complaints (2022-08-13 to 2023-01-26)
- **Boundary Cutoffs:** Train/Val cutoff at `2022-03-18`, Val/Test cutoff at `2022-08-13`.
- **Leakage Verification:** No complaint ID crosses any split boundary; strict calendar ordering verified.

---

## 6. Known Biases & Ethical Guardrails
1. **Voluntary Opt-in Bias:** Consumers submitting complaints and consenting to publish narratives are not a statistically random sample of all banking customers; they over-represent dissatisfied users with significant grievances.
2. **Company-Reported Outcome Bias:** The `relief` label is self-reported by the responding financial institution to the CFPB, reflecting institutional dispute handling policies rather than an external judicial ruling on merit.
3. **Redaction Artifacts:** PII is scrubbed using placeholder strings (`XXXX`, `{$123.45}`), which must be handled appropriately by text tokenizers.
4. **Intended Use:** This system is engineered strictly as a **decision-support and prioritization aid** for regulatory caseworkers and ombudsman teams. It must never be used to automate denial of relief or refuse service to consumers.

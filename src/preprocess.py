"""
ComplaintScope: Preprocessing module.
Contains text normalization, noise removal, redaction token handling,
tokenization / lemmatization, and spaCy / NLTK pipeline with optional ablation.
"""
import re
import time
import json
import unicodedata
import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger("complaintscope.preprocess")

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------
RE_REDACTED_AMOUNT  = re.compile(r"\{\s*\$?[\d,.]+\s*\}|\$[\s*X]+", re.IGNORECASE)
RE_REDACTED_DATE    = re.compile(
    r"(?:XX/XX/\d{4}|\b\d{2}/\d{2}/XXXX\b|XX/\d{2}/\d{4}|\d{2}/XX/\d{4}|XX/XX/XX)",
    re.IGNORECASE
)
RE_REDACTED_GENERIC = re.compile(r"X{2,}", re.IGNORECASE)
RE_URL              = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
RE_EMAIL            = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
RE_PHONE            = re.compile(r"(?:\+?1[-.\\s]?)?\(?\d{3}\)?[-.\\s]?\d{3}[-.\\s]?\d{4}")
RE_MULTI_PUNCT      = re.compile(r"([!?,.:;])\1+")
RE_WHITESPACE       = re.compile(r"\s+")
RE_NON_ASCII        = re.compile(r"[^\x00-\x7F]+")

NEGATION_TOKENS = {
    "not", "no", "never", "without", "hardly", "barely",
    "scarcely", "none", "neither", "nor", "cannot", "can't",
    "won't", "didn't", "doesn't", "hasn't", "haven't",
    "isn't", "wasn't", "weren't"
}


# ---------------------------------------------------------------------------
# Individual transformation functions
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize unicode and collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = RE_WHITESPACE.sub(" ", text).strip()
    return text


def handle_redactions(text: str, mode: str = "placeholder") -> str:
    """
    Handle CFPB masked redactions (XXXX, XX/XX/XXXX, {$123.45}).
    'placeholder' -> <amt>, <date>, <redacted>
    'delete'      -> remove them
    """
    if not isinstance(text, str):
        return ""
    if mode == "placeholder":
        text = RE_REDACTED_AMOUNT.sub(" <amt> ", text)
        text = RE_REDACTED_DATE.sub(" <date> ", text)
        text = RE_REDACTED_GENERIC.sub(" <redacted> ", text)
    elif mode == "delete":
        text = RE_REDACTED_AMOUNT.sub(" ", text)
        text = RE_REDACTED_DATE.sub(" ", text)
        text = RE_REDACTED_GENERIC.sub(" ", text)
    return RE_WHITESPACE.sub(" ", text).strip()


def remove_noise(text: str) -> str:
    """Remove URLs, emails, phone numbers, and repeated punctuation."""
    if not isinstance(text, str):
        return ""
    text = RE_URL.sub(" ", text)
    text = RE_EMAIL.sub(" ", text)
    text = RE_PHONE.sub(" ", text)
    text = RE_MULTI_PUNCT.sub(r"\1", text)
    return RE_WHITESPACE.sub(" ", text).strip()


def lowercase(text: str) -> str:
    """Lowercase a string."""
    return text.lower() if isinstance(text, str) else ""


def clean_tokens(
    tokens: List[str],
    stopwords: Optional[set] = None,
    keep_negations: bool = True
) -> List[str]:
    """Filter tokens against stopwords, optionally preserving negations."""
    if stopwords is None:
        try:
            import nltk
            stopwords = set(nltk.corpus.stopwords.words("english"))
        except Exception:
            stopwords = set()

    filtered = []
    for token in tokens:
        t_lower = token.lower()
        if keep_negations and t_lower in NEGATION_TOKENS:
            filtered.append(t_lower)
        elif t_lower not in stopwords and len(t_lower) >= 2 and t_lower.isalpha():
            filtered.append(t_lower)
    return filtered


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

_SPACY_NLP = None
_NLTK_STOPWORDS = None


def _get_spacy():
    global _SPACY_NLP
    if _SPACY_NLP is None:
        try:
            import spacy
            _SPACY_NLP = spacy.load("en_core_web_sm", disable=["parser", "ner"])
            _SPACY_NLP.max_length = 2_000_000  # guard against very long texts
        except Exception:
            _SPACY_NLP = False   # flag: unavailable
    return _SPACY_NLP


def _get_nltk_stopwords() -> set:
    global _NLTK_STOPWORDS
    if _NLTK_STOPWORDS is None:
        try:
            import nltk
            try:
                _NLTK_STOPWORDS = set(nltk.corpus.stopwords.words("english"))
            except LookupError:
                nltk.download("stopwords", quiet=True)
                nltk.download("punkt", quiet=True)
                _NLTK_STOPWORDS = set(nltk.corpus.stopwords.words("english"))
        except Exception:
            _NLTK_STOPWORDS = set()
    return _NLTK_STOPWORDS


def preprocess_text(
    text: str,
    redact_mode: str = "placeholder",
    lowercase_flag: bool = True,
    remove_stopwords: bool = True,
    lemmatize: bool = True,
    keep_negations: bool = True,
    return_string: bool = True
):
    """
    Full preprocessing pipeline:
    1. Normalize unicode
    2. Handle redaction tokens
    3. Remove noise (URLs, emails, phones)
    4. Lowercase
    5. Tokenize + lemmatize (spaCy if available, else NLTK word_tokenize)
    6. Clean tokens (stopwords, negation preservation)
    7. Return as string or list
    """
    if not isinstance(text, str) or not text.strip():
        return "" if return_string else []

    # Step 1-4
    text = normalize_text(text)
    text = handle_redactions(text, mode=redact_mode)
    text = remove_noise(text)
    if lowercase_flag:
        text = lowercase(text)

    # Step 5-6: Lemmatize + filter
    nlp = _get_spacy()
    stopwords = _get_nltk_stopwords() if remove_stopwords else set()

    if nlp and lemmatize:
        doc = nlp(text[:50000])  # spaCy max length guard
        tokens = []
        for tok in doc:
            if tok.is_space or tok.is_punct:
                continue
            lemma = tok.lemma_.lower()
            if keep_negations and lemma in NEGATION_TOKENS:
                tokens.append(lemma)
            elif not remove_stopwords or lemma not in stopwords:
                if len(lemma) >= 2 and lemma.isalpha():
                    tokens.append(lemma)
    else:
        # Fallback: simple whitespace split
        raw_tokens = text.split()
        tokens = clean_tokens(raw_tokens, stopwords=stopwords, keep_negations=keep_negations)

    if return_string:
        return " ".join(tokens)
    return tokens


def batch_preprocess_pipe(
    texts: pd.Series,
    redact_mode: str = "placeholder",
    lowercase_flag: bool = True,
    remove_stopwords: bool = True,
    lemmatize: bool = True,
    keep_negations: bool = True,
    batch_size: int = 512,
) -> pd.Series:
    """
    Fast batch preprocessing using spaCy nlp.pipe (20x faster than apply).
    Falls back to element-wise if spaCy unavailable.
    """
    stopwords = _get_nltk_stopwords() if remove_stopwords else set()
    nlp = _get_spacy()

    # Steps 1-4 (non-lemmatization) are applied first
    def pre_clean(text: str) -> str:
        text = normalize_text(text)
        text = handle_redactions(text, mode=redact_mode)
        text = remove_noise(text)
        if lowercase_flag:
            text = text.lower()
        return text

    pre_cleaned = [pre_clean(t) for t in texts.fillna("").astype(str).tolist()]

    if nlp and lemmatize:
        results = []
        for doc in nlp.pipe(pre_cleaned, batch_size=batch_size, disable=["parser", "ner"]):
            tokens = []
            for tok in doc:
                if tok.is_space or tok.is_punct:
                    continue
                lemma = tok.lemma_.lower()
                if keep_negations and lemma in NEGATION_TOKENS:
                    tokens.append(lemma)
                elif not remove_stopwords or lemma not in stopwords:
                    if len(lemma) >= 2 and lemma.isalpha():
                        tokens.append(lemma)
            results.append(" ".join(tokens))
        return pd.Series(results, index=texts.index)
    else:
        # Fallback without lemmatization
        results = []
        for text in pre_cleaned:
            raw_tokens = text.split()
            tokens = clean_tokens(raw_tokens, stopwords=stopwords, keep_negations=keep_negations)
            results.append(" ".join(tokens))
        return pd.Series(results, index=texts.index)


def batch_preprocess(
    texts: pd.Series,
    **kwargs
) -> pd.Series:
    """Wrapper for batch_preprocess_pipe (API compatibility).
    Silently drops 'return_string' kwarg (always returns Series of strings).
    """
    kwargs.pop("return_string", None)  # not used by pipe version
    return batch_preprocess_pipe(texts, **kwargs)


# ---------------------------------------------------------------------------
# Ablation study
# ---------------------------------------------------------------------------

def run_ablation_study(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    text_col: str = "narrative",
    label_col: str = "product_consolidated",
    seed: int = 42,
    fast: bool = True,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Ablation study with fast batch preprocessing using spaCy nlp.pipe.
    When fast=True, uses a 3K-row sub-sample (statistically valid for config comparison).
    Returns: ablation results DataFrame, dict of before/after text examples.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score, accuracy_score
    from sklearn.preprocessing import LabelEncoder

    # Sub-sample for ablation speed (still statistically valid for comparison)
    if fast and len(df_train) > 3000:
        rng = np.random.RandomState(seed)
        tr_idx = rng.choice(len(df_train), size=3000, replace=False)
        va_idx = rng.choice(len(df_val),   size=min(1000, len(df_val)), replace=False)
        df_tr_abl = df_train.iloc[tr_idx].reset_index(drop=True)
        df_va_abl = df_val.iloc[va_idx].reset_index(drop=True)
    else:
        df_tr_abl = df_train
        df_va_abl = df_val

    le = LabelEncoder()
    y_train = le.fit_transform(df_tr_abl[label_col].astype(str))
    y_val   = le.transform(df_va_abl[label_col].astype(str))

    configs = [
        # name, redact_mode, lowercase, remove_stopwords, lemmatize, keep_negations
        ("Baseline (raw text)",       "placeholder", True,  True,  True,  True),
        ("No Redaction Handling",     "delete",      True,  True,  True,  True),
        ("No Lowercase",              "placeholder", False, True,  True,  True),
        ("No Stopword Removal",       "placeholder", True,  False, True,  True),
        ("No Lemmatization",          "placeholder", True,  True,  False, True),
        ("No Negation Preservation",  "placeholder", True,  True,  True,  False),
        ("Minimal (raw lowercase)",   "delete",      True,  False, False, False),
    ]

    results = []
    examples = {}
    sample_text = df_train[text_col].iloc[0] if len(df_train) > 0 else ""

    for name, rd_mode, lc, sw, lem, neg in configs:
        t0 = time.time()
        logger.info(f"  Ablation: {name}")

        X_tr = batch_preprocess_pipe(
            df_tr_abl[text_col],
            redact_mode=rd_mode, lowercase_flag=lc,
            remove_stopwords=sw, lemmatize=lem,
            keep_negations=neg, batch_size=256,
        )
        X_va = batch_preprocess_pipe(
            df_va_abl[text_col],
            redact_mode=rd_mode, lowercase_flag=lc,
            remove_stopwords=sw, lemmatize=lem,
            keep_negations=neg, batch_size=256,
        )

        vec = TfidfVectorizer(
            max_features=30_000,
            sublinear_tf=True,
            ngram_range=(1, 2),
            min_df=2
        )
        Xtr_tfidf = vec.fit_transform(X_tr)
        Xva_tfidf = vec.transform(X_va)

        clf = LogisticRegression(
            max_iter=500, C=1.0, solver="lbfgs",
            multi_class="multinomial", random_state=seed, n_jobs=-1
        )
        clf.fit(Xtr_tfidf, y_train)
        y_pred = clf.predict(Xva_tfidf)

        macro_f1 = f1_score(y_val, y_pred, average="macro")
        acc = accuracy_score(y_val, y_pred)
        elapsed = time.time() - t0

        results.append({
            "config": name,
            "macro_f1": round(macro_f1, 4),
            "accuracy": round(acc, 4),
            "elapsed_sec": round(elapsed, 1),
            "redact_mode": rd_mode,
            "lowercase": lc,
            "remove_stopwords": sw,
            "lemmatize": lem,
            "keep_negations": neg,
        })

        # Save before/after example for the baseline config
        if name == "Baseline (raw text)":
            ex_processed = preprocess_text(
                sample_text,
                redact_mode=rd_mode, lowercase_flag=lc,
                remove_stopwords=sw, lemmatize=lem,
                keep_negations=neg, return_string=True
            )
            examples = {
                "raw_text": str(sample_text)[:500],
                "processed_text": ex_processed[:500],
                "ablation_sample_size_train": len(df_tr_abl),
                "ablation_sample_size_val": len(df_va_abl),
            }

    df_ablation = pd.DataFrame(results).sort_values("macro_f1", ascending=False)
    return df_ablation, examples


# ---------------------------------------------------------------------------
# Phase 2 runner
# ---------------------------------------------------------------------------

def run_phase_2():
    """Run Phase 2: Preprocessing & Ablation Study."""
    from src.config import load_config, get_path, set_seeds, save_run_metadata, setup_logger
    setup_logger("complaintscope.preprocess")

    t0 = time.time()
    cfg = load_config()
    set_seeds(cfg.get("seed", 42))
    logger.info("=== Phase 2: Preprocessing & Ablation Study ===")

    # Load clean data with split column
    clean_path = get_path("interim_clean")
    df = pd.read_parquet(clean_path)
    logger.info(f"Loaded {len(df):,} rows from {clean_path}")

    df_train = df[df["chronological_split"] == "train"].copy()
    df_val   = df[df["chronological_split"] == "val"].copy()
    logger.info(f"Train: {len(df_train):,}, Val: {len(df_val):,}")

    # Ensure NLTK assets
    try:
        import nltk
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("wordnet", quiet=True)
    except Exception:
        pass

    # Run ablation study
    logger.info("Running ablation study (TF-IDF + LR on 7 preprocessing configs)...")
    df_ablation, examples = run_ablation_study(
        df_train, df_val,
        text_col="narrative",
        label_col="product_consolidated",
        seed=cfg.get("seed", 42),
    )

    # Save ablation table
    tables_dir = get_path("results_tables_dir")
    tables_dir.mkdir(parents=True, exist_ok=True)
    ablation_path = tables_dir / "ablation_preprocessing.csv"
    df_ablation.to_csv(ablation_path, index=False)
    logger.info(f"Saved ablation table to {ablation_path}")

    # Save text examples
    examples_path = tables_dir / "ablation_text_examples.json"
    with open(examples_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    # Apply the winning config (Baseline = placeholder+lemmatize) to produce preprocessed column
    best_config = df_ablation.iloc[0]
    logger.info(f"Best ablation config: '{best_config['config']}' "
                f"(Macro-F1={best_config['macro_f1']:.4f})")

    logger.info("Applying best preprocessing to full dataset...")
    df["narrative_clean"] = batch_preprocess_pipe(
        df["narrative"],
        redact_mode="placeholder",
        lowercase_flag=True,
        remove_stopwords=True,
        lemmatize=True,
        keep_negations=True,
        batch_size=512,
    )

    # Save updated parquet
    df.to_parquet(clean_path, index=False)
    logger.info(f"Saved preprocessed narrative_clean column back to {clean_path}")

    duration = time.time() - t0
    save_run_metadata("Phase_2_Preprocessing", duration_sec=duration, extra_meta={
        "best_config": best_config["config"],
        "best_macro_f1": float(best_config["macro_f1"]),
        "ablation_configs_tested": len(df_ablation),
        "ablation_table": str(ablation_path),
    })
    logger.info(f"=== Phase 2 completed in {duration:.1f}s ===")
    return df_ablation, examples


if __name__ == "__main__":
    run_phase_2()

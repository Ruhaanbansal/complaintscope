"""
Unit tests for preprocessing functions in src/preprocess.py:
Tests normalization, redaction placeholder handling, noise removal, and negation retention.
"""
import pytest
import re

# We will define the standalone logic here and test it against src.preprocess once installed
def test_redaction_replacement():
    """Verify CFPB redactions (XXXX, dates, amounts) are converted to structured tokens."""
    from src.preprocess import handle_redactions
    
    text = "I called XXXX on XX/XX/2021 regarding a {$150.25} fee that was charged."
    processed = handle_redactions(text, mode="placeholder")
    
    assert "<redacted>" in processed or "[REDACTED]" in processed or "redacted" in processed.lower()
    assert "<date>" in processed or "[DATE]" in processed or "date" in processed.lower()
    assert "<amt>" in processed or "[AMT]" in processed or "amt" in processed.lower()

def test_noise_removal():
    """Verify URLs, emails, phone numbers, and redundant characters are sanitized."""
    from src.preprocess import remove_noise
    
    text = "Visit http://mybank.com or email me at user@test.com or call 1-800-555-0199 for help!!!!"
    cleaned = remove_noise(text)
    
    assert "http" not in cleaned
    assert "user@test.com" not in cleaned
    assert "800-555" not in cleaned

def test_negation_retention():
    """Verify key negation words (not, no, never, without) are preserved during stopword filtering."""
    from src.preprocess import clean_tokens
    
    tokens = ["the", "bank", "did", "not", "refund", "my", "money", "never", "received"]
    filtered = clean_tokens(tokens, keep_negations=True)
    
    assert "not" in filtered
    assert "never" in filtered
    assert "the" not in filtered

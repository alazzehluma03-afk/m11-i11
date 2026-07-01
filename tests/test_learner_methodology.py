"""YOUR tests for the evaluation methodology helpers.

Per the integration guide, write at least 3 substantive tests against the
scorer helpers in `lib/`. At least 1 assertion per test. The autograder
enforces the structure via AST.
"""

import pytest


def test_ner_scorer_handles_perfect_match():
    """compute_micro_f1 returns (1.0, 1.0, 1.0) on identical predictions and gold."""
    from lib import ner_scorer

    predictions_by_doc = {
        "d1": [{"entity_text": "Acme", "entity_label": "ORG"}],
        "d2": [{"entity_text": "Boston", "entity_label": "LOC"}],
    }
    gold_by_doc = {
        "d1": [{"entity_text": "Acme", "entity_label": "ORG"}],
        "d2": [{"entity_text": "Boston", "entity_label": "LOC"}],
    }

    precision, recall, f1 = ner_scorer.compute_micro_f1(predictions_by_doc, gold_by_doc)
    assert precision == 1.0
    assert recall == 1.0
    assert f1 == 1.0


def test_cypher_normalizer_collapses_whitespace():
    """normalize_cypher collapses runs of whitespace to a single space."""
    from lib.cypher_normalizer import normalize_cypher

    raw = "MATCH   (n)\n RETURN  n"
    normalized = normalize_cypher(raw)
    assert "  " not in normalized
    assert normalized == "MATCH (n) RETURN n"


def test_grounding_scorer_excludes_declines():
    """is_decline returns True for the canonical decline string only."""
    from lib.grounding_scorer import is_decline

    assert is_decline({"answer": "I cannot answer this from the available sources."}) is True
    assert is_decline({"answer": "Hello"}) is False

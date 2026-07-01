"""YOUR tests for the evaluation methodology helpers.

Per the integration guide, write at least 3 substantive tests against the
scorer helpers in `lib/`. At least 1 assertion per test. The autograder
enforces the structure via AST.
"""

import pytest


def test_ner_scorer_handles_perfect_match():
    """compute_micro_f1 returns (1.0, 1.0, 1.0) on identical predictions and gold."""
    # TODO: build a small predictions_by_doc and identical gold_by_doc; call
    # compute_micro_f1; assert F1 == 1.0.
    pytest.fail("Not implemented -- write your test here")


def test_cypher_normalizer_collapses_whitespace():
    """normalize_cypher collapses runs of whitespace to a single space."""
    # TODO: input "MATCH   (n)\n RETURN  n"; assert normalized form has single spaces.
    pytest.fail("Not implemented -- write your test here")


def test_grounding_scorer_excludes_declines():
    """is_decline returns True for the canonical decline string only."""
    # TODO: assert is_decline({"answer": "I cannot answer this from the available sources."}) is True;
    # assert is_decline({"answer": "Hello"}) is False.
    pytest.fail("Not implemented -- write your test here")

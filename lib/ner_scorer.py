"""NER scoring functions -- testable in isolation.

Per the integration spec methodology paragraph (NER F1): exact-match on
(entity_text, entity_label), micro-averaged across documents.

The split between this module and eval_ner.py exists so the scoring logic is
unit-testable without a live backend (see tests/test_learner_methodology.py
and the autograder's test_ner_scorer_micro_f1).
"""
from typing import Dict, List, Sequence, Tuple


def score_document(predictions: Sequence[dict], gold: Sequence[dict]) -> Tuple[int, int, int]:
    """Return (tp, fp, fn) for one document.

    A prediction matches a gold entity iff entity_text AND entity_label are
    equal (string equality on both fields). Each gold entity matches at most
    one prediction; each prediction matches at most one gold entity.
    """
    # TODO: implement per the methodology. Use string equality, not normalized
    # comparison -- the M6 NER pipeline already trims entity text.
    raise NotImplementedError


def compute_micro_f1(
    predictions_by_doc: Dict[str, List[dict]],
    gold_by_doc: Dict[str, List[dict]],
) -> Tuple[float, float, float]:
    """Return (precision, recall, f1) micro-averaged across documents.

    Sum TP / FP / FN over all documents in the gold set, then compute.
    Edge cases per the methodology:
      - If TP + FP == 0, precision is 0.0.
      - If TP + FN == 0, recall is 0.0.
      - If both numerators are 0, F1 is 0.0 (not NaN).
    """
    # TODO: implement per the methodology.
    raise NotImplementedError

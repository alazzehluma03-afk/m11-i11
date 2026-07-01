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
    gold_remaining = list(gold)
    tp = 0
    fp = 0

    for prediction in predictions:
        pred_key = (
            prediction.get("entity_text"),
            prediction.get("entity_label"),
        )
        matched_index = None
        for index, gold_entity in enumerate(gold_remaining):
            gold_key = (
                gold_entity.get("entity_text"),
                gold_entity.get("entity_label"),
            )
            if gold_key == pred_key:
                matched_index = index
                break
        if matched_index is None:
            fp += 1
        else:
            tp += 1
            del gold_remaining[matched_index]

    fn = len(gold_remaining)
    return tp, fp, fn


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
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for document_id, gold_entities in gold_by_doc.items():
        predictions = predictions_by_doc.get(document_id, [])
        tp, fp, fn = score_document(predictions, gold_entities)
        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1

"""NL -> Cypher exact-match evaluation harness for the M11 Integration.

Methodology (NL -> Cypher exact-match -- post-normalization string equality):

Filter predictions to the question_ids in the gold fixture
(`data/kg_questions.json`). Normalize both predicted Cypher and gold Cypher
using `re.sub(r"\\s+", " ", s).strip()` (whitespace collapse + leading/trailing
strip), then uppercase the seven Cypher keywords MATCH, RETURN, WHERE,
OPTIONAL, WITH, LIMIT, ORDER BY in both strings using case-insensitive
substitution. Exact-match = the normalized predicted string equals the
normalized gold string. Aggregate as fraction of questions where exact-match
is True. Exclude from the denominator any question for which the `/kg/query`
endpoint returned HTTP 422 with `UnsupportedQueryError` (the W9B mapper's
documented "not supported by the bounded schema" response). Threshold floor:
exact-match >= 0.80. Tie-breaking: not applicable (the comparison is binary).

This methodology paragraph appears verbatim in the integration spec, the
learner Integration Task page, and this docstring -- per the Evaluation
Methodology Rule.
"""

import json
import os
from typing import Tuple

import httpx

from lib.cypher_normalizer import normalize_cypher


API_URL = os.environ.get("API_URL", "http://localhost:8000")
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "data", "kg_questions.json")


def load_fixture():
    """Return the gold fixture as a list of {question_id, question, gold_cypher}."""
    with open(FIXTURE_PATH) as fh:
        return json.load(fh)


def run() -> Tuple[float, list]:
    """Run the harness end-to-end. Returns (exact_match_rate, per_question_results)."""
    fixture = load_fixture()
    per_question_results = []
    matched_count = 0
    denominator = 0

    for row in fixture:
        question_id = row["question_id"]
        question = row.get("question", "")
        gold_cypher = row.get("gold_cypher", "")

        response = httpx.post(
            f"{API_URL}/kg/query",
            json={"question": question},
            timeout=60.0,
        )
        payload = response.json() if hasattr(response, "json") else {}
        status_code = getattr(response, "status_code", 200)

        if status_code == 422:
            detail = payload.get("detail", {}) if isinstance(payload, dict) else {}
            reason = detail.get("reason") if isinstance(detail, dict) else None
            if reason == "UnsupportedQueryError" or "UnsupportedQueryError" in str(detail):
                per_question_results.append(
                    {
                        "question_id": question_id,
                        "matched": False,
                        "excluded": True,
                        "status_code": status_code,
                        "predicted_cypher": None,
                        "gold_cypher": gold_cypher,
                    }
                )
                continue

        if status_code >= 500:
            matched = False
            excluded = False
        else:
            predicted_cypher = (payload.get("cypher") if isinstance(payload, dict) else "") or ""
            predicted_norm = normalize_cypher(predicted_cypher)
            gold_norm = normalize_cypher(gold_cypher)
            matched = predicted_norm == gold_norm
            excluded = False

        denominator += 1
        if matched:
            matched_count += 1

        per_question_results.append(
            {
                "question_id": question_id,
                "matched": matched,
                "excluded": excluded,
                "status_code": status_code,
                "predicted_cypher": predicted_cypher if status_code < 500 else None,
                "gold_cypher": gold_cypher,
            }
        )

    exact_match_rate = matched_count / denominator if denominator else 0.0
    return exact_match_rate, per_question_results

"""RAG grounding-rate evaluation harness for the M11 Integration.

Methodology (RAG grounding rate -- citation-resolves-to-retrieved-chunk):

Filter to the question_ids in the gold fixture (`data/rag_questions.json`).
For each question: (i) call POST /rag/answer; (ii) read the candidate set
from the response's `retrieved` field (each entry carries a `chunk_id`).
A response is grounded iff (a) `response.citations` has length >= 1, AND
(b) every `chunk_id` in `response.citations` is in the candidate set for
the same question. Decline-exclusion: if
`response.answer` is exactly the canonical decline string (case-sensitive,
punctuation-sensitive, exact match against "I cannot answer this from the
available sources."), the question is excluded from the denominator (counted
as "declined", not "ungrounded"). Aggregate as grounding rate = grounded /
(total - declined). Threshold floor: grounding rate >= 0.85. Edge case: if
every question declines, the denominator is 0; the report writes `0.0 (all
declined)` rather than dividing by zero.

This methodology paragraph appears verbatim in the integration spec, the
learner Integration Task page, and this docstring -- per the Evaluation
Methodology Rule.
"""

import json
import os
from typing import Tuple

import httpx

from lib.grounding_scorer import is_decline, is_grounded


API_URL = os.environ.get("API_URL", "http://localhost:8000")
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "data", "rag_questions.json")


def load_fixture():
    """Return the gold fixture as a list of {question_id, question, k, ...}."""
    with open(FIXTURE_PATH) as fh:
        return json.load(fh)


def run() -> Tuple[float, list]:
    """Run the harness end-to-end. Returns (grounding_rate, per_question_results)."""
    fixture = load_fixture()
    per_question_results = []
    grounded_count = 0
    denominator = 0

    for row in fixture:
        question_id = row["question_id"]
        question = row.get("question", "")
        k = row.get("k", 4)

        response = httpx.post(
            f"{API_URL}/rag/answer",
            json={"question": question, "k": k},
            timeout=60.0,
        )
        payload = response.json() if hasattr(response, "json") else {}
        status_code = getattr(response, "status_code", 200)

        if status_code >= 500:
            grounded = False
            declined = False
            excluded = False
        else:
            declined = is_decline(payload)
            if declined:
                excluded = True
            else:
                candidate_ids = []
                retrieved = payload.get("retrieved", []) or []
                for item in retrieved:
                    if isinstance(item, dict):
                        chunk_id = item.get("chunk_id")
                    else:
                        chunk_id = item
                    if chunk_id is not None:
                        candidate_ids.append(str(chunk_id))
                grounded = is_grounded(payload, candidate_ids)
                excluded = False

        if not excluded:
            denominator += 1
            if grounded:
                grounded_count += 1

        per_question_results.append(
            {
                "question_id": question_id,
                "grounded": grounded,
                "declined": declined,
                "excluded": excluded,
                "status_code": status_code,
                "citations": payload.get("citations", []) if isinstance(payload, dict) else [],
            }
        )

    grounding_rate = grounded_count / denominator if denominator else 0.0
    return grounding_rate, per_question_results

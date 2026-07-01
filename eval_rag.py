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
    # TODO: implement per the methodology.
    # Steps:
    #   1. Load the fixture.
    #   2. For each question, POST /rag/answer with the question and k.
    #   3. Check is_decline first; if True, exclude from denominator.
    #   4. Otherwise, gather the candidate_ids from the response's
    #      `retrieved` field, call lib.grounding_scorer.is_grounded.
    #   5. Aggregate grounding_rate = grounded / (total - declined).
    raise NotImplementedError

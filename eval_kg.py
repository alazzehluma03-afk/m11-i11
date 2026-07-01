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
    # TODO: implement per the methodology.
    # Steps:
    #   1. Load the fixture.
    #   2. For each question, POST /kg/query with {"question": q}.
    #   3. If the response is 422 with UnsupportedQueryError, mark the question
    #      "excluded" -- do not count it in the denominator.
    #   4. Otherwise, read the returned cypher field, normalize both predicted
    #      and gold via lib.cypher_normalizer.normalize_cypher, compare.
    #   5. Aggregate exact-match rate = matched / (total - excluded).
    raise NotImplementedError

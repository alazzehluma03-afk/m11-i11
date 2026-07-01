"""Autograder for the M11 Integration: Compose Evaluation.

This file maps to the Section H test plan in build-packet.md. Tests fall into
four groups:

  1. Report structure   -- the generated reports/evaluation-report.md exists
     and contains the required sections.
  2. Floor checks       -- the three headline numbers meet their floors.
  3. Unit checks        -- lib/{ner_scorer,cypher_normalizer,grounding_scorer}
     each correctly implement the methodology.
  4. Discipline checks  -- methodology paragraphs match across docstring + spec
     + guide; learner test file structurally complete.

The report-related tests parse `reports/evaluation-report.md`; if the file
does not exist (unmodified starter), the parse-related tests fail.

`test_learner_test_complete` is in this file because it is part of the
autograder's deliverable.
"""
from __future__ import annotations

import ast
import os
import re

import pytest


REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
REPORT_PATH = os.path.join(REPO_ROOT, "reports", "evaluation-report.md")
LEARNER_TEST_FILE = os.path.join(
    os.path.dirname(__file__), "test_learner_methodology.py"
)

MIN_LEARNER_TESTS = 3

NER_F1_FLOOR = 0.65
KG_EM_FLOOR = 0.80
RAG_GROUNDING_FLOOR = 0.85


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_report() -> str:
    if not os.path.exists(REPORT_PATH):
        pytest.fail(
            f"Missing report: {REPORT_PATH}. Run `python eval_runner.py "
            f"--output reports/evaluation-report.md` and commit the result."
        )
    with open(REPORT_PATH) as fh:
        return fh.read()


def _parse_headline_floats(body: str) -> dict:
    """Extract the three headline numbers from the `## Headline` section."""
    headline_match = re.search(r"## Headline(.*?)(?=^## |\Z)", body, re.DOTALL | re.MULTILINE)
    if not headline_match:
        return {}
    chunk = headline_match.group(1)
    results = {}
    patterns = {
        "ner_f1": r"NER F1[^0-9]*([0-9]+\.[0-9]+)",
        "kg_em": r"(?:NL\s*(?:->|→)?\s*Cypher|KG)[^0-9]*([0-9]+\.[0-9]+)",
        "rag_grounding": r"(?:RAG|[Gg]rounding)[^0-9]*([0-9]+\.[0-9]+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, chunk)
        if m:
            results[key] = float(m.group(1))
    return results


# ---------------------------------------------------------------------------
# Report structure
# ---------------------------------------------------------------------------

def test_report_file_present():
    """`reports/evaluation-report.md` exists."""
    assert os.path.exists(REPORT_PATH), (
        f"Missing {REPORT_PATH}. Did you run eval_runner.py and commit the report?"
    )


def test_report_has_three_headlines():
    """Report contains the three headline metric numbers in `## Headline`."""
    body = _read_report()
    headlines = _parse_headline_floats(body)
    missing = [k for k in ("ner_f1", "kg_em", "rag_grounding") if k not in headlines]
    assert not missing, (
        f"Headline section missing or unparseable for: {missing}. "
        "The `## Headline` section must contain NER F1, NL->Cypher EM, and RAG "
        "grounding rate as parseable floats."
    )


def test_per_question_table_present():
    """Report contains a per-question table for each endpoint.

    The spec calls for one per-question table per endpoint (NER, KG, RAG).
    Counting all `|`-prefixed lines is too lenient -- a single long table
    covering one endpoint would pass with row_count >= 3. Instead, require
    each endpoint section name to appear in the report AND that a Markdown
    table follows it.
    """
    body = _read_report()
    endpoint_section_markers = (
        # endpoint label that must precede a per-question table
        ("/extract", "NER"),
        ("/kg/query", "KG"),
        ("/rag/answer", "RAG"),
    )
    missing = []
    for marker, label in endpoint_section_markers:
        # The report must mention the endpoint (or its label) AND have at
        # least one Markdown table header line somewhere after that mention.
        if marker not in body and label not in body:
            missing.append(marker)
            continue
        idx = body.find(marker)
        if idx == -1:
            idx = body.find(label)
        tail = body[idx:]
        # Look for a Markdown table header within ~80 lines after the marker.
        header_re = re.compile(r"^\|.+\|.+\|", re.MULTILINE)
        if not header_re.search(tail.split("\n\n## ")[0]):
            missing.append(marker)
    assert not missing, (
        f"Report does not contain a per-question table after the section for: "
        f"{missing}. The spec calls for one per-endpoint per-question table "
        f"(NER on /extract, KG on /kg/query, RAG on /rag/answer)."
    )


def test_metrics_signals_in_report():
    """Report includes p95, error rate, total request count per endpoint."""
    body = _read_report()
    text = body.lower()
    required = ("p95", "error rate", "request count")
    missing = [r for r in required if r not in text]
    endpoints = ("/extract", "/kg/query", "/rag/answer")
    missing_eps = [ep for ep in endpoints if ep not in body]
    assert not missing, (
        f"Report missing required derived signals: {missing}. The "
        "`## Derived /metrics Signals` section must include p95, error rate, "
        "and request count per endpoint."
    )
    assert not missing_eps, (
        f"Report missing references to endpoints: {missing_eps}. The "
        "derived-signals section must report each endpoint."
    )


# ---------------------------------------------------------------------------
# Floor checks
# ---------------------------------------------------------------------------

def test_ner_floor_met():
    """NER F1 >= 0.65."""
    body = _read_report()
    headlines = _parse_headline_floats(body)
    f1 = headlines.get("ner_f1")
    assert f1 is not None, "NER F1 not parseable from report Headline section."
    assert f1 >= NER_F1_FLOOR, f"NER F1 floor not met: {f1} < {NER_F1_FLOOR}"


def test_kg_floor_met():
    """NL->Cypher exact-match >= 0.80."""
    body = _read_report()
    headlines = _parse_headline_floats(body)
    em = headlines.get("kg_em")
    assert em is not None, "KG exact-match not parseable from report Headline section."
    assert em >= KG_EM_FLOOR, f"KG EM floor not met: {em} < {KG_EM_FLOOR}"


def test_rag_floor_met():
    """RAG grounding rate >= 0.85."""
    body = _read_report()
    headlines = _parse_headline_floats(body)
    gr = headlines.get("rag_grounding")
    assert gr is not None, "RAG grounding rate not parseable from report Headline section."
    assert gr >= RAG_GROUNDING_FLOOR, (
        f"RAG grounding floor not met: {gr} < {RAG_GROUNDING_FLOOR}"
    )


# ---------------------------------------------------------------------------
# Unit checks
# ---------------------------------------------------------------------------

def test_ner_scorer_micro_f1():
    """`lib.ner_scorer.compute_micro_f1` returns the expected F1 on a synthetic fixture.

    Catches buggy variant: macro vs micro; partial-match vs exact-match.
    """
    from lib.ner_scorer import compute_micro_f1

    # 3 docs. Doc1: TP=2, FP=0, FN=0. Doc2: TP=1, FP=1, FN=1. Doc3: TP=0, FP=0, FN=2.
    # Micro: TP=3, FP=1, FN=3. P=3/4=0.75, R=3/6=0.5, F1=0.6.
    pred = {
        "d1": [{"entity_text": "Acme", "entity_label": "ORG"},
               {"entity_text": "Boston", "entity_label": "LOC"}],
        "d2": [{"entity_text": "Jane", "entity_label": "PER"},
               {"entity_text": "Wrong", "entity_label": "ORG"}],
        "d3": [],
    }
    gold = {
        "d1": [{"entity_text": "Acme", "entity_label": "ORG"},
               {"entity_text": "Boston", "entity_label": "LOC"}],
        "d2": [{"entity_text": "Jane", "entity_label": "PER"},
               {"entity_text": "Missing", "entity_label": "ORG"}],
        "d3": [{"entity_text": "Tokyo", "entity_label": "LOC"},
               {"entity_text": "Sony", "entity_label": "ORG"}],
    }
    p, r, f1 = compute_micro_f1(pred, gold)
    assert abs(p - 0.75) < 1e-3, f"Expected precision ~0.75, got {p}"
    assert abs(r - 0.5) < 1e-3, f"Expected recall ~0.5, got {r}"
    assert abs(f1 - 0.6) < 1e-3, f"Expected F1 ~0.6, got {f1}"


def test_cypher_normalizer_whitespace():
    """`lib.cypher_normalizer.normalize_cypher` collapses whitespace + uppercases keywords.

    Catches buggy variant: normalization missing.
    """
    from lib.cypher_normalizer import normalize_cypher

    a = "match   (r:Restaurant)\n  return  r.name"
    b = "MATCH (r:Restaurant) RETURN r.name"
    assert normalize_cypher(a) == normalize_cypher(b), (
        f"Whitespace + keyword case differences should normalize equal. "
        f"normalize_cypher(a) = {normalize_cypher(a)!r}; "
        f"normalize_cypher(b) = {normalize_cypher(b)!r}"
    )


def test_cypher_normalizer_uppercases_keywords():
    """Normalized output uppercases the full keyword set the guide names.

    Catches buggy variant: only some keywords are uppercased, or the
    normalizer touches whitespace but not case (a half implementation
    that the whitespace-equality test above does not catch).
    """
    from lib.cypher_normalizer import normalize_cypher

    raw = "match (r:Restaurant) where r.city = 'X' optional match (r)-[:SERVES]->(c) with r, c return r.name order by r.rating desc limit 5"
    out = normalize_cypher(raw)
    for kw in ("MATCH", "WHERE", "OPTIONAL", "WITH", "RETURN", "ORDER BY", "LIMIT"):
        assert kw in out, (
            f"Normalized output is missing uppercase keyword {kw!r}. The "
            "normalizer must uppercase MATCH, RETURN, WHERE, OPTIONAL, WITH, "
            "ORDER BY, LIMIT (and the rest of the documented keyword list)."
        )


def test_grounding_scorer_denominator_excludes_declines():
    """A 10-answered / 5-declined fixture aggregates to denominator = 10.

    Catches buggy variant: harness divides grounded by total, not by
    (total - declined). The guide's Step 6 specifies this anchor (10
    answered + 5 declined -> denominator 10).
    """
    from lib.grounding_scorer import is_decline

    decline_str = "I cannot answer this from the available sources."
    answered = [{"answer": "X", "citations": [{"chunk_id": "c1"}]}] * 10
    declined = [{"answer": decline_str, "citations": []}] * 5
    population = answered + declined
    denom = sum(1 for r in population if not is_decline(r))
    assert denom == 10, (
        f"Expected denominator = 10 (answered) after excluding 5 declines; "
        f"got {denom}. The grounding rate is grounded / (total - declined)."
    )


def test_grounding_scorer_excludes_declines():
    """`lib.grounding_scorer.is_decline` matches the canonical decline string exactly.

    Catches buggy variant: decline-exclusion bug.
    """
    from lib.grounding_scorer import is_decline

    decline = {"answer": "I cannot answer this from the available sources."}
    not_decline = {"answer": "I cannot answer that from these sources."}
    not_decline_2 = {"answer": "Acme Bistro serves Italian food."}

    assert is_decline(decline) is True
    assert is_decline(not_decline) is False, (
        "is_decline must use exact (case- and punctuation-sensitive) match on "
        "the canonical decline string."
    )
    assert is_decline(not_decline_2) is False


def test_grounding_scorer_membership():
    """`lib.grounding_scorer.is_grounded` requires every cited chunk_id to be
    in the candidate set, not just that citations is non-empty.

    Catches buggy variant: harness checks only condition (a) (citations
    length >= 1) and skips condition (b) (every cited chunk_id in the
    candidate set). Without condition (b), a response that cites a
    chunk_id not present in `retrieved` would be scored as grounded --
    defeating the entire grounding methodology.
    """
    from lib.grounding_scorer import is_grounded

    # Grounded: both citations resolve into the candidate set.
    grounded_response = {
        "answer": "Acme Bistro serves Italian.",
        "citations": [{"chunk_id": "chunk-1"}, {"chunk_id": "chunk-2"}],
    }
    candidates = {"chunk-1", "chunk-2", "chunk-3"}
    assert is_grounded(grounded_response, candidates) is True, (
        "is_grounded must return True when every cited chunk_id is in the "
        "candidate set."
    )

    # Ungrounded -- citation references a chunk_id NOT in the candidate set.
    # This is the trap: a learner who only checks `len(citations) >= 1`
    # passes the case where the model fabricates a citation id.
    ungrounded_response = {
        "answer": "Acme Bistro serves Italian.",
        "citations": [{"chunk_id": "chunk-1"}, {"chunk_id": "ghost-chunk"}],
    }
    assert is_grounded(ungrounded_response, candidates) is False, (
        "is_grounded returned True on a response whose citation list contains "
        "a chunk_id NOT in the candidate set. This is the silent-pass path: "
        "condition (b) of the methodology requires every cited chunk_id to "
        "be in the candidate set, not just citations to be non-empty."
    )

    # Ungrounded -- no citations.
    no_citations = {"answer": "Acme Bistro serves Italian.", "citations": []}
    assert is_grounded(no_citations, candidates) is False, (
        "is_grounded must return False when citations is empty (condition (a))."
    )


# ---------------------------------------------------------------------------
# Discipline checks
# ---------------------------------------------------------------------------

def test_methodology_stated_in_three_places():
    """Each eval_*.py docstring carries the methodology paragraph's canonical key phrases.

    Catches buggy variant: methodology paragraphs differ across docstring /
    spec / guide.
    """
    expected = {
        "eval_ner.py": [
            "micro-averaged",
            "F1 >= 0.65",
            "entity_text",
            "entity_label",
        ],
        "eval_kg.py": [
            "exact-match >= 0.80",
            "UnsupportedQueryError",
            "case-insensitive",
        ],
        "eval_rag.py": [
            "grounding rate >= 0.85",
            "canonical decline",
            "candidate set",
        ],
    }
    for filename, phrases in expected.items():
        path = os.path.join(REPO_ROOT, filename)
        assert os.path.exists(path), f"Missing harness file: {path}"
        with open(path) as fh:
            text = fh.read()
        missing = [p for p in phrases if p not in text]
        assert not missing, (
            f"{filename} docstring is missing canonical methodology phrases: "
            f"{missing}. The methodology paragraph must appear verbatim from "
            f"the integration spec (Evaluation Methodology Rule)."
        )


# ---------------------------------------------------------------------------
# Orchestration check -- eval_runner actually invokes the three harnesses + reader
# ---------------------------------------------------------------------------

def test_eval_runner_orchestrates_harnesses(tmp_path, monkeypatch):
    """`eval_runner.main` calls eval_ner.run / eval_kg.run / eval_rag.run and
    threads each harness's result + the /metrics signals into the written report.

    Catches buggy variant: `eval_runner.main` / `assemble_report` remains
    NotImplemented, writes hardcoded numbers, or fabricates a report without
    actually invoking the three harnesses or the metrics_reader accessors.
    """
    import eval_runner
    import eval_ner
    import eval_kg
    import eval_rag
    from lib import metrics_reader

    # Sentinel values are uniquely-shaped floats and counts so the assertions
    # below cannot pass against fabricated/hardcoded numbers.
    NER_P, NER_R, NER_F1 = 0.7137, 0.6913, 0.7023
    KG_EM = 0.8473
    RAG_GR = 0.9241
    P95_BY_PATH = {"/extract": 0.4271, "/kg/query": 0.5183, "/rag/answer": 1.7395}
    ERR_BY_PATH = {"/extract": 0.0131, "/kg/query": 0.0277, "/rag/answer": 0.0419}
    CNT_BY_PATH = {"/extract": 137.0, "/kg/query": 152.0, "/rag/answer": 168.0}

    monkeypatch.setattr(
        eval_ner, "run",
        lambda: (NER_P, NER_R, NER_F1, [{"doc_id": "d1", "f1": 0.71}]),
    )
    monkeypatch.setattr(
        eval_kg, "run",
        lambda: (KG_EM, [{"question_id": "q1", "match": True}]),
    )
    monkeypatch.setattr(
        eval_rag, "run",
        lambda: (RAG_GR, [{"question_id": "q1", "grounded": True}]),
    )
    monkeypatch.setattr(
        metrics_reader, "get_p95_latency",
        lambda path, body=None: P95_BY_PATH.get(path, 0.0),
    )
    monkeypatch.setattr(
        metrics_reader, "get_error_rate",
        lambda path, body=None: ERR_BY_PATH.get(path, 0.0),
    )
    monkeypatch.setattr(
        metrics_reader, "get_request_count",
        lambda path, body=None: CNT_BY_PATH.get(path, 0.0),
    )
    monkeypatch.setattr(
        metrics_reader, "scrape_metrics",
        lambda api_url=None: "# stubbed /metrics body",
    )

    output_path = tmp_path / "evaluation-report.md"
    exit_code = eval_runner.main(["--output", str(output_path)])

    assert exit_code == 0, (
        f"eval_runner.main should return 0 on success; returned {exit_code!r}."
    )
    assert output_path.exists(), (
        f"eval_runner.main should write the report to --output; "
        f"{output_path} does not exist."
    )

    report = output_path.read_text()

    # The harness sentinels must surface in the report -- proves eval_*.run()
    # were actually called and their outputs threaded through assemble_report.
    # All three NER outputs (P, R, F1) must surface -- a learner whose
    # assemble_report drops precision/recall and only writes F1 would still
    # pass the prior check.
    for label, sentinel in (("NER P", NER_P), ("NER R", NER_R), ("NER F1", NER_F1)):
        assert (
            f"{sentinel:.2f}" in report
            or f"{sentinel:.3f}" in report
            or f"{sentinel:.4f}" in report
            or str(sentinel) in report
        ), (
            f"Report does not contain the {label} sentinel {sentinel}. "
            "eval_ner.run() returns (precision, recall, F1) -- all three must "
            "surface in the report, not just F1."
        )
    assert f"{KG_EM:.2f}" in report or f"{KG_EM:.3f}" in report or f"{KG_EM:.4f}" in report or str(KG_EM) in report, (
        f"Report does not contain the KG EM sentinel {KG_EM}. eval_kg.run() "
        "was either not called or its result was not threaded into the report."
    )
    assert f"{RAG_GR:.2f}" in report or f"{RAG_GR:.3f}" in report or f"{RAG_GR:.4f}" in report or str(RAG_GR) in report, (
        f"Report does not contain the RAG grounding sentinel {RAG_GR}. "
        "eval_rag.run() was either not called or its result was not threaded "
        "into the report."
    )

    # At least one p95 / error-rate / request-count sentinel per endpoint must
    # appear -- proves metrics_reader accessors were called and their outputs
    # surfaced in the Derived /metrics Signals section.
    for path, p95 in P95_BY_PATH.items():
        formatted = [f"{p95:.2f}", f"{p95:.3f}", f"{p95:.4f}", str(p95)]
        assert any(s in report for s in formatted), (
            f"Report does not contain the p95 sentinel {p95} for {path}. "
            "metrics_reader.get_p95_latency was not called or its value was "
            "not surfaced in the report."
        )
    for path, cnt in CNT_BY_PATH.items():
        formatted = [str(int(cnt)), f"{cnt:.0f}", f"{cnt}"]
        assert any(s in report for s in formatted), (
            f"Report does not contain the request-count sentinel {cnt} for "
            f"{path}. metrics_reader.get_request_count was not called or its "
            "value was not surfaced in the report."
        )
    for path, err in ERR_BY_PATH.items():
        formatted = [f"{err:.2f}", f"{err:.3f}", f"{err:.4f}", str(err), f"{err * 100:.1f}", f"{err * 100:.2f}"]
        assert any(s in report for s in formatted), (
            f"Report does not contain the error-rate sentinel {err} for {path}. "
            "metrics_reader.get_error_rate was not called or its value was not "
            "surfaced in the report."
        )


# ---------------------------------------------------------------------------
# Focused per-harness checks -- prove each eval_*.run() actually calls the
# endpoint, applies the documented methodology (422 exclusion / decline
# exclusion / per-doc aggregation), and returns per-question detail rather
# than hardcoded numbers. Stubs `httpx.post` + `load_fixture` per harness.
# ---------------------------------------------------------------------------


class _StubResponse:
    """Minimal httpx.Response stand-in for monkeypatched httpx.post."""

    def __init__(self, status_code=200, json_body=None):
        self.status_code = status_code
        self._json = json_body if json_body is not None else {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            request = httpx.Request("POST", "http://stub")
            raise httpx.HTTPStatusError(
                f"{self.status_code}", request=request,
                response=self,  # type: ignore[arg-type]
            )


def test_eval_ner_run_calls_extract_and_scores_fixture(monkeypatch):
    """`eval_ner.run` POSTs to `/extract` for each fixture row, scores returned
    entities via compute_micro_f1, and returns per-document detail.

    Catches buggy variant: `eval_ner.run` returns hardcoded numbers, never
    calls `/extract`, or skips per-document aggregation.
    """
    import httpx
    import eval_ner

    fixture = [
        {"document_id": "d1", "text": "Acme is based in Boston.",
         "gold_entities": [
             {"entity_text": "Acme", "entity_label": "ORG"},
             {"entity_text": "Boston", "entity_label": "LOC"},
         ]},
        {"document_id": "d2", "text": "Jane works at Sony.",
         "gold_entities": [
             {"entity_text": "Jane", "entity_label": "PER"},
             {"entity_text": "Sony", "entity_label": "ORG"},
         ]},
    ]
    monkeypatch.setattr(eval_ner, "load_fixture", lambda: fixture)

    by_text = {row["text"]: row["gold_entities"] for row in fixture}
    calls = []

    def fake_post(url, json=None, **kwargs):
        calls.append((url, json))
        text = (json or {}).get("text", "")
        return _StubResponse(200, {"entities": by_text.get(text, [])})

    monkeypatch.setattr(httpx, "post", fake_post)

    result = eval_ner.run()

    assert any("/extract" in str(url) for url, _ in calls), (
        "eval_ner.run must POST to /extract for each fixture row. "
        f"Observed calls: {calls!r}"
    )
    assert len(calls) >= len(fixture), (
        f"eval_ner.run made {len(calls)} POSTs for {len(fixture)} fixture rows; "
        "each row must call /extract."
    )

    assert isinstance(result, tuple) and len(result) == 4, (
        "eval_ner.run must return (precision, recall, f1, per_doc_results)."
    )
    precision, recall, f1, per_doc = result
    assert per_doc, "eval_ner.run must return per-document results, not [] or None."
    assert abs(f1 - 1.0) < 1e-6, (
        f"With predictions == gold for every doc, micro F1 must be 1.0; got {f1!r}. "
        "This indicates eval_ner.run is returning hardcoded numbers or not "
        "calling compute_micro_f1 on the live API response."
    )


def test_eval_kg_run_calls_kg_query_and_excludes_422(monkeypatch):
    """`eval_kg.run` POSTs to `/kg/query`, normalizes Cypher, and excludes
    HTTP 422 UnsupportedQueryError rows from the denominator.

    Catches buggy variant: `eval_kg.run` counts 422 rows as failures (denominator
    not adjusted), skips normalization, or returns a hardcoded rate.
    """
    import httpx
    import eval_kg

    fixture = [
        {"question_id": "q1", "question": "Q1?", "gold_cypher": "MATCH (r) RETURN r"},
        {"question_id": "q2", "question": "Q2?", "gold_cypher": "MATCH (n) RETURN n"},
        {"question_id": "q3", "question": "Q3?", "gold_cypher": "MATCH (x) RETURN x"},
    ]
    monkeypatch.setattr(eval_kg, "load_fixture", lambda: fixture)

    by_q = {row["question"]: row for row in fixture}
    calls = []

    def fake_post(url, json=None, **kwargs):
        calls.append((url, json))
        question = (json or {}).get("question", "")
        if question == "Q3?":
            return _StubResponse(422, {
                "detail": {"reason": "UnsupportedQueryError",
                           "message": "not supported"}
            })
        # Return the gold (with deliberate whitespace) so the normalizer is exercised.
        cypher = by_q[question]["gold_cypher"].replace(" ", "  ")
        return _StubResponse(200, {"cypher": cypher, "results": []})

    monkeypatch.setattr(httpx, "post", fake_post)

    result = eval_kg.run()

    assert any("/kg/query" in str(url) for url, _ in calls), (
        "eval_kg.run must POST to /kg/query for each fixture row. "
        f"Observed calls: {calls!r}"
    )

    assert isinstance(result, tuple) and len(result) == 2, (
        "eval_kg.run must return (exact_match_rate, per_question_results)."
    )
    em, per_q = result
    assert per_q, "eval_kg.run must return per-question results."
    # 2 of 3 questions answered; both match gold. 1 returns 422 (excluded).
    # Correct rate = 2/2 = 1.0. If the harness counted 422 as failure, rate = 2/3.
    assert abs(em - 1.0) < 1e-6, (
        f"Expected EM = 1.0 (2 matches / 2 supported; 1 UnsupportedQueryError "
        f"excluded). Got {em!r}. Likely cause: 422 row counted in denominator "
        "or normalize_cypher not applied."
    )


def test_eval_rag_run_calls_rag_answer_and_excludes_declines(monkeypatch):
    """`eval_rag.run` POSTs to `/rag/answer` and excludes canonical-decline
    responses from the grounding-rate denominator.

    Catches buggy variant: `eval_rag.run` counts declines as ungrounded
    (denominator not adjusted), skips grounding check, or hardcodes the rate.
    """
    import httpx
    import eval_rag

    fixture = [
        {"question_id": "r1", "question": "R1?", "k": 4,
         "gold_citation_chunk_ids": ["c1", "c2"]},
        {"question_id": "r2", "question": "R2?", "k": 4,
         "gold_citation_chunk_ids": ["c3"]},
        {"question_id": "r3", "question": "R3?", "k": 4,
         "gold_citation_chunk_ids": ["c9"]},
    ]
    monkeypatch.setattr(eval_rag, "load_fixture", lambda: fixture)

    DECLINE = "I cannot answer this from the available sources."
    calls = []

    def fake_post(url, json=None, **kwargs):
        calls.append((url, json))
        q = (json or {}).get("question", "")
        if q == "R3?":
            return _StubResponse(200, {
                "answer": DECLINE, "citations": [], "retrieved": [],
            })
        gold = {row["question"]: row["gold_citation_chunk_ids"] for row in fixture}
        chunk_ids = gold[q]
        return _StubResponse(200, {
            "answer": "ok",
            "citations": [{"chunk_id": cid} for cid in chunk_ids],
            "retrieved": [{"chunk_id": cid} for cid in chunk_ids],
        })

    monkeypatch.setattr(httpx, "post", fake_post)

    result = eval_rag.run()

    assert any("/rag/answer" in str(url) for url, _ in calls), (
        "eval_rag.run must POST to /rag/answer for each fixture row. "
        f"Observed calls: {calls!r}"
    )

    assert isinstance(result, tuple) and len(result) == 2, (
        "eval_rag.run must return (grounding_rate, per_question_results)."
    )
    rate, per_q = result
    assert per_q, "eval_rag.run must return per-question results."
    # 2 grounded / 2 non-declined = 1.0. If declines were counted, rate = 2/3.
    assert abs(rate - 1.0) < 1e-6, (
        f"Expected grounding rate = 1.0 (2 grounded / 2 non-declined; 1 decline "
        f"excluded). Got {rate!r}. Likely cause: decline counted in denominator "
        "or is_grounded not applied."
    )


# ---------------------------------------------------------------------------
# Learner-Written Test Rule (AST check)
# ---------------------------------------------------------------------------

def _function_has_assertion(node: ast.FunctionDef) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assert):
            return True
    return False


def _function_is_bare_pass(node: ast.FunctionDef) -> bool:
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    return len(body) == 1 and isinstance(body[0], ast.Pass)


def _function_has_not_implemented_placeholder(node: ast.FunctionDef) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            is_pytest_fail = (
                isinstance(func, ast.Attribute)
                and func.attr == "fail"
                and isinstance(func.value, ast.Name)
                and func.value.id == "pytest"
            )
            if is_pytest_fail and sub.args:
                first = sub.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    if "not implemented" in first.value.lower():
                        return True
    return False


def test_learner_test_complete():
    """`tests/test_learner_methodology.py` has >= 3 substantive test functions."""
    assert os.path.exists(LEARNER_TEST_FILE), (
        f"Missing learner test file: {LEARNER_TEST_FILE}"
    )
    with open(LEARNER_TEST_FILE) as fh:
        tree = ast.parse(fh.read(), filename=LEARNER_TEST_FILE)

    test_funcs = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert len(test_funcs) >= MIN_LEARNER_TESTS, (
        f"tests/test_learner_methodology.py has {len(test_funcs)} test "
        f"functions; required at least {MIN_LEARNER_TESTS}."
    )

    problems = []
    for fn in test_funcs:
        if _function_is_bare_pass(fn):
            problems.append(f"{fn.name}: body is bare `pass`")
            continue
        if _function_has_not_implemented_placeholder(fn):
            problems.append(f"{fn.name}: still contains `pytest.fail(\"Not implemented...\")` placeholder")
            continue
        if not _function_has_assertion(fn):
            problems.append(f"{fn.name}: has no `assert` statement")

    assert not problems, "Learner test issues:\n  - " + "\n  - ".join(problems)

    # Guide Step 6 specifies coverage of all three lib scorer modules.
    # Require each module to be actually imported or called from inside a
    # test function -- a bare comment that names the modules no longer
    # satisfies this check, which was the prior loophole.
    expected_modules = ("ner_scorer", "cypher_normalizer", "grounding_scorer")
    imported = set()
    referenced_in_tests = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for name in expected_modules:
                if name in mod:
                    imported.add(name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                for name in expected_modules:
                    if name in alias.name:
                        imported.add(name)
        elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            # Search the function body for any Attribute/Name access that
            # references one of the module names.
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    for name in expected_modules:
                        if name in sub.id:
                            referenced_in_tests.add(name)
                elif isinstance(sub, ast.Attribute):
                    for name in expected_modules:
                        if name in sub.attr:
                            referenced_in_tests.add(name)
    covered = imported | referenced_in_tests
    uncovered = [m for m in expected_modules if m not in covered]
    assert not uncovered, (
        "tests/test_learner_methodology.py does not import or reference "
        f"these required lib modules from inside a test function: {uncovered}. "
        "The guide (Step 6) specifies coverage of all three: NER scorer "
        "(F1=1.0 on synthetic match, F1≈0.0 on disjoint), Cypher normalizer "
        "(whitespace collapse + keyword uppercase), and grounding scorer "
        "(decline-exclusion). Add a test that imports and calls into each."
    )

    # Tighten further: at least one assert per scorer must compare against a
    # numeric value the methodology calls out. The guide names specific
    # anchor values (F1 == 1.0, F1 < 0.1 / ≈ 0.0). Require at least one
    # numeric literal in the body of a test that names ner_scorer, and at
    # least one assert comparing to 0 / 1 truthy values for the cypher
    # normalizer (uppercase transformation produces a known string).
    ner_tests_have_numeric_compare = False
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
            continue
        names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
        if not any("ner_scorer" in s for s in names | attrs):
            continue
        # Check this test's asserts reference a numeric constant near 1.0 or 0.0.
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assert):
                for k in ast.walk(sub):
                    if isinstance(k, ast.Constant) and isinstance(k.value, (int, float)):
                        ner_tests_have_numeric_compare = True
    assert ner_tests_have_numeric_compare, (
        "At least one ner_scorer test must assert against a numeric F1 "
        "value (the guide names F1=1.0 on synthetic match and F1≈0.0 on "
        "disjoint predictions). A bare structural test that calls the "
        "scorer but does not check its output value does not exercise the "
        "methodology."
    )

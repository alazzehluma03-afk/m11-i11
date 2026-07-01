"""Pre-built M11-instrumented backend for the Integration.

The Integration is not gated on the Lab landing -- this file is the
reference-quality M11-instrumented backend (three middlewares + three metrics
+ /metrics mount). You read this for reference; you do NOT modify it for the
Integration deliverable.

For the Integration, your work is in `eval_ner.py`, `eval_kg.py`, `eval_rag.py`,
`eval_runner.py`, and `lib/{ner_scorer,cypher_normalizer,grounding_scorer}.py`.

Backend behavior (deterministic, fixture-driven). The endpoints are wired to
the same three fixtures the harnesses use under `data/`. When `/extract`,
`/kg/query`, or `/rag/answer` is called with input that matches a fixture
row, the endpoint returns the fixture's gold value (the gold entities, the
gold Cypher, or citations resolving to the gold retrieved chunk_ids); a
single fixture row in `data/kg_questions.json` is sentinel-marked as
unsupported and the endpoint returns the documented HTTP 422
`UnsupportedQueryError`. Inputs with no fixture match return the canonical
decline / unsupported / empty responses. A correctly-implemented harness run
against this backend therefore meets all three published floors
(NER F1 >= 0.65, NL->Cypher EM >= 0.80, RAG grounding >= 0.85); the work
the learner must do is the harness, not the backend.
"""
import json
import logging
import os
import time
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app


requests_total = Counter(
    "requests_total",
    "Total HTTP requests",
    ["path", "status"],
)

request_latency_seconds = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

inflight_requests = Gauge(
    "inflight_requests",
    "In-flight requests",
)


_request_id: ContextVar[str] = ContextVar("request_id", default="")
_logger = logging.getLogger("m11.api")


class RequestIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        rid = uuid.uuid4().hex
        token = _request_id.set(rid)

        async def send_with_header(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", rid.encode("ascii")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            _request_id.reset(token)


class StructuredLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = time.perf_counter()
        status_holder = {"status": 0}

        async def capture_status(message):
            if message["type"] == "http.response.start":
                status_holder["status"] = message.get("status", 0)
            await send(message)

        await self.app(scope, receive, capture_status)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        path = scope.get("path", "")
        _logger.info(json.dumps({
            "request_id": _request_id.get(""),
            "path": path,
            "status": status_holder["status"],
            "latency_ms": round(elapsed_ms, 3),
        }))


class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if path == "/metrics":
            await self.app(scope, receive, send)
            return
        inflight_requests.inc()
        start = time.perf_counter()
        status_holder = {"status": 0}

        async def capture_status(message):
            if message["type"] == "http.response.start":
                status_holder["status"] = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        finally:
            elapsed = time.perf_counter() - start
            inflight_requests.dec()
            requests_total.labels(path=path, status=str(status_holder["status"])).inc()
            request_latency_seconds.labels(path=path).observe(elapsed)


# ---------------------------------------------------------------------------
# Fixture loading -- the pre-built backend serves gold values for fixture
# matches so a correctly-implemented harness meets the published floors.
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DECLINE_STRING = "I cannot answer this from the available sources."

# A single sentinel question is wired to return HTTP 422 UnsupportedQueryError
# so the harness exercises the documented exclusion codepath. The fixture
# leaves the gold_cypher in place; the backend overrides the response to 422.
_UNSUPPORTED_KG_SENTINEL_QID = "kg-025"


def _load_json(name: str):
    with open(os.path.join(_DATA_DIR, name)) as fh:
        return json.load(fh)


try:
    _NER_BY_TEXT = {row["text"]: row["gold_entities"] for row in _load_json("ner_conll30.json")}
except FileNotFoundError:
    _NER_BY_TEXT = {}

try:
    _KG_BY_QUESTION = {row["question"]: row for row in _load_json("kg_questions.json")}
except FileNotFoundError:
    _KG_BY_QUESTION = {}

try:
    _RAG_BY_QUESTION = {row["question"]: row for row in _load_json("rag_questions.json")}
except FileNotFoundError:
    _RAG_BY_QUESTION = {}


app = FastAPI(title="M11 Backend (instrumented)")

# Order: last add_middleware is outermost in Starlette.
app.add_middleware(MetricsMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

app.mount("/metrics", make_asgi_app())


class ExtractRequest(BaseModel):
    text: str


class KGRequest(BaseModel):
    question: str


class RAGRequest(BaseModel):
    question: str
    k: int = 4


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


@app.post("/extract")
def extract(req: ExtractRequest):
    """Return gold_entities for fixture-matched text; else empty entities."""
    entities = _NER_BY_TEXT.get(req.text, [])
    return {"entities": entities}


@app.post("/kg/query")
def kg_query(req: KGRequest):
    """Return matching gold_cypher; sentinel returns 422 UnsupportedQueryError."""
    row = _KG_BY_QUESTION.get(req.question)
    if row is None:
        raise HTTPException(
            status_code=422,
            detail={
                "reason": "UnsupportedQueryError",
                "message": "question is not supported by the bounded schema",
            },
        )
    if row.get("question_id") == _UNSUPPORTED_KG_SENTINEL_QID:
        raise HTTPException(
            status_code=422,
            detail={
                "reason": "UnsupportedQueryError",
                "message": "question is not supported by the bounded schema",
            },
        )
    return {"cypher": row["gold_cypher"], "results": []}


@app.post("/rag/answer")
def rag_answer(req: RAGRequest):
    """Return citations that resolve to the gold retrieved chunk_ids.

    For fixture-matched questions the backend returns citations whose
    chunk_ids match the gold candidate set, so a correctly-implemented
    grounding-rate harness scores 1.0. For non-fixture questions the backend
    returns the canonical decline string (excluded from the denominator).
    """
    row = _RAG_BY_QUESTION.get(req.question)
    if row is None:
        return {
            "answer": DECLINE_STRING,
            "citations": [],
            "retrieved": [],
        }
    chunk_ids = row.get("gold_citation_chunk_ids", [])
    citations = [{"chunk_id": cid} for cid in chunk_ids]
    retrieved = [{"chunk_id": cid} for cid in chunk_ids]
    return {
        "answer": f"Match for question_id={row.get('question_id', '?')}.",
        "citations": citations,
        "retrieved": retrieved,
    }

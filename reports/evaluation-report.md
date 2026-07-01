## Headline
- NER Precision: 1.0000
- NER Recall: 1.0000
- NER F1: 1.0000
- NL->Cypher EM: 1.0000
- RAG grounding rate: 1.0000

## Per-Endpoint Detail
### /extract

| document_id | tp | fp | fn | precision | recall | f1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| doc-001 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-002 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-003 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-004 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-005 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-006 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-007 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-008 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-009 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-010 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-011 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-012 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-013 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-014 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-015 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-016 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-017 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-018 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-019 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-020 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-021 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-022 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-023 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-024 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-025 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-026 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-027 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-028 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-029 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
| doc-030 | 1.0 | 1.0 | 1.0 | 0.5000 | 0.5000 | 0.5000 |
Sample failures:
- No failure samples available.

### /kg/query

| question_id | matched | excluded | status_code |
| --- | --- | --- | ---: |
| kg-001 | True | False | 200 |
| kg-002 | True | False | 200 |
| kg-003 | True | False | 200 |
| kg-004 | True | False | 200 |
| kg-005 | True | False | 200 |
| kg-006 | True | False | 200 |
| kg-007 | True | False | 200 |
| kg-008 | True | False | 200 |
| kg-009 | True | False | 200 |
| kg-010 | True | False | 200 |
| kg-011 | True | False | 200 |
| kg-012 | True | False | 200 |
| kg-013 | True | False | 200 |
| kg-014 | True | False | 200 |
| kg-015 | True | False | 200 |
| kg-016 | True | False | 200 |
| kg-017 | True | False | 200 |
| kg-018 | True | False | 200 |
| kg-019 | True | False | 200 |
| kg-020 | True | False | 200 |
| kg-021 | True | False | 200 |
| kg-022 | True | False | 200 |
| kg-023 | True | False | 200 |
| kg-024 | True | False | 200 |
| kg-025 | False | True | 422 |
Sample failures:
- kg-025: {'question_id': 'kg-025', 'matched': False, 'excluded': True, 'status_code': 422, 'predicted_cypher': None, 'gold_cypher': 'MATCH (r:Restaurant) WHERE r.opened_year >= 2025 RETURN r.name'}

### /rag/answer

| question_id | grounded | declined | excluded |
| --- | --- | --- | --- |
| rag-001 | True | False | False |
| rag-002 | True | False | False |
| rag-003 | True | False | False |
| rag-004 | True | False | False |
| rag-005 | True | False | False |
| rag-006 | True | False | False |
| rag-007 | True | False | False |
| rag-008 | True | False | False |
| rag-009 | True | False | False |
| rag-010 | True | False | False |
| rag-011 | True | False | False |
| rag-012 | True | False | False |
| rag-013 | True | False | False |
| rag-014 | True | False | False |
| rag-015 | True | False | False |
| rag-016 | True | False | False |
| rag-017 | True | False | False |
| rag-018 | True | False | False |
| rag-019 | True | False | False |
| rag-020 | True | False | False |
Sample failures:
- No failure samples available.

## Methodologies
### NER
NER F1 evaluation harness for the M11 Integration.

Methodology (NER F1 -- token-level entity exact-match):

Filter the predictions to the document_ids present in the gold fixture
(`data/ner_conll30.json`); discard predictions for any other document_id. An
entity is a true positive (TP) iff a gold entity with the same `entity_text`
AND the same `entity_label` exists in the same `document_id` (string-equality
on `entity_text`; string-equality on `entity_label`; whitespace is not
normalized -- the M6 NER pipeline already returns trimmed entity text). An
entity in predictions with no matching gold entity is a false positive (FP).
A gold entity with no matching prediction is a false negative (FN). Compute
precision = TP / (TP + FP), recall = TP / (TP + FN), F1 = 2*P*R / (P + R).
Aggregate micro-averaged across documents -- sum TPs / FPs / FNs across all 30
documents, then compute. Threshold floor: F1 >= 0.65. NaN handling: if
TP + FP = 0, precision is 0; if TP + FN = 0, recall is 0; if both are 0, F1
is 0 (not NaN -- the report writes `0.0`, not `nan`).

This methodology paragraph appears verbatim in the integration spec, the
learner Integration Task page, and this docstring -- per the Evaluation
Methodology Rule.


### KG
NL -> Cypher exact-match evaluation harness for the M11 Integration.

Methodology (NL -> Cypher exact-match -- post-normalization string equality):

Filter predictions to the question_ids in the gold fixture
(`data/kg_questions.json`). Normalize both predicted Cypher and gold Cypher
using `re.sub(r"\s+", " ", s).strip()` (whitespace collapse + leading/trailing
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


### RAG
RAG grounding-rate evaluation harness for the M11 Integration.

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


## Derived /metrics Signals
- /extract: p95=0.0000, Error Rate=0.0000, Request Count=0; error rate=0.0000, request count=0
- /kg/query: p95=0.0000, Error Rate=0.0000, Request Count=0; error rate=0.0000, request count=0
- /rag/answer: p95=0.0000, Error Rate=0.0000, Request Count=0; error rate=0.0000, request count=0

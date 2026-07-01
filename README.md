# Module 11 — Integration Task: Compose Evaluation

Author an automated evaluation harness that runs against the live M11-instrumented M10 stack and produces a single Markdown report with three headline numbers — **NER F1**, **NL → Cypher exact-match**, **RAG grounding rate** — plus three derived `/metrics` signals per endpoint — **p95 latency**, **error rate**, **total request count**. Reproducible from one command.

The published Integration Task guide is the canonical task list. See TalentLMS → Module 11 → Integration Task for the link, or check your cohort's Slack pinned message.

## What ships here

```
.
├── api/                              pre-built M11-instrumented backend
│   ├── main.py
│   └── __init__.py
├── compose/
│   ├── docker-compose.yml            M10 stack with instrumented api
│   ├── .env.example
│   ├── seed_neo4j.sh
│   └── seed_weaviate.sh
├── data/
│   ├── ner_conll30.json              30 NER documents
│   ├── kg_questions.json             25 NL→Cypher pairs
│   └── rag_questions.json            20 RAG questions
├── eval_ner.py                       TODO: NER F1 harness
├── eval_kg.py                        TODO: NL->Cypher EM harness
├── eval_rag.py                       TODO: RAG grounding harness
├── eval_runner.py                    TODO: orchestrator + report writer
├── lib/
│   ├── metrics_reader.py             PROVIDED -- read this; do not modify
│   ├── ner_scorer.py                 TODO
│   ├── cypher_normalizer.py          TODO
│   └── grounding_scorer.py           TODO
├── reports/
│   └── .gitkeep                      evaluation-report.md lands here
├── tests/
│   ├── test_evaluation_harness.py    autograder
│   ├── test_learner_methodology.py   YOUR tests
│   └── conftest.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Setup

Use **Python 3.11** for this template (the pinned `pydantic==2.6.0` does not build on Python 3.13).

```bash
git checkout -b integration-11-compose-evaluation
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Bring up the stack

```bash
cp compose/.env.example compose/.env
docker compose -f compose/docker-compose.yml up -d
# Poll /readyz -- Neo4j takes ~30 s to come up on a cold start.
for i in $(seq 1 60); do
  if curl -fsS http://localhost:8000/readyz >/dev/null 2>&1; then
    echo "stack ready"; break
  fi
  sleep 1
done
bash compose/seed_neo4j.sh
bash compose/seed_weaviate.sh
```

## Run

```bash
python eval_runner.py --output reports/evaluation-report.md
pytest tests/ -v
```

## Submission

Open a PR within your fork. The PR description must include:

1. Confirmation that `python eval_runner.py` produces the report and all three floors are met.
2. The three headline numbers as Markdown copied from the report.
3. A short paragraph (~150 words) reflecting on one methodology decision you made.
4. Paste your PR URL into TalentLMS → Module 11 → Integration 11 to submit this assignment.

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.

"""Orchestrator -- runs the three eval harnesses, reads /metrics, writes report.

Usage:
    python eval_runner.py --output reports/evaluation-report.md
"""

import argparse
import os
import sys

import eval_ner
import eval_kg
import eval_rag
from lib import metrics_reader


def assemble_report(ner_result, kg_result, rag_result, metrics_signals) -> str:
    """Return the Markdown report body.

    Required sections (autograder checks):
      - ## Headline -- three parseable numbers (NER F1, KG EM, RAG grounding rate).
      - ## Methodologies -- the three methodology paragraphs (copy from
        eval_ner.py, eval_kg.py, eval_rag.py docstrings).
      - ## Per-Endpoint Detail -- per-question table + sample failures per
        endpoint.
      - ## Derived /metrics Signals -- p95 latency, error rate, total request
        count for each of /extract, /kg/query, /rag/answer.
    """
    # TODO: assemble the Markdown report. See the integration spec rubric and
    # the autograder test_evaluation_harness.py for what each section must
    # contain.
    raise NotImplementedError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="reports/evaluation-report.md",
        help="Where to write the Markdown report.",
    )
    args = parser.parse_args(argv)

    # TODO: run the three harnesses, read /metrics signals via metrics_reader,
    # assemble the report, write to args.output. Return 0 on success.
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())

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
    ner_precision, ner_recall, ner_f1, per_doc_results = ner_result
    kg_em, kg_results = kg_result
    rag_grounding, rag_results = rag_result

    def _format_row(items, key):
        return "\n".join(f"- {item[key]}" for item in items if key in item)

    def _failure_lines(items, field_name):
        failures = [item for item in items if not item.get(field_name, False)]
        if not failures:
            return ["- No failure samples available."]
        sample = failures[:3]
        return [f"- {item.get('question_id') or item.get('document_id')}: {item}" for item in sample]

    sections = []
    sections.append("## Headline")
    sections.append(f"- NER Precision: {ner_precision:.4f}")
    sections.append(f"- NER Recall: {ner_recall:.4f}")
    sections.append(f"- NER F1: {ner_f1:.4f}")
    sections.append(f"- NL->Cypher EM: {kg_em:.4f}")
    sections.append(f"- RAG grounding rate: {rag_grounding:.4f}")
    sections.append("")

    sections.append("## Per-Endpoint Detail")
    sections.append("### /extract")
    sections.append("")
    sections.append("| document_id | tp | fp | fn | precision | recall | f1 |")
    sections.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in per_doc_results:
        sections.append(
            f"| {item.get('document_id', '')} | {item.get('tp', 0)} | {item.get('fp', 0)} | {item.get('fn', 0)} | {item.get('precision', 0):.4f} | {item.get('recall', 0):.4f} | {item.get('f1', 0):.4f} |"
        )
    sections.append("Sample failures:")
    sections.extend(_failure_lines(per_doc_results, "f1"))
    sections.append("")

    sections.append("### /kg/query")
    sections.append("")
    sections.append("| question_id | matched | excluded | status_code |")
    sections.append("| --- | --- | --- | ---: |")
    for item in kg_results:
        sections.append(f"| {item.get('question_id', '')} | {item.get('matched', False)} | {item.get('excluded', False)} | {item.get('status_code', '')} |")
    sections.append("Sample failures:")
    sections.extend(_failure_lines(kg_results, "matched"))
    sections.append("")

    sections.append("### /rag/answer")
    sections.append("")
    sections.append("| question_id | grounded | declined | excluded |")
    sections.append("| --- | --- | --- | --- |")
    for item in rag_results:
        sections.append(f"| {item.get('question_id', '')} | {item.get('grounded', False)} | {item.get('declined', False)} | {item.get('excluded', False)} |")
    sections.append("Sample failures:")
    sections.extend(_failure_lines(rag_results, "grounded"))
    sections.append("")

    sections.append("## Methodologies")
    sections.append("### NER")
    sections.append(eval_ner.__doc__ or "")
    sections.append("")
    sections.append("### KG")
    sections.append(eval_kg.__doc__ or "")
    sections.append("")
    sections.append("### RAG")
    sections.append(eval_rag.__doc__ or "")
    sections.append("")

    sections.append("## Derived /metrics Signals")
    for endpoint, values in metrics_signals.items():
        sections.append(
            f"- {endpoint}: p95={values.get('p95', 0.0):.4f}, Error Rate={values.get('error_rate', 0.0):.4f}, Request Count={values.get('request_count', 0):.0f}; error rate={values.get('error_rate', 0.0):.4f}, request count={values.get('request_count', 0):.0f}"
        )

    return "\n".join(sections) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="reports/evaluation-report.md",
        help="Where to write the Markdown report.",
    )
    args = parser.parse_args(argv)

    ner_result = eval_ner.run()
    kg_result = eval_kg.run()
    rag_result = eval_rag.run()

    body = metrics_reader.scrape_metrics()
    metrics_signals = {
        "/extract": {
            "p95": metrics_reader.get_p95_latency("/extract", body=body),
            "error_rate": metrics_reader.get_error_rate("/extract", body=body),
            "request_count": metrics_reader.get_request_count("/extract", body=body),
        },
        "/kg/query": {
            "p95": metrics_reader.get_p95_latency("/kg/query", body=body),
            "error_rate": metrics_reader.get_error_rate("/kg/query", body=body),
            "request_count": metrics_reader.get_request_count("/kg/query", body=body),
        },
        "/rag/answer": {
            "p95": metrics_reader.get_p95_latency("/rag/answer", body=body),
            "error_rate": metrics_reader.get_error_rate("/rag/answer", body=body),
            "request_count": metrics_reader.get_request_count("/rag/answer", body=body),
        },
    }
    report_body = assemble_report(ner_result, kg_result, rag_result, metrics_signals)

    output_path = args.output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as fh:
        fh.write(report_body)
    return 0


if __name__ == "__main__":
    sys.exit(main())

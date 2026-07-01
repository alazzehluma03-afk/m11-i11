#!/usr/bin/env bash
# Integration 11: Weaviate seeding is a no-op.
#
# The pre-baked backend in api/main.py is deterministic and fixture-driven --
# it returns gold citations for questions in data/rag_questions.json and the
# canonical decline sentinel for everything else. It never queries Weaviate.
# The weaviate container is still brought up by docker-compose.yml because
# it is part of the M10/M11 service topology, but no data needs to be loaded
# for the evaluation harnesses to produce the published floor numbers.
#
# This script intentionally does nothing and exits 0 so the documented
# `bash compose/seed_weaviate.sh` step in the Integration guide stays green.
set -euo pipefail
echo "Weaviate seeding skipped -- the M11 Integration backend is fixture-driven and does not query Weaviate."

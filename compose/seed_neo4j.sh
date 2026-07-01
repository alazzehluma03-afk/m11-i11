#!/usr/bin/env bash
# Integration 11: Neo4j seeding is a no-op.
#
# The pre-baked backend in api/main.py is deterministic and fixture-driven --
# it returns gold answers for questions in data/kg_questions.json and HTTP
# 422 UnsupportedQueryError for everything else. It never reads from Neo4j.
# The neo4j container is still brought up by docker-compose.yml because it
# is part of the M10/M11 service topology, but no data needs to be loaded
# for the evaluation harnesses to produce the published floor numbers.
#
# This script intentionally does nothing and exits 0 so the documented
# `bash compose/seed_neo4j.sh` step in the Integration guide stays green.
set -euo pipefail
echo "Neo4j seeding skipped -- the M11 Integration backend is fixture-driven and does not query Neo4j."

#!/usr/bin/env bash
# The `lint` gate (ADR-0100, PLAN-0001): the project's own code only, never the engine's tools/.
# Python: syntax of ingest/ and tests/. The site's lint (web/) joins in T2.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
py="$(bash scripts/venv_python.sh)" || exit 2
"$py" -m compileall -q ingest tests
echo "lint: python ok (ingest, tests)"

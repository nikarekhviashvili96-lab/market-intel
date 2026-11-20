#!/usr/bin/env bash
# The `lint` gate (ADR-0100, PLAN-0001): the project's own code only, never the engine's tools/.
# Python: syntax of ingest/ and tests/. Site (web/, since T2): exact npm versions, ESLint and `tsc --noEmit`.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
py="$(bash scripts/venv_python.sh)" || exit 2
"$py" -m compileall -q ingest tests
echo "lint: python ok (ingest, tests)"
if [ ! -d web/node_modules ]; then
  echo "lint: web/node_modules missing: run 'npm --prefix web ci'" >&2
  exit 2
fi
npm --prefix web run --silent lint
echo "lint: web ok (exact versions, eslint, tsc)"

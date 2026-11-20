#!/usr/bin/env bash
# The `unit` gate (ADR-0100, PLAN-0001): pytest for the job (database tests skip without TEST_DATABASE_URL),
# then Vitest for the site (web/, since T2).
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
py="$(bash scripts/venv_python.sh)" || exit 2
"$py" -m pytest -q
if [ ! -d web/node_modules ]; then
  echo "unit: web/node_modules missing: run 'npm --prefix web ci'" >&2
  exit 2
fi
npm --prefix web run --silent test

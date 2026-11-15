#!/usr/bin/env bash
# The `unit` gate (ADR-0100, PLAN-0001): pytest for the job (database tests skip without TEST_DATABASE_URL).
# The site's Vitest run (web/) joins in T2.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
py="$(bash scripts/venv_python.sh)" || exit 2
"$py" -m pytest -q

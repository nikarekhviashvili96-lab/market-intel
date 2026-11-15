#!/usr/bin/env bash
# Creates the project's .venv with the engine's launcher and installs the pinned ingest/requirements.txt
# (ADR-0100 "install" step). One script for every place that needs it: CI (.github/workflows/gates.yml),
# a fresh clone (scripts/fresh_clone_check.sh) and a person's first setup. Safe to run again.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
bash .claude/hooks/py.sh -m venv .venv
py="$(bash scripts/venv_python.sh)"
"$py" -m pip install --disable-pip-version-check --quiet -r ingest/requirements.txt
"$py" -m pip check
"$py" -c "import sys; print('.venv ready:', sys.executable, sys.version.split()[0])"

#!/usr/bin/env bash
# Prints the path of the project's own Python (.venv), Windows or macOS/Linux layout (ADR-0100).
# Exit 2 when the virtual environment is missing (a check that cannot run is never a pass).
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for candidate in "$root/.venv/Scripts/python.exe" "$root/.venv/Scripts/python" "$root/.venv/bin/python"; do
  if [ -x "$candidate" ]; then
    printf '%s\n' "$candidate"
    exit 0
  fi
done
echo "no .venv: run 'bash .claude/hooks/py.sh -m venv .venv' and install ingest/requirements.txt" >&2
exit 2

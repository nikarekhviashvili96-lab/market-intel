#!/usr/bin/env bash
# Fresh-clone check: proves the CI path works on a checkout with no .venv — the T1 failure of 2026-11-15, when CI
# had no .venv and `lint` / `unit` exited 2. It clones the committed HEAD (never the working tree) into a temporary
# folder, runs the same scripts/setup_venv.sh the gates workflow runs, then the `lint` and `unit` gates there.
# Needs the network (pip). Run before pushing a change to dependencies, scripts/ or the gates workflow:
#   bash scripts/fresh_clone_check.sh
# Exit: 0 pass · 1 a step failed · 2 the check could not start.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d 2>/dev/null)" || { echo "fresh-clone: no temporary folder" >&2; exit 2; }
trap 'rm -rf "$tmp"' EXIT
git clone --quiet --no-hardlinks "$root" "$tmp/repo" || { echo "fresh-clone: git clone failed" >&2; exit 2; }
cd "$tmp/repo"
if [ -e .venv ]; then echo "fresh-clone: the clone already has .venv — not a fresh clone" >&2; exit 2; fi
echo "fresh-clone: $(git log --oneline -1)"
bash scripts/setup_venv.sh || { echo "fresh-clone: FAIL — setup_venv.sh" >&2; exit 1; }
bash .claude/hooks/py.sh tools/gates/gate.py --only lint,unit || { echo "fresh-clone: FAIL — lint/unit" >&2; exit 1; }
echo "fresh-clone: PASS — a checkout without .venv gets lint and unit green through scripts/setup_venv.sh"

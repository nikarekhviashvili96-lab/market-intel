#!/usr/bin/env bash
# Installs the site's packages exactly as web/package-lock.json pins them (ADR-0100 "install" step, PLAN-0001 T2).
# One script for CI (.github/workflows/gates.yml), a fresh clone (scripts/fresh_clone_check.sh) and a first setup.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
npm --prefix web ci --no-audit --no-fund
echo "web ready: node $(node --version), npm $(npm --version)"

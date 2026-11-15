---
id: PLAN-NNNN
type: plan
title: <short title>
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
spec: "[[SPEC-NNNN-slug]]"
adrs: []
---

# PLAN-NNNN: <title>

## 1. Approach

One paragraph: how it will be built and why this way (links to the relevant ADRs).

## 2. Tasks

- [ ] T1 — <a test / eval that fails first> (AC-001) — verify: `<command>`
- [ ] T2 — <code> (REQ-001, AC-001) — verify: `bash .claude/hooks/py.sh tools/gates/gate.py`

## 3. Gates, tests and evals

- Must be green: …
- Added (each with its drill): …

## 4. Orchestration

Code loop ([[ADR-0005-maker-checker-orchestration]], stage I): Sonnet 5.5 writes the code, Opus 5.5 checks it, at most 2 rounds per task — only if `orchestration/config.toml` has `enabled = true`.

## 5. Risks and rollback

| Risk | Mitigation | Rollback |
|---|---|---|

## 6. Done when

Every task is ticked; every gate is green; `verifier` → `VERDICT: pass`; the owner has seen the result with their own eyes.

## გადახრები

(Deviations — the heading stays in Georgian: the guard allows edits of an approved plan under it. Added during execution, old lines are never removed: `YYYY-MM-DD — what changed and why`)

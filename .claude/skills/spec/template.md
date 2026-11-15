---
id: SPEC-NNNN
type: spec
title: <short title>
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
intent: "[[intent]]"
adrs: []
related: []
---

# SPEC-NNNN: <title>

## 1. Problem and goal

What problem it solves and which goal it serves (G1, G2… from `intent.md`). One paragraph.

## 2. Users and scenarios

Who, in what situation, trying to do what. 2–5 scenarios, at least one of them a "bad day" (needed data is missing or stale, input is wrong or malicious, the connection drops, many users at once).

## 3. Scope

- **In:** …
- **Out:** … (and why)

## 4. Requirements

| ID | Requirement | Goal | Priority |
|---|---|---|---|
| REQ-001 | … | G1 | must |

For an AI agent, write into the requirements: the system instruction in one file (`prompts/system.md`) and each tool — with its description, a `strict` schema and its side-effect class (read / reversible write / irreversible), which decides who runs the call (`docs/guides/agent.md` §3).

## 5. Acceptance criteria

| ID | Given / When / Then | What you will see or do | What proves it (gate / test / eval) |
|---|---|---|---|
| AC-001 | Given … When … Then … | … | Test: … (or a gate, or an eval — for an AI agent) |

## 6. Success measures and evals

How we will know it works — in numbers for what the person said in their own words ("answers correctly", "is fast", "does not cost much") and a machine measures. 2–4 measures; each has a threshold, where it is measured and when it is checked.

| ID | Measure | Threshold | Where it is measured (test / eval set / gate) | When |
|---|---|---|---|---|
| M-001 | … | … | … | Every change; at stage 6 — weekly |

For an AI product this section is the contract of the level-2 gates (`evals-georgian`, `evals-grounding` — `tools/gates/gates.toml`): the thresholds move from here into the gate and are never lowered; the control set (`evals/`) is written together with the spec and re-runs on every model or instruction change. The show (stage 5) does not start without these measures.

Language quality is not scored 1–5: for each error type (grammatical case, calque, invented word) a yes/no question with a quote, and the threshold is the share of answers free of that error. The judge model is first measured against the owner's labels (kappa ≥0.6), the set is split into dev and test, two versions are compared pairwise on the same cases; for an agent — pass^k (`evals/README.md`).

## 7. Non-functional requirements

Speed, cost (per month or per request), security (personal data, malicious input; for an AI agent — prompt injection), accessibility; the quality of Georgian text, if the product writes or speaks Georgian (for an AI agent — the eval thresholds from §6).

## 8. Risks and assumptions

| Risk / assumption | Effect | Mitigation |
|---|---|---|

## 9. Open questions

- …

## Change history

- YYYY-MM-DD — first version.

---
id: evals-guide
type: guide
title: Evals — how we will measure the agent's behaviour
---

# Evals

A test checks that the code works correctly; an **eval** checks that the agent **answers** correctly — in its language, grounded in facts, keeping the rules. The agent does not exist yet, so this folder is only a plan for now; evals switch on as the level-2 gates ([[ADR-0006-deterministic-gates-and-evals]], `tools/gates/gates.toml`: `evals-georgian`, `evals-grounding`). The first set is written from the first specification's acceptance criteria — every criterion about behaviour has its own case in the set.

## What we already know (the engine author's measurement, 2026-09-16)

Four models were measured for Georgian on 120 dialogues, with two independent judge models: GPT-5.5 — best in Georgian (4.9/5); Sonnet 5 — good (4.3), but in 26% of answers it adds an unfounded detail; **Haiku 4.5 — unfit for Georgian text (2.6/5)**; Georgian text spends 1.5–2 times more tokens than English. The set and the scripts were built for another project and are not part of the engine; the method is this: `runner.py` (running the models with `claude -p`, `codex exec`, Ollama) → `score.py` (deterministic checks) → `judge.py` (two judges from different families, blind) → `judge_agg.py` — and the first eval's plan is written in the same form. These scores are holistic — one number from 1 to 5 for a whole answer; such a score hides a specific error (below), so a new set no longer uses it.

## Thresholds (lowering them is forbidden)

| Suite | What it checks | Threshold |
|---|---|---|
| georgian | factual correctness (deterministic), resistance to attacks, language errors — a yes/no question with a quote per type (a judge model, measured against the owner's labels) | deterministic ≥95%, adversarial ≥95%; each language-error type — ≥95% of answers are free of it (a specification may make it stricter) |
| grounding | the domain's invariants ([[REVIEW]]) and that every factual claim has a source | 0 violations |

## Measuring so that the number does not fool us

These rules come from an analysis of three articles (the numbers are from a secondary source, L-012) and apply to every new set:

- **Error analysis first.** A new set starts by reading real answers: on 30–100 answers you write in free words what is wrong, then group the similar ones. The groups become error types, each with its own check. You do not invent in advance a measure for what you cannot find in real answers.
- **A yes/no question with a quote, not a score.** The judge model (a model that rates another model's answer) answers one question per type — "is there a grammatical-case error here?", "a calque?", "an invented word?" — and backs a "yes" with a quote. Code looks for the quote in the answer: if it is not found, the rating does not count (just like a [[REVIEW]] finding without a location). The reason is measured: on a set with seeded errors the holistic score showed 5.0, the questions — 1.57.
- **The judge is measured first.** The owner labels 30–50 answers themselves (yes/no per type); the judge's agreement and kappa (agreement minus what chance alone would give) ≥0.6 — to be used as a gate, ≥0.8 — without the owner's check. Below 0.6 the judge is only advisory: the language part is INCONCLUSIVE (exit 2), never PASS. The article's judge had kappa 0.15 — it caught 10 of 26 errors.
- **dev and test.** The set is split in two: dev — on it you tune the instruction, the tools and the judge's questions; test — you only measure (the article's sizes: ~20 and ~60). A change fitted to test raises the number, not the quality. The first version's 10+3 questions are all test; you study the cause of a failure on a new, similar dev case.
- **Detection threshold and pairwise comparison.** On 60 cases a difference of under ~12 points between two versions is noise (the article's estimate; a simple calculation at the 90% level gives ~11) — you cannot call such a difference an improvement. You compare two versions pairwise on the same cases: which got fixed and which got broken (McNemar's test — a statistical check for paired comparisons); in the article the "better" version broke 14% of the cases, and the average hid it.
- **pass^k for an agent.** The same task runs k times (e.g. 3 times); pass^k is the share of tasks that passed every time (reliability), not "at least once". In the article pass^3 = 0.75: every fourth task failed at least once.
- **An agent's judge sees the actions.** Where the machine cannot check an agent's result and a model rates it, it is given the tool calls and the final state, not only the conversation: a judge that saw only the conversation was no better than a coin (AUC 0.49), with the calls — 0.73 (AUC — how well it tells good from bad: 0.5 — a coin, 1.0 — infallible).

## Rating an agent's behaviour — an agent with tools and several steps

The two suites above are for a document-answering agent. When an agent uses a tool or takes several steps (the agent guide's Q1 b), four dimensions of behaviour are added — each specification picks from its own task and sets the threshold itself (unlike georgian/grounding, where the threshold is fixed):

- **Task success** — on a set of sample tasks, whether the goal was reached; the final state or the result is checked deterministically, not the model's self-assessment.
- **Tool-call correctness** — the right tool from the allowed list, with the right arguments; a forbidden or wrong call is a failure (this is also about security — [[REVIEW]]).
- **Trajectory** — the order of steps is sensible, does not break the loop's step limit and takes no extra, fruitless step.
- **Cost per task** — tokens and price under a set threshold (from the answer's `usage` field).

**Tool-choice cases.** Tool-call correctness is measured with three kinds of cases: (1) a question that needs a specific tool — the right one is called, with the right arguments; (2) a question that needs no tool (a greeting, the answer is already in the material) — no call at all; (3) two similar tools (e.g. "view" and "book") — the one the question asks for is chosen. All three are checked deterministically, from the tool-call log. A failure first fixes the tool's description — "when you call it and when you do not" (`docs/guides/agent.md` §3) — and only then the instruction.

Deterministic checking comes first (the final state, the tool-call log, the token total); a judge model only where the machine cannot check (language quality, sometimes task success), and even then two models from different families. On every change the set runs again and is compared pairwise with the old result.

## Principles

- Every prompt or model change → the whole set runs again; the result is kept and compared pairwise with the old one.
- A gate is a floor, not a goal: passing it does not mean "good enough" — next to the number it always shows how many cases it was measured on and what the judge's kappa was.
- Deterministic checking (a string, a number, a tool call) always comes first; a judge model only where nothing else is possible (language quality), and even then two models from different families.
- A new failure from real use → a new case in the set (the regression does not happen again).

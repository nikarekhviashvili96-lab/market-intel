---
id: process
type: guide
title: Process — how we work: the path of work, roles, models and your decisions
related:
  - "[[intent]]"
  - "[[plan]]"
  - "[[progress]]"
  - "[[ADR-0001-foundation-and-sdlc-loop]]"
  - "[[ADR-0005-maker-checker-orchestration]]"
  - "[[ADR-0009-decision-model-dispatcher]]"
  - "[[ADR-0010-prompt-cache-and-cost]]"
---

# Process — how we work

Four files at the root complete each other: [[intent]] says what we are building and why; [[plan]] — in what order; [[progress]] — where we are now; and this file — **how we work**: the path every piece of work takes, who does what (you or which model) and where everything stops for your decision. The decisions themselves live in ADRs (`docs/adr/`); here is only the full picture, with links. If something here contradicts an ADR, the ADR is right and this file must be fixed.

## 1. The picture

Picture a building site. You are the client: you say what you want (the intent), you approve the drawing of one room (the specification) and the work schedule (the plan). Sonnet 5.5 is the builder — it builds; Opus 5.5 is the inspector — it checks whether it was built to the drawing; the gates (automatic machine checks) are the tape measure nobody can argue with; at the end you accept the work, with your own eyes. Haiku 5.5 is the helper who finds and sorts material, and the dispatcher (Jev) stands at the door and suggests who gets a new task.

## 2. The path of work — eight steps

| # | Step | Where it lives | Who does it | Who checks it | Your word |
|---|---|---|---|---|---|
| 1 | Intent | `intent.md` | Claude, talking with you (`/intent`) | — | `/approve intent` |
| 2 | Specification — an exact description of a feature, with testable criteria and success measures (evals, §6) | `docs/specs/SPEC-NNNN-…` | Claude (`/spec`) | the `spec-reviewer` subagent | `/approve spec N` |
| 3 | Plan — tasks, each tied to a requirement | `docs/plans/PLAN-NNNN-…` | Claude (`/feature-plan`) | — | `/approve plan N` |
| 4 | Code — test first, then code; one task = one commit, on a branch | git | Sonnet 5.5 — the session itself, started on Sonnet from the beginning | — | — |
| 5 | Gates | `bash .claude/hooks/py.sh tools/gates/gate.py` | the machine | exit 0 = passed; red is fixed first | — |
| 6 | Review — by the rules of [[REVIEW]] | `orchestration/runs/` | — | Opus 5.5, at most 2 rounds | if a serious finding remains after 2 rounds — you |
| 7 | Result — the show, publishing on your "yes", the pilot | — | Claude shows you the working result | you — by eye | `/approve live N` — "it is live", or a remark |
| 8 | Run and observe — the measures (the spec's §6), cost, drift, feedback ([[ADR-0013-sdlc-loop-2026-upgrade]]) | `/observatory`, logs, `evals/` | Claude measures and reminds you | the machine (evals, gates) | a new wish or a live bug → a new `/spec` |

While orchestration is off, step 6 is done in the same session by the `verifier` and the critic subagents.

**An architectural decision** takes its own path: `/adr` → an ADR with status `proposed` → (once orchestration is on — `run.py arch`: Opus 5.5 writes the proposal, Sonnet 5.5 audits it, Opus 5.5 writes the synthesis, once) → your `/approve adr N`. An accepted ADR no longer changes — a new ADR replaces it.

**Small work.** Work of more than three steps goes into `tasks/todo.md` first and counts as done only with a receipt (a commit or your word). How far the process may be lightened for a very small change is not decided yet.

## 3. Who does what — the models

This is stage I: only Claude's three models so far. **It is still a proposal**: [[ADR-0005-maker-checker-orchestration]] and [[ADR-0009-decision-model-dispatcher]] wait for your approval. Stage I's code is already written (`orchestration/run.py`); the drill checks it (`tools/gates/drill.py`, group `orchestration`), and the commit check runs it too. The code is off (`orchestration/config.toml`) until you switch it on (P-001); the dispatcher is only a decision so far — its code is not in this template (P-004).

| Role | Who | Why it |
|---|---|---|
| Code and Georgian text | Sonnet 5.5 | good quality at a middle price; the largest volume falls on it |
| Checking and architecture | Opus 5.5 | the strongest at this stage; starts each check in a fresh context |
| Routine — search, sorting, English summaries | Haiku 5.5 | 20 times cheaper than Sonnet; writes no Georgian text until it is measured (P-005) |
| Dispatcher — which model gets a task | Jev (decision model), off | writes no text, answers with a probability; when in doubt picks the stronger model |
| Above everything | deterministic gates | a model's "approve" cannot override a failing check |

**Stage II** — Fable 5.1, GPT (Astra, Sol) and other models — is written down but not switched on; when and in what role is your call.

**Subagents** ([[ADR-0010-prompt-cache-and-cost]]): the largest measured cost (44%) came from subagents working on a large context, so each one gets a narrow question, reads little and answers briefly — context under 100 thousand tokens where possible. Search, listing and reading facts out of files with a short English answer (Georgian files included) go to Haiku 5.5 — in the engine author's measurement (2026-10-13) it was as accurate as Sonnet on such questions at ~8 times lower cost; long summaries, judgement and Georgian go to Sonnet 5.5 (P-005), checking to Opus 5.5.

## 4. Where only you decide

- Approving documents: intent, spec, plan, ADR — `/approve …` (Claude cannot; the guard blocks it).
- Keys: only you write into `.env` — Claude can neither read nor write it.
- Switching on: orchestration (P-001), the dispatcher (P-004), moving to stage II.
- Installing a program, deleting a file, `git push`, merging into `main`.
- Changing the working environment (hooks, gates, skills, rules, agent instructions) — Claude asks you every time.
- Proposals in [[PROPOSALS]] — you answer plainly: "P-001 — yes" or "no".

## 5. The rhythm of a session

At the start of a session Claude is handed the "day sheet" by itself: `progress.md`'s "ახლა" (now), `plan.md`'s current phase and `tasks/todo.md`. That is when you pick the model — before the first message (`/model sonnet`) — and you do not change it midway: a switch makes the whole conversation be "written" again (the prompt cache — a saved copy of the earlier context — is tied to the model) and spends the subscription limit for nothing. Another model's work goes to a subagent. During work every important step is saved on the branch with a CHECKPOINT commit (a save point), and the gates run on every commit. At the end say "let's wrap up" or `/session-close` — the session is recorded and everything is put in its place. Every few sessions `/reflect` proposes improvements, and `/observatory` shows you what the agents did. If two sessions work in one folder, each saves only its own files (L-011).

**Cache and cost** ([[ADR-0010-prompt-cache-and-cost]]). Claude re-reads the whole conversation at every step, and does it cheaply only while its saved copy (the cache) is still alive — in the main session it lasts one hour, and every step restarts that hour. So the last line of the status line tells you whether the copy is warm (`♻ cache warm until ~14:05`), expiring, or already cold (`❄`). On a cold copy the next message writes the whole conversation again; if the conversation is large, the line also shows you the price and tells you that a new session is cheaper for a new topic — a new session starts at ~80 thousand tokens, while an old one may be over 300 thousand. Habits that follow: one topic — one session; after a break longer than an hour, if the conversation is large, first `/session-close`, then a new session (the engine gives you everything back with the "day sheet" anyway); in a large session do not reopen VS Code or Claude Code in the middle of work — that also rebuilds the whole conversation, just like a permission request left unanswered for more than an hour (in one measured case a 12.6-hour wait made 310 thousand tokens be written again); and after ↻2–3 a new session is better anyway. What a session cost and why its copy was rebuilt, `/observatory` shows you (the "Cache and cost" part).

## 6. When something breaks

If the guard refused an action (`GUARD[…]`), Claude changes course — it does not go around it. A red gate is fixed and never skipped. If a fix fails twice, Claude stops and tells you plainly what did not work. If a serious finding still remains after two review rounds, the result is marked "unverified" (UNVERIFIED) and you decide. At any time you can say "undo the last change" — git's save points exist for exactly that.

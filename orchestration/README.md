---
id: orchestration-guide
type: guide
title: Orchestration — maker/checker loops (off)
---

# Orchestration (maker / checker)

**The picture:** one model makes (maker), another checks (checker). Running the same model twice is not a "second opinion" — both runs share the same blind spots; so the checker is a different model and starts from a fresh context. Decision: [[ADR-0005-maker-checker-orchestration]].

**Status: built in and off** (`config.toml` → `enabled = false`). Switching it on is the owner's decision (proposal P-001). **Stage 1** (`stage = 1`) — only Claude works; `run.py` will not run another provider's model (exit 5, `STAGE GATE`). Moving to stage II (Fable, ChatGPT checkers) is a separate decision of the owner. The dispatcher — a decision model that suggests which model gets a task ([[ADR-0009-decision-model-dispatcher]]) — is only a decision so far: its code is not in this template (P-004).

| Loop | maker | checker | Rounds | What it returns |
|---|---|---|---|---|
| Architecture — `run.py arch` | Opus 5.5 — the proposal and, at the end, the synthesis | Sonnet 5.5 — an audit and its own position | 1 | a draft ADR (`proposed`); the owner decides with `/approve` |
| Code — `run.py code-check` | Sonnet 5.5 (the session itself) | Opus 5.5 — the diff, the specification and [[REVIEW]] | at most 2 reviews per task | `VERDICT: approve / changes-requested / blocked` |
| Routine | Haiku 5.5 — subagents (`model: haiku`) | deterministic gates | — | — |

Every model is written in `config.toml` as `provider:model` (e.g. `claude:claude-opus-5-5`), so changing a model is a one-line change.

## Commands

```bash
bash .claude/hooks/py.sh orchestration/run.py status          # what state it is in (also /orchestrate)
bash .claude/hooks/py.sh orchestration/run.py arch --topic "Which channel do we start with?" --dry-run
bash .claude/hooks/py.sh orchestration/run.py code-check --plan PLAN-0001 --task T3 --dry-run
bash .claude/hooks/py.sh orchestration/run.py code-check --plan PLAN-0001 --task T3 --response notes/T3-reply.md --dry-run   # round 2
```

`--dry-run` calls no model and writes nothing — it shows what would run. A real run (once switched on) asks the owner every time (permissions: ask).

## How it works

- **Claude's step:** `claude -p --restricted` with read-only tools only (`Read, Grep, Glob`), with a cost ceiling per call (`max_budget_usd`). `--restricted` does not read the project's settings, so `run.py` passes the `Read` deny rules for secret files again through `--settings` — the project's own and files of the same kind in any subfolder (`**/.env.*`, `**/*.pem`, …); and it does not hand the nested process the keys of other services (`tools/claude_cli.py`). Prompts and answers go through `tools/redact.py` — no key stays in the record.
- **A secret file never reaches a prompt:** `--context` will not take one (exit 5, `CONTEXT`), and the diff under review leaves such files out — the checker sees only their names. One table decides which file is secret (`run.py`, `SECRET_KINDS`) — the same one the nested call's deny rules are built from; so `.env.example` stays out too (the nested session could not read it anyway). With `--restricted` the nested session does not read a file outside the project folder (measured on 2026-10-18).
- **Text from outside is data:** the topic, the plan, the diff and the previous model's answer go into the prompt between two marks that carry a random word chosen for that prompt; text written without knowing that word cannot close the block and cannot pass for an instruction to the model.
- **Stage II (not yet):** ChatGPT — `codex exec -s read-only` (Codex CLI), signed in with `codex login`, without an API key. It is ready in the code, but at `stage = 1` that path is closed.
- **Records:** `orchestration/runs/<date>-<loop>-…-<time>/` — every run has its own folder: the prompts, the answers, `meta.json` (the stage, the models, each step's price — a failed one's too, and a failed step's error text, redacted) and `nested-settings.json` (the deny rules the nested call received). On screen `run.py` gives the reason for a failure in its own words: a step's error text may hold text that came from the diff or from a file it read. The round limit is counted from these records, so it holds across sessions too. A failed run spends no round and its record stays — also when the checker's last line is not `VERDICT:` / `POSITION:`.
- **The second round remembers the first:** from round 2 the code checker sees in its prompt its own previous review (the last finished round's `review.md`) and the maker's answer to it — the file `--response` names: per finding "fixed" or "rejected, because…". The checker first rates every previous finding in one line (`PREVIOUS <n>: resolved | open | rejected-accepted | disputed`) and raises a rejected one again only with new evidence — so a fix meets an answer, not new demands. If the finished round's `review.md` no longer exists, the loop stops (exit 5, `PREVIOUS REVIEW`): there is no rating from scratch. `--response` is not accepted in the first round, for a file outside the project or for a secret file (exit 5, `RESPONSE`). Which record a round answered is said by `previous_run` in `meta.json`. The drill checks this (`tools/gates/drill.py`, the orchestration group); the completeness of the `PREVIOUS …` lines is not machine-checked yet — it depends on the model's answer.
- **Prompts:** `prompts/` — maker, checker, synthesis, code checker. The checkers use [[REVIEW]]'s severity scale and format.
- **Gates stand above the loop:** a checker's "approve" cannot override a failing gate ([[ADR-0006-deterministic-gates-and-evals]]).

**Exit codes (`run.py`):** `0` success · `1` a step failed (or `GIT ERROR`, `RUNS`) · `3` off · `4` the round limit is used up · `5` wrong input or config — the message always starts with its own mark: `CONFIG`, `STAGE GATE`, `MODEL SPEC`, `TOOLS`, `BUDGET CONFIG`, `LIMITS`, `SANDBOX`, `DENY RULES`, `TEMPLATE`, `ORCH_CLAUDE_CMD`, `TOPIC`, `CONTEXT`, `PLAN`, `BAD TASK`, `BAD BASE`, `NO DIFF`, `REVIEW CONTRACT`, `PREVIOUS REVIEW`, `RESPONSE`.

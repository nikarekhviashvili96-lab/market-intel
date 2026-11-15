---
id: gates-guide
type: guide
title: Gates — how they work and how a new one is added
---

# Gates

A gate is a machine check whose result cannot be argued with: it passed, it failed, or it could not run. It does not trust a model's word "it works" — it checks for itself. Decision: [[ADR-0006-deterministic-gates-and-evals]].

## Running

```bash
bash .claude/hooks/py.sh tools/gates/gate.py                 # every enabled gate, the whole project
bash .claude/hooks/py.sh tools/gates/gate.py --list          # every gate, disabled ones too, with the reason
bash .claude/hooks/py.sh tools/gates/gate.py --pre-commit    # what .githooks/pre-commit runs
bash .claude/hooks/py.sh tools/gates/gate.py --files a.md    # only these files (the Stop hook uses it this way)
bash .claude/hooks/py.sh tools/gates/drill.py                # every check is broken on purpose — it must catch it
bash .claude/hooks/py.sh tools/gates/drill.py --self-test    # checks the drill: with stubs it must say DEAD
```

`bash .claude/hooks/py.sh` is the engine's launcher: it finds Python 3.12 or newer by itself on Windows, macOS and Linux (on Windows `py -3.12` works too).

**Result:** `0` — every enabled gate passed; `1` — something failed; `2` — INCONCLUSIVE (it could not run, e.g. `GITLEAKS_BIN` points at a file that does not exist, or it checked zero files). **SKIP** means "disabled" — it is not "passed", and the last line always says how many gates were not checked.

## Where it runs

- **On every commit** — `.githooks/pre-commit` (`core.hooksPath = .githooks`, in this repository only — `.claude/hooks/firstrun.py` switches it on by itself at the first session start). Going around it (`--no-verify`) is forbidden.
- **At the end of every turn** — the Stop hook checks only the files this session changed; on a failure the agent continues and fixes it.
- **By hand** — at any time, with the command above.

The drill runs on a commit when the commit holds an engine file (`.claude/hooks/`, `.claude/settings*`, `.claude/skills/`, `.claude/agents/`, `.claude/rules/`, `.githooks/`, `tools/`, the orchestration code); on any other commit its line is SKIP and says so. The same list (`PREFIXES` in `tools/engine_line.py`) also feeds the end-of-session line ([[ADR-0015-permission-windows-only-where-a-person-decides]]): which engine file changed since the session started and whether the drill checked it — a drill that passed on a commit leaves a receipt in git's folder; on a commit the whole engine is checked, so the receipt also covers a file that changed earlier and has stayed unchanged since. A commit made with `--no-verify` or with the check switched off has no receipt, and its file shows with ⚠ until a later commit passes the drill; the guard and `.githooks/` always carry ⚠. The episode keeps the line (SessionEnd), `/session-close` hands it to the owner word for word, and the next session's start shows it to the person directly. Its group `decision` works only where the dispatcher's code is (`orchestration/decide.py`) — it is not in this template, so the drill leaves that group out and says so in its last line (`LEFT OUT: decision …`).

On a full run the `secrets` gate checks four things: staged files, unsaved changes, the history and files not yet added to git (gitleaks's git mode cannot see the last at all, so each is checked separately). Before a commit only staged files are checked. If gitleaks is not on the computer, the engine's own scanner checks the same files (`tools/redact.py` — the same list the sentinel works from), and the result line says so plainly: it has no entropy threshold and does not check git's history (ADR-0011). It knows the providers' key prefixes and, since 2026-10-20, a quoted value assigned to a secret's name too (`named-secret`): the name ends in a secret word (`DB_PASSWORD`, `api_key`, `client_secret`), the value is 8+ characters and has both a letter and a digit — so `password = get_password()`, an environment variable's name and a `${…}` template pass.

The `budget` gate measures how many bytes every session loads before the first word — CLAUDE.md and its imports, rules without `paths:`, the descriptions of skills and agents — and fails if the total exceeds `max_bytes`, or if `max_bytes` is higher than the owner's last `/approve budget N`. The guard (G7) protects the same budget on every change; the list: `bash .claude/hooks/py.sh tools/budget.py`.

The drill has a floor — the drill gate's `floor` in `gates.toml`, i.e. how many cases the drill holds ([[ADR-0015-permission-windows-only-where-a-person-decides]]). The `drill` gate fails if the sum of ARMED and ELSEWHERE in the drill's last line is below the floor (a case was removed, or a group stopped running) or above it (with a new case the floor rises in the same commit — the gate names the exact number). ELSEWHERE is a case only another system runs (Windows network paths, macOS and Linux file modes and links): it counts here too, so the number is the same on every system. Only the owner can lower the floor compared with the previous commit — `/approve floor N` writes a new line into the ledger, which the gate reads (LEDGER); a drill gate that is disabled, removed from the commit or deleted lowers the floor to 0 and asks for the same line; when the owner's disabling is already in the previous commit, the floor written on that gate counts — later commits pass while it stays unchanged, and lowering it or deleting the gate again asks for the owner's line. Before a commit the gate reads both the floor and whether the drill gate is enabled from the `gates.toml` the commit will record (the staged version), not from disk: if a larger drill is staged but the raised floor is only on disk, the commit stops. When `drill.py` on disk differs from what the commit will record (new cases not yet staged — maybe another session's), the drill does not run and the commit stops (DRILL-UNSTAGED): either add `drill.py` to the commit (`git add`) or, if another session is changing it, wait until it makes its own commit (L-007). The guard (G7) blocks lowering the floor, deleting it and disabling the drill gate on every change. The kit has no dispatcher group, so its floor is its own.

## Adding a new gate

1. A new `[[gate]]` in `gates.toml` — `builtin` (an internal check in `gate.py`) or `cmd` (a command as a list of arguments, e.g. `["ruff", "check", "."]`; it runs without a shell, so an `&` or `;` written in it cannot start a second command; exit 0 = passed, a tool that is not installed = INCONCLUSIVE).
2. In `drill.py` — a clean control (must pass) and a seeded defect (must fail with **this gate's own** message); in the same commit the drill's `floor` rises by the number of new cases.
3. `gates.toml`, `gate.py` and `drill.py` are engine files and a permission window no longer guards them ([[ADR-0015-permission-windows-only-where-a-person-decides]]): a window whose content a person cannot read is no protection — it only trains them to say "yes". The machine guards them: on a commit the drill catches a gate that was disabled or weakened (a trial in the engine's workshop on 2026-10-31: the `secrets` gate disabled → 21 DEAD, a faked PASS → 18 DEAD). A window stays on the permissions file itself (`.claude/settings.json`), because one change to it opens every protection at once; that engine files have no window while the permissions file, money switches, installs, push and deletion still do, is checked by the drill's `wiring` group.
4. Never: lowering a threshold or disabling a gate "to go green".

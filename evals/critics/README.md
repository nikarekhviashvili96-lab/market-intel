---
id: evals-critics
type: guide
title: The critics' drill — whether the critics can fail, and at the right place
---

# The critics' drill (D-070)

**What for.** Three critics (`.claude/agents/critic-correctness.md`, `critic-security.md`, `critic-quality.md`) check
code, but until now nobody had shown that any of them **can** catch an error. A critic that always says "no defect"
and a good critic print the same line on clean code ([[ADR-0006-deterministic-gates-and-evals]]). This drill gives
each one clean control code and code with one error of its own lens seeded on purpose, and checks the answer — no
model rates a model.

**How.** Each case is a separate `claude -p` session in a temporary folder holding only that case's files
(`--restricted`, only Read/Grep/Glob, the model the critic's frontmatter names). The verdict is read from its last
line. Then the whole answer goes through `tools/check_findings.py`, with the same folder: a finding whose file, line
or quote is not confirmed does not count ([[REVIEW]]). So ARMED is only a critic that found the error **at the right
place**; and the control is clean only when `VERDICT OK` comes with zero finding lines — as the critic's own contract
asks. The security critic has a third case too: a file is read through a helper that is not in the folder, i.e. the
deciding fact is not visible. The right answer there is an UNRESOLVED line and `VERDICT INCONCLUSIVE`: FAIL would
inflate a guess, and OK would trust an unread helper.

```bash
bash .claude/hooks/py.sh evals/critics/run.py                          # all three critics, with the control
bash .claude/hooks/py.sh evals/critics/run.py --critic critic-security # only one
```

It costs money (each case is one model session) and runs by hand — the commit check does not run it. The result is
saved in `results-<date-time>.json`. Exit code: 0 — all ARMED; 1 — some DEAD (stayed silent, "found" it elsewhere or
its lines are not confirmed); 2 — INCONCLUSIVE (the control did not come back clean, the call failed or the last line
is missing).

**The first run (2026-10-20, `results-2026-10-20-2017.json`, $0.26).** Six of seven cases were ARMED; the seventh —
the security critic's UNRESOLVED case — counted as DEAD, although the critic answered exactly right (INCONCLUSIVE, the
missing fact — `safe_join`'s code, and who would show it — the `storage` module). The error was in the checker:
`check_findings.py` looked for a quote in the fourth column of the UNRESOLVED line (the description of the missing
fact), which quotes nothing. It was fixed, the drill got its own case, and re-rating the same saved answers gives all
seven ARMED. The live run found what the drill's hand-written cases could not (like L-010).

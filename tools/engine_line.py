#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One line at the end of a session: which engine files changed, and whether their commit passed the drill
(ADR-0015). Information, not a lock — the person sees that the engine changed and can ask why.

  bash .claude/hooks/py.sh tools/engine_line.py [--root DIR] [--since REV]

Engine files are the ones the drill runs for at commit — PREFIXES, which gate.py takes as its HARNESS_PREFIXES, so the
two never disagree: hooks, the commit check, the permissions file, skills, agents, rules, the engine's tools and the
orchestration code. "Changed" means committed after --since — the commit the session started from (HEAD when not
given: only what is not committed yet; "-" when the session began before the first commit: every commit after the
first) — or not committed yet, whoever changed it. A project's first commit is where the engine arrives, not a change
to it, and before it there is nothing to compare with: no line.
A commit passed the drill when the drill gate, at that commit or at the push that sent it (the drill runs at push since
2026-11-15), left a receipt for its tree (write_receipt — <git common dir>/engine-drill-receipts). A commit not yet
pushed, or made without the checks (pulled, rebased, `--no-verify`), has none and reads "not checked by the drill". ⚠ marks the guard and the
commit check (.githooks/): a change there can weaken every other check.
Prints nothing when no engine file changed. Exit 0, or 2 when git could not answer (nothing is claimed then).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PREFIXES = (".claude/hooks/", ".claude/settings", ".claude/skills/", ".claude/agents/", ".claude/rules/", ".githooks/",
            "tools/", "orchestration/run.py", "orchestration/decide.py", "orchestration/config.toml",
            "orchestration/prompts/")
RECEIPTS = "engine-drill-receipts"
# (a file, or a folder ending in /, and the words a person reads) — the first that matches wins
WORDS = ((".claude/hooks/guard.py", "⚠ guard (the safety checker)"), (".githooks/", "⚠ the commit check"),
         (".claude/hooks/sentinel.py", "sentinel (guard of outside text and keys)"),
         (".claude/hooks/episodic.py", "session memory"), (".claude/hooks/stop_gate.py", "end-of-turn check"),
         (".claude/hooks/statusline.py", "status line"), (".claude/hooks/firstrun.py", "first run"),
         (".claude/hooks/py.sh", "Python launcher"), (".claude/hooks/", "hooks"),
         (".claude/settings", "permissions file"), ("tools/gates/gates.toml", "gate list"),
         ("tools/gates/drill.py", "drill"), ("tools/gates/gate.py", "gate runner"),
         ("tools/gates/README.md", "gates guide"), ("tools/gates/", "gates"),
         ("tools/drill_floor.py", "drill floor"), ("tools/engine_line.py", "end-of-session line"),
         ("tools/backup_line.py", "backup reminder"),
         ("tools/approve.py", "owner's approval (/approve)"), ("orchestration/", "orchestration"))
STATES = (("unchecked", "⚠ committed, but the drill has not checked it"),
          ("pending", "not committed yet (the drill checks it at push)"),
          ("checked", "committed and checked by the drill ✓"))


def git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def receipts_file(root: Path) -> Path | None:
    common = (git(root, "rev-parse", "--git-common-dir") or "").strip()
    if not common:
        return None
    p = Path(common)
    return (p if p.is_absolute() else root / p) / RECEIPTS


def write_receipt(root: Path, rev: str | None = None) -> bool:
    """Once the drill passed: at commit, the tree the commit records (`git write-tree` — the index the commit takes,
    GIT_INDEX_FILE included); at push, the tree of the pushed commit `rev`. Best effort: without a receipt the line only
    calls that commit unchecked."""
    tree = (git(root, "rev-parse", f"{rev}^{{tree}}") if rev else git(root, "write-tree")) or ""
    tree, where = tree.strip(), receipts_file(root)
    if not tree or where is None:
        return False
    try:
        with where.open("a", encoding="utf-8") as fh:
            fh.write(tree + "\n")
    except OSError:
        return False
    return True


def words(path: str) -> str:
    parts = path.split("/")
    if path.startswith(".claude/skills/") and len(parts) > 3:
        return f"skill /{parts[2]}"
    if path.startswith((".claude/agents/", ".claude/rules/")) and len(parts) > 2:
        return ("subagent " if parts[1] == "agents" else "rule ") + Path(parts[-1]).stem
    for start, said in WORDS:
        if path == start or (start.endswith("/") and path.startswith(start)) or path.startswith(start + "."):
            return said
    return f"engine tool {parts[-1]}"


def committed(root: Path, since: str | None, seen: set[str]) -> dict[str, str] | None:
    """{engine file: checked | unchecked} in the commits after `since` (None: every commit but the first). The drill at
    commit runs over the whole tree, so a file is checked when the commit that last changed it, or any newer one, left a
    receipt — that tree holds the file exactly as it is now; a change newer than the newest receipt is unchecked."""
    log = git(root, "log", "--format=%x00%T %P", "--name-only", "--no-renames", "HEAD" if since is None else f"{since}..HEAD")
    if log is None:
        return None
    out: dict[str, str] = {}
    drilled = False  # this commit or a newer one left a receipt
    for chunk in log.split("\0"):  # newest first
        lines = chunk.strip().splitlines()
        if not lines or len(lines[0].split()) < 2:  # a first commit has no parent: the engine arrives, it does not change
            continue
        drilled = drilled or lines[0].split()[0] in seen
        for f in lines[1:]:
            if f.startswith(PREFIXES) and f not in out:
                out[f] = "checked" if drilled else "unchecked"
    return out


def changes(root: Path, since: str | None) -> dict[str, str] | None:
    """{engine file: checked | unchecked | pending}; {} before the first commit; None when git could not answer."""
    where = receipts_file(root)
    if where is None:
        return None
    if git(root, "rev-parse", "--verify", "-q", "HEAD") is None:
        return {}  # before the first commit there is nothing to compare with
    try:
        seen = set(where.read_text(encoding="utf-8").split()) if where.is_file() else set()
    except OSError:
        seen = set()  # every commit then reads "not checked": an alarm too many, never one too few
    out = committed(root, since, seen)
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
    if out is None or status is None:
        return None
    for rec in status.split("\0"):
        if rec[3:].startswith(PREFIXES):
            out[rec[3:]] = "pending"
    return out


def line(root: Path, since: str | None = "HEAD") -> str | None:
    """The line; "" when no engine file changed, None when git could not answer."""
    found = changes(root, since)
    if found is None:
        return None
    groups = []
    for state, said in STATES:
        names = list(dict.fromkeys(words(f) for f in sorted(found) if found[f] == state))
        if names:
            groups.append(f"{said}: {', '.join(names)}")
    return "🔧 engine changed — " + "; ".join(groups) + "." if groups else ""


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="the session's engine line (ADR-0015)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--since", default="HEAD", help="the commit the session started from; '-' = before the first commit")
    a = ap.parse_args(argv)
    text = line(Path(a.root).resolve(), None if a.since == "-" else a.since)
    if text is None:
        print("ENGINE-LINE INCONCLUSIVE: git could not say what changed — nothing is claimed", file=sys.stderr)
        return 2
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

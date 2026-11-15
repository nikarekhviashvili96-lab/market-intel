#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""First run of the engine in a new project (ADR-0011): make the folder a git repository, switch on the commit checks
and look at what is missing — so a person who has just installed the engine can start straight from their idea.

SessionStart hook (startup, resume, clear). It runs `git init` when the folder is not a repository, sets
core.hooksPath = .githooks in this repository only, makes the commit hook executable on macOS and Linux (a copy
without file modes loses that bit, and git then skips the hook), and checks git itself, git's name and e-mail,
Python 3.12+ and gitleaks; a project inside another repository, or a core.hooksPath of the person's own, is
reported and left alone. Install hints name Windows, macOS and Linux. It also says once where Claude Code's sandbox
stands (ADR-0014; read by tools/sandbox_state.py: none on native Windows — WSL2 has it; off until the person switches it
on) — it never switches the sandbox on.
Silent when everything is in place; otherwise one short note for the agent: what was done and what is
missing. It never touches the global git config (L-005), never installs anything (installing a tool is the person's
yes) and never fails the session — it always exits 0. Missing tools are reported once per repository (a marker
inside .git/); commit checks that are not running are reported at every session start, and with no repository of its
own (git missing, or an enclosing repository) every note repeats on purpose.

  FIRSTRUN_ROOT   the project folder (default: CLAUDE_PROJECT_DIR, else the project this file belongs to)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
# Windows looks for a program in the current folder before PATH unless this is set. Here the current folder is the
# project, where a planted git.bat would otherwise run at every session start (review S4).
os.environ["NoDefaultCurrentDirectoryInExePath"] = "1"

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "tools" / "gates"))
sys.path.insert(0, str(HERE.parents[2] / "tools"))
MARKER = "engine-firstrun"  # inside .git/: the notes about missing tools that were already given
INSTALL = {  # what to offer the person, per system; installing is always their yes. py.sh repeats "python": change both
    "git": "Windows: `winget install Git.Git`; macOS: `xcode-select --install` or `brew install git`; "
           "Linux: `sudo apt install git`",
    "python": "Windows: `winget install Python.Python.3.12`; macOS: `brew install python@3.12`; "
              "Linux: `sudo apt install python3.12` (Ubuntu 24.04+), elsewhere `uv python install 3.12`",
    "gitleaks": "Windows: `winget install Gitleaks.Gitleaks`; macOS: `brew install gitleaks`; "
                "Linux: `sudo apt install gitleaks` or GitHub's release",
}


def project_root() -> Path:
    env = os.environ.get("FIRSTRUN_ROOT") or os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(env).resolve() if env else HERE.parents[2]


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    """git in the project. A git that cannot start reads as a failed command (exit 127), never as an exception."""
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return subprocess.CompletedProcess(["git", *args], 127, "", str(e))


def repo_top(root: Path) -> Path | None:
    r = git(root, "rev-parse", "--show-toplevel")
    return Path(r.stdout.strip()).resolve() if r.returncode == 0 and r.stdout.strip() else None


def gitleaks_note() -> str | None:
    """None when the secrets gate will find gitleaks; otherwise what the agent should tell the person."""
    try:
        from gate import find_gitleaks  # the same search the secrets gate makes
    except Exception as e:  # e.g. a Python without tomllib — say so, never guess
        return f"the gitleaks check could not run ({type(e).__name__}: {e})"
    if find_gitleaks():
        return None
    explicit = os.environ.get("GITLEAKS_BIN")
    if explicit:  # the gate treats a named but missing gitleaks as INCONCLUSIVE, not as "not installed"
        return (f"`GITLEAKS_BIN` names a file that does not exist ({explicit}) — the secrets check "
                "stops INCONCLUSIVE; ask the person whether to fix this variable or remove it")
    return ("no gitleaks — the engine's own scanner checks secrets at commit (weaker: it does not check git's "
            "history); offer the person to install gitleaks, with their yes "
            f"({INSTALL['gitleaks']})")


def sandbox_note(root: Path) -> str | None:
    """What the agent is told once about Claude Code's sandbox (ADR-0014) — None when it is on; a reading that fails
    is said too, never skipped."""
    try:
        import sandbox_state as sb
        return sb.firstrun_note(*sb.sandbox_state(root))
    except Exception as e:  # a copy without tools/sandbox_state.py, say — say so
        return (f"the sandbox state could not be read ({type(e).__name__}: {e}) — `tools/sandbox_state.py` "
                "must be checked by hand")


def setup(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Put the repository and its commit checks in place.
    -> (what was done, what is missing — told once, why the commit checks are not running — told every session)."""
    done: list[str] = []
    missing: list[str] = []
    gate_off: list[str] = []
    if shutil.which("git") is None:
        return done, ["git is not installed — save points (commits) and the commit checks cannot work; "
                      f"offer the person the install ({INSTALL['git']}) and wait for their yes"], gate_off
    top = repo_top(root)
    if top is None:
        r = git(root, "init", "-q")
        if r.returncode != 0:
            return done, [f"`git init` failed: {(r.stderr or r.stdout).strip()[-200:]}"], gate_off
        done.append("the folder became a git repository (`git init`): every step is kept as a save point (commit)")
    elif top != root:
        return done, [f"the project is inside another git repository ({top}) — the engine does not touch its settings; "
                      "ask the person whether a separate repository would be better"], gate_off
    hook = root / ".githooks" / "pre-commit"
    hooks = git(root, "config", "--get", "core.hooksPath").stdout.strip()  # this repository's, else the person's own
    if not hooks and hook.is_file():
        if git(root, "config", "--local", "core.hooksPath", ".githooks").returncode == 0:
            done.append("the commit checks are on (`core.hooksPath = .githooks`, in this repository only)")
        else:
            gate_off.append("`core.hooksPath` could not be written — the commit checks do not work")
    elif hooks and hooks.replace("\\", "/").rstrip("/") != ".githooks":
        gate_off.append(f"`core.hooksPath = {hooks[:120]}` — the engine's commit checks do not work; ask the person "
                        "whether to change it to `.githooks` in this repository")
    elif not hook.is_file():  # git skips a missing hook without a word
        gate_off.append("`.githooks/pre-commit` is missing — the commit checks do not work")
    if os.name != "nt" and hook.is_file() and not os.access(hook, os.X_OK):  # git on macOS/Linux skips it
        why_not = ""
        try:  # a link (even to a file in the project) or a file outside the project is not ours to change
            ours = not hook.is_symlink() and hook.resolve().is_relative_to(root.resolve())
        except (OSError, RuntimeError):
            ours = False
        if not ours:
            why_not = "a link, or a file outside the project — left alone"
        else:
            try:
                hook.chmod(hook.stat().st_mode | 0o100)  # the owner only: git runs the hook as the person who commits
                done.append("`.githooks/pre-commit` was made executable (`chmod +x`) — without it git would silently skip the commit "
                            "check on macOS and Linux")
            except OSError as e:
                why_not = e.strerror or type(e).__name__
        if why_not:
            gate_off.append(f"`.githooks/pre-commit` is not executable and could not be made so ({why_not}) — the commit "
                            "checks do not work; ask the person to run `chmod +x .githooks/pre-commit`")
    who = [key for key in ("user.name", "user.email") if not git(root, "config", "--get", key).stdout.strip()]
    if who:
        missing.append(f"git has no {' and '.join(who)} — no commit (save point) can be made; ask the person "
                       "for a name and an email and write their answer into this repository only (`git config --local user.name …`, "
                       "`git config --local user.email …`; for a public repository GitHub's private address "
                       "`…@users.noreply.github.com` is better)")
    if sys.version_info < (3, 12):  # why 3.12: .claude/hooks/py.sh
        missing.append(f"Python {sys.version_info.major}.{sys.version_info.minor} — the engine needs 3.12 or newer; "
                       f"offer the person the install ({INSTALL['python']})")
    note = gitleaks_note()
    if note:
        missing.append(note)
    return done, missing, gate_off


def marker_path(root: Path) -> Path | None:
    """The told-once marker inside this project's own .git/ — None without a repository of its own."""
    if repo_top(root) != root:
        return None
    r = git(root, "rev-parse", "--absolute-git-dir")
    return Path(r.stdout.strip()) / MARKER if r.returncode == 0 and r.stdout.strip() else None


def was_told(marker: Path | None, text: str) -> bool:
    try:
        return marker is not None and marker.is_file() and marker.read_text(encoding="utf-8") == text
    except OSError:
        return False


def record_told(marker: Path | None, text: str) -> None:
    if marker is None:
        return
    try:
        marker.write_text(text, encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    if os.environ.get("EPISODIC_NESTED") == "1":
        return 0  # a nested model call made by a tool: not a person's session
    root = project_root()
    try:
        done, missing, gate_off = setup(root)
        sandbox = sandbox_note(root)
        if sandbox:
            missing.append(sandbox)
        marker, text = marker_path(root), "\n".join(missing)
        if was_told(marker, text):
            missing = []  # a missing tool is said once; commit checks that are off are said every session
        if not done and not missing and not gate_off:
            return 0
        record_told(marker, text)
    except Exception as e:  # never break the session start
        done, missing, gate_off = [], [f"the first-run check failed: {type(e).__name__}: {e}"], []
    lines = ["## First run — the engine sets itself up (`.claude/hooks/firstrun.py`, ADR-0011)"]
    lines += [f"- done: {d}" for d in done]
    lines += [f"- missing: {m}" for m in gate_off + missing]
    lines.append("- Tell the person this in one or two plain sentences; do not ask them for setup and do not stop work on their idea.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Record FRED's real answer for DGS10 into tests/fixtures/fred_dgs10.json (PLAN-0001 T1, AC-001).

Run by the owner once: `{venv_python} -m ingest.record_fixture`. The FRED key is read from the environment
variable FRED_API_KEY, or else from that one line in the project's `.env`. The key is never printed and never
written: everything printed passes through `redact()` (the `api_key` parameter and the key itself), and an answer
that contains the key is not saved.

The window is fixed (10 years ending 2026-11-13) so the recording is reproducible; the answer is saved as FRED
sent it, only re-indented.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import httpx

from ingest.fred import FredParseError, parse_observations

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "fixtures" / "fred_dgs10.json"
URL = "https://api.stlouisfed.org/fred/series/observations"
WINDOW = {"observation_start": "2016-11-13", "observation_end": "2026-11-13"}
MASK = "[REDACTED]"
_KEY_PARAM = re.compile(r"(api_key(?:=|%3D))[^&\s\"'<>]+", re.IGNORECASE)


def redact(text: str, key: str | None) -> str:
    """Hide the `api_key` URL parameter's value and every occurrence of the key itself."""
    text = _KEY_PARAM.sub(lambda m: m.group(1) + MASK, text)
    if key:
        text = text.replace(key, MASK)
    return text


def find_key() -> str | None:
    key = os.environ.get("FRED_API_KEY", "").strip()
    if key:
        return key
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.partition("=")
            if sep and name.strip() == "FRED_API_KEY":
                return value.strip().strip('"').strip("'") or None
    return None


def record(key: str) -> str:
    """Fetch, check and save; returns the success line. Raises RuntimeError with a message that may need redacting."""
    params = {"series_id": "DGS10", "file_type": "json", "api_key": key, **WINDOW}
    try:
        response = httpx.get(URL, params=params, timeout=60)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Could not reach FRED ({type(exc).__name__}: {exc}); try again later.") from None
    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError(f"FRED answered HTTP {response.status_code} with something that is not JSON.") from None
    try:
        parsed = parse_observations(payload)
    except FredParseError as exc:
        raise RuntimeError(f"FRED's answer is not usable (HTTP {response.status_code}): {exc}") from None
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    if key in text or _KEY_PARAM.search(text):
        raise RuntimeError("Refusing to save: the answer contains the key.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    obs = parsed.observations
    return (f"Saved {OUT.relative_to(ROOT).as_posix()}: {len(obs)} observations, {obs[0].date} … {obs[-1].date}, "
            f"{len(parsed.missing_dates)} dates marked '.'")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]  # L-001
    key = find_key()
    if not key:
        print("No FRED key: add a line FRED_API_KEY=<your key> to .env, then run this again.", file=sys.stderr)
        return 1
    try:
        print(redact(record(key), key))
    except Exception as exc:  # anything, including an unexpected error, is printed only after redaction
        print(redact(str(exc) or type(exc).__name__, key), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Record FRED's real answer for DGS10 into tests/fixtures/fred_dgs10.json (PLAN-0001 T1, AC-001).

Run by the owner once: `{venv_python} -m ingest.record_fixture`. The FRED key is read from the environment
variable FRED_API_KEY, or else from that one line in the project's `.env`. The key is never printed and never
written: FRED's answer does not contain it, and network errors are reported without the request address.

The window is fixed (10 years ending 2026-11-13) so the recording is reproducible; the answer is saved as FRED
sent it, only re-indented.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

from ingest.fred import FredParseError, parse_observations

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "fixtures" / "fred_dgs10.json"
URL = "https://api.stlouisfed.org/fred/series/observations"
WINDOW = {"observation_start": "2016-11-13", "observation_end": "2026-11-13"}


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


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]  # L-001
    key = find_key()
    if not key:
        print("No FRED key: add a line FRED_API_KEY=<your key> to .env, then run this again.", file=sys.stderr)
        return 1
    params = {"series_id": "DGS10", "file_type": "json", "api_key": key, **WINDOW}
    try:
        response = httpx.get(URL, params=params, timeout=60)
    except httpx.HTTPError as exc:
        print(f"Could not reach FRED ({type(exc).__name__}); try again later.", file=sys.stderr)
        return 1
    try:
        payload = response.json()
    except ValueError:
        print(f"FRED answered HTTP {response.status_code} with something that is not JSON.", file=sys.stderr)
        return 1
    try:
        parsed = parse_observations(payload)
    except FredParseError as exc:
        print(f"FRED's answer is not usable: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    if key in text:
        print("Refusing to save: the answer contains the key.", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    obs = parsed.observations
    print(f"Saved {OUT.relative_to(ROOT).as_posix()}: {len(obs)} observations, {obs[0].date} … {obs[-1].date}, "
          f"{len(parsed.missing_dates)} dates marked '.'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Parse a FRED `series/observations` answer (file_type=json) into observations — SPEC-0001 REQ-001.

Rules (SPEC-0001 REQ-001, AC-001, AC-003; [[fred]] in docs/domain):
- the value "." is FRED's missing-observation marker: no observation, never 0;
- an error body, a non-numeric value, an empty series, a repeated or out-of-order date, or a `count` that
  does not match the rows fails the whole parse — nothing from such an answer may be stored.

Command line: `python -m ingest.fred <answer.json>` prints the parsed count and the skipped dates;
exit 0 on success, 1 when the answer is invalid.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

MISSING = "."
_NUMBER = re.compile(r"-?\d+(\.\d+)?")


class FredParseError(ValueError):
    """The answer is not a valid FRED observations answer; nothing from it may be stored."""


@dataclass(frozen=True)
class Observation:
    date: dt.date
    value: Decimal


@dataclass(frozen=True)
class ParsedSeries:
    observations: tuple[Observation, ...]
    missing_dates: tuple[dt.date, ...]


def parse_observations(payload: Any) -> ParsedSeries:
    """Validate a decoded FRED JSON answer and return its observations, oldest first."""
    if not isinstance(payload, dict):
        raise FredParseError("answer is not a JSON object")
    if "error_code" in payload or "error_message" in payload:
        raise FredParseError(f"FRED returned an error: {payload.get('error_code')} {payload.get('error_message')}")
    rows = payload.get("observations")
    if not isinstance(rows, list):
        raise FredParseError("answer has no 'observations' list")
    if not rows:
        raise FredParseError("empty series: no observations")
    count = payload.get("count")
    if count is not None and count != len(rows):
        raise FredParseError(f"count says {count} observations, answer holds {len(rows)}")

    observations: list[Observation] = []
    missing: list[dt.date] = []
    previous: dt.date | None = None
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise FredParseError(f"observation {i} is not an object")
        date = _parse_date(row.get("date"), i)
        if previous is not None and date <= previous:
            kind = "repeated" if date == previous else "out-of-order"
            raise FredParseError(f"{kind} date {date.isoformat()} at observation {i}")
        previous = date
        value = row.get("value")
        if value == MISSING:
            missing.append(date)
            continue
        if not isinstance(value, str) or not _NUMBER.fullmatch(value):
            raise FredParseError(f"non-numeric value {value!r} on {date.isoformat()}")
        observations.append(Observation(date, Decimal(value)))

    if not observations:
        raise FredParseError("empty series: every value is missing")
    return ParsedSeries(tuple(observations), tuple(missing))


def _parse_date(text: Any, index: int) -> dt.date:
    if not isinstance(text, str):
        raise FredParseError(f"observation {index} has no date")
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise FredParseError(f"observation {index} has an invalid date {text!r}") from None


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]  # L-001
    if len(argv) != 1:
        print("usage: python -m ingest.fred <answer.json>", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        parsed = parse_observations(payload)
    except (OSError, json.JSONDecodeError, FredParseError) as exc:
        print(f"invalid FRED answer: {exc}", file=sys.stderr)
        return 1
    obs = parsed.observations
    print(f"parsed {len(obs)} observations, {obs[0].date} … {obs[-1].date}")
    print(f"skipped {len(parsed.missing_dates)} missing dates ('.'):")
    for d in parsed.missing_dates:
        print(f"  {d.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

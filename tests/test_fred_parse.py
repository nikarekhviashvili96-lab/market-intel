"""Tests for ingest.fred — parsing a FRED series/observations answer (SPEC-0001 REQ-001, AC-001, AC-003)."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ingest.fred import FredParseError, Observation, parse_observations

ROOT = Path(__file__).resolve().parent.parent
RECORDING = ROOT / "tests" / "fixtures" / "fred_dgs10.json"


def answer(rows: list[tuple[str, str]], **extra: Any) -> dict[str, Any]:
    """A FRED-shaped answer with the given (date, value) rows."""
    body: dict[str, Any] = {
        "realtime_start": "2026-11-15",
        "realtime_end": "2026-11-15",
        "units": "lin",
        "count": len(rows),
        "offset": 0,
        "limit": 100000,
        "observations": [
            {"realtime_start": "2026-11-15", "realtime_end": "2026-11-15", "date": d, "value": v} for d, v in rows
        ],
    }
    body.update(extra)
    return body


# ── happy path ──────────────────────────────────────────────────────────────


def test_numeric_values_become_observations() -> None:
    parsed = parse_observations(answer([("2025-07-02", "4.30"), ("2025-07-03", "4.35")]))
    assert parsed.observations == (
        Observation(dt.date(2025, 7, 2), Decimal("4.30")),
        Observation(dt.date(2025, 7, 3), Decimal("4.35")),
    )
    assert parsed.missing_dates == ()


def test_dot_is_no_observation_never_zero() -> None:
    parsed = parse_observations(
        answer([("2025-07-03", "4.35"), ("2025-07-04", "."), ("2025-07-07", "4.39")])
    )
    dates = [o.date for o in parsed.observations]
    assert dt.date(2025, 7, 4) not in dates
    assert all(o.value != 0 for o in parsed.observations)
    assert parsed.missing_dates == (dt.date(2025, 7, 4),)
    assert len(parsed.observations) == 2


def test_negative_and_integer_values_parse() -> None:
    parsed = parse_observations(answer([("2020-01-02", "-0.10"), ("2020-01-03", "2")]))
    assert [o.value for o in parsed.observations] == [Decimal("-0.10"), Decimal("2")]


def test_value_keeps_its_exact_decimal_text() -> None:
    parsed = parse_observations(answer([("2025-07-02", "4.30")]))
    assert str(parsed.observations[0].value) == "4.30"


# ── answers that must fail the parse (AC-003) ───────────────────────────────


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"error_code": 400, "error_message": "Bad Request.  The value for variable api_key is not registered."}, id="error-body"),
        pytest.param(answer([]), id="empty-series"),
        pytest.param(answer([("2025-07-02", "4.30"), ("2025-07-02", "4.31")]), id="repeated-date"),
        pytest.param(answer([("2025-07-02", "N/A")]), id="non-numeric"),
        pytest.param(answer([("2025-07-02", "")]), id="empty-value"),
        pytest.param(answer([("2025-07-02", "NaN")]), id="nan"),
        pytest.param(answer([("2025-07-02", "Infinity")]), id="infinity"),
        pytest.param(answer([("2025-07-02", "1e3")]), id="exponent"),
        pytest.param(answer([("2025-07-02", " 4.30")]), id="padded"),
        pytest.param(answer([("2025-07-02", "0")])["observations"], id="not-an-object"),
        pytest.param({"count": 0}, id="no-observations-key"),
        pytest.param(answer([("2025-13-02", "4.30")]), id="bad-date"),
        pytest.param(answer([("2025-07-02", "4.30")], count=2), id="count-mismatch"),
        pytest.param(answer([("2025-07-03", "4.30"), ("2025-07-02", "4.31")]), id="out-of-order"),
        pytest.param(answer([("2025-07-02", ".")]), id="only-missing"),
    ],
)
def test_invalid_answer_fails(payload: Any) -> None:
    with pytest.raises(FredParseError):
        parse_observations(payload)


def test_observation_with_number_value_fails() -> None:
    payload = answer([("2025-07-02", "4.30")])
    payload["observations"][0]["value"] = 4.30
    with pytest.raises(FredParseError):
        parse_observations(payload)


def test_error_message_is_reported() -> None:
    with pytest.raises(FredParseError, match="Bad Request"):
        parse_observations({"error_code": 400, "error_message": "Bad Request."})


# ── the recorded FRED answer (AC-001) ───────────────────────────────────────


def _recording() -> Any:
    if not RECORDING.exists():
        pytest.fail(f"{RECORDING.relative_to(ROOT)} is missing — record it with `python -m ingest.record_fixture`")
    return json.loads(RECORDING.read_text(encoding="utf-8"))


def test_recording_parses_ten_years_with_holidays_skipped() -> None:
    raw = _recording()
    parsed = parse_observations(raw)
    first = parsed.observations[0].date
    last = parsed.observations[-1].date
    assert (last - first).days >= 365 * 10 - 10
    # 4 July is a US holiday every year: FRED marks it ".", so it is skipped, never stored as 0.
    july4 = [d for d in parsed.missing_dates if (d.month, d.day) == (7, 4)]
    assert july4, "expected at least one 4 July holiday marked '.'"
    stored = {o.date for o in parsed.observations}
    assert not stored & set(parsed.missing_dates)
    assert all(o.value > 0 for o in parsed.observations)


def test_recording_every_point_equals_the_recorded_value() -> None:
    raw = _recording()
    parsed = parse_observations(raw)
    recorded = {r["date"]: r["value"] for r in raw["observations"] if r["value"] != "."}
    assert len(parsed.observations) == len(recorded)
    for o in parsed.observations:
        assert Decimal(recorded[o.date.isoformat()]) == o.value


def test_command_line_prints_count_and_skipped_dates(tmp_path: Path) -> None:
    f = tmp_path / "a.json"
    f.write_text(json.dumps(answer([("2025-07-03", "4.35"), ("2025-07-04", "."), ("2025-07-07", "4.39")])), "utf-8")
    run = subprocess.run(
        [sys.executable, "-m", "ingest.fred", str(f)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert run.returncode == 0, run.stderr
    assert "2 observations" in run.stdout
    assert "2025-07-04" in run.stdout


def test_command_line_fails_on_invalid_answer(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text(json.dumps(answer([])), "utf-8")
    run = subprocess.run(
        [sys.executable, "-m", "ingest.fred", str(f)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert run.returncode == 1
    assert "empty" in run.stderr.lower()

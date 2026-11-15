"""Tests for ingest.record_fixture — the FRED key never reaches the screen or the fixture (PLAN-0001 T1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import pytest

from ingest import record_fixture
from ingest.record_fixture import redact

FAKE_KEY = "fakekeyfakekeyfakekeyfakekey0000"  # 32 lowercase alphanumerics, FRED's key shape; not a real key
URL = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={FAKE_KEY}&file_type=json"


def test_redact_removes_api_key_from_a_url() -> None:
    out = redact(URL, FAKE_KEY)
    assert FAKE_KEY not in out
    assert "api_key=[REDACTED]" in out
    assert "series_id=DGS10" in out and "file_type=json" in out


def test_redact_removes_api_key_param_even_without_knowing_the_key() -> None:
    out = redact("GET /fred?api_key=zzzz9999&x=1", None)
    assert "zzzz9999" not in out
    assert "api_key=[REDACTED]&x=1" in out


def test_redact_removes_the_bare_key_and_encoded_forms() -> None:
    out = redact(f"key {FAKE_KEY} / api_key%3D{FAKE_KEY} / \"api_key\": \"{FAKE_KEY}\"", FAKE_KEY)
    assert FAKE_KEY not in out


def test_redact_leaves_clean_text_alone() -> None:
    assert redact("FRED answered HTTP 500", FAKE_KEY) == "FRED answered HTTP 500"


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """The key comes from the environment; the output goes to a temporary file, never the real fixture."""
    monkeypatch.setenv("FRED_API_KEY", FAKE_KEY)
    out = tmp_path / "fred_dgs10.json"
    monkeypatch.setattr(record_fixture, "OUT", out)
    monkeypatch.setattr(record_fixture, "ROOT", tmp_path)
    return out


def _fake_get(response: httpx.Response | Exception) -> Any:
    def get(url: str, params: dict[str, str], timeout: float) -> httpx.Response:
        if isinstance(response, Exception):
            raise response
        return response
    return get


def test_network_error_that_quotes_the_url_is_redacted(
    isolated: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    request = httpx.Request("GET", URL)
    monkeypatch.setattr(record_fixture.httpx, "get", _fake_get(httpx.ConnectError(f"failed to connect: {URL}", request=request)))
    assert record_fixture.main() == 1
    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out + captured.err
    assert "api_key=[REDACTED]" in captured.err
    assert not isolated.exists()


def test_error_body_that_echoes_the_key_is_redacted(
    isolated: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    body = {"error_code": 400, "error_message": f"Bad Request. The value {FAKE_KEY} for api_key is not registered."}
    monkeypatch.setattr(record_fixture.httpx, "get", _fake_get(httpx.Response(400, json=body)))
    assert record_fixture.main() == 1
    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out + captured.err
    assert "Bad Request" in captured.err
    assert not isolated.exists()


def test_answer_containing_the_key_is_not_saved(
    isolated: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    body = {"count": 1, "note": FAKE_KEY, "observations": [{"date": "2025-07-02", "value": "4.30"}]}
    monkeypatch.setattr(record_fixture.httpx, "get", _fake_get(httpx.Response(200, json=body)))
    assert record_fixture.main() == 1
    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out + captured.err
    assert not isolated.exists()


def test_good_answer_is_saved_without_the_key(
    isolated: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    body = {"count": 2, "observations": [{"date": "2025-07-03", "value": "4.35"}, {"date": "2025-07-04", "value": "."}]}
    monkeypatch.setattr(record_fixture.httpx, "get", _fake_get(httpx.Response(200, json=body)))
    assert record_fixture.main() == 0
    text = isolated.read_text(encoding="utf-8")
    assert FAKE_KEY not in text and "api_key" not in text
    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out + captured.err
    assert "1 observations" in captured.out

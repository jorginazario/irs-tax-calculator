"""Integration tests for the /api/history endpoints."""

import sqlite3

import pytest
from starlette.testclient import TestClient

from src.api.main import app
from src.database import db as db_module

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures — redirect DB to a temp file for each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolate_db(tmp_path, monkeypatch):
    """Each test gets its own temporary SQLite database."""
    db_path = tmp_path / "test_history.db"
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    schema = db_module._SCHEMA_PATH.read_text()
    conn.executescript(schema)
    monkeypatch.setattr(db_module, "_connection", conn)
    monkeypatch.setattr(db_module, "get_db", lambda: conn)
    yield
    conn.close()


def _do_calculation() -> dict:
    """Run a full calculation via the API and return the response JSON."""
    payload = {
        "filing_status": "SINGLE",
        "w2s": [{"wages": "75000", "federal_withholding": "9000"}],
    }
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHistoryList:
    def test_empty_history(self):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_after_calculation(self):
        _do_calculation()
        resp = client.get("/api/history")
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 1
        assert rows[0]["filing_status"] == "SINGLE"
        assert rows[0]["total_income"] == 75000.0
        # Should not include JSON blobs
        assert "input_data" not in rows[0]
        assert "result_data" not in rows[0]

    def test_multiple_calculations_newest_first(self):
        _do_calculation()
        _do_calculation()
        resp = client.get("/api/history")
        rows = resp.json()
        assert len(rows) == 2
        assert rows[0]["id"] > rows[1]["id"]


class TestHistoryDetail:
    def test_get_existing(self):
        _do_calculation()
        listing = client.get("/api/history").json()
        calc_id = listing[0]["id"]

        resp = client.get(f"/api/history/{calc_id}")
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["id"] == calc_id
        assert detail["filing_status"] == "SINGLE"
        assert isinstance(detail["input_data"], dict)
        assert isinstance(detail["result_data"], dict)

    def test_get_nonexistent_returns_404(self):
        resp = client.get("/api/history/9999")
        assert resp.status_code == 404


class TestHistoryDelete:
    def test_delete_existing(self):
        _do_calculation()
        listing = client.get("/api/history").json()
        calc_id = listing[0]["id"]

        resp = client.delete(f"/api/history/{calc_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

        # Verify it's gone
        assert client.get(f"/api/history/{calc_id}").status_code == 404

    def test_delete_nonexistent_returns_404(self):
        resp = client.delete("/api/history/9999")
        assert resp.status_code == 404

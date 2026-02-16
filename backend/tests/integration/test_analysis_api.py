"""Integration tests for the analysis API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.database import db as db_module

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolate_db(tmp_path, monkeypatch):
    """Redirect the database to a temporary path for every test."""
    import sqlite3

    db_path = tmp_path / "test_tax.db"
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    schema = db_module._SCHEMA_PATH.read_text()
    conn.executescript(schema)
    monkeypatch.setattr(db_module, "_connection", conn)
    monkeypatch.setattr(db_module, "get_db", lambda: conn)
    yield
    conn.close()


# ---------------------------------------------------------------------------
# Tests: API key guard (should return 503 when ANTHROPIC_API_KEY is not set)
# ---------------------------------------------------------------------------

class TestApiKeyGuard:
    """All analysis endpoints should return 503 when ANTHROPIC_API_KEY is missing."""

    @pytest.fixture(autouse=True)
    def _clear_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def test_query_returns_503(self):
        resp = client.post("/api/analysis/query", json={"question": "How many?"})
        assert resp.status_code == 503

    def test_chart_returns_503(self):
        resp = client.post("/api/analysis/chart", json={"prompt": "Bar chart"})
        assert resp.status_code == 503

    def test_table_returns_503(self):
        resp = client.post("/api/analysis/table", json={"prompt": "Show table"})
        assert resp.status_code == 503

    def test_report_returns_503(self):
        resp = client.post("/api/analysis/report", json={"prompt": "Full report"})
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Tests: Mocked tool calls (with ANTHROPIC_API_KEY set)
# ---------------------------------------------------------------------------

class TestMockedToolCalls:
    """Test that endpoints call the right MCP tool functions."""

    @pytest.fixture(autouse=True)
    def _set_api_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

    @patch("mcp_server.tools.query_data.query_tax_data", new_callable=AsyncMock)
    def test_query_calls_tool(self, mock_fn):
        mock_fn.return_value = "Query: SELECT 1\n\n1 row"
        resp = client.post("/api/analysis/query", json={"question": "Count rows"})
        assert resp.status_code == 200
        assert resp.json()["result"] == "Query: SELECT 1\n\n1 row"
        mock_fn.assert_awaited_once_with("Count rows")

    @patch("mcp_server.tools.create_chart.create_chart", new_callable=AsyncMock)
    def test_chart_calls_tool(self, mock_fn):
        mock_fn.return_value = "<html>chart</html>"
        resp = client.post("/api/analysis/chart", json={"prompt": "Bar chart"})
        assert resp.status_code == 200
        assert "<html>" in resp.json()["result"]
        mock_fn.assert_awaited_once_with("Bar chart")

    @patch("mcp_server.tools.create_table.create_table", new_callable=AsyncMock)
    def test_table_calls_tool(self, mock_fn):
        mock_fn.return_value = "## Table\n| col |\n|---|\n| val |"
        resp = client.post("/api/analysis/table", json={"prompt": "Show table"})
        assert resp.status_code == 200
        assert "Table" in resp.json()["result"]
        mock_fn.assert_awaited_once_with("Show table")

    @patch("mcp_server.tools.generate_report.generate_report", new_callable=AsyncMock)
    def test_report_calls_tool(self, mock_fn):
        mock_fn.return_value = "## Executive Summary\nAll good."
        resp = client.post("/api/analysis/report", json={"prompt": "Full report"})
        assert resp.status_code == 200
        assert "Executive Summary" in resp.json()["result"]
        mock_fn.assert_awaited_once_with("Full report")

"""Tests for the SQLite database repository layer."""

import sqlite3
from unittest.mock import patch

import pytest

from src.database import db as db_module
from src.database.repository import (
    delete_calculation,
    get_calculation,
    list_calculations,
    save_calculation,
)
from src.models.workflow_models import FullTaxCalculationResult, TaxReturnInput
from src.workflows.orchestrator import calculate_full_tax

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_test_connection(tmp_path):
    """Create a fresh in-memory-style SQLite DB in tmp_path and return it."""
    db_path = tmp_path / "test_tax.db"
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    schema = db_module._SCHEMA_PATH.read_text()
    conn.executescript(schema)
    return conn


@pytest.fixture(autouse=True)
def _isolate_db(tmp_path, monkeypatch):
    """Redirect the repository to a temporary database for every test."""
    conn = _make_test_connection(tmp_path)
    monkeypatch.setattr(db_module, "_connection", conn)
    # Make get_db() always return our test connection
    monkeypatch.setattr(db_module, "get_db", lambda: conn)
    yield
    conn.close()


def _sample_input() -> TaxReturnInput:
    return TaxReturnInput(
        filing_status="SINGLE",
        w2s=[{"wages": "75000", "federal_withholding": "9000"}],
    )


def _sample_result(tax_input: TaxReturnInput | None = None) -> FullTaxCalculationResult:
    """Build a result via the orchestrator but suppress the auto-save side effect."""
    if tax_input is None:
        tax_input = _sample_input()
    with patch("src.database.repository.save_calculation"):
        return calculate_full_tax(tax_input)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSaveCalculation:
    def test_returns_int_id(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        row_id = save_calculation(tax_input, result)
        assert isinstance(row_id, int)
        assert row_id >= 1

    def test_sequential_ids(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        id1 = save_calculation(tax_input, result)
        id2 = save_calculation(tax_input, result)
        assert id2 == id1 + 1


class TestListCalculations:
    def test_empty_list(self):
        rows = list_calculations()
        assert rows == []

    def test_returns_correct_summaries(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        save_calculation(tax_input, result)

        rows = list_calculations()
        assert len(rows) == 1
        row = rows[0]
        assert row["filing_status"] == "SINGLE"
        assert row["total_income"] == float(result.summary.total_income)
        # Summary rows should NOT contain JSON blobs
        assert "input_data" not in row
        assert "result_data" not in row

    def test_newest_first(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        id1 = save_calculation(tax_input, result)
        id2 = save_calculation(tax_input, result)

        rows = list_calculations()
        assert len(rows) == 2
        assert rows[0]["id"] == id2
        assert rows[1]["id"] == id1


class TestGetCalculation:
    def test_returns_full_row(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        row_id = save_calculation(tax_input, result)

        row = get_calculation(row_id)
        assert row is not None
        assert row["id"] == row_id
        assert row["filing_status"] == "SINGLE"
        # JSON blobs should be parsed
        assert isinstance(row["input_data"], dict)
        assert isinstance(row["result_data"], dict)
        assert row["input_data"]["filing_status"] == "SINGLE"

    def test_nonexistent_returns_none(self):
        assert get_calculation(9999) is None


class TestDeleteCalculation:
    def test_delete_existing(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        row_id = save_calculation(tax_input, result)

        assert delete_calculation(row_id) is True
        assert get_calculation(row_id) is None

    def test_delete_nonexistent(self):
        assert delete_calculation(9999) is False


class TestMultipleSavesAndList:
    def test_three_saves(self):
        tax_input = _sample_input()
        result = _sample_result(tax_input)
        for _ in range(3):
            save_calculation(tax_input, result)

        rows = list_calculations()
        assert len(rows) == 3
        # IDs should be descending (newest first)
        ids = [r["id"] for r in rows]
        assert ids == sorted(ids, reverse=True)

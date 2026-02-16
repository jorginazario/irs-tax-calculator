"""CRUD operations for tax calculation history."""

import json

from src.database.db import get_db
from src.models.workflow_models import FullTaxCalculationResult, TaxReturnInput


def save_calculation(tax_input: TaxReturnInput, result: FullTaxCalculationResult) -> int:
    """Persist a tax calculation. Returns the new row id."""
    conn = get_db()
    summary = result.summary
    cursor = conn.execute(
        """
        INSERT INTO tax_calculations
            (filing_status, input_data, total_income, agi, taxable_income,
             federal_tax, total_credits, total_tax, effective_rate,
             marginal_rate, refund_or_owed, result_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tax_input.filing_status.value,
            tax_input.model_dump_json(),
            float(summary.total_income),
            float(summary.agi),
            float(summary.taxable_income),
            float(summary.total_income_tax_before_credits),
            float(summary.total_credits),
            float(summary.total_tax),
            float(summary.effective_rate),
            float(summary.marginal_rate),
            float(summary.refund_or_owed),
            result.model_dump_json(),
        ),
    )
    conn.commit()
    return cursor.lastrowid  # type: ignore[return-value]


def list_calculations() -> list[dict]:
    """Return summary rows (no JSON blobs) ordered by newest first."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, created_at, filing_status, total_income, agi,
               taxable_income, federal_tax, total_credits, total_tax,
               effective_rate, marginal_rate, refund_or_owed
        FROM tax_calculations
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_calculation(calc_id: int) -> dict | None:
    """Return a full row (including parsed JSON blobs) or None."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tax_calculations WHERE id = ?", (calc_id,)
    ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["input_data"] = json.loads(result["input_data"])
    result["result_data"] = json.loads(result["result_data"])
    return result


def delete_calculation(calc_id: int) -> bool:
    """Delete a calculation by id. Returns True if a row was actually deleted."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM tax_calculations WHERE id = ?", (calc_id,))
    conn.commit()
    return cursor.rowcount > 0

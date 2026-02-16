"""Tool for creating formatted markdown tables from tax data."""

import json
import sqlite3
from pathlib import Path

import anthropic

from mcp_server.context import get_system_prompt

DB_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "tax_data.db"

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "REPLACE", "ATTACH", "DETACH",
}


def _get_readonly_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Tax database not found at {DB_PATH}. "
            "Run a tax calculation first to create the database."
        )
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _validate_readonly_sql(sql: str) -> bool:
    upper = sql.upper()
    tokens = upper.split()
    return not any(kw in tokens for kw in FORBIDDEN_KEYWORDS)


def _ask_claude(system_prompt: str, user_prompt: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _extract_json(text: str) -> dict:
    """Extract JSON from Claude's response, handling markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()
    return json.loads(cleaned)


def _format_markdown_table(rows: list[dict], columns: list[str], title: str) -> str:
    """Build a markdown table from rows and column names."""
    if not rows:
        return f"## {title}\n\nNo data found."

    # Calculate display values
    display_rows = []
    for row in rows:
        display_row = {}
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                display_row[col] = f"{val:,.2f}"
            elif val is None:
                display_row[col] = ""
            else:
                display_row[col] = str(val)
        display_rows.append(display_row)

    # Build markdown
    lines = [f"## {title}", ""]

    # Header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines.extend([header, separator])

    # Data rows
    for row in display_rows:
        line = "| " + " | ".join(row.get(col, "") for col in columns) + " |"
        lines.append(line)

    lines.append(f"\n*{len(display_rows)} row{'s' if len(display_rows) != 1 else ''}*")
    return "\n".join(lines)


async def create_table(prompt: str) -> str:
    """Generate a formatted markdown table from tax data.

    Uses Claude to determine the SQL query and column formatting,
    then produces a clean markdown table.

    Args:
        prompt: Description of the desired table.

    Returns:
        Markdown-formatted table string.
    """
    if not prompt.strip():
        return "Error: Please describe the table you want to create."

    system_prompt = get_system_prompt("create_table")

    table_request = (
        f"User wants this table: {prompt}\n\n"
        "Return a JSON object with exactly these keys:\n"
        "- \"sql\": a SELECT query to get the data\n"
        "- \"columns\": list of column display names (matching SQL column aliases)\n"
        "- \"title\": a descriptive title for the table\n\n"
        "Use column aliases in your SQL to give human-readable names.\n"
        "Return ONLY valid JSON, no other text."
    )

    try:
        response_text = _ask_claude(system_prompt, table_request)
    except anthropic.APIError as e:
        return f"Error communicating with Claude API: {e}"

    try:
        plan = _extract_json(response_text)
    except (json.JSONDecodeError, ValueError):
        return f"Error: Could not parse table plan.\nRaw response: {response_text[:500]}"

    sql = plan.get("sql", "")
    columns = plan.get("columns", [])
    title = plan.get("title", "Tax Data")

    if not sql or not columns:
        return "Error: Claude did not provide both SQL and column names."

    if not _validate_readonly_sql(sql):
        return "Error: Generated query contains forbidden operations."

    try:
        conn = _get_readonly_connection()
    except FileNotFoundError as e:
        return str(e)

    try:
        cursor = conn.execute(sql)
        raw_rows = cursor.fetchall()
        actual_columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(zip(actual_columns, row)) for row in raw_rows]
    except sqlite3.Error as e:
        conn.close()
        return f"SQL Error: {e}\nGenerated query: {sql}"
    finally:
        conn.close()

    # Use actual column names from query results if they differ
    display_columns = actual_columns if actual_columns else columns

    return _format_markdown_table(rows, display_columns, title)

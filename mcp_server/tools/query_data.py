"""Tool for querying tax data using natural language questions."""

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
    """Open a read-only SQLite connection to the tax database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Tax database not found at {DB_PATH}. "
            "Run a tax calculation first to create the database."
        )
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _validate_readonly_sql(sql: str) -> bool:
    """Check that the SQL contains only read operations."""
    upper = sql.upper()
    tokens = upper.split()
    return not any(kw in tokens for kw in FORBIDDEN_KEYWORDS)


def _ask_claude(system_prompt: str, user_prompt: str) -> str:
    """Call the Claude API with the given prompts."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _format_results(rows: list[sqlite3.Row], columns: list[str]) -> str:
    """Format query results as a readable text table."""
    if not rows:
        return "No results found."

    # Convert rows to list of dicts
    data = [dict(row) for row in rows]

    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            val = str(row.get(col, ""))
            widths[col] = max(widths[col], len(val))

    # Build header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)

    # Build rows
    lines = [header, separator]
    for row in data:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        lines.append(line)

    lines.append(f"\n({len(data)} row{'s' if len(data) != 1 else ''})")
    return "\n".join(lines)


async def query_tax_data(question: str) -> str:
    """Query tax calculation history using natural language.

    Translates a natural language question into SQL, executes it against
    the tax_calculations database, and returns formatted results.

    Args:
        question: A natural language question about tax calculations.

    Returns:
        Formatted text with query results.
    """
    if not question.strip():
        return "Error: Please provide a question about your tax data."

    # Step 1: Translate question to SQL
    system_prompt = get_system_prompt("query_data")
    try:
        sql = _ask_claude(system_prompt, question).strip()
    except anthropic.APIError as e:
        return f"Error communicating with Claude API: {e}"

    # Clean up: remove markdown code fences if present
    if sql.startswith("```"):
        lines = sql.split("\n")
        sql = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    # Step 2: Validate SQL is read-only
    if not _validate_readonly_sql(sql):
        return "Error: Generated query contains forbidden operations. Only SELECT queries are allowed."

    # Step 3: Execute query
    try:
        conn = _get_readonly_connection()
    except FileNotFoundError as e:
        return str(e)

    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        result = _format_results(rows, columns)
        return f"Query: {sql}\n\n{result}"
    except sqlite3.Error as e:
        return f"SQL Error: {e}\nGenerated query: {sql}"
    finally:
        conn.close()

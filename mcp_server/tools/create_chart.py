"""Tool for creating Plotly charts from tax data."""

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


async def create_chart(prompt: str) -> str:
    """Generate a Plotly chart from tax data based on a user prompt.

    Uses Claude to determine the appropriate SQL query and chart type,
    then generates a self-contained HTML visualization.

    Args:
        prompt: Description of the desired chart/visualization.

    Returns:
        Self-contained HTML string with the Plotly chart, or an error message.
    """
    if not prompt.strip():
        return "Error: Please describe the chart you want to create."

    system_prompt = get_system_prompt("create_chart")

    chart_request = (
        f"User wants this chart: {prompt}\n\n"
        "Return a JSON object with exactly these keys:\n"
        "- \"sql\": a SELECT query to get the data needed\n"
        "- \"plotly_code\": Python code using plotly.graph_objects that:\n"
        "  1. Assumes a variable 'rows' exists as a list of dicts with the query results\n"
        "  2. Creates a plotly figure assigned to variable 'fig'\n"
        "  3. Does NOT call fig.show()\n"
        "  4. Uses a clean, professional style\n\n"
        "Return ONLY valid JSON, no other text."
    )

    try:
        response_text = _ask_claude(system_prompt, chart_request)
    except anthropic.APIError as e:
        return f"Error communicating with Claude API: {e}"

    # Parse the response
    try:
        plan = _extract_json(response_text)
    except (json.JSONDecodeError, ValueError):
        return f"Error: Could not parse chart plan from Claude response.\nRaw response: {response_text[:500]}"

    sql = plan.get("sql", "")
    plotly_code = plan.get("plotly_code", "")

    if not sql or not plotly_code:
        return "Error: Claude did not provide both SQL and Plotly code."

    # Validate SQL
    if not _validate_readonly_sql(sql):
        return "Error: Generated query contains forbidden operations. Only SELECT queries are allowed."

    # Execute SQL
    try:
        conn = _get_readonly_connection()
    except FileNotFoundError as e:
        return str(e)

    try:
        cursor = conn.execute(sql)
        raw_rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in raw_rows]
    except sqlite3.Error as e:
        conn.close()
        return f"SQL Error: {e}\nGenerated query: {sql}"
    finally:
        conn.close()

    if not rows:
        return "No data found to chart. Run some tax calculations first."

    # Execute Plotly code in a sandboxed namespace
    import plotly.graph_objects as go

    namespace = {"rows": rows, "go": go}
    try:
        exec(plotly_code, namespace)  # noqa: S102
    except Exception as e:
        return f"Error executing chart code: {e}\nGenerated code:\n{plotly_code}"

    fig = namespace.get("fig")
    if fig is None:
        return "Error: Chart code did not produce a 'fig' variable."

    # Generate self-contained HTML
    try:
        html = fig.to_html(include_plotlyjs="cdn", full_html=True)
        return html
    except Exception as e:
        return f"Error generating HTML: {e}"

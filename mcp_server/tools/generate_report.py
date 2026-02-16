"""Tool for generating analytical reports from tax data."""

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


async def generate_report(prompt: str) -> str:
    """Generate a comprehensive analytical report from tax data.

    Uses Claude to determine what data to query, gathers the results,
    then produces a formatted report with insights and analysis.

    Args:
        prompt: Description of the desired report.

    Returns:
        Formatted text report with sections and analysis.
    """
    if not prompt.strip():
        return "Error: Please describe the report you want to generate."

    system_prompt = get_system_prompt("generate_report")

    # Step 1: Ask Claude to plan the data gathering
    planning_request = (
        f"User wants this report: {prompt}\n\n"
        "Return a JSON object with exactly these keys:\n"
        "- \"queries\": a list of SQL SELECT queries to gather the needed data "
        "(each query should be a string)\n"
        "- \"analysis_prompt\": a description of what analysis to perform "
        "once the data is collected\n\n"
        "Include queries for summary statistics, breakdowns, and any relevant "
        "aggregations. Return ONLY valid JSON, no other text."
    )

    try:
        plan_text = _ask_claude(system_prompt, planning_request)
    except anthropic.APIError as e:
        return f"Error communicating with Claude API: {e}"

    try:
        plan = _extract_json(plan_text)
    except (json.JSONDecodeError, ValueError):
        return f"Error: Could not parse report plan.\nRaw response: {plan_text[:500]}"

    queries = plan.get("queries", [])
    analysis_prompt = plan.get("analysis_prompt", "Analyze the tax data.")

    if not queries:
        return "Error: No data queries were generated for this report."

    # Step 2: Execute all queries and gather data
    try:
        conn = _get_readonly_connection()
    except FileNotFoundError as e:
        return str(e)

    gathered_data = []
    try:
        for i, sql in enumerate(queries):
            if not isinstance(sql, str):
                continue
            if not _validate_readonly_sql(sql):
                gathered_data.append(f"Query {i + 1}: SKIPPED (contains forbidden operations)")
                continue
            try:
                cursor = conn.execute(sql)
                raw_rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = [dict(zip(columns, row)) for row in raw_rows]
                gathered_data.append(
                    f"Query {i + 1}: {sql}\n"
                    f"Results ({len(rows)} rows): {json.dumps(rows, indent=2, default=str)}"
                )
            except sqlite3.Error as e:
                gathered_data.append(f"Query {i + 1}: ERROR - {e}\nSQL: {sql}")
    finally:
        conn.close()

    if not gathered_data:
        return "No data could be retrieved. Run some tax calculations first."

    # Step 3: Ask Claude to write the report based on gathered data
    data_section = "\n\n".join(gathered_data)

    report_request = (
        f"Based on the following tax calculation data, write a comprehensive report.\n\n"
        f"Analysis goal: {analysis_prompt}\n\n"
        f"Data gathered:\n{data_section}\n\n"
        "Write a well-structured report with:\n"
        "1. Executive summary\n"
        "2. Key findings with specific numbers\n"
        "3. Breakdown by relevant categories\n"
        "4. Notable observations or insights\n"
        "5. Recommendations if applicable\n\n"
        "Use clear section headers (markdown ##). Include specific dollar amounts "
        "and percentages. Be concise but thorough."
    )

    report_system = (
        "You are a tax data analyst writing a report. Use the provided data to create "
        "a clear, professional report. All numbers should be formatted with commas "
        "and dollar signs where appropriate. Percentages should be clearly labeled. "
        "If the data is empty or insufficient, note that clearly."
    )

    try:
        report = _ask_claude(report_system, report_request)
    except anthropic.APIError as e:
        return f"Error generating report: {e}"

    return report

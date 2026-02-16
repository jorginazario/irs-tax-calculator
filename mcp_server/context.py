"""Tax domain context for LLM system prompts used by MCP tools."""

SCHEMA_CONTEXT = """
Database: SQLite (backend/tax_data.db)

Table: tax_calculations
  id              INTEGER PRIMARY KEY AUTOINCREMENT
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))  -- ISO 8601 timestamp
  filing_status   TEXT NOT NULL   -- One of: SINGLE, MARRIED_FILING_JOINTLY, MARRIED_FILING_SEPARATELY, HEAD_OF_HOUSEHOLD, QUALIFYING_SURVIVING_SPOUSE
  input_data      TEXT NOT NULL   -- Full JSON of TaxReturnInput (W-2s, 1099s, deductions, credits)
  total_income    REAL NOT NULL   -- Gross income from all sources
  agi             REAL NOT NULL   -- Adjusted Gross Income
  taxable_income  REAL NOT NULL   -- Income after deductions
  federal_tax     REAL NOT NULL   -- Federal income tax before credits
  total_credits   REAL NOT NULL   -- Sum of all applied tax credits
  total_tax       REAL NOT NULL   -- Final tax liability after credits
  effective_rate  REAL NOT NULL   -- Effective tax rate (total_tax / total_income), stored as decimal (0.22 = 22%)
  marginal_rate   REAL NOT NULL   -- Marginal tax bracket rate, stored as decimal
  refund_or_owed  REAL NOT NULL   -- Negative = refund due, Positive = amount owed
  result_data     TEXT NOT NULL   -- Full JSON of FullTaxCalculationResult
""".strip()

DOMAIN_CONTEXT = """
Tax Domain Knowledge (Tax Year 2024):

Filing Statuses:
  - SINGLE: Unmarried individual
  - MARRIED_FILING_JOINTLY (MFJ): Married couple filing together
  - MARRIED_FILING_SEPARATELY (MFS): Married individual filing alone
  - HEAD_OF_HOUSEHOLD (HoH): Unmarried with qualifying dependent
  - QUALIFYING_SURVIVING_SPOUSE: Widowed with dependent child

Key Relationships:
  - total_income >= agi >= taxable_income (always true)
  - effective_rate = total_tax / total_income (as a decimal, e.g. 0.22 = 22%)
  - refund_or_owed: negative means a refund is due, positive means taxes are owed
  - federal_tax is before credits; total_tax = federal_tax - total_credits (approximately)

Income Sources (in input_data JSON):
  - W-2: wages, salaries, tips from an employer
  - 1099-NEC: freelance/contract income (self-employment)
  - 1099-INT: interest income
  - 1099-DIV: ordinary and qualified dividends
  - 1099-B: short-term and long-term capital gains/losses

2024 Federal Brackets (Single): 10%, 12%, 22%, 24%, 32%, 35%, 37%
Standard Deduction (2024): Single $14,600 | MFJ $29,200 | HoH $21,900
""".strip()

_TOOL_DESCRIPTIONS = {
    "query_data": "You translate natural language questions about tax data into SQL queries. Return ONLY the SQL query, no explanation.",
    "create_chart": "You analyze tax data visualization requests and produce Plotly Python code. Return a JSON object with keys: 'sql' (the query to run) and 'plotly_code' (Python code using plotly that assumes a variable 'rows' containing query results as list of dicts).",
    "create_table": "You analyze tax data table requests and produce SQL queries with formatting hints. Return a JSON object with keys: 'sql' (the query to run), 'columns' (list of column display names), and 'title' (table title).",
    "generate_report": "You analyze tax data and write comprehensive reports. Return a JSON object with keys: 'queries' (list of SQL queries to run for gathering data) and 'analysis_prompt' (a prompt describing what to analyze given the query results).",
}


def get_system_prompt(tool_name: str) -> str:
    """Return a system prompt tailored for the given tool.

    Args:
        tool_name: One of 'query_data', 'create_chart', 'create_table', 'generate_report'.

    Returns:
        A system prompt string for use with the Claude API.
    """
    tool_desc = _TOOL_DESCRIPTIONS.get(tool_name, "You help analyze tax calculation data.")

    return f"""You are a data analyst specializing in US federal tax data for tax year 2024.

{tool_desc}

{SCHEMA_CONTEXT}

{DOMAIN_CONTEXT}

Important rules:
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
- Use the exact column names from the schema.
- When filtering by filing_status, use the exact enum values (e.g., WHERE filing_status = 'SINGLE').
- Rates are stored as decimals (0.22 not 22). Multiply by 100 for display percentages.
- For monetary values, round to 2 decimal places in queries.
- The input_data and result_data columns contain JSON. Use json_extract() for querying nested fields.
"""

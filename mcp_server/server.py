"""MCP server for tax data analysis.

Exposes tools for querying, charting, tabulating, and reporting on
tax calculation history stored in the SQLite database.

Run with: python -m mcp_server.server
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tax Data Analyst")


@mcp.tool()
async def query_tax_data(question: str) -> str:
    """Query your tax calculation history using natural language.

    Ask questions like:
    - "How many calculations have been run?"
    - "What is the average effective tax rate for single filers?"
    - "Show me all calculations with income over $100,000"

    Args:
        question: A natural language question about your tax data.

    Returns:
        Formatted text with the query results.
    """
    from mcp_server.tools.query_data import query_tax_data as _query

    return await _query(question)


@mcp.tool()
async def create_chart(prompt: str) -> str:
    """Generate a Plotly chart from your tax data.

    Describe the visualization you want, for example:
    - "Bar chart of total tax by filing status"
    - "Scatter plot of income vs effective tax rate"
    - "Pie chart showing the breakdown of tax credits"

    Args:
        prompt: Description of the chart you want to create.

    Returns:
        Self-contained HTML string with the Plotly chart.
    """
    from mcp_server.tools.create_chart import create_chart as _chart

    return await _chart(prompt)


@mcp.tool()
async def create_table(prompt: str) -> str:
    """Generate a formatted data table from your tax data.

    Describe the table you want, for example:
    - "Summary of all calculations sorted by total tax"
    - "Comparison of effective rates across filing statuses"
    - "Top 5 calculations by income"

    Args:
        prompt: Description of the table you want to create.

    Returns:
        Markdown-formatted table string.
    """
    from mcp_server.tools.create_table import create_table as _table

    return await _table(prompt)


@mcp.tool()
async def generate_report(prompt: str) -> str:
    """Generate an analytical report from your tax data.

    Describe the report you want, for example:
    - "Full analysis of all tax calculations"
    - "Compare tax outcomes for different filing statuses"
    - "Report on the impact of credits on final tax liability"

    Args:
        prompt: Description of the report you want to generate.

    Returns:
        Formatted analytical report with insights and recommendations.
    """
    from mcp_server.tools.generate_report import generate_report as _report

    return await _report(prompt)


if __name__ == "__main__":
    mcp.run()

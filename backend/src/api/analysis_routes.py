"""FastAPI routes for AI-powered tax data analysis.

Wraps the MCP server tool functions so the frontend can call them via HTTP.
Requires ANTHROPIC_API_KEY to be set in the environment.
"""

import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add project root so mcp_server package is importable
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

analysis_router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class PromptRequest(BaseModel):
    prompt: str


class AnalysisResponse(BaseModel):
    result: str


def _check_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not set. Analysis features require a valid API key.",
        )


@analysis_router.post("/analysis/query", response_model=AnalysisResponse)
async def analysis_query(body: QueryRequest) -> AnalysisResponse:
    """Query tax data using natural language."""
    _check_api_key()
    from mcp_server.tools.query_data import query_tax_data

    result = await query_tax_data(body.question)
    return AnalysisResponse(result=result)


@analysis_router.post("/analysis/chart", response_model=AnalysisResponse)
async def analysis_chart(body: PromptRequest) -> AnalysisResponse:
    """Generate a Plotly chart from tax data."""
    _check_api_key()
    from mcp_server.tools.create_chart import create_chart

    result = await create_chart(body.prompt)
    return AnalysisResponse(result=result)


@analysis_router.post("/analysis/table", response_model=AnalysisResponse)
async def analysis_table(body: PromptRequest) -> AnalysisResponse:
    """Generate a markdown table from tax data."""
    _check_api_key()
    from mcp_server.tools.create_table import create_table

    result = await create_table(body.prompt)
    return AnalysisResponse(result=result)


@analysis_router.post("/analysis/report", response_model=AnalysisResponse)
async def analysis_report(body: PromptRequest) -> AnalysisResponse:
    """Generate an analytical report from tax data."""
    _check_api_key()
    from mcp_server.tools.generate_report import generate_report

    result = await generate_report(body.prompt)
    return AnalysisResponse(result=result)

"""API-specific Pydantic models — request/response schemas for FastAPI endpoints."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from src.models.filing_status import FilingStatus


class EstimateInput(BaseModel):
    """Quick estimate input — gross income + filing status only."""

    gross_income: Decimal = Field(ge=0, description="Total gross income")
    filing_status: FilingStatus


class EstimateResult(BaseModel):
    """Quick estimate output — simplified tax summary."""

    gross_income: Decimal
    filing_status: FilingStatus
    standard_deduction: Decimal
    taxable_income: Decimal
    estimated_tax: Decimal
    effective_rate: Decimal
    marginal_rate: Decimal


class BracketEntry(BaseModel):
    """One bracket in a tax bracket schedule."""

    upper_bound: Decimal | None = None
    rate: Decimal


class BracketsResponse(BaseModel):
    """All 2024 federal income-tax brackets by filing status."""

    tax_year: int = 2024
    brackets: dict[str, list[BracketEntry]]


class DeductionsResponse(BaseModel):
    """Standard deduction amounts by filing status for 2024."""

    tax_year: int = 2024
    standard_deductions: dict[str, Decimal]


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


# ---------------------------------------------------------------------------
# History / persistence models
# ---------------------------------------------------------------------------


class CalculationSummary(BaseModel):
    """Summary row returned by the list endpoint (no JSON blobs)."""

    id: int
    created_at: str
    filing_status: str
    total_income: float
    agi: float
    taxable_income: float
    federal_tax: float
    total_credits: float
    total_tax: float
    effective_rate: float
    marginal_rate: float
    refund_or_owed: float


class CalculationDetail(BaseModel):
    """Full calculation record including serialised input and result."""

    id: int
    created_at: str
    filing_status: str
    total_income: float
    agi: float
    taxable_income: float
    federal_tax: float
    total_credits: float
    total_tax: float
    effective_rate: float
    marginal_rate: float
    refund_or_owed: float
    input_data: Any
    result_data: Any


class DeleteResponse(BaseModel):
    """Response for delete operations."""

    success: bool
    message: str

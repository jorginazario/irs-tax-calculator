"""FastAPI routes for the IRS Tax Calculator API."""

from decimal import Decimal

from fastapi import APIRouter

from src.api.models import (
    BracketEntry,
    BracketsResponse,
    DeductionsResponse,
    EstimateInput,
    EstimateResult,
)
from src.data.tax_year_2024 import FEDERAL_BRACKETS, STANDARD_DEDUCTION
from src.models.workflow_models import FullTaxCalculationResult, TaxReturnInput
from src.tools.calculate_bracket_tax import calculate_bracket_tax
from src.tools.lookup_standard_deduction import lookup_standard_deduction
from src.workflows.orchestrator import calculate_full_tax

router = APIRouter()


@router.post("/calculate", response_model=FullTaxCalculationResult)
def full_calculation(tax_return: TaxReturnInput) -> FullTaxCalculationResult:
    """Full tax calculation — accepts all income sources and deductions.

    Runs the complete pipeline: income aggregation, FICA, AGI, deductions,
    tax computation, credits, and summary.
    """
    return calculate_full_tax(tax_return)


@router.post("/calculate/estimate", response_model=EstimateResult)
def quick_estimate(body: EstimateInput) -> EstimateResult:
    """Quick estimate from gross income + filing status.

    Uses the standard deduction and bracket tax only — no FICA, credits, or
    investment income breakdown.
    """
    std_ded = lookup_standard_deduction(body.filing_status)
    taxable_income = max(body.gross_income - std_ded.total_deduction, Decimal("0"))
    bracket_result = calculate_bracket_tax(taxable_income, body.filing_status)

    return EstimateResult(
        gross_income=body.gross_income,
        filing_status=body.filing_status,
        standard_deduction=std_ded.total_deduction,
        taxable_income=taxable_income,
        estimated_tax=bracket_result.total_tax,
        effective_rate=bracket_result.effective_rate,
        marginal_rate=bracket_result.marginal_rate,
    )


@router.get("/brackets/2024", response_model=BracketsResponse)
def get_brackets() -> BracketsResponse:
    """Return 2024 federal income-tax brackets for all filing statuses."""
    brackets: dict[str, list[BracketEntry]] = {}
    for status, bracket_list in FEDERAL_BRACKETS.items():
        brackets[status] = [
            BracketEntry(upper_bound=upper, rate=rate)
            for upper, rate in bracket_list
        ]
    return BracketsResponse(brackets=brackets)


@router.get("/deductions/2024", response_model=DeductionsResponse)
def get_deductions() -> DeductionsResponse:
    """Return 2024 standard deduction amounts for all filing statuses."""
    return DeductionsResponse(standard_deductions=STANDARD_DEDUCTION)

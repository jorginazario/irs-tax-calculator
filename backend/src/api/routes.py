"""FastAPI routes for the IRS Tax Calculator API."""

from decimal import Decimal

from fastapi import APIRouter, HTTPException

from src.api.models import (
    BracketEntry,
    BracketsResponse,
    CalculationDetail,
    CalculationSummary,
    DeductionsResponse,
    DeleteResponse,
    EstimateInput,
    EstimateResult,
)
from src.data.tax_year_2024 import FEDERAL_BRACKETS, STANDARD_DEDUCTION
from src.database.repository import (
    delete_calculation,
    get_calculation,
    list_calculations,
)
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


# ---------------------------------------------------------------------------
# History endpoints
# ---------------------------------------------------------------------------


@router.get("/history", response_model=list[CalculationSummary])
def history_list() -> list[CalculationSummary]:
    """List all saved tax calculations (newest first)."""
    rows = list_calculations()
    return [CalculationSummary(**row) for row in rows]


@router.get("/history/{calc_id}", response_model=CalculationDetail)
def history_detail(calc_id: int) -> CalculationDetail:
    """Return a single saved calculation with full input/result data."""
    row = get_calculation(calc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return CalculationDetail(**row)


@router.delete("/history/{calc_id}", response_model=DeleteResponse)
def history_delete(calc_id: int) -> DeleteResponse:
    """Delete a saved calculation by id."""
    deleted = delete_calculation(calc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return DeleteResponse(success=True, message=f"Calculation {calc_id} deleted")

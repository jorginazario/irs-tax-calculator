"""Progressive federal income-tax calculation — IRC §1(j), Rev. Proc. 2023-34."""

from decimal import ROUND_HALF_UP, Decimal

from src.data.tax_year_2024 import FEDERAL_BRACKETS
from src.models.filing_status import FilingStatus
from src.models.tax_output import BracketDetail, BracketTaxResult

TWO_PLACES = Decimal("0.01")


def calculate_bracket_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> BracketTaxResult:
    """Compute federal income tax using 2024 progressive brackets.

    Form 1040 Line 16 (tax from Tax Table / Tax Computation Worksheet).
    """
    if taxable_income < 0:
        msg = "taxable_income must be >= 0"
        raise ValueError(msg)

    brackets = FEDERAL_BRACKETS[filing_status.value]
    breakdown: list[BracketDetail] = []
    total_tax = Decimal("0")
    prev_top = Decimal("0")
    marginal_rate = Decimal("0.10")  # default if income is 0

    for upper_bound, rate in brackets:
        if taxable_income <= prev_top:
            break

        bracket_bottom = prev_top
        if upper_bound is None:
            taxable_in_bracket = taxable_income - prev_top
        else:
            taxable_in_bracket = min(taxable_income, upper_bound) - prev_top

        tax_in_bracket = (taxable_in_bracket * rate).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        breakdown.append(
            BracketDetail(
                rate=rate,
                bracket_bottom=bracket_bottom,
                bracket_top=upper_bound,
                taxable_in_bracket=taxable_in_bracket,
                tax_in_bracket=tax_in_bracket,
            )
        )

        total_tax += tax_in_bracket
        marginal_rate = rate
        prev_top = upper_bound if upper_bound is not None else taxable_income

    effective_rate = (
        (total_tax / taxable_income).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        if taxable_income > 0
        else Decimal("0")
    )

    return BracketTaxResult(
        taxable_income=taxable_income,
        filing_status=filing_status,
        total_tax=total_tax.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        effective_rate=effective_rate,
        marginal_rate=marginal_rate,
        breakdown=breakdown,
    )

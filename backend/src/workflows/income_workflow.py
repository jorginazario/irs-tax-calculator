"""Income aggregation workflow — collect and categorize all income sources.

Sums W-2 wages, 1099-NEC, 1099-INT, 1099-DIV, and 1099-B into a single
IncomeResult with net investment income pre-computed for NIIT.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.models.workflow_models import IncomeResult, TaxReturnInput

TWO_PLACES = Decimal("0.01")


def run_income_workflow(tax_return: TaxReturnInput) -> IncomeResult:
    """Aggregate all income sources from form inputs.

    Form 1040 Lines 1-8: Wages, interest, dividends, capital gains, other income.
    """
    wages = sum((w2.wages for w2 in tax_return.w2s), Decimal("0"))
    se_income = sum(
        (nec.compensation for nec in tax_return.income_1099_nec), Decimal("0")
    )
    interest = sum(
        (form.interest for form in tax_return.income_1099_int), Decimal("0")
    )
    ordinary_divs = sum(
        (form.ordinary_dividends for form in tax_return.income_1099_div), Decimal("0")
    )
    qualified_divs = sum(
        (form.qualified_dividends for form in tax_return.income_1099_div), Decimal("0")
    )
    st_gains = sum(
        (form.short_term_gains for form in tax_return.income_1099_b), Decimal("0")
    )
    lt_gains = sum(
        (form.long_term_gains for form in tax_return.income_1099_b), Decimal("0")
    )

    # Total gross income — Form 1040 Line 9
    total_gross = (
        wages + se_income + interest + ordinary_divs + st_gains + lt_gains
    )

    # Net investment income for NIIT — IRC §1411
    # Interest + ordinary dividends + net capital gains (losses capped at $0 for NII)
    net_gains = max(st_gains + lt_gains, Decimal("0"))
    nii = interest + ordinary_divs + net_gains

    return IncomeResult(
        wages=wages.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        self_employment_income=se_income.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        interest_income=interest.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        ordinary_dividends=ordinary_divs.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        qualified_dividends=qualified_divs.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        short_term_gains=st_gains.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        long_term_gains=lt_gains.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        total_gross_income=total_gross.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        net_investment_income=nii.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

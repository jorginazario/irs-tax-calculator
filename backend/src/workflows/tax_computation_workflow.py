"""Tax computation workflow — federal income tax calculation.

Applies progressive bracket tax on ordinary income, then adds preferential-rate
tax on qualified dividends and long-term capital gains (stacked per IRC §1(h)),
plus NIIT.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import DeductionResult, IncomeResult, TaxComputationResult
from src.tools.calculate_bracket_tax import calculate_bracket_tax
from src.tools.calculate_capital_gains_tax import calculate_capital_gains_tax
from src.tools.calculate_niit import calculate_niit
from src.tools.calculate_qualified_dividend_tax import calculate_qualified_dividend_tax

TWO_PLACES = Decimal("0.01")


def run_tax_computation_workflow(
    income: IncomeResult,
    agi_result: AGIResult,
    deductions: DeductionResult,
    filing_status: FilingStatus,
) -> TaxComputationResult:
    """Compute federal income tax — Form 1040 Line 16.

    Order of computation (IRC §1(h)):
    1. Bracket tax on ordinary taxable income
    2. Qualified dividend tax at 0/15/20%, stacked on ordinary income
    3. Long-term capital gains tax at 0/15/20%, stacked on ordinary + qualified divs
    4. NIIT (3.8% on lesser of NII or MAGI excess) — IRC §1411
    """
    # 1. Bracket tax on ordinary taxable income
    bracket_result = calculate_bracket_tax(
        taxable_income=deductions.ordinary_taxable_income,
        filing_status=filing_status,
    )
    ordinary_tax = bracket_result.total_tax

    # 2. Qualified dividend tax — stacked on ordinary income
    div_result = calculate_qualified_dividend_tax(
        qualified_dividends=deductions.preferential_qualified_dividends,
        ordinary_income=deductions.ordinary_taxable_income,
        filing_status=filing_status,
    )
    qualified_div_tax = div_result.tax

    # 3. Long-term capital gains tax — stacked on ordinary + qualified divs
    # Per IRC §1(h), LTCG stacks above qualified dividends
    stacking_base = deductions.ordinary_taxable_income + deductions.preferential_qualified_dividends
    cg_result = calculate_capital_gains_tax(
        short_term_gains=Decimal("0"),  # ST gains already included in ordinary taxable
        long_term_gains=deductions.preferential_long_term_gains,
        ordinary_income=stacking_base,
        filing_status=filing_status,
    )
    capital_gains_tax = cg_result.long_term_tax

    # 4. NIIT — IRC §1411, Form 8960
    # MAGI ≈ AGI for most taxpayers (no foreign exclusions here)
    niit_result = calculate_niit(
        magi=agi_result.agi,
        net_investment_income=income.net_investment_income,
        filing_status=filing_status,
    )
    niit = niit_result.niit

    total = (ordinary_tax + qualified_div_tax + capital_gains_tax + niit).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )

    return TaxComputationResult(
        ordinary_tax=ordinary_tax,
        qualified_dividend_tax=qualified_div_tax,
        capital_gains_tax=capital_gains_tax,
        niit=niit,
        total_income_tax=total,
    )

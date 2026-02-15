"""Summary workflow — assemble final tax result.

Combines all upstream workflow outputs into a single TaxSummary with
effective/marginal rates, withholding, and refund/owed calculation.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.models.tax_output import AGIResult, FicaResult
from src.models.workflow_models import (
    CreditsResult,
    DeductionResult,
    IncomeResult,
    TaxComputationResult,
    TaxReturnInput,
    TaxSummary,
)
from src.tools.calculate_bracket_tax import calculate_bracket_tax

TWO_PLACES = Decimal("0.01")


def run_summary_workflow(
    tax_return: TaxReturnInput,
    income: IncomeResult,
    agi_result: AGIResult,
    deductions: DeductionResult,
    tax_computation: TaxComputationResult,
    credits: CreditsResult,
    fica: FicaResult,
) -> TaxSummary:
    """Assemble the final tax summary — Form 1040 bottom line.

    Total tax = income tax after credits + FICA
    Refund/owed = income tax after credits - total payments
    (FICA is a separate obligation and is not offset by income tax payments.)
    """
    # Auto-sum W-2 withholding from all W-2s
    total_withholding = sum(
        (w2.federal_withholding for w2 in tax_return.w2s), Decimal("0")
    )

    total_payments = total_withholding + tax_return.estimated_payments

    # Total tax = income tax after credits + FICA
    income_tax_after_credits = credits.tax_after_credits
    total_tax = income_tax_after_credits + fica.total_fica

    # Refund/owed: negative = refund, positive = owed
    # Only income tax is offset by withholding/estimated payments
    refund_or_owed = income_tax_after_credits - total_payments

    # Effective rate = total tax / total income (0 if no income)
    effective_rate = (
        (total_tax / income.total_gross_income).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
        if income.total_gross_income > Decimal("0")
        else Decimal("0")
    )

    # Marginal rate — use the bracket tax tool to determine the bracket
    # Use total taxable income to find the marginal bracket
    bracket_result = calculate_bracket_tax(
        taxable_income=deductions.taxable_income,
        filing_status=tax_return.filing_status,
    )
    marginal_rate = bracket_result.marginal_rate

    return TaxSummary(
        filing_status=tax_return.filing_status,
        total_income=income.total_gross_income.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        agi=agi_result.agi.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        deduction_amount=deductions.deduction_amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        taxable_income=deductions.taxable_income.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        ordinary_tax=tax_computation.ordinary_tax.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        qualified_dividend_tax=tax_computation.qualified_dividend_tax.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        capital_gains_tax=tax_computation.capital_gains_tax.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        niit=tax_computation.niit.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        total_income_tax_before_credits=tax_computation.total_income_tax.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        total_credits=credits.total_credits_applied.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        income_tax_after_credits=income_tax_after_credits.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        total_fica=fica.total_fica.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        total_tax=total_tax.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        effective_rate=effective_rate,
        marginal_rate=marginal_rate,
        total_withholding=total_withholding.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        estimated_payments=tax_return.estimated_payments.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        total_payments=total_payments.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        refund_or_owed=refund_or_owed.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

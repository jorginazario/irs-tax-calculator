"""Calculate Adjusted Gross Income (AGI) — Form 1040 Line 11."""

from decimal import ROUND_HALF_UP, Decimal

from src.models.tax_input import AboveLineDeductions, GrossIncome
from src.models.tax_output import AGIResult

TWO_PLACES = Decimal("0.01")


def calculate_agi(
    gross_income: GrossIncome,
    above_line_deductions: AboveLineDeductions | None = None,
) -> AGIResult:
    """Sum all income sources, subtract above-the-line deductions, floor at 0.

    Form 1040: Line 9 (total income) minus Schedule 1 Part II → Line 11 (AGI).
    """
    if above_line_deductions is None:
        above_line_deductions = AboveLineDeductions()

    total_income = sum(
        [
            gross_income.w2_wages,
            gross_income.nec_1099,
            gross_income.interest_income,
            gross_income.ordinary_dividends,
            gross_income.short_term_gains,
            gross_income.long_term_gains,
        ],
        Decimal("0"),
    )

    total_deductions = sum(
        [
            above_line_deductions.educator_expenses,
            above_line_deductions.student_loan_interest,
            above_line_deductions.hsa_deduction,
            above_line_deductions.ira_deduction,
            above_line_deductions.se_tax_deduction,
            above_line_deductions.self_employed_health_insurance,
            above_line_deductions.penalty_early_withdrawal,
            above_line_deductions.alimony_paid,
        ],
        Decimal("0"),
    )

    agi = max(total_income - total_deductions, Decimal("0"))

    return AGIResult(
        total_gross_income=total_income.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        total_above_line_deductions=total_deductions.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        agi=agi.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

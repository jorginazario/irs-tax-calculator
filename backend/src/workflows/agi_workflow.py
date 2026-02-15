"""AGI workflow — compute Adjusted Gross Income with SE deduction injected.

Builds GrossIncome from IncomeResult, merges the SE tax deduction from FICA
into above-the-line deductions, and delegates to the calculate_agi tool.
"""

from src.models.tax_input import AboveLineDeductions, GrossIncome
from src.models.tax_output import AGIResult, FicaResult
from src.models.workflow_models import IncomeResult, TaxReturnInput
from src.tools.calculate_agi import calculate_agi


def run_agi_workflow(
    tax_return: TaxReturnInput,
    income: IncomeResult,
    fica: FicaResult,
) -> AGIResult:
    """Compute AGI — Form 1040 Line 11.

    The SE tax deduction (50% of self-employment tax) is an above-the-line
    deduction that must be computed before AGI. This workflow auto-injects it.
    """
    gross_income = GrossIncome(
        w2_wages=income.wages,
        nec_1099=income.self_employment_income,
        interest_income=income.interest_income,
        ordinary_dividends=income.ordinary_dividends,
        qualified_dividends=income.qualified_dividends,
        short_term_gains=income.short_term_gains,
        long_term_gains=income.long_term_gains,
    )

    above_line = AboveLineDeductions(
        se_tax_deduction=fica.se_tax_deduction,
        hsa_deduction=tax_return.hsa_deduction,
        student_loan_interest=tax_return.student_loan_interest,
        educator_expenses=tax_return.educator_expenses,
        ira_deduction=tax_return.ira_deduction,
        self_employed_health_insurance=tax_return.self_employed_health_insurance,
    )

    return calculate_agi(gross_income, above_line)

"""Orchestrator — chain all workflows into a single tax calculation.

This is the single entry point that the API (Phase 3) will call.
"""

import logging

from src.models.workflow_models import FullTaxCalculationResult, TaxReturnInput
from src.workflows.agi_workflow import run_agi_workflow
from src.workflows.credits_workflow import run_credits_workflow
from src.workflows.deduction_workflow import run_deduction_workflow
from src.workflows.fica_workflow import run_fica_workflow
from src.workflows.income_workflow import run_income_workflow
from src.workflows.summary_workflow import run_summary_workflow
from src.workflows.tax_computation_workflow import run_tax_computation_workflow

logger = logging.getLogger(__name__)


def calculate_full_tax(tax_return: TaxReturnInput) -> FullTaxCalculationResult:
    """Run the full tax-calculation pipeline.

    Pipeline order:
    1. Income  → aggregate all income sources
    2. FICA    → compute FICA/SE tax (needed for SE deduction before AGI)
    3. AGI     → sum income, subtract above-the-line deductions
    4. Deduction → standard vs. itemized, partition ordinary vs. preferential
    5. Tax Computation → bracket + preferential + NIIT
    6. Credits → apply CTC and other credits
    7. Summary → final liability, rates, refund/owed
    """
    filing_status = tax_return.filing_status

    # 1. Income aggregation
    income = run_income_workflow(tax_return)

    # 2. FICA (must run before AGI — SE deduction is above-the-line)
    fica = run_fica_workflow(income, filing_status)

    # 3. AGI
    agi = run_agi_workflow(tax_return, income, fica)

    # 4. Deduction
    deductions = run_deduction_workflow(tax_return, income, agi)

    # 5. Tax Computation
    tax_computation = run_tax_computation_workflow(
        income, agi, deductions, filing_status
    )

    # 6. Credits
    credits = run_credits_workflow(tax_return, agi, tax_computation)

    # 7. Summary
    summary = run_summary_workflow(
        tax_return, income, agi, deductions, tax_computation, credits, fica
    )

    result = FullTaxCalculationResult(
        income=income,
        fica=fica,
        agi=agi,
        deductions=deductions,
        tax_computation=tax_computation,
        credits=credits,
        summary=summary,
    )

    # Auto-persist to SQLite
    try:
        from src.database.repository import save_calculation

        save_calculation(tax_return, result)
    except Exception:
        logger.warning("Failed to auto-save calculation to database", exc_info=True)

    return result

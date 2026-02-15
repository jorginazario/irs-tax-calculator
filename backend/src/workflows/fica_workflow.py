"""FICA workflow — delegate to the calculate_fica tool.

Thin wrapper that extracts W-2 wages and SE income from IncomeResult
and passes them to the FICA tool.
"""

from src.models.filing_status import FilingStatus
from src.models.tax_output import FicaResult
from src.models.workflow_models import IncomeResult
from src.tools.calculate_fica import calculate_fica


def run_fica_workflow(
    income: IncomeResult,
    filing_status: FilingStatus,
) -> FicaResult:
    """Compute FICA taxes — Schedule SE, Form 1040 Lines 4 and 14."""
    return calculate_fica(
        w2_wages=income.wages,
        self_employment_income=income.self_employment_income,
        filing_status=filing_status,
    )

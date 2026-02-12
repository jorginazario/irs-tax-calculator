"""Look up the standard deduction — IRS Pub 501, Rev. Proc. 2023-34 §3."""

from src.data.tax_year_2024 import (
    ADDITIONAL_DEDUCTION_MARRIED,
    ADDITIONAL_DEDUCTION_SINGLE_HOH,
    STANDARD_DEDUCTION,
)
from src.models.filing_status import FilingStatus
from src.models.tax_output import StandardDeductionResult

# Statuses that use the "single/HoH" additional deduction amount
_SINGLE_HOH = {FilingStatus.SINGLE, FilingStatus.HEAD_OF_HOUSEHOLD}


def lookup_standard_deduction(
    filing_status: FilingStatus,
    is_blind: bool = False,
    is_over_65: bool = False,
) -> StandardDeductionResult:
    """Return standard deduction including additional amounts for age/blindness.

    Additional deduction (per qualifying condition):
      - Single / HoH: $1,950
      - MFJ / MFS / QSS: $1,550
    """
    base = STANDARD_DEDUCTION[filing_status.value]

    per_condition = (
        ADDITIONAL_DEDUCTION_SINGLE_HOH
        if filing_status in _SINGLE_HOH
        else ADDITIONAL_DEDUCTION_MARRIED
    )

    qualifying_conditions = int(is_blind) + int(is_over_65)
    additional = per_condition * qualifying_conditions

    return StandardDeductionResult(
        filing_status=filing_status,
        base_amount=base,
        additional_amount=additional,
        total_deduction=base + additional,
    )

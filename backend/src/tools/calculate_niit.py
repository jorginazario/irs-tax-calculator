"""Net Investment Income Tax (NIIT) calculation — IRC §1411.

3.8% tax on the lesser of:
  (a) net investment income, or
  (b) MAGI exceeding the filing-status threshold.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.data.tax_year_2024 import NIIT_RATE, NIIT_THRESHOLDS
from src.models.filing_status import FilingStatus
from src.models.tax_output import NiitResult

TWO_PLACES = Decimal("0.01")


def calculate_niit(
    magi: Decimal,
    net_investment_income: Decimal,
    filing_status: FilingStatus,
) -> NiitResult:
    """Compute the 3.8% Net Investment Income Tax.

    Form 8960, Line 17.
    """
    if magi < 0:
        msg = "magi must be >= 0"
        raise ValueError(msg)
    if net_investment_income < 0:
        msg = "net_investment_income must be >= 0"
        raise ValueError(msg)

    threshold = NIIT_THRESHOLDS[filing_status.value]
    excess_magi = max(magi - threshold, Decimal("0"))

    taxable_base = min(net_investment_income, excess_magi)
    niit = (taxable_base * NIIT_RATE).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return NiitResult(
        magi=magi,
        threshold=threshold,
        excess_magi=excess_magi,
        net_investment_income=net_investment_income,
        niit=niit,
    )

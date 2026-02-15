"""Capital gains tax calculation — IRC §1(h), Schedule D, Form 8949.

Short-term gains are taxed as ordinary income (handled by bracket tax tool).
Long-term gains use preferential 0%/15%/20% rates, stacked on ordinary income.
"""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import CapitalGainsTaxResult
from src.tools.preferential_rate import calculate_preferential_rate_tax


def calculate_capital_gains_tax(
    short_term_gains: Decimal,
    long_term_gains: Decimal,
    ordinary_income: Decimal,
    filing_status: FilingStatus,
) -> CapitalGainsTaxResult:
    """Compute tax on capital gains.

    - Short-term: taxed at ordinary rates (returned as-is for bracket tax to handle).
    - Long-term: taxed at preferential 0%/15%/20% rates stacked on ordinary income.

    Schedule D Tax Worksheet, Lines 18-22.
    """
    if ordinary_income < 0:
        msg = "ordinary_income must be >= 0"
        raise ValueError(msg)

    long_term_tax, breakdown = calculate_preferential_rate_tax(
        amount=long_term_gains,
        ordinary_income=ordinary_income,
        filing_status=filing_status,
    )

    return CapitalGainsTaxResult(
        short_term_gains=short_term_gains,
        long_term_gains=long_term_gains,
        long_term_tax=long_term_tax,
        breakdown=breakdown,
    )

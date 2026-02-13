"""Qualified dividend tax calculation — IRC §1(h).

Qualified dividends receive the same preferential 0%/15%/20% rates as
long-term capital gains, stacked on top of ordinary income.
"""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import QualifiedDividendTaxResult
from src.tools.preferential_rate import calculate_preferential_rate_tax


def calculate_qualified_dividend_tax(
    qualified_dividends: Decimal,
    ordinary_income: Decimal,
    filing_status: FilingStatus,
) -> QualifiedDividendTaxResult:
    """Compute tax on qualified dividends at preferential rates.

    Qualified Dividends and Capital Gain Tax Worksheet — Form 1040, Line 16.
    """
    if qualified_dividends < 0:
        msg = "qualified_dividends must be >= 0"
        raise ValueError(msg)
    if ordinary_income < 0:
        msg = "ordinary_income must be >= 0"
        raise ValueError(msg)

    tax, breakdown = calculate_preferential_rate_tax(
        amount=qualified_dividends,
        ordinary_income=ordinary_income,
        filing_status=filing_status,
    )

    return QualifiedDividendTaxResult(
        qualified_dividends=qualified_dividends,
        tax=tax,
        breakdown=breakdown,
    )

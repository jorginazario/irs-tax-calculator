"""Shared helper for 0%/15%/20% preferential-rate tax calculation.

Used by both long-term capital gains and qualified dividends — IRC §1(h).
The preferential income is "stacked" on top of ordinary income to determine
which rate brackets it falls into.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.data.tax_year_2024 import CAPITAL_GAINS_THRESHOLDS
from src.models.filing_status import FilingStatus
from src.models.tax_output import PreferentialRateDetail

TWO_PLACES = Decimal("0.01")


def calculate_preferential_rate_tax(
    amount: Decimal,
    ordinary_income: Decimal,
    filing_status: FilingStatus,
) -> tuple[Decimal, list[PreferentialRateDetail]]:
    """Apply 0%/15%/20% rates to *amount*, stacked on top of *ordinary_income*.

    Returns (total_tax, breakdown).  If amount <= 0, returns ($0, []).
    """
    if amount <= 0:
        return Decimal("0.00"), []

    thresholds = CAPITAL_GAINS_THRESHOLDS[filing_status.value]
    breakdown: list[PreferentialRateDetail] = []
    total_tax = Decimal("0")

    # "stacking" means ordinary income has already filled the lower brackets.
    # The preferential income starts where ordinary income left off.
    remaining = amount
    income_so_far = ordinary_income  # cursor tracking how much total income has been placed

    for upper_bound, rate in thresholds:
        if remaining <= 0:
            break

        # Room left in this bracket above income already placed
        room = remaining if upper_bound is None else max(upper_bound - income_so_far, Decimal("0"))

        if room <= 0:
            # Ordinary income already exceeds this bracket — skip
            income_so_far = max(income_so_far, upper_bound if upper_bound else income_so_far)
            continue

        taxable_in_bracket = min(remaining, room)
        tax_in_bracket = (taxable_in_bracket * rate).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        breakdown.append(
            PreferentialRateDetail(
                rate=rate,
                bracket_bottom=income_so_far,
                bracket_top=upper_bound,
                taxable_in_bracket=taxable_in_bracket,
                tax_in_bracket=tax_in_bracket,
            )
        )

        total_tax += tax_in_bracket
        remaining -= taxable_in_bracket
        income_so_far += taxable_in_bracket

    return total_tax.quantize(TWO_PLACES, rounding=ROUND_HALF_UP), breakdown

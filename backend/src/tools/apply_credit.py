"""Apply a tax credit — refundable or non-refundable.

Non-refundable credits cannot reduce tax below $0.
Refundable credits can result in a negative tax (refund).
"""

from decimal import ROUND_HALF_UP, Decimal

from src.models.tax_output import CreditResult

TWO_PLACES = Decimal("0.01")


def apply_credit(
    tax_owed: Decimal,
    credit_amount: Decimal,
    is_refundable: bool = False,
) -> CreditResult:
    """Apply a single tax credit to the tax liability.

    Form 1040, Lines 19-24 (non-refundable) and Lines 27-32 (refundable).
    """
    if credit_amount < 0:
        msg = "credit_amount must be >= 0"
        raise ValueError(msg)

    tax_after = tax_owed - credit_amount

    if not is_refundable:
        tax_after = max(tax_after, Decimal("0"))

    credit_applied = (tax_owed - tax_after).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return CreditResult(
        tax_before=tax_owed.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        credit_applied=credit_applied,
        tax_after=tax_after.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

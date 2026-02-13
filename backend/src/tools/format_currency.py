"""Format a Decimal value as a US-dollar currency string."""

from decimal import ROUND_HALF_UP, Decimal

TWO_PLACES = Decimal("0.01")


def format_currency(amount: Decimal) -> str:
    """Format *amount* as "$1,234.56".  Negatives use "-$1,234.56".

    Pure formatting — no Pydantic model needed.
    """
    rounded = amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    # Normalize negative zero → positive zero
    if rounded == 0:
        rounded = Decimal("0.00")
    if rounded < 0:
        return f"-${abs(rounded):,.2f}"
    return f"${rounded:,.2f}"

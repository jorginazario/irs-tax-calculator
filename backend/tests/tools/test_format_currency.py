"""Tests for format_currency tool."""

from decimal import Decimal

from src.tools.format_currency import format_currency


class TestFormatCurrency:
    """Formatting Decimal values as US dollar strings."""

    def test_positive_whole(self):
        assert format_currency(Decimal("1234")) == "$1,234.00"

    def test_positive_with_cents(self):
        assert format_currency(Decimal("1234.56")) == "$1,234.56"

    def test_negative(self):
        assert format_currency(Decimal("-1234.56")) == "-$1,234.56"

    def test_zero(self):
        assert format_currency(Decimal("0")) == "$0.00"

    def test_large_number(self):
        assert format_currency(Decimal("1234567.89")) == "$1,234,567.89"

    def test_small_cents(self):
        assert format_currency(Decimal("0.99")) == "$0.99"

    def test_rounding_up(self):
        """$1.005 rounds to $1.01 (ROUND_HALF_UP)."""
        assert format_currency(Decimal("1.005")) == "$1.01"

    def test_rounding_down(self):
        """$1.004 rounds to $1.00."""
        assert format_currency(Decimal("1.004")) == "$1.00"

    def test_negative_zero(self):
        """Negative zero should display as $0.00."""
        assert format_currency(Decimal("-0.001")) == "$0.00"

    def test_one_cent(self):
        assert format_currency(Decimal("0.01")) == "$0.01"

    def test_negative_small(self):
        assert format_currency(Decimal("-0.50")) == "-$0.50"

"""Tests for apply_credit tool.

Covers refundable and non-refundable credit scenarios.
"""

from decimal import Decimal

import pytest

from src.tools.apply_credit import apply_credit


class TestNonRefundableCredit:
    """Non-refundable credits cannot reduce tax below $0."""

    def test_basic_reduction(self):
        """$5,000 tax, $2,000 credit → $3,000 after."""
        result = apply_credit(Decimal("5000"), Decimal("2000"), is_refundable=False)
        assert result.tax_before == Decimal("5000.00")
        assert result.credit_applied == Decimal("2000.00")
        assert result.tax_after == Decimal("3000.00")

    def test_credit_exceeds_tax(self):
        """$1,000 tax, $3,000 non-refundable credit → floored at $0."""
        result = apply_credit(Decimal("1000"), Decimal("3000"), is_refundable=False)
        assert result.tax_after == Decimal("0.00")
        assert result.credit_applied == Decimal("1000.00")  # only $1k actually applied

    def test_credit_equals_tax(self):
        """$2,000 tax, $2,000 credit → $0."""
        result = apply_credit(Decimal("2000"), Decimal("2000"), is_refundable=False)
        assert result.tax_after == Decimal("0.00")
        assert result.credit_applied == Decimal("2000.00")

    def test_zero_credit(self):
        """$5,000 tax, $0 credit → unchanged."""
        result = apply_credit(Decimal("5000"), Decimal("0"), is_refundable=False)
        assert result.tax_after == Decimal("5000.00")
        assert result.credit_applied == Decimal("0.00")

    def test_zero_tax(self):
        """$0 tax, $1,000 non-refundable credit → $0."""
        result = apply_credit(Decimal("0"), Decimal("1000"), is_refundable=False)
        assert result.tax_after == Decimal("0.00")
        assert result.credit_applied == Decimal("0.00")


class TestRefundableCredit:
    """Refundable credits can push tax below $0 (refund)."""

    def test_basic_refundable(self):
        """$5,000 tax, $2,000 refundable credit → $3,000."""
        result = apply_credit(Decimal("5000"), Decimal("2000"), is_refundable=True)
        assert result.tax_after == Decimal("3000.00")
        assert result.credit_applied == Decimal("2000.00")

    def test_refundable_below_zero(self):
        """$1,000 tax, $3,000 refundable credit → -$2,000 (refund)."""
        result = apply_credit(Decimal("1000"), Decimal("3000"), is_refundable=True)
        assert result.tax_after == Decimal("-2000.00")
        assert result.credit_applied == Decimal("3000.00")

    def test_zero_tax_refundable(self):
        """$0 tax, $1,500 refundable credit → -$1,500."""
        result = apply_credit(Decimal("0"), Decimal("1500"), is_refundable=True)
        assert result.tax_after == Decimal("-1500.00")
        assert result.credit_applied == Decimal("1500.00")


class TestApplyCreditErrors:
    """Error handling."""

    def test_negative_credit_raises(self):
        with pytest.raises(ValueError, match="credit_amount must be >= 0"):
            apply_credit(Decimal("5000"), Decimal("-100"), is_refundable=False)

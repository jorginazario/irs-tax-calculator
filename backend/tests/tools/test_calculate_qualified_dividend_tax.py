"""Tests for calculate_qualified_dividend_tax tool.

Qualified dividends use the same 0%/15%/20% rate table as long-term capital gains.
Expected values hand-calculated from 2024 thresholds (Rev. Proc. 2023-34).
"""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.tools.calculate_qualified_dividend_tax import calculate_qualified_dividend_tax


class TestSingleQualifiedDividends:
    """SINGLE filing status — qualified dividend tax."""

    def test_zero_dividends(self):
        result = calculate_qualified_dividend_tax(
            Decimal("0"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.tax == Decimal("0.00")
        assert result.breakdown == []

    def test_all_in_zero_bracket(self):
        """$5,000 qualified divs on $30,000 ordinary → all at 0% (cap $47,025)."""
        result = calculate_qualified_dividend_tax(
            Decimal("5000"), Decimal("30000"), FilingStatus.SINGLE
        )
        assert result.tax == Decimal("0.00")
        assert len(result.breakdown) == 1
        assert result.breakdown[0].rate == Decimal("0.00")

    def test_spans_zero_and_fifteen(self):
        """$20,000 qualified divs on $40,000 ordinary (SINGLE, 0% cap $47,025).
        $7,025 at 0% → $0.00
        $12,975 at 15% → $1,946.25
        Total: $1,946.25
        """
        result = calculate_qualified_dividend_tax(
            Decimal("20000"), Decimal("40000"), FilingStatus.SINGLE
        )
        assert result.tax == Decimal("1946.25")

    def test_entirely_in_fifteen(self):
        """$10,000 qualified divs on $100,000 ordinary → all at 15%."""
        result = calculate_qualified_dividend_tax(
            Decimal("10000"), Decimal("100000"), FilingStatus.SINGLE
        )
        assert result.tax == Decimal("1500.00")

    def test_into_twenty(self):
        """$50,000 qualified divs on $510,000 ordinary (SINGLE, 15% cap $518,900).
        $8,900 at 15% → $1,335.00
        $41,100 at 20% → $8,220.00
        Total: $9,555.00
        """
        result = calculate_qualified_dividend_tax(
            Decimal("50000"), Decimal("510000"), FilingStatus.SINGLE
        )
        assert result.tax == Decimal("9555.00")


class TestMFJQualifiedDividends:
    """MARRIED_FILING_JOINTLY — qualified dividend tax."""

    def test_all_zero_bracket_mfj(self):
        """$20,000 on $60,000 ordinary → all at 0% (MFJ cap $94,050)."""
        result = calculate_qualified_dividend_tax(
            Decimal("20000"), Decimal("60000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.tax == Decimal("0.00")

    def test_spans_zero_and_fifteen_mfj(self):
        """$30,000 on $80,000 ordinary (MFJ, 0% cap $94,050).
        $14,050 at 0% → $0
        $15,950 at 15% → $2,392.50
        Total: $2,392.50
        """
        result = calculate_qualified_dividend_tax(
            Decimal("30000"), Decimal("80000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.tax == Decimal("2392.50")


class TestQualifiedDividendErrors:
    """Error handling."""

    def test_negative_dividends_raises(self):
        with pytest.raises(ValueError, match="qualified_dividends must be >= 0"):
            calculate_qualified_dividend_tax(
                Decimal("-1"), Decimal("50000"), FilingStatus.SINGLE
            )

    def test_negative_ordinary_income_raises(self):
        with pytest.raises(ValueError, match="ordinary_income must be >= 0"):
            calculate_qualified_dividend_tax(
                Decimal("5000"), Decimal("-1"), FilingStatus.SINGLE
            )

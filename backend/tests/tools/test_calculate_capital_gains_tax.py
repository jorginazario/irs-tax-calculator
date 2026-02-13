"""Tests for calculate_capital_gains_tax tool.

Expected values hand-calculated from 2024 capital gains rate thresholds (Rev. Proc. 2023-34).
Long-term gains are stacked on top of ordinary income to determine the applicable rate.
"""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.tools.calculate_capital_gains_tax import calculate_capital_gains_tax


class TestSingleCapitalGains:
    """SINGLE filing status — capital gains tax."""

    def test_zero_gains(self):
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("0"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("0.00")
        assert result.breakdown == []

    def test_long_term_in_zero_bracket(self):
        """$10,000 LTCG on $30,000 ordinary income → entirely in 0% bracket (cap: $47,025)."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("10000"), Decimal("30000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("0.00")
        assert len(result.breakdown) == 1
        assert result.breakdown[0].rate == Decimal("0.00")

    def test_long_term_spans_zero_and_fifteen(self):
        """$30,000 LTCG on $40,000 ordinary income (SINGLE, 0% cap $47,025).
        $7,025 at 0% → $0.00
        $22,975 at 15% → $3,446.25
        Total: $3,446.25
        """
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("30000"), Decimal("40000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("3446.25")
        assert len(result.breakdown) == 2
        assert result.breakdown[0].rate == Decimal("0.00")
        assert result.breakdown[0].taxable_in_bracket == Decimal("7025")
        assert result.breakdown[1].rate == Decimal("0.15")
        assert result.breakdown[1].taxable_in_bracket == Decimal("22975")

    def test_long_term_entirely_in_fifteen(self):
        """$50,000 LTCG on $100,000 ordinary income → all in 15% bracket.
        Ordinary fills 0% bracket. All $50,000 at 15% → $7,500.
        """
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("50000"), Decimal("100000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("7500.00")

    def test_long_term_into_twenty(self):
        """$100,000 LTCG on $500,000 ordinary income (SINGLE, 15% cap $518,900).
        $18,900 at 15% → $2,835.00
        $81,100 at 20% → $16,220.00
        Total: $19,055.00
        """
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("100000"), Decimal("500000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("19055.00")

    def test_long_term_all_twenty(self):
        """$50,000 LTCG on $600,000 ordinary income → entirely in 20% bracket."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("50000"), Decimal("600000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("10000.00")
        assert len(result.breakdown) == 1
        assert result.breakdown[0].rate == Decimal("0.20")

    def test_short_term_passed_through(self):
        """Short-term gains are included in result but not taxed here."""
        result = calculate_capital_gains_tax(
            Decimal("5000"), Decimal("10000"), Decimal("30000"), FilingStatus.SINGLE
        )
        assert result.short_term_gains == Decimal("5000")
        # Short-term does not affect long_term_tax
        assert result.long_term_tax == Decimal("0.00")

    def test_negative_long_term_gains(self):
        """Negative LTCG (loss) → $0 tax, empty breakdown."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("-3000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.long_term_tax == Decimal("0.00")
        assert result.breakdown == []


class TestMFJCapitalGains:
    """MARRIED_FILING_JOINTLY — capital gains tax."""

    def test_zero_bracket_mfj(self):
        """$20,000 LTCG on $60,000 ordinary → all in 0% (cap $94,050)."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("20000"), Decimal("60000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.long_term_tax == Decimal("0.00")

    def test_spans_zero_and_fifteen_mfj(self):
        """$50,000 LTCG on $80,000 ordinary (MFJ, 0% cap $94,050).
        $14,050 at 0% → $0
        $35,950 at 15% → $5,392.50
        Total: $5,392.50
        """
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("50000"), Decimal("80000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.long_term_tax == Decimal("5392.50")


class TestHOHCapitalGains:
    """HEAD_OF_HOUSEHOLD — capital gains tax."""

    def test_zero_bracket_hoh(self):
        """$20,000 LTCG on $40,000 ordinary → all in 0% (cap $63,000)."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("20000"), Decimal("40000"),
            FilingStatus.HEAD_OF_HOUSEHOLD,
        )
        assert result.long_term_tax == Decimal("0.00")


class TestMFSCapitalGains:
    """MARRIED_FILING_SEPARATELY — capital gains tax."""

    def test_fifteen_bracket_mfs(self):
        """$20,000 LTCG on $50,000 ordinary (MFS, 0% cap $47,025) → all at 15%."""
        result = calculate_capital_gains_tax(
            Decimal("0"), Decimal("20000"), Decimal("50000"),
            FilingStatus.MARRIED_FILING_SEPARATELY,
        )
        assert result.long_term_tax == Decimal("3000.00")


class TestCapitalGainsErrors:
    """Error handling."""

    def test_negative_ordinary_income_raises(self):
        with pytest.raises(ValueError, match="ordinary_income must be >= 0"):
            calculate_capital_gains_tax(
                Decimal("0"), Decimal("10000"), Decimal("-1"), FilingStatus.SINGLE
            )

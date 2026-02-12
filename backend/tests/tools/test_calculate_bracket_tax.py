"""Tests for calculate_bracket_tax tool.

All expected values hand-calculated from 2024 brackets (Rev. Proc. 2023-34).
"""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.tools.calculate_bracket_tax import calculate_bracket_tax


class TestSingleBracketTax:
    """SINGLE filing status — progressive bracket-tax calculations."""

    def test_zero_income(self):
        result = calculate_bracket_tax(Decimal("0"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("0.00")
        assert result.effective_rate == Decimal("0")
        assert result.breakdown == []

    def test_10k(self):
        """$10,000 — entirely in 10% bracket."""
        result = calculate_bracket_tax(Decimal("10000"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("1000.00")
        assert result.marginal_rate == Decimal("0.10")

    def test_30k(self):
        """$30,000 — spans 10% + 12% brackets.
        11600 * 0.10 = 1160 + 18400 * 0.12 = 2208 → $3,368
        """
        result = calculate_bracket_tax(Decimal("30000"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("3368.00")
        assert result.marginal_rate == Decimal("0.12")

    def test_50k(self):
        """$50,000 — spans 10% + 12% + 22% brackets.
        1160 + 4266 + 627 = $6,053
        """
        result = calculate_bracket_tax(Decimal("50000"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("6053.00")
        assert result.marginal_rate == Decimal("0.22")

    def test_100k(self):
        """$100,000 — 10% + 12% + 22% (just under $100,525 boundary).
        1160 + 4266 + 11627 = $17,053
        """
        result = calculate_bracket_tax(Decimal("100000"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("17053.00")
        assert result.marginal_rate == Decimal("0.22")

    def test_700k(self):
        """$700,000 — spans all 7 brackets.
        1160 + 4266 + 11742.50 + 21942 + 16568 + 127968.75 + 33540.50 = $217,187.75
        """
        result = calculate_bracket_tax(Decimal("700000"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("217187.75")
        assert result.marginal_rate == Decimal("0.37")

    def test_bracket_boundary_exact(self):
        """$11,600 — exactly fills the 10% bracket."""
        result = calculate_bracket_tax(Decimal("11600"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("1160.00")
        assert result.marginal_rate == Decimal("0.10")
        assert len(result.breakdown) == 1

    def test_bracket_boundary_one_over(self):
        """$11,601 — $1 spills into 12% bracket."""
        result = calculate_bracket_tax(Decimal("11601"), FilingStatus.SINGLE)
        assert result.total_tax == Decimal("1160.12")
        assert result.marginal_rate == Decimal("0.12")
        assert len(result.breakdown) == 2

    def test_effective_rate_100k(self):
        result = calculate_bracket_tax(Decimal("100000"), FilingStatus.SINGLE)
        # 17053 / 100000 = 0.170530
        assert result.effective_rate == Decimal("0.170530")

    def test_breakdown_structure(self):
        """Verify breakdown contains correct per-bracket detail."""
        result = calculate_bracket_tax(Decimal("30000"), FilingStatus.SINGLE)
        assert len(result.breakdown) == 2
        b0 = result.breakdown[0]
        assert b0.rate == Decimal("0.10")
        assert b0.bracket_bottom == Decimal("0")
        assert b0.bracket_top == Decimal("11600")
        assert b0.taxable_in_bracket == Decimal("11600")
        assert b0.tax_in_bracket == Decimal("1160.00")


class TestMFJBracketTax:
    """MARRIED_FILING_JOINTLY filing status."""

    def test_50k(self):
        """23200 * 0.10 = 2320 + 26800 * 0.12 = 3216 → $5,536"""
        result = calculate_bracket_tax(
            Decimal("50000"), FilingStatus.MARRIED_FILING_JOINTLY
        )
        assert result.total_tax == Decimal("5536.00")
        assert result.marginal_rate == Decimal("0.12")

    def test_200k(self):
        """2320 + 8532 + 23254 = $34,106"""
        result = calculate_bracket_tax(
            Decimal("200000"), FilingStatus.MARRIED_FILING_JOINTLY
        )
        assert result.total_tax == Decimal("34106.00")
        assert result.marginal_rate == Decimal("0.22")


class TestHOHBracketTax:
    """HEAD_OF_HOUSEHOLD filing status."""

    def test_75k(self):
        """16550 * 0.10 = 1655 + 46550 * 0.12 = 5586 + 11900 * 0.22 = 2618 → $9,859"""
        result = calculate_bracket_tax(
            Decimal("75000"), FilingStatus.HEAD_OF_HOUSEHOLD
        )
        assert result.total_tax == Decimal("9859.00")
        assert result.marginal_rate == Decimal("0.22")


class TestMFSBracketTax:
    """MARRIED_FILING_SEPARATELY filing status."""

    def test_200k(self):
        """1160 + 4266 + 11742.50 + 21942 + 2576 = $41,686.50"""
        result = calculate_bracket_tax(
            Decimal("200000"), FilingStatus.MARRIED_FILING_SEPARATELY
        )
        assert result.total_tax == Decimal("41686.50")
        assert result.marginal_rate == Decimal("0.32")


class TestBracketTaxErrors:
    """Error handling."""

    def test_negative_income_raises(self):
        with pytest.raises(ValueError, match="taxable_income must be >= 0"):
            calculate_bracket_tax(Decimal("-1"), FilingStatus.SINGLE)

    def test_filing_status_preserved(self):
        result = calculate_bracket_tax(Decimal("50000"), FilingStatus.HEAD_OF_HOUSEHOLD)
        assert result.filing_status == FilingStatus.HEAD_OF_HOUSEHOLD

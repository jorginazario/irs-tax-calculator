"""Tests for calculate_fica tool.

Hand-calculated from 2024 FICA constants:
  SS rate: 6.2% employee (capped at $168,600 wage base)
  Medicare: 1.45% (no cap)
  Additional Medicare: 0.9% over $200k SINGLE / $250k MFJ
  SE: 92.35% taxable base; 12.4% SS + 2.9% Medicare; 50% deductible
"""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.tools.calculate_fica import calculate_fica


class TestW2Only:
    """W-2 employee wages only (no self-employment)."""

    def test_basic_wages(self):
        """$50,000 W-2 wages (SINGLE).
        SS: $50,000 × 0.062 = $3,100.00
        Medicare: $50,000 × 0.0145 = $725.00
        Additional Medicare: $0 (below $200k)
        Total: $3,825.00
        """
        result = calculate_fica(Decimal("50000"), Decimal("0"), FilingStatus.SINGLE)
        assert result.ss_tax == Decimal("3100.00")
        assert result.medicare_tax == Decimal("725.00")
        assert result.additional_medicare_tax == Decimal("0.00")
        assert result.se_tax == Decimal("0")
        assert result.se_tax_deduction == Decimal("0")
        assert result.total_fica == Decimal("3825.00")

    def test_wages_above_ss_cap(self):
        """$200,000 W-2 wages — SS capped at $168,600 wage base.
        SS: $168,600 × 0.062 = $10,453.20
        Medicare: $200,000 × 0.0145 = $2,900.00
        Additional Medicare: $0 (at $200k threshold, not over)
        Total: $13,353.20
        """
        result = calculate_fica(Decimal("200000"), Decimal("0"), FilingStatus.SINGLE)
        assert result.ss_tax == Decimal("10453.20")
        assert result.medicare_tax == Decimal("2900.00")
        assert result.additional_medicare_tax == Decimal("0.00")
        assert result.total_fica == Decimal("13353.20")

    def test_additional_medicare_single(self):
        """$250,000 W-2 wages (SINGLE, threshold $200k).
        SS: $168,600 × 0.062 = $10,453.20
        Medicare: $250,000 × 0.0145 = $3,625.00
        Additional Medicare: ($250,000 - $200,000) × 0.009 = $450.00
        Total: $14,528.20
        """
        result = calculate_fica(Decimal("250000"), Decimal("0"), FilingStatus.SINGLE)
        assert result.ss_tax == Decimal("10453.20")
        assert result.medicare_tax == Decimal("3625.00")
        assert result.additional_medicare_tax == Decimal("450.00")
        assert result.total_fica == Decimal("14528.20")

    def test_zero_wages(self):
        result = calculate_fica(Decimal("0"), Decimal("0"), FilingStatus.SINGLE)
        assert result.total_fica == Decimal("0.00")
        assert result.se_tax_deduction == Decimal("0")


class TestSelfEmploymentOnly:
    """Self-employment income only (no W-2)."""

    def test_basic_se(self):
        """$100,000 SE income (SINGLE).
        SE base: $100,000 × 0.9235 = $92,350.00
        SE SS: $92,350 × 0.124 = $11,451.40
        SE Medicare: $92,350 × 0.029 = $2,678.15
        SE tax: $14,129.55
        SE deduction: $14,129.55 × 0.5 = $7,064.78
        Additional Medicare: $0 (SE base $92,350 < $200k threshold)
        Total: $14,129.55
        """
        result = calculate_fica(Decimal("0"), Decimal("100000"), FilingStatus.SINGLE)
        assert result.ss_tax == Decimal("11451.40")
        assert result.medicare_tax == Decimal("2678.15")
        assert result.se_tax == Decimal("14129.55")
        assert result.se_tax_deduction == Decimal("7064.78")
        assert result.additional_medicare_tax == Decimal("0.00")
        assert result.total_fica == Decimal("14129.55")

    def test_se_above_ss_cap(self):
        """$200,000 SE income — SE base $184,700 exceeds $168,600 wage base.
        SE base: $200,000 × 0.9235 = $184,700.00
        SE SS: $168,600 × 0.124 = $20,906.40
        SE Medicare: $184,700 × 0.029 = $5,356.30
        SE tax: $26,262.70
        SE deduction: $13,131.35
        """
        result = calculate_fica(Decimal("0"), Decimal("200000"), FilingStatus.SINGLE)
        assert result.ss_tax == Decimal("20906.40")
        assert result.medicare_tax == Decimal("5356.30")
        assert result.se_tax == Decimal("26262.70")
        assert result.se_tax_deduction == Decimal("13131.35")


class TestCombinedW2AndSE:
    """W-2 wages + self-employment income."""

    def test_combined_ss_cap(self):
        """$150,000 W-2 + $50,000 SE. SS wage base remaining for SE: $168,600 - $150,000 = $18,600.
        W-2 SS: $150,000 × 0.062 = $9,300.00
        W-2 Medicare: $150,000 × 0.0145 = $2,175.00
        SE base: $50,000 × 0.9235 = $46,175.00
        SE SS: min($46,175, $18,600) × 0.124 = $18,600 × 0.124 = $2,306.40
        SE Medicare: $46,175 × 0.029 = $1,339.08
        SE tax: $2,306.40 + $1,339.08 = $3,645.48
        SE deduction: $1,822.74
        Additional Medicare: ($150,000 + $46,175 - $200,000) × 0.009 = −$3,825 → $0
        Total: $9,300 + $2,175 + $3,645.48 + $0 = $15,120.48
        """
        result = calculate_fica(
            Decimal("150000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.ss_tax == Decimal("11606.40")  # W2 SS + SE SS
        assert result.se_tax == Decimal("3645.48")
        assert result.se_tax_deduction == Decimal("1822.74")

    def test_combined_additional_medicare(self):
        """$180,000 W-2 + $50,000 SE (SINGLE, threshold $200k).
        SE base: $50,000 × 0.9235 = $46,175.00
        Combined for additional Medicare: $180,000 + $46,175 = $226,175
        Excess: $226,175 - $200,000 = $26,175
        Additional Medicare: $26,175 × 0.009 = $235.58
        """
        result = calculate_fica(
            Decimal("180000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.additional_medicare_tax == Decimal("235.58")


class TestMFJFica:
    """MARRIED_FILING_JOINTLY — additional Medicare threshold $250,000."""

    def test_mfj_no_additional_medicare(self):
        """$200,000 W-2 (MFJ, threshold $250k) → no additional Medicare."""
        result = calculate_fica(
            Decimal("200000"), Decimal("0"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.additional_medicare_tax == Decimal("0.00")

    def test_mfj_additional_medicare(self):
        """$300,000 W-2 (MFJ).
        Additional Medicare: ($300,000 - $250,000) × 0.009 = $450.00
        """
        result = calculate_fica(
            Decimal("300000"), Decimal("0"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.additional_medicare_tax == Decimal("450.00")


class TestMFSFica:
    """MARRIED_FILING_SEPARATELY — additional Medicare threshold $125,000."""

    def test_mfs_additional_medicare(self):
        """$150,000 W-2 (MFS, threshold $125k).
        Additional Medicare: ($150,000 - $125,000) × 0.009 = $225.00
        """
        result = calculate_fica(
            Decimal("150000"), Decimal("0"),
            FilingStatus.MARRIED_FILING_SEPARATELY,
        )
        assert result.additional_medicare_tax == Decimal("225.00")


class TestFicaErrors:
    """Error handling."""

    def test_negative_wages_raises(self):
        with pytest.raises(ValueError, match="w2_wages must be >= 0"):
            calculate_fica(Decimal("-1"), Decimal("0"), FilingStatus.SINGLE)

    def test_negative_se_income_raises(self):
        with pytest.raises(ValueError, match="self_employment_income must be >= 0"):
            calculate_fica(Decimal("0"), Decimal("-1"), FilingStatus.SINGLE)

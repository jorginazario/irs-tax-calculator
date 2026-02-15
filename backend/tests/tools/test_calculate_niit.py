"""Tests for calculate_niit tool.

3.8% NIIT on the lesser of net investment income or MAGI exceeding threshold.
Thresholds: $200k SINGLE/HOH, $250k MFJ/QSS, $125k MFS.
"""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.tools.calculate_niit import calculate_niit


class TestSingleNIIT:
    """SINGLE filing status — NIIT."""

    def test_below_threshold(self):
        """MAGI $180,000 < $200,000 threshold → $0 NIIT."""
        result = calculate_niit(
            Decimal("180000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("0.00")
        assert result.excess_magi == Decimal("0")

    def test_at_threshold(self):
        """MAGI exactly $200,000 → $0 NIIT."""
        result = calculate_niit(
            Decimal("200000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("0.00")
        assert result.excess_magi == Decimal("0")

    def test_above_threshold_nii_smaller(self):
        """MAGI $250,000, NII $30,000, excess $50,000.
        Lesser of $30,000 and $50,000 = $30,000.
        $30,000 × 0.038 = $1,140.00
        """
        result = calculate_niit(
            Decimal("250000"), Decimal("30000"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("1140.00")
        assert result.excess_magi == Decimal("50000")
        assert result.threshold == Decimal("200000")

    def test_above_threshold_excess_smaller(self):
        """MAGI $220,000, NII $50,000, excess $20,000.
        Lesser of $50,000 and $20,000 = $20,000.
        $20,000 × 0.038 = $760.00
        """
        result = calculate_niit(
            Decimal("220000"), Decimal("50000"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("760.00")

    def test_zero_investment_income(self):
        """MAGI $300,000 but NII $0 → $0 NIIT."""
        result = calculate_niit(
            Decimal("300000"), Decimal("0"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("0.00")

    def test_zero_magi(self):
        result = calculate_niit(
            Decimal("0"), Decimal("10000"), FilingStatus.SINGLE
        )
        assert result.niit == Decimal("0.00")


class TestMFJNIIT:
    """MARRIED_FILING_JOINTLY — threshold $250,000."""

    def test_below_threshold_mfj(self):
        result = calculate_niit(
            Decimal("240000"), Decimal("80000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.niit == Decimal("0.00")
        assert result.threshold == Decimal("250000")

    def test_above_threshold_mfj(self):
        """MAGI $300,000, NII $100,000, excess $50,000.
        Lesser = $50,000. $50,000 × 0.038 = $1,900.00
        """
        result = calculate_niit(
            Decimal("300000"), Decimal("100000"),
            FilingStatus.MARRIED_FILING_JOINTLY,
        )
        assert result.niit == Decimal("1900.00")


class TestMFSNIIT:
    """MARRIED_FILING_SEPARATELY — threshold $125,000."""

    def test_above_threshold_mfs(self):
        """MAGI $175,000, NII $60,000, excess $50,000.
        Lesser = $50,000. $50,000 × 0.038 = $1,900.00
        """
        result = calculate_niit(
            Decimal("175000"), Decimal("60000"),
            FilingStatus.MARRIED_FILING_SEPARATELY,
        )
        assert result.niit == Decimal("1900.00")
        assert result.threshold == Decimal("125000")


class TestHOHNIIT:
    """HEAD_OF_HOUSEHOLD — threshold $200,000."""

    def test_above_threshold_hoh(self):
        """MAGI $250,000, NII $40,000, excess $50,000.
        Lesser = $40,000. $40,000 × 0.038 = $1,520.00
        """
        result = calculate_niit(
            Decimal("250000"), Decimal("40000"),
            FilingStatus.HEAD_OF_HOUSEHOLD,
        )
        assert result.niit == Decimal("1520.00")


class TestNIITErrors:
    """Error handling."""

    def test_negative_magi_raises(self):
        with pytest.raises(ValueError, match="magi must be >= 0"):
            calculate_niit(Decimal("-1"), Decimal("10000"), FilingStatus.SINGLE)

    def test_negative_nii_raises(self):
        with pytest.raises(ValueError, match="net_investment_income must be >= 0"):
            calculate_niit(Decimal("250000"), Decimal("-1"), FilingStatus.SINGLE)

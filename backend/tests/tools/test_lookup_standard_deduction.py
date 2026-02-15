"""Tests for lookup_standard_deduction tool."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.tools.lookup_standard_deduction import lookup_standard_deduction


class TestBaseStandardDeduction:
    """Base standard deduction amounts — Rev. Proc. 2023-34 §3."""

    def test_single(self):
        r = lookup_standard_deduction(FilingStatus.SINGLE)
        assert r.base_amount == Decimal("14600")
        assert r.additional_amount == Decimal("0")
        assert r.total_deduction == Decimal("14600")

    def test_mfj(self):
        r = lookup_standard_deduction(FilingStatus.MARRIED_FILING_JOINTLY)
        assert r.total_deduction == Decimal("29200")

    def test_mfs(self):
        r = lookup_standard_deduction(FilingStatus.MARRIED_FILING_SEPARATELY)
        assert r.total_deduction == Decimal("14600")

    def test_hoh(self):
        r = lookup_standard_deduction(FilingStatus.HEAD_OF_HOUSEHOLD)
        assert r.total_deduction == Decimal("21900")

    def test_qss(self):
        r = lookup_standard_deduction(FilingStatus.QUALIFYING_SURVIVING_SPOUSE)
        assert r.total_deduction == Decimal("29200")


class TestAdditionalDeduction:
    """Additional deduction for blindness and age ≥ 65 — IRS Pub 501."""

    def test_single_over_65(self):
        r = lookup_standard_deduction(FilingStatus.SINGLE, is_over_65=True)
        assert r.additional_amount == Decimal("1950")
        assert r.total_deduction == Decimal("16550")

    def test_single_blind(self):
        r = lookup_standard_deduction(FilingStatus.SINGLE, is_blind=True)
        assert r.additional_amount == Decimal("1950")
        assert r.total_deduction == Decimal("16550")

    def test_single_blind_and_over_65(self):
        r = lookup_standard_deduction(FilingStatus.SINGLE, is_blind=True, is_over_65=True)
        assert r.additional_amount == Decimal("3900")  # 1950 * 2
        assert r.total_deduction == Decimal("18500")

    def test_mfj_over_65(self):
        r = lookup_standard_deduction(FilingStatus.MARRIED_FILING_JOINTLY, is_over_65=True)
        assert r.additional_amount == Decimal("1550")
        assert r.total_deduction == Decimal("30750")

    def test_mfj_blind_and_over_65(self):
        r = lookup_standard_deduction(
            FilingStatus.MARRIED_FILING_JOINTLY, is_blind=True, is_over_65=True
        )
        assert r.additional_amount == Decimal("3100")  # 1550 * 2
        assert r.total_deduction == Decimal("32300")

    def test_hoh_over_65(self):
        r = lookup_standard_deduction(FilingStatus.HEAD_OF_HOUSEHOLD, is_over_65=True)
        assert r.additional_amount == Decimal("1950")
        assert r.total_deduction == Decimal("23850")

    def test_mfs_blind(self):
        r = lookup_standard_deduction(FilingStatus.MARRIED_FILING_SEPARATELY, is_blind=True)
        assert r.additional_amount == Decimal("1550")
        assert r.total_deduction == Decimal("16150")

    def test_qss_over_65_and_blind(self):
        r = lookup_standard_deduction(
            FilingStatus.QUALIFYING_SURVIVING_SPOUSE, is_blind=True, is_over_65=True
        )
        assert r.additional_amount == Decimal("3100")
        assert r.total_deduction == Decimal("32300")

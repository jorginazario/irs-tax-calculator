"""Tests for the credits workflow."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import (
    TaxComputationResult,
    TaxCredits,
    TaxReturnInput,
    W2Income,
)
from src.workflows.credits_workflow import run_credits_workflow


def _make_agi(agi: Decimal) -> AGIResult:
    return AGIResult(
        total_gross_income=agi,
        total_above_line_deductions=Decimal("0"),
        agi=agi,
    )


def _make_tax_comp(total: Decimal) -> TaxComputationResult:
    return TaxComputationResult(
        ordinary_tax=total,
        qualified_dividend_tax=Decimal("0"),
        capital_gains_tax=Decimal("0"),
        niit=Decimal("0"),
        total_income_tax=total,
    )


class TestCreditsWorkflow:
    """Test CTC calculation with phaseout and refundable split."""

    def test_no_children(self):
        ret = TaxReturnInput(filing_status=FilingStatus.SINGLE)
        agi = _make_agi(Decimal("75000"))
        tax_comp = _make_tax_comp(Decimal("8341"))
        result = run_credits_workflow(ret, agi, tax_comp)
        assert result.child_tax_credit == Decimal("0.00")
        assert result.total_credits_applied == Decimal("0.00")
        assert result.tax_after_credits == Decimal("8341.00")

    def test_one_child_under_phaseout(self):
        """Single filer, 1 child, AGI $75k (under $200k phaseout)."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            credits=TaxCredits(num_qualifying_children=1),
        )
        agi = _make_agi(Decimal("75000"))
        tax_comp = _make_tax_comp(Decimal("8341"))
        result = run_credits_workflow(ret, agi, tax_comp)
        assert result.child_tax_credit == Decimal("2000.00")
        assert result.nonrefundable_ctc_applied == Decimal("2000.00")
        assert result.refundable_ctc_applied == Decimal("0.00")
        assert result.tax_after_credits == Decimal("6341.00")

    def test_two_children_mfj(self):
        """MFJ, 2 children, AGI $150k (under $400k phaseout)."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
            credits=TaxCredits(num_qualifying_children=2),
        )
        agi = _make_agi(Decimal("150000"))
        tax_comp = _make_tax_comp(Decimal("15000"))
        result = run_credits_workflow(ret, agi, tax_comp)
        assert result.child_tax_credit == Decimal("4000.00")
        assert result.nonrefundable_ctc_applied == Decimal("4000.00")
        assert result.tax_after_credits == Decimal("11000.00")

    def test_ctc_exceeds_liability_refundable(self):
        """Tax liability < CTC — excess becomes refundable ACTC (up to $1,700/child)."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            credits=TaxCredits(num_qualifying_children=2),
        )
        agi = _make_agi(Decimal("30000"))
        tax_comp = _make_tax_comp(Decimal("1000"))
        result = run_credits_workflow(ret, agi, tax_comp)
        # CTC = $4,000 (2 × $2,000)
        assert result.child_tax_credit == Decimal("4000.00")
        # Non-refundable: limited to $1,000 (tax liability)
        assert result.nonrefundable_ctc_applied == Decimal("1000.00")
        # Refundable: unused = 4000-1000 = 3000, cap = 2 × 1700 = 3400
        # min(3000, 3400) = 3000
        assert result.refundable_ctc_applied == Decimal("3000.00")
        # Tax after: 1000 - 1000 - 3000 = -3000
        assert result.tax_after_credits == Decimal("-3000.00")

    def test_ctc_phaseout_single(self):
        """Single filer, 1 child, AGI $210k — CTC phased out partially."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            credits=TaxCredits(num_qualifying_children=1),
        )
        agi = _make_agi(Decimal("210000"))
        tax_comp = _make_tax_comp(Decimal("40000"))
        result = run_credits_workflow(ret, agi, tax_comp)
        # Phaseout: (210000 - 200000) / 1000 = 10 units × $50 = $500
        # CTC = 2000 - 500 = 1500
        assert result.child_tax_credit == Decimal("1500.00")
        assert result.nonrefundable_ctc_applied == Decimal("1500.00")
        assert result.tax_after_credits == Decimal("38500.00")

    def test_ctc_fully_phased_out(self):
        """Very high AGI — CTC completely phased out."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            credits=TaxCredits(num_qualifying_children=1),
        )
        agi = _make_agi(Decimal("250000"))
        tax_comp = _make_tax_comp(Decimal("50000"))
        result = run_credits_workflow(ret, agi, tax_comp)
        # Phaseout: (250000-200000)/1000 = 50 × $50 = $2500 > $2000
        # CTC = max(2000-2500, 0) = 0
        assert result.child_tax_credit == Decimal("0.00")
        assert result.total_credits_applied == Decimal("0.00")

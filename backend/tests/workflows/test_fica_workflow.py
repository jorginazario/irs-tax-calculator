"""Tests for the FICA workflow."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.workflow_models import IncomeResult
from src.workflows.fica_workflow import run_fica_workflow


def _make_income(**kwargs) -> IncomeResult:
    defaults = dict(
        wages=Decimal("0"),
        self_employment_income=Decimal("0"),
        interest_income=Decimal("0"),
        ordinary_dividends=Decimal("0"),
        qualified_dividends=Decimal("0"),
        short_term_gains=Decimal("0"),
        long_term_gains=Decimal("0"),
        total_gross_income=Decimal("0"),
        net_investment_income=Decimal("0"),
    )
    defaults.update(kwargs)
    return IncomeResult(**defaults)


class TestFicaWorkflow:
    """Test FICA workflow delegation to calculate_fica tool."""

    def test_w2_only(self):
        income = _make_income(wages=Decimal("75000"), total_gross_income=Decimal("75000"))
        result = run_fica_workflow(income, FilingStatus.SINGLE)
        # SS: 75000 * 0.062 = 4650
        assert result.ss_tax == Decimal("4650.00")
        # Medicare: 75000 * 0.0145 = 1087.50
        assert result.medicare_tax == Decimal("1087.50")
        assert result.se_tax == Decimal("0.00")
        assert result.se_tax_deduction == Decimal("0.00")

    def test_se_only(self):
        income = _make_income(
            self_employment_income=Decimal("120000"),
            total_gross_income=Decimal("120000"),
        )
        result = run_fica_workflow(income, FilingStatus.SINGLE)
        assert result.se_tax > Decimal("0")
        assert result.se_tax_deduction > Decimal("0")
        # SE deduction = 50% of SE tax
        assert result.se_tax_deduction == (result.se_tax * Decimal("0.5")).quantize(
            Decimal("0.01")
        )

    def test_zero_income(self):
        income = _make_income()
        result = run_fica_workflow(income, FilingStatus.SINGLE)
        assert result.total_fica == Decimal("0.00")
        assert result.se_tax_deduction == Decimal("0.00")

    def test_high_income_additional_medicare(self):
        income = _make_income(wages=Decimal("250000"), total_gross_income=Decimal("250000"))
        result = run_fica_workflow(income, FilingStatus.SINGLE)
        # Additional Medicare: 0.9% on (250000 - 200000) = $450
        assert result.additional_medicare_tax == Decimal("450.00")

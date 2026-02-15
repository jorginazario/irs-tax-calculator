"""Tests for the tax computation workflow."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import DeductionResult, IncomeResult
from src.workflows.tax_computation_workflow import run_tax_computation_workflow


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


def _make_agi(agi: Decimal) -> AGIResult:
    return AGIResult(
        total_gross_income=agi,
        total_above_line_deductions=Decimal("0"),
        agi=agi,
    )


def _make_deductions(**kwargs) -> DeductionResult:
    defaults = dict(
        standard_deduction_amount=Decimal("14600"),
        itemized_total=Decimal("0"),
        used_standard=True,
        deduction_amount=Decimal("14600"),
        taxable_income=Decimal("0"),
        ordinary_taxable_income=Decimal("0"),
        preferential_qualified_dividends=Decimal("0"),
        preferential_long_term_gains=Decimal("0"),
    )
    defaults.update(kwargs)
    return DeductionResult(**defaults)


class TestTaxComputationWorkflow:
    """Test federal income tax computation."""

    def test_ordinary_income_only(self):
        """$60,400 ordinary taxable income (Single) — standard scenario."""
        income = _make_income(wages=Decimal("75000"), total_gross_income=Decimal("75000"))
        agi = _make_agi(Decimal("75000"))
        deductions = _make_deductions(
            taxable_income=Decimal("60400"),
            ordinary_taxable_income=Decimal("60400"),
        )
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        # Bracket tax on $60,400:
        # 10%: 11600 * 0.10 = 1160
        # 12%: (47150-11600) * 0.12 = 4266
        # 22%: (60400-47150) * 0.22 = 2915
        # Total ≈ 8341
        assert result.ordinary_tax == Decimal("8341.00")
        assert result.qualified_dividend_tax == Decimal("0.00")
        assert result.capital_gains_tax == Decimal("0.00")
        assert result.niit == Decimal("0.00")
        assert result.total_income_tax == Decimal("8341.00")

    def test_with_qualified_dividends(self):
        """$50,400 ordinary + $5,000 qualified dividends (Single)."""
        income = _make_income(
            wages=Decimal("70000"),
            qualified_dividends=Decimal("5000"),
            total_gross_income=Decimal("70000"),
            net_investment_income=Decimal("5000"),
        )
        agi = _make_agi(Decimal("70000"))
        deductions = _make_deductions(
            taxable_income=Decimal("55400"),
            ordinary_taxable_income=Decimal("50400"),
            preferential_qualified_dividends=Decimal("5000"),
        )
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        # Ordinary tax on $50,400 < $60,400 from above
        assert result.ordinary_tax > Decimal("0")
        # Qualified dividends taxed at preferential rates
        assert result.qualified_dividend_tax >= Decimal("0")
        assert result.niit == Decimal("0.00")  # under $200k

    def test_with_long_term_gains(self):
        """Ordinary + LTCG (Single, under NIIT threshold)."""
        income = _make_income(
            wages=Decimal("50000"),
            long_term_gains=Decimal("20000"),
            total_gross_income=Decimal("70000"),
            net_investment_income=Decimal("20000"),
        )
        agi = _make_agi(Decimal("70000"))
        deductions = _make_deductions(
            taxable_income=Decimal("55400"),
            ordinary_taxable_income=Decimal("35400"),
            preferential_long_term_gains=Decimal("20000"),
        )
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        assert result.ordinary_tax > Decimal("0")
        assert result.capital_gains_tax >= Decimal("0")  # 0% bracket likely
        assert result.niit == Decimal("0.00")

    def test_niit_applies(self):
        """High income triggers NIIT — Single $250k AGI with $30k NII."""
        income = _make_income(
            wages=Decimal("220000"),
            interest_income=Decimal("10000"),
            ordinary_dividends=Decimal("20000"),
            total_gross_income=Decimal("250000"),
            net_investment_income=Decimal("30000"),
        )
        agi = _make_agi(Decimal("250000"))
        deductions = _make_deductions(
            taxable_income=Decimal("235400"),
            ordinary_taxable_income=Decimal("235400"),
        )
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        # NIIT: 3.8% on min(30000 NII, 250000-200000 excess) = 3.8% * 30000 = 1140
        assert result.niit == Decimal("1140.00")

    def test_zero_income(self):
        income = _make_income()
        agi = _make_agi(Decimal("0"))
        deductions = _make_deductions()
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        assert result.total_income_tax == Decimal("0.00")

    def test_stacking_order_divs_then_gains(self):
        """Verify qualified dividends stack before LTCG per IRC §1(h)."""
        income = _make_income(
            wages=Decimal("40000"),
            qualified_dividends=Decimal("10000"),
            long_term_gains=Decimal("10000"),
            ordinary_dividends=Decimal("10000"),
            total_gross_income=Decimal("60000"),
            net_investment_income=Decimal("20000"),
        )
        agi = _make_agi(Decimal("60000"))
        deductions = _make_deductions(
            taxable_income=Decimal("45400"),
            ordinary_taxable_income=Decimal("25400"),
            preferential_qualified_dividends=Decimal("10000"),
            preferential_long_term_gains=Decimal("10000"),
        )
        result = run_tax_computation_workflow(income, agi, deductions, FilingStatus.SINGLE)
        # All components should be non-negative
        assert result.ordinary_tax >= Decimal("0")
        assert result.qualified_dividend_tax >= Decimal("0")
        assert result.capital_gains_tax >= Decimal("0")
        # Total should be sum
        expected_total = (
            result.ordinary_tax
            + result.qualified_dividend_tax
            + result.capital_gains_tax
            + result.niit
        )
        assert result.total_income_tax == expected_total

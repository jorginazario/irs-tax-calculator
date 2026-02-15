"""Tests for the deduction workflow."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import (
    IncomeResult,
    ItemizedDeductions,
    TaxReturnInput,
    W2Income,
)
from src.workflows.deduction_workflow import run_deduction_workflow


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


class TestDeductionWorkflow:
    """Test deduction selection and income partitioning."""

    def test_standard_deduction_single(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("75000"))],
        )
        income = _make_income(wages=Decimal("75000"), total_gross_income=Decimal("75000"))
        agi = _make_agi(Decimal("75000"))
        result = run_deduction_workflow(ret, income, agi)
        assert result.used_standard is True
        assert result.deduction_amount == Decimal("14600.00")
        assert result.taxable_income == Decimal("60400.00")
        assert result.ordinary_taxable_income == Decimal("60400.00")

    def test_standard_deduction_mfj(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
            w2s=[W2Income(wages=Decimal("150000"))],
        )
        income = _make_income(wages=Decimal("150000"), total_gross_income=Decimal("150000"))
        agi = _make_agi(Decimal("150000"))
        result = run_deduction_workflow(ret, income, agi)
        assert result.used_standard is True
        assert result.deduction_amount == Decimal("29200.00")
        assert result.taxable_income == Decimal("120800.00")

    def test_itemized_exceeds_standard(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("200000"))],
            itemized_deductions=ItemizedDeductions(
                state_and_local_taxes=Decimal("10000"),
                mortgage_interest=Decimal("12000"),
                charitable=Decimal("5000"),
            ),
        )
        income = _make_income(wages=Decimal("200000"), total_gross_income=Decimal("200000"))
        agi = _make_agi(Decimal("200000"))
        result = run_deduction_workflow(ret, income, agi)
        # Itemized: 10000 (SALT capped) + 12000 + 5000 = 27000 > 14600
        assert result.used_standard is False
        assert result.itemized_total == Decimal("27000.00")
        assert result.deduction_amount == Decimal("27000.00")
        assert result.taxable_income == Decimal("173000.00")

    def test_salt_cap_10000(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("200000"))],
            itemized_deductions=ItemizedDeductions(
                state_and_local_taxes=Decimal("25000"),
                mortgage_interest=Decimal("8000"),
            ),
        )
        income = _make_income(wages=Decimal("200000"), total_gross_income=Decimal("200000"))
        agi = _make_agi(Decimal("200000"))
        result = run_deduction_workflow(ret, income, agi)
        # SALT capped at $10,000 + mortgage $8,000 = $18,000
        assert result.itemized_total == Decimal("18000.00")

    def test_salt_cap_5000_mfs(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.MARRIED_FILING_SEPARATELY,
            w2s=[W2Income(wages=Decimal("100000"))],
            itemized_deductions=ItemizedDeductions(
                state_and_local_taxes=Decimal("15000"),
                mortgage_interest=Decimal("12000"),
            ),
        )
        income = _make_income(wages=Decimal("100000"), total_gross_income=Decimal("100000"))
        agi = _make_agi(Decimal("100000"))
        result = run_deduction_workflow(ret, income, agi)
        # SALT capped at $5,000 for MFS + mortgage $12,000 = $17,000
        assert result.itemized_total == Decimal("17000.00")

    def test_medical_7_5_percent_floor(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("50000"))],
            itemized_deductions=ItemizedDeductions(
                medical=Decimal("10000"),
                state_and_local_taxes=Decimal("5000"),
            ),
        )
        income = _make_income(wages=Decimal("50000"), total_gross_income=Decimal("50000"))
        agi = _make_agi(Decimal("50000"))
        result = run_deduction_workflow(ret, income, agi)
        # Medical: 10000 - (50000 * 0.075) = 10000 - 3750 = 6250
        # SALT: 5000 (under cap)
        # Total: 6250 + 5000 = 11250 < 14600 standard → use standard
        assert result.itemized_total == Decimal("11250.00")
        assert result.used_standard is True

    def test_force_standard_deduction(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("200000"))],
            force_standard_deduction=True,
            itemized_deductions=ItemizedDeductions(
                state_and_local_taxes=Decimal("10000"),
                mortgage_interest=Decimal("12000"),
                charitable=Decimal("5000"),
            ),
        )
        income = _make_income(wages=Decimal("200000"), total_gross_income=Decimal("200000"))
        agi = _make_agi(Decimal("200000"))
        result = run_deduction_workflow(ret, income, agi)
        # Forced standard even though itemized ($27k) > standard ($14.6k)
        assert result.used_standard is True
        assert result.deduction_amount == Decimal("14600.00")

    def test_preferential_income_partitioning(self):
        """Qualified dividends and LTCG split from ordinary taxable income."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("80000"))],
        )
        income = _make_income(
            wages=Decimal("80000"),
            qualified_dividends=Decimal("5000"),
            long_term_gains=Decimal("10000"),
            total_gross_income=Decimal("80000"),
        )
        agi = _make_agi(Decimal("80000"))
        result = run_deduction_workflow(ret, income, agi)
        # taxable = 80000 - 14600 = 65400
        # preferential = 5000 + 10000 = 15000
        # ordinary = 65400 - 15000 = 50400
        assert result.taxable_income == Decimal("65400.00")
        assert result.preferential_qualified_dividends == Decimal("5000.00")
        assert result.preferential_long_term_gains == Decimal("10000.00")
        assert result.ordinary_taxable_income == Decimal("50400.00")

    def test_preferential_exceeds_taxable_proportional_cap(self):
        """When preferential income exceeds taxable income, cap proportionally."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("20000"))],
        )
        income = _make_income(
            wages=Decimal("20000"),
            qualified_dividends=Decimal("3000"),
            long_term_gains=Decimal("7000"),
            total_gross_income=Decimal("20000"),
        )
        agi = _make_agi(Decimal("20000"))
        result = run_deduction_workflow(ret, income, agi)
        # taxable = 20000 - 14600 = 5400
        # preferential = 3000 + 7000 = 10000 > 5400
        # ratio = 5400 / 10000 = 0.54
        # pref_divs = 3000 * 0.54 = 1620
        # pref_ltcg = 5400 - 1620 = 3780
        assert result.taxable_income == Decimal("5400.00")
        assert result.preferential_qualified_dividends == Decimal("1620.00")
        assert result.preferential_long_term_gains == Decimal("3780.00")
        assert result.ordinary_taxable_income == Decimal("0.00")

    def test_zero_income(self):
        ret = TaxReturnInput(filing_status=FilingStatus.SINGLE)
        income = _make_income()
        agi = _make_agi(Decimal("0"))
        result = run_deduction_workflow(ret, income, agi)
        assert result.taxable_income == Decimal("0.00")
        assert result.ordinary_taxable_income == Decimal("0.00")

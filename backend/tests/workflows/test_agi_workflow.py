"""Tests for the AGI workflow."""

from decimal import Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import FicaResult
from src.models.workflow_models import (
    Income1099NEC,
    IncomeResult,
    TaxReturnInput,
    W2Income,
)
from src.workflows.agi_workflow import run_agi_workflow


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


def _make_fica(**kwargs) -> FicaResult:
    defaults = dict(
        ss_tax=Decimal("0"),
        medicare_tax=Decimal("0"),
        additional_medicare_tax=Decimal("0"),
        se_tax=Decimal("0"),
        se_tax_deduction=Decimal("0"),
        total_fica=Decimal("0"),
    )
    defaults.update(kwargs)
    return FicaResult(**defaults)


class TestAGIWorkflow:
    """Test AGI workflow with SE deduction injection."""

    def test_simple_w2(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("75000"))],
        )
        income = _make_income(wages=Decimal("75000"), total_gross_income=Decimal("75000"))
        fica = _make_fica()
        result = run_agi_workflow(ret, income, fica)
        assert result.agi == Decimal("75000.00")

    def test_se_deduction_reduces_agi(self):
        """SE deduction is automatically injected from FICA result."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            income_1099_nec=[Income1099NEC(compensation=Decimal("100000"))],
        )
        income = _make_income(
            self_employment_income=Decimal("100000"),
            total_gross_income=Decimal("100000"),
        )
        # SE tax = ~14130 (100000 * 0.9235 * 0.153), deduction = ~7065
        fica = _make_fica(
            se_tax=Decimal("14130.00"),
            se_tax_deduction=Decimal("7065.00"),
        )
        result = run_agi_workflow(ret, income, fica)
        # AGI = 100000 - 7065 = 92935
        assert result.agi == Decimal("92935.00")
        assert result.total_above_line_deductions == Decimal("7065.00")

    def test_hsa_deduction(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("60000"))],
            hsa_deduction=Decimal("4150"),
        )
        income = _make_income(wages=Decimal("60000"), total_gross_income=Decimal("60000"))
        fica = _make_fica()
        result = run_agi_workflow(ret, income, fica)
        assert result.agi == Decimal("55850.00")

    def test_multiple_above_line_deductions(self):
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            w2s=[W2Income(wages=Decimal("80000"))],
            hsa_deduction=Decimal("4150"),
            student_loan_interest=Decimal("2500"),
            educator_expenses=Decimal("300"),
        )
        income = _make_income(wages=Decimal("80000"), total_gross_income=Decimal("80000"))
        fica = _make_fica()
        result = run_agi_workflow(ret, income, fica)
        # AGI = 80000 - 4150 - 2500 - 300 = 73050
        assert result.agi == Decimal("73050.00")

    def test_zero_income(self):
        ret = TaxReturnInput(filing_status=FilingStatus.SINGLE)
        income = _make_income()
        fica = _make_fica()
        result = run_agi_workflow(ret, income, fica)
        assert result.agi == Decimal("0.00")

    def test_se_plus_hsa(self):
        """Combined SE deduction and HSA deduction."""
        ret = TaxReturnInput(
            filing_status=FilingStatus.SINGLE,
            income_1099_nec=[Income1099NEC(compensation=Decimal("80000"))],
            hsa_deduction=Decimal("4150"),
        )
        income = _make_income(
            self_employment_income=Decimal("80000"),
            total_gross_income=Decimal("80000"),
        )
        fica = _make_fica(
            se_tax=Decimal("11304.00"),
            se_tax_deduction=Decimal("5652.00"),
        )
        result = run_agi_workflow(ret, income, fica)
        # AGI = 80000 - 5652 - 4150 = 70198
        assert result.agi == Decimal("70198.00")

"""Tests for the income aggregation workflow."""

from decimal import Decimal

import pytest

from src.models.filing_status import FilingStatus
from src.models.workflow_models import (
    Income1099B,
    Income1099DIV,
    Income1099INT,
    Income1099NEC,
    TaxReturnInput,
    W2Income,
)
from src.workflows.income_workflow import run_income_workflow


def _make_return(**kwargs) -> TaxReturnInput:
    return TaxReturnInput(filing_status=FilingStatus.SINGLE, **kwargs)


class TestIncomeWorkflow:
    """Test income aggregation from form inputs."""

    def test_single_w2(self):
        ret = _make_return(w2s=[W2Income(wages=Decimal("75000"))])
        result = run_income_workflow(ret)
        assert result.wages == Decimal("75000.00")
        assert result.total_gross_income == Decimal("75000.00")
        assert result.net_investment_income == Decimal("0.00")

    def test_multiple_w2s(self):
        ret = _make_return(
            w2s=[
                W2Income(wages=Decimal("50000")),
                W2Income(wages=Decimal("30000")),
            ]
        )
        result = run_income_workflow(ret)
        assert result.wages == Decimal("80000.00")
        assert result.total_gross_income == Decimal("80000.00")

    def test_1099_nec_only(self):
        ret = _make_return(
            income_1099_nec=[Income1099NEC(compensation=Decimal("120000"))]
        )
        result = run_income_workflow(ret)
        assert result.self_employment_income == Decimal("120000.00")
        assert result.wages == Decimal("0.00")
        assert result.total_gross_income == Decimal("120000.00")

    def test_mixed_income(self):
        ret = _make_return(
            w2s=[W2Income(wages=Decimal("100000"))],
            income_1099_int=[Income1099INT(interest=Decimal("5000"))],
            income_1099_div=[
                Income1099DIV(
                    ordinary_dividends=Decimal("3000"),
                    qualified_dividends=Decimal("2000"),
                )
            ],
            income_1099_b=[
                Income1099B(
                    short_term_gains=Decimal("1000"),
                    long_term_gains=Decimal("10000"),
                )
            ],
        )
        result = run_income_workflow(ret)
        assert result.wages == Decimal("100000.00")
        assert result.interest_income == Decimal("5000.00")
        assert result.ordinary_dividends == Decimal("3000.00")
        assert result.qualified_dividends == Decimal("2000.00")
        assert result.short_term_gains == Decimal("1000.00")
        assert result.long_term_gains == Decimal("10000.00")
        # 100000 + 5000 + 3000 + 1000 + 10000 = 119000
        assert result.total_gross_income == Decimal("119000.00")
        # NII = 5000 + 3000 + max(1000+10000, 0) = 19000
        assert result.net_investment_income == Decimal("19000.00")

    def test_capital_losses_reduce_income(self):
        ret = _make_return(
            w2s=[W2Income(wages=Decimal("50000"))],
            income_1099_b=[
                Income1099B(
                    short_term_gains=Decimal("-5000"),
                    long_term_gains=Decimal("-3000"),
                )
            ],
        )
        result = run_income_workflow(ret)
        # 50000 + (-5000) + (-3000) = 42000
        assert result.total_gross_income == Decimal("42000.00")
        # NII: losses capped at 0 for NII purposes
        assert result.net_investment_income == Decimal("0.00")

    def test_zero_income(self):
        ret = _make_return()
        result = run_income_workflow(ret)
        assert result.total_gross_income == Decimal("0.00")
        assert result.net_investment_income == Decimal("0.00")

    def test_interest_and_dividends_count_as_nii(self):
        ret = _make_return(
            income_1099_int=[Income1099INT(interest=Decimal("10000"))],
            income_1099_div=[
                Income1099DIV(
                    ordinary_dividends=Decimal("8000"),
                    qualified_dividends=Decimal("5000"),
                )
            ],
        )
        result = run_income_workflow(ret)
        # NII = interest + ordinary_dividends + max(gains, 0)
        # = 10000 + 8000 + 0 = 18000
        assert result.net_investment_income == Decimal("18000.00")
        assert result.total_gross_income == Decimal("18000.00")

    def test_multiple_1099_b_forms(self):
        ret = _make_return(
            income_1099_b=[
                Income1099B(short_term_gains=Decimal("2000"), long_term_gains=Decimal("5000")),
                Income1099B(short_term_gains=Decimal("-1000"), long_term_gains=Decimal("3000")),
            ],
        )
        result = run_income_workflow(ret)
        assert result.short_term_gains == Decimal("1000.00")
        assert result.long_term_gains == Decimal("8000.00")
        # NII = max(1000 + 8000, 0) = 9000
        assert result.net_investment_income == Decimal("9000.00")

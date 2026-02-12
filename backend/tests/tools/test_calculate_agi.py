"""Tests for calculate_agi tool."""

from decimal import Decimal

import pytest

from src.models.tax_input import AboveLineDeductions, GrossIncome
from src.tools.calculate_agi import calculate_agi


class TestCalculateAGI:
    """Unit tests for AGI calculation — Form 1040 Line 11."""

    def test_simple_w2_only(self):
        income = GrossIncome(w2_wages=Decimal("75000"))
        result = calculate_agi(income)
        assert result.agi == Decimal("75000.00")
        assert result.total_gross_income == Decimal("75000.00")
        assert result.total_above_line_deductions == Decimal("0.00")

    def test_multiple_income_sources(self):
        income = GrossIncome(
            w2_wages=Decimal("50000"),
            nec_1099=Decimal("10000"),
            interest_income=Decimal("500"),
            ordinary_dividends=Decimal("1200"),
            long_term_gains=Decimal("3000"),
        )
        result = calculate_agi(income)
        assert result.total_gross_income == Decimal("64700.00")
        assert result.agi == Decimal("64700.00")

    def test_with_above_line_deductions(self):
        income = GrossIncome(w2_wages=Decimal("80000"))
        deductions = AboveLineDeductions(
            student_loan_interest=Decimal("2500"),
            hsa_deduction=Decimal("4150"),
        )
        result = calculate_agi(income, deductions)
        assert result.total_above_line_deductions == Decimal("6650.00")
        assert result.agi == Decimal("73350.00")

    def test_deductions_exceed_income_floors_at_zero(self):
        income = GrossIncome(w2_wages=Decimal("5000"))
        deductions = AboveLineDeductions(
            ira_deduction=Decimal("7000"),
            student_loan_interest=Decimal("2500"),
        )
        result = calculate_agi(income, deductions)
        assert result.agi == Decimal("0.00")

    def test_zero_income(self):
        income = GrossIncome()
        result = calculate_agi(income)
        assert result.agi == Decimal("0.00")
        assert result.total_gross_income == Decimal("0.00")

    def test_capital_losses_reduce_income(self):
        income = GrossIncome(
            w2_wages=Decimal("60000"),
            short_term_gains=Decimal("-3000"),
        )
        result = calculate_agi(income)
        assert result.total_gross_income == Decimal("57000.00")
        assert result.agi == Decimal("57000.00")

    def test_mixed_gains_and_losses(self):
        income = GrossIncome(
            w2_wages=Decimal("100000"),
            short_term_gains=Decimal("-5000"),
            long_term_gains=Decimal("8000"),
        )
        result = calculate_agi(income)
        assert result.total_gross_income == Decimal("103000.00")
        assert result.agi == Decimal("103000.00")

    def test_none_deductions_defaults(self):
        income = GrossIncome(w2_wages=Decimal("50000"))
        result = calculate_agi(income, None)
        assert result.agi == Decimal("50000.00")

    def test_rounding(self):
        """Fractional cents are rounded to 2 decimal places."""
        income = GrossIncome(
            w2_wages=Decimal("33333.33"),
            interest_income=Decimal("11111.11"),
        )
        result = calculate_agi(income)
        assert result.agi == Decimal("44444.44")

    def test_all_deduction_types(self):
        income = GrossIncome(w2_wages=Decimal("100000"))
        deductions = AboveLineDeductions(
            educator_expenses=Decimal("300"),
            student_loan_interest=Decimal("2500"),
            hsa_deduction=Decimal("4150"),
            ira_deduction=Decimal("7000"),
            se_tax_deduction=Decimal("1000"),
            self_employed_health_insurance=Decimal("500"),
            penalty_early_withdrawal=Decimal("100"),
            alimony_paid=Decimal("0"),
        )
        result = calculate_agi(income, deductions)
        assert result.total_above_line_deductions == Decimal("15550.00")
        assert result.agi == Decimal("84450.00")


class TestGrossIncomeValidation:
    """Validation tests for GrossIncome model."""

    def test_qualified_exceeds_ordinary_raises(self):
        with pytest.raises(ValueError, match="qualified_dividends cannot exceed"):
            GrossIncome(
                ordinary_dividends=Decimal("100"),
                qualified_dividends=Decimal("200"),
            )

    def test_negative_w2_wages_raises(self):
        with pytest.raises(ValueError):
            GrossIncome(w2_wages=Decimal("-1"))

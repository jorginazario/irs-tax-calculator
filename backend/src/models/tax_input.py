"""Pydantic input models for IRS Tax Calculator."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.models.filing_status import FilingStatus


class GrossIncome(BaseModel):
    """All income sources — Form 1040 Lines 1-8."""

    w2_wages: Decimal = Field(default=Decimal("0"), ge=0, description="W-2 Box 1 wages")
    nec_1099: Decimal = Field(
        default=Decimal("0"), ge=0, description="1099-NEC non-employee compensation"
    )
    interest_income: Decimal = Field(
        default=Decimal("0"), ge=0, description="1099-INT interest income"
    )
    ordinary_dividends: Decimal = Field(
        default=Decimal("0"), ge=0, description="1099-DIV ordinary dividends"
    )
    qualified_dividends: Decimal = Field(
        default=Decimal("0"), ge=0, description="1099-DIV qualified dividends"
    )
    short_term_gains: Decimal = Field(
        default=Decimal("0"), description="1099-B short-term capital gains (may be negative)"
    )
    long_term_gains: Decimal = Field(
        default=Decimal("0"), description="1099-B long-term capital gains (may be negative)"
    )

    @model_validator(mode="after")
    def qualified_le_ordinary(self) -> "GrossIncome":
        if self.qualified_dividends > self.ordinary_dividends:
            msg = "qualified_dividends cannot exceed ordinary_dividends"
            raise ValueError(msg)
        return self


class AboveLineDeductions(BaseModel):
    """Above-the-line (Schedule 1) deductions — Form 1040 Line 10."""

    educator_expenses: Decimal = Field(default=Decimal("0"), ge=0)
    student_loan_interest: Decimal = Field(default=Decimal("0"), ge=0)
    hsa_deduction: Decimal = Field(default=Decimal("0"), ge=0)
    ira_deduction: Decimal = Field(default=Decimal("0"), ge=0)
    se_tax_deduction: Decimal = Field(default=Decimal("0"), ge=0)
    self_employed_health_insurance: Decimal = Field(default=Decimal("0"), ge=0)
    penalty_early_withdrawal: Decimal = Field(default=Decimal("0"), ge=0)
    alimony_paid: Decimal = Field(default=Decimal("0"), ge=0)


class BracketTaxInput(BaseModel):
    """Input for the bracket-tax tool."""

    taxable_income: Decimal = Field(ge=0)
    filing_status: FilingStatus


class StandardDeductionInput(BaseModel):
    """Input for the standard-deduction lookup tool."""

    filing_status: FilingStatus
    is_blind: bool = False
    is_over_65: bool = False


class AGIInput(BaseModel):
    """Input for the AGI calculation tool."""

    gross_income: GrossIncome
    above_line_deductions: AboveLineDeductions = AboveLineDeductions()


class CapitalGainsTaxInput(BaseModel):
    """Input for the capital gains tax tool."""

    short_term_gains: Decimal = Field(default=Decimal("0"), description="1099-B short-term gains")
    long_term_gains: Decimal = Field(default=Decimal("0"), description="1099-B long-term gains")
    ordinary_income: Decimal = Field(
        ge=0, description="Ordinary taxable income (for stacking)"
    )
    filing_status: FilingStatus


class QualifiedDividendTaxInput(BaseModel):
    """Input for the qualified dividend tax tool."""

    qualified_dividends: Decimal = Field(ge=0, description="1099-DIV qualified dividends")
    ordinary_income: Decimal = Field(
        ge=0, description="Ordinary taxable income (for stacking)"
    )
    filing_status: FilingStatus


class NiitInput(BaseModel):
    """Input for the Net Investment Income Tax tool."""

    magi: Decimal = Field(ge=0, description="Modified Adjusted Gross Income")
    net_investment_income: Decimal = Field(ge=0, description="Net investment income")
    filing_status: FilingStatus


class FicaInput(BaseModel):
    """Input for the FICA / self-employment tax tool."""

    w2_wages: Decimal = Field(default=Decimal("0"), ge=0, description="W-2 wages")
    self_employment_income: Decimal = Field(
        default=Decimal("0"), ge=0, description="Net self-employment income"
    )
    filing_status: FilingStatus


class CreditInput(BaseModel):
    """Input for the apply_credit tool."""

    tax_owed: Decimal = Field(description="Tax before credit")
    credit_amount: Decimal = Field(ge=0, description="Credit amount to apply")
    is_refundable: bool = Field(
        default=False, description="If True, credit can reduce tax below $0"
    )

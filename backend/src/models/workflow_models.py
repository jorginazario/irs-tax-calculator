"""Pydantic models for the workflow layer — form-level inputs and workflow outputs.

These models sit above the tool-level models, providing the shape of data
as it flows through the full tax-calculation pipeline.
"""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.models.filing_status import FilingStatus


# ---------------------------------------------------------------------------
# Form-level INPUT models
# ---------------------------------------------------------------------------


class W2Income(BaseModel):
    """W-2 wage and withholding data — Form W-2."""

    wages: Decimal = Field(default=Decimal("0"), ge=0, description="Box 1: Wages, tips, etc.")
    federal_withholding: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 2: Federal income tax withheld"
    )
    social_security_wages: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 3: Social Security wages"
    )
    medicare_wages: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 5: Medicare wages"
    )


class Income1099NEC(BaseModel):
    """1099-NEC — non-employee compensation."""

    compensation: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 1: Nonemployee compensation"
    )


class Income1099INT(BaseModel):
    """1099-INT — interest income."""

    interest: Decimal = Field(default=Decimal("0"), ge=0, description="Box 1: Interest income")


class Income1099DIV(BaseModel):
    """1099-DIV — dividends."""

    ordinary_dividends: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 1a: Total ordinary dividends"
    )
    qualified_dividends: Decimal = Field(
        default=Decimal("0"), ge=0, description="Box 1b: Qualified dividends"
    )

    @model_validator(mode="after")
    def qualified_le_ordinary(self) -> "Income1099DIV":
        if self.qualified_dividends > self.ordinary_dividends:
            msg = "qualified_dividends cannot exceed ordinary_dividends"
            raise ValueError(msg)
        return self


class Income1099B(BaseModel):
    """1099-B — capital gains/losses (may be negative for losses)."""

    short_term_gains: Decimal = Field(
        default=Decimal("0"), description="Net short-term gains (may be negative)"
    )
    long_term_gains: Decimal = Field(
        default=Decimal("0"), description="Net long-term gains (may be negative)"
    )


class ItemizedDeductions(BaseModel):
    """Schedule A — itemized deductions."""

    medical: Decimal = Field(default=Decimal("0"), ge=0, description="Medical and dental expenses")
    state_and_local_taxes: Decimal = Field(
        default=Decimal("0"), ge=0, description="State/local taxes (SALT)"
    )
    mortgage_interest: Decimal = Field(
        default=Decimal("0"), ge=0, description="Home mortgage interest"
    )
    charitable: Decimal = Field(
        default=Decimal("0"), ge=0, description="Gifts to charity"
    )
    casualty: Decimal = Field(
        default=Decimal("0"), ge=0, description="Casualty and theft losses"
    )
    other: Decimal = Field(default=Decimal("0"), ge=0, description="Other itemized deductions")


class TaxCredits(BaseModel):
    """Tax credit inputs."""

    num_qualifying_children: int = Field(
        default=0, ge=0, description="Number of qualifying children for CTC"
    )


class TaxReturnInput(BaseModel):
    """Master input for the full tax-calculation pipeline — one tax return."""

    filing_status: FilingStatus
    is_over_65: bool = False
    is_blind: bool = False

    # Income sources (all optional — default to empty)
    w2s: list[W2Income] = Field(default_factory=list)
    income_1099_nec: list[Income1099NEC] = Field(default_factory=list)
    income_1099_int: list[Income1099INT] = Field(default_factory=list)
    income_1099_div: list[Income1099DIV] = Field(default_factory=list)
    income_1099_b: list[Income1099B] = Field(default_factory=list)

    # Deductions
    itemized_deductions: ItemizedDeductions | None = None
    force_standard_deduction: bool = False

    # Above-the-line deductions (besides auto-calculated SE deduction)
    hsa_deduction: Decimal = Field(default=Decimal("0"), ge=0)
    student_loan_interest: Decimal = Field(default=Decimal("0"), ge=0)
    educator_expenses: Decimal = Field(default=Decimal("0"), ge=0)
    ira_deduction: Decimal = Field(default=Decimal("0"), ge=0)
    self_employed_health_insurance: Decimal = Field(default=Decimal("0"), ge=0)

    # Credits
    credits: TaxCredits = Field(default_factory=TaxCredits)

    # Payments already made
    estimated_payments: Decimal = Field(default=Decimal("0"), ge=0)


# ---------------------------------------------------------------------------
# Workflow OUTPUT models
# ---------------------------------------------------------------------------


class IncomeResult(BaseModel):
    """Output of the income aggregation workflow."""

    wages: Decimal = Field(description="Total W-2 wages")
    self_employment_income: Decimal = Field(description="Total 1099-NEC compensation")
    interest_income: Decimal = Field(description="Total 1099-INT interest")
    ordinary_dividends: Decimal = Field(description="Total ordinary dividends")
    qualified_dividends: Decimal = Field(description="Total qualified dividends")
    short_term_gains: Decimal = Field(description="Net short-term capital gains/losses")
    long_term_gains: Decimal = Field(description="Net long-term capital gains/losses")
    total_gross_income: Decimal = Field(description="Sum of all income sources")
    net_investment_income: Decimal = Field(
        description="Interest + ordinary dividends + net gains (for NIIT)"
    )


class DeductionResult(BaseModel):
    """Output of the deduction workflow."""

    standard_deduction_amount: Decimal = Field(description="Standard deduction (if applicable)")
    itemized_total: Decimal = Field(description="Itemized deduction total (if applicable)")
    used_standard: bool = Field(description="True if standard deduction was used")
    deduction_amount: Decimal = Field(description="Final deduction amount applied")
    taxable_income: Decimal = Field(description="AGI minus deduction, floored at 0")
    ordinary_taxable_income: Decimal = Field(
        description="Taxable income minus preferential income"
    )
    preferential_qualified_dividends: Decimal = Field(
        description="Qualified dividends subject to preferential rates"
    )
    preferential_long_term_gains: Decimal = Field(
        description="Long-term gains subject to preferential rates"
    )


class TaxComputationResult(BaseModel):
    """Output of the tax computation workflow — Form 1040 Line 16+."""

    ordinary_tax: Decimal = Field(description="Tax on ordinary income (bracket tax)")
    qualified_dividend_tax: Decimal = Field(description="Tax on qualified dividends at 0/15/20%")
    capital_gains_tax: Decimal = Field(description="Tax on long-term gains at 0/15/20%")
    niit: Decimal = Field(description="Net Investment Income Tax (3.8%)")
    total_income_tax: Decimal = Field(description="Sum of all income tax components")


class CreditsResult(BaseModel):
    """Output of the credits workflow."""

    child_tax_credit: Decimal = Field(description="CTC amount (before refundable split)")
    nonrefundable_ctc_applied: Decimal = Field(description="Non-refundable CTC applied")
    refundable_ctc_applied: Decimal = Field(description="Additional (refundable) CTC applied")
    total_credits_applied: Decimal = Field(description="Total credits applied")
    tax_after_credits: Decimal = Field(description="Income tax after all credits")


class TaxSummary(BaseModel):
    """Final tax summary — the bottom line."""

    filing_status: FilingStatus
    total_income: Decimal
    agi: Decimal
    deduction_amount: Decimal
    taxable_income: Decimal

    # Tax breakdown
    ordinary_tax: Decimal
    qualified_dividend_tax: Decimal
    capital_gains_tax: Decimal
    niit: Decimal
    total_income_tax_before_credits: Decimal
    total_credits: Decimal
    income_tax_after_credits: Decimal
    total_fica: Decimal
    total_tax: Decimal  # income tax after credits + FICA

    # Rates
    effective_rate: Decimal = Field(description="total_tax / total_income")
    marginal_rate: Decimal = Field(description="Highest bracket rate reached")

    # Payments and balance
    total_withholding: Decimal
    estimated_payments: Decimal
    total_payments: Decimal
    refund_or_owed: Decimal = Field(
        description="Negative = refund, positive = amount owed"
    )


class FullTaxCalculationResult(BaseModel):
    """Complete result including all intermediate workflow outputs — for API transparency."""

    income: IncomeResult
    fica: "FicaResult"
    agi: "AGIResult"
    deductions: DeductionResult
    tax_computation: TaxComputationResult
    credits: CreditsResult
    summary: TaxSummary


# Avoid circular imports — use forward refs
from src.models.tax_output import AGIResult, FicaResult  # noqa: E402

FullTaxCalculationResult.model_rebuild()

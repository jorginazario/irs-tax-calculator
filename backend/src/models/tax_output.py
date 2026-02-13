"""Pydantic output models for IRS Tax Calculator."""

from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.filing_status import FilingStatus


class BracketDetail(BaseModel):
    """One bracket in the progressive tax breakdown."""

    rate: Decimal
    bracket_bottom: Decimal
    bracket_top: Decimal | None = None  # None = no cap (top bracket)
    taxable_in_bracket: Decimal
    tax_in_bracket: Decimal


class BracketTaxResult(BaseModel):
    """Result of progressive bracket-tax computation."""

    taxable_income: Decimal
    filing_status: FilingStatus
    total_tax: Decimal
    effective_rate: Decimal = Field(description="total_tax / taxable_income (0 if income is 0)")
    marginal_rate: Decimal = Field(description="Rate of the highest bracket reached")
    breakdown: list[BracketDetail]


class StandardDeductionResult(BaseModel):
    """Result of standard deduction lookup."""

    filing_status: FilingStatus
    base_amount: Decimal
    additional_amount: Decimal
    total_deduction: Decimal


class AGIResult(BaseModel):
    """Result of AGI calculation."""

    total_gross_income: Decimal
    total_above_line_deductions: Decimal
    agi: Decimal


class PreferentialRateDetail(BaseModel):
    """One bracket in the 0%/15%/20% preferential-rate breakdown.

    Shared by long-term capital gains and qualified dividends — IRC §1(h).
    """

    rate: Decimal
    bracket_bottom: Decimal
    bracket_top: Decimal | None = None  # None = no cap (top bracket)
    taxable_in_bracket: Decimal
    tax_in_bracket: Decimal


class CapitalGainsTaxResult(BaseModel):
    """Result of capital gains tax computation — IRC §1(h), Form 8949 / Schedule D."""

    short_term_gains: Decimal
    long_term_gains: Decimal
    long_term_tax: Decimal
    breakdown: list[PreferentialRateDetail]


class QualifiedDividendTaxResult(BaseModel):
    """Result of qualified dividend tax computation — IRC §1(h)."""

    qualified_dividends: Decimal
    tax: Decimal
    breakdown: list[PreferentialRateDetail]


class NiitResult(BaseModel):
    """Result of Net Investment Income Tax calculation — IRC §1411."""

    magi: Decimal
    threshold: Decimal
    excess_magi: Decimal
    net_investment_income: Decimal
    niit: Decimal


class FicaResult(BaseModel):
    """Result of FICA / self-employment tax calculation — IRC §§3101, 3111."""

    ss_tax: Decimal
    medicare_tax: Decimal
    additional_medicare_tax: Decimal
    se_tax: Decimal
    se_tax_deduction: Decimal
    total_fica: Decimal


class CreditResult(BaseModel):
    """Result of applying a tax credit."""

    tax_before: Decimal
    credit_applied: Decimal
    tax_after: Decimal

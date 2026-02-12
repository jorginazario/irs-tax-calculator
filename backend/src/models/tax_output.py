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

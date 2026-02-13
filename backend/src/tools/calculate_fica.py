"""FICA and self-employment tax calculation — IRC §§3101, 3111, 1401.

Covers:
  - Employee-side Social Security (6.2%, capped at $168,600 wage base)
  - Employee-side Medicare (1.45%)
  - Self-employment tax (SE taxable base = 92.35% of net SE income)
  - Additional Medicare Tax (0.9% on combined wages + SE income over threshold)
  - SE tax deduction (50% of total SE tax, above-the-line)
"""

from decimal import ROUND_HALF_UP, Decimal

from src.data.tax_year_2024 import (
    ADDITIONAL_MEDICARE_RATE,
    ADDITIONAL_MEDICARE_THRESHOLDS,
    MEDICARE_RATE_EMPLOYEE,
    SOCIAL_SECURITY_RATE_EMPLOYEE,
    SOCIAL_SECURITY_WAGE_BASE,
)
from src.models.filing_status import FilingStatus
from src.models.tax_output import FicaResult

TWO_PLACES = Decimal("0.01")

# 92.35% of net SE income is the taxable base — IRC §1402(a)
SE_TAXABLE_FRACTION = Decimal("0.9235")
SE_SS_RATE = Decimal("0.124")  # combined employee + employer SS (12.4%)
SE_MEDICARE_RATE = Decimal("0.029")  # combined employee + employer Medicare (2.9%)
SE_DEDUCTIBLE_FRACTION = Decimal("0.5")


def calculate_fica(
    w2_wages: Decimal,
    self_employment_income: Decimal,
    filing_status: FilingStatus,
) -> FicaResult:
    """Compute FICA (employee side) + self-employment tax.

    Schedule SE, Form 1040 Lines 4 and 14.
    """
    if w2_wages < 0:
        msg = "w2_wages must be >= 0"
        raise ValueError(msg)
    if self_employment_income < 0:
        msg = "self_employment_income must be >= 0"
        raise ValueError(msg)

    # --- W-2 Employee Side ---
    ss_wages = min(w2_wages, SOCIAL_SECURITY_WAGE_BASE)
    w2_ss_tax = (ss_wages * SOCIAL_SECURITY_RATE_EMPLOYEE).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )
    w2_medicare_tax = (w2_wages * MEDICARE_RATE_EMPLOYEE).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )

    # --- Self-Employment Tax ---
    se_tax = Decimal("0")
    se_ss_tax = Decimal("0")
    se_medicare_tax = Decimal("0")

    if self_employment_income > 0:
        # SE taxable base = 92.35% of net SE income — IRC §1402(a)
        se_base = (self_employment_income * SE_TAXABLE_FRACTION).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        # SS portion: capped at remaining wage base after W-2 wages
        remaining_ss_base = max(SOCIAL_SECURITY_WAGE_BASE - w2_wages, Decimal("0"))
        se_ss_wages = min(se_base, remaining_ss_base)
        se_ss_tax = (se_ss_wages * SE_SS_RATE).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        # Medicare portion: on full SE base (no cap)
        se_medicare_tax = (se_base * SE_MEDICARE_RATE).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        se_tax = se_ss_tax + se_medicare_tax

    # --- Additional Medicare Tax — IRC §3101(b)(2) ---
    # Applied to combined wages + SE base exceeding threshold
    # Note: for SE, the additional Medicare applies to SE income (not SE base)
    # but only the employee-equivalent portion triggers it. We use W-2 wages + SE base.
    additional_medicare_threshold = ADDITIONAL_MEDICARE_THRESHOLDS[filing_status.value]
    se_base_for_amt = Decimal("0")
    if self_employment_income > 0:
        se_base_for_amt = (self_employment_income * SE_TAXABLE_FRACTION).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )
    combined_for_medicare = w2_wages + se_base_for_amt
    excess_medicare = max(combined_for_medicare - additional_medicare_threshold, Decimal("0"))
    additional_medicare = (excess_medicare * ADDITIONAL_MEDICARE_RATE).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )

    # --- SE Tax Deduction (above-the-line) ---
    se_tax_deduction = (se_tax * SE_DEDUCTIBLE_FRACTION).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )

    # --- Totals ---
    total_fica = w2_ss_tax + w2_medicare_tax + se_tax + additional_medicare

    return FicaResult(
        ss_tax=(w2_ss_tax + se_ss_tax).quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        medicare_tax=(w2_medicare_tax + se_medicare_tax).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        additional_medicare_tax=additional_medicare,
        se_tax=se_tax,
        se_tax_deduction=se_tax_deduction,
        total_fica=total_fica.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

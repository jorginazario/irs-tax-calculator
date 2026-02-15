"""
IRS Tax Year 2024 — Federal tax constants.

Sources:
  - Rev. Proc. 2023-34 (inflation adjustments for 2024)
  - IRS Publication 17 (Your Federal Income Tax)
  - IRS Publication 501 (Dependents, Standard Deduction, and Filing Information)
  - IRC Section 1(j) (tax brackets), Section 1(h) (capital gains rates)
  - IRC Section 1411 (Net Investment Income Tax)
  - IRC Section 3101/3111 (FICA)
  - IRS Publication 596 (Earned Income Credit)
"""

from decimal import Decimal

# ---------------------------------------------------------------------------
# Filing statuses
# ---------------------------------------------------------------------------
# Canonical strings — match the FilingStatus enum in models/filing_status.py
SINGLE = "SINGLE"
MFJ = "MARRIED_FILING_JOINTLY"
MFS = "MARRIED_FILING_SEPARATELY"
HOH = "HEAD_OF_HOUSEHOLD"
QSS = "QUALIFYING_SURVIVING_SPOUSE"

# ---------------------------------------------------------------------------
# Federal income‑tax brackets — Rev. Proc. 2023-34, §1
# Each entry: (upper_bound, rate).  The last bracket has no upper bound (None).
# Brackets are cumulative — tax is computed progressively.
# ---------------------------------------------------------------------------
FEDERAL_BRACKETS: dict[str, list[tuple[Decimal | None, Decimal]]] = {
    SINGLE: [
        (Decimal("11600"), Decimal("0.10")),
        (Decimal("47150"), Decimal("0.12")),
        (Decimal("100525"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243725"), Decimal("0.32")),
        (Decimal("609350"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    MFJ: [
        (Decimal("23200"), Decimal("0.10")),
        (Decimal("94300"), Decimal("0.12")),
        (Decimal("201050"), Decimal("0.22")),
        (Decimal("383900"), Decimal("0.24")),
        (Decimal("487450"), Decimal("0.32")),
        (Decimal("731200"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    MFS: [
        (Decimal("11600"), Decimal("0.10")),
        (Decimal("47150"), Decimal("0.12")),
        (Decimal("100525"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243725"), Decimal("0.32")),
        (Decimal("365600"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    HOH: [
        (Decimal("16550"), Decimal("0.10")),
        (Decimal("63100"), Decimal("0.12")),
        (Decimal("100500"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243700"), Decimal("0.32")),
        (Decimal("609350"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    QSS: [
        (Decimal("23200"), Decimal("0.10")),
        (Decimal("94300"), Decimal("0.12")),
        (Decimal("201050"), Decimal("0.22")),
        (Decimal("383900"), Decimal("0.24")),
        (Decimal("487450"), Decimal("0.32")),
        (Decimal("731200"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
}

# ---------------------------------------------------------------------------
# Standard deduction — Rev. Proc. 2023-34, §3 / IRS Pub 501
# ---------------------------------------------------------------------------
STANDARD_DEDUCTION: dict[str, Decimal] = {
    SINGLE: Decimal("14600"),
    MFJ: Decimal("29200"),
    MFS: Decimal("14600"),
    HOH: Decimal("21900"),
    QSS: Decimal("29200"),
}

# Additional standard deduction for age ≥ 65 or blindness (per condition)
# Single / HoH: $1,950 per qualifying condition
# MFJ / MFS / QSS: $1,550 per qualifying condition
# Rev. Proc. 2023-34, §3.01
ADDITIONAL_DEDUCTION_SINGLE_HOH = Decimal("1950")
ADDITIONAL_DEDUCTION_MARRIED = Decimal("1550")

# ---------------------------------------------------------------------------
# Long-term capital gains & qualified dividend rate thresholds — IRC §1(h)
# Rev. Proc. 2023-34, §1.  Rates: 0% / 15% / 20%
# Thresholds represent the *upper bound* of taxable income for each rate.
# ---------------------------------------------------------------------------
CAPITAL_GAINS_THRESHOLDS: dict[str, list[tuple[Decimal | None, Decimal]]] = {
    SINGLE: [
        (Decimal("47025"), Decimal("0.00")),
        (Decimal("518900"), Decimal("0.15")),
        (None, Decimal("0.20")),
    ],
    MFJ: [
        (Decimal("94050"), Decimal("0.00")),
        (Decimal("583750"), Decimal("0.15")),
        (None, Decimal("0.20")),
    ],
    MFS: [
        (Decimal("47025"), Decimal("0.00")),
        (Decimal("291850"), Decimal("0.15")),
        (None, Decimal("0.20")),
    ],
    HOH: [
        (Decimal("63000"), Decimal("0.00")),
        (Decimal("551350"), Decimal("0.15")),
        (None, Decimal("0.20")),
    ],
    QSS: [
        (Decimal("94050"), Decimal("0.00")),
        (Decimal("583750"), Decimal("0.15")),
        (None, Decimal("0.20")),
    ],
}

# ---------------------------------------------------------------------------
# Net Investment Income Tax (NIIT) — IRC §1411
# 3.8% on lesser of net investment income or MAGI exceeding threshold
# ---------------------------------------------------------------------------
NIIT_RATE = Decimal("0.038")

NIIT_THRESHOLDS: dict[str, Decimal] = {
    SINGLE: Decimal("200000"),
    MFJ: Decimal("250000"),
    MFS: Decimal("125000"),
    HOH: Decimal("200000"),
    QSS: Decimal("250000"),
}

# ---------------------------------------------------------------------------
# FICA — IRC §§3101, 3111; SSA 2024 fact sheet
# ---------------------------------------------------------------------------
SOCIAL_SECURITY_WAGE_BASE = Decimal("168600")
SOCIAL_SECURITY_RATE_EMPLOYEE = Decimal("0.062")   # 6.2%
SOCIAL_SECURITY_RATE_EMPLOYER = Decimal("0.062")
MEDICARE_RATE_EMPLOYEE = Decimal("0.0145")          # 1.45%
MEDICARE_RATE_EMPLOYER = Decimal("0.0145")

# Additional Medicare Tax — IRC §3101(b)(2)
ADDITIONAL_MEDICARE_RATE = Decimal("0.009")         # 0.9%
ADDITIONAL_MEDICARE_THRESHOLDS: dict[str, Decimal] = {
    SINGLE: Decimal("200000"),
    MFJ: Decimal("250000"),
    MFS: Decimal("125000"),
    HOH: Decimal("200000"),
    QSS: Decimal("250000"),
}

# Self‑employment tax rate (combined employee + employer)
SE_TAX_RATE = Decimal("0.153")  # 15.3%
SE_DEDUCTIBLE_FRACTION = Decimal("0.5")  # 50% of SE tax is above-the-line deduction

# ---------------------------------------------------------------------------
# Child Tax Credit — IRC §24, Rev. Proc. 2023-34
# ---------------------------------------------------------------------------
CHILD_TAX_CREDIT_MAX = Decimal("2000")
CHILD_TAX_CREDIT_REFUNDABLE = Decimal("1700")  # Additional Child Tax Credit
CHILD_TAX_CREDIT_PHASEOUT: dict[str, Decimal] = {
    SINGLE: Decimal("200000"),
    MFJ: Decimal("400000"),
    MFS: Decimal("200000"),
    HOH: Decimal("200000"),
    QSS: Decimal("400000"),
}
CHILD_TAX_CREDIT_PHASEOUT_RATE = Decimal("0.05")  # $50 per $1,000 over threshold

# ---------------------------------------------------------------------------
# Earned Income Tax Credit — IRS Pub 596, Rev. Proc. 2023-34
# Max credit and AGI limits for tax year 2024 (single / HoH filers)
# MFJ limits are higher by the "MFJ add-on" amount
# ---------------------------------------------------------------------------
EITC_MAX_CREDIT: dict[int, Decimal] = {
    0: Decimal("632"),
    1: Decimal("4213"),
    2: Decimal("6960"),
    3: Decimal("7830"),
}

EITC_AGI_LIMIT_SINGLE: dict[int, Decimal] = {
    0: Decimal("18591"),
    1: Decimal("49084"),
    2: Decimal("55768"),
    3: Decimal("59899"),
}

EITC_AGI_LIMIT_MFJ: dict[int, Decimal] = {
    0: Decimal("25511"),
    1: Decimal("56004"),
    2: Decimal("62688"),
    3: Decimal("66819"),
}

# Max investment income to qualify for EITC
EITC_MAX_INVESTMENT_INCOME = Decimal("11600")

"""Deduction workflow — standard vs. itemized, income partitioning.

Determines the deduction method, computes taxable income, and partitions it
into ordinary vs. preferential (qualified dividends + long-term gains) portions
for correct tax computation under IRC §1(h).
"""

from decimal import ROUND_HALF_UP, Decimal

from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import DeductionResult, IncomeResult, TaxReturnInput
from src.tools.lookup_standard_deduction import lookup_standard_deduction

TWO_PLACES = Decimal("0.01")

# SALT cap — Tax Cuts and Jobs Act §11042, IRC §164(b)(6)
SALT_CAP_DEFAULT = Decimal("10000")
SALT_CAP_MFS = Decimal("5000")

# Medical expense floor — IRC §213(a): deduct only the amount exceeding 7.5% of AGI
MEDICAL_AGI_THRESHOLD = Decimal("0.075")


def _compute_itemized_total(
    tax_return: TaxReturnInput,
    agi: Decimal,
) -> Decimal:
    """Compute the itemized deduction total with SALT cap and medical threshold."""
    if tax_return.itemized_deductions is None:
        return Decimal("0")

    item = tax_return.itemized_deductions

    # Medical: only amount exceeding 7.5% of AGI — IRC §213(a)
    medical_floor = (agi * MEDICAL_AGI_THRESHOLD).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )
    medical_deduction = max(item.medical - medical_floor, Decimal("0"))

    # SALT: capped at $10,000 ($5,000 MFS) — IRC §164(b)(6)
    salt_cap = (
        SALT_CAP_MFS
        if tax_return.filing_status == FilingStatus.MARRIED_FILING_SEPARATELY
        else SALT_CAP_DEFAULT
    )
    salt_deduction = min(item.state_and_local_taxes, salt_cap)

    total = (
        medical_deduction
        + salt_deduction
        + item.mortgage_interest
        + item.charitable
        + item.casualty
        + item.other
    )

    return total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def run_deduction_workflow(
    tax_return: TaxReturnInput,
    income: IncomeResult,
    agi_result: AGIResult,
) -> DeductionResult:
    """Determine deduction method and partition taxable income.

    Form 1040 Lines 12-15.

    Critical: taxable income is split into ordinary and preferential portions.
    Qualified dividends and net long-term capital gains receive preferential
    0%/15%/20% rates under IRC §1(h). The ordinary portion is taxed at
    regular bracket rates.
    """
    # Standard deduction
    std_result = lookup_standard_deduction(
        filing_status=tax_return.filing_status,
        is_blind=tax_return.is_blind,
        is_over_65=tax_return.is_over_65,
    )
    standard_amount = std_result.total_deduction

    # Itemized deduction
    itemized_total = _compute_itemized_total(tax_return, agi_result.agi)

    # Choose higher unless forced
    if tax_return.force_standard_deduction:
        used_standard = True
        deduction_amount = standard_amount
    elif tax_return.itemized_deductions is not None and itemized_total > standard_amount:
        used_standard = False
        deduction_amount = itemized_total
    else:
        used_standard = True
        deduction_amount = standard_amount

    # Taxable income — Form 1040 Line 15
    taxable_income = max(agi_result.agi - deduction_amount, Decimal("0"))

    # Partition into ordinary vs. preferential — IRC §1(h)
    # Preferential = qualified dividends + net long-term capital gains (if positive)
    pref_qualified_divs = income.qualified_dividends
    pref_ltcg = max(income.long_term_gains, Decimal("0"))
    total_preferential = pref_qualified_divs + pref_ltcg

    # If preferential exceeds taxable income, proportionally cap each component
    if total_preferential > taxable_income and total_preferential > Decimal("0"):
        ratio = taxable_income / total_preferential
        pref_qualified_divs = (pref_qualified_divs * ratio).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )
        pref_ltcg = (taxable_income - pref_qualified_divs).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

    ordinary_taxable = max(
        taxable_income - pref_qualified_divs - pref_ltcg, Decimal("0")
    )

    return DeductionResult(
        standard_deduction_amount=standard_amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        itemized_total=itemized_total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        used_standard=used_standard,
        deduction_amount=deduction_amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        taxable_income=taxable_income.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        ordinary_taxable_income=ordinary_taxable.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        preferential_qualified_dividends=pref_qualified_divs.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        preferential_long_term_gains=pref_ltcg.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

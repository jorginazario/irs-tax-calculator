"""Credits workflow — apply tax credits to reduce liability.

Currently implements Child Tax Credit (IRC §24) with phaseout and
refundable Additional Child Tax Credit.
"""

from decimal import ROUND_HALF_UP, Decimal

from src.data.tax_year_2024 import (
    CHILD_TAX_CREDIT_MAX,
    CHILD_TAX_CREDIT_PHASEOUT,
    CHILD_TAX_CREDIT_PHASEOUT_RATE,
    CHILD_TAX_CREDIT_REFUNDABLE,
)
from src.models.filing_status import FilingStatus
from src.models.tax_output import AGIResult
from src.models.workflow_models import CreditsResult, TaxComputationResult, TaxReturnInput
from src.tools.apply_credit import apply_credit

TWO_PLACES = Decimal("0.01")


def _calculate_child_tax_credit(
    num_children: int,
    agi: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """Compute the total CTC before splitting into refundable/non-refundable.

    IRC §24: $2,000 per qualifying child, phased out by $50 per $1,000
    of AGI exceeding the threshold.
    """
    if num_children <= 0:
        return Decimal("0")

    max_credit = CHILD_TAX_CREDIT_MAX * num_children
    threshold = CHILD_TAX_CREDIT_PHASEOUT[filing_status.value]
    excess = max(agi - threshold, Decimal("0"))

    # Phaseout: $50 reduction per $1,000 of excess (round up to next $1,000)
    # Equivalent to: ceil(excess / 1000) * 50 = excess * 0.05 rounded up
    phaseout_units = (excess / Decimal("1000")).to_integral_value(rounding=ROUND_HALF_UP)
    phaseout = (phaseout_units * Decimal("50")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return max(max_credit - phaseout, Decimal("0"))


def run_credits_workflow(
    tax_return: TaxReturnInput,
    agi_result: AGIResult,
    tax_computation: TaxComputationResult,
) -> CreditsResult:
    """Apply all eligible tax credits — Form 1040 Lines 19-32.

    Child Tax Credit (IRC §24):
    - Non-refundable portion: up to full CTC, limited by tax liability
    - Refundable portion (ACTC): up to $1,700/child, applied after non-refundable
    """
    total_tax = tax_computation.total_income_tax

    # Child Tax Credit
    ctc_total = _calculate_child_tax_credit(
        num_children=tax_return.credits.num_qualifying_children,
        agi=agi_result.agi,
        filing_status=tax_return.filing_status,
    )

    # Split into non-refundable and refundable portions
    # Non-refundable: limited by tax liability (cannot reduce below $0)
    nonrefundable_result = apply_credit(
        tax_owed=total_tax,
        credit_amount=ctc_total,
        is_refundable=False,
    )
    nonrefundable_applied = nonrefundable_result.credit_applied
    tax_after_nonrefundable = nonrefundable_result.tax_after

    # Refundable (Additional Child Tax Credit): up to $1,700 per child
    # Only the unused portion of CTC (up to the refundable cap) becomes refundable
    unused_ctc = ctc_total - nonrefundable_applied
    refundable_cap = CHILD_TAX_CREDIT_REFUNDABLE * tax_return.credits.num_qualifying_children
    refundable_amount = min(unused_ctc, refundable_cap)

    refundable_result = apply_credit(
        tax_owed=tax_after_nonrefundable,
        credit_amount=refundable_amount,
        is_refundable=True,
    )
    refundable_applied = refundable_result.credit_applied

    total_credits = nonrefundable_applied + refundable_applied
    tax_after = refundable_result.tax_after

    return CreditsResult(
        child_tax_credit=ctc_total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        nonrefundable_ctc_applied=nonrefundable_applied.quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        ),
        refundable_ctc_applied=refundable_applied.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        total_credits_applied=total_credits.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        tax_after_credits=tax_after.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    )

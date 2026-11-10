"""Tax credit calculations.

Simplifications: this module implements the nonrefundable Child Tax Credit
phase-out only. It does not compute the refundable Additional Child Tax
Credit, the Earned Income Credit, or any other credit. See the README
"Limitations" section.
"""

from __future__ import annotations

from decimal import ROUND_CEILING, Decimal

from taxestimator.brackets import CTC_PHASEOUT_THRESHOLD
from taxestimator.models import FilingStatus

CTC_PER_CHILD = Decimal(2000)
CTC_PHASEOUT_STEP = Decimal(50)
CTC_PHASEOUT_INCREMENT = Decimal(1000)


def child_tax_credit(
    num_qualifying_children: int, agi: Decimal, filing_status: FilingStatus
) -> Decimal:
    """Nonrefundable Child Tax Credit after the AGI-based phase-out.

    The credit is reduced by $50 for each $1,000 (or fraction thereof) that
    AGI exceeds the filing-status threshold.
    """
    if num_qualifying_children <= 0:
        return Decimal(0)

    credit = CTC_PER_CHILD * num_qualifying_children
    threshold = CTC_PHASEOUT_THRESHOLD[filing_status]

    if agi <= threshold:
        return credit

    excess = agi - threshold
    increments = (excess / CTC_PHASEOUT_INCREMENT).to_integral_value(rounding=ROUND_CEILING)
    reduction = increments * CTC_PHASEOUT_STEP
    return max(Decimal(0), credit - reduction)

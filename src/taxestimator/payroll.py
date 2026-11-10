"""Self-employment (SECA) tax calculation.

Simplifications: this module does not account for the additional 0.9%
Medicare surtax that applies above $200k/$250k thresholds, nor for partial
years or multiple employers reducing the Social Security wage base already
used elsewhere. See the README "Limitations" section.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from taxestimator.brackets import SS_WAGE_BASE
from taxestimator.models import SelfEmploymentTaxResult

NET_EARNINGS_FACTOR = Decimal("0.9235")  # IRC 1402(a) 92.35% adjustment
SOCIAL_SECURITY_RATE = Decimal("0.124")  # combined employer+employee 6.2% x2
MEDICARE_RATE = Decimal("0.029")  # combined employer+employee 1.45% x2

CENTS = Decimal("0.01")


def self_employment_tax(net_profit: Decimal, tax_year: int) -> SelfEmploymentTaxResult:
    """Compute SECA tax owed and the portion deductible when figuring AGI."""
    if net_profit <= 0:
        return SelfEmploymentTaxResult(se_tax=Decimal(0), deductible_half=Decimal(0))

    net_earnings = net_profit * NET_EARNINGS_FACTOR
    wage_base = SS_WAGE_BASE.get(tax_year, SS_WAGE_BASE[max(SS_WAGE_BASE)])

    social_security_tax = min(net_earnings, wage_base) * SOCIAL_SECURITY_RATE
    medicare_tax = net_earnings * MEDICARE_RATE
    se_tax = (social_security_tax + medicare_tax).quantize(CENTS, rounding=ROUND_HALF_UP)
    deductible_half = (se_tax / 2).quantize(CENTS, rounding=ROUND_HALF_UP)

    return SelfEmploymentTaxResult(se_tax=se_tax, deductible_half=deductible_half)

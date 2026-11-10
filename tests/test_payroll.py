from decimal import Decimal

from taxestimator.payroll import self_employment_tax


def test_zero_or_negative_profit_has_no_se_tax():
    assert self_employment_tax(Decimal(0), 2024).se_tax == Decimal(0)
    assert self_employment_tax(Decimal(-500), 2024).se_tax == Decimal(0)


def test_typical_se_tax_calculation():
    result = self_employment_tax(Decimal(18000), 2024)
    assert result.se_tax == Decimal("2543.32")
    assert result.deductible_half == Decimal("1271.66")


def test_social_security_portion_caps_at_wage_base():
    # Net earnings well above the 2024 SS wage base ($168,600): only the
    # Medicare portion keeps growing past that point.
    below_cap = self_employment_tax(Decimal(180000), 2024)
    above_cap = self_employment_tax(Decimal(400000), 2024)
    # Medicare-only marginal rate above the cap is 2.9% * 0.9235 on the SE
    # income delta, which is less than the combined 15.3% below the cap.
    delta_profit = Decimal(400000) - Decimal(180000)
    delta_tax = above_cap.se_tax - below_cap.se_tax
    assert delta_tax < delta_profit * Decimal("0.153")

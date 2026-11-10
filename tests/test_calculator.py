from decimal import Decimal

from taxestimator.brackets import ORDINARY_BRACKETS
from taxestimator.calculator import bracket_tax, compute, marginal_rate_for
from taxestimator.models import FilingStatus, TaxpayerProfile


def profile(**overrides):
    defaults = {"tax_year": 2024, "filing_status": FilingStatus.SINGLE}
    defaults.update(overrides)
    return TaxpayerProfile(**defaults)


def test_bracket_tax_at_exact_first_threshold():
    brackets = ORDINARY_BRACKETS[2024][FilingStatus.SINGLE]
    assert bracket_tax(Decimal(0), Decimal(11600), brackets) == Decimal("1160.00")


def test_bracket_tax_zero_amount_is_zero():
    brackets = ORDINARY_BRACKETS[2024][FilingStatus.SINGLE]
    assert bracket_tax(Decimal(0), Decimal(0), brackets) == Decimal(0)


def test_wage_earner_single_standard_deduction():
    result = compute(profile(wages=Decimal(85000)))
    assert result.adjusted_gross_income == Decimal("85000.00")
    assert result.taxable_income == Decimal("70400.00")
    assert result.total_tax == Decimal("10541.00")
    assert result.marginal_rate == Decimal("0.22")
    assert result.effective_rate == Decimal("0.1240")
    assert result.balance_due == Decimal("10541.00")  # no withholding -> owes it all


def test_long_term_gains_fully_within_zero_percent_bracket():
    result = compute(
        profile(ordinary_dividends=Decimal(50000), qualified_dividends=Decimal(50000))
    )
    # taxable income (35,400) sits entirely below the 2024 single 0% LTCG
    # threshold ($47,025), so an otherwise-nontrivial income owes no tax.
    assert result.taxable_income == Decimal("35400.00")
    assert result.preferential_income == Decimal("35400.00")
    assert result.ordinary_taxable_income == Decimal("0.00")
    assert result.total_tax == Decimal("0.00")


def test_long_term_gains_stack_on_top_of_ordinary_income():
    result = compute(profile(wages=Decimal(40000), long_term_capital_gains=Decimal(50000)))
    assert result.taxable_income == Decimal("75400.00")
    assert result.ordinary_taxable_income == Decimal("25400.00")
    assert result.preferential_income == Decimal("50000.00")
    assert result.ordinary_tax == Decimal("2816.00")
    assert result.preferential_tax == Decimal("4256.25")
    assert result.total_tax == Decimal("7072.25")


def test_child_tax_credit_reduces_tax_below_phaseout():
    with_child = compute(profile(wages=Decimal(85000), qualifying_children=1))
    without_child = compute(profile(wages=Decimal(85000)))
    assert without_child.total_tax - with_child.total_tax == Decimal("2000.00")


def test_child_tax_credit_phases_out_above_threshold():
    # Single filer threshold is $200,000; $210,000 AGI is $10,000 over,
    # which is 10 "or-fraction-thereof" $1,000 increments * $50 = $500 cut
    # from the $2,000 credit, leaving $1,500.
    result = compute(profile(wages=Decimal(210000), qualifying_children=1))
    no_kids = compute(profile(wages=Decimal(210000)))
    assert no_kids.ordinary_tax - result.ordinary_tax == Decimal(0)  # sanity: same bracket math
    assert no_kids.total_tax - result.total_tax == Decimal("1500.00")


def test_self_employment_income_adds_se_tax_and_half_deduction():
    result = compute(profile(self_employment_income=Decimal(18000)))
    # 18000 * 0.9235 = 16623; SE tax = 16623 * 0.153 = 2543.319 -> 2543.32
    assert result.self_employment_tax == Decimal("2543.32")
    assert result.adjustments == Decimal("1271.66")


def test_zero_income_owes_zero_tax():
    result = compute(profile())
    assert result.total_tax == Decimal("0.00")
    assert result.taxable_income == Decimal("0.00")


def test_withholding_creates_a_refund():
    result = compute(profile(wages=Decimal(20000), withholding=Decimal(5000)))
    assert result.balance_due < 0
    assert -result.balance_due == result.payments - result.total_tax


def test_marginal_rate_for_top_bracket_is_open_ended():
    brackets = ORDINARY_BRACKETS[2024][FilingStatus.SINGLE]
    assert marginal_rate_for(Decimal(10000000), brackets) == Decimal("0.37")

from decimal import Decimal

from taxestimator.credits import child_tax_credit
from taxestimator.models import FilingStatus


def test_no_children_no_credit():
    assert child_tax_credit(0, Decimal(50000), FilingStatus.SINGLE) == Decimal(0)


def test_full_credit_below_threshold():
    assert child_tax_credit(2, Decimal(100000), FilingStatus.SINGLE) == Decimal(4000)


def test_full_credit_at_exact_threshold():
    assert child_tax_credit(1, Decimal(200000), FilingStatus.SINGLE) == Decimal(2000)


def test_partial_dollar_over_threshold_still_costs_a_full_increment():
    # $1 over triggers the first $50 reduction, since any fraction of a
    # $1,000 increment counts as a full increment.
    result = child_tax_credit(1, Decimal("200000.01"), FilingStatus.SINGLE)
    assert result == Decimal(1950)


def test_credit_cannot_go_negative():
    result = child_tax_credit(1, Decimal(1000000), FilingStatus.SINGLE)
    assert result == Decimal(0)


def test_married_jointly_has_a_higher_threshold():
    single_result = child_tax_credit(1, Decimal(250000), FilingStatus.SINGLE)
    mfj_result = child_tax_credit(1, Decimal(250000), FilingStatus.MARRIED_JOINTLY)
    assert mfj_result == Decimal(2000)
    assert single_result < mfj_result

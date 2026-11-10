from decimal import Decimal

import pytest

from taxestimator.brackets import (
    LTCG_BRACKETS,
    ORDINARY_BRACKETS,
    STANDARD_DEDUCTION,
    SUPPORTED_YEARS,
)
from taxestimator.models import FilingStatus


@pytest.mark.parametrize("year", SUPPORTED_YEARS)
@pytest.mark.parametrize("status", list(FilingStatus))
def test_ordinary_brackets_strictly_increasing(year, status):
    brackets = ORDINARY_BRACKETS[year][status]
    thresholds = [upper for upper, _rate in brackets if upper is not None]
    assert thresholds == sorted(set(thresholds))
    assert brackets[-1][0] is None, "last bracket must be open-ended"
    rates = [rate for _upper, rate in brackets]
    assert rates == sorted(rates), "rates must increase monotonically"


@pytest.mark.parametrize("year", SUPPORTED_YEARS)
@pytest.mark.parametrize("status", list(FilingStatus))
def test_ltcg_brackets_have_three_tiers(year, status):
    brackets = LTCG_BRACKETS[year][status]
    assert [rate for _upper, rate in brackets] == [Decimal(0), Decimal("0.15"), Decimal("0.20")]


@pytest.mark.parametrize("year", SUPPORTED_YEARS)
def test_married_jointly_standard_deduction_is_roughly_double_single(year):
    single = STANDARD_DEDUCTION[year][FilingStatus.SINGLE]
    mfj = STANDARD_DEDUCTION[year][FilingStatus.MARRIED_JOINTLY]
    assert mfj == single * 2

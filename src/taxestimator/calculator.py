"""Core tax calculation engine.

The overall approach mirrors the structure of a real Form 1040:

1. Sum all income sources -> total income.
2. Subtract above-the-line adjustments (retirement contributions, half of
   SE tax) -> Adjusted Gross Income (AGI).
3. Subtract the larger of the standard deduction or itemized deductions
   -> taxable income.
4. Split taxable income into an "ordinary" portion and a "preferential"
   portion (qualified dividends + net long-term capital gains). The
   preferential portion is taxed using the qualified dividends/LTCG rate
   schedule, but -- critically -- it is taxed as if it sits *on top of*
   the ordinary income (the "stacking" rule from the IRS Qualified
   Dividends and Capital Gain Tax Worksheet).
5. Add self-employment tax (computed on gross self-employment income, not
   reduced by deductions) to get total tax before payments.
6. Apply nonrefundable credits (currently just the Child Tax Credit).
7. Compare total tax to withholding + estimated payments to get a
   refund/balance-due figure.

See the README "Limitations" section for everything this intentionally
does not model (AMT, state taxes, NIIT, the Additional Medicare surtax,
phase-outs other than the CTC, etc).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from taxestimator.brackets import LTCG_BRACKETS, ORDINARY_BRACKETS, STANDARD_DEDUCTION, BracketTable
from taxestimator.credits import child_tax_credit
from taxestimator.models import TaxpayerProfile, TaxResult
from taxestimator.payroll import self_employment_tax

CENTS = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def bracket_tax(floor: Decimal, amount: Decimal, brackets: BracketTable) -> Decimal:
    """Tax owed on ``amount`` of income that sits on top of ``floor`` of
    other income, under a progressive ``brackets`` schedule.

    Calling with ``floor=0`` computes ordinary progressive tax. Calling with
    a nonzero ``floor`` implements the IRS "stacking" rule used for
    qualified dividends / long-term capital gains, which are taxed as if
    they were the top slice of total taxable income.
    """
    if amount <= 0:
        return Decimal(0)

    ceiling = floor + amount
    tax = Decimal(0)
    lower = Decimal(0)

    for upper, rate in brackets:
        bracket_upper = ceiling if upper is None else upper
        overlap_lower = max(lower, floor)
        overlap_upper = min(bracket_upper, ceiling)
        if overlap_upper > overlap_lower:
            tax += (overlap_upper - overlap_lower) * rate
        if upper is None or upper >= ceiling:
            break
        lower = upper

    return tax


def marginal_rate_for(taxable_income: Decimal, brackets: BracketTable) -> Decimal:
    """The rate that applies to the next dollar of ordinary taxable income."""
    for upper, rate in brackets:
        if upper is None or taxable_income <= upper:
            return rate
    return brackets[-1][1]


def compute(profile: TaxpayerProfile) -> TaxResult:
    year = profile.tax_year
    status = profile.filing_status

    if year not in ORDINARY_BRACKETS:
        raise ValueError(
            f"tax_year {year} is not supported (supported years: "
            f"{sorted(ORDINARY_BRACKETS)})"
        )

    se_result = self_employment_tax(profile.self_employment_income, year)

    total_income = (
        profile.wages
        + profile.interest_income
        + profile.ordinary_dividends
        + profile.short_term_capital_gains
        + profile.long_term_capital_gains
        + profile.self_employment_income
        + profile.other_income
    )

    adjustments = profile.pretax_retirement_contributions + se_result.deductible_half
    agi = max(Decimal(0), total_income - adjustments)

    deduction = max(STANDARD_DEDUCTION[year][status], profile.itemized_deductions)
    taxable_income = max(Decimal(0), agi - deduction)

    preferential_income = min(
        taxable_income,
        max(Decimal(0), profile.qualified_dividends + profile.long_term_capital_gains),
    )
    ordinary_taxable_income = taxable_income - preferential_income

    ordinary_tax = bracket_tax(Decimal(0), ordinary_taxable_income, ORDINARY_BRACKETS[year][status])
    preferential_tax = bracket_tax(
        ordinary_taxable_income, preferential_income, LTCG_BRACKETS[year][status]
    )

    tax_before_credits = ordinary_tax + preferential_tax
    credit = child_tax_credit(profile.qualifying_children, agi, status)

    total_tax = max(Decimal(0), tax_before_credits - credit) + se_result.se_tax

    marginal_rate = marginal_rate_for(taxable_income, ORDINARY_BRACKETS[year][status])
    effective_rate = (total_tax / total_income) if total_income > 0 else Decimal(0)

    payments = profile.withholding + profile.estimated_payments
    balance_due = total_tax - payments

    return TaxResult(
        tax_year=year,
        filing_status=status,
        total_income=_money(total_income),
        adjustments=_money(adjustments),
        adjusted_gross_income=_money(agi),
        deduction_used=_money(deduction),
        taxable_income=_money(taxable_income),
        ordinary_taxable_income=_money(ordinary_taxable_income),
        preferential_income=_money(preferential_income),
        ordinary_tax=_money(ordinary_tax),
        preferential_tax=_money(preferential_tax),
        self_employment_tax=_money(se_result.se_tax),
        child_tax_credit=_money(credit),
        total_tax=_money(total_tax),
        marginal_rate=marginal_rate,
        effective_rate=effective_rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        payments=_money(payments),
        balance_due=_money(balance_due),
    )

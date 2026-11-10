"""Pydantic data models for taxpayer input and computed results.

Money fields use ``Decimal`` rather than ``float`` throughout this project.
Binary floating point cannot represent most base-10 currency amounts exactly
(e.g. ``0.1 + 0.2 != 0.3``), which is unacceptable when the numbers represent
tax liability. ``Decimal`` trades a little performance for exact, predictable
arithmetic -- the right tradeoff for financial software.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_JOINTLY = "married_jointly"
    MARRIED_SEPARATELY = "married_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


class TaxpayerProfile(BaseModel):
    """All inputs needed to estimate one taxpayer's federal income tax for one year."""

    tax_year: int = Field(..., description="Tax year to compute against, e.g. 2024")
    filing_status: FilingStatus

    wages: Decimal = Field(Decimal(0), ge=0, description="Form W-2 box 1 wages")
    interest_income: Decimal = Field(Decimal(0), ge=0, description="Taxable interest")
    ordinary_dividends: Decimal = Field(
        Decimal(0), ge=0, description="Total ordinary dividends (box 1a of 1099-DIV)"
    )
    qualified_dividends: Decimal = Field(
        Decimal(0),
        ge=0,
        description="Qualified dividends (box 1b); must be <= ordinary_dividends",
    )
    short_term_capital_gains: Decimal = Field(Decimal(0))
    long_term_capital_gains: Decimal = Field(Decimal(0))
    self_employment_income: Decimal = Field(
        Decimal(0), ge=0, description="Net profit from self-employment (Schedule C)"
    )
    other_income: Decimal = Field(Decimal(0))

    pretax_retirement_contributions: Decimal = Field(
        Decimal(0), ge=0, description="e.g. traditional 401(k) / IRA contributions"
    )
    itemized_deductions: Decimal = Field(
        Decimal(0), ge=0, description="Total itemized deductions, if greater than standard"
    )
    qualifying_children: int = Field(0, ge=0, description="Children qualifying for the CTC")

    withholding: Decimal = Field(Decimal(0), ge=0, description="Federal tax withheld")
    estimated_payments: Decimal = Field(Decimal(0), ge=0)

    @field_validator("qualified_dividends")
    @classmethod
    def _qualified_within_ordinary(cls, v: Decimal, info) -> Decimal:
        ordinary = info.data.get("ordinary_dividends", Decimal(0))
        if v > ordinary:
            raise ValueError("qualified_dividends cannot exceed ordinary_dividends")
        return v

    model_config = {"frozen": True}


class SelfEmploymentTaxResult(BaseModel):
    se_tax: Decimal
    deductible_half: Decimal


class TaxResult(BaseModel):
    """Computed output of :func:`taxestimator.calculator.compute`."""

    tax_year: int
    filing_status: FilingStatus

    total_income: Decimal
    adjustments: Decimal
    adjusted_gross_income: Decimal
    deduction_used: Decimal
    taxable_income: Decimal

    ordinary_taxable_income: Decimal
    preferential_income: Decimal
    ordinary_tax: Decimal
    preferential_tax: Decimal

    self_employment_tax: Decimal
    child_tax_credit: Decimal

    total_tax: Decimal
    marginal_rate: Decimal
    effective_rate: Decimal

    payments: Decimal
    balance_due: Decimal  # positive = owe the IRS, negative = refund

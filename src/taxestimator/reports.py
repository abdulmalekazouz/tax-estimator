"""Rendering TaxResult objects as human-readable text, JSON, or CSV."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable

from tabulate import tabulate

from taxestimator.models import TaxResult

_ROWS = [
    ("Total income", "total_income"),
    ("Adjustments", "adjustments"),
    ("Adjusted gross income (AGI)", "adjusted_gross_income"),
    ("Deduction used", "deduction_used"),
    ("Taxable income", "taxable_income"),
    ("  - ordinary portion", "ordinary_taxable_income"),
    ("  - preferential portion (QD/LTCG)", "preferential_income"),
    ("Tax on ordinary income", "ordinary_tax"),
    ("Tax on preferential income", "preferential_tax"),
    ("Self-employment tax", "self_employment_tax"),
    ("Child Tax Credit", "child_tax_credit"),
    ("Total tax", "total_tax"),
    ("Payments & withholding", "payments"),
    ("Balance due (negative = refund)", "balance_due"),
]


def render_text(result: TaxResult) -> str:
    header = f"Tax Estimate -- {result.tax_year} -- {result.filing_status.value}"
    rows = [(label, f"${getattr(result, field):,.2f}") for label, field in _ROWS]
    rows.append(("Marginal rate", f"{result.marginal_rate * 100:.1f}%"))
    rows.append(("Effective rate", f"{result.effective_rate * 100:.2f}%"))
    table = tabulate(rows, headers=["Line item", "Amount"], tablefmt="simple")
    return f"{header}\n{'=' * len(header)}\n{table}"


def to_dict(result: TaxResult) -> dict:
    data = result.model_dump(mode="json")
    return data


def render_json(result: TaxResult) -> str:
    return json.dumps(to_dict(result), indent=2)


def render_csv(results: Iterable[TaxResult]) -> str:
    results = list(results)
    if not results:
        return ""
    fieldnames = list(to_dict(results[0]).keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        writer.writerow(to_dict(result))
    return buffer.getvalue()

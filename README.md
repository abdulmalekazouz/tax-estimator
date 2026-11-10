# Tax Estimator

A U.S. federal income tax estimator built as a Python library, a CLI, and a small
Flask web app. It computes Adjusted Gross Income, taxable income, progressive
ordinary-income tax, "stacked" long-term capital gains / qualified dividend tax,
self-employment (SECA) tax, the Child Tax Credit phase-out, and the resulting
refund or balance due -- for tax years 2022-2024.

> **Disclaimer:** This is a portfolio / educational project, not tax software.
> It uses simplified, publicly available IRS bracket data and intentionally
> omits several real-world rules (see [Limitations](#limitations) below).
> It is not tax advice -- consult a qualified tax professional for actual
> filing decisions.

## Why this project

This project aims to be both (a) a demonstration of clean, tested, typed
Python, and (b) a reflection of actual U.S. tax mechanics -- bracket
progressivity, the qualified-dividends/capital-gains "stacking" rule, credit
phase-outs, and self-employment tax -- rather than a toy calculator that just
multiplies income by a flat rate.

## Features

- **Accurate bracket math.** Ordinary income is taxed progressively; long-term
  capital gains and qualified dividends are taxed under a separate rate
  schedule but correctly "stacked" on top of ordinary income, matching the
  IRS Qualified Dividends and Capital Gain Tax Worksheet.
- **Decimal, not float, for money.** All currency fields use Python's
  `Decimal` so results are exact to the cent -- no floating-point rounding
  surprises in a tax calculation.
- **Multiple income types**: wages, interest, ordinary/qualified dividends,
  short- and long-term capital gains, self-employment income, and other
  income.
- **Self-employment tax** (Social Security + Medicare) with the correct
  92.35% net-earnings adjustment, Social Security wage base cap, and the
  above-the-line deduction for half of SE tax.
- **Child Tax Credit** with its AGI-based phase-out.
- **Refund vs. balance due**, given withholding and estimated payments.
- **Three ways to use it**: a typed Python library, a CLI (single estimate,
  multi-year comparison, or batch JSON report), and a Flask web form.
- **Validated input** via Pydantic models (filing status, non-negative
  amounts, qualified dividends capped by ordinary dividends, etc.).
- **A 55-test pytest suite** (90% coverage) covering bracket invariants,
  hand-verified dollar amounts, credit phase-out edges, and both the CLI
  and the web app.

## Project layout

```
src/taxestimator/
    models.py      Pydantic models: FilingStatus, TaxpayerProfile, TaxResult
    brackets.py     IRS bracket / standard deduction / wage base reference data
    calculator.py   The compute() engine and the bracket-stacking algorithm
    credits.py      Child Tax Credit phase-out
    payroll.py      Self-employment (SECA) tax
    reports.py      Text / JSON / CSV rendering
    cli.py          argparse-based CLI (estimate / compare / report)
    webapp.py       Flask app (create_app() factory)
    templates/, static/   Web UI
tests/              pytest suite
examples/           Sample batch-input JSON for the `report` command
```

## Installation

Requires Python 3.9+.

```bash
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# A single estimate
taxestimator estimate --year 2024 --status single --wages 85000 \
    --interest-income 250 --withholding 9800

# Compare the same profile across several tax years
taxestimator compare --years 2022 2023 2024 --status married_jointly --wages 140000

# Batch-process a JSON file of profiles into a CSV report
taxestimator report --input examples/sample_profiles.json --format csv --output report.csv
```

### Library

```python
from decimal import Decimal
from taxestimator import FilingStatus, TaxpayerProfile, compute

profile = TaxpayerProfile(
    tax_year=2024,
    filing_status=FilingStatus.SINGLE,
    wages=Decimal("85000"),
    withholding=Decimal("9800"),
)
result = compute(profile)
print(result.total_tax, result.balance_due)
```

### Web app

```bash
flask --app taxestimator.webapp run --debug
```

Then open http://127.0.0.1:5000/, fill in the form, and submit to see a full
line-item breakdown and an estimated refund or balance due.

## Testing

```bash
pytest --cov=taxestimator --cov-report=term-missing
ruff check src tests
```

CI (`.github/workflows/ci.yml`) runs the same lint + test suite on Python
3.10, 3.11, and 3.12 for every push and pull request.

## Limitations

This project deliberately does not model:

- The Alternative Minimum Tax (AMT)
- State or local income tax
- The Net Investment Income Tax (3.8% NIIT) or the Additional Medicare
  surtax (0.9%)
- The refundable Additional Child Tax Credit, the Earned Income Credit, or
  any credit besides the basic nonrefundable Child Tax Credit
- Itemized deduction limits/phase-outs, QBI deduction, or above-the-line
  adjustments other than retirement contributions and half of SE tax
- Tax years outside 2022-2024

These are documented explicitly rather than silently assumed away, which
mirrors how I'd want to flag scope and assumptions on a real tax-software
feature.

## License

MIT -- see [LICENSE](LICENSE).

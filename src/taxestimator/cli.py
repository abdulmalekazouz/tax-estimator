"""Command-line interface for taxestimator.

Examples
--------
    taxestimator estimate --year 2024 --status single --wages 85000
    taxestimator compare --years 2022 2023 2024 --status single --wages 85000
    taxestimator report --input profiles.json --output results.csv --format csv
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from taxestimator.brackets import SUPPORTED_YEARS
from taxestimator.calculator import compute
from taxestimator.models import FilingStatus, TaxpayerProfile, TaxResult
from taxestimator.reports import render_csv, render_json, render_text

PROFILE_FIELDS = (
    "wages",
    "interest_income",
    "ordinary_dividends",
    "qualified_dividends",
    "short_term_capital_gains",
    "long_term_capital_gains",
    "self_employment_income",
    "other_income",
    "pretax_retirement_contributions",
    "itemized_deductions",
    "withholding",
    "estimated_payments",
)


def _add_profile_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--status",
        required=True,
        choices=[s.value for s in FilingStatus],
        help="Filing status",
    )
    for field in PROFILE_FIELDS:
        parser.add_argument(f"--{field.replace('_', '-')}", type=str, default="0")
    parser.add_argument("--dependents", type=int, default=0, help="Number of qualifying children")


def _profile_from_args(args: argparse.Namespace, year: int) -> TaxpayerProfile:
    kwargs: dict[str, Any] = {
        "tax_year": year,
        "filing_status": args.status,
        "qualifying_children": args.dependents,
    }
    for field in PROFILE_FIELDS:
        raw = getattr(args, field)
        try:
            kwargs[field] = Decimal(raw)
        except InvalidOperation as exc:
            raise SystemExit(f"error: --{field.replace('_', '-')} is not a valid number: {raw!r}") from exc
    return TaxpayerProfile(**kwargs)


def _cmd_estimate(args: argparse.Namespace) -> int:
    try:
        profile = _profile_from_args(args, args.year)
        result = compute(profile)
    except ValidationError as exc:
        print(f"Invalid input:\n{exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(render_json(result))
    else:
        print(render_text(result))
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    results: list[TaxResult] = []
    for year in args.years:
        try:
            profile = _profile_from_args(args, year)
            results.append(compute(profile))
        except ValidationError as exc:
            print(f"Invalid input for year {year}:\n{exc}", file=sys.stderr)
            return 1

    if args.format == "json":
        print(json.dumps([json.loads(render_json(r)) for r in results], indent=2))
    elif args.format == "csv":
        print(render_csv(results))
    else:
        for result in results:
            print(render_text(result))
            print()
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    profiles_data = data if isinstance(data, list) else [data]

    results: list[TaxResult] = []
    for entry in profiles_data:
        try:
            results.append(compute(TaxpayerProfile(**entry)))
        except ValidationError as exc:
            print(f"Invalid profile in {args.input}:\n{exc}", file=sys.stderr)
            return 1

    if args.format == "csv":
        output = render_csv(results)
    else:
        output = json.dumps([json.loads(render_json(r)) for r in results], indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {len(results)} result(s) to {args.output}")
    else:
        print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taxestimator", description="Estimate U.S. federal income tax."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    estimate = subparsers.add_parser("estimate", help="Estimate tax for a single year")
    estimate.add_argument("--year", type=int, required=True, choices=SUPPORTED_YEARS)
    estimate.add_argument("--format", choices=["text", "json"], default="text")
    _add_profile_arguments(estimate)
    estimate.set_defaults(func=_cmd_estimate)

    compare = subparsers.add_parser("compare", help="Compare the same profile across years")
    compare.add_argument("--years", type=int, nargs="+", required=True, choices=SUPPORTED_YEARS)
    compare.add_argument("--format", choices=["text", "json", "csv"], default="text")
    _add_profile_arguments(compare)
    compare.set_defaults(func=_cmd_compare)

    report = subparsers.add_parser("report", help="Batch-process profiles from a JSON file")
    report.add_argument("--input", required=True, help="Path to a JSON file (object or array)")
    report.add_argument("--output", help="Path to write results to (default: stdout)")
    report.add_argument("--format", choices=["json", "csv"], default="json")
    report.set_defaults(func=_cmd_report)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

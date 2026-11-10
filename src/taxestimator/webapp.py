"""A small Flask front end over the taxestimator library."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from flask import Flask, render_template, request
from pydantic import ValidationError

from taxestimator.brackets import SUPPORTED_YEARS
from taxestimator.calculator import compute
from taxestimator.models import FilingStatus, TaxpayerProfile

FORM_FIELDS = (
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


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            years=SUPPORTED_YEARS,
            statuses=list(FilingStatus),
            form_fields=FORM_FIELDS,
            errors=None,
            values={},
        )

    @app.post("/estimate")
    def estimate():
        form = request.form
        kwargs: dict[str, Any] = {
            "tax_year": int(form.get("tax_year", SUPPORTED_YEARS[-1])),
            "filing_status": form.get("filing_status", FilingStatus.SINGLE.value),
            "qualifying_children": int(form.get("qualifying_children") or 0),
        }
        for field in FORM_FIELDS:
            raw = form.get(field) or "0"
            try:
                kwargs[field] = Decimal(raw)
            except InvalidOperation:
                kwargs[field] = raw  # let pydantic raise a clean validation error

        try:
            profile = TaxpayerProfile(**kwargs)
            result = compute(profile)
        except (ValidationError, ValueError) as exc:
            return render_template(
                "index.html",
                years=SUPPORTED_YEARS,
                statuses=list(FilingStatus),
                form_fields=FORM_FIELDS,
                errors=str(exc),
                values=form,
            ), 400

        return render_template("result.html", result=result)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

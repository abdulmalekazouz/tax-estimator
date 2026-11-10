"""Published IRS reference data: ordinary income brackets, long-term capital
gains / qualified dividend brackets, and standard deductions.

This data is transcribed from publicly released IRS Revenue Procedures for
illustration and portfolio purposes. It is NOT guaranteed to be complete or
up to date -- always verify against the official IRS tables before relying
on any figure produced by this project. See the "Limitations" section of the
README for everything this project intentionally simplifies or omits.

Bracket tables are expressed as an ascending list of ``(upper_bound, rate)``
tuples. ``upper_bound`` is the top of taxable income taxed at ``rate``; the
final tuple uses ``None`` for "and above".
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from taxestimator.models import FilingStatus

D = Decimal
BracketTable = list[tuple[Optional[Decimal], Decimal]]

SUPPORTED_YEARS = (2022, 2023, 2024)

ORDINARY_BRACKETS: dict[int, dict[FilingStatus, BracketTable]] = {
    2022: {
        FilingStatus.SINGLE: [
            (D("10275"), D("0.10")),
            (D("41775"), D("0.12")),
            (D("89075"), D("0.22")),
            (D("170050"), D("0.24")),
            (D("215950"), D("0.32")),
            (D("539900"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_JOINTLY: [
            (D("20550"), D("0.10")),
            (D("83550"), D("0.12")),
            (D("178150"), D("0.22")),
            (D("340100"), D("0.24")),
            (D("431900"), D("0.32")),
            (D("647850"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("10275"), D("0.10")),
            (D("41775"), D("0.12")),
            (D("89075"), D("0.22")),
            (D("170050"), D("0.24")),
            (D("215950"), D("0.32")),
            (D("323925"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("14650"), D("0.10")),
            (D("55900"), D("0.12")),
            (D("89050"), D("0.22")),
            (D("170050"), D("0.24")),
            (D("215950"), D("0.32")),
            (D("539900"), D("0.35")),
            (None, D("0.37")),
        ],
    },
    2023: {
        FilingStatus.SINGLE: [
            (D("11000"), D("0.10")),
            (D("44725"), D("0.12")),
            (D("95375"), D("0.22")),
            (D("182100"), D("0.24")),
            (D("231250"), D("0.32")),
            (D("578125"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_JOINTLY: [
            (D("22000"), D("0.10")),
            (D("89450"), D("0.12")),
            (D("190750"), D("0.22")),
            (D("364200"), D("0.24")),
            (D("462500"), D("0.32")),
            (D("693750"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("11000"), D("0.10")),
            (D("44725"), D("0.12")),
            (D("95375"), D("0.22")),
            (D("182100"), D("0.24")),
            (D("231250"), D("0.32")),
            (D("346875"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("15700"), D("0.10")),
            (D("59850"), D("0.12")),
            (D("95350"), D("0.22")),
            (D("182100"), D("0.24")),
            (D("231250"), D("0.32")),
            (D("578100"), D("0.35")),
            (None, D("0.37")),
        ],
    },
    2024: {
        FilingStatus.SINGLE: [
            (D("11600"), D("0.10")),
            (D("47150"), D("0.12")),
            (D("100525"), D("0.22")),
            (D("191950"), D("0.24")),
            (D("243725"), D("0.32")),
            (D("609350"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_JOINTLY: [
            (D("23200"), D("0.10")),
            (D("94300"), D("0.12")),
            (D("201050"), D("0.22")),
            (D("383900"), D("0.24")),
            (D("487450"), D("0.32")),
            (D("731200"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("11600"), D("0.10")),
            (D("47150"), D("0.12")),
            (D("100525"), D("0.22")),
            (D("191950"), D("0.24")),
            (D("243725"), D("0.32")),
            (D("365600"), D("0.35")),
            (None, D("0.37")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("16550"), D("0.10")),
            (D("63100"), D("0.12")),
            (D("100500"), D("0.22")),
            (D("191950"), D("0.24")),
            (D("243700"), D("0.32")),
            (D("609350"), D("0.35")),
            (None, D("0.37")),
        ],
    },
}

LTCG_BRACKETS: dict[int, dict[FilingStatus, BracketTable]] = {
    2022: {
        FilingStatus.SINGLE: [(D("41675"), D("0")), (D("459750"), D("0.15")), (None, D("0.20"))],
        FilingStatus.MARRIED_JOINTLY: [
            (D("83350"), D("0")),
            (D("517200"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("41675"), D("0")),
            (D("258600"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("55800"), D("0")),
            (D("488500"), D("0.15")),
            (None, D("0.20")),
        ],
    },
    2023: {
        FilingStatus.SINGLE: [(D("44625"), D("0")), (D("492300"), D("0.15")), (None, D("0.20"))],
        FilingStatus.MARRIED_JOINTLY: [
            (D("89250"), D("0")),
            (D("553850"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("44625"), D("0")),
            (D("276900"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("59750"), D("0")),
            (D("523050"), D("0.15")),
            (None, D("0.20")),
        ],
    },
    2024: {
        FilingStatus.SINGLE: [(D("47025"), D("0")), (D("518900"), D("0.15")), (None, D("0.20"))],
        FilingStatus.MARRIED_JOINTLY: [
            (D("94050"), D("0")),
            (D("583750"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.MARRIED_SEPARATELY: [
            (D("47025"), D("0")),
            (D("291850"), D("0.15")),
            (None, D("0.20")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (D("63000"), D("0")),
            (D("551350"), D("0.15")),
            (None, D("0.20")),
        ],
    },
}

STANDARD_DEDUCTION: dict[int, dict[FilingStatus, Decimal]] = {
    2022: {
        FilingStatus.SINGLE: D("12950"),
        FilingStatus.MARRIED_JOINTLY: D("25900"),
        FilingStatus.MARRIED_SEPARATELY: D("12950"),
        FilingStatus.HEAD_OF_HOUSEHOLD: D("19400"),
    },
    2023: {
        FilingStatus.SINGLE: D("13850"),
        FilingStatus.MARRIED_JOINTLY: D("27700"),
        FilingStatus.MARRIED_SEPARATELY: D("13850"),
        FilingStatus.HEAD_OF_HOUSEHOLD: D("20800"),
    },
    2024: {
        FilingStatus.SINGLE: D("14600"),
        FilingStatus.MARRIED_JOINTLY: D("29200"),
        FilingStatus.MARRIED_SEPARATELY: D("14600"),
        FilingStatus.HEAD_OF_HOUSEHOLD: D("21900"),
    },
}

# Social Security wage base (OASDI), used by the self-employment tax module.
SS_WAGE_BASE: dict[int, Decimal] = {
    2022: D("147000"),
    2023: D("160200"),
    2024: D("168600"),
}

# Child Tax Credit phase-out begins above these AGI thresholds.
CTC_PHASEOUT_THRESHOLD: dict[FilingStatus, Decimal] = {
    FilingStatus.SINGLE: D("200000"),
    FilingStatus.HEAD_OF_HOUSEHOLD: D("200000"),
    FilingStatus.MARRIED_SEPARATELY: D("200000"),
    FilingStatus.MARRIED_JOINTLY: D("400000"),
}

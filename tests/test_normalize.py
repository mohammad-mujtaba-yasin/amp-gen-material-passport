"""Unit tests for unit normalisation (filled in during the normalize step).

Run:  python -m pytest -q
"""
from __future__ import annotations

import pytest

from src import config
from src import normalize


@pytest.mark.parametrize(
    "raw, expected_unit",
    [
        ("Cu.m", config.CUM),
        ("cum", config.CUM),
        ("Sq.m", config.SQM),
        ("Mtr.", config.M),
        ("Kg.", config.KG),
        ("Each", config.NOS),
    ],
)
def test_basic_unit_aliases(raw, expected_unit):
    unit, factor = normalize.normalize_unit(raw)
    assert unit == expected_unit
    assert factor == 1.0


def test_special_cubic_decimetre():
    # "10 Cubic decimetre" (item 24, wood work) == 0.01 cum
    unit, factor = normalize.normalize_unit("10 Cubic decimetre")
    assert unit == config.CUM
    assert factor == pytest.approx(0.01)

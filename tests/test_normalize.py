"""Unit tests for unit normalisation.
"""
from __future__ import annotations

import unittest
from src import config, normalize


class TestNormalize(unittest.TestCase):

    def test_basic_unit_aliases(self):
        cases = [
            ("Cu.m", config.CUM),
            ("cum", config.CUM),
            ("Sq.m", config.SQM),
            ("Mtr.", config.M),
            ("Kg.", config.KG),
            ("Each", config.NOS),
        ]
        for raw, expected in cases:
            unit, factor = normalize.normalize_unit(raw)
            self.assertEqual(unit, expected, f"Failed for {raw}")
            self.assertEqual(factor, 1.0)

    def test_special_cubic_decimetre(self):
        unit, factor = normalize.normalize_unit("10 Cubic decimetre")
        self.assertEqual(unit, config.CUM)
        self.assertAlmostEqual(factor, 0.01)


if __name__ == "__main__":
    unittest.main()

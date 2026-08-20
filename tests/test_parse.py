"""Unit tests for src/parse.py module.
"""
from __future__ import annotations

import unittest
from src import parse


class TestParse(unittest.TestCase):

    def test_extract_mix_ratio(self):
        self.assertEqual(parse.extract_mix_ratio("1:5:10 plain concrete"), "1:5:10")
        self.assertEqual(parse.extract_mix_ratio("1:2:4 RCC work"), "1:2:4")
        self.assertEqual(parse.extract_mix_ratio("mortar mix 1:6"), "1:6")
        self.assertIsNone(parse.extract_mix_ratio("plain work without mix"))

    def test_extract_grade(self):
        self.assertEqual(parse.extract_grade("M-15 grade plain cement concrete"), "M-15")
        self.assertEqual(parse.extract_grade("class designation 75 bricks"), "Class 75")
        self.assertEqual(parse.extract_grade("Fe-500D TMT bars"), "Fe-500D")

    def test_extract_dimensions(self):
        dims = parse.extract_dimensions("40 mm thick cement concrete")
        self.assertEqual(dims["thickness_mm"], 40.0)

        dims_dia = parse.extract_dimensions("100 mm dia CI rainwater pipe")
        self.assertEqual(dims_dia["diameter_mm"], 100.0)

        dims_3d = parse.extract_dimensions("50x50x50 mm plugs")
        self.assertEqual(dims_3d["length_mm"], 50.0)
        self.assertEqual(dims_3d["width_mm"], 50.0)
        self.assertEqual(dims_3d["height_mm"], 50.0)

    def test_infer_discipline(self):
        self.assertEqual(parse.infer_discipline("Earth work excavation"), "Civil & Sitework")
        self.assertEqual(parse.infer_discipline("Reinforced cement concrete beam"), "Structural")
        self.assertEqual(parse.infer_discipline("Door shutter 35 mm"), "Architectural")
        self.assertEqual(parse.infer_discipline("Cement plaster 12 mm"), "Finishes")
        self.assertEqual(parse.infer_discipline("CI rain water pipe 100 mm"), "Services / Plumbing")


if __name__ == "__main__":
    unittest.main()

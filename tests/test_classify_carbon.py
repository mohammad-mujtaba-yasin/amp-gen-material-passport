"""Unit tests for src/classify.py and src/carbon.py modules.
"""
from __future__ import annotations

import unittest
from src import carbon, classify, normalize, parse


class TestClassifyAndCarbon(unittest.TestCase):

    def test_classify_item(self):
        item = {"description": "Steel reinforcement for R.C.C. work including straightening and binding", "dsr_code": "5.29"}
        parse.parse_item(item)
        classify.classify_item(item)

        self.assertEqual(item["material_category"], "Reinf")
        self.assertGreaterEqual(item["material_confidence"], 0.9)
        self.assertEqual(item["schedule"], "DSR 1989")
        self.assertEqual(item["schedule_item_code"], "5.29")

    def test_enrich_carbon(self):
        item = {
            "description": "Steel reinforcement for R.C.C. work Fe-500D",
            "quantity": 1000.0,
            "unit": "Kg.",
        }
        parse.parse_item(item)
        normalize.normalize_item(item)
        classify.classify_item(item)
        carbon.enrich_carbon(item)

        self.assertEqual(item["density_kg_m3"], 7850.0)
        self.assertEqual(item["gwp_per_kg"], 2.363)
        self.assertEqual(item["embodied_carbon_a1_a3"], 2363.0)
        self.assertTrue("[OK]" in item["comment"])

    def test_carbon_excluded_earthwork(self):
        item = {
            "description": "Earth work excavation in foundation trenches",
            "quantity": 32.0,
            "unit": "Cu.m",
        }
        parse.parse_item(item)
        normalize.normalize_item(item)
        classify.classify_item(item)
        carbon.enrich_carbon(item)

        self.assertEqual(item["embodied_carbon_a1_a3"], 0.0)
        self.assertTrue("[EXCLUDED]" in item["comment"])


if __name__ == "__main__":
    unittest.main()

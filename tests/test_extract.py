"""Unit tests for src/extract.py and the extraction outputs.
"""
from __future__ import annotations

import unittest
from src import config, extract


class TestExtract(unittest.TestCase):

    def test_load_items(self):
        items = extract.load_items()
        self.assertEqual(len(items), 64)
        self.assertEqual(items[0]["item_no"], 1)
        self.assertEqual(items[-1]["item_no"], 64)

    def test_sub_items_mapping(self):
        items = extract.load_items()
        items_by_no = {it["item_no"]: it for it in items}

        # Verify sub-item parent numbers: 16, 17, 31, 32, 34, 51
        sub_item_parents = [16, 17, 31, 32, 34, 51]
        for p_no in sub_item_parents:
            self.assertIn(p_no, items_by_no)
            self.assertIn("sub_items", items_by_no[p_no])
            self.assertTrue(len(items_by_no[p_no]["sub_items"]) > 0)

        # Check specific sub-item values
        item16 = items_by_no[16]
        self.assertEqual(len(item16["sub_items"]), 5)
        self.assertEqual(item16["sub_items"][0]["sub_item_no"], "16(i)")
        self.assertEqual(item16["sub_items"][0]["quantity"], 108.0)

        item17 = items_by_no[17]
        self.assertEqual(len(item17["sub_items"]), 2)
        self.assertEqual(item17["sub_items"][0]["quantity"], 100.0)
        self.assertEqual(item17["sub_items"][1]["quantity"], 1375.0)

        item31 = items_by_no[31]
        self.assertEqual(len(item31["sub_items"]), 2)
        self.assertEqual(item31["sub_items"][0]["dsr_code"], "9.219.3")

        item32 = items_by_no[32]
        self.assertEqual(len(item32["sub_items"]), 2)

        item34 = items_by_no[34]
        self.assertEqual(len(item34["sub_items"]), 2)
        self.assertEqual(item34["sub_items"][0]["dsr_code"], "N.S.I.")

        item51 = items_by_no[51]
        self.assertEqual(len(item51["sub_items"]), 3)
        self.assertEqual(item51["sub_items"][0]["dsr_code"], "12.72.2.2")

    def test_building_meta(self):
        meta = extract.extract_building_meta()
        self.assertEqual(meta["no_of_items"], 64)
        self.assertEqual(meta["plinth_area_sqm"], 90.6)
        self.assertEqual(meta["depth_of_foundation_m"], 0.60)
        self.assertEqual(meta["plinth_height_m"], 0.45)


if __name__ == "__main__":
    unittest.main()

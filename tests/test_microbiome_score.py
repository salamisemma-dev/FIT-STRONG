import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import FoodItem, FoodRef, microbiome_score  # noqa: E402

DB = {
    "havermout": FoodRef("havermout", "fructan", "medium", 379, 13, 67, 7, 10.0, 8),
    "ui": FoodRef("ui", "fructan", "high", 40, 1.1, 9, 0.1, 1.7, 9),
}


class TestMicrobiomeScore(unittest.TestCase):
    def test_empty_day_zero(self):
        self.assertEqual(microbiome_score([], DB).score, 0.0)

    def test_high_fibre_prebiotic_scores_high(self):
        # 300g havermout -> 30g fibre (full 60) + 24 prebiotic pts (capped 40) = 100
        res = microbiome_score([FoodItem("havermout", 300)], DB)
        self.assertEqual(res.score, 100.0)
        self.assertEqual(res.fiber_g, 30.0)

    def test_unknown_food_unresolved_and_zero(self):
        res = microbiome_score([FoodItem("marsbar", 100)], DB)
        self.assertEqual(res.score, 0.0)
        self.assertIn("marsbar", res.unresolved)

    def test_caps_at_100(self):
        res = microbiome_score([FoodItem("havermout", 1000)], DB)
        self.assertLessEqual(res.score, 100.0)


if __name__ == "__main__":
    unittest.main()

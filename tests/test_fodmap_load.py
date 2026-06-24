import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import FoodItem, fodmap_load, meal_exceeds_threshold  # noqa: E402


class TestFodmapLoad(unittest.TestCase):
    def test_per_level_contribution(self):
        self.assertEqual(fodmap_load([FoodItem("ui", 100, "fructan", "high")]), 8.0)
        self.assertEqual(fodmap_load([FoodItem("x", 100, "fructan", "medium")]), 4.0)
        self.assertEqual(fodmap_load([FoodItem("x", 100, "fructan", "low")]), 1.0)
        self.assertEqual(fodmap_load([FoodItem("rijst", 100, "low_fodmap", "very_low")]), 0.0)

    def test_summation(self):
        items = [FoodItem("ui", 50, "fructan", "high"),
                 FoodItem("courgette", 100, "low_fodmap", "low")]
        self.assertEqual(fodmap_load(items), round(50 * 0.08 + 100 * 0.01, 2))

    def test_empty_meal(self):
        self.assertEqual(fodmap_load([]), 0.0)

    def test_threshold_boundary(self):
        below = [FoodItem("ui", 187, "fructan", "high")]   # 14.96
        above = [FoodItem("ui", 188, "fructan", "high")]   # 15.04
        self.assertFalse(meal_exceeds_threshold(below))
        self.assertTrue(meal_exceeds_threshold(above))


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import FoodItem, Meal, Symptom, detect_triggers  # noqa: E402

BASE = datetime(2026, 1, 1, 8, 0)


class TestTriggerDetection(unittest.TestCase):
    def test_in_window_pain_ranks_first(self):
        meals = [Meal(BASE, "breakfast", [FoodItem("ui", 50, "fructan", "high")])]
        symptoms = [Symptom(BASE + timedelta(hours=3), abdominal_pain=8)]
        result = detect_triggers(meals, symptoms)
        self.assertEqual(result[0].food_name, "ui")
        self.assertEqual(result[0].score, 8.0)
        self.assertEqual(result[0].occurrences, 1)

    def test_no_following_symptom_scores_nothing(self):
        meals = [Meal(BASE, "breakfast", [FoodItem("rijst", 100)])]
        symptoms = [Symptom(BASE + timedelta(hours=8), abdominal_pain=9)]  # outside window
        self.assertEqual(detect_triggers(meals, symptoms), [])

    def test_ordering_and_top_n(self):
        meals = [
            Meal(BASE, "breakfast", [FoodItem("ui", 10)]),
            Meal(BASE + timedelta(hours=6), "lunch", [FoodItem("knoflook", 5)]),
            Meal(BASE + timedelta(hours=12), "dinner", [FoodItem("appel", 100)]),
            Meal(BASE + timedelta(hours=18), "snack", [FoodItem("melk", 200)]),
        ]
        symptoms = [
            Symptom(BASE + timedelta(hours=3), abdominal_pain=9),
            Symptom(BASE + timedelta(hours=9), abdominal_pain=7),
            Symptom(BASE + timedelta(hours=15), abdominal_pain=5),
            Symptom(BASE + timedelta(hours=21), abdominal_pain=4),
        ]
        result = detect_triggers(meals, symptoms, top_n=3)
        self.assertEqual(len(result), 3)
        self.assertEqual([t.food_name for t in result], ["ui", "knoflook", "appel"])

    def test_bloating_tiebreaker_when_pain_none(self):
        meals = [Meal(BASE, "breakfast", [FoodItem("ui", 10)])]
        symptoms = [Symptom(BASE + timedelta(hours=3), bloating=6)]
        result = detect_triggers(meals, symptoms)
        self.assertEqual(result[0].food_name, "ui")

    def test_high_fodmap_outranks_innocent_bystander(self):
        # ui (high) + kipfilet (very_low) share one meal followed by pain.
        meals = [Meal(BASE, "lunch", [
            FoodItem("ui", 200, "fructan", "high"),
            FoodItem("kipfilet", 150, "low_fodmap", "very_low"),
        ])]
        symptoms = [Symptom(BASE + timedelta(hours=3), abdominal_pain=8)]
        result = detect_triggers(meals, symptoms)
        self.assertEqual(result[0].food_name, "ui")
        self.assertGreater(result[0].score, result[1].score)

    def test_empty_inputs(self):
        self.assertEqual(detect_triggers([], []), [])


if __name__ == "__main__":
    unittest.main()

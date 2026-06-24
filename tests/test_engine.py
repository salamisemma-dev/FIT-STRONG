import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402

BASE = datetime(2026, 1, 1, 8, 0)


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.client = fs.Client(weight_kg=80, height_cm=180, sex="male",
                                training_goal="muscle_gain", weekly_sport_hours=8)
        self.meals = [
            fs.Meal(BASE, "breakfast", [
                fs.FoodItem("havermout", 100, "fructan", "medium"),
                fs.FoodItem("ui", 200, "fructan", "high"),  # high FODMAP -> alert (16 load)
            ]),
        ]
        self.symptoms = [fs.Symptom(BASE + timedelta(hours=3), abdominal_pain=8)]
        self.db = {
            "havermout": fs.FoodRef("havermout", "fructan", "medium", 379, 13, 67, 7, 10.0, 8),
            "ui": fs.FoodRef("ui", "fructan", "high", 40, 1.1, 9, 0.1, 1.7, 9),
        }

    def test_end_to_end_report(self):
        report = fs.generate_report(
            self.client, self.meals, self.symptoms, [], self.db,
            day_calories=2000, day_protein_g=100, bristol_events=[6, 7, 6, 7],
            no_improvement_weeks=5,
        )
        # macro targets present and goal-correct
        self.assertEqual(report.macro_targets.protein_g, 160.0)
        # at least one trigger surfaced
        self.assertGreaterEqual(len(report.triggers), 1)
        # high FODMAP alert fired
        self.assertTrue(any(a.alert_type == "high_fodmap" for a in report.alerts))
        # energy-balance alerts fired (low cal + low protein + dehydration)
        kinds = {a.alert_type for a in report.alerts}
        self.assertIn("low_calories", kinds)
        self.assertIn("low_protein", kinds)
        self.assertIn("dehydration_risk", kinds)
        # microbiome present, disclaimer non-empty, referral set
        self.assertIsNotNone(report.microbiome)
        self.assertTrue(report.disclaimer.strip())
        self.assertIsNotNone(report.referral_advice)

    def test_to_dict_roundtrip(self):
        report = fs.generate_report(self.client, self.meals, self.symptoms, [], self.db)
        d = report.to_dict()
        self.assertEqual(set(d), {
            "macro_targets", "triggers", "alerts", "microbiome",
            "disclaimer", "referral_advice", "meta",
        })
        self.assertIsInstance(d["triggers"], list)

    def test_energy_balance_skipped_without_intake(self):
        report = fs.generate_report(self.client, self.meals, self.symptoms, [], self.db)
        # no fabricated energy alerts when intake omitted
        self.assertFalse(any(a.alert_type in ("low_calories", "low_protein") for a in report.alerts))


if __name__ == "__main__":
    unittest.main()

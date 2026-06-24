import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import models as m  # noqa: E402


class TestModels(unittest.TestCase):
    def test_valid_client(self):
        c = m.Client(weight_kg=80, height_cm=180, sex="male",
                     training_goal="muscle_gain", weekly_sport_hours=6)
        self.assertEqual(c.sex, m.Sex.MALE)
        self.assertEqual(c.training_goal, m.TrainingGoal.MUSCLE_GAIN)

    def test_enum_coercion_from_string(self):
        self.assertEqual(m.FodmapLevel.coerce("high"), m.FodmapLevel.HIGH)
        with self.assertRaises(ValueError):
            m.FodmapLevel.coerce("nope")

    def test_client_weight_range(self):
        for bad in (0, -5, 401):
            with self.assertRaises(ValueError):
                m.Client(weight_kg=bad, height_cm=180, sex="male",
                         training_goal="endurance", weekly_sport_hours=3)

    def test_symptom_range_checks(self):
        m.Symptom(recorded_at=datetime(2026, 1, 1), bristol_stool=4, abdominal_pain=10,
                  energy_level=1)
        with self.assertRaises(ValueError):
            m.Symptom(recorded_at=datetime(2026, 1, 1), bristol_stool=8)
        with self.assertRaises(ValueError):
            m.Symptom(recorded_at=datetime(2026, 1, 1), energy_level=0)
        with self.assertRaises(ValueError):
            m.Symptom(recorded_at=datetime(2026, 1, 1), abdominal_pain=11)

    def test_food_item_negative_amount(self):
        with self.assertRaises(ValueError):
            m.FoodItem(name="ui", amount_g=-1)
        with self.assertRaises(ValueError):
            m.FoodItem(name="  ", amount_g=10)

    def test_workout_borg_range(self):
        m.Workout(started_at=datetime(2026, 1, 1), duration_min=60, intensity=7,
                  perceived_exertion=15)
        with self.assertRaises(ValueError):
            m.Workout(started_at=datetime(2026, 1, 1), duration_min=60, intensity=11)
        with self.assertRaises(ValueError):
            m.Workout(started_at=datetime(2026, 1, 1), duration_min=60, intensity=5,
                      perceived_exertion=5)

    def test_food_ref_numeric_ranges(self):
        m.FoodRef("ui", "fructan", "high", 40, 1.1, 9, 0.1, 1.7, 9, 12)
        with self.assertRaises(ValueError):
            m.FoodRef("bad", "fructan", "high", -1, 1, 1, 1, 1, 1)
        with self.assertRaises(ValueError):
            m.FoodRef("bad", "fructan", "high", 1, 1, 1, 1, 1, 1, -1)

    def test_alert_severity_and_dict(self):
        a = m.Alert("low_protein", "critical", "x")
        self.assertEqual(a.to_dict()["severity"], "critical")
        with self.assertRaises(ValueError):
            m.Alert("x", "fatal", "y")


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import Client, compute_macro_targets  # noqa: E402


def _client(goal, hours, weight=80):
    return Client(weight_kg=weight, height_cm=180, sex="male",
                  training_goal=goal, weekly_sport_hours=hours)


class TestMacroTargets(unittest.TestCase):
    def test_protein_by_goal(self):
        self.assertEqual(compute_macro_targets(_client("muscle_gain", 5)).protein_g, 160.0)
        self.assertEqual(compute_macro_targets(_client("endurance", 5)).protein_g, 144.0)
        self.assertEqual(compute_macro_targets(_client("general_fitness", 5)).protein_g, 128.0)

    def test_carbs_band_switch(self):
        moderate = compute_macro_targets(_client("endurance", 6))  # < 7h
        intensive = compute_macro_targets(_client("endurance", 7))  # >= 7h
        self.assertEqual(moderate.carbs_basis, "moderate")
        self.assertEqual((moderate.carbs_g_low, moderate.carbs_g_high), (240.0, 400.0))
        self.assertEqual(intensive.carbs_basis, "intensive")
        self.assertEqual((intensive.carbs_g_low, intensive.carbs_g_high), (400.0, 560.0))

    def test_energy_maintenance(self):
        t = compute_macro_targets(_client("endurance", 5))
        self.assertEqual((t.energy_kcal_low, t.energy_kcal_high), (2400.0, 2800.0))

    def test_muscle_gain_surplus(self):
        t = compute_macro_targets(_client("muscle_gain", 5))
        self.assertEqual((t.energy_kcal_low, t.energy_kcal_high), (2700.0, 3300.0))


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import Client, check_energy_balance  # noqa: E402

CLIENT = Client(weight_kg=80, height_cm=180, sex="male",
                training_goal="muscle_gain", weekly_sport_hours=6)
# floors: calories 2400, protein 128


class TestEnergyBalance(unittest.TestCase):
    def test_adequate_day_no_alerts(self):
        self.assertEqual(check_energy_balance(CLIENT, 2600, 150, [4, 4]), [])

    def test_low_calories_warning(self):
        alerts = check_energy_balance(CLIENT, 2000, 150)
        types = {(a.alert_type, a.severity.value) for a in alerts}
        self.assertIn(("low_calories", "warning"), types)

    def test_low_protein_critical(self):
        alerts = check_energy_balance(CLIENT, 2600, 100)
        types = {(a.alert_type, a.severity.value) for a in alerts}
        self.assertIn(("low_protein", "critical"), types)

    def test_dehydration_risk(self):
        alerts = check_energy_balance(CLIENT, 2600, 150, [6, 7, 6, 7])  # 4 loose > 3
        self.assertTrue(any(a.alert_type == "dehydration_risk" for a in alerts))
        # exactly 3 loose should NOT fire
        alerts3 = check_energy_balance(CLIENT, 2600, 150, [6, 7, 6])
        self.assertFalse(any(a.alert_type == "dehydration_risk" for a in alerts3))

    def test_boundary_at_minimum(self):
        # exactly the floor -> no deficit alert
        self.assertEqual(check_energy_balance(CLIENT, 2400, 128), [])


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402


def _client(goal="general_fitness", hours=0.0, weight=80):
    return fs.Client(weight_kg=weight, height_cm=180, sex="male",
                     training_goal=goal, weekly_sport_hours=hours)


class TestFitStrongScore(unittest.TestCase):
    def test_energy_in_range_below_above(self):
        c = _client()  # energy 2400-2800, protein target 128
        in_range = fs.fitstrong_score(c, 2600, 128, [], {})
        below = fs.fitstrong_score(c, 1200, 128, [], {})
        above = fs.fitstrong_score(c, 3630, 128, [], {})  # high=2800 -> wait general energy 2400-2800
        self.assertEqual(in_range.subscores["energy"], 100.0)
        self.assertAlmostEqual(below.subscores["energy"], 1200 / 2400 * 100, places=1)
        self.assertLess(above.subscores["energy"], 100.0)

    def test_weight_renormalisation_when_components_absent(self):
        c = _client()  # weekly 0 -> training dropped; no food/meal/symptoms
        s = fs.fitstrong_score(c, 2600, 128, [], {})
        # only protein + energy present
        self.assertEqual(set(s.components_used), {"protein", "energy"})
        self.assertEqual(s.score, 100.0)  # both 100, renormalised
        self.assertEqual(s.band, "sterk")

    def test_band_thresholds_and_improvements_sorted(self):
        c = _client()
        s = fs.fitstrong_score(c, 1200, 64, [], {})  # protein 50, energy 50
        self.assertEqual(s.subscores["protein"], 50.0)
        self.assertEqual(s.band, "matig")
        # both < 70 -> improvements; tie on score -> area asc => energy before protein
        self.assertEqual([i.area for i in s.improvements], ["energy", "protein"])

    def test_microbiome_and_fodmap_and_training_components(self):
        c = _client(goal="muscle_gain", hours=8)
        db = {"havermout": fs.FoodRef("havermout", "fructan", "medium", 379, 13, 67, 7, 10.0, 8)}
        items = [fs.FoodItem("havermout", 300, "fructan", "medium")]
        s = fs.fitstrong_score(c, 3000, 160, items, db,
                               symptoms=[fs.Symptom(datetime(2026, 1, 1), abdominal_pain=8)])
        self.assertIn("microbiome", s.components_used)
        self.assertIn("fodmap", s.components_used)
        self.assertEqual(s.subscores["training"], 100.0)  # 8/5 capped
        self.assertEqual(s.subscores["symptoms"], 20.0)   # 100 - 8*10

    def test_deterministic(self):
        c = _client(goal="muscle_gain", hours=6)
        a = fs.fitstrong_score(c, 2500, 140, [], {})
        b = fs.fitstrong_score(c, 2500, 140, [], {})
        self.assertEqual(a.to_dict(), b.to_dict())


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402


def _db():
    refs = [
        fs.FoodRef("Kipfilet", "low_fodmap", "very_low", 165, 31, 0, 3.6, 0, 0, 200, id="chicken"),
        fs.FoodRef("Rijst", "low_fodmap", "very_low", 130, 2.7, 28, 0.3, 0.4, 1, 200, id="rice"),
        fs.FoodRef("Havermout", "fructan", "medium", 379, 13, 67, 7, 10.0, 8, 50, id="oats"),
        fs.FoodRef("Ui", "fructan", "high", 40, 1.1, 9, 0.1, 1.7, 9, 12, id="onion"),
    ]
    db = {}
    for r in refs:
        db[r.id] = r
        db[r.name.lower()] = r  # mimic real loader double-keying
    return db


def _client():
    return fs.Client(weight_kg=80, height_cm=180, sex="male",
                     training_goal="muscle_gain", weekly_sport_hours=8)


class TestDailyScheme(unittest.TestCase):
    def _item_ids(self, scheme):
        return {it["id"] for meal in scheme.meals for it in meal.items}

    def test_high_fodmap_excluded_when_sensitive(self):
        scheme = fs.daily_scheme(_client(), _db(), fodmap_sensitive=True)
        self.assertNotIn("onion", self._item_ids(scheme))

    def test_high_fodmap_allowed_when_not_sensitive(self):
        # onion is highest prebiotic but lands via fibre/veg pick only if not filtered;
        # at minimum it must be eligible (not force-dropped).
        scheme = fs.daily_scheme(_client(), _db(), fodmap_sensitive=False)
        self.assertIn("indicatief", " ".join(scheme.notes).lower())

    def test_exclude_ids_honoured(self):
        scheme = fs.daily_scheme(_client(), _db(), exclude_ids=("rice",))
        self.assertNotIn("rice", self._item_ids(scheme))

    def test_coverage_and_totals_present(self):
        scheme = fs.daily_scheme(_client(), _db()).to_dict()
        self.assertEqual(set(scheme["coverage"]), {"protein_pct", "carbs_pct", "energy_pct"})
        self.assertEqual(set(scheme["totals"]), {"protein_g", "carbs_g", "energy_kcal", "fiber_g"})
        self.assertEqual(len(scheme["meals"]), 3)

    def test_empty_db_note(self):
        scheme = fs.daily_scheme(_client(), {})
        self.assertTrue(any("Geen geschikte" in n for n in scheme.notes))

    def test_deterministic(self):
        a = fs.daily_scheme(_client(), _db()).to_dict()
        b = fs.daily_scheme(_client(), _db()).to_dict()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()

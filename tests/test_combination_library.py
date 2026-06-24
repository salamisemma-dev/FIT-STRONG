import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class TestCombinationLibrary(unittest.TestCase):
    def test_v2_food_db_loads_by_id_and_legacy_name(self):
        db = fs.load_food_db("config/food_db.json")
        self.assertGreaterEqual(len({ref.id for ref in db.values() if ref.id}), 36)
        self.assertIn("salmon_wild", db)
        self.assertIn("ui", db)
        self.assertEqual(db["salmon_wild"].protein_per_100g, 25)
        self.assertEqual(db["ui"].fodmap_level.value, "high")

    def test_supplements_and_rules_load(self):
        supplements = fs.load_supplement_db("config/supplement_db.json")
        rules = fs.load_combination_rules("config/combination_rules.json")
        self.assertIn("creatine_monohydrate", supplements)
        self.assertEqual(supplements["creatine_monohydrate"].dose_dict(), {"dose_g": 5})
        self.assertTrue(any(rule.id == "electrolytes_with_sweating" for rule in rules))
        self.assertTrue(all(isinstance(rule.condition, dict) for rule in rules))

    def test_post_workout_fish_combo_skips_extra_omega3(self):
        request = json.loads((ROOT / "examples" / "sample_combination_request.json").read_text(encoding="utf-8"))
        result = fs.recommend_combination(request).to_dict()
        food_ids = {item["id"] for item in result["recommended_combo"]["foods"]}
        supplement_ids = {item["id"] for item in result["recommended_combo"]["supplements"]}

        self.assertIn("salmon_wild", food_ids)
        self.assertIn("creatine_monohydrate", supplement_ids)
        self.assertIn("electrolytes_no_sorbitol", supplement_ids)
        self.assertNotIn("omega3_fish_oil", supplement_ids)
        self.assertTrue(any("Omega-3 visolie niet toegevoegd" in warning for warning in result["warnings"]))

    def test_sensitive_gut_filters_high_fodmap_and_warns_caffeine(self):
        result = fs.recommend_combination({
            "context": {"meal_timing": "pre_workout", "fodmap_sensitive": True, "meal_near_h": 1},
            "available_foods": ["ui", "rice_white", "olive_oil"],
            "available_supplements": ["caffeine_anhydrous"],
        }).to_dict()
        food_ids = {item["id"] for item in result["recommended_combo"]["foods"]}
        self.assertNotIn("ui", food_ids)
        self.assertTrue(any("Cafeine" in warning for warning in result["warnings"]))
        self.assertTrue(any("Vette maaltijd" in warning for warning in result["warnings"]))

    def test_unresolved_foods_are_reported(self):
        result = fs.recommend_combination({
            "context": {},
            "available_foods": ["mystery_powder"],
            "available_supplements": [],
        }).to_dict()
        self.assertEqual(result["meta"]["unresolved_foods"], ["mystery_powder"])

    def test_rule_ingredients_reference_known_library_items(self):
        foods = fs.load_food_db("config/food_db.json")
        supplements = fs.load_supplement_db("config/supplement_db.json")
        known_food_ids = {ref.id for ref in foods.values() if ref.id}
        known = known_food_ids | set(foods) | set(supplements)
        for rule in fs.load_combination_rules("config/combination_rules.json"):
            missing = [item for item in rule.ingredients if item not in known]
            self.assertEqual(missing, [], rule.id)

    def test_accepts_object_request_shapes(self):
        # Meal-doc shape: foods as [{id, amount_g}] under "foods", amount honored.
        meal = json.loads((ROOT / "examples" / "sample_high_protein_meal.json").read_text(encoding="utf-8"))
        result = fs.recommend_combination(meal).to_dict()
        foods = {item["id"]: item["amount_g"] for item in result["recommended_combo"]["foods"]}
        self.assertIn("salmon_wild", foods)
        self.assertEqual(foods["salmon_wild"], 150)  # requested amount, not safe-portion default

        # Stack-doc shape: supplements as [{id, dose}] under "supplements" — must be read,
        # not silently dropped. Creatine without carbs surfaces a reasoned warning.
        stack = json.loads((ROOT / "examples" / "sample_supplement_stack.json").read_text(encoding="utf-8"))
        stack_result = fs.recommend_combination(stack).to_dict()
        self.assertTrue(any("Creatine" in w for w in stack_result["warnings"]))

    def test_config_and_packaged_library_copies_are_identical(self):
        for name in ("food_db.json", "supplement_db.json", "combination_rules.json"):
            src = json.loads((ROOT / "config" / name).read_text(encoding="utf-8"))
            pkg = json.loads((ROOT / "src" / "fit_strong" / "data" / name).read_text(encoding="utf-8"))
            self.assertEqual(src, pkg)


if __name__ == "__main__":
    unittest.main()

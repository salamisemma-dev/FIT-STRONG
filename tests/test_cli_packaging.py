import copy
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fit_strong import cli, food_db  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]


class TestCliPackaging(unittest.TestCase):
    def test_default_food_db_has_packaged_fallback(self):
        with patch.object(food_db, "_DEFAULT_PATH", Path("__missing_repo_config__.json")):
            db = food_db.load_food_db()

        self.assertIn("ui", db)
        self.assertEqual(db["ui"].fodmap_level.value, "high")

    def test_run_does_not_mutate_loaded_diary(self):
        diary = {
            "client": {
                "weight_kg": 80,
                "height_cm": 180,
                "sex": "male",
                "training_goal": "general_fitness",
                "weekly_sport_hours": 4,
            },
            "meals": [],
            "symptoms": [{"recorded_at": "2026-01-01T11:00:00", "abdominal_pain": 4}],
            "workouts": [{"started_at": "2026-01-01T17:00:00", "duration_min": 45, "intensity": 6}],
        }
        original = copy.deepcopy(diary)

        with patch.object(cli, "load_diary", return_value=diary):
            cli.run("unused.json", "config/food_db.json")

        self.assertEqual(diary, original)

    def test_food_db_source_and_packaged_copy_are_identical(self):
        # spec-cli-packaging: config/ is the editable source; the packaged copy must
        # mirror it. Compare parsed content so line-endings never cause false drift.
        src = json.loads((_ROOT / "config" / "food_db.json").read_text(encoding="utf-8"))
        pkg = json.loads((_ROOT / "src" / "fit_strong" / "data" / "food_db.json").read_text(encoding="utf-8"))
        self.assertEqual(src, pkg)


if __name__ == "__main__":
    unittest.main()

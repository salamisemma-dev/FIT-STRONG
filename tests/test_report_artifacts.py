import json
import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402

BASE = datetime(2026, 1, 1, 8, 0)


def _setup():
    client = fs.Client(weight_kg=80, height_cm=180, sex="male",
                       training_goal="muscle_gain", weekly_sport_hours=8)
    db = {"havermout": fs.FoodRef("havermout", "fructan", "medium", 379, 13, 67, 7, 10.0, 8, 50, id="havermout")}
    meals = [fs.Meal(BASE, "breakfast", [fs.FoodItem("havermout", 100, "fructan", "medium")])]
    symptoms = [fs.Symptom(BASE + timedelta(hours=3), abdominal_pain=8)]
    report = fs.generate_report(client, meals, symptoms, [], db,
                                day_calories=2000, day_protein_g=100, no_improvement_weeks=5)
    score = fs.fitstrong_score(client, 2000, 100, [fs.FoodItem("havermout", 100, "fructan", "medium")],
                               db, symptoms=symptoms)
    scheme = fs.daily_scheme(client, db)
    return report, score, scheme


class TestReportArtifacts(unittest.TestCase):
    def test_render_html_self_contained(self):
        report, score, scheme = _setup()
        html = fs.render_html(report, score, scheme)
        self.assertTrue(html.lstrip().startswith("<!doctype html>"))
        self.assertIn("Fit &amp; Strong rapport", html)
        self.assertIn(str(score.score), html)
        self.assertIn("Maaltijd", html)              # scheme table rendered
        self.assertIn("indicatief", html.lower())    # disclaimer present
        # no external assets (offline, private)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)

    def test_render_html_without_scheme(self):
        report, score, _ = _setup()
        html = fs.render_html(report, score, None)
        self.assertIn("Fit &amp; Strong rapport", html)
        self.assertNotIn("Dagschema", html)

    def test_weekly_video_props_json_serialisable(self):
        _, score, _ = _setup()
        props = fs.weekly_video_props(score, week_label="Week 1")
        self.assertEqual(props["week_label"], "Week 1")
        self.assertEqual(props["score"], score.score)
        self.assertLessEqual(len(props["top_improvements"]), 3)
        json.dumps(props)  # must not raise


if __name__ == "__main__":
    unittest.main()

import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import fit_strong as fs  # noqa: E402
from fit_strong import cli  # noqa: E402

BASE = datetime(2026, 1, 1, 8, 0)


class TestCycleHormone(unittest.TestCase):
    def test_phase_mapping(self):
        self.assertEqual(fs.phase_for_cycle_day(1).value, "menstrual")
        self.assertEqual(fs.phase_for_cycle_day(8).value, "follicular")
        self.assertEqual(fs.phase_for_cycle_day(15).value, "ovulatory")
        self.assertEqual(fs.phase_for_cycle_day(23).value, "luteal")
        self.assertEqual(fs.phase_for_cycle_day(None).value, "unknown")

    def test_cycle_day_from_start_date(self):
        cycles = [fs.MenstrualCycle(cycle_start_date=date(2026, 1, 1), avg_cycle_length_days=28)]
        self.assertEqual(fs.cycle_day_for(date(2026, 1, 21), cycles), 21)

    def test_insufficient_data_does_not_invent_pattern(self):
        cycles = [fs.MenstrualCycle(cycle_start_date=date(2026, 1, 1), avg_cycle_length_days=28)]
        analysis = fs.analyze_cycle_hormones(
            [fs.Symptom(BASE + timedelta(days=7), abdominal_pain=3)],
            cycles,
            today=date(2026, 1, 8),
        )
        self.assertEqual(analysis.data_quality, "partial_data")
        self.assertEqual(analysis.alerts, [])

    def test_luteal_pattern_alert_requires_enough_data(self):
        cycles = [fs.MenstrualCycle(cycle_start_date=date(2026, 1, 1), avg_cycle_length_days=28)]
        symptoms = [
            fs.Symptom(BASE + timedelta(days=6), abdominal_pain=2),
            fs.Symptom(BASE + timedelta(days=8), bloating=3),
            fs.Symptom(BASE + timedelta(days=20), abdominal_pain=7),
            fs.Symptom(BASE + timedelta(days=22), bloating=8),
        ]
        analysis = fs.analyze_cycle_hormones(symptoms, cycles, today=date(2026, 1, 23))
        self.assertEqual(analysis.data_quality, "pattern_ready")
        self.assertGreaterEqual(analysis.luteal_delta, 1.5)
        self.assertTrue(any("Luteale fase" in alert for alert in analysis.alerts))

    def test_severe_hormonal_symptoms_alert(self):
        analysis = fs.analyze_cycle_hormones(
            [],
            [fs.MenstrualCycle(cycle_start_date=date(2026, 1, 1))],
            [fs.HormonalSymptom(BASE, pelvic_pain=9, menstrual_flow="heavy")],
            today=date(2026, 1, 1),
        )
        self.assertTrue(any("Hevige bekkenpijn" in alert for alert in analysis.alerts))
        self.assertTrue(any("Hevig bloedverlies" in alert for alert in analysis.alerts))

    def test_cli_emits_hormone_section_when_cycle_data_present(self):
        diary = {
            "client": {"weight_kg": 70, "height_cm": 170, "sex": "female", "training_goal": "general_fitness", "weekly_sport_hours": 3},
            "meals": [],
            "symptoms": [{"recorded_at": "2026-01-23T08:00:00", "abdominal_pain": 7}],
            "menstrual_cycles": [{"cycle_start_date": "2026-01-01", "avg_cycle_length_days": 28}],
            "hormonal_symptoms": [{"recorded_at": "2026-01-23T09:00:00", "cycle_day": 23, "pelvic_pain": 6}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diary.json"
            path.write_text(__import__("json").dumps(diary), encoding="utf-8")
            result = cli.run(str(path), "config/food_db.json")
        self.assertIsNotNone(result["hormone"])
        self.assertEqual(result["hormone"]["current_phase"], "luteal")

    def test_html_renders_hormone_section(self):
        client = fs.Client(70, 170, "female", "general_fitness", 3)
        report = fs.generate_report(client, [], [], [], {})
        score = fs.fitstrong_score(client, None, None, [], {}, symptoms=[])
        hormone = fs.analyze_cycle_hormones(
            [], [fs.MenstrualCycle(cycle_start_date=date(2026, 1, 1))], [], today=date(2026, 1, 3)
        )
        html = fs.render_html(report, score, None, hormone)
        self.assertIn("Cycluscontext", html)
        self.assertIn("geen diagnose", html)


if __name__ == "__main__":
    unittest.main()


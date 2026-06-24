---
id: spec-cycle-hormone
type: semantic
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-trigger-detection, spec-report-artifacts]
consumed_by: [cli, fit-strong-skill, html-report]
---

## Intent
Add optional, cycle-aware FODMAP support for users who menstruate, without turning the
engine into a diagnostic hormone tool. The feature correlates diary symptoms with cycle
phase, surfaces cautious phase-aware nutrition notes, and preserves the medical
disclaimer boundary.

## Contract
- `MenstrualCycle(cycle_start_date, cycle_end_date=None, avg_cycle_length_days=None, symptoms={})`.
- `HormonalSymptom(recorded_at, cycle_day=None, pelvic_pain=None, menstrual_flow=None,
  mood_irritability=None, headache=False, breast_tenderness=None, cycle_wellbeing=None, notes=None)`.
- `phase_for_cycle_day(day)` maps 1-5 menstrual, 6-13 follicular, 14-16 ovulatory,
  17-28 luteal by default; unknown/missing returns `unknown`.
- `analyze_cycle_hormones(symptoms, cycles, hormonal_symptoms, today=None,
  fodmap_sensitive=True) -> HormoneAnalysis` returns phase, averages, alerts, advice,
  data_quality and disclaimer.
- CLI emits `hormone` when `menstrual_cycles` or `hormonal_symptoms` are present.
- HTML report renders a cycle/hormone section only when analysis exists.

## Business Rules
- Never diagnose endometriosis, PMS, PMDD, infertility, estrogen imbalance, or hormone
  disease. Output language is pattern hypothesis only.
- Require at least two follicular and two luteal events before raising a luteal-vs-
  follicular pattern alert. Otherwise return `partial_data` or `insufficient_data`.
- Severe pelvic pain (>=8) or heavy bleeding creates a referral-style alert.
- FODMAP restriction must be framed as temporary/personalized, not a permanent hormone
  intervention.
- Missing cycle data must not fabricate phase or hormone conclusions.

## Evidence
`docs/EVIDENCE.md` records this as Hypothesis/Moderate: low-FODMAP has evidence for IBS
symptom management, endometriosis/diet evidence is emerging, estrogen-gut pain mechanisms
include preclinical work, and estrobolome links are mostly associative.

## Verification
`tests/test_cycle_hormone.py` validates phase mapping, model ranges, insufficient-data
behavior, luteal pattern alerting, severe symptom alerts, CLI JSON output, and HTML
section rendering.


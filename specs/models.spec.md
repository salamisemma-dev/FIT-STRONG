---
id: spec-models
type: schema
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: []
consumed_by: [spec-macro-targets, spec-fodmap-load, spec-trigger-detection, spec-energy-balance, spec-microbiome-score, spec-report-engine, spec-cycle-hormone]
---

## Intent
Typed, validated, in-memory data models mirroring the blueprint's PostgreSQL schema,
so the pure-Python engine can be developed and tested without a database. Persistence
is layered on later (roadmap); these dataclasses are the contract every algorithm
consumes.

## Contract
Dataclasses in `src/fit_strong/models.py` (frozen where natural):

- `Sex` = Enum('male','female','other').
- `TrainingGoal` = Enum('muscle_gain','endurance','general_fitness').
- `FodmapGroup` = Enum('lactose','fructose','fructan','galactan','polyol','low_fodmap','unknown').
- `FodmapLevel` = Enum('high','medium','low','very_low').
- `Client(weight_kg, height_cm, sex, training_goal, weekly_sport_hours, birth_date=None, body_fat_pct=None, ...)`
  - validate: `weight_kg` in (0,400]; `height_cm` in (0,300]; `weekly_sport_hours` in [0,80];
    `body_fat_pct` in [0,75] if set.
- `FoodItem(name, amount_g, fodmap_group, fodmap_level)` — one eaten item.
  - validate: `amount_g` ≥ 0.
- `FoodRef(name, fodmap_group, fodmap_level, calories_per_100g, protein_per_100g,
  carbs_per_100g, fat_per_100g, fiber_per_100g, prebiotic_score, safe_portion_g=None,
  id=None, category=None, omega3_g_per_100g=0.0, timing_advice=None, source=None, extra={})` —
  reference DB row. `prebiotic_score` in [0,10]; macro values, safe portion and omega-3 are non-negative.
  Optional metadata supports the v2 library without forcing algorithm modules to depend on it.
- `Meal(recorded_at: datetime, meal_type, items: list[FoodItem], notes=None)`.
- `Symptom(recorded_at: datetime, bristol_stool=None, abdominal_pain=None, bloating=None,
  energy_level=None, fatigue_score=None, stress_level=None, sleep_hours=None)`.
  - validate ranges mirroring DB CHECKs: bristol 1–7; abdominal_pain/bloating/stress 0–10;
    energy_level/fatigue 1–10.
- `Workout(started_at: datetime, duration_min, intensity, workout_type=None,
  perceived_exertion=None)` — intensity 1–10; perceived_exertion (Borg) 6–20 if set.
- `CyclePhase` = Enum('menstrual','follicular','ovulatory','luteal','unknown').
- `MenstrualFlow` = Enum('light','medium','heavy').
- `MenstrualCycle(cycle_start_date, cycle_end_date=None, avg_cycle_length_days=None, symptoms={})`.
  - validate: start/end are ISO dates or `date`; end >= start; avg length in [15,45] if set.
- `HormonalSymptom(recorded_at, cycle_day=None, pelvic_pain=None, menstrual_flow=None,
  mood_irritability=None, headache=False, breast_tenderness=None, cycle_wellbeing=None, notes=None)`.
  - validate: cycle_day 1-45; pelvic/mood/breast 0-10; cycle_wellbeing 1-10.
- `Alert(alert_type, severity, message)` — severity in {info,warning,critical}.

## Business rules
- Construction validates and raises `ValueError` with a clear message (constitution §4).
- All datetimes are timezone-naive local for the engine; callers normalise.
- Enums accept their string value for ergonomic construction.

## Downstream impact
Every algorithm + the report engine import these. A field rename here ripples to all
consumers and their tests — change this spec first, then regenerate.

## Verification
`tests/test_models.py` — asserts valid construction, every range CHECK raising
`ValueError`, enum-from-string coercion, and cycle/hormonal range validation.


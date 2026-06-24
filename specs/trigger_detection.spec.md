---
id: spec-trigger-detection
type: transformation
version: 1.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-fodmap-load]
consumed_by: [spec-report-engine]
---

## Intent
Correlate eaten foods with GI complaints that appear 2–4 hours later, to surface the
top suspected trigger foods for a client. This is the engine's core differentiator:
turning a diary into actionable suspects.

## Contract
`detect_triggers(meals, symptoms, *, window_start_h=2.0, window_end_h=4.0,
pain_threshold=4.0, top_n=3) -> list[TriggerScore]` in
`src/fit_strong/algorithms/trigger_detection.py`. Pure (time comes from the records).

- For each meal, find symptoms whose `recorded_at` is in
  `[meal.recorded_at + window_start_h, meal.recorded_at + window_end_h]`.
- A symptom "counts" when `abdominal_pain >= pain_threshold` (bloating used as
  tie-breaker if pain is None).
- Each food item in a counting meal accrues
  `score += pain_value * suspicion(item.fodmap_level)` where
  `suspicion = {high:1.0, medium:0.6, low:0.3, very_low:0.1}`. This is the fix for the
  "innocent bystander" failure mode: a low-FODMAP food sharing a meal with the real
  culprit no longer ranks equally — high-FODMAP foods carry more suspicion, matching
  the evidence that they are the likely triggers.
- Also accumulate `occurrences` (number of counting windows the food appeared in) and
  the raw pains (so `avg_pain` reflects observed pain, not the weighted score).
- `TriggerScore(food_name, score, occurrences, avg_pain)` sorted by score desc, then
  occurrences desc, then name asc; return top `top_n`. Empty inputs → `[]`.

## Business rules
- Foods are matched by case-insensitive `name`.
- A meal with no symptom in its window contributes nothing.
- Ties broken deterministically (score, then occurrences, then name asc) so output is
  stable for tests.

## Evidence
- Symptom onset for FODMAP-sensitive foods typically 2–4 h post-ingestion; the
  correlation window mirrors the blueprint's Algorithm 1.

## Downstream impact
Report engine lists these as "Top suspected triggers" and may seed a FODMAP
elimination plan. Window/threshold changes alter which foods surface.

## Verification
`tests/test_trigger_detection.py` — a food eaten before in-window pain ranks #1; a food
eaten with no following symptoms scores 0; ordering & top_n cap; empty inputs; and the
high-FODMAP food outranks an innocent low-FODMAP food sharing the same meal.

---
id: spec-fodmap-load
type: transformation
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models]
consumed_by: [spec-report-engine, spec-trigger-detection]
---

## Intent
Quantify the cumulative FODMAP burden of a meal so the engine can flag high-load meals
and feed trigger detection. A single weighting table here is the source of truth.

## Contract
`fodmap_load(items: list[FoodItem]) -> float` in
`src/fit_strong/algorithms/fodmap_load.py`. Pure.

- Per item contribution = `amount_g * weight(fodmap_level)` where
  `high=0.08, medium=0.04, low=0.01, very_low=0.0`.
- `low_fodmap`/`unknown` group with `very_low` level → 0 contribution.
- Result = sum, rounded to 2 decimals.
- `meal_exceeds_threshold(items, threshold_g=15.0) -> bool` → True when load > threshold.

Note on weights: the blueprint pseudo-code used 0.8/0.4/0.1; that yields absurd loads
(50 g high food → 40 "g FODMAP"). Real per-portion FODMAP content is grams-to-
milligrams scale, so weights are scaled by 1/10 to 0.08/0.04/0.01. This keeps the
15 g/meal threshold meaningful. (Documented deviation — see Business rules.)

## Business rules
- Threshold default 15 g cumulative per meal → `high_fodmap` alert upstream.
- Empty meal → 0.0.
- Negative `amount_g` impossible (model validates).

## Evidence
- Low-FODMAP diet reduces GI symptoms in endurance athletes (systematic review).
- 48 h high-carb low-FODMAP pre-exertion protocol is effective.

## Downstream impact
Report engine fires `high_fodmap` alerts off `meal_exceeds_threshold`; trigger
detection uses load as a tie-breaker. Re-weighting changes both.

## Verification
`tests/test_fodmap_load.py` — per-level contributions, summation, empty meal,
threshold boundary (just below / above 15 g).

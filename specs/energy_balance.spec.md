---
id: spec-energy-balance
type: validation
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-macro-targets]
consumed_by: [spec-report-engine]
---

## Intent
Protect against under-fuelling (muscle-loss risk) and dehydration by validating a
day's intake against weight-scaled minimums and stool frequency. Produces `Alert`s the
report surfaces.

## Contract
`check_energy_balance(client, day_calories=None, day_protein_g=None, bristol_events=None) ->
list[Alert]` in `src/fit_strong/algorithms/energy_balance.py`. Pure.

- `min_calories = weight_kg * 30`; if `day_calories < min_calories` →
  `Alert('low_calories','warning', ...)` naming the minimum.
- `min_protein = weight_kg * 1.6`; if `day_protein_g < min_protein` →
  `Alert('low_protein','critical', ...)`.
- `bristol_events`: list of bristol_stool ints for the day. If count of values in
  {6,7} `> 3` → `Alert('dehydration_risk','warning', ...)` (fluid/potassium loss).
- No supplied problems → `[]`. Missing values skip only their own check; partial input remains valid.

## Business rules
- Uses the same 30 kcal/kg and 1.6 g/kg floors as `spec-macro-targets` (single source).
- Protein deficit is `critical` (muscle catabolism); calorie deficit is `warning`.
- Severity strings restricted to the model's allowed set.
- Negative calorie/protein inputs and Bristol values outside 1–7 raise `ValueError`.

## Evidence
- Energy availability < 30 kcal/kg/day risks muscle breakdown / low energy availability.
- Protein floor 1.6 g/kg for trained individuals.
- Repeated Bristol 6–7 (≥4/day) → fluid & potassium loss risk.

## Downstream impact
Report engine embeds these alerts and escalates `critical` ones. Threshold changes
alter alert frequency.

## Verification
`tests/test_energy_balance.py` — low-calorie, low-protein, dehydration each fire with
correct type/severity; an adequate day yields `[]`; partial protein and Bristol-only inputs still alert; invalid inputs raise; boundary at exactly the minimum.

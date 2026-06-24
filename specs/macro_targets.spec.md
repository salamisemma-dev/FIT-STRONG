---
id: spec-macro-targets
type: transformation
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models]
consumed_by: [spec-report-engine, spec-energy-balance]
---

## Intent
Compute daily macronutrient & energy targets from body weight, training goal, and
weekly sport load. These targets anchor every downstream advice and the energy-balance
alerts. Centralising the g/kg and kcal/kg constants here (with citations) prevents the
"magic number" drift the constitution forbids.

## Contract
`compute_macro_targets(client: Client) -> MacroTargets` in
`src/fit_strong/algorithms/macro_targets.py`. Pure function.

`MacroTargets(protein_g, carbs_g_low, carbs_g_high, energy_kcal_low, energy_kcal_high,
protein_g_per_kg, carbs_basis)` — all rounded to 1 decimal.

Rules (w = weight_kg):
- **Protein g/kg by goal:** muscle_gain → 2.0; endurance → 1.8; general_fitness → 1.6.
  `protein_g = w * g_per_kg`.
- **Carbs:** training load decides the band. `weekly_sport_hours >= 7` → intensive
  (5–7 g/kg, `carbs_basis="intensive"`); else moderate (3–5 g/kg, `"moderate"`).
  `carbs_g_low = w*low`, `carbs_g_high = w*high`.
- **Energy:** maintenance 30–35 kcal/kg → `energy_kcal_low = w*30`,
  `energy_kcal_high = w*35`. If goal == muscle_gain, add a surplus of +300 (low) /
  +500 (high) kcal.

## Business rules
- Bands (low/high) are returned, not a single point — advice presents a range.
- Function is pure; no rounding before the final field assignment beyond the documented
  1-decimal rounding.

## Evidence
- Protein 1.6–2.2 g/kg for athletes (ISSN; Wageningen athlete-intake data).
- Carbs 3–5 g/kg moderate, 5–7 g/kg intensive training.
- Energy 30–35 kcal/kg maintenance; +300–500 kcal surplus for muscle gain.

## Downstream impact
Report engine and energy-balance alerts read these thresholds. Changing a constant
changes alert firing — update this spec and `tests/test_macro_targets.py` together.

## Verification
`tests/test_macro_targets.py` — table-driven cases for each goal and both training
bands, asserting protein/carbs/energy and the muscle-gain surplus.

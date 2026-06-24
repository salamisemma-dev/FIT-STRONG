---
id: spec-daily-scheme
type: transformation
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-macro-targets, spec-fodmap-load]
consumed_by: [spec-report-artifacts, cli, fit-strong-skill]
---

## Intent
Produce a concrete **daily nutrition scheme** that approaches the client's macro/energy
targets using foods from the library, respecting FODMAP sensitivity. Turns the engine
from "analyse what you ate" into "here's a day to eat".

## Contract
`daily_scheme(client, food_db, *, fodmap_sensitive=False, meals=3, exclude_ids=()) ->
DailyScheme` in `src/fit_strong/algorithms/daily_scheme.py`. Pure (DB passed in).

Deterministic greedy planner:
- Candidate foods = `food_db` minus `exclude_ids`; if `fodmap_sensitive`, drop
  `fodmap_level == "high"`.
- Targets from `compute_macro_targets(client)`: aim for `protein_g`, carb midpoint
  `(carbs_g_low+carbs_g_high)/2`, energy midpoint.
- Select deterministically (sorted by metric desc, then id asc): up to 3 protein anchors
  (highest `protein_per_100g`), 2 carb sources (highest `carbs_per_100g`), 2 fibre/veg
  (highest `fiber_per_100g`). Assign each its `safe_portion_g` (fallback 100 g).
- Distribute selected items round-robin across `meals` meals.
- Compute totals (protein/carbs/energy/fibre) and `coverage` =
  `{protein_pct, carbs_pct, energy_pct}` vs target (rounded, capped at 100 for display? no —
  report raw so over/under is visible).

`DailyScheme(meals: list[SchemeMeal], totals: dict, target: dict, coverage: dict,
notes: list[str])`; `SchemeMeal(label, items: list[{id, amount_g}])`; `to_dict()`.

## Business rules
- **Honest about limits:** with a small DB the plan is repetitive; if a target cannot be
  met (e.g. protein < 80% achievable), add a `notes` entry saying so — never silently
  pretend coverage.
- Indicative meal plan, not a prescription; pair with the disclaimer.
- Empty/edge food_db → empty meals + a note.

## Downstream impact
HTML report renders the scheme as a table; weekly video may summarise coverage. DB growth
improves variety without code change.

## Verification
`tests/test_daily_scheme.py` — targets approached for a normal client; high-FODMAP foods
excluded when `fodmap_sensitive`; `exclude_ids` honoured; coverage computed; small-DB
under-coverage produces an honest note; determinism.

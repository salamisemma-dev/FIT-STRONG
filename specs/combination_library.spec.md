---
id: spec-combination-library
type: orchestration
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-cli-packaging]
consumed_by: [fit-strong-skill, cli, future-api]
---

## Intent
Maintain an expanded food and supplement library and generate deterministic, gut-aware
meal/supplement combinations from foods a user says are available. This turns the core
engine from only retrospective diary analysis into practical meal assembly.

## Contract
- `config/food_db.json` may use v2 shape `{version,last_updated,foods:[...]}` with
  `macros_per_100g`; `load_food_db()` must keep supporting the original list format.
- `config/supplement_db.json` stores supplement rows with dose, timing, FODMAP impact,
  interactions, source and issue fields.
- `config/combination_rules.json` stores deterministic rules with `good_combo`,
  `warning`, or `bad_combo` type.
- `src/fit_strong/combinations.py::recommend_combination(request, ...)` returns
  `recommended_combo`, `why`, `warnings`, `alternatives`, and `meta`.
- Request foods accepted as `available_foods` (terse) or `foods` (meal-doc) and each
  entry as a bare id string or `{id|name, amount_g}`; supplements likewise as
  `available_supplements` or `supplements`, string or `{id,...}`. A provided `amount_g`
  is honored in the output instead of the default safe portion. A populated request is
  never silently dropped because of its shape.

## Business rules
- Only recommend items present in `available_foods` / `available_supplements` and known
  to the corresponding DB; unknown foods are reported in `meta.unresolved_foods`.
- If `fodmap_sensitive` is true, high-FODMAP foods are not selected as default foods.
- Omega-3 fish oil is not added when selected food already supplies omega-3 rich fish.
- Caffeine is warned, not automatically recommended, for FODMAP-sensitive users.
- Packaged copies under `src/fit_strong/data/` must mirror config JSON so installed
  packages behave like the source checkout.
- Advice is practical and indicative, never medical or supplement-prescriptive.

## Downstream impact
The Claude skill can use this to suggest meal combinations. A future API can call the
same pure recommender with request JSON.

## Verification
`tests/test_combination_library.py` — validates v2 food loading, supplement/rule loading,
post-workout fish recommendation behavior, warning behavior, unresolved food reporting,
object/meal-doc request shapes with honored amounts, and config/package data mirror identity.

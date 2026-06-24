---
id: spec-microbiome-score
type: transformation
version: 1.0
status: approved
owner: fit-strong-core
depends_on: [spec-models]
consumed_by: [spec-report-engine]
---

## Intent
Give an indicative 0–100 "gut-feeding" score from a day's fibre intake and the
prebiotic quality of the foods eaten, reflecting the gut-muscle-axis pillar (feeding
*Roseburia*-type microbiota). Explicitly indicative, never diagnostic.

## Contract
`microbiome_score(items: list[FoodItem], food_db: Mapping[str, FoodRef]) ->
MicrobiomeScore` in `src/fit_strong/algorithms/microbiome_score.py`. Pure.

- For each item resolvable in `food_db` (case-insensitive name):
  `fiber_g += amount_g/100 * ref.fiber_per_100g`;
  `prebiotic_points += amount_g/100 * ref.prebiotic_score`.
- `fiber_component = min(fiber_g / 30.0, 1.0) * 60`  (30 g/day target → full 60 pts).
- `prebiotic_component = min(prebiotic_points / 20.0, 1.0) * 40`.
- `score = round(fiber_component + prebiotic_component, 1)` (0–100).
- `MicrobiomeScore(score, fiber_g, prebiotic_points, unresolved: list[str])` where
  `unresolved` lists item names not found in `food_db`.

## Business rules
- Items absent from `food_db` contribute 0 but are reported in `unresolved` (honesty:
  the score is only as good as the DB coverage).
- Empty day → score 0.0.

## Evidence
- ~30 g/day dietary fibre target (Dutch/EFSA guidance).
- Fermentable fibre/prebiotics feed SCFA-producing, muscle-supporting microbiota
  (gut-muscle axis; Roseburia inulinivorans association with grip strength).

## Downstream impact
Report engine shows the score + prebiotic advice. Re-scaling the 30 g / 20-pt anchors
shifts everyone's score.

## Verification
`tests/test_microbiome_score.py` — high-fibre+prebiotic day scores high; unknown foods
land in `unresolved` and score 0; empty day 0.0; caps at 100.

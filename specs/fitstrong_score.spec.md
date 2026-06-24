---
id: spec-fitstrong-score
type: transformation
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-macro-targets, spec-fodmap-load, spec-microbiome-score]
consumed_by: [spec-report-artifacts, cli, fit-strong-skill]
---

## Intent
Answer the user's actual question — "hoe fit & strong ben ik en wat kan ik beter doen?"
— with a single composite **Fit & Strong score (0–100)** built from transparent
subscores, plus a prioritised list of improvements. This is the consolidation the engine
lacked: alerts were scattered, there was no headline number.

## Contract
`fitstrong_score(client, day_calories, day_protein_g, meal_items, food_db, *, workouts=None,
symptoms=None) -> FitStrongScore` in `src/fit_strong/algorithms/fitstrong_score.py`. Pure.

Subscores, each 0–100:
- **protein** = `min(day_protein_g / target.protein_g, 1) * 100` (target from spec-macro-targets).
- **energy** = 100 if `energy_kcal_low ≤ day_calories ≤ energy_kcal_high`; below low →
  `day_calories/low*100`; above high → `max(0, 100 - (day_calories-high)/high*100)`.
- **microbiome** = `microbiome_score(meal_items, food_db).score` (spec-microbiome-score).
- **fodmap** = `clamp(100 - day_load / 45 * 100, 0, 100)`, `day_load = fodmap_load(meal_items)`.
- **training** (only if `workouts` given OR weekly_sport_hours) =
  `min(weekly_sport_hours / 5, 1) * 100`.
- **symptoms** (only if `symptoms` given) = `clamp(100 - worst_discomfort*10, 0, 100)` where
  `worst_discomfort = max(abdominal_pain, bloating, 0)` over the day.

Weights: protein .25, energy .20, microbiome .20, fodmap .15, training .10, symptoms .10.
Absent components are dropped and remaining weights **renormalised** (no fabricated zeros).

`FitStrongScore(score, band, subscores: dict[str,float], components_used: list[str],
improvements: list[Improvement])`:
- `band`: <40 "aandacht nodig"; 40–60 "matig"; 60–80 "goed"; ≥80 "sterk".
- `improvements`: one `Improvement(area, score, action)` per subscore < 70, **worst first**.
- `to_dict()` for JSON/report.

## Business rules
- The composite is a **heuristic, not a validated clinical index** — labelled indicative
  in every consumer; weights + cut-offs recorded in `docs/EVIDENCE.md` (confidence: Hypothesis).
- Deterministic: identical inputs → identical score (all upstream pure).
- Never emits a component it had no data for.

## Evidence
Subscore thresholds reuse cited engine values (protein g/kg, energy kcal/kg, fibre 30 g,
FODMAP load); the **weighting** is an editorial heuristic — see `docs/EVIDENCE.md`.

## Downstream impact
The HTML report + weekly video headline this score and list improvements. Reweighting
shifts every user's score — change this spec + `tests/test_fitstrong_score.py` together.

## Verification
`tests/test_fitstrong_score.py` — subscore math per branch (in-range/below/above energy),
weight renormalisation when symptoms/training absent, band thresholds, improvements sorted
worst-first, determinism.

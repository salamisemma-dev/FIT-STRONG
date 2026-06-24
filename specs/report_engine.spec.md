---
id: spec-report-engine
type: orchestration
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-models, spec-macro-targets, spec-fodmap-load, spec-trigger-detection, spec-energy-balance, spec-microbiome-score]
consumed_by: [cli, fit-strong-skill]
---

## Intent
Compose the pure algorithms into one personalised report for a client over a diary
window — the single entry point the CLI and Claude skill call. Keeps orchestration out
of the algorithm modules (constitution §4 layering).

## Contract
`generate_report(client, meals, symptoms, workouts, food_db, *, day_calories=None,
day_protein_g=None, bristol_events=None, no_improvement_weeks=0.0) -> Report` in
`src/fit_strong/engine.py`.

`Report` fields:
- `macro_targets: MacroTargets`
- `triggers: list[TriggerScore]`
- `alerts: list[Alert]` (energy-balance + one `high_fodmap` alert per meal over
  threshold)
- `microbiome: MicrobiomeScore | None` (computed over all items in `meals`)
- `disclaimer: str` (fixed medical disclaimer; constitution §4)
- `referral_advice: str | None` (set when caller flags ≥4–6 weeks no improvement)
- `to_dict() -> dict` for JSON/CLI output.

## Business rules
- `disclaimer` is always present and non-empty.
- If `day_calories`, `day_protein_g`, or `bristol_events` are omitted, only the missing checks are skipped
  (no fabricated numbers — honesty over completeness). Partial input still produces valid alerts.
- Report is deterministic given identical inputs (all algos are pure).
- When `food_db` is provided, known meal item names are resolved to the DB FODMAP group/level before trigger and high-FODMAP alert checks.
- A known item above `safe_portion_g` produces a high-FODMAP meal alert even when the synthetic load is below threshold.

## Downstream impact
CLI and the Claude skill render `to_dict()`. Field changes ripple to both.

## Verification
`tests/test_engine.py` — end-to-end report from a small fixture diary asserts targets,
≥1 trigger, a high-FODMAP alert, microbiome score present, DB-backed FODMAP resolution, safe-portion alerting, partial Bristol alerting, disclaimer non-empty, and
`to_dict()` round-trips the structure.

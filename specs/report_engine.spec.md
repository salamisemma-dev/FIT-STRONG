---
id: spec-report-engine
type: orchestration
version: 1.0
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
day_protein_g=None, bristol_events=None) -> Report` in
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
- If `day_calories`/`day_protein_g`/`bristol_events` omitted, energy-balance is skipped
  (no fabricated numbers — honesty over completeness).
- Report is deterministic given identical inputs (all algos are pure).

## Downstream impact
CLI and the Claude skill render `to_dict()`. Field changes ripple to both.

## Verification
`tests/test_engine.py` — end-to-end report from a small fixture diary asserts targets,
≥1 trigger, a high-FODMAP alert, microbiome score present, disclaimer non-empty, and
`to_dict()` round-trips the structure.

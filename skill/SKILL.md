---
name: fit-strong
description: Evidence-based nutrition & training coach (NL). Use when a user wants gut-friendly sports-nutrition coaching, FODMAP trigger analysis, macro/energy targets, or a food/symptom/training diary turned into personal advice. Triggers: "fit and strong", "fit & strong", "darmklachten sporter", "FODMAP analyse", "voedingsadvies", "macro berekenen", "triggervoeding", "microbioom score". Built on the gut-muscle axis, SCFA, FODMAP-restriction and training-load evidence base.
---

# Fit & Strong — coaching skill

Turns a client's diary (food, symptoms, training) into a personalised, evidence-based
report: macro/energy targets, suspected FODMAP triggers, energy-balance & dehydration
alerts, and an indicative gut-microbiome score. **Indicative, not medical** — every
report carries a disclaimer and escalates to a dietitian when warranted.

The science and exact thresholds live in `../constitution.md` and `../specs/`. This
skill is a thin wrapper: gather data → call the engine → interpret the JSON in plain NL.

## When to use
Any request about gut-friendly sports nutrition, FODMAP triggers, macro/energy needs,
or "analyseer mijn voedingsdagboek". For ad-hoc single numbers (just a macro calc) you
can still call the engine — it's cheap.

## Workflow (4 phases, mirrors the blueprint)

### Phase 0 — Intake
Collect, conversationally: weight_kg, height_cm, sex, training_goal
(`muscle_gain`/`endurance`/`general_fitness`), weekly_sport_hours. Optional:
body_fat_pct, current PDS-complaints, medication/supplements. Never invent values —
ask.

### Phase 1 — Diary
Help the user log meals (time, foods + grams, FODMAP group/level if known), symptoms
(Bristol 1–7, abdominal_pain 0–10, bloating 0–10, energy_level 1–10), and workouts.
Assemble into the diary JSON shape in `../examples/sample_diary.json`.

### Phase 2 — Analysis (run the engine)
From the repo root:
```bash
fit-strong <diary.json> --food-db config/food_db.json
# source checkout without install: PowerShell `$env:PYTHONPATH="src"; python -m fit_strong.cli <diary.json> --food-db config/food_db.json`
```
This returns the full report as JSON. (Or import `fit_strong.generate_report` directly.)

### Phase 3 — Advice (interpret the JSON, in Dutch)
- **macro_targets** → present protein (g), carb band (g, moderate/intensive) and energy
  range. Add pre/post-workout timing (pre 1–2 g/kg carbs low-FODMAP; post 25 g eiwit +
  ~40 g snelle koolhydraten).
- **triggers** → "Top verdachte triggers" — the highest-scoring foods. High-FODMAP
  foods are weighted as more suspect; explain the 2–4 h correlation.
- **alerts** → surface every alert; treat `critical` (low_protein) urgently;
  `dehydration_risk` → vocht/kalium advies.
- **microbiome** → score /100 + prebiotic advice (geleidelijk vezels opbouwen uit
  darmvriendelijke bronnen: gekookte wortel, courgette, havermout, quinoa). Mention any
  `unresolved` foods (not in the DB → score is conservative).
- Always read out **disclaimer**; if `referral_advice` is set, advise a dietitian.

## Rules
- Indicative, never diagnostic. No medication advice.
- Don't fabricate intake numbers; omit energy-balance if calories/protein unknown
  (the engine already skips it — honesty over completeness).
- FODMAP elimination is a 3-phase clinical protocol (eliminatie → herintroductie →
  personalisatie); only suggest strict elimination when triggers clearly warrant it,
  and flag that long-term low-FODMAP may harm the microbiome.

## Verify before claiming done
Run `python -m unittest discover -s tests` and `node scripts/bob_validate.mjs --strict .`
from the repo root — both must be green.

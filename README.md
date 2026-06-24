# Fit & Strong

Evidence-based nutrition & training coaching **engine** + Claude skill. Turns a
food/symptom/training diary into personalised advice grounded in four research pillars:
the **gut-muscle axis**, **SCFA fuel**, **FODMAP restriction**, and **training load ↔
gut health**.

> Advice is **indicative, not medical**. Every report carries a disclaimer and advises
> a dietitian when no improvement is seen after 4–6 weeks.

## What it computes
| Module | Output |
|--------|--------|
| `compute_macro_targets` | Protein (g), carb band (moderate/intensive), energy range; +surplus for muscle gain |
| `fodmap_load` | Cumulative FODMAP burden per meal + 15 g threshold flag |
| `detect_triggers` | Top suspected trigger foods (2–4 h correlation, FODMAP-weighted) |
| `check_energy_balance` | Low-calorie / low-protein / dehydration alerts |
| `microbiome_score` | Indicative 0–100 gut-feeding score (fibre + prebiotic quality) |
| `generate_report` | All of the above, composed into one report |

## Quickstart
```bash
# Install locally, then run the engine on the sample diary
python -m pip install -e . --no-deps
fit-strong examples/sample_diary.json --food-db config/food_db.json

# From a source checkout without installing
$env:PYTHONPATH="src"; python -m fit_strong.cli examples/sample_diary.json --food-db config/food_db.json

# Tests (stdlib unittest, zero dependencies)
python -m unittest discover -s tests

# Spec / anti-drift gate
node scripts/bob_validate.mjs --strict .
```

Or as a library:
```python
import fit_strong as fs
client = fs.Client(weight_kg=80, height_cm=180, sex="male",
                   training_goal="muscle_gain", weekly_sport_hours=8)
report = fs.generate_report(client, meals, symptoms, food_db=fs.load_food_db())
print(report.to_dict())
```

## Project layout (BOB / spec-driven)
```
constitution.md          # supreme contract (tech standards, layering, evidence policy)
specs/*.spec.md          # 8 executable specs — permanent system memory
src/fit_strong/          # models -> algorithms (pure) -> engine -> cli
src/fit_strong/data/     # packaged food DB (install-safe copy of config/food_db.json)
config/food_db.json      # editable source food DB (FODMAP + macros + prebiotic score)
tests/                   # 44 unittest cases, one file per spec
scripts/bob_validate.mjs # spec + food-DB drift gate (CI)
scripts/bob_ready.mjs    # validate + tests in one gate (CI)
skill/SKILL.md           # Claude coaching-skill wrapper
docs/PVA.md              # plan van aanpak: pros, cons, and the fix for each con
docs/EVIDENCE.md         # every threshold + source + confidence level (honest)
docs/TRACEABILITY.md     # spec clause -> test method matrix
examples/sample_diary.json
```

## Status
Core engine complete & green (43 tests). Web frontend, Postgres persistence, auth and
ML are **roadmap** — see [docs/PVA.md](docs/PVA.md). The engine is deliberately free of
those concerns so they layer on without a rewrite.

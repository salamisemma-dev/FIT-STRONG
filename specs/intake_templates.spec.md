---
id: spec-intake-templates
version: 1.0.0
status: approved
owner: fit-strong-core
type: artifact
depends_on: [spec-models, spec-cycle-hormone]
consumed_by: [templates/voedingsdagboek_template_man.docx, templates/voedingsdagboek_template_vrouw.docx, docs/APP_PVA.md]
---

# Intake Templates Spec

The repository must provide novice-friendly Word diary templates that match the engine's
input concepts without requiring users to understand JSON.

## Contract

- `templates/voedingsdagboek_template_man.docx` exists and includes daily fields for:
  day/person, meals, drinks, supplements, symptoms, stool/Bristol, training, sleep,
  stress, hydration, day totals, and analysis readiness.
- `templates/voedingsdagboek_template_vrouw.docx` exists and includes all shared fields
  plus an optional `Cycluscontext` block.
- The male template must not require menstrual/cycle fields.
- Both templates must clearly state that unknown values can be left blank and that the
  tool is indicative, not medical advice.
- The app plan in `docs/APP_PVA.md` must define novice-first daily capture and JSON export
  toward the engine.

## Verification

`tests/test_intake_templates.py` checks the DOCX text and app PvA for required sections.



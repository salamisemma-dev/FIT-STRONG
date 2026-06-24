---
id: spec-cli-packaging
type: orchestration
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-report-engine, spec-models]
consumed_by: [cli, fit-strong-skill, ci]
---

## Intent
Make the CLI and default food database usable from both the source checkout and an
installed package. The coaching skill may run from a repo, while users and CI may call
the `fit-strong` console script after installation.

## Contract
- `pyproject.toml` exposes `fit-strong = "fit_strong.cli:main"`.
- `src/fit_strong/food_db.py::load_food_db(None)` loads the default database without
  requiring the repository-level `config/food_db.json` to exist.
- `src/fit_strong/cli.py::run(...)` does not mutate the parsed diary structure while
  constructing dataclasses.

## Business rules
- The package remains stdlib-only at runtime.
- The repository-level `config/food_db.json` remains the editable source copy; packaged
  data (`src/fit_strong/data/food_db.json`) is the install-safe fallback.
- The two copies MUST stay content-identical. `scripts/bob_validate.mjs` enforces this
  (CRLF-normalised) as a project drift gate, so the "fallback mirrors source" claim is
  machine-checked, not aspirational.
- CLI output must stay UTF-8 JSON.

## Downstream impact
README, CI, and `skill/SKILL.md` commands must stay honest about whether they run from
source (`PYTHONPATH=src`) or an installed package (`fit-strong`).

## Verification
`tests/test_cli_packaging.py` — asserts default food DB fallback loads when the repo
config path is unavailable, `run(...)` does not mutate symptom/workout records, and the
source DB (`config/food_db.json`) and packaged copy are content-identical. The
`scripts/bob_validate.mjs` food-DB drift gate enforces the same identity in CI.

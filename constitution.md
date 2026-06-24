# Fit & Strong — Constitution

**Version:** 1.0.0
**Status:** ratified
**Last updated:** 2026-06-24

The supreme contract for the Fit & Strong project. Every spec, module, and test
conforms to this document. Change this first when a rule must change.

---

## 1. Purpose & scope

Fit & Strong is an **evidence-based nutrition & training coaching engine**. It turns
a client's food/symptom/training diary into personalised advice grounded in four
research pillars:

1. **Gut-muscle axis** — fibre/prebiotics feed muscle-supporting microbiota
   (*Roseburia inulinivorans*).
2. **SCFA fuel** — short-chain fatty acids from fermentable fibre support muscle &
   gut wall.
3. **FODMAP restriction** — lowering FODMAP load reduces GI complaints in athletes.
4. **Training load ↔ gut health** — intensity shapes microbiome & recovery needs.

**In scope (this engine):** pure-Python calculation core — macro targets, FODMAP
load, trigger detection, energy-balance alerts, microbiome score — plus typed data
models, a reference food database loader, a CLI, and a Claude skill wrapper.

**Out of scope (roadmap):** web frontend, persistence layer / Postgres, auth,
notifications, ML models. The engine MUST stay free of those concerns so they can be
layered on later.

---

## 2. Technology standards

- **Language:** Python ≥ 3.11. Standard library only for the core engine — **no
  third-party runtime dependencies**. Tests use `unittest` (stdlib).
- **Typing:** every public function and data model is fully type-annotated. Models
  are `@dataclass`. Mutable default args are forbidden.
- **Purity:** algorithm functions in `src/fit_strong/algorithms/` are **pure** — no
  I/O, no clock reads, no globals. Time and data are passed in as arguments. This is
  what makes them deterministically testable.
- **Units:** SI + explicit suffixes in names (`weight_kg`, `amount_g`,
  `duration_min`, `energy_kcal`). Never store a bare number whose unit is ambiguous.

---

## 3. Naming conventions

- Modules & functions: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE`.
- One algorithm concept per module; module name matches the spec id
  (`macro_targets.py` ↔ `spec-macro-targets`).
- Public API is re-exported from `src/fit_strong/__init__.py`.

---

## 4. Architecture rules

- **Layering:** `models` (data) → `algorithms` (pure logic) → `engine` (orchestration)
  → `cli` / skill. A lower layer never imports a higher one.
- **No silent clamping that hides bad input.** Validate at construction
  (dataclass `__post_init__`) and raise `ValueError` with a clear message at system
  boundaries. Ranges mirror the DB CHECK constraints in the blueprint.
- Files stay under 500 lines. Split by spec, not by convenience.
- Advice is **indicative, not medical**. Every generated report carries a disclaimer
  and a referral trigger (no improvement after 4–6 weeks → advise dietitian).

---

## 5. Evidence traceability

Every algorithm threshold (g/kg, kcal/kg, FODMAP weights, 2–4h correlation window)
MUST cite its source in the owning spec's **Evidence** section, and appear in
`docs/EVIDENCE.md` with a **confidence level** (Strong / Moderate / Hypothesis) and an
honest caveat where the value is a simplification. A magic number with no citation, or a
claim of certainty above its evidence, is a constitution violation. Thresholds marked
*Hypothesis* may drive only *indicative* output — never absolute medical thresholds.

---

## 6. Verification policy

- No code without an approved spec whose **Verification** section names a real test.
- Every spec maps to at least one test in `tests/`; the validator
  (`scripts/bob_validate.mjs --strict .`) enforces spec→test traceability at file level
  and fails CI on drift. Clause-level mapping (each acceptance criterion → test method)
  is maintained in `docs/TRACEABILITY.md`.
- `python -m unittest discover -s tests` MUST be green before any task is "done".

---

## 7. Governance

This constitution is the authority. Specs refine it; code implements specs. To change
behaviour: amend the spec (and this file if a rule changes), get approval, then change
code. Deviations from a rule here are DRIFT until this file is amended and the change
recorded in the commit message.

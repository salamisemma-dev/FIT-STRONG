# Spec → test traceability matrix

`scripts/bob_validate.mjs` enforces traceability at **file level** (every spec's
`## Verification` must name an existing test file). This matrix adds the **clause level**:
each spec's acceptance criteria mapped to the specific test method that exercises it.

It is **maintained by hand** — not yet machine-enforced per clause. That honest limit is
recorded in `docs/PVA.md` (N8) and the backlog below. Run `python -m unittest discover -s
tests` to execute every method named here.

## spec-models → `tests/test_models.py`
| Criterion | Test method |
|---|---|
| Valid client constructs; enums coerce from value | `test_valid_client`, `test_enum_coercion_from_string` |
| weight/height/sport-hours range CHECKs raise | `test_client_weight_range` |
| Symptom range CHECKs (Bristol, pain, energy) raise | `test_symptom_range_checks` |
| FoodItem amount ≥ 0 and non-empty name | `test_food_item_negative_amount` |
| Workout intensity / Borg range raise | `test_workout_borg_range` |
| FoodRef numeric ranges (calories ≥0, prebiotic 0–10) raise | `test_food_ref_numeric_ranges` |
| Alert severity restricted; `to_dict` | `test_alert_severity_and_dict` |

## spec-macro-targets → `tests/test_macro_targets.py`
| Criterion | Test method |
|---|---|
| Protein g/kg per goal (2.0/1.8/1.6) | `test_protein_by_goal` |
| Carb band switch at ≥7 h/wk | `test_carbs_band_switch` |
| Energy 30–35 kcal/kg maintenance | `test_energy_maintenance` |
| +300/+500 kcal muscle-gain surplus | `test_muscle_gain_surplus` |

## spec-fodmap-load → `tests/test_fodmap_load.py`
| Criterion | Test method |
|---|---|
| Per-level weights 0.08/0.04/0.01/0 | `test_per_level_contribution` |
| Summation over items | `test_summation` |
| Empty meal → 0.0 | `test_empty_meal` |
| 15 g threshold boundary (below/above) | `test_threshold_boundary` |

## spec-trigger-detection → `tests/test_trigger_detection.py`
| Criterion | Test method |
|---|---|
| In-window pain ranks the food #1 | `test_in_window_pain_ranks_first` |
| Symptom outside 2–4 h window → no score | `test_no_following_symptom_scores_nothing` |
| Ordering + `top_n` cap | `test_ordering_and_top_n` |
| Bloating counts when pain is low | `test_bloating_counts_when_pain_low` |
| Bloating counts when pain is None | `test_bloating_counts_when_pain_none` |
| Innocent low-FODMAP bystander not surfaced | `test_high_fodmap_suppresses_innocent_bystander` |
| Empty inputs → [] | `test_empty_inputs` |

## spec-energy-balance → `tests/test_energy_balance.py`
| Criterion | Test method |
|---|---|
| Adequate day → no alerts | `test_adequate_day_no_alerts` |
| Low calories → warning | `test_low_calories_warning` |
| Low protein → critical | `test_low_protein_critical` |
| Partial input: protein only still alerts | `test_partial_low_protein_still_alerts` |
| Partial input: Bristol only still alerts | `test_dehydration_risk_without_macro_inputs` |
| Dehydration cut-off (>3 loose) incl. boundary | `test_dehydration_risk` |
| Invalid (negative cal/protein, Bristol 8) raise | `test_invalid_inputs_raise` |
| Boundary exactly at floor → no alert | `test_boundary_at_minimum` |

## spec-microbiome-score → `tests/test_microbiome_score.py`
| Criterion | Test method |
|---|---|
| Empty day → 0.0 | `test_empty_day_zero` |
| High fibre + prebiotic → high score | `test_high_fibre_prebiotic_scores_high` |
| Unknown food → `unresolved`, 0 contribution | `test_unknown_food_unresolved_and_zero` |
| Score caps at 100 | `test_caps_at_100` |

## spec-report-engine → `tests/test_engine.py`
| Criterion | Test method |
|---|---|
| End-to-end report (targets, triggers, alerts, micro, disclaimer, referral) | `test_end_to_end_report` |
| `to_dict()` structure round-trips | `test_to_dict_roundtrip` |
| Energy-balance skipped when intake omitted | `test_energy_balance_skipped_without_intake` |
| food_db resolves unlabelled diary items for alerts+triggers | `test_food_db_resolves_missing_fodmap_labels_for_alerts_and_triggers` |
| `safe_portion_g` excess fires high_fodmap even at low synthetic load | `test_safe_portion_excess_fires_even_when_synthetic_load_is_low` |
| Partial Bristol-only input still alerts | `test_partial_bristol_events_still_alert` |

## spec-cli-packaging → `tests/test_cli_packaging.py`
| Criterion | Test method / gate |
|---|---|
| Default food DB loads without repo `config/` (install fallback) | `test_default_food_db_has_packaged_fallback` |
| `run(...)` does not mutate parsed diary | `test_run_does_not_mutate_loaded_diary` |
| Source DB and packaged copy are content-identical | `test_food_db_source_and_packaged_copy_are_identical` + `bob_validate.mjs` library drift gate |

## spec-fitstrong-score → `tests/test_fitstrong_score.py`
| Criterion | Test method |
|---|---|
| Energy subscore in-range / below / above branches | `test_energy_in_range_below_above` |
| Weights renormalise when components absent | `test_weight_renormalisation_when_components_absent` |
| Band thresholds + improvements sorted worst-first | `test_band_thresholds_and_improvements_sorted` |
| Microbiome/FODMAP/training/symptoms components | `test_microbiome_and_fodmap_and_training_components` |
| Deterministic | `test_deterministic` |

## spec-daily-scheme → `tests/test_daily_scheme.py`
| Criterion | Test method |
|---|---|
| High-FODMAP excluded when sensitive | `test_high_fodmap_excluded_when_sensitive` |
| Not force-dropped when not sensitive (+ indicatief note) | `test_high_fodmap_allowed_when_not_sensitive` |
| `exclude_ids` honoured | `test_exclude_ids_honoured` |
| Coverage + totals present, 3 meals | `test_coverage_and_totals_present` |
| Empty DB → honest note | `test_empty_db_note` |
| Deterministic | `test_deterministic` |

## spec-report-artifacts → `tests/test_report_artifacts.py`
| Criterion | Test method |
|---|---|
| HTML self-contained (score, disclaimer, scheme row, no external assets) | `test_render_html_self_contained` |
| HTML without scheme omits scheme section | `test_render_html_without_scheme` |
| `weekly_video_props` JSON-serialisable, ≤3 improvements | `test_weekly_video_props_json_serialisable` |

## Backlog (toward machine-enforced clause traceability)
Annotate each test with its spec-clause id (e.g. a `# trace: spec-macro-targets/protein`
marker) and extend `bob_validate.mjs` to assert every enumerated clause has ≥1 matching
marker. Until then this matrix is the reviewed contract.


## spec-combination-library
- v2 food DB loads by ID and legacy name -> `tests/test_combination_library.py::test_v2_food_db_loads_by_id_and_legacy_name`
- supplement/rule loading and normalized dose output -> `tests/test_combination_library.py::test_supplements_and_rules_load`
- post-workout fish combo skips redundant omega-3 -> `tests/test_combination_library.py::test_post_workout_fish_combo_skips_extra_omega3`
- sensitive gut filters high-FODMAP and warns caffeine/fat timing -> `tests/test_combination_library.py::test_sensitive_gut_filters_high_fodmap_and_warns_caffeine`
- unknown available foods are surfaced -> `tests/test_combination_library.py::test_unresolved_foods_are_reported`
- config/package data mirrors stay identical -> `tests/test_combination_library.py::test_config_and_packaged_library_copies_are_identical`
- rule ingredients reference known library items -> `tests/test_combination_library.py::test_rule_ingredients_reference_known_library_items`
- object/meal-doc request shapes accepted, requested amount honored -> `tests/test_combination_library.py::test_accepts_object_request_shapes`

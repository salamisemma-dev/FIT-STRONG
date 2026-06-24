"""Report orchestration — implements spec-report-engine.

Composes the pure algorithms into one personalised, deterministic report. The only
entry point the CLI and the Claude skill call (constitution §4 layering).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional

from .algorithms.energy_balance import check_energy_balance
from .algorithms.fodmap_load import fodmap_load, meal_exceeds_threshold
from .algorithms.macro_targets import MacroTargets, compute_macro_targets
from .algorithms.microbiome_score import MicrobiomeScore, microbiome_score
from .algorithms.trigger_detection import TriggerScore, detect_triggers
from .models import Alert, Client, FoodItem, FoodRef, Meal, Severity, Symptom, Workout

DISCLAIMER = (
    "Dit advies is indicatief en geen medisch advies. Bij aanhoudende klachten of "
    "alarmsignalen: raadpleeg een (sport)diëtist of arts."
)
REFERRAL_ADVICE = (
    "Geen verbetering na 4–6 weken consequent opvolgen — doorverwijzing naar een "
    "diëtist of (sport)arts aanbevolen."
)


@dataclass
class Report:
    macro_targets: MacroTargets
    triggers: list[TriggerScore]
    alerts: list[Alert]
    microbiome: Optional[MicrobiomeScore] = None
    disclaimer: str = DISCLAIMER
    referral_advice: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "macro_targets": self.macro_targets.to_dict(),
            "triggers": [t.to_dict() for t in self.triggers],
            "alerts": [a.to_dict() for a in self.alerts],
            "microbiome": self.microbiome.to_dict() if self.microbiome else None,
            "disclaimer": self.disclaimer,
            "referral_advice": self.referral_advice,
            "meta": self.meta,
        }


def _food_db_by_name(food_db: Mapping[str, FoodRef]) -> dict[str, FoodRef]:
    return {key.strip().lower(): value for key, value in food_db.items()}


def _resolve_meals(meals: list[Meal], food_db: Mapping[str, FoodRef]) -> list[Meal]:
    by_name = _food_db_by_name(food_db)
    if not by_name:
        return meals

    resolved: list[Meal] = []
    for meal in meals:
        items: list[FoodItem] = []
        for item in meal.items:
            ref = by_name.get(item.name.strip().lower())
            if ref is None:
                items.append(item)
                continue
            items.append(FoodItem(item.name, item.amount_g, ref.fodmap_group, ref.fodmap_level))
        resolved.append(Meal(meal.recorded_at, meal.meal_type, items, meal.notes))
    return resolved


def _meal_exceeds_safe_portion(meal: Meal, food_db: Mapping[str, FoodRef]) -> bool:
    by_name = _food_db_by_name(food_db)
    for item in meal.items:
        ref = by_name.get(item.name.strip().lower())
        if ref and ref.safe_portion_g is not None and item.amount_g > ref.safe_portion_g:
            return True
    return False


def generate_report(
    client: Client,
    meals: list[Meal],
    symptoms: list[Symptom],
    workouts: Optional[list[Workout]] = None,
    food_db: Optional[Mapping[str, FoodRef]] = None,
    *,
    day_calories: Optional[float] = None,
    day_protein_g: Optional[float] = None,
    bristol_events: Optional[list[int]] = None,
    no_improvement_weeks: float = 0.0,
) -> Report:
    food_db = food_db or {}
    workouts = workouts or []
    resolved_meals = _resolve_meals(meals, food_db)

    macro_targets = compute_macro_targets(client)
    triggers = detect_triggers(resolved_meals, symptoms)

    alerts: list[Alert] = []
    # One high_fodmap alert per meal over threshold or configured safe portion.
    for meal in resolved_meals:
        if meal_exceeds_threshold(meal.items) or _meal_exceeds_safe_portion(meal, food_db):
            alerts.append(Alert(
                "high_fodmap", Severity.WARNING,
                f"Hoge FODMAP-belasting bij {meal.meal_type.value} "
                f"({meal.recorded_at:%Y-%m-%d %H:%M}): load {fodmap_load(meal.items)}.",
            ))
    # Energy-balance is partial-input safe: no fabricated numbers, no dropped Bristol alert.
    if day_calories is not None or day_protein_g is not None or bristol_events is not None:
        alerts.extend(check_energy_balance(client, day_calories, day_protein_g, bristol_events))

    micro: Optional[MicrobiomeScore] = None
    if food_db:
        all_items = [item for meal in resolved_meals for item in meal.items]
        micro = microbiome_score(all_items, food_db)

    referral = REFERRAL_ADVICE if no_improvement_weeks >= 4 else None

    return Report(
        macro_targets=macro_targets,
        triggers=triggers,
        alerts=alerts,
        microbiome=micro,
        referral_advice=referral,
        meta={
            "client": client.name,
            "n_meals": len(meals),
            "n_symptoms": len(symptoms),
            "n_workouts": len(workouts),
        },
    )

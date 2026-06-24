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
from .models import Alert, Client, FoodRef, Meal, Severity, Symptom, Workout

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

    macro_targets = compute_macro_targets(client)
    triggers = detect_triggers(meals, symptoms)

    alerts: list[Alert] = []
    # One high_fodmap alert per meal over threshold.
    for meal in meals:
        if meal_exceeds_threshold(meal.items):
            alerts.append(Alert(
                "high_fodmap", Severity.WARNING,
                f"Hoge FODMAP-belasting bij {meal.meal_type.value} "
                f"({meal.recorded_at:%Y-%m-%d %H:%M}): load {fodmap_load(meal.items)}.",
            ))
    # Energy-balance only when intake numbers are supplied (no fabricated data).
    if day_calories is not None and day_protein_g is not None:
        alerts.extend(check_energy_balance(client, day_calories, day_protein_g, bristol_events))

    micro: Optional[MicrobiomeScore] = None
    if food_db:
        all_items = [item for meal in meals for item in meal.items]
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

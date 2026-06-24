"""Daily macro & energy targets — implements spec-macro-targets. Pure."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Client, TrainingGoal

# g/kg protein by goal (constitution §5: cited in spec-macro-targets).
_PROTEIN_G_PER_KG = {
    TrainingGoal.MUSCLE_GAIN: 2.0,
    TrainingGoal.ENDURANCE: 1.8,
    TrainingGoal.GENERAL_FITNESS: 1.6,
}
_INTENSIVE_HOURS = 7.0          # weekly sport hours at/above which carbs band is intensive
_CARBS_MODERATE = (3.0, 5.0)    # g/kg
_CARBS_INTENSIVE = (5.0, 7.0)   # g/kg
_ENERGY_KCAL_PER_KG = (30.0, 35.0)
_MUSCLE_GAIN_SURPLUS = (300.0, 500.0)  # +kcal low/high


@dataclass
class MacroTargets:
    protein_g: float
    carbs_g_low: float
    carbs_g_high: float
    energy_kcal_low: float
    energy_kcal_high: float
    protein_g_per_kg: float
    carbs_basis: str  # "moderate" | "intensive"

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def compute_macro_targets(client: Client) -> MacroTargets:
    w = client.weight_kg
    g_per_kg = _PROTEIN_G_PER_KG[client.training_goal]

    if client.weekly_sport_hours >= _INTENSIVE_HOURS:
        carbs_basis, (c_low, c_high) = "intensive", _CARBS_INTENSIVE
    else:
        carbs_basis, (c_low, c_high) = "moderate", _CARBS_MODERATE

    e_low, e_high = w * _ENERGY_KCAL_PER_KG[0], w * _ENERGY_KCAL_PER_KG[1]
    if client.training_goal == TrainingGoal.MUSCLE_GAIN:
        e_low += _MUSCLE_GAIN_SURPLUS[0]
        e_high += _MUSCLE_GAIN_SURPLUS[1]

    return MacroTargets(
        protein_g=round(w * g_per_kg, 1),
        carbs_g_low=round(w * c_low, 1),
        carbs_g_high=round(w * c_high, 1),
        energy_kcal_low=round(e_low, 1),
        energy_kcal_high=round(e_high, 1),
        protein_g_per_kg=g_per_kg,
        carbs_basis=carbs_basis,
    )

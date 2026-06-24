"""Composite Fit & Strong score + improvements — implements spec-fitstrong-score. Pure.

Heuristic, NOT a validated clinical index (see docs/EVIDENCE.md, confidence: Hypothesis).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional

from ..models import Client, FoodItem, FoodRef, Symptom, Workout
from .fodmap_load import fodmap_load
from .macro_targets import compute_macro_targets
from .microbiome_score import microbiome_score

_WEIGHTS = {
    "protein": 0.25,
    "energy": 0.20,
    "microbiome": 0.20,
    "fodmap": 0.15,
    "training": 0.10,
    "symptoms": 0.10,
}
_FODMAP_DAY_CAP = 45.0          # day load at/above which fodmap subscore hits 0
_TRAINING_TARGET_H = 5.0        # weekly sport hours for a full training subscore
_IMPROVE_THRESHOLD = 70.0       # subscores below this become improvement actions

_ACTIONS = {
    "protein": "Verhoog eiwitinname richting je doel (mager vlees, vis, ei, peulvruchten).",
    "energy": "Stem je energie-inname af op je behoefte; te laag remt herstel en spierbehoud.",
    "microbiome": "Bouw vezels/prebiotica op uit darmvriendelijke bronnen (havermout, courgette, wortel).",
    "fodmap": "Verlaag de FODMAP-belasting per maaltijd; spreid hoog-FODMAP voeding.",
    "training": "Verhoog je trainingsvolume geleidelijk richting ~5 u/week.",
    "symptoms": "Houd klachten bij en test triggers; bij aanhoudende klachten een diëtist raadplegen.",
}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


@dataclass
class Improvement:
    area: str
    score: float
    action: str

    def to_dict(self) -> dict:
        return {"area": self.area, "score": self.score, "action": self.action}


@dataclass
class FitStrongScore:
    score: float
    band: str
    subscores: dict[str, float]
    components_used: list[str]
    improvements: list[Improvement] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "band": self.band,
            "subscores": self.subscores,
            "components_used": self.components_used,
            "improvements": [i.to_dict() for i in self.improvements],
        }


def _band(score: float) -> str:
    if score < 40:
        return "aandacht nodig"
    if score < 60:
        return "matig"
    if score < 80:
        return "goed"
    return "sterk"


def fitstrong_score(
    client: Client,
    day_calories: Optional[float],
    day_protein_g: Optional[float],
    meal_items: list[FoodItem],
    food_db: Mapping[str, FoodRef],
    *,
    workouts: Optional[list[Workout]] = None,
    symptoms: Optional[list[Symptom]] = None,
) -> FitStrongScore:
    target = compute_macro_targets(client)
    subs: dict[str, float] = {}

    if day_protein_g is not None and target.protein_g > 0:
        subs["protein"] = round(_clamp(day_protein_g / target.protein_g * 100), 1)

    if day_calories is not None:
        low, high = target.energy_kcal_low, target.energy_kcal_high
        if day_calories < low:
            energy = day_calories / low * 100
        elif day_calories > high:
            energy = 100 - (day_calories - high) / high * 100
        else:
            energy = 100.0
        subs["energy"] = round(_clamp(energy), 1)

    if food_db and meal_items:
        subs["microbiome"] = microbiome_score(meal_items, food_db).score

    if meal_items:
        subs["fodmap"] = round(_clamp(100 - fodmap_load(meal_items) / _FODMAP_DAY_CAP * 100), 1)

    if workouts is not None or client.weekly_sport_hours:
        subs["training"] = round(_clamp(client.weekly_sport_hours / _TRAINING_TARGET_H * 100), 1)

    if symptoms:
        worst = max(
            (max(s.abdominal_pain or 0, s.bloating or 0) for s in symptoms),
            default=0,
        )
        subs["symptoms"] = round(_clamp(100 - worst * 10), 1)

    # Weighted score over present components, renormalised (no fabricated zeros).
    total_weight = sum(_WEIGHTS[k] for k in subs)
    score = round(sum(subs[k] * _WEIGHTS[k] for k in subs) / total_weight, 1) if total_weight else 0.0

    improvements = sorted(
        (Improvement(area=k, score=subs[k], action=_ACTIONS[k]) for k in subs if subs[k] < _IMPROVE_THRESHOLD),
        key=lambda i: (i.score, i.area),
    )

    return FitStrongScore(
        score=score,
        band=_band(score),
        subscores=subs,
        components_used=list(subs.keys()),
        improvements=improvements,
    )

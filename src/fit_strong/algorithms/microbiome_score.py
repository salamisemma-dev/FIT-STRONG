"""Indicative gut-feeding score 0–100 — implements spec-microbiome-score. Pure.

NOT diagnostic. Reflects fibre intake + prebiotic quality (gut-muscle axis).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from ..models import FoodItem, FoodRef

_FIBER_TARGET_G = 30.0      # g/day -> full fibre component
_PREBIOTIC_TARGET = 20.0    # accumulated prebiotic points -> full prebiotic component
_FIBER_WEIGHT = 60.0
_PREBIOTIC_WEIGHT = 40.0


@dataclass
class MicrobiomeScore:
    score: float
    fiber_g: float
    prebiotic_points: float
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def microbiome_score(items: list[FoodItem], food_db: Mapping[str, FoodRef]) -> MicrobiomeScore:
    db = {k.strip().lower(): v for k, v in food_db.items()}
    fiber_g = 0.0
    prebiotic_points = 0.0
    unresolved: list[str] = []

    for item in items:
        ref = db.get(item.name.strip().lower())
        if ref is None:
            unresolved.append(item.name)
            continue
        factor = item.amount_g / 100.0
        fiber_g += factor * ref.fiber_per_100g
        prebiotic_points += factor * ref.prebiotic_score

    fiber_component = min(fiber_g / _FIBER_TARGET_G, 1.0) * _FIBER_WEIGHT
    prebiotic_component = min(prebiotic_points / _PREBIOTIC_TARGET, 1.0) * _PREBIOTIC_WEIGHT

    return MicrobiomeScore(
        score=round(fiber_component + prebiotic_component, 1),
        fiber_g=round(fiber_g, 1),
        prebiotic_points=round(prebiotic_points, 1),
        unresolved=unresolved,
    )

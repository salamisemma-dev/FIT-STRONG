"""Cumulative FODMAP load of a meal — implements spec-fodmap-load. Pure.

Weights scaled 1/10 vs the blueprint pseudo-code (0.8/0.4/0.1) so the 15 g/meal
threshold stays meaningful — documented deviation in the spec.
"""

from __future__ import annotations

from ..models import FodmapLevel, FoodItem

_WEIGHT = {
    FodmapLevel.HIGH: 0.08,
    FodmapLevel.MEDIUM: 0.04,
    FodmapLevel.LOW: 0.01,
    FodmapLevel.VERY_LOW: 0.0,
}
DEFAULT_THRESHOLD_G = 15.0


def fodmap_load(items: list[FoodItem]) -> float:
    total = sum(item.amount_g * _WEIGHT[item.fodmap_level] for item in items)
    return round(total, 2)


def meal_exceeds_threshold(items: list[FoodItem], threshold_g: float = DEFAULT_THRESHOLD_G) -> bool:
    return fodmap_load(items) > threshold_g

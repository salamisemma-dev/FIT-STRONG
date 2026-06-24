"""Food→symptom correlation (2–4 h) — implements spec-trigger-detection. Pure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from ..models import FodmapGroup, FodmapLevel, Meal, Symptom

# Per-food suspicion weight: a low-FODMAP food sharing a meal with the real culprit
# must not rank equally. Mirrors the evidence that high-FODMAP foods are likely triggers.
_SUSPICION = {
    FodmapLevel.HIGH: 1.0,
    FodmapLevel.MEDIUM: 0.6,
    FodmapLevel.LOW: 0.3,
    FodmapLevel.VERY_LOW: 0.1,
}


@dataclass
class TriggerScore:
    food_name: str
    score: float
    occurrences: int
    avg_pain: float

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def _symptom_intensity(symptom: Symptom) -> float:
    return max(
        symptom.abdominal_pain if symptom.abdominal_pain is not None else 0,
        symptom.bloating if symptom.bloating is not None else 0,
    )


def _is_fodmap_suspect(item) -> bool:
    return item.fodmap_level != FodmapLevel.VERY_LOW and item.fodmap_group != FodmapGroup.LOW_FODMAP


def detect_triggers(
    meals: list[Meal],
    symptoms: list[Symptom],
    *,
    window_start_h: float = 2.0,
    window_end_h: float = 4.0,
    pain_threshold: float = 4.0,
    top_n: int = 3,
) -> list[TriggerScore]:
    if not meals or not symptoms:
        return []

    score: dict[str, float] = {}
    occ: dict[str, int] = {}
    pains: dict[str, list[float]] = {}

    start = timedelta(hours=window_start_h)
    end = timedelta(hours=window_end_h)

    for meal in meals:
        lo = meal.recorded_at + start
        hi = meal.recorded_at + end
        window = [s for s in symptoms if lo <= s.recorded_at <= hi]
        counting = [s for s in window if _symptom_intensity(s) >= pain_threshold]
        if not counting:
            continue
        pain_value = max(_symptom_intensity(s) for s in counting)
        for item in meal.items:
            if not _is_fodmap_suspect(item):
                continue
            key = item.name.strip().lower()
            suspicion = pain_value * _SUSPICION[item.fodmap_level]
            score[key] = score.get(key, 0.0) + suspicion
            occ[key] = occ.get(key, 0) + 1
            pains.setdefault(key, []).append(pain_value)

    results = [
        TriggerScore(
            food_name=name,
            score=round(score[name], 2),
            occurrences=occ[name],
            avg_pain=round(sum(pains[name]) / len(pains[name]), 2),
        )
        for name in score
    ]
    results.sort(key=lambda t: (-t.score, -t.occurrences, t.food_name))
    return results[:top_n]

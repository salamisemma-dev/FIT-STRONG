"""Deterministic daily nutrition scheme — implements spec-daily-scheme. Pure.

Greedy and honest: with a small food DB the plan is repetitive, and unmet targets are
reported in `notes` rather than hidden.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from ..models import Client, FoodRef
from .macro_targets import compute_macro_targets

_DEFAULT_PORTION_G = 100.0


@dataclass
class SchemeMeal:
    label: str
    items: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"label": self.label, "items": self.items}


@dataclass
class DailyScheme:
    meals: list[SchemeMeal]
    totals: dict
    target: dict
    coverage: dict
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "meals": [m.to_dict() for m in self.meals],
            "totals": self.totals,
            "target": self.target,
            "coverage": self.coverage,
            "notes": self.notes,
        }


def _pick(candidates: list[FoodRef], key, n: int, chosen: set[str]) -> list[FoodRef]:
    ordered = sorted(candidates, key=lambda r: (-key(r), (r.id or r.name)))
    out = []
    for ref in ordered:
        rid = ref.id or ref.name
        if rid in chosen:
            continue
        out.append(ref)
        chosen.add(rid)
        if len(out) >= n:
            break
    return out


def daily_scheme(
    client: Client,
    food_db: Mapping[str, FoodRef],
    *,
    fodmap_sensitive: bool = False,
    meals: int = 3,
    exclude_ids: tuple[str, ...] = (),
) -> DailyScheme:
    target_macros = compute_macro_targets(client)
    target = {
        "protein_g": target_macros.protein_g,
        "carbs_g": round((target_macros.carbs_g_low + target_macros.carbs_g_high) / 2, 1),
        "energy_kcal": round((target_macros.energy_kcal_low + target_macros.energy_kcal_high) / 2, 1),
    }

    # Deduplicate refs (DB is keyed by both id and name → same ref appears twice).
    seen_ids: set[int] = set()
    uniq: list[FoodRef] = []
    for ref in food_db.values():
        if id(ref) in seen_ids:
            continue
        seen_ids.add(id(ref))
        uniq.append(ref)

    excluded = set(exclude_ids)
    candidates = [
        r for r in uniq
        if (r.id or r.name) not in excluded
        and not (fodmap_sensitive and r.fodmap_level.value == "high")
    ]

    notes: list[str] = []
    if not candidates:
        notes.append("Geen geschikte voedingsmiddelen in de database voor dit schema.")
        return DailyScheme([SchemeMeal(f"Maaltijd {i+1}") for i in range(meals)],
                           {"protein_g": 0, "carbs_g": 0, "energy_kcal": 0, "fiber_g": 0},
                           target, {"protein_pct": 0, "carbs_pct": 0, "energy_pct": 0}, notes)

    chosen: set[str] = set()
    selected: list[FoodRef] = []
    selected += _pick(candidates, lambda r: r.protein_per_100g, 3, chosen)
    selected += _pick(candidates, lambda r: r.carbs_per_100g, 2, chosen)
    selected += _pick(candidates, lambda r: r.fiber_per_100g, 2, chosen)

    totals = {"protein_g": 0.0, "carbs_g": 0.0, "energy_kcal": 0.0, "fiber_g": 0.0}
    meal_buckets = [SchemeMeal(f"Maaltijd {i+1}") for i in range(max(1, meals))]
    for idx, ref in enumerate(selected):
        amount = ref.safe_portion_g or _DEFAULT_PORTION_G
        factor = amount / 100.0
        totals["protein_g"] += factor * ref.protein_per_100g
        totals["carbs_g"] += factor * ref.carbs_per_100g
        totals["energy_kcal"] += factor * ref.calories_per_100g
        totals["fiber_g"] += factor * ref.fiber_per_100g
        meal_buckets[idx % len(meal_buckets)].items.append({"id": ref.id or ref.name, "amount_g": amount})

    totals = {k: round(v, 1) for k, v in totals.items()}
    coverage = {
        "protein_pct": round(totals["protein_g"] / target["protein_g"] * 100, 1) if target["protein_g"] else 0,
        "carbs_pct": round(totals["carbs_g"] / target["carbs_g"] * 100, 1) if target["carbs_g"] else 0,
        "energy_pct": round(totals["energy_kcal"] / target["energy_kcal"] * 100, 1) if target["energy_kcal"] else 0,
    }

    if coverage["protein_pct"] < 80:
        notes.append(f"Eiwitdoel niet gehaald uit de huidige database ({coverage['protein_pct']}%); "
                     "breid de voedingsdatabase uit of voeg een eiwitbron toe.")
    if coverage["energy_pct"] < 80:
        notes.append(f"Energiedoel niet gehaald ({coverage['energy_pct']}%); porties of bronnen uitbreiden.")
    notes.append("Indicatief schema — geen voorschrift. Stem af op persoonlijke tolerantie.")

    return DailyScheme(meal_buckets, totals, target, coverage, notes)

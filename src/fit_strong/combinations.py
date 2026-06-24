"""Food + supplement combination recommender — implements spec-combination-library.

Deterministic, rule-assisted, and conservative: it recommends from known available
items only, emits caveats, and never presents supplement advice as medical treatment.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

from .food_db import load_food_db
from .models import FoodRef

_DEFAULT_SUPPLEMENT_PATH = Path(__file__).resolve().parents[2] / "config" / "supplement_db.json"
_DEFAULT_RULES_PATH = Path(__file__).resolve().parents[2] / "config" / "combination_rules.json"


@dataclass
class SupplementRef:
    id: str
    name: str
    form: str
    benefits: list[str] = field(default_factory=list)
    potential_issues: list[str] = field(default_factory=list)
    timing: str | None = None
    fodmap_impact: str | None = None
    interactions: list[str] = field(default_factory=list)
    source: str | None = None
    safe_dose: dict[str, Any] = field(default_factory=lambda: {"amount": None, "unit": None, "note": "volgens product"})

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise ValueError("SupplementRef id/name must be non-empty")
        amount = self.safe_dose.get("amount")
        if amount is not None and amount < 0:
            raise ValueError(f"safe_dose.amount must be >= 0, got {amount}")

    def dose_dict(self) -> dict:
        amount = self.safe_dose.get("amount")
        unit = self.safe_dose.get("unit")
        if amount is not None and unit:
            return {f"dose_{unit}": amount}
        return {"dose": self.safe_dose.get("note") or "volgens product"}


@dataclass
class CombinationRule:
    id: str
    type: str
    description: str
    ingredients: list[str]
    condition: dict[str, Any]
    reason: str

    def __post_init__(self) -> None:
        if self.type not in {"good_combo", "bad_combo", "warning"}:
            raise ValueError(f"unknown rule type: {self.type}")


@dataclass
class CombinationRecommendation:
    recommended_combo: dict
    why: list[str]
    warnings: list[str]
    alternatives: list[str]
    meta: dict

    def to_dict(self) -> dict:
        return {
            "recommended_combo": self.recommended_combo,
            "why": self.why,
            "warnings": self.warnings,
            "alternatives": self.alternatives,
            "meta": self.meta,
        }


def _read_json(path: str | Path | None, default_path: Path, package_name: str) -> Any:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if default_path.exists():
        return json.loads(default_path.read_text(encoding="utf-8"))
    resource = resources.files("fit_strong").joinpath(f"data/{package_name}")
    return json.loads(resource.read_text(encoding="utf-8"))


def load_supplement_db(path: str | Path | None = None) -> dict[str, SupplementRef]:
    raw = _read_json(path, _DEFAULT_SUPPLEMENT_PATH, "supplement_db.json")
    rows = raw.get("supplements") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("supplement DB must be a list or an object with a supplements list")
    refs = [SupplementRef(**row) for row in rows]
    return {ref.id: ref for ref in refs}


def load_combination_rules(path: str | Path | None = None) -> list[CombinationRule]:
    raw = _read_json(path, _DEFAULT_RULES_PATH, "combination_rules.json")
    rows = raw.get("rules") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("combination rules must be a list or an object with a rules list")
    return [CombinationRule(**row) for row in rows]


def _lookup_food(food_db: Mapping[str, FoodRef], key: str) -> FoodRef | None:
    return food_db.get(key.strip().lower())


def _coerce_request_items(value: Any) -> list[tuple[str, float | None]]:
    """Accept either ['id', ...] or [{'id'|'name':..., 'amount_g':...}, ...].

    Real-world meal/stack docs carry objects with amounts; bare id lists are the
    terse form. Both resolve to (key, amount_or_None) so callers never silently
    drop a populated request because of its shape.
    """
    items: list[tuple[str, float | None]] = []
    for entry in value or []:
        if isinstance(entry, str):
            items.append((entry, None))
        elif isinstance(entry, Mapping):
            key = entry.get("id") or entry.get("name")
            if key:
                items.append((str(key), entry.get("amount_g")))
    return items


def _food_score(ref: FoodRef, timing: str) -> float:
    protein = ref.protein_per_100g / 8
    carbs = ref.carbs_per_100g / 20 if timing in {"post_workout", "pre_workout"} else 0
    omega = min(ref.omega3_g_per_100g, 2.0) / 2
    prebiotic = ref.prebiotic_score / 10
    penalty = 0.0
    if timing == "pre_workout" and ref.fat_per_100g > 10:
        penalty += 2.0
    return protein + carbs + omega + prebiotic - penalty


def _condition_flags(selected_foods: list[tuple[str, FoodRef]], context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "meal_timing": context.get("meal_timing"),
        "fodmap_sensitive": bool(context.get("fodmap_sensitive")),
        "avoid_lactose": bool(context.get("avoid_lactose")),
        "workout_intensity": context.get("workout_intensity", 0),
        "sweat_loss_high": bool(context.get("sweat_loss_high")),
        "meal_near_h": context.get("meal_near_h", 99),
        "any_carb_present": any(ref.carbs_per_100g >= 15 for _, ref in selected_foods),
        "contains_fat": any(ref.fat_per_100g >= 5 for _, ref in selected_foods),
        "fiber_present": any(ref.fiber_per_100g >= 3 for _, ref in selected_foods),
        "fish_omega3_present": sum(ref.omega3_g_per_100g for _, ref in selected_foods) >= 1.0,
    }


def _rule_matches(rule: CombinationRule, flags: Mapping[str, Any]) -> bool:
    condition = rule.condition
    for key, expected in condition.items():
        if key.endswith("_gt"):
            flag_key = key[:-3]
            if not flags.get(flag_key, 0) > expected:
                return False
        elif key.endswith("_lt"):
            flag_key = key[:-3]
            if not flags.get(flag_key, 0) < expected:
                return False
        elif flags.get(key) != expected:
            return False
    return True


def recommend_combination(
    request: Mapping[str, Any],
    *,
    food_db: Mapping[str, FoodRef] | None = None,
    supplement_db: Mapping[str, SupplementRef] | None = None,
    rules: list[CombinationRule] | None = None,
) -> CombinationRecommendation:
    context = request.get("context", {})
    timing = context.get("meal_timing", "meal")
    food_db = food_db or load_food_db()
    supplement_db = supplement_db or load_supplement_db()
    rules = rules if rules is not None else load_combination_rules()

    raw_foods = request.get("available_foods")
    if raw_foods is None:
        raw_foods = request.get("foods")  # accept meal-doc shape
    food_candidates = []
    requested_amounts: dict[str, float] = {}
    unresolved_foods = []
    for key, amount in _coerce_request_items(raw_foods):
        ref = _lookup_food(food_db, key)
        if ref is None:
            unresolved_foods.append(key)
            continue
        if context.get("fodmap_sensitive") and ref.fodmap_level.value == "high":
            continue
        food_candidates.append((key, ref))
        if amount is not None:
            requested_amounts[key] = amount

    food_candidates.sort(key=lambda pair: (-_food_score(pair[1], timing), pair[0]))
    selected_foods = food_candidates[:4]
    flags = _condition_flags(selected_foods, context)

    selected_food_ids = {key for key, _ in selected_foods}
    raw_supps = request.get("available_supplements")
    if raw_supps is None:
        raw_supps = request.get("supplements")  # accept stack-doc shape
    available_supplements = {key for key, _ in _coerce_request_items(raw_supps)}
    supplement_items = []
    warnings = []
    why = []

    for key, ref in selected_foods:
        amount = ref.safe_portion_g or 100
        why.append(f"{ref.name}: {ref.protein_per_100g:g} g eiwit/100 g, FODMAP {ref.fodmap_level.value}.")
        if ref.timing_advice:
            why.append(ref.timing_advice)

    for rule in rules:
        involved = set(rule.ingredients)
        has_available_supp = involved & available_supplements
        has_selected_food = involved & selected_food_ids or any((ref.id in involved) for _, ref in selected_foods)
        if not _rule_matches(rule, flags):
            continue
        if rule.type == "warning" and has_available_supp:
            warnings.append(f"{rule.description}: {rule.reason}")
        elif rule.type == "bad_combo" and has_selected_food:
            warnings.append(f"{rule.description}: {rule.reason}")
        elif rule.type == "good_combo" and (has_available_supp or has_selected_food):
            why.append(f"{rule.description}: {rule.reason}")

    for sid in sorted(available_supplements):
        supp = supplement_db.get(sid)
        if supp is None:
            warnings.append(f"Onbekend supplement: {sid}")
            continue
        if sid == "omega3_fish_oil" and flags["fish_omega3_present"]:
            warnings.append("Omega-3 visolie niet toegevoegd: de maaltijd bevat al omega-3 rijke vis.")
            continue
        if sid == "caffeine_anhydrous" and context.get("fodmap_sensitive"):
            warnings.append("Cafeine kan darmprikkeling geven; niet standaard toegevoegd bij gevoelige darm.")
            continue
        if sid == "creatine_monohydrate" and not flags["any_carb_present"]:
            warnings.append("Creatine kan, maar combineer praktischer met koolhydraten.")
            continue
        if sid == "electrolytes_no_sorbitol" and not (flags["workout_intensity"] > 7 and flags["sweat_loss_high"]):
            continue
        item = {"id": sid}
        item.update(supp.dose_dict())
        supplement_items.append(item)
        why.append(f"{supp.name}: {supp.timing or 'timing volgens product'}.")

    foods = [
        {"id": ref.id or key, "amount_g": requested_amounts.get(key, ref.safe_portion_g or 100)}
        for key, ref in selected_foods
    ]
    alternatives = []
    if any((ref.id == "quinoa") for _, ref in selected_foods):
        alternatives.append("Vervang quinoa door witte rijst als je minder vezels wilt.")
    if not any((ref.category == "vis") for _, ref in selected_foods):
        alternatives.append("Kies zalm, forel of kabeljauw als visrijke eiwitvariant.")

    return CombinationRecommendation(
        recommended_combo={"foods": foods, "supplements": supplement_items},
        why=why[:10],
        warnings=warnings,
        alternatives=alternatives,
        meta={"unresolved_foods": unresolved_foods, "rules_evaluated": len(rules), "timing": timing},
    )

"""Reference food-database loader. Reads JSON into FoodRef objects.

Supports the original list-of-rows format and the v2 `{version, foods}` library
format. The only I/O boundary in the package; algorithms receive loaded mappings.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Dict

from .models import FoodRef

_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "food_db.json"
_PACKAGE_DATA = "data/food_db.json"


def _read_json(path: str | Path | None, package_name: str) -> Any:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if _DEFAULT_PATH.exists() and package_name == _PACKAGE_DATA:
        return json.loads(_DEFAULT_PATH.read_text(encoding="utf-8"))
    resource = resources.files("fit_strong").joinpath(package_name)
    return json.loads(resource.read_text(encoding="utf-8"))


def _food_rows(raw: Any) -> list[dict]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("foods"), list):
        return raw["foods"]
    raise ValueError("food DB must be a list or an object with a foods list")


def _normalise_food_row(row: dict) -> dict:
    if "macros_per_100g" not in row:
        return row
    macros = row["macros_per_100g"]
    keep = {k: v for k, v in row.items() if k != "macros_per_100g"}
    keep.update({
        "calories_per_100g": macros["calories"],
        "protein_per_100g": macros["protein_g"],
        "carbs_per_100g": macros["carbs_g"],
        "fat_per_100g": macros["fat_g"],
        "fiber_per_100g": macros["fiber_g"],
    })
    allowed = set(FoodRef.__dataclass_fields__)
    extra = {k: v for k, v in keep.items() if k not in allowed}
    normalised = {k: v for k, v in keep.items() if k in allowed}
    if extra:
        normalised["extra"] = extra
    return normalised


def load_food_db(path: "str | Path | None" = None) -> Dict[str, FoodRef]:
    rows = _food_rows(_read_json(path, _PACKAGE_DATA))
    db: Dict[str, FoodRef] = {}
    for row in rows:
        ref = FoodRef(**_normalise_food_row(row))
        keys = {ref.name.strip().lower()}
        if ref.id:
            keys.add(ref.id.strip().lower())
        for key in keys:
            db[key] = ref
    return db

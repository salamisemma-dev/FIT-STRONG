"""Reference food-database loader. Reads config/food_db.json into FoodRef objects.

The only I/O boundary in the package; algorithms stay pure and receive the loaded
mapping as an argument.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Dict

from .models import FoodRef

_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "food_db.json"
_PACKAGE_DATA = "data/food_db.json"


def _read_default_rows() -> list[dict]:
    if _DEFAULT_PATH.exists():
        return json.loads(_DEFAULT_PATH.read_text(encoding="utf-8"))

    resource = resources.files("fit_strong").joinpath(_PACKAGE_DATA)
    return json.loads(resource.read_text(encoding="utf-8"))


def load_food_db(path: "str | Path | None" = None) -> Dict[str, FoodRef]:
    rows = json.loads(Path(path).read_text(encoding="utf-8")) if path else _read_default_rows()
    db: Dict[str, FoodRef] = {}
    for row in rows:
        ref = FoodRef(**row)
        db[ref.name.strip().lower()] = ref
    return db

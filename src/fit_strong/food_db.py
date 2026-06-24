"""Reference food-database loader. Reads config/food_db.json into FoodRef objects.

The only I/O boundary in the package; algorithms stay pure and receive the loaded
mapping as an argument.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .models import FoodRef

_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "food_db.json"


def load_food_db(path: "str | Path | None" = None) -> Dict[str, FoodRef]:
    p = Path(path) if path else _DEFAULT_PATH
    rows = json.loads(p.read_text(encoding="utf-8"))
    db: Dict[str, FoodRef] = {}
    for row in rows:
        ref = FoodRef(**row)
        db[ref.name.strip().lower()] = ref
    return db

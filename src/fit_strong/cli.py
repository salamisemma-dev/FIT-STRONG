"""Fit & Strong CLI — render a personalised report from a diary JSON file.

Usage:
    python -m fit_strong.cli path/to/diary.json [--food-db config/food_db.json]

Diary JSON shape: see examples/sample_diary.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any

from .engine import generate_report
from .food_db import load_food_db
from .models import Client, FoodItem, Meal, Symptom, Workout


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _build_meal(raw: dict[str, Any]) -> Meal:
    items = [FoodItem(**it) for it in raw.get("items", [])]
    return Meal(recorded_at=_dt(raw["recorded_at"]), meal_type=raw["meal_type"], items=items,
                notes=raw.get("notes"))


def load_diary(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def run(diary_path: str, food_db_path: str | None = None) -> dict:
    data = load_diary(diary_path)
    client = Client(**data["client"])
    meals = [_build_meal(m) for m in data.get("meals", [])]
    symptoms = [
        Symptom(recorded_at=_dt(s["recorded_at"]),
                **{k: v for k, v in s.items() if k != "recorded_at"})
        for s in data.get("symptoms", [])
    ]
    workouts = [
        Workout(started_at=_dt(w["started_at"]),
                **{k: v for k, v in w.items() if k != "started_at"})
        for w in data.get("workouts", [])
    ]

    food_db = {}
    try:
        food_db = load_food_db(food_db_path)
    except FileNotFoundError:
        print("warn: food DB not found — microbiome score skipped", file=sys.stderr)

    report = generate_report(
        client, meals, symptoms, workouts, food_db,
        day_calories=data.get("day_calories"),
        day_protein_g=data.get("day_protein_g"),
        bristol_events=data.get("bristol_events"),
        no_improvement_weeks=data.get("no_improvement_weeks", 0.0),
    )
    return report.to_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fit-strong", description="Evidence-based coaching report.")
    parser.add_argument("diary", help="path to diary JSON")
    parser.add_argument("--food-db", default=None, help="path to food_db.json")
    args = parser.parse_args(argv)

    # Dutch text + Windows console: force UTF-8 so accented chars render correctly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

    result = run(args.diary, args.food_db)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

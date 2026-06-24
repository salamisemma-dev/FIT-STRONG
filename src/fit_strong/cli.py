"""Fit & Strong CLI — personalised report from a diary JSON file.

Usage:
    fit-strong path/to/diary.json [--food-db food_db.json]
                                  [--html report.html] [--video-props props.json]

The bundled food DB is used by default. Diary JSON shape: see examples/sample_diary.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any

from .algorithms.daily_scheme import daily_scheme
from .algorithms.fitstrong_score import fitstrong_score
from .algorithms.cycle_hormone import analyze_cycle_hormones
from .engine import generate_report
from .food_db import load_food_db
from .models import Client, FoodItem, Meal, Symptom, Workout, MenstrualCycle, HormonalSymptom
from .report_html import render_html
from .video_props import weekly_video_props


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _build_meal(raw: dict[str, Any]) -> Meal:
    items = [FoodItem(**it) for it in raw.get("items", [])]
    return Meal(recorded_at=_dt(raw["recorded_at"]), meal_type=raw["meal_type"], items=items,
                notes=raw.get("notes"))


def load_diary(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _build(data: dict[str, Any], food_db: dict):
    """Construct all engine artefacts from a parsed diary (no I/O, no mutation)."""
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
    cycles = [MenstrualCycle(**c) for c in data.get("menstrual_cycles", [])]
    hormonal_symptoms = [
        HormonalSymptom(recorded_at=_dt(h["recorded_at"]),
                        **{k: v for k, v in h.items() if k != "recorded_at"})
        for h in data.get("hormonal_symptoms", [])
    ]
    report = generate_report(
        client, meals, symptoms, workouts, food_db,
        day_calories=data.get("day_calories"),
        day_protein_g=data.get("day_protein_g"),
        bristol_events=data.get("bristol_events"),
        no_improvement_weeks=data.get("no_improvement_weeks", 0.0),
    )
    all_items = [item for meal in meals for item in meal.items]
    score = fitstrong_score(
        client, data.get("day_calories"), data.get("day_protein_g"),
        all_items, food_db, workouts=workouts, symptoms=symptoms,
    )
    scheme = daily_scheme(client, food_db, fodmap_sensitive=bool(data.get("fodmap_sensitive"))) \
        if food_db else None
    if cycles or hormonal_symptoms:
        latest_date = max(
            [s.recorded_at.date() for s in symptoms] +
            [h.recorded_at.date() for h in hormonal_symptoms]
        ) if (symptoms or hormonal_symptoms) else None
        hormone = analyze_cycle_hormones(
            symptoms, cycles, hormonal_symptoms,
            today=latest_date,
            fodmap_sensitive=bool(data.get("fodmap_sensitive", True)),
        )
    else:
        hormone = None
    return report, score, scheme, hormone


def _load_food_db(food_db_path: str | None) -> dict:
    try:
        return load_food_db(food_db_path)
    except FileNotFoundError:
        print("warn: food DB not found — microbiome/scheme skipped", file=sys.stderr)
        return {}


def run(diary_path: str, food_db_path: str | None = None) -> dict:
    data = load_diary(diary_path)
    report, score, scheme, hormone = _build(data, _load_food_db(food_db_path))
    result = report.to_dict()
    result["fitstrong"] = score.to_dict()
    result["daily_scheme"] = scheme.to_dict() if scheme else None
    result["hormone"] = hormone.to_dict() if hormone else None
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fit-strong", description="Evidence-based coaching report.")
    parser.add_argument("diary", help="path to diary JSON")
    parser.add_argument("--food-db", default=None, help="path to food_db.json (default: bundled)")
    parser.add_argument("--html", default=None, help="write a self-contained HTML report to this path")
    parser.add_argument("--video-props", default=None, help="write Remotion weekly-video props JSON here")
    parser.add_argument("--week-label", default="Deze week", help="label for the weekly video")
    args = parser.parse_args(argv)

    # Dutch text + Windows console: force UTF-8 so accented chars render correctly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

    data = load_diary(args.diary)
    report, score, scheme, hormone = _build(data, _load_food_db(args.food_db))

    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(render_html(report, score, scheme, hormone))
        print(f"HTML report written to {args.html}", file=sys.stderr)
    if args.video_props:
        with open(args.video_props, "w", encoding="utf-8") as fh:
            json.dump(weekly_video_props(score, week_label=args.week_label), fh,
                      indent=2, ensure_ascii=False)
        print(f"Video props written to {args.video_props}", file=sys.stderr)

    result = report.to_dict()
    result["fitstrong"] = score.to_dict()
    result["daily_scheme"] = scheme.to_dict() if scheme else None
    result["hormone"] = hormone.to_dict() if hormone else None
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

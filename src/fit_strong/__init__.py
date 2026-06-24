"""Fit & Strong — evidence-based nutrition & training coaching engine.

Public API. Layering (constitution §4): models -> algorithms -> engine -> cli/skill.
"""

from .algorithms.energy_balance import check_energy_balance
from .algorithms.fodmap_load import (
    DEFAULT_THRESHOLD_G,
    fodmap_load,
    meal_exceeds_threshold,
)
from .algorithms.macro_targets import MacroTargets, compute_macro_targets
from .algorithms.microbiome_score import MicrobiomeScore, microbiome_score
from .algorithms.trigger_detection import TriggerScore, detect_triggers
from .algorithms.fitstrong_score import FitStrongScore, Improvement, fitstrong_score
from .algorithms.daily_scheme import DailyScheme, SchemeMeal, daily_scheme
from .engine import DISCLAIMER, Report, generate_report
from .report_html import render_html
from .video_props import weekly_video_props
from .food_db import load_food_db
from .combinations import (
    CombinationRecommendation,
    CombinationRule,
    SupplementRef,
    load_combination_rules,
    load_supplement_db,
    recommend_combination,
)
from .models import (
    Alert,
    Client,
    FodmapGroup,
    FodmapLevel,
    FoodItem,
    FoodRef,
    Meal,
    MealType,
    Severity,
    Sex,
    Symptom,
    TrainingGoal,
    Workout,
)

__version__ = "1.0.0"

__all__ = [
    "Alert", "Client", "FodmapGroup", "FodmapLevel", "FoodItem", "FoodRef", "Meal",
    "MealType", "Severity", "Sex", "Symptom", "TrainingGoal", "Workout",
    "MacroTargets", "compute_macro_targets",
    "fodmap_load", "meal_exceeds_threshold", "DEFAULT_THRESHOLD_G",
    "detect_triggers", "TriggerScore",
    "check_energy_balance",
    "microbiome_score", "MicrobiomeScore",
    "generate_report", "Report", "DISCLAIMER",
    "fitstrong_score", "FitStrongScore", "Improvement",
    "daily_scheme", "DailyScheme", "SchemeMeal",
    "render_html", "weekly_video_props",
    "load_food_db",
    "SupplementRef", "CombinationRule", "CombinationRecommendation",
    "load_supplement_db", "load_combination_rules", "recommend_combination",
    "__version__",
]

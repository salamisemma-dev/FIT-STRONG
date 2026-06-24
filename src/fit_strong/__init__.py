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
from .engine import DISCLAIMER, Report, generate_report
from .food_db import load_food_db
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
    "load_food_db",
    "__version__",
]

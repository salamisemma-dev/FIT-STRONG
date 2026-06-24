"""Typed, validated in-memory data models — implements spec-models.

Mirrors the blueprint's PostgreSQL schema so the pure engine runs without a DB.
Construction validates and raises ValueError at the boundary (constitution §4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


# --------------------------------------------------------------------------- enums
class _StrEnum(str, Enum):
    """Enum whose members compare equal to their string value, and that coerces
    a string into a member via `coerce`."""

    @classmethod
    def coerce(cls, value: "str | _StrEnum") -> "_StrEnum":
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:  # pragma: no cover - message path
            allowed = ", ".join(m.value for m in cls)
            raise ValueError(f"{cls.__name__}: '{value}' not in {{{allowed}}}") from exc


class Sex(_StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class TrainingGoal(_StrEnum):
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"


class FodmapGroup(_StrEnum):
    LACTOSE = "lactose"
    FRUCTOSE = "fructose"
    FRUCTAN = "fructan"
    GALACTAN = "galactan"
    POLYOL = "polyol"
    LOW_FODMAP = "low_fodmap"
    UNKNOWN = "unknown"


class FodmapLevel(_StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class MealType(_StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    POST_WORKOUT = "post_workout"


class Severity(_StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ----------------------------------------------------------------------- helpers
def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _in_range(value: Optional[float], lo: float, hi: float, name: str) -> None:
    if value is None:
        return
    _require(lo <= value <= hi, f"{name} must be in [{lo}, {hi}], got {value}")


# ------------------------------------------------------------------------- models
@dataclass
class Client:
    weight_kg: float
    height_cm: float
    sex: Sex
    training_goal: TrainingGoal
    weekly_sport_hours: float
    birth_date: Optional[date] = None
    body_fat_pct: Optional[float] = None
    name: Optional[str] = None

    def __post_init__(self) -> None:
        self.sex = Sex.coerce(self.sex)
        self.training_goal = TrainingGoal.coerce(self.training_goal)
        _require(0 < self.weight_kg <= 400, f"weight_kg must be in (0, 400], got {self.weight_kg}")
        _require(0 < self.height_cm <= 300, f"height_cm must be in (0, 300], got {self.height_cm}")
        _require(0 <= self.weekly_sport_hours <= 80, f"weekly_sport_hours must be in [0, 80], got {self.weekly_sport_hours}")
        _in_range(self.body_fat_pct, 0, 75, "body_fat_pct")


@dataclass
class FoodItem:
    name: str
    amount_g: float
    fodmap_group: FodmapGroup = FodmapGroup.UNKNOWN
    fodmap_level: FodmapLevel = FodmapLevel.VERY_LOW

    def __post_init__(self) -> None:
        self.fodmap_group = FodmapGroup.coerce(self.fodmap_group)
        self.fodmap_level = FodmapLevel.coerce(self.fodmap_level)
        _require(self.amount_g >= 0, f"amount_g must be >= 0, got {self.amount_g}")
        _require(bool(self.name and self.name.strip()), "FoodItem.name must be non-empty")


@dataclass
class FoodRef:
    name: str
    fodmap_group: FodmapGroup
    fodmap_level: FodmapLevel
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    prebiotic_score: int
    safe_portion_g: Optional[float] = None

    def __post_init__(self) -> None:
        self.fodmap_group = FodmapGroup.coerce(self.fodmap_group)
        self.fodmap_level = FodmapLevel.coerce(self.fodmap_level)
        for name in (
            "calories_per_100g", "protein_per_100g", "carbs_per_100g",
            "fat_per_100g", "fiber_per_100g",
        ):
            _require(getattr(self, name) >= 0, f"{name} must be >= 0, got {getattr(self, name)}")
        _in_range(self.prebiotic_score, 0, 10, "prebiotic_score")
        if self.safe_portion_g is not None:
            _require(self.safe_portion_g >= 0, f"safe_portion_g must be >= 0, got {self.safe_portion_g}")


@dataclass
class Meal:
    recorded_at: datetime
    meal_type: MealType
    items: list[FoodItem] = field(default_factory=list)
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        self.meal_type = MealType.coerce(self.meal_type)


@dataclass
class Symptom:
    recorded_at: datetime
    bristol_stool: Optional[int] = None
    abdominal_pain: Optional[int] = None
    bloating: Optional[int] = None
    energy_level: Optional[int] = None
    fatigue_score: Optional[int] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None

    def __post_init__(self) -> None:
        _in_range(self.bristol_stool, 1, 7, "bristol_stool")
        _in_range(self.abdominal_pain, 0, 10, "abdominal_pain")
        _in_range(self.bloating, 0, 10, "bloating")
        _in_range(self.energy_level, 1, 10, "energy_level")
        _in_range(self.fatigue_score, 1, 10, "fatigue_score")
        _in_range(self.stress_level, 0, 10, "stress_level")
        _in_range(self.sleep_hours, 0, 24, "sleep_hours")


@dataclass
class Workout:
    started_at: datetime
    duration_min: int
    intensity: int
    workout_type: Optional[str] = None
    perceived_exertion: Optional[int] = None

    def __post_init__(self) -> None:
        _require(self.duration_min >= 0, f"duration_min must be >= 0, got {self.duration_min}")
        _in_range(self.intensity, 1, 10, "intensity")
        _in_range(self.perceived_exertion, 6, 20, "perceived_exertion")


@dataclass
class Alert:
    alert_type: str
    severity: Severity
    message: str

    def __post_init__(self) -> None:
        self.severity = Severity.coerce(self.severity)

    def to_dict(self) -> dict:
        return {"alert_type": self.alert_type, "severity": self.severity.value, "message": self.message}

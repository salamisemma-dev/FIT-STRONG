"""Energy-balance & dehydration alerts — implements spec-energy-balance. Pure."""

from __future__ import annotations

from ..models import Alert, Client, Severity

_MIN_KCAL_PER_KG = 30.0   # shared floor with spec-macro-targets
_MIN_PROTEIN_PER_KG = 1.6
_LOOSE_STOOL = {6, 7}
_LOOSE_STOOL_LIMIT = 3    # > 3 loose stools/day -> dehydration risk


def check_energy_balance(
    client: Client,
    day_calories: float,
    day_protein_g: float,
    bristol_events: list[int] | None = None,
) -> list[Alert]:
    alerts: list[Alert] = []
    w = client.weight_kg

    min_calories = w * _MIN_KCAL_PER_KG
    if day_calories < min_calories:
        alerts.append(Alert(
            "low_calories", Severity.WARNING,
            f"Te weinig calorieën ({day_calories:.0f} kcal). Minimum ~{min_calories:.0f} kcal "
            f"({_MIN_KCAL_PER_KG:.0f} kcal/kg) — risico op spierafbraak.",
        ))

    min_protein = w * _MIN_PROTEIN_PER_KG
    if day_protein_g < min_protein:
        alerts.append(Alert(
            "low_protein", Severity.CRITICAL,
            f"Te weinig eiwit ({day_protein_g:.0f} g). Minimum ~{min_protein:.0f} g "
            f"({_MIN_PROTEIN_PER_KG:.1f} g/kg).",
        ))

    loose = sum(1 for b in (bristol_events or []) if b in _LOOSE_STOOL)
    if loose > _LOOSE_STOOL_LIMIT:
        alerts.append(Alert(
            "dehydration_risk", Severity.WARNING,
            f"{loose}x dunne ontlasting (Bristol 6–7) vandaag — risico op vocht- en "
            f"kaliumverlies. Vocht aanvullen.",
        ))

    return alerts

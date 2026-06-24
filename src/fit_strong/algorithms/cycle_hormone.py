"""Cycle-aware FODMAP and hormone-pattern support — implements spec-cycle-hormone.

Indicative only: this detects diary patterns and phase-aware nutrition cautions. It does
not diagnose hormone disorders, endometriosis, PMS, PMDD, or infertility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from statistics import mean
from typing import Optional

from ..models import CyclePhase, HormonalSymptom, MenstrualCycle, Symptom

_MIN_PHASE_EVENTS = 2
_LUTEAL_DELTA_ALERT = 1.5


@dataclass
class CyclePhaseAdvice:
    phase: CyclePhase
    focus: list[str]
    nutrition: list[str]
    cautions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "phase": self.phase.value,
            "focus": self.focus,
            "nutrition": self.nutrition,
            "cautions": self.cautions,
        }


@dataclass
class HormoneAnalysis:
    current_phase: CyclePhase
    cycle_day: Optional[int]
    luteal_avg_symptom: Optional[float]
    follicular_avg_symptom: Optional[float]
    luteal_delta: Optional[float]
    alerts: list[str]
    advice: CyclePhaseAdvice
    data_quality: str
    disclaimer: str = (
        "Cycluscontext is indicatief en geen diagnose. Bij hevige pijn, "
        "abnormaal bloedverlies, mogelijke zwangerschap, endometrioseklachten of "
        "aanhoudende klachten: raadpleeg arts, gynaecoloog of diëtist."
    )

    def to_dict(self) -> dict:
        return {
            "current_phase": self.current_phase.value,
            "cycle_day": self.cycle_day,
            "luteal_avg_symptom": self.luteal_avg_symptom,
            "follicular_avg_symptom": self.follicular_avg_symptom,
            "luteal_delta": self.luteal_delta,
            "alerts": self.alerts,
            "advice": self.advice.to_dict(),
            "data_quality": self.data_quality,
            "disclaimer": self.disclaimer,
        }


def cycle_day_for(recorded: date, cycles: list[MenstrualCycle]) -> Optional[int]:
    matching = [c for c in cycles if c.cycle_start_date <= recorded and (c.cycle_end_date is None or recorded <= c.cycle_end_date)]
    if not matching:
        prior = [c for c in cycles if c.cycle_start_date <= recorded]
        if not prior:
            return None
        cycle = max(prior, key=lambda c: c.cycle_start_date)
    else:
        cycle = max(matching, key=lambda c: c.cycle_start_date)
    day = (recorded - cycle.cycle_start_date).days + 1
    length = cycle.avg_cycle_length_days or 28
    return day if 1 <= day <= max(length, 45) else None


def phase_for_cycle_day(cycle_day: Optional[int], avg_cycle_length_days: int = 28) -> CyclePhase:
    if cycle_day is None:
        return CyclePhase.UNKNOWN
    if cycle_day <= 5:
        return CyclePhase.MENSTRUAL
    if cycle_day <= 13:
        return CyclePhase.FOLLICULAR
    if cycle_day <= 16:
        return CyclePhase.OVULATORY
    if cycle_day <= avg_cycle_length_days:
        return CyclePhase.LUTEAL
    return CyclePhase.UNKNOWN


def phase_advice(phase: CyclePhase, *, fodmap_sensitive: bool = True) -> CyclePhaseAdvice:
    low_fodmap_caution = "Gebruik laag-FODMAP als tijdelijke klachtenstrategie; herintroductie blijft belangrijk."
    if phase == CyclePhase.MENSTRUAL:
        return CyclePhaseAdvice(
            phase,
            ["pijn/energie monitoren", "herstel en slaap prioriteren"],
            ["ijzerrijke opties zoals mager rood vlees of spinazie", "zinkbronnen zoals eieren of pompoenpitten"],
            [low_fodmap_caution] if fodmap_sensitive else [],
        )
    if phase == CyclePhase.FOLLICULAR:
        return CyclePhaseAdvice(
            phase,
            ["training kan vaak makkelijker voelen", "blijf klachten loggen"],
            ["voldoende eiwit", "koolhydraten afstemmen op training, niet onnodig beperken"],
            [low_fodmap_caution] if fodmap_sensitive else [],
        )
    if phase == CyclePhase.OVULATORY:
        return CyclePhaseAdvice(
            phase,
            ["observeer buikpijn versus cycluspijn", "houd triggers apart van ovulatieklachten"],
            ["licht verteerbare maaltijden rond training", "hydratie en elektrolyten bij intensief sporten"],
            [low_fodmap_caution] if fodmap_sensitive else [],
        )
    if phase == CyclePhase.LUTEAL:
        return CyclePhaseAdvice(
            phase,
            ["let op opgeblazen gevoel, eetlust en obstipatie", "maak maaltijden kleiner als klachten toenemen"],
            ["magnesiumrijke opties zoals amandelen binnen portie", "calcium via lactosevrije zuivel", "spreid vezels rustig"],
            [low_fodmap_caution, "Cafeïne en zeer vette pre-workout maaltijden kunnen klachten versterken." ] if fodmap_sensitive else [],
        )
    return CyclePhaseAdvice(
        phase,
        ["cyclusdag ontbreekt"],
        ["voeg cycle_start_date of cycle_day toe voor faseadvies"],
        ["Zonder cyclusdata wordt geen hormoonpatroon geconcludeerd."],
    )


def _symptom_intensity(symptom: Symptom, hormonal: list[HormonalSymptom], cycles: list[MenstrualCycle]) -> Optional[tuple[CyclePhase, float]]:
    cycle_day = cycle_day_for(symptom.recorded_at.date(), cycles)
    phase = phase_for_cycle_day(cycle_day)
    if phase == CyclePhase.UNKNOWN:
        return None
    gi = max(symptom.abdominal_pain or 0, symptom.bloating or 0)
    same_day = [h for h in hormonal if h.recorded_at.date() == symptom.recorded_at.date()]
    hormone = max([max(h.pelvic_pain or 0, h.mood_irritability or 0, h.breast_tenderness or 0) for h in same_day] or [0])
    return phase, max(gi, hormone)


def analyze_cycle_hormones(
    symptoms: list[Symptom],
    cycles: list[MenstrualCycle] | None = None,
    hormonal_symptoms: list[HormonalSymptom] | None = None,
    *,
    today: Optional[date] = None,
    fodmap_sensitive: bool = True,
) -> HormoneAnalysis:
    cycles = cycles or []
    hormonal_symptoms = hormonal_symptoms or []
    today = today or date.today()
    cycle_day = cycle_day_for(today, cycles) if cycles else None
    current_phase = phase_for_cycle_day(cycle_day)

    buckets: dict[CyclePhase, list[float]] = {CyclePhase.FOLLICULAR: [], CyclePhase.LUTEAL: []}
    for symptom in symptoms:
        item = _symptom_intensity(symptom, hormonal_symptoms, cycles)
        if item is None:
            continue
        phase, intensity = item
        if phase in buckets:
            buckets[phase].append(float(intensity))
    for h in hormonal_symptoms:
        day = h.cycle_day or cycle_day_for(h.recorded_at.date(), cycles)
        phase = phase_for_cycle_day(day)
        intensity = max(h.pelvic_pain or 0, h.mood_irritability or 0, h.breast_tenderness or 0)
        if phase in buckets and intensity > 0:
            buckets[phase].append(float(intensity))

    follicular = round(mean(buckets[CyclePhase.FOLLICULAR]), 2) if buckets[CyclePhase.FOLLICULAR] else None
    luteal = round(mean(buckets[CyclePhase.LUTEAL]), 2) if buckets[CyclePhase.LUTEAL] else None
    delta = round(luteal - follicular, 2) if luteal is not None and follicular is not None else None
    alerts: list[str] = []
    quality = "insufficient_data"
    if len(buckets[CyclePhase.FOLLICULAR]) >= _MIN_PHASE_EVENTS and len(buckets[CyclePhase.LUTEAL]) >= _MIN_PHASE_EVENTS:
        quality = "pattern_ready"
        if delta is not None and delta >= _LUTEAL_DELTA_ALERT:
            alerts.append("Luteale fase toont hogere klachten dan folliculaire fase; behandel dit als patroonhypothese, geen diagnose.")
    elif cycles or hormonal_symptoms:
        quality = "partial_data"

    if any((h.pelvic_pain or 0) >= 8 for h in hormonal_symptoms):
        alerts.append("Hevige bekkenpijn gemeld; bespreek dit met arts of gynaecoloog.")
    if any(h.menstrual_flow and h.menstrual_flow.value == "heavy" for h in hormonal_symptoms):
        alerts.append("Hevig bloedverlies gemeld; medisch laten beoordelen bij aanhouden of zorgen.")

    return HormoneAnalysis(
        current_phase=current_phase,
        cycle_day=cycle_day,
        luteal_avg_symptom=luteal,
        follicular_avg_symptom=follicular,
        luteal_delta=delta,
        alerts=alerts,
        advice=phase_advice(current_phase, fodmap_sensitive=fodmap_sensitive),
        data_quality=quality,
    )


"""Weekly-recap video props — implements spec-report-artifacts (video half).

Emits a JSON-serialisable dict the Remotion subproject (video/) consumes. The Remotion
app has its own deps and is NOT imported here — this keeps the Python engine zero-dep.
"""

from __future__ import annotations

from .algorithms.fitstrong_score import FitStrongScore
from .engine import DISCLAIMER


def weekly_video_props(score: FitStrongScore, *, week_label: str) -> dict:
    return {
        "week_label": week_label,
        "score": score.score,
        "band": score.band,
        "subscores": score.subscores,
        "top_improvements": [i.to_dict() for i in score.improvements[:3]],
        "disclaimer": DISCLAIMER,
    }

"""Self-contained HTML report — implements spec-report-artifacts (HTML half).

Inline CSS + inline SVG, no external assets, no JS, no network. Opens offline by
double-click. Pure string building, deterministic, UTF-8.
"""

from __future__ import annotations

from html import escape
from typing import Optional

from .algorithms.daily_scheme import DailyScheme
from .algorithms.fitstrong_score import FitStrongScore
from .engine import Report

_BAND_COLOR = {
    "aandacht nodig": "#c0392b",
    "matig": "#e67e22",
    "goed": "#27ae60",
    "sterk": "#16a085",
}


def _gauge_svg(score: float, band: str) -> str:
    # Semi-circular-ish bar: 0..100 mapped to a 0..280px filled width.
    color = _BAND_COLOR.get(band, "#27ae60")
    fill = max(0.0, min(100.0, score)) / 100 * 280
    return (
        '<svg width="320" height="120" viewBox="0 0 320 120" role="img" '
        f'aria-label="Fit and Strong score {score} of 100">'
        '<rect x="20" y="50" width="280" height="22" rx="11" fill="#ecf0f1"/>'
        f'<rect x="20" y="50" width="{fill:.1f}" height="22" rx="11" fill="{color}"/>'
        f'<text x="20" y="38" font-size="26" font-weight="700" fill="{color}">{score:g}<tspan '
        'font-size="14" fill="#7f8c8d">/100</tspan></text>'
        f'<text x="300" y="38" font-size="14" text-anchor="end" fill="{color}">{escape(band)}</text>'
        '</svg>'
    )


def _alerts_html(report: Report) -> str:
    if not report.alerts:
        return "<p>Geen waarschuwingen.</p>"
    rows = []
    for a in report.alerts:
        crit = ' style="border-left:4px solid #c0392b;background:#fdecea"' if a.severity.value == "critical" else ""
        rows.append(f'<li{crit}><strong>{escape(a.alert_type)}</strong> '
                    f'({escape(a.severity.value)}): {escape(a.message)}</li>')
    return f'<ul class="alerts">{"".join(rows)}</ul>'


def _scheme_html(scheme: Optional[DailyScheme]) -> str:
    if scheme is None:
        return ""
    meal_rows = []
    for meal in scheme.meals:
        items = ", ".join(f'{escape(i["id"])} ({i["amount_g"]:g} g)' for i in meal.items) or "—"
        meal_rows.append(f"<tr><td>{escape(meal.label)}</td><td>{items}</td></tr>")
    cov = scheme.coverage
    notes = "".join(f"<li>{escape(n)}</li>" for n in scheme.notes)
    return (
        "<h2>Dagschema (indicatief)</h2>"
        f'<table><tr><th>Maaltijd</th><th>Items</th></tr>{"".join(meal_rows)}</table>'
        f"<p>Dekking t.o.v. doel — eiwit {cov['protein_pct']:g}%, "
        f"koolhydraten {cov['carbs_pct']:g}%, energie {cov['energy_pct']:g}%.</p>"
        f"<ul>{notes}</ul>"
    )


def render_html(report: Report, score: FitStrongScore, scheme: Optional[DailyScheme] = None) -> str:
    mt = report.macro_targets
    subs = "".join(f"<tr><td>{escape(k)}</td><td>{v:g}</td></tr>" for k, v in score.subscores.items())
    improvements = "".join(
        f"<li><strong>{escape(i.area)}</strong> ({i.score:g}/100): {escape(i.action)}</li>"
        for i in score.improvements
    ) or "<li>Geen directe verbeterpunten — goed bezig.</li>"
    triggers = "".join(f"<li>{escape(t.food_name)} (score {t.score:g})</li>" for t in report.triggers) \
        or "<li>Geen verdachte triggers gevonden.</li>"
    micro = f"{report.microbiome.score:g}/100" if report.microbiome else "n.v.t."
    referral = f'<p class="referral">{escape(report.referral_advice)}</p>' if report.referral_advice else ""

    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fit &amp; Strong rapport</title>
<style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#2c3e50;line-height:1.5}}
  h1{{margin-bottom:0}} h2{{margin-top:28px;border-bottom:2px solid #ecf0f1;padding-bottom:4px}}
  table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ecf0f1;padding:6px 8px;text-align:left}}
  ul.alerts{{list-style:none;padding-left:0}} ul.alerts li{{padding:6px 8px;margin:4px 0;background:#f8f9fa;border-radius:4px}}
  .referral{{background:#fff3cd;padding:10px;border-radius:6px}}
  .disclaimer{{margin-top:28px;font-size:13px;color:#7f8c8d;border-top:1px solid #ecf0f1;padding-top:10px}}
</style></head><body>
<h1>Fit &amp; Strong rapport</h1>
<p>Hoe fit &amp; strong ben je nu, en wat kan beter.</p>
{_gauge_svg(score.score, score.band)}
<h2>Wat kan beter</h2><ul>{improvements}</ul>
<h2>Subscores</h2><table><tr><th>Onderdeel</th><th>Score /100</th></tr>{subs}</table>
<h2>Dagdoelen (macro &amp; energie)</h2>
<table>
<tr><th>Eiwit</th><td>{mt.protein_g:g} g ({mt.protein_g_per_kg:g} g/kg)</td></tr>
<tr><th>Koolhydraten</th><td>{mt.carbs_g_low:g}–{mt.carbs_g_high:g} g ({escape(mt.carbs_basis)})</td></tr>
<tr><th>Energie</th><td>{mt.energy_kcal_low:g}–{mt.energy_kcal_high:g} kcal</td></tr>
</table>
<h2>Waarschuwingen</h2>{_alerts_html(report)}
<h2>Verdachte triggers (2–4 u)</h2><ul>{triggers}</ul>
<h2>Microbioom-score</h2><p>{micro} (indicatief)</p>
{_scheme_html(scheme)}
{referral}
<p class="disclaimer">{escape(report.disclaimer)}</p>
</body></html>"""

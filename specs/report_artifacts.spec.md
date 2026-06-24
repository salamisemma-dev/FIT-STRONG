---
id: spec-report-artifacts
type: orchestration
version: 1.0.0
status: approved
owner: fit-strong-core
depends_on: [spec-report-engine, spec-fitstrong-score, spec-daily-scheme]
consumed_by: [cli, fit-strong-skill, weekly-video]
---

## Intent
Render the engine's numbers into artefacts a human actually uses: a **self-contained HTML
report** (read it, act on it) and **weekly-video props** (data for an optional Remotion
recap clip). No web framework, no external assets — keeps the engine stdlib-only.

## Contract
`src/fit_strong/report_html.py::render_html(report, score, scheme=None) -> str`:
- One self-contained HTML document (inline CSS + inline SVG; no external links/JS).
- Sections: Fit&Strong score gauge (SVG, 0–100, banded), macro-targets table, alerts list
  (critical visually distinct), suspected triggers, microbiome score, improvements
  ("wat kan beter"), the daily scheme table if provided, and the disclaimer + referral.
- Pure string building; deterministic; UTF-8.

`src/fit_strong/video_props.py::weekly_video_props(score, *, week_label) -> dict`:
- JSON-serialisable props the Remotion composition consumes: `score`, `band`,
  `top_improvements` (≤3), `subscores`, `week_label`, `disclaimer`.
- The Remotion subproject lives under `video/` with its **own** package.json/deps; it is
  fed this dict and is not part of the Python package (isolation keeps the engine zero-dep).

## Business rules
- HTML must open offline by double-click; no network calls (privacy + works anywhere).
- Disclaimer always rendered; `critical` alerts never visually buried.
- The video is an optional artefact; the engine never requires Node to function.

## Downstream impact
CLI `--html <path>` writes the report; `--video-props <path>` writes the Remotion props.
The Remotion app reads the props JSON. Field renames ripple to `video/`.

## Verification
`tests/test_report_artifacts.py` — `render_html` returns one HTML doc containing the score,
disclaimer, and a scheme row, with no `http://`/`https://` external asset references;
`weekly_video_props` returns a JSON-serialisable dict with ≤3 improvements and the score.

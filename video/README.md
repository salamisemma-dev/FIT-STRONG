# Fit & Strong — weekly recap video (optional, Remotion)

An **optional** Remotion clip that turns a week's Fit & Strong score into a ~8-second
shareable video. It is **isolated** from the Python engine: own `package.json`, own deps.
The engine never needs Node to function (constitution: engine stays stdlib-only).

> Honest status: this subproject has now been **installed and rendered** in this workspace.
> `npm audit` reports 0 vulnerabilities, and `npm run render` produced `out/weekly-recap.mp4`
> from engine-generated `props.json`. The output folder and live props are ignored artifacts.

## Data flow
```
fit-strong <diary.json> --video-props video/props.json   # engine emits props
cd video && npm install                                   # one-time
npm run render                                            # -> out/weekly-recap.mp4
```
- `props.json` is produced by `fit_strong.weekly_video_props(...)` /
  `--video-props`. Shape mirrors `weeklyRecapSchema` in `src/WeeklyRecap.tsx`.
- `props.example.json` is a committed sample; `npm run render:example` uses it.

## Why a separate subproject
A health *report* you read and act on is the core UI (the self-contained
`--html report.html`). A video is a nice-to-have recap, wrong as a primary interface —
so it lives here, opt-in, and cannot drag Node/React deps into the engine.

## Verification
- `npm install` -> completed with 0 vulnerabilities after pinning Remotion `4.0.482` and zod `4.3.6`.
- `npm run render:example` -> rendered `out/example.mp4`.
- `fit-strong ../examples/sample_diary.json --video-props props.json` then `npm run render` -> rendered `out/weekly-recap.mp4`.

## Files
- `src/Root.tsx` — registers the `WeeklyRecap` composition (1080×1080, 30 fps, 8 s).
- `src/WeeklyRecap.tsx` — the component + zod schema (kept in sync with the engine props).
- `props.example.json` — sample input.

# Plan van Aanpak — Fit & Strong

**Datum:** 2026-06-24 · **Aanpak:** BOB (spec-driven, test-first) · **Stack:** Python ≥3.11, stdlib-only

## 1. Doel & scope

Een **evidence-based coaching-engine** + Claude-skill die een voedings-/klachten-/
trainingsdagboek omzet in persoonlijk advies, gebaseerd op vier pijlers: darm-spier-as,
SCFA, FODMAP-restrictie, trainingsbelasting.

**In scope (deze build):** pure rekenkern (macro-targets, FODMAP-load, triggerdetectie,
energiebalans, microbioom-score), getypte datamodellen, referentie-voedingsdatabase,
CLI, Claude-skill wrapper. BOB-proof: constitution + 8 specs + strikte validator + 43
tests.

**Buiten scope (roadmap):** web-frontend (Next.js), persistentie (Postgres/RLS), auth,
notificaties, ML-modellen. De engine blijft vrij van die zorgen zodat ze later als
laag erbovenop kunnen.

## 2. Architectuur

`models` (data, gevalideerd) → `algorithms` (puur, geen I/O) → `engine` (orkestratie)
→ `cli` / skill. Een lagere laag importeert nooit een hogere. Alle drempelwaarden zijn
gedocumenteerd met bron in de bijbehorende spec (geen "magic numbers").

## 3. Voor- en nadelen — met fix per nadeel

| # | Voordeel | — |
|---|----------|---|
| V1 | Wetenschappelijk traceerbaar: elke drempel staat in `docs/EVIDENCE.md` met **bron + confidence-level** (Strong/Moderate/Hypothesis) en eerlijke caveat; geen bluf. | |
| V2 | Pure functies → deterministisch, triviaal te testen (43 tests, 0.067s). | |
| V3 | Zero runtime-dependencies → draait overal met kale Python, geen supply-chain-risico. | |
| V4 | Spec-driven (BOB) → intentie is permanente, machine-gecontroleerde memory. | |
| V5 | Engine los van UI/DB → frontend & persistentie later inplugbaar zonder herschrijven. | |

| # | Nadeel | Fix (toegepast in deze build) |
|---|--------|-------------------------------|
| N1 | **Naïeve correlatie flagt onschuldige "bystander"-voeding** die toevallig in dezelfde maaltijd zat als de echte trigger. | **Gefixt:** triggerscore gewogen met FODMAP-niveau en very-low/low_fodmap bystanders worden niet als FODMAP-trigger gerapporteerd. Hoog-FODMAP-voeding rankt boven onschuldige low-FODMAP. Regressietest `test_high_fodmap_outranks_innocent_bystander`. |
| N2 | **Blueprint FODMAP-gewichten (0.8/0.4/0.1)** gaven absurde loads (50 g → 40 "g FODMAP"), drempel 15 g betekenisloos. | **Beheerst:** synthetische load-gewichten geschaald naar 0.08/0.04/0.01 en engine gebruikt `safe_portion_g` uit de food DB als extra alert-pad. Dit blijft een pragmatisch model, geen exact FODMAP-grammodel. |
| N3 | **Verzonnen getallen** als de gebruiker calorieën/eiwit niet opgeeft. | **Gefixt:** energiebalans accepteert partial input: ontbrekende calorieën/eiwit worden niet verzonnen, maar Bristol-events of losse eiwitdata kunnen nog steeds alerts geven. |
| N4 | **Onbekende voeding** verstilt de microbioom-score (lijkt compleet, is het niet). | **Gefixt:** `unresolved`-lijst geeft expliciet terug welke items niet in de DB zaten → score is eerlijk conservatief. |
| N5 | **Medisch risico**: advies kan als diagnose worden gelezen. | **Gefixt:** verplichte disclaimer in elk rapport + `referral_advice` bij ≥4–6 weken geen verbetering (constitution §4). |
| N6 | **Ongeldige invoer** (negatief gewicht, Bristol 9) corrumpeert berekeningen. | **Gefixt:** validatie bij constructie (`__post_init__`), `ValueError` aan de grens, spiegelt DB-CHECK-constraints. 7 modeltests. |
| N7 | **Windows + Nederlandse tekst** → mojibake in console. | **Gefixt:** CLI forceert UTF-8 stdout; validator is CRLF-safe. |
| N8 | **Spec-drift** (code wijkt af van bedoeling) over tijd. | **Beheerst:** `bob_validate.mjs --strict` (semver, dup-id, depends_on-resolutie, spec→test-bestandskoppeling, **food-DB mirror drift-gate**) + `bob_ready.mjs` in CI. Clause-niveau koppeling in `docs/TRACEABILITY.md` (handmatig onderhouden; machine-enforcement clause-niveau = backlog). |
| N9 | **Langdurig laag-FODMAP** kan microbioom schaden (open wetenschappelijk punt). | **Beheerst:** skill adviseert het 3-fasen klinische protocol (eliminatie→herintroductie→personalisatie) en waarschuwt expliciet; geen permanente strikte eliminatie. |
| N10 | **Voedingsdatabase is klein** (12 items) → veel `unresolved`. | **Beheerst:** DB is los JSON, uitbreidbaar zonder code; `unresolved` maakt dekking zichtbaar. Uitbreiden = roadmap. |
| N11 | **Dubbele food-DB** (`config/` source + packaged copy) was al gedrift (line-endings) → twee bronnen van waarheid. | **Gefixt:** kopieën gesynct + **drift-gate** in `bob_validate.mjs` (CRLF-genormaliseerd content-identity) + test `test_food_db_source_and_packaged_copy_are_identical`. Negatief getest (gate faalt bij drift). |

## 4. Roadmap (buiten deze sessie)
0. **Evidence-verharding:** elke Moderate/Hypothesis-rij in `docs/EVIDENCE.md` pinnen op editie/DOI/URL; heuristische FODMAP-gewichten vervangen door Monash per-portie-data; energie-floor op FFM i.p.v. totaal lichaamsgewicht zodra lichaamssamenstelling-input bestaat. Clause-niveau traceability machine-enforced maken (`docs/TRACEABILITY.md` backlog).
1. Voedingsdatabase uitbreiden (NEVO / Monash-FODMAP bronnen).
2. Persistentielaag (Postgres-schema uit blueprint) + RLS.
3. Next.js frontend met de Energie-Barometer-component.
4. ML: trigger-predictie & energie-forecast (mappen op bestaande pure features).
5. Notificatie-service (dagboek-reminders).

## 5. Definition of Done (deze build) — gehaald
- [x] Constitution + 8 approved specs, strikte validator groen.
- [x] Pure engine + modellen + CLI + food-DB.
- [x] 43 tests groen (`unittest`, stdlib).
- [x] CLI end-to-end op voorbeelddagboek.
- [x] Claude-skill wrapper.
- [x] Elk geïdentificeerd nadeel gefixt of expliciet beheerst.

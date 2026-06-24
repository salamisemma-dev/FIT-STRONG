# Evidence base — Fit & Strong

Every numeric threshold in the engine is listed here with its source and an **honest
confidence level**. This file exists because "elke drempel heeft een bron" was a bluff
until the sources were named and calibrated. Where a value is a pragmatic simplification
of the underlying science, that is stated — not hidden.

**Confidence legend**
- **Strong** — backed by a position stand / consensus statement / well-established scale.
- **Moderate** — supported by primary studies or guideline bodies, but with caveats.
- **Hypothesis** — plausible, from the source blueprint, not independently verified here;
  drives only *indicative* output, never clinical advice.

| Threshold (engine location) | Value | Source | Confidence | Honest caveat |
|---|---|---|---|---|
| Protein g/kg (`macro_targets.py`) | 1.6 / 1.8 / 2.0 g/kg by goal | Jäger et al., ISSN Position Stand on protein & exercise, *J Int Soc Sports Nutr* 2017;14:20. Morton et al., *Br J Sports Med* 2018;52:376–384 (≈1.6 g/kg breakpoint, up to ~2.2). | **Strong** | Goal-based split (endurance 1.8) is our allocation within the evidence band, not a per-goal value from one paper. |
| Carb band moderate 3–5 / intensive 5–7 g/kg (`macro_targets.py`) | tied to ≥7 h/wk | Thomas, Erdman, Burke. ACSM/AND/Dietitians of Canada Joint Position Statement *Nutrition and Athletic Performance*, *Med Sci Sports Exerc* 2016;48:543–568 (carbs by training load: light 3–5, moderate 5–7, high 6–10 g/kg/day). | **Strong** | We collapse the guideline's load tiers to a single 7 h/wk split — a coarse proxy for training load, not a cited cut-point. |
| Energy floor 30 kcal/kg (`energy_balance.py`) | < 30 kcal/kg → alert | Low energy availability threshold ≈30 kcal/kg **fat-free mass**/day (Loucks; IOC RED-S consensus, Mountjoy et al., *Br J Sports Med* 2018). | **Moderate** | **Simplification:** engine uses 30 kcal/kg **total body weight**, not FFM. It is a conservative under-fuelling flag, not a RED-S diagnosis. |
| Energy maintenance 30–35 kcal/kg; +300–500 kcal surplus (`macro_targets.py`) | range | General sports-nutrition practice; surplus for hypertrophy ~ +10–20%. | **Moderate** | Practical heuristic; individual needs vary with body composition & activity. |
| Bristol 6–7 = loose; >3/day → dehydration flag (`energy_balance.py`) | | Lewis & Heaton, Bristol Stool Form Scale, *Scand J Gastroenterol* 1997;32:920–924. | **Strong (scale)** / **Moderate (>3/day cut-off)** | Bristol scale itself is validated; the ">3 loose/day → fluid/K⁺ risk" cut-off is a pragmatic safety heuristic, not a clinical criterion. |
| FODMAP correlation window 2–4 h (`trigger_detection.py`) | | Symptom onset after fermentable-carb ingestion; low-FODMAP in athletes: Lis et al., *Med Sci Sports Exerc* 2018;50:116–123; reviews of low-FODMAP & GI symptoms. | **Moderate** | Onset timing varies by transit & food; 2–4 h is a reasonable default, configurable. |
| FODMAP level → suspicion weights 1.0/0.6/0.3/0.1 (`trigger_detection.py`) | | Derived from FODMAP-level concept (Monash University FODMAP program). | **Moderate (concept)** / **Hypothesis (exact weights)** | The weights are our heuristic ranking, **not** measured FODMAP grams. |
| Synthetic FODMAP load weights 0.08/0.04/0.01; 15 g/meal threshold (`fodmap_load.py`) | | Scaled 1/10 from the source blueprint (0.8/0.4/0.1). | **Hypothesis** | Pragmatic relative-burden model, **not** a Monash gram-per-portion model. `safe_portion_g` from the food DB is the more grounded alert path. |
| Fibre target 30 g/day (`microbiome_score.py`) | | EFSA Dietary Reference Values for carbohydrates & fibre, 2010 (≥25 g/day adequate); Gezondheidsraad *Richtlijnen goede voeding* 2015 (~30 g/day, 14 g/1000 kcal). | **Strong** | Population target; athletes' needs may differ. |
| Prebiotic-points anchor 20 pts; 0–10 per-food `prebiotic_score` (`microbiome_score.py`) | | Heuristic encoding of prebiotic/fermentable-fibre richness. | **Hypothesis** | Per-food scores are expert-estimate, not lab values; the 0–100 score is explicitly **indicative**. |
| Gut–muscle axis / *Roseburia inulinivorans* ↔ grip strength | rationale for prebiotic emphasis | Reported in the source blueprint (LUMC/Granada/Almería line of work). | **Hypothesis** | Not independently verified in this repo. Motivates the prebiotic score only; drives **no** clinical/medical advice. |
| Cycle-aware hormone/FODMAP context (`cycle_hormone.py`): phase buckets day 1-5/6-13/14-16/17-28; luteal alert delta >=1.5 with >=2 events per phase | phase mapping + pattern threshold | Low-FODMAP has evidence for IBS symptom control but should be temporary/professional-guided; estrogen-gut pain mechanism is early/preclinical; estrobolome literature is mostly associative. See Monash/FODMAP history, Gut 2022 IBS review references, UCSF/Science reporting on estrogen/PYY gut-pain mechanism, estrobolome reviews. | **Moderate (IBS/FODMAP)** / **Hypothesis (cycle pattern threshold)** | No hormone diagnosis. Phase windows and delta are journaling heuristics; cycle length varies, hormonal contraception/perimenopause/endometriosis require clinician context. |
| Fit & Strong composite weights (`fitstrong_score.py`): protein .25 · energy .20 · microbiome .20 · fodmap .15 · training .10 · symptoms .10; band cuts 40/60/80; improvement cut 70; FODMAP day-cap 45 g; training target 5 h/wk | | Editorial heuristic combining the cited subscore inputs into one headline number. | **Hypothesis** | The **weighting and the composite itself are not validated**. It is a motivational summary, not a diagnosis or fitness measurement. Subscore *inputs* carry their own confidence (rows above). |

## What this does NOT claim
- It is **not** a validated clinical decision tool. All output is indicative (constitution §4).
- FODMAP elimination is a clinician-supervised 3-phase protocol; the skill flags this and
  warns that long-term strict low-FODMAP may harm the microbiome.
- Numbers above marked **Hypothesis** are scaffolding for *relative* signals (ranking,
  indicative scores), never absolute medical thresholds.

## Hardening backlog (next round)
Pin each **Moderate/Hypothesis** row, especially cycle/hormone rows, to a specific edition/DOI/URL, replace the
heuristic FODMAP weights with Monash per-portion data where licensing allows, and
switch the energy floor to FFM when body-composition input is available.

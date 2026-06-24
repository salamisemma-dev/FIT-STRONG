# App PvA — Fit & Strong Voedingsdagboek

**Doel:** een extreem eenvoudige dagboek-app waarmee een leek dagelijks eten, drinken, supplementen, klachten, training en herstel invult. De app exporteert per dag of week engine-klare JSON zodat de Python-repo analyses kan draaien zonder handmatig overtypen.

## 1. Kernidee

De app is geen medische app en geen calorie-app voor gevorderden. Het is een begeleid dagboek:

1. Vandaag openen.
2. Eten/drinken toevoegen met tijd, hoeveelheid en eventueel FODMAP-inschatting.
3. Klachten invullen met simpele schuifjes.
4. Training/herstel invullen.
5. Voor vrouwen optioneel cycluscontext invullen.
6. Dag afsluiten.
7. Export naar `daily_diaries/YYYY-MM-DD.json` of weekbundel.

## 2. Leek-modus eerst

De standaardmodus moet zo weinig mogelijk vragen tonen:

- Grote knoppen: Ontbijt, Lunch, Avondeten, Snack, Drank, Supplement, Klacht, Training.
- Hoeveelheden mogen als gram, portie, stuk, glas, schep of handje.
- Onbekend mag leeg blijven.
- Veelgebruikte producten verschijnen bovenaan.
- Herhaal gisteren / herhaal maaltijd-knop.
- FODMAP wordt optioneel: laag/middel/hoog/onbekend.
- Elke dag krijgt een voortgangsbalk: eten, klachten, training, slaap/herstel.

## 3. Datamodel richting engine

De app exporteert hetzelfde shape als de CLI nu leest:

- `client`: gewicht, lengte, geslacht, doel, sporturen.
- `meals`: tijd + food items + hoeveelheid.
- `symptoms`: tijd + Bristol + pijn + opgeblazen + energie.
- `workouts`: tijd + type + duur + intensiteit.
- `day_calories`, `day_protein_g`, optioneel.
- `fodmap_sensitive`, optioneel.
- `menstrual_cycles` en `hormonal_symptoms`, alleen als gebruiker dit zelf invult.
- `supplements`, later te koppelen aan combination-engine.

## 4. MVP-schermen

1. **Onboarding:** man/vrouw/anders, doel, gewicht, lengte, sporturen, FODMAP-gevoelig ja/nee/onbekend.
2. **Vandaag:** simpele dagkaart met knoppen en voortgang.
3. **Maaltijd toevoegen:** tijd, product, hoeveelheid, snelle favorieten.
4. **Klacht toevoegen:** Bristol, buikpijn, opgeblazen, energie.
5. **Training/herstel:** type, duur, intensiteit, slaap, stress, water.
6. **Cycluscontext:** alleen zichtbaar als gebruiker dit aanzet.
7. **Analyse export:** dag/week exporteren naar repo-map of bestand delen.
8. **Rapport bekijken:** HTML-rapport openen dat de engine maakt.

## 5. Voor- en nadelen met fix

| # | Voordeel | Waarom nuttig |
|---|----------|---------------|
| V1 | Minder overtypen | Gebruiker vult dagelijks in; engine krijgt nette JSON. |
| V2 | Lage drempel | Grote knoppen, favorieten en herhaalopties maken het bruikbaar voor leken. |
| V3 | Betere analyse | Tijdstippen, klachten en hoeveelheden worden consistenter bijgehouden. |
| V4 | Man/vrouw bruikbaar | Basis is gelijk; cycluscontext is optioneel en expliciet. |
| V5 | Repo blijft bron van analyse | App verzamelt data; Python-engine blijft testbare rekenkern. |

| # | Nadeel | Fix |
|---|--------|-----|
| N1 | Te veel vragen maakt invullen irritant. | Leek-modus met alleen kernvelden; geavanceerde velden inklapbaar. |
| N2 | Mensen weten geen grammen. | Porties toestaan: stuk, glas, handje, schep; later converteren met onzekerheidslabel. |
| N3 | FODMAP-inschatting is moeilijk. | `onbekend` is standaard toegestaan; engine mag niets verzinnen. |
| N4 | Cyclusdata kan medisch voelen. | Opt-in, apart scherm, geen diagnose, geen verplicht veld, duidelijke disclaimer. |
| N5 | Privacyrisico door gezondheidsdata. | Local-first MVP; export alleen door gebruiker; geen cloud zonder expliciete toestemming. |
| N6 | Barcode/fotoherkenning kan fout zijn. | Niet in MVP; later alleen met bevestiging door gebruiker. |
| N7 | Analyse kan als oordeel voelen. | Rapport toont verbeterpunten praktisch en indicatief, geen schuldtaal. |
| N8 | Repo-import kan technisch zijn. | Exportknop maakt `YYYY-MM-DD.json`; later auto-sync naar ingest-folder. |
| N9 | Dagboek vergeten. | Zachte reminder en incomplete-dag status; geen straf of streak-pressure. |
| N10 | Verschil man/vrouw kan te binair worden. | Onboarding heeft man/vrouw/anders; cyclusmodule is losse opt-in feature, niet afgeleid uit geslacht. |

## 5b. Brutale review — nadelen die het oorspronkelijke plan miste (met fix)

| # | Nadeel (eerlijk) | Fix |
|---|------------------|-----|
| N11 | **3D-motion vs leek-snelheid/perf.** Zware motion botst met "lage drempel" en laat low-end telefoons haperen; kan first-use vertragen. | Motion = puur decoratieve laag. Alleen GPU-goedkope `transform`/`opacity` (geen layout/box-shadow-animatie in lijsten). Lazy scroll-reveal. Motion blokkeert nooit input. `prefers-reduced-motion` = volledige kill-switch (zit al in de prototype). |
| N12 | **Engine is Python; de browser kan hem niet draaien.** "Export JSON → draai CLI" geeft een leek géén rapport in de app — de kern-belofte ("hoe fit ben ik") werkt niet in-app. **Grootste eerlijkheidsgat.** | MVP eerlijk: app = invoer + export, rapport via CLI (door jou). Echt in-app rapport vereist óf de scoring/report-logica geport naar JS, óf een kleine hosted endpoint die de Python-engine draait. Expliciet als **roadmap** gelabeld; niet doen alsof MVP dit al kan. |
| N13 | **Portie→gram conversie ontbreekt.** Plan zegt "later converteren met onzekerheidslabel" maar er is geen tabel; zonder gram kan de engine macro's niet schatten. | Lever een huishoudmaat→gram tabel als **data** (per categorie: glas=250 ml, schep=30 g, handje noten=20 g, …), met `estimated:true` vlag in de JSON zodat downstream weet dat het een schatting is. |
| N14 | **Toegankelijkheid** (motion, contrast, gezondheidscontext). | WCAG-AA contrast, `prefers-reduced-motion`, toetsenbord/focus, schaalbare tekst, geen kleur-alleen-betekenis (FODMAP-tags ook tekst). |
| N15 | **Schema-drift app↔engine.** App-JSON moet exact matchen met wat de CLI leest; nu geen gate. | Publiceer een JSON Schema voor de diary, voeg `fit-strong --validate-diary <file>` toe en een CI-check; de app valideert vóór export. |
| N16 | **3D-tilt/parallax kan op touch niet werken of misselijk maken.** Hover-tilt bestaat niet op mobiel; parallax kan vestibulaire klachten geven. | Tilt alleen op pointer/hover-capable devices (`@media (hover:hover)`); op touch een subtiele press-scale. Parallax beperkt + uit bij reduced-motion. |
| N17 | **"Data uit Samsung Notes/Keep of iPhone Notities droppen" kan niet rechtstreeks.** Een webapp heeft geen API om andermans notitie-apps te lezen — de belofte zou vals zijn. | Realistische mechanismen: (a) **plakken** (kopieer notitie → plak → parse regels, in prototype), (b) **.txt slepen** (desktop, in prototype), (c) **Web Share Target** (Android-PWA: deel-knop vanuit Notes → app) = roadmap, (d) iOS: Share Sheet/Shortcuts = beperkt, roadmap. Geen valse auto-sync-belofte. |
| N18 | **Light theme kan contrast/leesbaarheid breken** t.o.v. dark-getunede accenten. | Aparte light-tokens (donkerder primair/cyaan/groen voor AA-contrast op licht), thema persist in localStorage, volgt `prefers-color-scheme` als geen keuze. |

## 9. Visuele richting — hyperflow & 3D motion

Geïnspireerd op de SALAMIS- en saldiapp brand-designs. **Concreet prototype:** [`app/prototype/index.html`](../app/prototype/index.html) (self-contained, offline, zero deps) — het "Vandaag"-scherm met de volledige richting.

**Designtokens (uit de brand-HTML's):**
- Achtergrond cyber-dark `#060810`; glas-surfaces (`rgba(255,255,255,.04–.07)`, `backdrop-filter: blur`).
- Primair indigo `#4361EE` → paars `#6d28d9`/`#BD93F9`; accent cyaan `#66FCF1` + groen `#39FF86` (score), roze `#FF00B4`, goud `#FFD166`, koraal `#FF6B6B` (waarschuwing).
- Type: Inter (UI) + JetBrains Mono (cijfers/specs).
- Easings: cinema `cubic-bezier(.16,1,.3,1)`, snap `cubic-bezier(.34,1.56,.64,1)`.

**Hyperflow-motion-vocabulaire:**
- Drijvende radiale **orbs** + fijne **grain**-overlay als levende achtergrond.
- **Scroll-reveal** (IntersectionObserver, fade-up) per sectie.
- **Floating/3D-tilt** kaarten (hover-tilt op pointer-devices, press-scale op touch).
- **Glassmorphism** nav + bottom-sheet; geanimeerde **score-ring** (SVG stroke-dashoffset).
- Gradient-glow accenten; alles **GPU-goedkoop** en **uit bij `prefers-reduced-motion`**.

**Niet-onderhandelbaar:** motion mag de leek-snelheid nooit schaden. De data-laag (invoer→export→engine) werkt identiek met motion volledig uit.

**Themes:** licht én donker, beide met de tokens hierboven (light = donkerder primair/cyaan/groen voor AA-contrast). Keuze persist; volgt anders systeemvoorkeur.

**Profiel & cyclus:** segmented `Man | Vrouw` in de nav. Bij `Vrouw` verschijnt een opt-in **Cyclus**-kaart (fase + cyclusdag + fase-tip), gekoppeld aan de bestaande `spec-cycle-hormone` engine-logica. Cyclus is nooit afgeleid uit geslacht-alleen en nooit verplicht (N4/N10).

**Notities & import:** vrije notitie-veld (snelle log) + een **"Importeer uit Notities"**-blok (plak tekst of sleep `.txt`; regel-parser herkent tijd + product). Zie N17 voor de eerlijke grens t.o.v. Samsung/iPhone-notitie-apps.

Alle vier (themes, profiel/cyclus, notities, import) staan werkend in de prototype [`app/prototype/index.html`](../app/prototype/index.html).

## 6. Technische aanpak

**Aanbevolen MVP:** lokale webapp of PWA.

- Frontend: React/Next.js of eenvoudige Vite PWA.
- Opslag MVP: browser localStorage/IndexedDB.
- Export: JSON-bestand downloaden.
- Analyse: JSON in repo plaatsen en `fit-strong dag.json --html rapport.html` draaien.
- Later: desktop wrapper of mobiele app, plus automatische map-sync.

## 7. Bouwvolgorde

1. JSON-schema stabiliseren voor dagelijkse diary input.
2. PWA wireframe bouwen met `Vandaag` als eerste scherm.
3. Export maken naar engine-compatible JSON.
4. Import smoke-test met CLI.
5. HTML-rapport openen vanuit app.
6. Favorieten, herhalen, supplementen en cyclus opt-in toevoegen.
7. Pas daarna accounts/cloud/persistentie.

## 8. Definition of Done voor MVP

- Een leek kan binnen 2 minuten zijn eerste dag starten.
- Dag invullen kan zonder grammen te weten.
- Exportbestand draait door de bestaande CLI.
- Man/vrouw/anders onboarding werkt zonder cyclusdata te forceren.
- Vrouwelijke cycluscontext verschijnt alleen bij opt-in.
- Geen medische claims, geen diagnose, geen cloudplicht.

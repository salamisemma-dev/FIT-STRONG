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

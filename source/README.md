# Voyage: AP World Daily (production notes)

Boreen-style daily game for James's AP World History class. Live artifact:
https://claude.ai/artifact/NqBkj3FSw6SKtkyE39qfA4 (slug b0ca3d79-3ecc-4440-89d8-f38484e806e5)

## How the schedule works
- One voyage per calendar day, Day 1 = Mon 23 Nov 2026, last = Wed 5 May 2027 (164 days).
  The AP World History: Modern exam is Thu 6 May 2027.
- Unit for day n = ((n-1) mod 9) + 1, so CED Units 1-9 rotate daily (James chose "cycle all 9 units", "every day").
- Voyage used = data/u{unit}.json voyages[k mod count], with k = floor((n-1)/9).
  Units 1-2 need 19 voyages each, Units 3-9 need 18 each for no repeats (164 total).
- Progress is stored per device in localStorage key "voyage-d{n}". Teacher preview (footer) steps through any day without saving.

## Gameplay
5 questions, 30 s each, many accepted answers per question, wrong guesses free, first right answer kept.
Tiers: 1 Pepper 10 km, 2 Silk 25 km, 3 Silver 50 km, 4 Gem 100 km. Stops at 0/90/200/330/500 km.
Matching: case/accent/punctuation-insensitive, plural-tolerant, typo tolerance 1 (5-8 chars) or 2 (9+ chars).

## Files
- content/u{1-9}.txt: question source. Format:
  `#unit N | Title | Era`, `@voyage routeId | Title | Subtitle`, `? Category | Question`,
  then `T Display name|alias|alias;` items (T = tier 1-4).
- build.py: parses content -> data/u{N}.json and validates (5 questions, map exists, duplicate aliases).
- routes.json + gen.mjs: route definitions (5 named stops, 4 legs of [lon,lat] waypoints, projection center).
  gen.mjs (npm i world-atlas d3-geo topojson-client) writes maps.json; split into maps/{route}.json.
- index.html: engine (inline JS); fetches data/ and maps/ relative to the artifact.
- Publish: publish_files to the slug above, patch mode, with new data/maps files.

## Coverage as of 27 Nov 2026
93 voyages written: Unit 4 has 13; every other unit has 10.
Unique voyages run through Day 90 (Sat 20 Feb 2027); after that a unit's voyages repeat until more are added.
Next batches should add 2 voyages per unit (18 per batch) and reuse routes where sensible.
Build: build.py reads maps/ and writes data/ next to itself, so run it with symlinks
(source/maps -> ../maps, source/data -> ../data) or copy the output into the repo folders.
gen.mjs falls back to "M0,0" when a tiny regional map has no graticule line in view.

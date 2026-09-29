# TravelMap — status / handoff

Written so a future session (any machine) can pick this up cold. Keep it current as
things move — it's the source of truth alongside the code itself.

**Testing/verification workflow:** treat `https://spdltd-spdco.github.io/travelmap/` as
the check of record, not a local server. A local `python3 -m http.server 8080` (via WSL)
still works fine for the owner's own manual testing in a real browser (it's on the key's
referrer allow-list) — but Claude's own Browser-pane tool has repeatedly hit caching
layers (a local-preview-proxy bug, and separately GitHub Pages' own `Cache-Control:
max-age=600` on the live site) that serve a stale snapshot even across brand-new tabs.
Direct `curl` and the owner's real browser are unaffected. If a just-pushed change
doesn't show up when checking via the Browser pane, re-navigate with a `?r=<n>`
cache-busting query string before concluding something's broken.

## What this is

Personal, online-only Google Maps tool for a Japan trip. Two users max (owner + one
friend), nothing sensitive in it. Two pages + one data file + a generator script:

- `index.html` — the **viewer**: fixed neighborhood regions + categorized POIs from
  `data/japan.geojson`, a **regions menu** (▤ button in the top bar) that lists every
  region and jumps/pulses/pops up whichever one you tap, live Places search that drops a
  pin and shows its relationship to the fixed layer (containing/nearest neighborhood,
  nearest fixed POIs + distances, directions deep link), geolocation "where am I".
  Mobile-tuned for Android Chrome/Brave/Firefox (see README "Using Firefox or Brave").
- `edit.html` — the **builder**: draw polygons/POIs on a map, exports `japan.geojson`.
- `data/japan.geojson` — the fixed layer, generated (don't hand-edit — see below).
  Currently **12 regions** (3 hand-traced real boundaries, 9 generated blobs — see
  "Region data status") **+ 6 POIs**.
- `tools/regions.json` + `tools/gen_regions.py` — the actual source for regions. Each
  entry is either `{center, radius_m}` (auto-generates a natural-looking irregular blob,
  deterministic per name) or `{path: [[lat,lng], ...]}` (used as-is — for a hand-traced
  boundary). Re-run `python3 tools/gen_regions.py` after editing regions.json; it
  merges into `data/japan.geojson` by name, leaving POI points and any untracked
  polygons alone, and bumps `updated`.
- `manifest.webmanifest` + `icons/` — installable as a home-screen app (PWA / WebAPK).

## Region data status

**Hand-traced (real boundaries, via Google Maps right-click "What's here?"):**
Kabukicho (6 pts), Golden Gai (4 pts, nested inside Kabukicho on purpose), Omoide
Yokocho (4 pts, also inside/adjacent to Kabukicho). Overlapping regions are fine and
expected — the relationship panel already handles a point being inside multiple.

**Still generated blobs** (illustrative, not real boundaries — fine for now, but not
"traced" the way the three above are): Shibuya, Harajuku / Omotesando, Shimokitazawa,
Asakusa, Akihabara, Ginza, Roppongi, Ueno, Nakameguro.

Tracing more of these the same way (owner right-clicks in the Browser pane, Claude reads
the coordinates off-screen and relays them back — direct automated right-clicking turned
out to be too unreliable to use solo) is the natural next content task, whenever wanted.

## Key design decisions (don't relitigate these without reason)

- **GeoJSON, not XML/KML** — the owner said "xml" colloquially early on; GeoJSON is
  what's actually used throughout.
- **Data lives in this same public repo**, fetched at runtime from
  `raw.githubusercontent.com/.../main/data/japan.geojson` (CORS-friendly, updates on a
  plain `git push`, no app redeploy needed). Falls back to the relative
  `./data/japan.geojson` if that fetch fails (local dev, or before first GitHub push).
- **API key is never committed.** `HARDCODED_KEY = ""` in both HTML files. The viewer
  shows an in-app dialog (first load, or via the ⚙ button) and stores the key in
  `localStorage` under `travelmap.apiKey` — shared between `index.html` and `edit.html`
  since they're one origin. A rejected key auto-clears and reprompts. The real
  protection is the key's HTTP-referrer restriction, not secrecy.
- **Online-only, by owner's explicit direction** — no offline/service-worker complexity.
- **POI categories**: hotel / restaurant / bar / sight / transit / other, each with a
  color + icon, set per-marker in the builder.
- **Regions carry `blurb` (one-line, always visible under the name label) and `notes`**
  (deeper, shown only in the click/menu popup) — separate fields, don't collapse them.

## Remotes

- `origin` → `https://github.com/spdltd-spdco/travelmap.git` (public repo). Auth is a
  GitHub fine-grained PAT (repo-scoped to `travelmap`, Contents read/write only) stored
  via `git credential approve` in Windows' credential store — pushes are non-interactive.
- `nas` → `\\nasraid\git\TravelMap\TravelMap.git` — a bare repo on the NAS git share
  (same convention as `\\nasraid\git\BetAllaire\BetAllaire.git`), a dumb storage mirror
  kept in lockstep with `origin`. Needs LAN access (fails cleanly off-network — that's
  fine, it's not required for day-to-day work, just resync when back on the LAN). No
  server-side software runs there. Push both together:
  ```
  git push origin main
  git push nas main
  ```
- Both remotes were last confirmed in sync at `6c0906f` (2026-09-11).

## Fully done

1. ✅ GitHub repo + Pages live at `https://spdltd-spdco.github.io/travelmap/`.
2. ✅ Raw data URL confirmed working (200, GeoJSON, CORS header).
3. ✅ Billing linked (account `013F7F-82DF1C-D6F8B2`, free trial) to project
   `travelmap-508223`; Maps JavaScript API + Places API (legacy, which the code actually
   calls) + Places API (New) all enabled.
4. ✅ Key (named "TravelMap") created, restricted, and **verified working end-to-end**
   live on Pages — map renders, zooms to the regions, search/relationship panel/regions
   menu all confirmed functioning. Website restrictions as Google's form actually
   accepts them (exact port, no wildcard on `http://`):
   ```
   http://localhost:8080/*
   http://127.0.0.1:8080/*
   https://spdltd-spdco.github.io/travelmap/*
   ```
   Add another exact-port entry if a local test server ever runs on a different port.
5. ✅ `#map` 0-height CSS bug fixed (see "Fixed bugs").
6. ✅ Regions menu + mobile/touch optimizations for Android Chrome/Brave/Firefox
   (overscroll, tap-highlight, touch-action, 44px targets, zoom-control repositioning).
7. ✅ Kabukicho / Golden Gai / Omoide Yokocho hand-traced to real boundaries.

## Outstanding

- Hand-trace the remaining 9 neighborhoods if/when wanted (see "Region data status").
- Curate real POIs beyond the original 6 samples, if wanted.
- Confirm phone install: Chrome/Brave → ⋮ → **Add to Home screen** (WebAPK) for the
  owner + friend. Not yet confirmed actually done on a real device as of last session.
- Nothing is blocking; the app is live, working, and usable today.

## Fixed bugs

- **`#map` rendered 0px tall.** `google.maps.Map` sets an inline `position:relative` on
  its container, silently beating our plain `#map{position:...}` rule (inline beats a
  non-`!important` stylesheet rule) and collapsing `inset:0` since a statically-flowed
  div has no intrinsic height. Fixed with `!important` on `position` in both
  `index.html` (viewport-positioned, also given explicit `height:100dvh;width:100%`) and
  `edit.html` (positioned against `<main>`, a sized grid cell — no explicit height there,
  a `100vh` would overflow past the cell).

## Cowork prompts issued (all resolved)

Three rounds, all in the owner's chat history: (1) create the GitHub repo + Google Cloud
project/key; (2) enable Pages + verify the raw data URL; (3) diagnose the key's referrer
restrictions after a `RefererNotAllowedMapError` on local testing.

## Full history

Everything is in git — this file plus the code is a complete, current snapshot. No
credentials, keys, or secrets exist anywhere in the repo or this file — the key lives
only in each device's browser `localStorage`.

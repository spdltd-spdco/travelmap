# TravelMap — status / handoff

Written so a future session (any machine) can pick this up cold. Keep it current as
things move — it's the source of truth alongside the code itself.

## What this is

Personal, online-only Google Maps tool for a Japan trip. Two users max (owner + one
friend), nothing sensitive in it. Two pages + one data file:

- `index.html` — the **viewer**: fixed neighborhood regions + categorized POIs from
  `data/japan.geojson`, live Places search that drops a pin and shows its relationship
  to the fixed layer (containing/nearest neighborhood, nearest fixed POIs + distances,
  directions deep link), geolocation "where am I".
- `edit.html` — the **builder**: draw polygons/POIs on a map, exports `japan.geojson`.
- `data/japan.geojson` — the fixed layer. Currently a **sample Tokyo dataset** (4
  neighborhoods, 8 POIs) — not yet the owner's real curated data.
- `manifest.webmanifest` + `icons/` — installable as a home-screen app (PWA / WebAPK).

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

## Remotes

- `origin` → `https://github.com/spdltd-spdco/travelmap.git` (public repo, created
  empty by Cowork). **As of this writing, `main` has not been pushed there yet** — the
  push needs interactive GitHub sign-in (Git Credential Manager), so it has to be run
  from an actual terminal, not a headless/background one:
  ```
  git push -u origin main
  ```
- `nas` → `\\nasraid\git\TravelMap\TravelMap.git` — a bare repo on the NAS git share
  (same convention as `\\nasraid\git\BetAllaire\BetAllaire.git`), used purely as a dumb
  storage mirror. No server-side software runs there. Push alongside origin:
  ```
  git push origin main
  git push nas main
  ```

## Outstanding, in order

1. **Push to GitHub** (`git push -u origin main` — owner runs this, needs browser auth).
2. **Enable GitHub Pages**: repo → Settings → Pages → Deploy from branch → `main` / root
   → Save. Expected URL: `https://spdltd-spdco.github.io/travelmap/`.
3. **Verify the raw data URL** now serves the file:
   `https://raw.githubusercontent.com/spdltd-spdco/travelmap/main/data/japan.geojson`
   should return 200, a GeoJSON body, and an `access-control-allow-origin` header.
4. **Google Cloud — blocked on billing.** Project `travelmap-508223` exists, but the
   Google account (`sstenton@gmail.com`) has no billing account at all. Once one is
   linked: enable Maps JavaScript API + Places API, create key `travelmap-web`,
   restrict it —
   - referrers: `http://localhost:*/*`, `http://127.0.0.1:*/*`,
     `https://spdltd-spdco.github.io/travelmap/*`
   - APIs: Maps JavaScript API + Places API only.
5. Open the deployed site, paste the key once via the **⚙** button.
6. Replace the sample dataset: curate real neighborhoods/POIs in `edit.html`, **Export
   japan.geojson**, overwrite `data/japan.geojson`, commit, push (both remotes).
7. Install on phones: Chrome → ⋮ → **Add to Home screen** (WebAPK) is the primary path
   for the owner + one friend. A standalone `.apk` via pwabuilder.com is documented in
   the README as a fallback if a literal installable file is wanted.

## Cowork prompts already issued

Two rounds, both in the owner's chat history: (1) create the GitHub repo + Google Cloud
project/key — GitHub side completed, Google Cloud side blocked on billing as above; (2) a
follow-up to enable Pages and verify the raw data URL once content is pushed. Re-issue
the Pages/verify prompt after step 1 above if it hasn't run yet.

## Full history

Everything is in git — this file plus the code is a complete, current snapshot. No
credentials, keys, or secrets exist anywhere in the repo or this file (there is no key
yet; when one exists it belongs only in each device's `localStorage`, never here).

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

- `origin` → `https://github.com/spdltd-spdco/travelmap.git` (public repo). Auth is a
  GitHub fine-grained PAT (repo-scoped to `travelmap`, Contents read/write only) stored
  via `git credential approve` in Windows' credential store — pushes are non-interactive
  now. Currently at `9ab7999`.
- `nas` → `\\nasraid\git\TravelMap\TravelMap.git` — a bare repo on the NAS git share
  (same convention as `\\nasraid\git\BetAllaire\BetAllaire.git`), used purely as a dumb
  storage mirror, kept in lockstep with `origin`. No server-side software runs there.
  Push both together:
  ```
  git push origin main
  git push nas main
  ```

## Outstanding, in order

**Done:**
1. ✅ Pushed to GitHub — `origin/main` and `nas/main` both at `9ab7999` (includes the
   `#map` 0-height CSS fix, see below).
2. ✅ GitHub Pages live at `https://spdltd-spdco.github.io/travelmap/`.
3. ✅ Raw data URL confirmed: `.../main/data/japan.geojson` returns 200, a GeoJSON body,
   `access-control-allow-origin: *`.
4. ✅ Billing linked (account `013F7F-82DF1C-D6F8B2`, free trial) to project
   `travelmap-508223`.
5. ✅ Key created — **named "TravelMap"** (not `travelmap-web` as originally planned).
   APIs enabled on it: Maps JavaScript API, Places API (legacy — what the app's search
   code actually calls), Places API (New, for a future migration). Website
   restrictions, as Google's form actually accepts them:
   ```
   http://localhost:8080/*
   http://127.0.0.1:8080/*
   https://spdltd-spdco.github.io/travelmap/*
   ```
   **Important quirk found:** Google's referrer form rejects a wildcard port on
   `http://` (`http://localhost:*/*` → "Invalid website domain") — it has to be the
   exact port, `:8080` for the WSL-python local server used in this project. If a local
   test server ever runs on a different port, add another exact-port entry. Restriction
   edits took a few minutes to propagate; the app auto-clears a rejected key, so re-paste
   after any restriction change.

**Outstanding:**
6. Confirm the key actually works end-to-end (map renders + zooms to the Tokyo sample
   regions) — was mid-verification, blocked on the referrer propagation delay above.
7. Replace the sample dataset: curate real neighborhoods/POIs in `edit.html`, **Export
   japan.geojson**, overwrite `data/japan.geojson`, commit, push (both remotes).
8. Install on phones: Chrome → ⋮ → **Add to Home screen** (WebAPK) is the primary path
   for the owner + one friend. A standalone `.apk` via pwabuilder.com is documented in
   the README as a fallback if a literal installable file is wanted.

## Fixed bugs

- **`#map` rendered 0px tall** (commit `9ab7999`). `google.maps.Map` sets an inline
  `position:relative` on its container, silently beating our plain `#map{position:...}`
  rule (inline always wins over a non-`!important` stylesheet rule) and collapsing
  `inset:0` since a statically-flowed div has no intrinsic height. Fixed with
  `!important` on `position` in both `index.html` (viewer, positioned against the
  viewport — also given an explicit `height:100dvh;width:100%` belt-and-suspenders) and
  `edit.html` (builder, positioned against `<main>`, a sized grid cell — no explicit
  height there, an `100vh` would overflow past the cell).

## Cowork prompts already issued

Three rounds so far, all in the owner's chat history: (1) create the GitHub repo +
Google Cloud project/key; (2) enable Pages + verify the raw data URL once content was
pushed; (3) diagnose the key's referrer restrictions after a `RefererNotAllowedMapError`
on local testing — resolved, see the website-restrictions block above.

## Full history

Everything is in git — this file plus the code is a complete, current snapshot. No
credentials, keys, or secrets exist anywhere in the repo or this file (there is no key
yet; when one exists it belongs only in each device's `localStorage`, never here).

# TravelMap

A personal, online-only map for a trip:

- **`index.html`** — the **viewer**. Shows your fixed neighborhood regions + points of
  interest, and lets you search any hotel / restaurant / bar and see where it sits
  relative to them (which neighborhood it's in, distance to your nearby fixed points,
  one-tap directions). Mobile-first; installs as an app.
- **`edit.html`** — the **builder**. Draw the neighborhoods and drop the fixed POIs,
  then **Export japan.geojson**.
- **`data/japan.geojson`** — the fixed layer. Ships with a small sample Tokyo set.

Plain static HTML + the Google Maps JavaScript API. No build step, no backend.

---

## 1. Google Maps API key

1. [Google Cloud Console → Credentials](https://console.cloud.google.com/google/maps-apis/credentials)
   → create an API key.
2. Enable **Maps JavaScript API** and **Places API** for the project (billing on; the
   free monthly allowances cover personal use many times over).
3. Restrict the key → *Application restrictions* → **Websites**, add:
   - `https://YOUR-USERNAME.github.io/travelmap/*`  (your Pages URL)
   - `http://localhost:PORT/*` and `http://127.0.0.1:PORT/*`  (local testing, exact port —
     Google's form rejects a wildcard port on `http://`, e.g. `http://localhost:*/*` is
     refused as an "Invalid website domain". Use whatever port you actually serve on,
     e.g. `:8080`; add another entry if you ever use a different port.)
   *API restrictions* → **Maps JavaScript API** + **Places API** only (add the legacy
   **Places API** specifically if your project also has **Places API (New)** enabled —
   the app's current search code calls the legacy `Autocomplete`/`PlacesService` classes).
4. Restriction changes can take a few minutes to propagate — if a fresh key is rejected
   right after saving restrictions, wait ~5 minutes and try again. A rejected key is
   auto-cleared by the app, so you'll need to re-paste it.

**The key is never committed.** Leave `HARDCODED_KEY = ""` in `index.html` / `edit.html`.
On first load each page shows a dialog — paste the key once and it's kept in that
browser's `localStorage` (shared between the two pages, since they're one origin). Redo
it any time with the **⚙** button in the viewer's top bar. A bad key is cleared
automatically so you can re-enter it.

Only set `HARDCODED_KEY = "AIza..."` for a private or purely-local build where baking it
in is convenient.

Because the site is a public GitHub Pages URL, the **website restriction** in step 3 is
what actually protects the key — anyone who saw it couldn't use it from another origin.

---

## 2. Point the viewer at the data

In `index.html`:

```js
const DATA_URL = "https://raw.githubusercontent.com/YOUR-USER/YOUR-REPO/main/data/japan.geojson";
```

`raw.githubusercontent.com` sends the right CORS headers, so the viewer fetches the data
**straight from the repo**. Updating the map is then just:

```
edit in edit.html  →  Export japan.geojson  →  replace data/japan.geojson  →  git commit && git push
```

Open the app and pull-to-refresh (or tap **refresh** in the legend). **No redeploy of the
app is needed** — the raw file updates on its own, usually within a minute.

Leave `DATA_URL = ""` to instead load `./data/japan.geojson` from wherever the page is
served (fine if the app and data live in the same repo; costs a ~20 s redeploy per change).

---

## 3. Host the viewer

Any static host. Push this folder to GitHub, then:

**Cloudflare Pages** — dash.cloudflare.com → Workers & Pages → Create → Pages → connect the
repo. Framework preset **None**, build command empty, output dir `/`. Works with a
**private** repo on the free plan. You get `https://<name>.pages.dev`.

**GitHub Pages** — repo Settings → Pages → Deploy from branch → `main` / root. Note: a
*private* repo needs a paid plan; a public repo works on free.

Add the resulting URL to the API key's website restrictions (step 1.3).

---

## 4. Put it on your Android phone

### Easiest — no file, no developer mode

Open the hosted URL in **Chrome** → ⋮ menu → **Add to Home screen** → *Install*.
Chrome builds a real app (WebAPK): own icon, own entry in the app drawer and recents,
full-screen, uninstalls like any app. Do the same on your friend's phone. This is all you
actually need for two people.

### If you want an actual `.apk` file

1. Deploy the site (step 3) so it has an HTTPS URL.
2. Go to **[pwabuilder.com](https://www.pwabuilder.com)**, enter the URL, choose
   **Android** → **Generate**. It produces a signed `app-release-signed.apk` (plus an
   `.aab` and a `assetlinks.json`).
3. Copy the APK to the phone, tap it. Android asks to allow installs from that source
   (Chrome / Files) — allow it. **Developer mode / USB debugging is not required**; that's
   only for `adb install` from a PC.
4. One APK installs on any device — send the same file to your friend.
5. *(Optional)* host the generated `assetlinks.json` at
   `/.well-known/assetlinks.json` on the site so the app launches with no address bar.

The APK is a thin shell around the live URL, so app/data updates never need a rebuild —
you'd only regenerate it if you change the app's name, icon, or URL.

### Using Firefox or Brave on Android instead of Chrome

The site itself works the same in any of the three — Maps JS, geolocation, and the
regions menu are plain web APIs, nothing Chrome-specific. Two real differences:

- **"Add to Home screen"**: Brave is Chromium-based, so it installs the same WebAPK as
  Chrome (own icon, standalone, no address bar). **Firefox for Android does not** build a
  standalone app from a PWA — its "Add to Home screen" makes a bookmark shortcut that
  still opens inside Firefox's UI. Everything still works, it just won't be full-screen.
  If you want the WebAPK experience, use Chrome or Brave for the install step (you can
  still browse day-to-day in Firefox).
- **Content blocking**: if the map ever fails to load only in one of these browsers,
  check its shield/tracking-protection settings for the site — Brave's aggressive
  Shields or Firefox's strict Enhanced Tracking Protection can occasionally over-block
  Google subdomains. Lowering protection for this one site (not globally) fixes it.

---

## Local testing

Referrer restrictions don't apply to `file://`, and the builder's **Load current** button
needs `fetch`, so serve the folder:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080/` (viewer) or `http://localhost:8080/edit.html` (builder).
Temporarily set the key's *Application restrictions* to **None** if `localhost` isn't
whitelisted yet.

---

## Data format

`data/japan.geojson` is a normal GeoJSON `FeatureCollection` with an extra top-level
`updated` timestamp (shown in the viewer's legend).

- **Neighborhoods** — `Polygon` / `MultiPolygon` features. `properties`: `name`, `color`,
  `notes`.
- **POIs** — `Point` features. `properties`: `name`, `category`
  (`hotel` · `restaurant` · `bar` · `sight` · `transit` · `other`), `notes`.

Anything else the builder exports (rectangles, circles, paths) still renders as polygons /
lines but isn't used by the relationship panel.

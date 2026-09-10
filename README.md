# Interactive Map Builder

A single-page tool for drawing regions/boundaries and dropping points-of-interest markers
on Google Maps. Draw polygons, rectangles, circles and paths; rename/colour/annotate each
feature in the sidebar; everything auto-saves to the browser and exports/imports as GeoJSON.

Pure static HTML + the Google Maps JavaScript API. No build step, no backend.

---

## 1. Get a Google Maps API key

1. In the [Google Cloud Console → Credentials](https://console.cloud.google.com/google/maps-apis/credentials),
   create an API key.
2. Enable **Maps JavaScript API** and **Places API** for the project. Billing must be
   enabled (there is a large free monthly tier; this tool's usage is tiny).
3. **Restrict the key** (Credentials → your key → *Application restrictions*):
   - *Website restrictions* → add the URL the site will be served from, e.g.
     - `https://YOUR-USERNAME.github.io/*`
     - `http://localhost:*/*` (for local testing via a dev server)
   - *API restrictions* → limit to **Maps JavaScript API** + **Places API**.

   A Maps JS key is always visible in page source — the website restriction is what makes
   a leaked key useless anywhere else, so don't skip it.

## 2. Add the key to the page

Open `index.html`, find this line near the top of the `<script>` block, and paste your key:

```js
const HARDCODED_KEY = "AIza...your-key...";
```

Leave it as `""` instead if you'd rather the page prompt each visitor for a key and
remember it in their browser (nothing committed to the repo).

---

## 3. Host it

### Option A — GitHub Pages

> Serving Pages from a **private** repo requires a paid plan (Pro / Team / Enterprise).
> On a free account the repo must be public — in which case leave `HARDCODED_KEY = ""`
> and rely on the prompt, or accept that the restricted key is exposed. If you need a
> private repo on a free plan, use Option B.

```bash
# from this folder, after committing your key change
git remote add origin https://github.com/YOUR-USERNAME/interactive-map.git
git push -u origin main
```

Then in the repo on github.com: **Settings → Pages → Build and deployment**
→ Source: *Deploy from a branch* → Branch: `main` / `/ (root)` → **Save**.
The URL appears there after ~1 minute: `https://YOUR-USERNAME.github.io/interactive-map/`.

Add that exact URL to the key's website restrictions (step 1.3).

### Option B — Cloudflare Pages (free, works with a private repo)

1. Push this folder to a private GitHub repo (the two `git` commands above).
2. [Cloudflare dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → *Create* →
   **Pages** → *Connect to Git* → pick the repo.
3. Framework preset: **None**. Build command: *(empty)*. Output directory: `/`.
4. Deploy. You get `https://interactive-map-xxx.pages.dev/` — add it to the key
   restrictions. (Cloudflare Access can put a login in front of it if you want the site
   itself private, not just the repo.)

Netlify and Vercel work the same way (no build command, publish directory `/`).

---

## Local testing

Referrer restrictions don't apply to `file://`, so either:

- temporarily set the key's *Application restrictions* to **None**, then open `index.html`
  directly, **or**
- serve the folder and use the `localhost` restriction:

```bash
python -m http.server 8080
# open http://localhost:8080
```

## Data

Features + map view persist in `localStorage` per browser. Use **Export GeoJSON** to save a
portable copy; **Import** merges a GeoJSON file back in. Circles round-trip as 64-point
polygons that carry their `radius`/`center` so re-importing restores a real circle.

#!/usr/bin/env python3
"""
Generate natural-looking neighborhood polygon overlays for TravelMap.

These are illustrative "the area people mean when they say Shibuya" shapes, not
surveyed or administrative boundaries — actual ward boundaries are too large for
trip use, and most named tourist neighborhoods don't have an official polygon at
all. Each region is a deterministic irregular blob around a center point + radius,
so re-running this script without changing tools/regions.json reproduces the exact
same shape.

Reads:  tools/regions.json   — name, center [lat,lng], radius_m, color, blurb, notes
Writes: data/japan.geojson   — replaces Polygon features matching a region's name
                                by name, leaves Point features (POIs) and any other
                                polygons untouched, bumps "updated".

Usage:
    python3 tools/gen_regions.py
"""
import json
import math
import random
import hashlib
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "tools" / "regions.json"
DATA_FILE = ROOT / "data" / "japan.geojson"

VERTICES = 14        # points around the generated ring
JITTER = 0.30         # max fractional +/- radius noise before smoothing
SMOOTH_PASSES = 2    # neighbor-averaging passes so it reads as a blob, not a starburst


def seeded_rng(name):
    """Deterministic per-region RNG so re-running the script is stable."""
    h = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return random.Random(int(h[:16], 16))


def meters_to_latlng_offset(lat0, dx_m, dy_m):
    dlat = dy_m / 111_320.0
    dlng = dx_m / (111_320.0 * math.cos(math.radians(lat0)))
    return dlat, dlng


def make_blob(center, radius_m, name):
    lat0, lng0 = center
    rng = seeded_rng(name)
    radii = [radius_m * (1 + rng.uniform(-JITTER, JITTER)) for _ in range(VERTICES)]
    for _ in range(SMOOTH_PASSES):
        radii = [
            (radii[i - 1] + radii[i] + radii[(i + 1) % VERTICES]) / 3
            for i in range(VERTICES)
        ]
    ring = []
    for i in range(VERTICES):
        theta = 2 * math.pi * i / VERTICES
        r = radii[i]
        dx, dy = r * math.cos(theta), r * math.sin(theta)
        dlat, dlng = meters_to_latlng_offset(lat0, dx, dy)
        ring.append([round(lng0 + dlng, 6), round(lat0 + dlat, 6)])
    ring.append(ring[0])  # close the ring
    return ring


def build_feature(region):
    ring = make_blob(region["center"], region["radius_m"], region["name"])
    return {
        "type": "Feature",
        "properties": {
            "kind": "polygon",
            "name": region["name"],
            "color": region.get("color", "#2b6cff"),
            "blurb": region.get("blurb", ""),
            "notes": region.get("notes", ""),
        },
        "geometry": {"type": "Polygon", "coordinates": [ring]},
    }


def is_named_polygon(feature):
    return feature.get("geometry", {}).get("type") == "Polygon"


def main():
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))["regions"]
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    existing = data.get("features", [])

    generated = {r["name"]: build_feature(r) for r in regions}
    existing_polygon_names = {
        f["properties"].get("name") for f in existing if is_named_polygon(f)
    }

    kept = [
        f
        for f in existing
        if not (is_named_polygon(f) and f["properties"].get("name") in generated)
    ]

    data["features"] = kept + list(generated.values())
    data["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    DATA_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Wrote {len(generated)} region polygon(s) to {DATA_FILE.relative_to(ROOT)}:")
    for name in generated:
        tag = "updated" if name in existing_polygon_names else "added"
        print(f"  [{tag}] {name}")

    leftover = [f for f in kept if is_named_polygon(f)]
    if leftover:
        print("Existing polygon(s) not in regions.json, left untouched:")
        for f in leftover:
            print(f"  - {f['properties'].get('name')}")

    poi_count = sum(1 for f in kept if f.get("geometry", {}).get("type") == "Point")
    print(f"POI point features preserved: {poi_count}")


if __name__ == "__main__":
    main()

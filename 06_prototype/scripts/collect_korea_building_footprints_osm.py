#!/usr/bin/env python3
"""Collect public OSM building footprints for the Korea civil infra COP demo.

The output is safe for the public demo because it contains public building
footprints and non-PII tags only. It does not collect residents, ownership,
unit-level apartment data, contact details, or access-control information.
"""

from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
DATA_ROOT = PROJECT_ROOT / "03_data/korea_civil_infra_cop"
APP_DATA_ROOT = PROJECT_ROOT / "06_prototype/app/korea_civil_infra_cop/data"

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]

FOCUS_AOIS = [
    {"id": "seoul_cbd", "label": "Seoul CBD", "bbox": (37.550, 126.960, 37.590, 127.020), "limit": 800},
    {"id": "yeouido_mapo", "label": "Yeouido/Mapo", "bbox": (37.515, 126.880, 37.560, 126.960), "limit": 700},
    {"id": "gangnam_seocho", "label": "Gangnam/Seocho", "bbox": (37.480, 127.000, 37.530, 127.080), "limit": 800},
    {"id": "songpa_jamsil", "label": "Songpa/Jamsil", "bbox": (37.500, 127.070, 37.545, 127.140), "limit": 700},
    {"id": "guro_geumcheon", "label": "Guro/Geumcheon", "bbox": (37.460, 126.860, 37.510, 126.930), "limit": 650},
    {"id": "northeast_seoul", "label": "North-east Seoul", "bbox": (37.580, 127.020, 37.650, 127.110), "limit": 750},
]

MAX_FEATURES = 3200


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def overpass_query(bbox: tuple[float, float, float, float], limit: int) -> str:
    south, west, north, east = bbox
    return f"""
[out:json][timeout:40];
(
  way["building"]({south},{west},{north},{east});
);
out tags geom {limit};
"""


def fetch_overpass(query: str) -> dict[str, Any]:
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_error: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": "D4D-Civil-Infra-COP/0.1 public-demo building-footprints",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:
            last_error = error
            time.sleep(1.5)
    raise RuntimeError(f"Overpass request failed: {last_error}")


def classify_building(tags: dict[str, str]) -> str:
    building = tags.get("building", "").lower()
    amenity = tags.get("amenity", "").lower()
    shop = tags.get("shop", "").lower()
    office = tags.get("office", "").lower()

    if building in {"apartments", "residential", "dormitory", "house", "terrace"}:
        return "residential"
    if building in {"commercial", "retail", "office"} or shop or office:
        return "commercial"
    if building in {"industrial", "warehouse", "factory"}:
        return "industrial"
    if building in {"hospital", "school", "university", "public", "civic"} or amenity in {"hospital", "school", "university", "college"}:
        return "public_or_civic"
    return "other_building"


def polygon_area_m2(coords: list[list[float]]) -> float:
    if len(coords) < 4:
        return 0.0
    mean_lat = sum(lat for _, lat in coords) / len(coords)
    meters_per_lon = 111_320 * math.cos(math.radians(mean_lat))
    meters_per_lat = 110_540
    projected = [(lon * meters_per_lon, lat * meters_per_lat) for lon, lat in coords]
    area = 0.0
    for index, (x1, y1) in enumerate(projected):
        x2, y2 = projected[(index + 1) % len(projected)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def centroid(coords: list[list[float]]) -> tuple[float, float]:
    if not coords:
        return 0.0, 0.0
    return (
        sum(point[0] for point in coords) / len(coords),
        sum(point[1] for point in coords) / len(coords),
    )


def feature_from_way(element: dict[str, Any], aoi: dict[str, Any]) -> dict[str, Any] | None:
    geometry = element.get("geometry") or []
    if len(geometry) < 4:
        return None
    coords = [[float(point["lon"]), float(point["lat"])] for point in geometry if "lon" in point and "lat" in point]
    if len(coords) < 4:
        return None
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    tags = {str(key): str(value) for key, value in (element.get("tags") or {}).items()}
    osm_id = str(element.get("id"))
    center_lon, center_lat = centroid(coords[:-1])
    area = polygon_area_m2(coords)
    building_value = tags.get("building", "yes")
    building_class = classify_building(tags)
    name = tags.get("name") or tags.get("addr:housename") or f"OSM building {osm_id}"

    return {
        "type": "Feature",
        "id": f"osm_way_{osm_id}",
        "properties": {
            "id": f"osm_way_{osm_id}",
            "osm_type": "way",
            "osm_id": osm_id,
            "name": name,
            "building": building_value,
            "building_class": building_class,
            "levels": tags.get("building:levels"),
            "area_m2_est": round(area, 1),
            "centroid_lat": round(center_lat, 7),
            "centroid_lon": round(center_lon, 7),
            "source": "OpenStreetMap Overpass API",
            "source_mode": "public_exact_building_footprint",
            "aoi": aoi["id"],
            "aoi_label": aoi["label"],
            "safe_use": "civilian exposure, evacuation/deconfliction, and response planning only; no PII or unit-level resident data",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords],
        },
    }


def collect() -> dict[str, Any]:
    seen_ids: set[str] = set()
    features: list[dict[str, Any]] = []
    aoi_stats: list[dict[str, Any]] = []

    for aoi in FOCUS_AOIS:
        query = overpass_query(aoi["bbox"], int(aoi["limit"]))
        payload = fetch_overpass(query)
        accepted = 0
        for element in payload.get("elements", []):
            if element.get("type") != "way":
                continue
            unique = f"way/{element.get('id')}"
            if unique in seen_ids:
                continue
            feature = feature_from_way(element, aoi)
            if not feature:
                continue
            seen_ids.add(unique)
            features.append(feature)
            accepted += 1
            if len(features) >= MAX_FEATURES:
                break
        aoi_stats.append({
            "aoi": aoi["id"],
            "label": aoi["label"],
            "bbox": aoi["bbox"],
            "accepted_features": accepted,
        })
        if len(features) >= MAX_FEATURES:
            break
        time.sleep(1.0)

    by_class: dict[str, int] = {}
    for feature in features:
        key = feature["properties"]["building_class"]
        by_class[key] = by_class.get(key, 0) + 1

    return {
        "type": "FeatureCollection",
        "schema": "korea_civil_infra_building_footprints_osm.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "name": "OpenStreetMap Overpass API",
            "url": "https://overpass-api.de/",
            "license": "Open Database License (ODbL)",
            "note": "Public building footprints only. No PII, ownership, resident, contact, access-control, or protected-facility attributes are collected.",
        },
        "collection_policy": {
            "precision": "public exact building footprint",
            "public_demo_rule": "Display for civilian exposure and deconfliction only.",
            "sensitive_exclusions": [
                "resident/unit-level apartment data",
                "ownership records",
                "contact details",
                "access-control information",
                "military or protected-facility enrichment",
            ],
        },
        "aoi_stats": aoi_stats,
        "class_counts": by_class,
        "features": features,
    }


def main() -> int:
    collection = collect()
    write_json(DATA_ROOT / "building_footprints_osm.geojson", collection)
    write_json(DATA_ROOT / "metadata/building_footprints_osm_summary.json", {
        "generated_at": collection["generated_at"],
        "feature_count": len(collection["features"]),
        "class_counts": collection["class_counts"],
        "aoi_stats": collection["aoi_stats"],
        "source": collection["source"],
        "collection_policy": collection["collection_policy"],
    })

    APP_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(APP_DATA_ROOT / "building_footprints_osm.geojson", collection)
    js_payload = "window.KOREA_BUILDING_FOOTPRINTS = "
    js_payload += json.dumps(collection, ensure_ascii=False, indent=2)
    js_payload += ";\n"
    (APP_DATA_ROOT / "building_footprints_osm.js").write_text(js_payload, encoding="utf-8")

    print(json.dumps({
        "feature_count": len(collection["features"]),
        "class_counts": collection["class_counts"],
        "geojson": str(DATA_ROOT / "building_footprints_osm.geojson"),
        "app_js": str(APP_DATA_ROOT / "building_footprints_osm.js"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

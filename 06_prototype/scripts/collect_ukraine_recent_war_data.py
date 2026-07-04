#!/usr/bin/env python3
"""Collect public Russia-Ukraine war OSINT datasets for D4D scenario building.

The collector intentionally avoids raw social-media media, faces, account-level
PII, and live tactical targeting outputs. It stores source data, filtered tables,
and a manifest that records both successful and blocked sources.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
DATA_ROOT = PROJECT_ROOT / "03_data" / "ukraine_recent_war_osint"
RAW = DATA_ROOT / "raw"
PROCESSED = DATA_ROOT / "processed"
METADATA = DATA_ROOT / "metadata"

START_DATE = dt.date(2025, 12, 1)
END_DATE = dt.date(2026, 7, 4)

USER_AGENT = "d4d-codex-osint-research/0.2 (+non-commercial hackathon research)"

csv.field_size_limit(sys.maxsize)


GDELT_EVENT_FIELDS = [
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_ADM2Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL",
]


AOIS = [
    {"id": "kyiv", "label": "Kyiv", "bbox": (50.20, 30.10, 50.70, 30.90), "lat": 50.4501, "lon": 30.5234},
    {"id": "kharkiv", "label": "Kharkiv", "bbox": (49.75, 35.85, 50.20, 36.65), "lat": 49.9935, "lon": 36.2304},
    {"id": "odesa", "label": "Odesa", "bbox": (46.25, 30.45, 46.70, 30.95), "lat": 46.4825, "lon": 30.7233},
    {"id": "dnipro", "label": "Dnipro", "bbox": (48.20, 34.60, 48.75, 35.40), "lat": 48.4647, "lon": 35.0462},
    {"id": "zaporizhzhia", "label": "Zaporizhzhia", "bbox": (47.60, 34.80, 48.15, 35.55), "lat": 47.8388, "lon": 35.1396},
    {"id": "lviv", "label": "Lviv", "bbox": (49.55, 23.70, 50.10, 24.30), "lat": 49.8397, "lon": 24.0297},
    {"id": "kramatorsk", "label": "Kramatorsk / Donetsk North", "bbox": (48.35, 37.20, 49.20, 38.45), "lat": 48.7389, "lon": 37.5844},
]


GDELT_DOC_QUERIES = [
    "Ukrzaliznytsia",
    '"Ukraine" "railway" "attack"',
    '"Ukraine" "energy infrastructure"',
    '"Ukraine" "power grid"',
    '"Ukraine" "Shahed"',
    '"Ukraine" "missile" "drone"',
    '"Odesa" "port" "drone"',
    '"Black Sea" "Ukraine" "shipping"',
]


def ensure_dirs() -> None:
    for directory in [
        RAW,
        PROCESSED,
        METADATA,
        RAW / "petro_ivaniuk",
        RAW / "missile_attacks_github",
        RAW / "ucdp",
        RAW / "gdelt_events",
        RAW / "gdelt_doc",
        RAW / "osm_overpass",
        RAW / "warspotting",
        RAW / "oryx",
        RAW / "isw",
        RAW / "open_meteo",
        RAW / "blocked_or_key_required",
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def request_bytes(
    url: str,
    *,
    data: Optional[bytes] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 60,
    retries: int = 2,
    sleep_seconds: float = 1.0,
) -> Tuple[Optional[bytes], Dict[str, object]]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        request_headers.update(headers)
    last_error = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=request_headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                blob = response.read()
                return blob, {
                    "url": url,
                    "status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": response.headers.get("Content-Length"),
                    "sha256": sha256_bytes(blob),
                    "fetched_at": now_iso(),
                    "attempt": attempt + 1,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read(500).decode("utf-8", "replace") if exc.fp else ""
            last_error = {"type": "HTTPError", "code": exc.code, "reason": exc.reason, "body": body}
            if exc.code in {403, 404, 406}:
                break
            time.sleep(sleep_seconds * (attempt + 1))
        except Exception as exc:  # noqa: BLE001 - manifest should capture source failures.
            last_error = {"type": type(exc).__name__, "message": str(exc)}
            time.sleep(sleep_seconds * (attempt + 1))
    return None, {"url": url, "error": last_error, "fetched_at": now_iso()}


def write_bytes(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()[:80] or "query"


def parse_date(value: str) -> Optional[dt.date]:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y%m%d"):
        try:
            return dt.datetime.strptime(value[: len(fmt)], fmt).date()
        except ValueError:
            pass
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def in_recent_window(value: str) -> bool:
    date = parse_date(value)
    return bool(date and START_DATE <= date <= END_DATE)


def collect_petro_ivaniuk(manifest: List[Dict[str, object]]) -> None:
    files = [
        "README.md",
        "LICENSE",
        "data/russia_losses_equipment.json",
        "data/russia_losses_equipment_correction.json",
        "data/russia_losses_equipment_oryx.json",
        "data/russia_losses_personnel.json",
    ]
    base = "https://raw.githubusercontent.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset/main/"
    source_entries = []
    for file_name in files:
        url = base + file_name
        out = RAW / "petro_ivaniuk" / file_name.replace("/", "__")
        if out.exists():
            manifest.append({"source": "petro_ivaniuk_github", "file": file_name, "local_path": str(out), "status": "cached"})
            continue
        blob, meta = request_bytes(url)
        meta.update({"source": "petro_ivaniuk_github", "file": file_name})
        if blob:
            write_bytes(out, blob)
            meta["local_path"] = str(out)
            source_entries.append(meta)
        manifest.append(meta)
        time.sleep(0.3)

    equipment_path = RAW / "petro_ivaniuk" / "data__russia_losses_equipment.json"
    personnel_path = RAW / "petro_ivaniuk" / "data__russia_losses_personnel.json"
    if equipment_path.exists():
        equipment = json.loads(equipment_path.read_text(encoding="utf-8"))
        recent = [row for row in equipment if in_recent_window(str(row.get("date", "")))]
        fields = sorted({key for row in recent for key in row.keys()})
        count = write_csv(PROCESSED / "petro_russian_equipment_losses_recent.csv", recent, fields)
        manifest.append({"source": "petro_ivaniuk_github", "processed": "equipment_recent", "rows": count})
    if personnel_path.exists():
        personnel = json.loads(personnel_path.read_text(encoding="utf-8"))
        recent = [row for row in personnel if in_recent_window(str(row.get("date", "")))]
        fields = sorted({key for row in recent for key in row.keys()})
        count = write_csv(PROCESSED / "petro_russian_personnel_losses_recent.csv", recent, fields)
        manifest.append({"source": "petro_ivaniuk_github", "processed": "personnel_recent", "rows": count})
    write_json(RAW / "petro_ivaniuk" / "download_manifest.json", source_entries)


def collect_missile_attack_csvs(manifest: List[Dict[str, object]]) -> None:
    files = [
        "README.md",
        "missile_attacks_daily.csv",
        "missiles_and_uavs.csv",
    ]
    base = "https://raw.githubusercontent.com/DTL-DA/Massive-Missile-Attacks-on-Ukraine-EndtoEnd/main/"
    for file_name in files:
        url = base + file_name
        out = RAW / "missile_attacks_github" / file_name
        if out.exists():
            manifest.append({"source": "massive_missile_attacks_github", "file": file_name, "local_path": str(out), "status": "cached"})
            continue
        blob, meta = request_bytes(url)
        meta.update({"source": "massive_missile_attacks_github", "file": file_name})
        if blob:
            write_bytes(out, blob)
            meta["local_path"] = str(out)
        manifest.append(meta)
        time.sleep(0.3)

    attacks_path = RAW / "missile_attacks_github" / "missile_attacks_daily.csv"
    if not attacks_path.exists():
        return
    rows = []
    with attacks_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if in_recent_window(row.get("time_start", "")):
                rows.append(row)
    count = write_csv(PROCESSED / "missile_uav_attacks_recent.csv", rows, list(rows[0].keys()) if rows else [])
    daily: Dict[str, Dict[str, object]] = {}
    for row in rows:
        date = str(parse_date(row.get("time_start", "")) or "")
        if not date:
            continue
        bucket = daily.setdefault(
            date,
            {
                "date": date,
                "rows": 0,
                "launched_total": 0.0,
                "destroyed_total": 0.0,
                "shahed_reported_total": 0.0,
                "sources": set(),
            },
        )
        bucket["rows"] = int(bucket["rows"]) + 1
        for src, dst in [("launched", "launched_total"), ("destroyed", "destroyed_total"), ("is_shahed", "shahed_reported_total")]:
            try:
                bucket[dst] = float(bucket[dst]) + float(row.get(src) or 0)
            except ValueError:
                pass
        source = row.get("source")
        if source:
            bucket["sources"].add(source)
    daily_rows = []
    for item in sorted(daily.values(), key=lambda x: x["date"]):
        item = dict(item)
        item["sources"] = ";".join(sorted(item["sources"]))
        daily_rows.append(item)
    daily_fields = ["date", "rows", "launched_total", "destroyed_total", "shahed_reported_total", "sources"]
    daily_count = write_csv(PROCESSED / "missile_uav_daily_summary_recent.csv", daily_rows, daily_fields)
    manifest.append({"source": "massive_missile_attacks_github", "processed": "recent_attack_rows", "rows": count})
    manifest.append({"source": "massive_missile_attacks_github", "processed": "daily_summary", "rows": daily_count})


def collect_ucdp(manifest: List[Dict[str, object]], *, include_stable_ged: bool = True) -> None:
    downloads = [
        {
            "id": "candidate_ged_26_0_5",
            "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_5.csv",
            "path": RAW / "ucdp" / "GEDEvent_v26_0_5.csv",
        },
    ]
    if include_stable_ged:
        downloads.append(
            {
                "id": "stable_ged_26_1_csv_zip",
                "url": "https://ucdp.uu.se/downloads/ged/ged261-csv.zip",
                "path": RAW / "ucdp" / "ged261-csv.zip",
            }
        )
    for item in downloads:
        if item["path"].exists():
            manifest.append({"source": "ucdp", "dataset": item["id"], "local_path": str(item["path"]), "status": "cached"})
            continue
        blob, meta = request_bytes(item["url"], timeout=120, retries=1)
        meta.update({"source": "ucdp", "dataset": item["id"]})
        if blob:
            write_bytes(item["path"], blob)
            meta["local_path"] = str(item["path"])
        manifest.append(meta)
        time.sleep(0.5)

    candidate_path = RAW / "ucdp" / "GEDEvent_v26_0_5.csv"
    if candidate_path.exists():
        rows, fields = filter_csv_rows(candidate_path, lambda row: row_mentions_ukraine(row))
        count = write_csv(PROCESSED / "ucdp_candidate_ged_ukraine_filtered.csv", rows, fields)
        manifest.append({"source": "ucdp", "processed": "candidate_ukraine_filtered", "rows": count})

    stable_zip = RAW / "ucdp" / "ged261-csv.zip"
    if stable_zip.exists():
        try:
            with zipfile.ZipFile(stable_zip) as zf:
                csv_name = next((name for name in zf.namelist() if name.lower().endswith(".csv")), None)
                if csv_name:
                    text = zf.read(csv_name).decode("utf-8", "replace")
                    reader = csv.DictReader(io.StringIO(text))
                    rows = [row for row in reader if row_mentions_ukraine(row) and int(row.get("year") or 0) >= 2022]
                    fields = reader.fieldnames or sorted({key for row in rows for key in row.keys()})
                    count = write_csv(PROCESSED / "ucdp_stable_ged_ukraine_2022plus_filtered.csv", rows, fields)
                    manifest.append({"source": "ucdp", "processed": "stable_ged_ukraine_2022plus", "rows": count})
        except Exception as exc:  # noqa: BLE001
            manifest.append({"source": "ucdp", "processed": "stable_ged_filter", "error": str(exc)})


def row_mentions_ukraine(row: Dict[str, str]) -> bool:
    text = " ".join(str(value) for value in row.values() if value)
    return bool(re.search(r"\bUkraine\b|\bUkrainian\b|\bRussia-Ukraine\b", text, re.I))


def filter_csv_rows(path: Path, predicate) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if predicate(row)]
        return rows, reader.fieldnames or []


def collect_gdelt_doc(manifest: List[Dict[str, object]]) -> None:
    if os.environ.get("D4D_SKIP_GDELT_DOC") == "1":
        manifest.append({"source": "gdelt_doc_api", "status": "skipped_by_env"})
        return
    all_articles: Dict[str, Dict[str, object]] = {}
    for query in GDELT_DOC_QUERIES:
        slug = safe_slug(query)
        path = RAW / "gdelt_doc" / f"{slug}.json"
        if path.exists():
            parsed = add_gdelt_doc_articles(path.read_bytes(), query, all_articles)
            manifest.append(
                {
                    "source": "gdelt_doc_api",
                    "query": query,
                    "local_path": str(path),
                    "status": "cached",
                    "articles": parsed,
                }
            )
            continue
        params = urllib.parse.urlencode(
            {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": os.environ.get("D4D_GDELT_DOC_MAXRECORDS", "50"),
                "timespan": "6m",
            }
        )
        url = "http://api.gdeltproject.org/api/v2/doc/doc?" + params
        blob, meta = request_bytes(
            url,
            timeout=int(os.environ.get("D4D_GDELT_DOC_TIMEOUT", "25")),
            retries=int(os.environ.get("D4D_GDELT_DOC_RETRIES", "0")),
            sleep_seconds=2.0,
        )
        meta.update({"source": "gdelt_doc_api", "query": query})
        if blob:
            write_bytes(path, blob)
            meta["local_path"] = str(path)
            parsed = add_gdelt_doc_articles(blob, query, all_articles)
            meta["articles"] = parsed
        manifest.append(meta)
        time.sleep(4.0)

    rows = sorted(all_articles.values(), key=lambda x: str(x.get("seendate", "")), reverse=True)
    fields = ["query", "seendate", "title", "domain", "language", "sourcecountry", "url", "url_mobile", "socialimage"]
    count = write_csv(PROCESSED / "gdelt_doc_ukraine_scenario_articles.csv", rows, fields)
    manifest.append({"source": "gdelt_doc_api", "processed": "deduped_articles", "rows": count})


def add_gdelt_doc_articles(blob: bytes, query: str, all_articles: Dict[str, Dict[str, object]]) -> int:
    try:
        data = json.loads(blob.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return 0
    articles = data.get("articles", [])
    for article in articles:
        url_key = article.get("url")
        if not url_key:
            continue
        article = dict(article)
        article["query"] = query
        all_articles[url_key] = article
    return len(articles)


def collect_gdelt_event_exports(manifest: List[Dict[str, object]], *, hours: int = 24) -> None:
    lastupdate_url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
    blob, meta = request_bytes(lastupdate_url, timeout=30, retries=1)
    meta.update({"source": "gdelt_v2_event_export", "file": "lastupdate.txt"})
    if not blob:
        manifest.append(meta)
        return
    write_bytes(RAW / "gdelt_events" / "lastupdate.txt", blob)
    manifest.append(meta)
    text = blob.decode("utf-8", "replace")
    match = re.search(r"gdeltv2/(\d{14})\.export\.CSV\.zip", text)
    if not match:
        manifest.append({"source": "gdelt_v2_event_export", "error": "could not parse latest timestamp"})
        return
    latest = dt.datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
    intervals = int(hours * 4)
    rows: List[List[str]] = []
    url_count = 0
    for idx in range(intervals):
        stamp = latest - dt.timedelta(minutes=15 * idx)
        ts = stamp.strftime("%Y%m%d%H%M%S")
        url = f"http://data.gdeltproject.org/gdeltv2/{ts}.export.CSV.zip"
        blob, file_meta = request_bytes(url, timeout=60, retries=0)
        file_meta.update({"source": "gdelt_v2_event_export", "timestamp": ts})
        if not blob:
            manifest.append(file_meta)
            continue
        zip_path = RAW / "gdelt_events" / f"{ts}.export.CSV.zip"
        write_bytes(zip_path, blob)
        file_meta["local_path"] = str(zip_path)
        manifest.append(file_meta)
        url_count += 1
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                name = zf.namelist()[0]
                for raw_line in zf.read(name).decode("utf-8", "replace").splitlines():
                    if re.search(r"\bUKR\b|Ukraine|Ukrain", raw_line, re.I):
                        parts = raw_line.split("\t")
                        if len(parts) < len(GDELT_EVENT_FIELDS):
                            parts += [""] * (len(GDELT_EVENT_FIELDS) - len(parts))
                        rows.append(parts[: len(GDELT_EVENT_FIELDS)])
        except Exception as exc:  # noqa: BLE001
            manifest.append({"source": "gdelt_v2_event_export", "timestamp": ts, "parse_error": str(exc)})
        time.sleep(0.1)
    dict_rows = [dict(zip(GDELT_EVENT_FIELDS, row)) for row in rows]
    count = write_csv(PROCESSED / "gdelt_event_export_ukraine_filtered_recent.csv", dict_rows, GDELT_EVENT_FIELDS)
    manifest.append(
        {
            "source": "gdelt_v2_event_export",
            "processed": "ukraine_filtered_events",
            "downloaded_export_files": url_count,
            "rows": count,
            "hours": hours,
        }
    )


def collect_osm_overpass(manifest: List[Dict[str, object]]) -> None:
    all_rows: List[Dict[str, object]] = []
    for aoi in AOIS:
        south, west, north, east = aoi["bbox"]
        query = f"""[out:json][timeout:60];
(
  nwr["railway"~"station|halt|yard"]({south},{west},{north},{east});
  nwr["power"~"substation|plant|generator"]({south},{west},{north},{east});
  nwr["amenity"="hospital"]({south},{west},{north},{east});
  nwr["bridge"="yes"]({south},{west},{north},{east});
  nwr["harbour"]({south},{west},{north},{east});
  nwr["industrial"="port"]({south},{west},{north},{east});
  nwr["seamark:type"~"harbour|anchorage"]({south},{west},{north},{east});
);
out center tags 500;"""
        data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        blob, meta = request_bytes(
            "https://overpass-api.de/api/interpreter",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=90,
            retries=1,
            sleep_seconds=3.0,
        )
        meta.update({"source": "openstreetmap_overpass", "aoi": aoi["id"], "label": aoi["label"]})
        if blob:
            path = RAW / "osm_overpass" / f"{aoi['id']}_critical_infrastructure.json"
            write_bytes(path, blob)
            meta["local_path"] = str(path)
            try:
                data_json = json.loads(blob.decode("utf-8", "replace"))
                elements = data_json.get("elements", [])
                meta["elements"] = len(elements)
                for element in elements:
                    tags = element.get("tags", {})
                    center = element.get("center", {})
                    lat = element.get("lat", center.get("lat"))
                    lon = element.get("lon", center.get("lon"))
                    all_rows.append(
                        {
                            "aoi": aoi["id"],
                            "aoi_label": aoi["label"],
                            "osm_type": element.get("type"),
                            "osm_id": element.get("id"),
                            "lat": lat,
                            "lon": lon,
                            "name": tags.get("name") or tags.get("name:en") or tags.get("name:uk"),
                            "railway": tags.get("railway"),
                            "power": tags.get("power"),
                            "amenity": tags.get("amenity"),
                            "bridge": tags.get("bridge"),
                            "harbour": tags.get("harbour"),
                            "industrial": tags.get("industrial"),
                            "operator": tags.get("operator"),
                            "source": "OpenStreetMap Overpass",
                        }
                    )
            except json.JSONDecodeError as exc:
                meta["parse_error"] = str(exc)
        manifest.append(meta)
        time.sleep(4.0)
    fields = [
        "aoi",
        "aoi_label",
        "osm_type",
        "osm_id",
        "lat",
        "lon",
        "name",
        "railway",
        "power",
        "amenity",
        "bridge",
        "harbour",
        "industrial",
        "operator",
        "source",
    ]
    count = write_csv(PROCESSED / "osm_ukraine_aoi_critical_infrastructure.csv", all_rows, fields)
    manifest.append({"source": "openstreetmap_overpass", "processed": "critical_infrastructure", "rows": count})


def collect_warspotting(manifest: List[Dict[str, object]]) -> None:
    combined_rows: List[Dict[str, object]] = []
    for side in ["russia", "unknown"]:
        url = f"https://ukr.warspotting.net/api/losses/{side}"
        blob, meta = request_bytes(url, timeout=30, retries=1, sleep_seconds=10.0)
        meta.update({"source": "warspotting", "side": side})
        if blob:
            path = RAW / "warspotting" / f"latest_losses_{side}.json"
            write_bytes(path, blob)
            meta["local_path"] = str(path)
            try:
                data = json.loads(blob.decode("utf-8", "replace"))
                losses = data.get("losses", [])
                meta["losses"] = len(losses)
                for loss in losses:
                    row = dict(loss)
                    row["api_side"] = side
                    combined_rows.append(row)
            except json.JSONDecodeError as exc:
                meta["parse_error"] = str(exc)
        manifest.append(meta)
        time.sleep(12.0)
    if combined_rows:
        fields = sorted({key for row in combined_rows for key in row.keys()})
        count = write_csv(PROCESSED / "warspotting_latest_losses.csv", combined_rows, fields)
        manifest.append({"source": "warspotting", "processed": "latest_losses", "rows": count})


def collect_oryx_summaries(manifest: List[Dict[str, object]]) -> None:
    pages = [
        {
            "side": "russia",
            "url": "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html",
        },
        {
            "side": "ukraine",
            "url": "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html",
        },
    ]
    rows = []
    for page in pages:
        blob, meta = request_bytes(page["url"], timeout=60, retries=1, headers={"User-Agent": "Mozilla/5.0 " + USER_AGENT})
        meta.update({"source": "oryx", "side": page["side"]})
        if blob:
            html = blob.decode("utf-8", "replace")
            headings = extract_h3_text(html)
            meta["headings"] = len(headings)
            write_json(RAW / "oryx" / f"{page['side']}_category_headings.json", {"url": page["url"], "headings": headings})
            for heading in headings:
                parsed = parse_oryx_heading(page["side"], heading, page["url"])
                if parsed:
                    rows.append(parsed)
        manifest.append(meta)
        time.sleep(2.0)
    fields = ["side", "category", "total", "destroyed", "damaged", "abandoned", "captured", "source_url", "raw_heading"]
    count = write_csv(PROCESSED / "oryx_equipment_loss_category_summaries.csv", rows, fields)
    manifest.append({"source": "oryx", "processed": "category_summaries", "rows": count})


def extract_h3_text(html: str) -> List[str]:
    headings = []
    for match in re.finditer(r"<h3[^>]*>(.*?)</h3>", html, re.S | re.I):
        text = re.sub(r"<.*?>", " ", match.group(1))
        text = unescape(" ".join(text.split()))
        if "of which:" in text or "Losses of" in text:
            headings.append(text)
    return headings


def parse_oryx_heading(side: str, heading: str, url: str) -> Optional[Dict[str, object]]:
    clean = heading.replace("\xa0", " ")
    total_match = re.search(r"^(.*?)\s*-\s*([0-9,]+),\s*of which:\s*(.*)$", clean, re.I)
    if not total_match:
        return None
    category = total_match.group(1).strip()
    totals_text = total_match.group(3)
    row = {
        "side": side,
        "category": category,
        "total": int(total_match.group(2).replace(",", "")),
        "destroyed": "",
        "damaged": "",
        "abandoned": "",
        "captured": "",
        "source_url": url,
        "raw_heading": clean,
    }
    for key in ["destroyed", "damaged", "abandoned", "captured"]:
        match = re.search(key + r":\s*([0-9,]+)", totals_text, re.I)
        if match:
            row[key] = int(match.group(1).replace(",", ""))
    return row


def collect_isw_links(manifest: List[Dict[str, object]]) -> None:
    url = "https://www.understandingwar.org/research/russia-ukraine"
    blob, meta = request_bytes(url, timeout=60, retries=1, headers={"User-Agent": "Mozilla/5.0 " + USER_AGENT})
    meta.update({"source": "isw", "file": "russia_ukraine_index"})
    rows = []
    if blob:
        html = blob.decode("utf-8", "replace")
        write_bytes(RAW / "isw" / "russia_ukraine_index.html", blob)
        seen = set()
        for match in re.finditer(r'href="([^"]+/research/russia-ukraine/[^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
            link = match.group(1)
            title = unescape(re.sub(r"<.*?>", " ", match.group(2)))
            title = " ".join(title.split())
            if not title or link in seen or "twitter.com" in link:
                continue
            seen.add(link)
            rows.append({"title": title, "url": link})
        meta["links"] = len(rows)
    manifest.append(meta)
    count = write_csv(PROCESSED / "isw_recent_russia_ukraine_assessment_links.csv", rows, ["title", "url"])
    manifest.append({"source": "isw", "processed": "assessment_links", "rows": count})


def collect_open_meteo(manifest: List[Dict[str, object]]) -> None:
    rows: List[Dict[str, object]] = []
    end = min(END_DATE, dt.date.today() - dt.timedelta(days=1))
    for aoi in AOIS:
        params = urllib.parse.urlencode(
            {
                "latitude": aoi["lat"],
                "longitude": aoi["lon"],
                "start_date": START_DATE.isoformat(),
                "end_date": end.isoformat(),
                "daily": "temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
                "timezone": "UTC",
            }
        )
        url = "https://archive-api.open-meteo.com/v1/archive?" + params
        blob, meta = request_bytes(url, timeout=60, retries=1)
        meta.update({"source": "open_meteo_archive", "aoi": aoi["id"]})
        if blob:
            path = RAW / "open_meteo" / f"{aoi['id']}_daily_weather.json"
            write_bytes(path, blob)
            meta["local_path"] = str(path)
            try:
                data = json.loads(blob.decode("utf-8", "replace"))
                daily = data.get("daily", {})
                times = daily.get("time", [])
                for idx, date_value in enumerate(times):
                    rows.append(
                        {
                            "aoi": aoi["id"],
                            "aoi_label": aoi["label"],
                            "date": date_value,
                            "temperature_2m_mean": pick_list(daily.get("temperature_2m_mean"), idx),
                            "precipitation_sum": pick_list(daily.get("precipitation_sum"), idx),
                            "wind_speed_10m_max": pick_list(daily.get("wind_speed_10m_max"), idx),
                        }
                    )
                meta["days"] = len(times)
            except json.JSONDecodeError as exc:
                meta["parse_error"] = str(exc)
        manifest.append(meta)
        time.sleep(0.5)
    fields = ["aoi", "aoi_label", "date", "temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]
    count = write_csv(PROCESSED / "open_meteo_aoi_daily_weather_recent.csv", rows, fields)
    manifest.append({"source": "open_meteo_archive", "processed": "aoi_daily_weather", "rows": count})


def pick_list(values: Optional[List[object]], idx: int) -> object:
    if not values or idx >= len(values):
        return ""
    return values[idx]


def collect_key_required_placeholders(manifest: List[Dict[str, object]]) -> None:
    placeholders = [
        {
            "source": "acled",
            "status": "blocked_invalid_credentials",
            "needed_env": ["ACLED_EMAIL", "ACLED_ACCESS_TOKEN", "ACLED_REFRESH_TOKEN"],
            "example_endpoint": "https://acleddata.com/api/acled/read?_format=json&country=Ukraine&event_date=2025-12-01|2026-07-04&event_date_where=BETWEEN&limit=5000",
            "note": "ACLED uses myACLED OAuth. Provided credentials failed with invalid_grant on 2026-07-04; verify password or account activation.",
        },
        {
            "source": "nasa_firms",
            "status": "key_issued_smoke_passed",
            "needed_env": ["NASA_FIRMS_MAP_KEY"],
            "example_endpoint": "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/22,44,40,53/10/2026-07-04",
            "note": "Use for thermal anomaly/fire proxy, not direct strike attribution without corroboration.",
        },
        {
            "source": "alerts_in_ua",
            "status": "request_submitted_token_pending",
            "needed_env": ["ALERTS_IN_UA_TOKEN"],
            "example_project": "https://github.com/alerts-ua/alerts-in-ua-py",
            "note": "User submitted the API token request form on 2026-07-04. Use delayed/historical mode for public demos.",
        },
        {
            "source": "kaggle",
            "status": "api_token_issued_smoke_passed",
            "needed_env": ["KAGGLE_API_TOKEN"],
            "dataset": "piterfm/massive-missile-attacks-on-ukraine",
            "note": "A Kaggle API token named D4D Ukraine OSINT was issued and direct Bearer API smoke passed.",
        },
        {
            "source": "hdx",
            "status": "api_token_issued_smoke_passed",
            "needed_env": ["HDX_API_TOKEN"],
            "example_endpoint": "https://data.humdata.org/api/3/action/package_search?q=Ukraine&rows=20",
            "note": "HDX token named D4D Ukraine OSINT was issued and authorized CKAN package_search passed.",
        },
        {
            "source": "reliefweb",
            "status": "blocked_preapproved_appname_required",
            "needed_env": ["RELIEFWEB_APPNAME"],
            "example_endpoint": "https://api.reliefweb.int/v2/reports?appname={RELIEFWEB_APPNAME}&query[value]=Ukraine&limit=100",
            "note": "ReliefWeb API v2 requires a pre-approved appname from 2025-11-01.",
        },
    ]
    write_json(RAW / "blocked_or_key_required" / "api_placeholders.json", placeholders)
    manifest.extend(placeholders)


def build_dataset_catalog(manifest: List[Dict[str, object]]) -> None:
    files = []
    for path in sorted(DATA_ROOT.rglob("*")):
        if path.is_file() and path.name != "dataset_catalog.json":
            files.append(
                {
                    "path": str(path),
                    "relative_path": str(path.relative_to(DATA_ROOT)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_bytes(path.read_bytes()),
                }
            )
    catalog = {
        "dataset_id": "ukraine_recent_war_osint_v0_1",
        "built_at": now_iso(),
        "date_window": {"start": START_DATE.isoformat(), "end": END_DATE.isoformat()},
        "safety_note": "Public, delayed, aggregate, or non-PII OSINT only. No raw social-media media or live targeting support.",
        "manifest_entries": len(manifest),
        "files": files,
    }
    write_json(METADATA / "dataset_catalog.json", catalog)


def build_readme(manifest: List[Dict[str, object]]) -> None:
    processed_files = sorted(PROCESSED.glob("*"))
    rows = []
    for path in processed_files:
        row_count = ""
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                    row_count = sum(1 for _ in reader)
                except StopIteration:
                    row_count = 0
        rows.append((path.name, row_count, path.stat().st_size))
    table = "\n".join(f"| `{name}` | {count} | {size} |" for name, count, size in rows)
    readme = f"""# Ukraine Recent War OSINT Dataset

- Built at: {now_iso()}
- Date window: {START_DATE.isoformat()} to {END_DATE.isoformat()}
- Scenario focus: rail/energy infrastructure pressure, missile/UAV saturation, Black Sea / port context, and COP/C2 prioritization.
- Safety: no live targeting recommendations, no PII collection, no raw social-media media archive.

## Processed Tables

| File | Rows | Bytes |
|---|---:|---:|
{table}

## Source Families

- Petro Ivaniuk GitHub: Russian equipment/personnel loss time series.
- Massive Missile Attacks derivative GitHub CSV: missile/UAV launch and interception records.
- UCDP GED/candidate GED: academically maintained organized violence event data.
- GDELT DOC/API and GDELT v2 exports: news-derived article/event layer.
- OpenStreetMap Overpass: selected AOI critical infrastructure basemap.
- WarSpotting: latest visually confirmed loss records where accessible.
- Oryx: category-level equipment loss summaries only, with source URL retained.
- ISW: recent assessment link index, not full copyrighted article archive.
- Open-Meteo: AOI weather context for scenario explanation.

## Key-Required / Blocked Sources

See `raw/blocked_or_key_required/api_placeholders.json`.

## Suggested Use

Use `processed/missile_uav_daily_summary_recent.csv`, `processed/osm_ukraine_aoi_critical_infrastructure.csv`, and `processed/gdelt_event_export_ukraine_filtered_recent.csv` as the first MVP data spine. Then add ACLED and NASA FIRMS after keys are available.
"""
    (DATA_ROOT / "README.md").write_text(readme, encoding="utf-8")
    write_json(METADATA / "collection_manifest.json", manifest)


def main() -> int:
    ensure_dirs()
    manifest: List[Dict[str, object]] = []
    steps = [
        ("petro_ivaniuk", collect_petro_ivaniuk),
        ("missile_attacks", collect_missile_attack_csvs),
        ("ucdp", collect_ucdp),
        ("gdelt_doc", collect_gdelt_doc),
        ("gdelt_event_exports", collect_gdelt_event_exports),
        ("osm_overpass", collect_osm_overpass),
        ("warspotting", collect_warspotting),
        ("oryx", collect_oryx_summaries),
        ("isw", collect_isw_links),
        ("open_meteo", collect_open_meteo),
        ("key_required_placeholders", collect_key_required_placeholders),
    ]
    for name, func in steps:
        print(f"[collect] {name}", flush=True)
        try:
            if name == "gdelt_event_exports":
                func(manifest, hours=int(os.environ.get("D4D_GDELT_HOURS", "24")))
            elif name == "ucdp":
                include_stable = os.environ.get("D4D_SKIP_UCDP_STABLE", "0") != "1"
                func(manifest, include_stable_ged=include_stable)
            else:
                func(manifest)
        except Exception as exc:  # noqa: BLE001
            manifest.append({"source": name, "fatal_step_error": str(exc), "type": type(exc).__name__, "time": now_iso()})
            print(f"[warn] {name}: {exc}", file=sys.stderr, flush=True)
    build_readme(manifest)
    build_dataset_catalog(manifest)
    print(f"[done] dataset root: {DATA_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

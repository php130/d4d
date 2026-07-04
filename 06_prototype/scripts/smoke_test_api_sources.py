#!/usr/bin/env python3
"""Smoke test live API/data sources for the D4D maritime COP project.

The script reads credentials from the project `.env`, calls small low-risk
queries, and writes a versioned report plus tiny raw snapshots. It never prints
or stores API keys in reports.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
ENV_PATH = PROJECT_ROOT / ".env"
RAW_ROOT = PROJECT_ROOT / "03_data/raw/api_snapshots"
REPORT_ROOT = PROJECT_ROOT / "03_data/processed/api_smoke_tests"
DEFAULT_HEADERS = {
    "User-Agent": "D4D-hackathon-research/0.1 contact:mollykim2602@gmail.com",
}


KST = timezone(timedelta(hours=9))


@dataclass
class SmokeResult:
    service: str
    status: str
    event_use: str
    checked_at: str
    url_label: str
    http_status: int | None = None
    sample_path: str | None = None
    detail: str | None = None
    next_action: str | None = None


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        env[key.strip()] = value
    return env


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    return datetime.now(KST).strftime("%Y%m%d_%H%M%S")


def write_sample(run_dir: Path, service: str, suffix: str, payload: bytes) -> str:
    service_dir = run_dir / service
    service_dir.mkdir(parents=True, exist_ok=True)
    safe_payload = payload[:200_000]
    path = service_dir / f"sample.{suffix}"
    path.write_bytes(safe_payload)
    return str(path)


def url_with_query(base_url: str, params: dict[str, Any]) -> str:
    return base_url + "?" + urllib.parse.urlencode(
        {k: v for k, v in params.items() if v is not None},
        doseq=True,
    )


def get_bytes(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> tuple[int, bytes]:
    request_headers = DEFAULT_HEADERS.copy()
    request_headers.update(headers or {})
    req = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.read()


def post_form(url: str, data: dict[str, str], timeout: int = 20) -> tuple[int, bytes]:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.read()


def post_json(url: str, data: dict[str, Any], headers: dict[str, str] | None = None, timeout: int = 20) -> tuple[int, bytes]:
    encoded = json.dumps(data).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    request_headers.update(headers or {})
    req = urllib.request.Request(url, data=encoded, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.read()


def decode_json(payload: bytes) -> Any:
    return json.loads(payload.decode("utf-8"))


def result(
    service: str,
    status: str,
    event_use: str,
    url_label: str,
    *,
    http_status: int | None = None,
    sample_path: str | None = None,
    detail: str | None = None,
    next_action: str | None = None,
) -> SmokeResult:
    return SmokeResult(
        service=service,
        status=status,
        event_use=event_use,
        checked_at=now_iso(),
        url_label=url_label,
        http_status=http_status,
        sample_path=sample_path,
        detail=detail,
        next_action=next_action,
    )


def catch_result(service: str, event_use: str, url_label: str, exc: Exception) -> SmokeResult:
    if isinstance(exc, urllib.error.HTTPError):
        detail = f"HTTPError {exc.code}: {exc.reason}"
        http_status = exc.code
        if exc.code == 429:
            return result(
                service,
                "rate_limited",
                event_use,
                url_label,
                http_status=http_status,
                detail=detail[:500],
                next_action="Back off before retrying; cache the latest sample or use bulk export/BigQuery for higher-volume GDELT collection.",
            )
    elif isinstance(exc, urllib.error.URLError):
        detail = f"URLError: {exc.reason}"
        http_status = None
    else:
        detail = f"{type(exc).__name__}: {exc}"
        http_status = None
    return result(
        service,
        "failed",
        event_use,
        url_label,
        http_status=http_status,
        detail=detail[:500],
        next_action="Check endpoint authorization, params, or service availability.",
    )


def data_go_kr_weather(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "data_go_kr_weather"
    event_use = "WEATHER_HAZARD"
    key = env.get("DATA_GO_KR_SERVICE_KEY_PLAIN") or env.get("DATA_GO_KR_SERVICE_KEY")
    if not key:
        return result(service, "skipped", event_use, "VilageFcstInfoService", next_action="Store DATA_GO_KR_SERVICE_KEY.")

    # Ultra-short observations are usually safest after a short publication lag.
    kst_now = datetime.now(KST) - timedelta(hours=2)
    base_date = kst_now.strftime("%Y%m%d")
    base_time = kst_now.strftime("%H00")
    params = {
        "serviceKey": key,
        "pageNo": 1,
        "numOfRows": 10,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": 60,
        "ny": 127,
    }
    url = url_with_query(
        "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst",
        params,
    )
    try:
        http_status, payload = get_bytes(url)
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        header = data.get("response", {}).get("header", {})
        code = header.get("resultCode")
        msg = header.get("resultMsg")
        status = "passed" if code == "00" else "failed"
        return result(service, status, event_use, "data.go.kr KMA ultra-short nowcast", http_status=http_status, sample_path=sample_path, detail=f"{code}: {msg}")
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "data.go.kr KMA ultra-short nowcast", exc)


def kma_apihub_sea(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "kma_apihub_sea_forecast"
    event_use = "WEATHER_HAZARD, SEA_STATE_RISK"
    key = env.get("KMA_APIHUB_KEY")
    if not key:
        return result(service, "skipped", event_use, "KMA APIHub fct_afs_do", next_action="Store KMA_APIHUB_KEY.")
    params = {
        "tmfc": "0",
        "reg": "12A00000",
        "disp": "0",
        "help": "0",
        "authKey": key,
    }
    url = url_with_query("https://apihub.kma.go.kr/api/typ01/url/fct_afs_do.php", params)
    try:
        http_status, payload = get_bytes(url)
        sample_path = write_sample(run_dir, service, "txt", payload)
        text = payload.decode("utf-8", errors="replace")
        status = "passed" if http_status == 200 and "ERROR" not in text[:300].upper() else "failed"
        detail = text.replace("\r", " ").replace("\n", " ")[:220]
        return result(service, status, event_use, "KMA APIHub short sea forecast", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "KMA APIHub short sea forecast", exc)


def vworld_geocode(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "vworld_geocode"
    event_use = "COP_BASE_LAYER"
    key = env.get("VWORLD_API_KEY")
    if not key:
        return result(service, "skipped", event_use, "VWorld address", next_action="Store VWORLD_API_KEY.")
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "address": "서울특별시 중구 세종대로 110",
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": "road",
        "key": key,
    }
    url = url_with_query("https://api.vworld.kr/req/address", params)
    try:
        http_status, payload = get_bytes(url)
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        response = data.get("response", {})
        status = "passed" if response.get("status") == "OK" else "failed"
        return result(service, status, event_use, "VWorld road-address geocoding", http_status=http_status, sample_path=sample_path, detail=str(response.get("status")))
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "VWorld road-address geocoding", exc)


def gdelt_maritime(run_dir: Path) -> SmokeResult:
    service = "gdelt_maritime"
    event_use = "OSINT_INCIDENT"
    params = {
        "query": '("maritime incident" OR "port disruption" OR "AIS")',
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 5,
        "sort": "HybridRel",
    }
    url = url_with_query("https://api.gdeltproject.org/api/v2/doc/doc", params)
    try:
        http_status, payload = get_bytes(url)
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        articles = data.get("articles", [])
        status = "passed" if isinstance(articles, list) else "failed"
        return result(service, status, event_use, "GDELT DOC API maritime query", http_status=http_status, sample_path=sample_path, detail=f"articles={len(articles)}")
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "GDELT DOC API maritime query", exc)


def open_meteo_marine(run_dir: Path) -> SmokeResult:
    service = "open_meteo_marine"
    event_use = "SEA_STATE_RISK"
    params = {
        "latitude": 35.10,
        "longitude": 129.05,
        "hourly": "wave_height,sea_surface_temperature",
        "forecast_days": 1,
    }
    url = url_with_query("https://marine-api.open-meteo.com/v1/marine", params)
    try:
        http_status, payload = get_bytes(url)
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        status = "passed" if "hourly" in data else "failed"
        detail = ",".join(data.get("hourly", {}).keys())[:220]
        return result(service, status, event_use, "Open-Meteo Marine API Busan AOI", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "Open-Meteo Marine API Busan AOI", exc)


def copernicus_sentinel1(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "copernicus_sentinel1_catalogue"
    event_use = "SAR_DARK_VESSEL_CANDIDATE"
    email = env.get("COPERNICUS_DATASPACE_EMAIL")
    password = env.get("COPERNICUS_DATASPACE_PASSWORD")
    token = env.get("COPERNICUS_ACCESS_TOKEN")
    try:
        if email and password:
            _, payload = post_form(
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                {
                    "client_id": "cdse-public",
                    "username": email,
                    "password": password,
                    "grant_type": "password",
                },
            )
            token = decode_json(payload)["access_token"]
        if not token:
            return result(service, "skipped", event_use, "Copernicus OData Products", next_action="Store COPERNICUS_ACCESS_TOKEN or account credentials.")
        params = {
            "$filter": "Collection/Name eq 'SENTINEL-1'",
            "$top": 1,
            "$select": "Id,Name,ContentDate",
        }
        url = url_with_query("https://catalogue.dataspace.copernicus.eu/odata/v1/Products", params)
        http_status, payload = get_bytes(url, headers={"Authorization": f"Bearer {token}"})
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        rows = data.get("value", [])
        status = "passed" if isinstance(rows, list) and rows else "failed"
        detail = rows[0].get("Name") if rows else "no products returned"
        return result(service, status, event_use, "Copernicus Data Space Sentinel-1 product search", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "Copernicus Data Space Sentinel-1 product search", exc)


def nasa_cmr(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "nasa_earthdata_cmr"
    event_use = "OCEAN_STATE, WEATHER_HAZARD"
    token = env.get("NASA_EARTHDATA_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    params = {"keyword": "ocean wind", "page_size": 1}
    url = url_with_query("https://cmr.earthdata.nasa.gov/search/collections.json", params)
    try:
        http_status, payload = get_bytes(url, headers=headers)
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        entries = data.get("feed", {}).get("entry", [])
        status = "passed" if isinstance(entries, list) and entries else "failed"
        detail = entries[0].get("short_name") if entries else "no collections returned"
        return result(service, status, event_use, "NASA CMR collection search", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "NASA CMR collection search", exc)


def global_fishing_watch(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "global_fishing_watch"
    event_use = "AIS_GAP, SAR_DARK_VESSEL_CANDIDATE"
    token = env.get("GLOBAL_FISHING_WATCH_TOKEN")
    email_status = env.get("GLOBAL_FISHING_WATCH_EMAIL_VERIFICATION_STATUS")
    if not token:
        return result(
            service,
            "blocked",
            event_use,
            "GFW API",
            detail=email_status or "token missing",
            next_action="Verify the account email, then create/store GLOBAL_FISHING_WATCH_TOKEN.",
        )
    params = {
        "datasets[0]": "public-global-presence:latest",
        "temporal-aggregation": "false",
        "num-bins": 9,
        "interval": "DAY",
    }
    url = url_with_query("https://gateway.api.globalfishingwatch.org/v3/4wings/bins/1", params)
    try:
        http_status, payload = get_bytes(url, headers={"Authorization": f"Bearer {token}"})
        sample_path = write_sample(run_dir, service, "json", payload)
        data = decode_json(payload)
        entries = data.get("entries", []) if isinstance(data, dict) else []
        status = "passed" if isinstance(entries, list) else "failed"
        detail = f"entries={len(entries)}"
        return result(service, status, event_use, "GFW 4Wings AIS vessel presence bins", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "GFW 4Wings AIS vessel presence bins", exc)


def safetydata(env: dict[str, str]) -> SmokeResult:
    service = "safetydata"
    event_use = "OSINT_INCIDENT, DISASTER_ALERT"
    key = env.get("SAFETYDATA_API_KEY")
    if not key:
        return result(
            service,
            "blocked",
            event_use,
            "SafetyData API",
            detail=env.get("SAFETYDATA_APPLICATION_STATUS", "key missing"),
            next_action="Wait for disaster message application approval, then store SAFETYDATA_API_KEY.",
        )
    return result(service, "pending_connector", event_use, "SafetyData API", detail="key present; endpoint connector not implemented yet")


def opensanctions_match(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "opensanctions_match"
    event_use = "SANCTION_OR_WATCHLIST_MATCH"
    key = env.get("OPENSANCTIONS_API_KEY")
    if not key:
        return result(service, "skipped", event_use, "OpenSanctions /match/default", next_action="Store OPENSANCTIONS_API_KEY.")
    payload = {
        "queries": {
            "query": {
                "schema": "Person",
                "properties": {"name": ["Vladimir Putin"]},
            }
        }
    }
    try:
        http_status, response = post_json(
            "https://api.opensanctions.org/match/default",
            payload,
            headers={"Authorization": f"ApiKey {key}"},
        )
        sample_path = write_sample(run_dir, service, "json", response)
        data = decode_json(response)
        results = data.get("responses", {}).get("query", {}).get("results", [])
        status = "passed" if isinstance(results, list) else "failed"
        detail = f"results={len(results)}"
        return result(service, status, event_use, "OpenSanctions match/default documented sample query", http_status=http_status, sample_path=sample_path, detail=detail)
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "OpenSanctions match/default documented sample query", exc)


def run_all() -> dict[str, Any]:
    env = load_env(ENV_PATH)
    rid = run_id()
    raw_run_dir = RAW_ROOT / rid
    report_run_dir = REPORT_ROOT / rid
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    report_run_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        data_go_kr_weather(env, raw_run_dir),
        kma_apihub_sea(env, raw_run_dir),
        vworld_geocode(env, raw_run_dir),
        gdelt_maritime(raw_run_dir),
        open_meteo_marine(raw_run_dir),
        copernicus_sentinel1(env, raw_run_dir),
        nasa_cmr(env, raw_run_dir),
        opensanctions_match(env, raw_run_dir),
        global_fishing_watch(env, raw_run_dir),
        safetydata(env),
    ]
    report = {
        "run_id": rid,
        "generated_at": now_iso(),
        "env_path": str(ENV_PATH),
        "raw_snapshot_dir": str(raw_run_dir),
        "results": [asdict(item) for item in checks],
    }
    (report_run_dir / "smoke_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = REPORT_ROOT / "latest.json"
    latest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def print_summary(report: dict[str, Any]) -> None:
    print(f"API smoke test run: {report['run_id']}")
    for item in report["results"]:
        http = "" if item["http_status"] is None else f" HTTP {item['http_status']}"
        detail = f" - {item['detail']}" if item.get("detail") else ""
        print(f"- {item['service']}: {item['status']}{http}{detail}")
    print(f"Report: {REPORT_ROOT / report['run_id'] / 'smoke_report.json'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = run_all()
    print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

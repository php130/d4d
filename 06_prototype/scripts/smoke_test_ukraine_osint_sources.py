#!/usr/bin/env python3
"""Smoke test Ukraine OSINT API sources that need separate credentials.

The script reads secrets from `/Users/mollykim/projects/D4D/.env`, performs
small low-risk requests, and writes tiny samples plus a redacted JSON report.
It never prints or stores API keys, passwords, or tokens in the report.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
ENV_PATH = PROJECT_ROOT / ".env"
REPORT_ROOT = PROJECT_ROOT / "03_data/processed/ukraine_osint_api_smoke_tests"
SNAPSHOT_ROOT = PROJECT_ROOT / "03_data/ukraine_recent_war_osint/raw/api_smoke_tests"
KST = timezone(timedelta(hours=9))

DEFAULT_HEADERS = {
    "User-Agent": "D4D-hackathon-research/0.1 contact:mollykim2602@gmail.com",
}


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
    path = run_dir / service / f"sample.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload[:200_000])
    return str(path)


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


def request_bytes(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    method: str | None = None,
    timeout: int = 30,
) -> tuple[int, bytes]:
    request_headers = DEFAULT_HEADERS.copy()
    request_headers.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.read()


def catch_result(service: str, event_use: str, url_label: str, exc: Exception) -> SmokeResult:
    if isinstance(exc, urllib.error.HTTPError):
        detail = f"HTTPError {exc.code}: {exc.reason}"
        http_status = exc.code
        if exc.code in {401, 403}:
            next_action = "Check credentials, account approval, token scope, or dataset terms."
        elif exc.code == 429:
            next_action = "Back off and retry later; use cached samples for demos."
        else:
            next_action = "Check endpoint parameters or service status."
        return result(
            service,
            "failed",
            event_use,
            url_label,
            http_status=http_status,
            detail=detail,
            next_action=next_action,
        )
    if isinstance(exc, urllib.error.URLError):
        detail = f"URLError: {exc.reason}"
    else:
        detail = f"{type(exc).__name__}: {exc}"
    return result(
        service,
        "failed",
        event_use,
        url_label,
        detail=detail[:500],
        next_action="Check local network or endpoint availability.",
    )


def acled_oauth(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "acled_oauth"
    event_use = "CONFLICT_EVENT_SPINE"
    token = env.get("ACLED_ACCESS_TOKEN")
    if not token:
        login_status = env.get("ACLED_LOGIN_STATUS", "missing_token")
        return result(
            service,
            "blocked",
            event_use,
            "ACLED OAuth + Ukraine query",
            detail=login_status,
            next_action="Verify ACLED username/password or email activation, then refresh ACLED_ACCESS_TOKEN.",
        )

    params = urllib.parse.urlencode(
        {
            "_format": "json",
            "country": "Ukraine",
            "event_date": "2026-06-01|2026-07-04",
            "event_date_where": "BETWEEN",
            "limit": "5",
            "fields": "event_id_cnty|event_date|event_type|sub_event_type|country|admin1|location|latitude|longitude|source|fatalities",
        }
    )
    url = f"https://acleddata.com/api/acled/read?{params}"
    try:
        http_status, payload = request_bytes(url, headers={"Authorization": f"Bearer {token}"})
        sample_path = write_sample(run_dir, service, "json", payload)
        data = json.loads(payload.decode("utf-8"))
        rows = data.get("data") if isinstance(data, dict) else data
        count = len(rows) if isinstance(rows, list) else None
        return result(
            service,
            "passed" if http_status == 200 else "failed",
            event_use,
            "ACLED Ukraine events",
            http_status=http_status,
            sample_path=sample_path,
            detail=f"rows={count}",
        )
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "ACLED Ukraine events", exc)


def nasa_firms(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "nasa_firms"
    event_use = "THERMAL_ANOMALY_PROXY"
    key = env.get("NASA_FIRMS_MAP_KEY")
    if not key:
        return result(service, "skipped", event_use, "NASA FIRMS area CSV", next_action="Store NASA_FIRMS_MAP_KEY.")

    # Tiny area around Kyiv for a one-day check to keep sample small.
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/30,48,31,49/1/2026-07-03"
    try:
        http_status, payload = request_bytes(url)
        sample_path = write_sample(run_dir, service, "csv", payload)
        text = payload.decode("utf-8", errors="replace")
        ok = http_status == 200 and "Invalid MAP_KEY" not in text[:500]
        rows = max(0, len(text.splitlines()) - 1) if text.strip() else 0
        return result(
            service,
            "passed" if ok else "failed",
            event_use,
            "NASA FIRMS VIIRS_SNPP_NRT tiny AOI",
            http_status=http_status,
            sample_path=sample_path,
            detail=f"rows={rows}",
        )
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "NASA FIRMS VIIRS_SNPP_NRT tiny AOI", exc)


def kaggle_api(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "kaggle_api"
    event_use = "MISSILE_UAV_ATTACK_DATASET"
    token = env.get("KAGGLE_API_TOKEN")
    if not token:
        return result(service, "skipped", event_use, "Kaggle dataset API", next_action="Store KAGGLE_API_TOKEN or legacy KAGGLE_KEY.")

    url = "https://www.kaggle.com/api/v1/datasets/list?" + urllib.parse.urlencode(
        {"search": "ukraine missile", "page": "1", "pageSize": "5"}
    )
    try:
        http_status, payload = request_bytes(url, headers={"Authorization": f"Bearer {token}"})
        sample_path = write_sample(run_dir, service, "json", payload)
        data = json.loads(payload.decode("utf-8"))
        count = len(data) if isinstance(data, list) else None
        return result(
            service,
            "passed" if http_status == 200 else "failed",
            event_use,
            "Kaggle dataset search",
            http_status=http_status,
            sample_path=sample_path,
            detail=f"results={count}; token_file=/Users/mollykim/.kaggle/access_token",
        )
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "Kaggle dataset search", exc)


def hdx_ckan(env: dict[str, str], run_dir: Path) -> SmokeResult:
    service = "hdx_ckan"
    event_use = "HUMANITARIAN_CONTEXT_LAYER"
    token = env.get("HDX_API_TOKEN")
    if not token:
        return result(service, "skipped", event_use, "HDX CKAN package_search", next_action="Store HDX_API_TOKEN or use public CKAN only.")

    url = "https://data.humdata.org/api/3/action/package_search?" + urllib.parse.urlencode(
        {"q": "Ukraine", "rows": "5"}
    )
    try:
        http_status, payload = request_bytes(url, headers={"Authorization": token})
        sample_path = write_sample(run_dir, service, "json", payload)
        data = json.loads(payload.decode("utf-8"))
        result_obj = data.get("result", {}) if isinstance(data, dict) else {}
        count = result_obj.get("count")
        return result(
            service,
            "passed" if http_status == 200 and data.get("success") is True else "failed",
            event_use,
            "HDX CKAN package_search Ukraine",
            http_status=http_status,
            sample_path=sample_path,
            detail=f"total_count={count}",
        )
    except Exception as exc:  # noqa: BLE001
        return catch_result(service, event_use, "HDX CKAN package_search Ukraine", exc)


def main() -> int:
    env = load_env(ENV_PATH)
    rid = run_id()
    sample_run_dir = SNAPSHOT_ROOT / rid
    report_run_dir = REPORT_ROOT / rid
    report_run_dir.mkdir(parents=True, exist_ok=True)

    results = [
        acled_oauth(env, sample_run_dir),
        nasa_firms(env, sample_run_dir),
        kaggle_api(env, sample_run_dir),
        hdx_ckan(env, sample_run_dir),
    ]

    report = {
        "run_id": rid,
        "checked_at": now_iso(),
        "results": [asdict(item) for item in results],
        "summary": {
            "passed": sum(1 for item in results if item.status == "passed"),
            "blocked": sum(1 for item in results if item.status == "blocked"),
            "skipped": sum(1 for item in results if item.status == "skipped"),
            "failed": sum(1 for item in results if item.status == "failed"),
        },
    }
    report_path = report_run_dir / "smoke_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"run_id": rid, "report_path": str(report_path), "summary": report["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

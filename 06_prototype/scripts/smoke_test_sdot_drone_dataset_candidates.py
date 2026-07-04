#!/usr/bin/env python3
"""Smoke test public GNSS/RF/link dataset candidates for S-DOT drone research.

This script checks metadata/page accessibility only. It does not download large
raw RF/IQ datasets. Each fetched sample is capped and stored for audit.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
CANDIDATES_JSON = PROJECT_ROOT / "03_data/processed/literature_sdot_drone/gnss_rf_link_dataset_candidates_20260704.json"
REPORT_ROOT = PROJECT_ROOT / "03_data/processed/literature_sdot_drone/dataset_smoke_tests"
LATEST_JSON = PROJECT_ROOT / "03_data/processed/literature_sdot_drone/latest_dataset_smoke_test.json"
SAMPLE_LIMIT = 200_000
KST = timezone(timedelta(hours=9))

DEFAULT_HEADERS = {
    "User-Agent": "D4D-SDOT-dataset-smoke-test/0.1 contact:mollykim2602@gmail.com",
    "Accept": "text/html,application/json,text/plain;q=0.9,*/*;q=0.8",
}

KEYWORDS = [
    "jamming",
    "spoofing",
    "meaconing",
    "gnss",
    "gps",
    "galileo",
    "i/q",
    "iq",
    "rinex",
    "ubx",
    "c/n0",
    "cn0",
    "dop",
    "doppler",
    "pseudorange",
    "rss",
    "rssi",
    "snr",
    "packet loss",
    "uav",
    "drone",
    "trajectory",
    "received power",
]


@dataclass
class UrlCheck:
    label: str
    url: str
    status: str
    checked_at: str
    http_status: int | None = None
    final_url: str | None = None
    content_type: str | None = None
    content_length_header: str | None = None
    sample_path: str | None = None
    sample_bytes: int | None = None
    title: str | None = None
    keyword_hits: list[str] | None = None
    detail: str | None = None


@dataclass
class DatasetSmokeResult:
    dataset_id: str
    name: str
    classification: str
    domain: str
    overall_status: str
    status: str
    best_sdot_use: list[str]
    limitations: list[str]
    checks: list[UrlCheck]
    metadata_summary: dict[str, Any]
    next_action: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    return datetime.now(KST).strftime("%Y%m%d_%H%M%S")


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_")[:120]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_sample(run_dir: Path, dataset_id: str, label: str, payload: bytes, content_type: str | None) -> str:
    suffix = "json" if content_type and "json" in content_type else "html" if content_type and "html" in content_type else "txt"
    path = run_dir / "samples" / safe_name(dataset_id) / f"{safe_name(label)}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload[:SAMPLE_LIMIT])
    return str(path)


def request_sample(url: str, timeout: int = 20) -> tuple[int, str, str | None, str | None, bytes]:
    headers = DEFAULT_HEADERS.copy()
    headers["Range"] = f"bytes=0-{SAMPLE_LIMIT - 1}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = response.read(SAMPLE_LIMIT)
        return (
            response.status,
            response.geturl(),
            response.headers.get("content-type"),
            response.headers.get("content-length"),
            payload,
        )


def decode_payload(payload: bytes, content_type: str | None) -> str:
    encoding = "utf-8"
    if content_type:
        match = re.search(r"charset=([^;]+)", content_type, flags=re.I)
        if match:
            encoding = match.group(1).strip()
    return payload.decode(encoding, errors="replace")


def extract_title(text: str) -> str | None:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
    if title_match:
        return re.sub(r"\s+", " ", title_match.group(1)).strip()[:200]
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
    if h1_match:
        return re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", h1_match.group(1))).strip()[:200]
    return None


def keyword_hits(text: str) -> list[str]:
    lower = text.lower()
    return [keyword for keyword in KEYWORDS if keyword.lower() in lower]


def check_url(run_dir: Path, dataset_id: str, label: str, url: str) -> UrlCheck:
    try:
        http_status, final_url, content_type, content_length, payload = request_sample(url)
        sample_path = write_sample(run_dir, dataset_id, label, payload, content_type)
        text = decode_payload(payload, content_type)
        return UrlCheck(
            label=label,
            url=url,
            status="passed" if 200 <= http_status < 400 else "failed",
            checked_at=now_iso(),
            http_status=http_status,
            final_url=final_url,
            content_type=content_type,
            content_length_header=content_length,
            sample_path=sample_path,
            sample_bytes=len(payload),
            title=extract_title(text),
            keyword_hits=keyword_hits(text),
        )
    except urllib.error.HTTPError as exc:
        return UrlCheck(
            label=label,
            url=url,
            status="failed",
            checked_at=now_iso(),
            http_status=exc.code,
            detail=f"HTTPError {exc.code}: {exc.reason}",
        )
    except Exception as exc:  # noqa: BLE001
        return UrlCheck(
            label=label,
            url=url,
            status="failed",
            checked_at=now_iso(),
            detail=f"{type(exc).__name__}: {exc}",
        )


def zenodo_api_url(url: str) -> str | None:
    match = re.search(r"zenodo\.org/records/(\d+)", url)
    if not match:
        return None
    return f"https://zenodo.org/api/records/{match.group(1)}"


def github_api_url(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    return f"https://api.github.com/repos/{parts[0]}/{parts[1]}"


def extract_json_metadata(check: UrlCheck) -> dict[str, Any]:
    if check.status != "passed" or not check.sample_path:
        return {}
    path = Path(check.sample_path)
    if not path.exists() or path.suffix != ".json":
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if "files" in data and isinstance(data["files"], list):
        total_size = sum(file.get("filesize") or file.get("size") or 0 for file in data["files"] if isinstance(file, dict))
        return {
            "api_kind": "zenodo_record",
            "record_id": data.get("id"),
            "doi": data.get("doi"),
            "file_count": len(data["files"]),
            "total_file_size_bytes": total_size,
            "title": data.get("metadata", {}).get("title"),
        }
    if "full_name" in data and "html_url" in data:
        return {
            "api_kind": "github_repo",
            "full_name": data.get("full_name"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "license": (data.get("license") or {}).get("spdx_id") if isinstance(data.get("license"), dict) else None,
            "default_branch": data.get("default_branch"),
        }
    return {}


def dataset_url_checks(run_dir: Path, dataset: dict[str, Any]) -> tuple[list[UrlCheck], dict[str, Any]]:
    urls: list[tuple[str, str]] = []
    for key, label in [
        ("source_url", "source"),
        ("related_tool_url", "related_tool"),
        ("paper_url", "paper"),
    ]:
        if dataset.get(key):
            urls.append((label, dataset[key]))

    source_url = dataset.get("source_url", "")
    extra_urls = []
    if zenodo := zenodo_api_url(source_url):
        extra_urls.append(("zenodo_api", zenodo))
    if github := github_api_url(source_url):
        extra_urls.append(("github_api", github))

    checks = [check_url(run_dir, dataset["dataset_id"], label, url) for label, url in urls + extra_urls]
    metadata_summary: dict[str, Any] = {}
    for check in checks:
        metadata_summary.update(extract_json_metadata(check))
    return checks, metadata_summary


def status_for_checks(checks: list[UrlCheck]) -> str:
    if not checks:
        return "no_urls"
    passed = [check for check in checks if check.status == "passed"]
    if len(passed) == len(checks):
        return "passed"
    if passed:
        return "partial"
    return "failed"


def next_action(dataset: dict[str, Any], status: str) -> str:
    if status == "failed":
        return "Retry manually or look for an alternate mirror/API before relying on this source."
    if dataset["classification"] == "candidate_validation":
        if dataset["dataset_id"] == "yunnan_gnss_interference_spoofing":
            return "Best first smoke-test target for v0.7 GNSS feature ranges; inspect file sizes before downloading."
        if dataset["dataset_id"] == "aerpaw_dataset_12":
            return "Best first smoke-test target for RSS/GPS link-health feature ranges; inspect Dryad file list before downloading."
        return "Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined."
    return "Keep as reference-only citation/design input for now."


def build_results(run_dir: Path, candidates: dict[str, Any]) -> list[DatasetSmokeResult]:
    results: list[DatasetSmokeResult] = []
    for dataset in candidates["datasets"]:
        checks, metadata_summary = dataset_url_checks(run_dir, dataset)
        overall = status_for_checks(checks)
        results.append(
            DatasetSmokeResult(
                dataset_id=dataset["dataset_id"],
                name=dataset["name"],
                classification=dataset["classification"],
                domain=dataset["domain"],
                overall_status=overall,
                status=overall,
                best_sdot_use=dataset.get("best_sdot_use", []),
                limitations=dataset.get("limitations", []),
                checks=checks,
                metadata_summary=metadata_summary,
                next_action=next_action(dataset, overall),
            )
        )
    return results


def write_markdown(run_dir: Path, report: dict[str, Any]) -> Path:
    path = run_dir / "dataset_smoke_test_report.md"
    lines = [
        "# S-DOT Drone Dataset Candidate Smoke Test",
        "",
        f"- Run ID: `{report['run_id']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- Candidate datasets: {report['summary']['dataset_count']}",
        f"- Passed: {report['summary']['passed']}",
        f"- Partial: {report['summary']['partial']}",
        f"- Failed: {report['summary']['failed']}",
        "",
        "## Results",
        "",
        "| Dataset | Class | Status | URL Checks | Next Action |",
        "|---|---|---|---:|---|",
    ]
    for item in report["results"]:
        checks = item["checks"]
        passed = sum(1 for check in checks if check["status"] == "passed")
        lines.append(
            f"| `{item['dataset_id']}` | {item['classification']} | {item['overall_status']} | {passed}/{len(checks)} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Samples are capped at 200KB and are page/API metadata only.",
            "- No large RF/IQ/UBX/RINEX datasets were downloaded.",
            "- Public data can calibrate feature ranges, but the end-to-end S-DOT mission timeline remains synthetic.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    candidates = read_json(CANDIDATES_JSON)
    rid = run_id()
    run_dir = REPORT_ROOT / rid
    run_dir.mkdir(parents=True, exist_ok=True)

    results = build_results(run_dir, candidates)
    summary = {
        "dataset_count": len(results),
        "passed": sum(1 for result in results if result.overall_status == "passed"),
        "partial": sum(1 for result in results if result.overall_status == "partial"),
        "failed": sum(1 for result in results if result.overall_status == "failed"),
        "no_urls": sum(1 for result in results if result.overall_status == "no_urls"),
    }
    report = {
        "run_id": rid,
        "checked_at": now_iso(),
        "candidate_source": str(CANDIDATES_JSON),
        "sample_limit_bytes": SAMPLE_LIMIT,
        "summary": summary,
        "results": [asdict(result) for result in results],
    }
    report_path = run_dir / "dataset_smoke_test_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = write_markdown(run_dir, report)
    LATEST_JSON.write_text(
        json.dumps(
            {
                "latest": str(report_path),
                "latest_markdown": str(md_path),
                "run_id": rid,
                "updated_at": now_iso(),
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"report": str(report_path), "markdown": str(md_path), "summary": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

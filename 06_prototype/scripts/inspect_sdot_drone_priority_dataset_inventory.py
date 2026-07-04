#!/usr/bin/env python3
"""Inspect priority public dataset inventories for S-DOT drone v0.7.

The script collects metadata and file inventory only. It intentionally does not
download source data files, especially large RF/IQ archives.
"""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
OUT_ROOT = PROJECT_ROOT / "03_data/processed/literature_sdot_drone/dataset_inventory"
LATEST_JSON = PROJECT_ROOT / "03_data/processed/literature_sdot_drone/latest_priority_dataset_inventory.json"
KST = timezone(timedelta(hours=9))

HEADERS = {
    "User-Agent": "D4D-SDOT-dataset-inventory/0.1 contact:mollykim2602@gmail.com",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}


@dataclass(frozen=True)
class SourceSpec:
    dataset_id: str
    title: str
    source_url: str
    source_kind: str
    api_url: str
    sdot_use: list[str]
    ingestion_role: str
    caveat: str


SOURCES = [
    SourceSpec(
        dataset_id="yunnan_gnss_interference_spoofing",
        title="GNSS Dataset (with Interference and Spoofing) Part I",
        source_url="https://data.mendeley.com/datasets/ccdgjcfvn5/1",
        source_kind="mendeley_public_api",
        api_url="https://data.mendeley.com/public-api/datasets/ccdgjcfvn5",
        sdot_use=[
            "GNSS C/N0, DOP, Doppler, pseudorange, position feature-range calibration",
            "clean/jamming/spoofing receiver-state class reference",
        ],
        ingestion_role="best_gnss_feature_range_candidate",
        caveat="Static receiver dataset; not a moving drone trajectory. Do not reuse offensive spoofing/jamming setup details.",
    ),
    SourceSpec(
        dataset_id="aerpaw_dataset_12",
        title="AERPAW Dataset-12: Rural air-to-ground channel measurements at 3.3 GHz",
        source_url="https://aerpaw.org/dataset/uav-based-signal-data-collected-at-varying-altitudes-and-sampling-rates-for-wireless-communication-studies/",
        source_kind="dryad_api_plus_html",
        api_url="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.2z34tmpvv",
        sdot_use=[
            "UAV RSS/link-health feature-range calibration",
            "GPS/RSS timestamp alignment and bearer-health model reference",
        ],
        ingestion_role="best_link_health_feature_range_candidate",
        caveat="Large 150GB+ IQ archive; use metadata and README first, not bulk download.",
    ),
    SourceSpec(
        dataset_id="zenodo_gnss_jamming_spoofing_meaconing_2025",
        title="GNSS Dataset Under Jamming, Spoofing, and Meaconing Conditions",
        source_url="https://zenodo.org/records/15911359",
        source_kind="zenodo_record_api",
        api_url="https://zenodo.org/api/records/15911359",
        sdot_use=[
            "GNSS attack-condition taxonomy",
            "UBX/RINEX/RF-monitoring/navigation-solution schema reference",
        ],
        ingestion_role="small_readme_and_taxonomy_reference",
        caveat="Record currently exposes a small README through Zenodo; external/raw resources should be checked manually before use.",
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    return datetime.now(KST).strftime("%Y%m%d_%H%M%S")


def fetch(url: str, timeout: int = 25) -> tuple[int, str | None, bytes]:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.headers.get("content-type"), response.read()


def fetch_json(url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        status, content_type, payload = fetch(url)
        data = json.loads(payload.decode("utf-8", errors="replace"))
        return data, {"status": "passed", "http_status": status, "content_type": content_type, "bytes": len(payload)}
    except urllib.error.HTTPError as exc:
        return None, {"status": "failed", "http_status": exc.code, "detail": f"HTTPError {exc.code}: {exc.reason}"}
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "failed", "detail": f"{type(exc).__name__}: {exc}"}


def fetch_text(url: str) -> tuple[str | None, dict[str, Any]]:
    try:
        status, content_type, payload = fetch(url)
        return payload.decode("utf-8", errors="replace"), {
            "status": "passed",
            "http_status": status,
            "content_type": content_type,
            "bytes": len(payload),
        }
    except urllib.error.HTTPError as exc:
        return None, {"status": "failed", "http_status": exc.code, "detail": f"HTTPError {exc.code}: {exc.reason}"}
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "failed", "detail": f"{type(exc).__name__}: {exc}"}


def human_size(size: int | float | None) -> str | None:
    if size is None:
        return None
    value = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return None


def textify(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def mendeley_inventory(spec: SourceSpec) -> dict[str, Any]:
    data, check = fetch_json(spec.api_url)
    if not data:
        return {"source_check": check, "inventory_status": "failed"}

    files = data.get("files", [])
    total_size = data.get("size") or sum(file.get("size") or 0 for file in files if isinstance(file, dict))
    file_summaries = []
    for file in files[:20]:
        details = file.get("content_details") or {}
        file_summaries.append(
            {
                "filename": file.get("filename"),
                "size_bytes": file.get("size") or details.get("size"),
                "size_human": human_size(file.get("size") or details.get("size")),
                "content_type": details.get("content_type"),
                "file_id": file.get("id"),
                "has_download_url": bool(details.get("download_url")),
                "status": file.get("status"),
            }
        )

    return {
        "source_check": check,
        "inventory_status": "passed",
        "doi": (data.get("doi") or {}).get("id") if isinstance(data.get("doi"), dict) else None,
        "license": (data.get("data_licence") or {}).get("short_name"),
        "publication_date": data.get("publish_date"),
        "repository_size_bytes": total_size,
        "repository_size_human": human_size(total_size),
        "file_count": len(files),
        "sample_files": file_summaries,
        "feature_terms": extract_terms(data.get("description", "")),
        "structure_notes": [
            "Dataset is split into raw clean-data parts and a processed/attack-condition part.",
            "Public description identifies normal, jamming-affected, and spoofing-affected receiver scenarios.",
            "Description references five constellations and multiple signal bands; treat as receiver-feature calibration, not drone trajectory truth.",
        ],
        "candidate_sdot_fields": [
            "cn0_dbhz_mean",
            "doppler_shift_proxy",
            "pseudorange_residual_proxy",
            "carrier_phase_quality_proxy",
            "hdop",
            "vdop",
            "receiver_position_error_proxy",
            "gnss_condition_label",
        ],
        "download_policy": "Optional small single-zip inspection only after selecting a concrete feature table. Never bulk-download the full 8.58GB during demo prep.",
        "recommended_ingestion": "Use API metadata and selected small zip only after choosing a specific feature table; avoid bulk download.",
    }


def extract_dryad_files(page_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r'<a[^>]+class="js-individual-dl"[^>]+href="([^"]+)"[^>]*>.*?</i>(.*?)</a>', page_text, flags=re.I | re.S):
        href, name_html = match.groups()
        end = min(len(page_text), match.end() + 900)
        near = page_text[match.end() : end]
        size_match = re.search(r"([0-9]+(?:\.[0-9]+)?\s*(?:KB|MB|GB|TB|B))", textify(near), flags=re.I)
        rows.append(
            {
                "filename": textify(name_html),
                "size_human": size_match.group(1) if size_match else None,
                "download_path": href,
            }
        )
    return rows


def dryad_inventory(spec: SourceSpec) -> dict[str, Any]:
    data, api_check = fetch_json(spec.api_url)
    page_text, page_check = fetch_text("https://datadryad.org/stash/dataset/doi:10.5061/dryad.2z34tmpvv?public=true")
    if not data:
        return {"source_check": api_check, "inventory_status": "failed"}

    files = extract_dryad_files(page_text or "")
    return {
        "source_check": api_check,
        "html_check": page_check,
        "inventory_status": "passed",
        "doi": data.get("identifier"),
        "license": data.get("license"),
        "publication_date": data.get("publicationDate"),
        "repository_size_bytes": data.get("storageSize"),
        "repository_size_human": human_size(data.get("storageSize")),
        "file_count": len(files),
        "sample_files": files[:10],
        "keywords": data.get("keywords", []),
        "feature_terms": extract_terms(" ".join([data.get("abstract", ""), data.get("methods", "")])),
        "structure_notes": [
            "UAV follows repeated trajectories at 40m, 70m, and 100m altitude.",
            "40m runs include 5MHz, 10MHz, and 20MHz sampling rates.",
            "GPS coordinates are 1Hz; radio measurements are timestamped separately and aligned by interpolation.",
            "Data uses SigMF metadata/data files and includes RSS measurements from fixed nodes LW1-LW5.",
            "Dryad page exposes multiple file blocks; use the current Dryad API record as the authoritative dataset metadata.",
        ],
        "candidate_sdot_fields": [
            "rss_dbm",
            "rss1_dbm",
            "rss2_dbm",
            "snr_bucket",
            "gps_x",
            "gps_y",
            "gps_z",
            "interpolated_mx",
            "interpolated_my",
            "interpolated_mz",
            "altitude_m",
            "sampling_rate_hz",
        ],
        "download_policy": "Use Dryad API/methods text and README-level metadata first. Avoid 150GB archive unless a small subset can be isolated.",
        "recommended_ingestion": "Use README/API metadata now. Only ingest GPS/RSS metadata if a small subset can be isolated; do not bulk download 150GB archive.",
    }


def zenodo_inventory(spec: SourceSpec) -> dict[str, Any]:
    data, check = fetch_json(spec.api_url)
    if not data:
        return {"source_check": check, "inventory_status": "failed"}

    files = data.get("files", [])
    file_summaries = []
    for file in files:
        size = file.get("filesize") or file.get("size")
        file_summaries.append(
            {
                "filename": file.get("key"),
                "size_bytes": size,
                "size_human": human_size(size),
                "content_link_present": bool((file.get("links") or {}).get("self")),
            }
        )
    return {
        "source_check": check,
        "inventory_status": "passed",
        "doi": data.get("doi"),
        "license": ((data.get("metadata") or {}).get("license") or {}).get("id")
        if isinstance((data.get("metadata") or {}).get("license"), dict)
        else (data.get("metadata") or {}).get("license"),
        "publication_date": (data.get("metadata") or {}).get("publication_date"),
        "repository_size_bytes": sum(file.get("filesize") or file.get("size") or 0 for file in files),
        "repository_size_human": human_size(sum(file.get("filesize") or file.get("size") or 0 for file in files)),
        "file_count": len(files),
        "sample_files": file_summaries,
        "feature_terms": extract_terms(json.dumps(data.get("metadata", {}), ensure_ascii=False)),
        "structure_notes": [
            "Zenodo record exposes a small README through the record API.",
            "README describes scenario-level metadata and GNSS monitoring/navigation files such as scenario metadata, RF monitoring, PVT, RINEX, and UBX-style raw receiver data.",
            "Use as taxonomy/schema reference unless raw-resource access is separately validated.",
        ],
        "candidate_sdot_fields": [
            "attack_condition_label",
            "receiver_mobility_label",
            "mon_rf_quality_proxy",
            "nav_pvt_position_proxy",
            "rinex_observation_ref",
            "scenario_metadata_ref",
        ],
        "download_policy": "Safe to use README/taxonomy. Do not assume raw scenario files are locally available from the Zenodo record.",
        "recommended_ingestion": "Ingest README/taxonomy only unless external raw-resource access is explicitly needed.",
    }


def extract_terms(text: str) -> list[str]:
    terms = [
        "C/N0",
        "DOP",
        "Doppler",
        "pseudorange",
        "carrier phase",
        "GPS",
        "GNSS",
        "jamming",
        "spoofing",
        "meaconing",
        "RSS",
        "SigMF",
        "IQ",
        "trajectory",
        "altitude",
        "sampling rate",
        "packet loss",
        "SNR",
    ]
    lower = text.lower()
    return [term for term in terms if term.lower() in lower]


def inventory_for(spec: SourceSpec) -> dict[str, Any]:
    if spec.source_kind == "mendeley_public_api":
        details = mendeley_inventory(spec)
    elif spec.source_kind == "dryad_api_plus_html":
        details = dryad_inventory(spec)
    elif spec.source_kind == "zenodo_record_api":
        details = zenodo_inventory(spec)
    else:
        details = {"inventory_status": "failed", "source_check": {"status": "failed", "detail": "unsupported source_kind"}}

    return {
        "dataset_id": spec.dataset_id,
        "title": spec.title,
        "source_url": spec.source_url,
        "api_url": spec.api_url,
        "source_kind": spec.source_kind,
        "sdot_use": spec.sdot_use,
        "ingestion_role": spec.ingestion_role,
        "caveat": spec.caveat,
        **details,
    }


def write_markdown(run_dir: Path, report: dict[str, Any]) -> Path:
    path = run_dir / "priority_dataset_inventory_report.md"
    lines = [
        "# S-DOT Drone Priority Dataset Inventory",
        "",
        f"- Run ID: `{report['run_id']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- Sources inspected: {report['summary']['source_count']}",
        f"- Passed: {report['summary']['passed']}",
        f"- Failed: {report['summary']['failed']}",
        "- Scope: metadata, file inventory, and dataset descriptions only; no raw source data downloaded.",
        "",
        "## Summary",
        "",
        "| Dataset | Status | Size | Files | Role | Next Action |",
        "|---|---|---:|---:|---|---|",
    ]
    for item in report["results"]:
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                item["dataset_id"],
                item.get("inventory_status"),
                item.get("repository_size_human") or "unknown",
                item.get("file_count", "unknown"),
                item["ingestion_role"],
                item.get("recommended_ingestion", "Review manually."),
            )
        )

    lines.extend(["", "## Details", ""])
    for item in report["results"]:
        lines.extend(
            [
                f"### {item['dataset_id']}",
                "",
                f"- Title: {item['title']}",
                f"- Source: {item['source_url']}",
                f"- DOI/license: {item.get('doi') or 'unknown'} / {item.get('license') or 'unknown'}",
                f"- S-DOT use: {'; '.join(item['sdot_use'])}",
                f"- Caveat: {item['caveat']}",
                f"- Download policy: {item.get('download_policy') or 'Review manually.'}",
                f"- Feature terms found: {', '.join(item.get('feature_terms') or []) or 'none extracted'}",
                f"- Candidate S-DOT fields: {', '.join(item.get('candidate_sdot_fields') or []) or 'none'}",
                "",
                "Structure notes:",
                "",
            ]
        )
        for note in item.get("structure_notes") or ["none"]:
            lines.append(f"- {note}")
        lines.extend(
            [
                "",
                "Sample files:",
                "",
            ]
        )
        sample_files = item.get("sample_files") or []
        if not sample_files:
            lines.append("- none")
        else:
            for file in sample_files[:8]:
                lines.append(f"- `{file.get('filename')}` ({file.get('size_human') or 'unknown size'})")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    rid = run_id()
    run_dir = OUT_ROOT / rid
    run_dir.mkdir(parents=True, exist_ok=True)

    results = [inventory_for(spec) for spec in SOURCES]
    summary = {
        "source_count": len(results),
        "passed": sum(1 for item in results if item.get("inventory_status") == "passed"),
        "failed": sum(1 for item in results if item.get("inventory_status") == "failed"),
    }
    report = {
        "run_id": rid,
        "checked_at": now_iso(),
        "summary": summary,
        "results": results,
        "safety_boundary": [
            "No raw RF/IQ/UBX/RINEX or large zip data downloaded.",
            "Use public datasets for defensive feature calibration and citation only.",
            "Keep end-to-end mission timelines synthetic.",
        ],
    }

    report_path = run_dir / "priority_dataset_inventory_report.json"
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

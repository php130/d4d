#!/usr/bin/env python3
"""Slow arXiv retry for S-DOT drone literature topics that hit rate limits."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
BASE_DIR = PROJECT_ROOT / "03_data" / "processed" / "literature_sdot_drone"
RESEARCH_DIR = PROJECT_ROOT / "01_research" / "literature" / "sdot_drone_research"

RETRY_TOPICS = [
    {
        "topic_id": "uav_networks_ddil_dtn",
        "label": "UAV networks, DDIL, DTN, intermittent links",
        "queries": [
            '"UAV networks" delay tolerant network',
            '"drone network" intermittent connectivity',
            '"UAV communication" "packet loss" "edge computing"',
            '"tactical network" UAV "delay tolerant"',
            '"disconnected intermittent limited" network UAV',
        ],
    },
    {
        "topic_id": "anti_jamming_resilient_uav_comms",
        "label": "Resilient UAV communications under jamming",
        "queries": [
            '"UAV communication" jamming detection',
            '"anti-jamming" UAV communication survey',
            '"unmanned aerial vehicle" "communication jamming"',
            '"UAV" "radio frequency interference" communication',
            '"resilient communications" UAV jamming',
        ],
    },
    {
        "topic_id": "edge_ai_compression_video",
        "label": "Edge AI / compression / video semantic transmission",
        "queries": [
            '"edge AI" UAV video compression',
            '"semantic video transmission" wireless',
            '"adaptive video transmission" UAV edge',
            '"object-level" video compression edge intelligence',
            '"event-based" data transmission sensor networks UAV',
        ],
    },
    {
        "topic_id": "uav_sensor_fusion_tracking",
        "label": "UAV sensor fusion and tracking",
        "queries": [
            '"UAV" "multi-sensor fusion" tracking',
            '"drone" "sensor fusion" "situational awareness"',
            '"UAV" "EO IR" "RF" "sensor fusion"',
            '"multi-UAV" "sensor fusion" "target tracking"',
        ],
    },
    {
        "topic_id": "uav_digital_twin_simulation",
        "label": "UAV simulation / digital twin / 3D validation",
        "queries": [
            '"UAV" digital twin simulation',
            '"drone" "digital twin" "simulation"',
            '"UAV" "3D simulation" "autonomous navigation"',
            '"unmanned aerial vehicle" "simulation environment" "sensor data"',
        ],
    },
    {
        "topic_id": "provenance_trust_c2",
        "label": "Provenance, trust, C2, decision support",
        "queries": [
            '"provenance" "sensor fusion" decision support',
            '"trust management" "sensor fusion" UAV',
            '"command and control" UAV sensor fusion decision support',
            '"common operational picture" UAV sensor fusion',
        ],
    },
]

KEY_TERMS = {
    "semantic communication": 8,
    "uav": 7,
    "unmanned aerial vehicle": 7,
    "drone": 6,
    "gnss": 7,
    "gps": 5,
    "jamming": 8,
    "spoofing": 8,
    "kalman": 6,
    "sensor fusion": 5,
    "edge computing": 4,
    "digital twin": 3,
    "delay tolerant": 5,
    "intermittent": 4,
    "provenance": 4,
    "command and control": 4,
}


def now_version() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())[:180]


def stable_id(record: dict[str, Any]) -> str:
    seed = record.get("url") or record.get("title")
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def relevance_score(record: dict[str, Any]) -> int:
    text = f" {record.get('title','')} {record.get('abstract','')} ".lower()
    score = 2
    year = int(record.get("year") or 0)
    if year >= 2025:
        score += 5
    elif year >= 2022:
        score += 4
    elif year >= 2018:
        score += 3
    for term, points in KEY_TERMS.items():
        if term in text:
            score += points
    return score


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-SDOT-drone-arxiv-retry/0.1"})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read().decode("utf-8", errors="replace")


def normalize_arxiv(entry: ET.Element, topic: dict[str, Any], query: str) -> dict[str, Any]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    title = clean_text(entry.findtext("a:title", namespaces=ns))
    abstract = clean_text(entry.findtext("a:summary", namespaces=ns))
    authors = [clean_text(author.findtext("a:name", namespaces=ns)) for author in entry.findall("a:author", ns)]
    published = entry.findtext("a:published", namespaces=ns) or ""
    arxiv_id = entry.findtext("a:id", namespaces=ns) or ""
    categories = [cat.attrib.get("term", "") for cat in entry.findall("a:category", ns)]
    record = {
        "id": "",
        "source": "arXiv",
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "matched_topics": [topic["topic_id"]],
        "query": query,
        "openalex_id": "",
        "doi": "",
        "title": title,
        "authors": [a for a in authors if a],
        "year": published[:4] if published else "",
        "publication_date": published[:10],
        "url": arxiv_id,
        "is_open_access": True,
        "cited_by_count": 0,
        "concepts": categories,
        "abstract": abstract,
        "referenced_works": [],
        "related_works": [],
    }
    record["id"] = stable_id(record)
    record["relevance_score"] = relevance_score(record)
    return record


def fetch(topic: dict[str, Any], max_results: int, delay: float) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records = []
    failures = []
    for query in topic["queries"]:
        params = {
            "search_query": f"all:{query}",
            "start": "0",
            "max_results": str(max_results),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        try:
            root = ET.fromstring(request_text(url))
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                records.append(normalize_arxiv(entry, topic, query))
        except Exception as exc:  # noqa: BLE001
            failures.append({"topic_id": topic["topic_id"], "query": query, "error": str(exc)})
        time.sleep(delay)
    return records, failures


def key(record: dict[str, Any]) -> str:
    return record.get("doi") or record.get("url") or normalize_title(record.get("title", "")) or record["id"]


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = ["id", "source", "topic_id", "topic_label", "query", "title", "authors", "year", "publication_date", "url", "relevance_score", "concepts", "abstract"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, "") for field in fields}
            row["authors"] = "; ".join(record.get("authors", []))
            row["concepts"] = "; ".join(record.get("concepts", []))
            writer.writerow(row)


def write_queue(path: Path, records: list[dict[str, Any]], limit: int) -> None:
    lines = ["# S-DOT Drone arXiv Retry Queue", "", f"- Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    for idx, record in enumerate(records[:limit], 1):
        lines += [
            f"## {idx}. {record['title']}",
            "",
            f"- Topic: {record['topic_label']}",
            f"- Year: {record.get('year','')}",
            f"- Score: {record.get('relevance_score', 0)}",
            f"- URL: {record.get('url','')}",
            f"- Authors: {', '.join(record.get('authors', [])[:5])}",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument("--delay", type=float, default=4.0)
    parser.add_argument("--queue-limit", type=int, default=80)
    args = parser.parse_args()

    base_latest = json.loads((BASE_DIR / "latest.json").read_text(encoding="utf-8"))
    base_records = json.loads(Path(base_latest["outputs"]["records_json"]).read_text(encoding="utf-8"))
    snowball_path = BASE_DIR / "latest_snowball.json"
    if snowball_path.exists():
        snowball_latest = json.loads(snowball_path.read_text(encoding="utf-8"))
        merged_records = json.loads(Path(snowball_latest["outputs"]["merged_json"]).read_text(encoding="utf-8"))
    else:
        merged_records = base_records

    existing = {key(record) for record in merged_records}
    raw_records = []
    failures = []
    for topic in RETRY_TOPICS:
        topic_records, topic_failures = fetch(topic, args.max_results, args.delay)
        raw_records.extend(topic_records)
        failures.extend(topic_failures)

    new_by_key = {}
    for record in raw_records:
        k = key(record)
        if k in existing:
            continue
        current = new_by_key.get(k)
        if not current or record["relevance_score"] > current["relevance_score"]:
            new_by_key[k] = record
    new_records = sorted(new_by_key.values(), key=lambda r: (r["relevance_score"], int(r.get("year") or 0)), reverse=True)

    version = now_version()
    run_dir = BASE_DIR / f"arxiv_retry_{version}"
    run_dir.mkdir(parents=True, exist_ok=True)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    out_json = run_dir / "sdot_drone_arxiv_retry_new_records.json"
    out_csv = run_dir / "sdot_drone_arxiv_retry_new_records.csv"
    queue = RESEARCH_DIR / f"sdot_drone_arxiv_retry_queue_{version}.md"
    summary_path = run_dir / "arxiv_retry_summary.json"

    out_json.write_text(json.dumps(new_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(out_csv, new_records)
    write_queue(queue, new_records, args.queue_limit)
    summary = {
        "version": f"arxiv_retry_{version}",
        "generated_at": datetime.now().isoformat(),
        "raw_records": len(raw_records),
        "new_records": len(new_records),
        "failure_count": len(failures),
        "failures": failures,
        "outputs": {"new_json": str(out_json), "new_csv": str(out_csv), "queue": str(queue)},
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BASE_DIR / "latest_arxiv_retry.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (BASE_DIR / "VERSIONS.md").open("a", encoding="utf-8") as f:
        f.write(f"- arxiv_retry_{version}: raw {len(raw_records)}, new {len(new_records)}, failures {len(failures)}, outputs `{run_dir}`\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

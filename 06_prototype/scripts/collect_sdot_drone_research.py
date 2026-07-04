#!/usr/bin/env python3
"""Collect drone-first S-DOT research metadata.

Sources:
- OpenAlex Works API
- arXiv API

The script stores metadata only. It does not download or redistribute full
papers. The output is intended to seed reading queues and technical synthesis
for the D4D S-DOT drone semantic transmission direction.
"""

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
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
OUT_DIR = PROJECT_ROOT / "03_data" / "processed" / "literature_sdot_drone"
RESEARCH_DIR = PROJECT_ROOT / "01_research" / "literature" / "sdot_drone_research"

OPENALEX_SELECT = ",".join(
    [
        "id",
        "doi",
        "display_name",
        "publication_year",
        "publication_date",
        "authorships",
        "primary_location",
        "open_access",
        "cited_by_count",
        "concepts",
        "abstract_inverted_index",
        "referenced_works",
        "related_works",
    ]
)

TOPICS = [
    {
        "topic_id": "semantic_communications_uav_edge",
        "label": "Semantic communications for UAV / edge",
        "weight": 6,
        "queries": [
            '"semantic communication" UAV edge intelligence',
            '"semantic communications" unmanned aerial vehicle',
            '"task-oriented semantic communication" UAV',
            '"semantic communication" image transmission wireless edge',
            '"semantic communication" "Internet of Drones"',
        ],
    },
    {
        "topic_id": "uav_gnss_denied_navigation",
        "label": "UAV GNSS-denied navigation",
        "weight": 6,
        "queries": [
            '"UAV" "GNSS-denied" navigation survey',
            '"GPS-denied" UAV navigation "visual inertial"',
            '"UAV" "GPS denied" "SLAM"',
            '"unmanned aerial vehicle" "GNSS denied" "sensor fusion"',
            '"drone" "GPS-denied" navigation "Kalman"',
        ],
    },
    {
        "topic_id": "gnss_jamming_spoofing_detection",
        "label": "GNSS jamming / spoofing detection and integrity",
        "weight": 7,
        "queries": [
            '"GNSS jamming detection" UAV',
            '"GNSS spoofing detection" UAV',
            '"GPS spoofing detection" inertial measurement unit',
            '"GNSS interference detection" "Kalman filter"',
            '"GNSS integrity monitoring" residual "Kalman"',
            '"receiver autonomous integrity monitoring" UAV GNSS',
        ],
    },
    {
        "topic_id": "kalman_residual_integrity",
        "label": "Kalman residual / NIS / integrity monitoring",
        "weight": 5,
        "queries": [
            '"normalized innovation squared" Kalman filter fault detection',
            '"innovation-based" fault detection "Kalman filter" navigation',
            '"residual-based" anomaly detection "Kalman filter" UAV',
            '"state estimation" "uncertainty ellipse" UAV tracking',
        ],
    },
    {
        "topic_id": "uav_networks_ddil_dtn",
        "label": "UAV networks, DDIL, DTN, intermittent links",
        "weight": 5,
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
        "weight": 5,
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
        "weight": 4,
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
        "weight": 4,
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
        "weight": 3,
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
        "weight": 3,
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
    "semantic communications": 8,
    "task-oriented": 5,
    "goal-oriented": 5,
    "uav": 7,
    "unmanned aerial vehicle": 7,
    "drone": 6,
    "gnss": 7,
    "gps": 5,
    "jamming": 8,
    "spoofing": 8,
    "interference": 4,
    "kalman": 6,
    "innovation": 4,
    "normalized innovation": 7,
    "residual": 5,
    "integrity monitoring": 6,
    "raim": 6,
    "slam": 5,
    "visual inertial": 6,
    "gps-denied": 7,
    "gnss-denied": 7,
    "edge intelligence": 5,
    "edge computing": 4,
    "delay tolerant": 5,
    "intermittent": 4,
    "sensor fusion": 5,
    "uncertainty": 4,
    "digital twin": 3,
    "common operational picture": 4,
    "command and control": 4,
    "provenance": 4,
}

NEGATIVE_TERMS = {
    "medical": 4,
    "patient": 4,
    "agriculture": 3,
    "crop": 3,
    "finance": 3,
    "metaverse": 2,
    "blockchain": 2,
}


def now_version() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())[:180]


def reconstruct_abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    pairs = []
    for word, positions in inverted.items():
        for pos in positions:
            pairs.append((int(pos), word))
    return " ".join(word for _, word in sorted(pairs))


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-SDOT-drone-research/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-SDOT-drone-research/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def stable_id(record: dict[str, Any]) -> str:
    seed = record.get("doi") or record.get("openalex_id") or record.get("url") or normalize_title(record.get("title", ""))
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def landing_url(location: dict | None, doi: str, fallback: str) -> str:
    if location:
        if location.get("landing_page_url"):
            return location["landing_page_url"]
        if location.get("pdf_url"):
            return location["pdf_url"]
    if doi:
        return f"https://doi.org/{doi}"
    return fallback


def relevance_score(record: dict[str, Any], topic_weight: int = 0) -> int:
    text = f" {record.get('title','')} {record.get('abstract','')} ".lower()
    score = topic_weight
    year = int(record.get("year") or 0)
    cited = int(record.get("cited_by_count") or 0)
    if year >= 2025:
        score += 5
    elif year >= 2022:
        score += 4
    elif year >= 2018:
        score += 3
    elif year >= 2012:
        score += 1
    if record.get("is_open_access"):
        score += 2
    if cited >= 1000:
        score += 5
    elif cited >= 300:
        score += 4
    elif cited >= 100:
        score += 3
    elif cited >= 25:
        score += 2
    elif cited >= 5:
        score += 1
    for term, points in KEY_TERMS.items():
        if term in text:
            score += points
    for term, penalty in NEGATIVE_TERMS.items():
        if term in text and not any(anchor in text for anchor in ["uav", "drone", "gnss", "tactical", "wireless"]):
            score -= penalty
    return score


def normalize_openalex(work: dict[str, Any], topic: dict[str, Any], query: str) -> dict[str, Any]:
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    authors = []
    for authorship in work.get("authorships", [])[:8]:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            authors.append(author["display_name"])
    concepts = [c.get("display_name") for c in work.get("concepts", [])[:12] if c.get("display_name")]
    location = work.get("primary_location") or {}
    record = {
        "id": "",
        "source": "OpenAlex",
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "query": query,
        "openalex_id": work.get("id", ""),
        "doi": doi,
        "title": clean_text(work.get("display_name")),
        "authors": authors,
        "year": work.get("publication_year") or "",
        "publication_date": work.get("publication_date") or "",
        "url": landing_url(location, doi, work.get("id", "")),
        "is_open_access": bool((work.get("open_access") or {}).get("is_oa")),
        "cited_by_count": work.get("cited_by_count") or 0,
        "concepts": concepts,
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "referenced_works": work.get("referenced_works") or [],
        "related_works": work.get("related_works") or [],
    }
    record["id"] = stable_id(record)
    record["relevance_score"] = relevance_score(record, int(topic.get("weight", 0)))
    return record


def normalize_arxiv(entry: ET.Element, topic: dict[str, Any], query: str) -> dict[str, Any]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    title = clean_text(entry.findtext("a:title", namespaces=ns))
    abstract = clean_text(entry.findtext("a:summary", namespaces=ns))
    authors = [clean_text(author.findtext("a:name", namespaces=ns)) for author in entry.findall("a:author", ns)]
    published = entry.findtext("a:published", namespaces=ns) or ""
    year = published[:4] if published else ""
    arxiv_id = entry.findtext("a:id", namespaces=ns) or ""
    categories = [cat.attrib.get("term", "") for cat in entry.findall("a:category", ns)]
    record = {
        "id": "",
        "source": "arXiv",
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "query": query,
        "openalex_id": "",
        "doi": "",
        "title": title,
        "authors": [a for a in authors if a],
        "year": year,
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
    record["relevance_score"] = relevance_score(record, int(topic.get("weight", 0)))
    return record


def fetch_openalex(topic: dict[str, Any], per_query: int) -> list[dict[str, Any]]:
    records = []
    for query in topic["queries"]:
        params = {
            "search": query,
            "per-page": str(per_query),
            "select": OPENALEX_SELECT,
            "sort": "cited_by_count:desc",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            data = request_json(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] OpenAlex failed topic={topic['topic_id']} query={query!r}: {exc}")
            continue
        for work in data.get("results", []):
            records.append(normalize_openalex(work, topic, query))
        time.sleep(0.15)
    return records


def fetch_arxiv(topic: dict[str, Any], per_query: int) -> list[dict[str, Any]]:
    records = []
    for query in topic["queries"]:
        params = {
            "search_query": f"all:{query}",
            "start": "0",
            "max_results": str(per_query),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        try:
            text = request_text(url)
            root = ET.fromstring(text)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] arXiv failed topic={topic['topic_id']} query={query!r}: {exc}")
            continue
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            records.append(normalize_arxiv(entry, topic, query))
        time.sleep(0.35)
    return records


def dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get("doi") or normalize_title(record.get("title", "")) or record["id"]
        existing = best.get(key)
        if not existing or record["relevance_score"] > existing["relevance_score"]:
            best[key] = record
        elif existing:
            topics = set(existing.get("matched_topics", [existing["topic_id"]]))
            topics.add(record["topic_id"])
            existing["matched_topics"] = sorted(topics)
    output = []
    for record in best.values():
        record.setdefault("matched_topics", [record["topic_id"]])
        output.append(record)
    return sorted(output, key=lambda item: (item["relevance_score"], int(item.get("cited_by_count") or 0), int(item.get("year") or 0)), reverse=True)


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "id",
        "source",
        "topic_id",
        "topic_label",
        "matched_topics",
        "query",
        "title",
        "authors",
        "year",
        "publication_date",
        "doi",
        "url",
        "is_open_access",
        "cited_by_count",
        "relevance_score",
        "concepts",
        "abstract",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, "") for field in fields}
            row["authors"] = "; ".join(record.get("authors", []))
            row["concepts"] = "; ".join(record.get("concepts", []))
            row["matched_topics"] = "; ".join(record.get("matched_topics", []))
            writer.writerow(row)


def write_markdown_catalog(path: Path, records: list[dict[str, Any]], limit: int) -> None:
    by_topic: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_topic[record["topic_id"]].append(record)
    lines = [
        "# S-DOT Drone Research Catalog",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Total deduped records: {len(records)}",
        f"- Catalog display limit per topic: {limit}",
        "",
    ]
    for topic in TOPICS:
        topic_records = by_topic.get(topic["topic_id"], [])
        lines += [
            f"## {topic['label']}",
            "",
            f"Records: {len(topic_records)}",
            "",
        ]
        for idx, record in enumerate(topic_records[:limit], 1):
            authors = ", ".join(record.get("authors", [])[:3])
            year = record.get("year") or "n.d."
            lines += [
                f"{idx}. **{record['title']}** ({year})",
                f"   - Source: {record['source']} | score {record['relevance_score']} | cited {record.get('cited_by_count', 0)}",
                f"   - Authors: {authors}",
                f"   - URL: {record.get('url','')}",
                "",
            ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_reading_queue(path: Path, records: list[dict[str, Any]], limit: int) -> None:
    lines = [
        "# S-DOT Drone First Reading Queue",
        "",
        "Priority reading list for the drone/GNSS/link degradation S-DOT direction.",
        "",
    ]
    for idx, record in enumerate(records[:limit], 1):
        abstract = clean_text(record.get("abstract", ""))
        if len(abstract) > 520:
            abstract = abstract[:520].rsplit(" ", 1)[0] + "..."
        lines += [
            f"## {idx}. {record['title']}",
            "",
            f"- Source: {record['source']}",
            f"- Topic: {record['topic_label']}",
            f"- Year: {record.get('year','')}",
            f"- Relevance score: {record['relevance_score']}",
            f"- Citations: {record.get('cited_by_count', 0)}",
            f"- URL: {record.get('url','')}",
            f"- Authors: {', '.join(record.get('authors', [])[:6])}",
            "",
            f"{abstract}",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_topic_summary(path: Path, records: list[dict[str, Any]]) -> None:
    topic_counts = Counter(record["topic_id"] for record in records)
    source_counts = Counter(record["source"] for record in records)
    year_counts = Counter(str(record.get("year") or "unknown") for record in records)
    top_terms = Counter()
    for record in records:
        text = f"{record.get('title','')} {record.get('abstract','')}".lower()
        for term in KEY_TERMS:
            if term in text:
                top_terms[term] += 1
    payload = {
        "generated_at": datetime.now().isoformat(),
        "total_records": len(records),
        "source_counts": dict(source_counts),
        "topic_counts": dict(topic_counts),
        "year_counts_top": dict(year_counts.most_common(15)),
        "key_term_counts_top": dict(top_terms.most_common(30)),
        "top_records": [
            {
                "title": r["title"],
                "year": r.get("year"),
                "source": r["source"],
                "topic_id": r["topic_id"],
                "relevance_score": r["relevance_score"],
                "url": r.get("url"),
            }
            for r in records[:30]
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openalex-per-query", type=int, default=35)
    parser.add_argument("--arxiv-per-query", type=int, default=12)
    parser.add_argument("--reading-limit", type=int, default=100)
    args = parser.parse_args()

    version = now_version()
    run_dir = OUT_DIR / version
    run_dir.mkdir(parents=True, exist_ok=True)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    raw_records: list[dict[str, Any]] = []
    for topic in TOPICS:
        print(f"[INFO] topic={topic['topic_id']} OpenAlex")
        raw_records.extend(fetch_openalex(topic, args.openalex_per_query))
        print(f"[INFO] topic={topic['topic_id']} arXiv")
        raw_records.extend(fetch_arxiv(topic, args.arxiv_per_query))

    records = dedupe(raw_records)

    all_json = run_dir / "sdot_drone_literature_records.json"
    all_csv = run_dir / "sdot_drone_literature_records.csv"
    queue_md = RESEARCH_DIR / f"sdot_drone_first_reading_queue_{version}.md"
    catalog_md = RESEARCH_DIR / f"sdot_drone_research_catalog_{version}.md"
    summary_json = run_dir / "sdot_drone_topic_summary.json"
    manifest = {
        "version": version,
        "generated_at": datetime.now().isoformat(),
        "topics": TOPICS,
        "raw_record_count": len(raw_records),
        "deduped_record_count": len(records),
        "outputs": {
            "records_json": str(all_json),
            "records_csv": str(all_csv),
            "topic_summary": str(summary_json),
            "reading_queue": str(queue_md),
            "catalog": str(catalog_md),
        },
        "sources": [
            "https://api.openalex.org/works",
            "https://export.arxiv.org/api/query",
        ],
    }

    all_json.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(all_csv, records)
    write_topic_summary(summary_json, records)
    write_reading_queue(queue_md, records, args.reading_limit)
    write_markdown_catalog(catalog_md, records, 20)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "latest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    versions_path = OUT_DIR / "VERSIONS.md"
    with versions_path.open("a", encoding="utf-8") as f:
        f.write(f"- {version}: raw {len(raw_records)}, deduped {len(records)}, outputs `{run_dir}`\n")

    print(json.dumps({
        "version": version,
        "raw_records": len(raw_records),
        "deduped_records": len(records),
        "run_dir": str(run_dir),
        "reading_queue": str(queue_md),
        "catalog": str(catalog_md),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Collect first-pass scholarly paper metadata for D4D research."""

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
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")


TOPICS = [
    {
        "topic_id": "T1_multi_uxv_control",
        "track_ids": ["T1"],
        "problem_ids": ["T1-001"],
        "label": "1인 다중 무인기 통제 / Multi-UxV control",
        "queries": [
            "multi UAV control human swarm autonomy",
            "human swarm interaction multi robot control unmanned systems cognitive load",
        ],
    },
    {
        "topic_id": "T1_terrain_aware_autonomy",
        "track_ids": ["T1"],
        "problem_ids": ["T1-002"],
        "label": "지형 인지형 자율성 / Terrain-aware autonomy",
        "queries": [
            "terrain aware UAV path planning GPS denied environment",
            "UAV path planning electronic warfare communication denied environment",
        ],
    },
    {
        "topic_id": "T1_counter_uas_sensor_fusion",
        "track_ids": ["T1"],
        "problem_ids": ["T1-003", "T1-005"],
        "label": "Counter-UAS 탐지·추적·요격",
        "queries": [
            "counter UAS drone detection RF EO IR radar sensor fusion",
            "autonomous drone interception target tracking counter unmanned aircraft systems",
        ],
    },
    {
        "topic_id": "T1_radio_silent_iff",
        "track_ids": ["T1"],
        "problem_ids": ["T1-006"],
        "label": "무선침묵 IFF / 저방출 피아식별",
        "queries": [
            "identification friend or foe UAV cryptographic challenge response replay attack",
            "radio silent authentication unmanned aerial vehicles challenge response protocol",
        ],
    },
    {
        "topic_id": "T2_fusion_intel_copilot",
        "track_ids": ["T2"],
        "problem_ids": ["T2-001"],
        "label": "멀티소스 융합 인텔 코파일럿",
        "queries": [
            "open source intelligence multi source fusion knowledge graph large language model",
            "OSINT intelligence analysis knowledge graph provenance citation LLM",
        ],
    },
    {
        "topic_id": "T2_cyber_threat_intelligence",
        "track_ids": ["T2"],
        "problem_ids": ["T2-003", "T2-004"],
        "label": "사이버 위협 인텔리전스 / 지식그래프 / 엔티티 해소",
        "queries": [
            "cyber threat intelligence knowledge graph entity resolution",
            "dark web threat intelligence credential exposure infostealer",
            "cyber threat intelligence ontology knowledge graph APT",
        ],
    },
    {
        "topic_id": "T2_air_isr_fusion",
        "track_ids": ["T2"],
        "problem_ids": ["T2-002"],
        "label": "공중 ISR 다중소스 융합",
        "queries": [
            "multi source ISR fusion aircraft satellite weather OSINT",
            "airborne ISR data fusion anomaly detection open source intelligence",
        ],
    },
    {
        "topic_id": "T3_sensor_fusion_cop",
        "track_ids": ["T3"],
        "problem_ids": ["T3-001", "T3-003"],
        "label": "센서퓨전 / 자연어 COP / C2",
        "queries": [
            "sensor fusion common operational picture command and control decision support",
            "multi domain command and control ontology sensor fusion",
        ],
    },
    {
        "topic_id": "T3_semantic_tactical_network",
        "track_ids": ["T3"],
        "problem_ids": ["T3-005"],
        "label": "전술망 시맨틱 전송 / 거부환경 통신",
        "queries": [
            "semantic communication tactical networks edge AI denied environment",
            "semantic communication wireless networks deep learning bandwidth constrained",
        ],
    },
    {
        "topic_id": "T3_sustainment_logistics",
        "track_ids": ["T3"],
        "problem_ids": ["T3-006"],
        "label": "지속지원 / 군수 C2 / 예측정비",
        "queries": [
            "military logistics sustainment predictive maintenance decision support",
            "resilient military supply chain logistics optimization denied environment",
        ],
    },
    {
        "topic_id": "T4_maritime_anomaly_ais",
        "track_ids": ["T4"],
        "problem_ids": ["T4-001", "T4-002"],
        "label": "AIS 기반 해상 이상탐지 / 회색지대 조기경보",
        "queries": [
            "AIS anomaly detection maritime domain awareness dark vessel",
            "maritime vessel trajectory anomaly detection AIS deep learning",
            "dark vessel detection SAR AIS fusion maritime surveillance",
        ],
    },
    {
        "topic_id": "T4_maritime_sensor_fusion",
        "track_ids": ["T4"],
        "problem_ids": ["T4-001", "T4-003"],
        "label": "해상 센서퓨전 / 무인 감시 자산",
        "queries": [
            "maritime surveillance sensor fusion EO IR radar sonar unmanned surface vehicle",
            "passive sonar anomaly detection maritime surveillance deep learning",
        ],
    },
    {
        "topic_id": "T5_wargame_ai_tutor",
        "track_ids": ["T5"],
        "problem_ids": ["T5-001", "T5-003"],
        "label": "AI 워게임 교관 / 의사결정 코치",
        "queries": [
            "wargaming artificial intelligence tutor after action review military training",
            "large language model wargame simulation decision support military training",
        ],
    },
    {
        "topic_id": "T5_on_device_tactical_ai",
        "track_ids": ["T5"],
        "problem_ids": ["T5-002"],
        "label": "온디바이스 전술 AI / 오프라인 RAG",
        "queries": [
            "on device large language model retrieval augmented generation offline",
            "edge AI tactical assistant offline RAG military decision support",
        ],
    },
    {
        "topic_id": "X_llm_reliability_provenance",
        "track_ids": ["T2", "T3", "T5"],
        "problem_ids": ["T2-001", "T3-001", "T5-002"],
        "label": "LLM 신뢰성 / citation / provenance / 평가",
        "queries": [
            "retrieval augmented generation citation provenance hallucination evaluation",
            "LLM agents tool use evaluation provenance question answering",
        ],
    },
]


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
    ]
)


def now_version() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-literature-seed/0.1 (mailto:none)"})
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-literature-seed/0.1 (mailto:none)"})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read().decode("utf-8", errors="replace")


def reconstruct_abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    pairs = []
    for word, positions in inverted.items():
        for pos in positions:
            pairs.append((pos, word))
    return " ".join(word for _, word in sorted(pairs))


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def stable_id(record: dict) -> str:
    seed = record.get("doi") or record.get("url") or record.get("title")
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def first_url(location: dict | None, doi: str, fallback: str = "") -> str:
    if location:
        landing = location.get("landing_page_url")
        pdf = location.get("pdf_url")
        if landing:
            return landing
        if pdf:
            return pdf
    if doi:
        return f"https://doi.org/{doi}"
    return fallback


def score_record(record: dict) -> int:
    year = int(record.get("year") or 0)
    citations = int(record.get("cited_by_count") or 0)
    score = 0
    if year >= 2024:
        score += 4
    elif year >= 2021:
        score += 3
    elif year >= 2018:
        score += 2
    elif year >= 2014:
        score += 1
    if record.get("is_open_access"):
        score += 2
    if citations >= 100:
        score += 3
    elif citations >= 30:
        score += 2
    elif citations >= 5:
        score += 1
    text = f"{record.get('title','')} {record.get('abstract','')}".lower()
    for term in ["survey", "review", "benchmark", "dataset", "knowledge graph", "sensor fusion", "anomaly detection"]:
        if term in text:
            score += 1
    return score


def normalize_openalex(work: dict, topic: dict, query: str) -> dict:
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    authors = []
    for authorship in work.get("authorships", [])[:8]:
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)
    concepts = [c.get("display_name") for c in work.get("concepts", [])[:8] if c.get("display_name")]
    primary_location = work.get("primary_location") or {}
    oa = work.get("open_access") or {}
    record = {
        "source": "OpenAlex",
        "source_id": work.get("id", ""),
        "doi": doi,
        "title": clean_text(work.get("display_name")),
        "authors": authors,
        "year": work.get("publication_year") or "",
        "publication_date": work.get("publication_date") or "",
        "url": first_url(primary_location, doi, work.get("id", "")),
        "pdf_url": (primary_location or {}).get("pdf_url") or "",
        "is_open_access": bool(oa.get("is_oa")),
        "cited_by_count": work.get("cited_by_count") or 0,
        "venue": ((primary_location.get("source") or {}).get("display_name") if primary_location else "") or "",
        "concepts": concepts,
        "abstract": clean_text(reconstruct_abstract(work.get("abstract_inverted_index"))),
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "track_ids": topic["track_ids"],
        "problem_ids": topic["problem_ids"],
        "query": query,
    }
    record["id"] = stable_id(record)
    record["priority_score"] = score_record(record)
    return record


def fetch_openalex(topic: dict, query: str, per_page: int) -> tuple[list[dict], dict]:
    params = {
        "search": query,
        "filter": "from_publication_date:2014-01-01",
        "per-page": str(per_page),
        "select": OPENALEX_SELECT,
        "sort": "cited_by_count:desc",
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = request_json(url)
    records = [normalize_openalex(work, topic, query) for work in data.get("results", [])]
    return records, {"url": url, "meta": data.get("meta", {})}


def normalize_arxiv_entry(entry: ET.Element, topic: dict, query: str) -> dict:
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
    abstract = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
    published = entry.findtext("atom:published", default="", namespaces=ns)
    year = published[:4] if published else ""
    authors = []
    for author in entry.findall("atom:author", ns)[:8]:
        name = author.findtext("atom:name", default="", namespaces=ns)
        if name:
            authors.append(clean_text(name))
    url = entry.findtext("atom:id", default="", namespaces=ns)
    pdf_url = ""
    for link in entry.findall("atom:link", ns):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href", "")
            break
    categories = [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns) if cat.attrib.get("term")]
    doi = entry.findtext("arxiv:doi", default="", namespaces=ns)
    record = {
        "source": "arXiv",
        "source_id": url.rsplit("/", 1)[-1],
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year,
        "publication_date": published[:10],
        "url": url,
        "pdf_url": pdf_url,
        "is_open_access": True,
        "cited_by_count": 0,
        "venue": "arXiv",
        "concepts": categories,
        "abstract": abstract,
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "track_ids": topic["track_ids"],
        "problem_ids": topic["problem_ids"],
        "query": query,
    }
    record["id"] = stable_id(record)
    record["priority_score"] = score_record(record)
    return record


def fetch_arxiv(topic: dict, query: str, per_page: int) -> tuple[list[dict], dict]:
    search_query = "all:" + " AND all:".join(query.split()[:8])
    params = {
        "search_query": search_query,
        "start": "0",
        "max_results": str(per_page),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    text = request_text(url)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    records = [normalize_arxiv_entry(entry, topic, query) for entry in entries]
    return records, {"url": url, "entry_count": len(records)}


def dedupe(records: list[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for record in records:
        key = (record.get("doi") or "").lower()
        if not key:
            title = re.sub(r"[^a-z0-9]+", "", record.get("title", "").lower())
            key = title[:120]
        if not key:
            key = record["id"]
        existing = by_key.get(key)
        if not existing:
            by_key[key] = record
            continue
        for field in ["topic_id", "topic_label", "query"]:
            existing[field] = existing.get(field) or record.get(field)
        existing["track_ids"] = sorted(set(existing.get("track_ids", []) + record.get("track_ids", [])))
        existing["problem_ids"] = sorted(set(existing.get("problem_ids", []) + record.get("problem_ids", [])))
        existing["priority_score"] = max(existing.get("priority_score", 0), record.get("priority_score", 0))
        if existing.get("source") != record.get("source"):
            existing["source"] = f"{existing.get('source')}+{record.get('source')}"
        if not existing.get("abstract") and record.get("abstract"):
            existing["abstract"] = record["abstract"]
        if not existing.get("pdf_url") and record.get("pdf_url"):
            existing["pdf_url"] = record["pdf_url"]
        if int(record.get("cited_by_count") or 0) > int(existing.get("cited_by_count") or 0):
            existing["cited_by_count"] = record.get("cited_by_count")
    return sorted(by_key.values(), key=lambda r: (r.get("priority_score", 0), int(r.get("cited_by_count") or 0)), reverse=True)


def write_csv(path: Path, records: list[dict]) -> None:
    fields = [
        "id",
        "priority_score",
        "source",
        "source_id",
        "doi",
        "title",
        "authors",
        "year",
        "publication_date",
        "url",
        "pdf_url",
        "is_open_access",
        "cited_by_count",
        "venue",
        "concepts",
        "topic_id",
        "topic_label",
        "track_ids",
        "problem_ids",
        "query",
        "abstract",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {}
            for field in fields:
                value = record.get(field, "")
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                row[field] = value
            writer.writerow(row)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, records: list[dict], version: str) -> None:
    lines = [
        "# D4D Literature Seed Catalog",
        "",
        f"- Version: `{version}`",
        f"- Records: {len(records)}",
        "- Sources: OpenAlex Works API, arXiv API",
        "- Scope: paper metadata and abstracts only; no full-text redistribution.",
        "",
        "## Top Papers By Track",
        "",
    ]
    for track in ["T1", "T2", "T3", "T4", "T5"]:
        subset = [record for record in records if track in record.get("track_ids", [])][:12]
        lines.extend([f"### {track}", ""])
        for record in subset:
            authors = ", ".join(record.get("authors", [])[:3])
            if len(record.get("authors", [])) > 3:
                authors += " et al."
            title = record.get("title", "Untitled").replace("[", "\\[").replace("]", "\\]")
            url = record.get("url") or record.get("pdf_url")
            lines.append(
                f"- **{title}** ({record.get('year') or 'n.d.'}) — {authors or 'Unknown authors'}"
            )
            lines.append(
                f"  - Topic: {record.get('topic_label')} | Score: {record.get('priority_score')} | Source: {record.get('source')} | [link]({url})"
            )
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--version", default=now_version())
    parser.add_argument("--per-query", type=int, default=8)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    root = Path(args.project_root)
    raw_dir = root / "03_data/raw/literature" / args.version
    processed_dir = root / "03_data/processed/literature/versions" / args.version
    research_dir = root / "01_research/literature"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    run_log: list[dict] = []
    for topic in TOPICS:
        for query in topic["queries"]:
            try:
                openalex_records, meta = fetch_openalex(topic, query, args.per_query)
                records.extend(openalex_records)
                run_log.append({"provider": "OpenAlex", "topic_id": topic["topic_id"], "query": query, "ok": True, **meta})
            except Exception as exc:
                run_log.append({"provider": "OpenAlex", "topic_id": topic["topic_id"], "query": query, "ok": False, "error": repr(exc)})
            time.sleep(args.sleep)
            try:
                arxiv_records, meta = fetch_arxiv(topic, query, max(3, args.per_query // 2))
                records.extend(arxiv_records)
                run_log.append({"provider": "arXiv", "topic_id": topic["topic_id"], "query": query, "ok": True, **meta})
            except Exception as exc:
                run_log.append({"provider": "arXiv", "topic_id": topic["topic_id"], "query": query, "ok": False, "error": repr(exc)})
            time.sleep(args.sleep)

    deduped = dedupe(records)
    manifest = {
        "version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topics": TOPICS,
        "sources": {
            "OpenAlex": "https://api.openalex.org/works",
            "arXiv": "https://export.arxiv.org/api/query",
        },
        "counts": {
            "raw_records": len(records),
            "deduped_records": len(deduped),
            "topics": len(TOPICS),
            "queries": sum(len(topic["queries"]) for topic in TOPICS),
        },
        "outputs": {
            "records_json": str(processed_dir / "literature_seed_catalog.json"),
            "records_csv": str(processed_dir / "literature_seed_catalog.csv"),
            "run_log": str(raw_dir / "collection_run_log.json"),
            "markdown": str(research_dir / "literature_seed_catalog.md"),
        },
    }
    write_json(raw_dir / "collection_run_log.json", run_log)
    write_json(processed_dir / "literature_seed_catalog.json", deduped)
    write_json(processed_dir / "dataset_manifest.json", manifest)
    write_csv(processed_dir / "literature_seed_catalog.csv", deduped)
    write_markdown(processed_dir / "literature_seed_catalog.md", deduped, args.version)
    write_markdown(research_dir / "literature_seed_catalog.md", deduped, args.version)

    current = root / "03_data/processed/literature/current"
    if current.exists() or current.is_symlink():
        current.unlink()
    current.symlink_to(Path("versions") / args.version)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

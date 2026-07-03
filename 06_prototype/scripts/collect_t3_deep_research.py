#!/usr/bin/env python3
"""Collect focused T3 deep-research literature for D4D.

The collector uses OpenAlex and arXiv metadata, then follows OpenAlex
referenced_works and related_works for a shallow snowball pass.
It stores metadata only; it does not download or redistribute full papers.
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
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")

PROJECT = {
    "project_id": "t3_resilient_maritime_semantic_cop",
    "title": "Resilient Maritime COP over Denied Networks",
    "title_ko": "거부환경 해상 COP 의미 전송 시스템",
    "primary_track_ids": ["T3"],
    "supporting_track_ids": ["T4", "T2"],
    "problem_ids": ["T3-001", "T3-005", "T4-001", "T4-002"],
}


TOPICS = [
    {
        "topic_id": "semantic_communication_core",
        "label": "Semantic communication core",
        "weight": 5,
        "queries": [
            '"semantic communications" wireless networks survey',
            '"semantic communication" "edge intelligence" survey',
            '"semantic communication" "bandwidth" "wireless"',
            '"task-oriented semantic communication" wireless networks',
        ],
    },
    {
        "topic_id": "tactical_denied_networks",
        "label": "Tactical / denied / degraded networks",
        "weight": 5,
        "queries": [
            '"tactical networks" "edge computing" "command and control"',
            '"denied environment" "command and control" network',
            '"disconnected intermittent limited" tactical network',
            '"delay tolerant network" military tactical communications',
        ],
    },
    {
        "topic_id": "cop_c2_situational_awareness",
        "label": "COP / C2 / situational awareness",
        "weight": 5,
        "queries": [
            '"common operational picture" "command and control"',
            '"common operational picture" sensor fusion decision support',
            '"situational awareness" "command and control" "sensor fusion"',
            '"ontology" "common operational picture" "command and control"',
        ],
    },
    {
        "topic_id": "sensor_fusion_event_correlation",
        "label": "Sensor fusion and event correlation",
        "weight": 4,
        "queries": [
            '"multi sensor fusion" "situational awareness" survey',
            '"event correlation" "sensor fusion" "situational awareness"',
            '"track fusion" "sensor fusion" "command and control"',
            '"spatio-temporal data fusion" "situational awareness"',
        ],
    },
    {
        "topic_id": "maritime_mda_ais_osint",
        "label": "Maritime MDA / AIS / OSINT",
        "weight": 4,
        "queries": [
            '"AIS anomaly detection" "maritime domain awareness" review',
            '"dark vessel" "AIS" "SAR" fusion',
            '"maritime domain awareness" "OSINT" "AIS"',
            '"maritime anomaly detection" "AIS" "deep learning"',
        ],
    },
    {
        "topic_id": "edge_ai_prioritization",
        "label": "Edge AI, event prioritization, compression",
        "weight": 3,
        "queries": [
            '"edge intelligence" "data compression" "wireless networks"',
            '"event prioritization" "edge computing" "IoT"',
            '"adaptive data transmission" "edge computing" sensor networks',
            '"quality of information" "sensor networks" decision support',
        ],
    },
    {
        "topic_id": "rag_provenance_briefing",
        "label": "RAG, provenance, citation-grounded briefing",
        "weight": 3,
        "queries": [
            '"retrieval augmented generation" citation provenance evaluation',
            '"source grounded" "large language model" "question answering"',
            '"RAG" hallucination attribution citation evaluation',
            '"provenance aware" question answering knowledge graph',
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
        "referenced_works",
        "related_works",
    ]
)

KEY_TERMS = {
    "semantic communication": 6,
    "semantic communications": 6,
    "common operational picture": 6,
    "command and control": 5,
    "situational awareness": 5,
    "sensor fusion": 5,
    "maritime domain awareness": 5,
    "automatic identification system": 4,
    " ais ": 3,
    "dark vessel": 5,
    "denied environment": 5,
    "tactical network": 4,
    "edge intelligence": 4,
    "edge computing": 3,
    "provenance": 4,
    "citation": 3,
    "retrieval augmented generation": 4,
    "knowledge graph": 4,
    "event correlation": 4,
    "decision support": 4,
    "data fusion": 4,
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())[:160]


def reconstruct_abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    pairs = []
    for word, positions in inverted.items():
        for pos in positions:
            pairs.append((int(pos), word))
    return " ".join(word for _, word in sorted(pairs))


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-T3-deep-research/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-T3-deep-research/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def stable_id(record: dict) -> str:
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


def relevance_score(record: dict, topic_weight: int = 0) -> int:
    text = f" {record.get('title','')} {record.get('abstract','')} ".lower()
    score = topic_weight
    year = int(record.get("year") or 0)
    cited = int(record.get("cited_by_count") or 0)
    if year >= 2024:
        score += 4
    elif year >= 2020:
        score += 3
    elif year >= 2016:
        score += 2
    if record.get("is_open_access"):
        score += 2
    if cited >= 500:
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
    for generic_bad in ["healthcare", "agriculture", "finance", "metaverse", "medical", "patient"]:
        if generic_bad in text and not any(anchor in text for anchor in ["tactical", "defense", "maritime", "command and control"]):
            score -= 3
    return score


def normalize_openalex(work: dict, topic: dict | None, query: str, relation: str, seed_openalex_id: str = "") -> dict:
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    authors = []
    for authorship in work.get("authorships", [])[:8]:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            authors.append(author["display_name"])
    concepts = [c.get("display_name") for c in work.get("concepts", [])[:10] if c.get("display_name")]
    location = work.get("primary_location") or {}
    record = {
        "id": "",
        "source": "OpenAlex",
        "relation": relation,
        "seed_openalex_id": seed_openalex_id,
        "topic_id": topic["topic_id"] if topic else "",
        "topic_label": topic["label"] if topic else "",
        "query": query,
        "openalex_id": work.get("id", ""),
        "doi": doi,
        "title": clean_text(work.get("display_name")),
        "authors": authors,
        "year": work.get("publication_year") or "",
        "publication_date": work.get("publication_date") or "",
        "url": landing_url(location, doi, work.get("id", "")),
        "pdf_url": location.get("pdf_url") or "",
        "is_open_access": bool((work.get("open_access") or {}).get("is_oa")),
        "cited_by_count": work.get("cited_by_count") or 0,
        "venue": ((location.get("source") or {}).get("display_name") if location else "") or "",
        "concepts": concepts,
        "abstract": clean_text(reconstruct_abstract(work.get("abstract_inverted_index"))),
        "referenced_works": work.get("referenced_works") or [],
        "related_works": work.get("related_works") or [],
    }
    record["id"] = stable_id(record)
    record["relevance_score"] = relevance_score(record, topic["weight"] if topic else 0)
    return record


def normalize_arxiv_entry(entry: ET.Element, topic: dict, query: str) -> dict:
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
    abstract = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
    published = entry.findtext("atom:published", default="", namespaces=ns)
    authors = []
    for author in entry.findall("atom:author", ns)[:8]:
        name = clean_text(author.findtext("atom:name", default="", namespaces=ns))
        if name:
            authors.append(name)
    url = entry.findtext("atom:id", default="", namespaces=ns)
    pdf_url = ""
    for link in entry.findall("atom:link", ns):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href", "")
    record = {
        "id": "",
        "source": "arXiv",
        "relation": "seed_search",
        "seed_openalex_id": "",
        "topic_id": topic["topic_id"],
        "topic_label": topic["label"],
        "query": query,
        "openalex_id": "",
        "doi": entry.findtext("arxiv:doi", default="", namespaces=ns),
        "title": title,
        "authors": authors,
        "year": published[:4] if published else "",
        "publication_date": published[:10],
        "url": url,
        "pdf_url": pdf_url,
        "is_open_access": True,
        "cited_by_count": 0,
        "venue": "arXiv",
        "concepts": [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns) if cat.attrib.get("term")],
        "abstract": abstract,
        "referenced_works": [],
        "related_works": [],
    }
    record["id"] = stable_id(record)
    record["relevance_score"] = relevance_score(record, topic["weight"])
    return record


def fetch_openalex_search(topic: dict, query: str, per_query: int) -> tuple[list[dict], dict]:
    params = {
        "search": query,
        "filter": "from_publication_date:2014-01-01",
        "per-page": str(per_query),
        "select": OPENALEX_SELECT,
        "sort": "relevance_score:desc",
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = request_json(url)
    records = [normalize_openalex(work, topic, query, "seed_search") for work in data.get("results", [])]
    return records, {"url": url, "meta": data.get("meta", {})}


def fetch_arxiv_search(topic: dict, query: str, per_query: int) -> tuple[list[dict], dict]:
    tokens = [t.strip('"') for t in re.findall(r'"[^"]+"|\S+', query)][:7]
    search_query = "all:" + " AND all:".join(tokens)
    params = {
        "search_query": search_query,
        "start": "0",
        "max_results": str(max(3, per_query // 2)),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    text = request_text(url)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    records = [normalize_arxiv_entry(entry, topic, query) for entry in root.findall("atom:entry", ns)]
    return records, {"url": url, "entry_count": len(records)}


def fetch_openalex_work(openalex_id: str) -> dict | None:
    if not openalex_id:
        return None
    url = openalex_id
    if url.startswith("https://openalex.org/"):
        url = "https://api.openalex.org/works/" + url.rsplit("/", 1)[-1] + "?" + urllib.parse.urlencode({"select": OPENALEX_SELECT})
    elif openalex_id.startswith("W"):
        url = "https://api.openalex.org/works/" + openalex_id + "?" + urllib.parse.urlencode({"select": OPENALEX_SELECT})
    data = request_json(url)
    return data


def dedupe(records: list[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for record in records:
        key = (record.get("doi") or "").lower()
        if not key:
            key = normalize_title(record.get("title", ""))
        if not key:
            key = record["id"]
        existing = by_key.get(key)
        if not existing:
            by_key[key] = record
            continue
        existing["relevance_score"] = max(existing.get("relevance_score", 0), record.get("relevance_score", 0))
        existing["cited_by_count"] = max(int(existing.get("cited_by_count") or 0), int(record.get("cited_by_count") or 0))
        for field in ["topic_id", "topic_label", "query", "relation"]:
            values = set(filter(None, re.split(r"\s*\|\s*", str(existing.get(field, "")))))
            if record.get(field):
                values.add(str(record[field]))
            existing[field] = " | ".join(sorted(values))
        if existing.get("source") != record.get("source") and record.get("source") not in existing.get("source", ""):
            existing["source"] = existing.get("source", "") + "+" + record.get("source", "")
        for field in ["abstract", "pdf_url", "doi", "url", "openalex_id"]:
            if not existing.get(field) and record.get(field):
                existing[field] = record[field]
    return sorted(by_key.values(), key=lambda r: (r.get("relevance_score", 0), int(r.get("cited_by_count") or 0)), reverse=True)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, records: list[dict]) -> None:
    fields = [
        "id",
        "relevance_score",
        "source",
        "relation",
        "topic_id",
        "topic_label",
        "query",
        "openalex_id",
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


def write_markdown(path: Path, records: list[dict], version: str) -> None:
    lines = [
        "# T3 Deep Research Literature Catalog",
        "",
        f"- Version: `{version}`",
        f"- Records: {len(records)}",
        "- Topic: Resilient Maritime COP over Denied Networks",
        "- Sources: OpenAlex, arXiv; snowball from OpenAlex referenced/related works",
        "",
        "## Top 40",
        "",
    ]
    for idx, record in enumerate(records[:40], start=1):
        authors = ", ".join(record.get("authors", [])[:3])
        if len(record.get("authors", [])) > 3:
            authors += " et al."
        lines.extend(
            [
                f"{idx}. **{record.get('title', 'Untitled')}** ({record.get('year') or 'n.d.'})",
                f"   - Score: {record.get('relevance_score')} | Cited by: {record.get('cited_by_count')} | Relation: {record.get('relation')} | Topic: {record.get('topic_label')}",
                f"   - Authors: {authors or 'Unknown'}",
                f"   - Link: {record.get('url') or record.get('pdf_url')}",
            ]
        )
        if record.get("abstract"):
            lines.append(f"   - Abstract note: {record['abstract'][:280]}...")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def update_current_symlink(root: Path, version_dir: Path) -> None:
    current = root / "03_data/processed/literature_t3/current"
    current.parent.mkdir(parents=True, exist_ok=True)
    if current.exists() or current.is_symlink():
        current.unlink()
    current.symlink_to(Path("versions") / version_dir.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--version", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--per-query", type=int, default=10)
    parser.add_argument("--snowball-per-seed", type=int, default=4)
    parser.add_argument("--max-snowball-fetches", type=int, default=180)
    parser.add_argument("--sleep", type=float, default=0.15)
    args = parser.parse_args()

    root = Path(args.project_root)
    raw_dir = root / "03_data/raw/literature_t3" / args.version
    version_dir = root / "03_data/processed/literature_t3/versions" / args.version
    research_dir = root / "01_research/literature/t3_deep_research"
    raw_dir.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    run_log: list[dict] = []

    for topic in TOPICS:
        for query in topic["queries"]:
            try:
                batch, meta = fetch_openalex_search(topic, query, args.per_query)
                records.extend(batch)
                run_log.append({"provider": "OpenAlex", "stage": "seed_search", "topic_id": topic["topic_id"], "query": query, "ok": True, "count": len(batch), **meta})
            except Exception as exc:
                run_log.append({"provider": "OpenAlex", "stage": "seed_search", "topic_id": topic["topic_id"], "query": query, "ok": False, "error": repr(exc)})
            time.sleep(args.sleep)
            try:
                batch, meta = fetch_arxiv_search(topic, query, args.per_query)
                records.extend(batch)
                run_log.append({"provider": "arXiv", "stage": "seed_search", "topic_id": topic["topic_id"], "query": query, "ok": True, "count": len(batch), **meta})
            except Exception as exc:
                run_log.append({"provider": "arXiv", "stage": "seed_search", "topic_id": topic["topic_id"], "query": query, "ok": False, "error": repr(exc)})
            time.sleep(args.sleep)

    seed_records = dedupe(records)
    candidates = []
    for seed in seed_records[:70]:
        ids = []
        ids.extend((seed.get("related_works") or [])[: args.snowball_per_seed])
        ids.extend((seed.get("referenced_works") or [])[: args.snowball_per_seed])
        for oid in ids:
            candidates.append((oid, seed.get("openalex_id", ""), seed.get("topic_id", ""), seed.get("query", "")))

    seen_works = {r.get("openalex_id") for r in seed_records if r.get("openalex_id")}
    fetched = 0
    for openalex_id, seed_id, topic_id, query in candidates:
        if fetched >= args.max_snowball_fetches:
            break
        if openalex_id in seen_works:
            continue
        seen_works.add(openalex_id)
        topic = next((t for t in TOPICS if t["topic_id"] == topic_id), None)
        try:
            work = fetch_openalex_work(openalex_id)
            if work:
                record = normalize_openalex(work, topic, query, "snowball_related_or_reference", seed_id)
                if record["relevance_score"] >= 8:
                    records.append(record)
                run_log.append({"provider": "OpenAlex", "stage": "snowball", "openalex_id": openalex_id, "seed_openalex_id": seed_id, "ok": True, "kept": record["relevance_score"] >= 8, "score": record["relevance_score"]})
                fetched += 1
        except Exception as exc:
            run_log.append({"provider": "OpenAlex", "stage": "snowball", "openalex_id": openalex_id, "seed_openalex_id": seed_id, "ok": False, "error": repr(exc)})
        time.sleep(args.sleep)

    final_records = dedupe(records)
    manifest = {
        "version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT,
        "topics": TOPICS,
        "counts": {
            "raw_records": len(records),
            "deduped_records": len(final_records),
            "seed_records": len(seed_records),
            "snowball_fetches": fetched,
            "topics": len(TOPICS),
            "queries": sum(len(t["queries"]) for t in TOPICS),
        },
        "sources": {
            "OpenAlex": "https://api.openalex.org/works",
            "arXiv": "https://export.arxiv.org/api/query",
        },
        "outputs": {
            "records_json": str(version_dir / "t3_deep_research_catalog.json"),
            "records_csv": str(version_dir / "t3_deep_research_catalog.csv"),
            "records_md": str(research_dir / "t3_deep_research_catalog.md"),
            "run_log": str(raw_dir / "collection_run_log.json"),
        },
    }
    write_json(raw_dir / "collection_run_log.json", run_log)
    write_json(version_dir / "dataset_manifest.json", manifest)
    write_json(version_dir / "t3_deep_research_catalog.json", final_records)
    write_csv(version_dir / "t3_deep_research_catalog.csv", final_records)
    write_markdown(version_dir / "t3_deep_research_catalog.md", final_records, args.version)
    write_markdown(research_dir / "t3_deep_research_catalog.md", final_records, args.version)
    update_current_symlink(root, version_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

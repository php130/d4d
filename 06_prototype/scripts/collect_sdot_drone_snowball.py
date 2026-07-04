#!/usr/bin/env python3
"""Snowball collect OpenAlex metadata from top S-DOT drone seed papers.

Reads the latest S-DOT drone literature records, follows referenced_works and
related_works from high-scoring OpenAlex seeds, fetches metadata, and writes
new-only plus merged outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
BASE_DIR = PROJECT_ROOT / "03_data" / "processed" / "literature_sdot_drone"
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

KEY_TERMS = {
    "semantic communication": 8,
    "semantic communications": 8,
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


def request_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "D4D-SDOT-drone-snowball/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


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


def relevance_score(record: dict[str, Any]) -> int:
    text = f" {record.get('title','')} {record.get('abstract','')} ".lower()
    score = 0
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
    return score


def normalize_openalex(work: dict[str, Any], seed_id: str, seed_title: str, relation: str) -> dict[str, Any]:
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
        "topic_id": "snowball",
        "topic_label": "OpenAlex references / related works snowball",
        "matched_topics": ["snowball"],
        "query": f"{relation} from {seed_id}",
        "snowball_relation": relation,
        "snowball_seed_id": seed_id,
        "snowball_seed_title": seed_title,
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
    record["relevance_score"] = relevance_score(record)
    return record


def api_url(openalex_id: str) -> str:
    work_id = openalex_id.rstrip("/").split("/")[-1]
    return f"https://api.openalex.org/works/{work_id}?select={OPENALEX_SELECT}"


def key(record: dict[str, Any]) -> str:
    return record.get("doi") or record.get("openalex_id") or normalize_title(record.get("title", "")) or record["id"]


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "id",
        "source",
        "topic_id",
        "topic_label",
        "matched_topics",
        "snowball_relation",
        "snowball_seed_title",
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


def write_queue(path: Path, records: list[dict[str, Any]], limit: int) -> None:
    lines = [
        "# S-DOT Drone Snowball Reading Queue",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Records shown: {min(limit, len(records))} / {len(records)}",
        "",
    ]
    for idx, record in enumerate(records[:limit], 1):
        authors = ", ".join(record.get("authors", [])[:5])
        lines += [
            f"## {idx}. {record['title']}",
            "",
            f"- Year: {record.get('year','')}",
            f"- Score: {record.get('relevance_score', 0)}",
            f"- Citations: {record.get('cited_by_count', 0)}",
            f"- Relation: {record.get('snowball_relation','')}",
            f"- Seed: {record.get('snowball_seed_title','')}",
            f"- URL: {record.get('url','')}",
            f"- Authors: {authors}",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-limit", type=int, default=140)
    parser.add_argument("--max-work-ids", type=int, default=1400)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--queue-limit", type=int, default=120)
    parser.add_argument("--checkpoint-every", type=int, default=50)
    args = parser.parse_args()

    latest = json.loads((BASE_DIR / "latest.json").read_text(encoding="utf-8"))
    base_path = Path(latest["outputs"]["records_json"])
    base_records = json.loads(base_path.read_text(encoding="utf-8"))
    existing_keys = {key(record) for record in base_records}
    existing_openalex = {record.get("openalex_id") for record in base_records if record.get("openalex_id")}

    seeds = [
        record for record in base_records
        if record.get("source") == "OpenAlex" and (record.get("referenced_works") or record.get("related_works"))
    ]
    seeds = sorted(seeds, key=lambda r: (int(r.get("relevance_score") or 0), int(r.get("cited_by_count") or 0)), reverse=True)[: args.seed_limit]

    candidates: dict[str, tuple[str, str, str]] = {}
    for seed in seeds:
        for relation, field in [("referenced_work", "referenced_works"), ("related_work", "related_works")]:
            for work_id in seed.get(field, []) or []:
                if work_id in existing_openalex:
                    continue
                candidates.setdefault(work_id, (seed["id"], seed["title"], relation))
                if len(candidates) >= args.max_work_ids:
                    break
            if len(candidates) >= args.max_work_ids:
                break
        if len(candidates) >= args.max_work_ids:
            break

    version = now_version()
    run_dir = BASE_DIR / f"snowball_{version}"
    run_dir.mkdir(parents=True, exist_ok=True)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    fetched = []
    failures = []
    checkpoint_path = run_dir / "checkpoint_fetched_records.json"
    checkpoint_failures_path = run_dir / "checkpoint_failures.json"
    for idx, (work_id, (seed_id, seed_title, relation)) in enumerate(candidates.items(), 1):
        try:
            work = request_json(api_url(work_id))
            record = normalize_openalex(work, seed_id, seed_title, relation)
            fetched.append(record)
        except Exception as exc:  # noqa: BLE001
            failures.append({"work_id": work_id, "error": str(exc)})
        if idx % 100 == 0:
            print(f"[INFO] fetched {idx}/{len(candidates)} failures={len(failures)}")
        if idx % args.checkpoint_every == 0:
            checkpoint_path.write_text(json.dumps(fetched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            checkpoint_failures_path.write_text(json.dumps(failures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(args.delay)

    checkpoint_path.write_text(json.dumps(fetched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checkpoint_failures_path.write_text(json.dumps(failures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    new_by_key: dict[str, dict[str, Any]] = {}
    for record in fetched:
        k = key(record)
        if k in existing_keys:
            continue
        current = new_by_key.get(k)
        if not current or record["relevance_score"] > current["relevance_score"]:
            new_by_key[k] = record
    new_records = sorted(new_by_key.values(), key=lambda r: (r["relevance_score"], int(r.get("cited_by_count") or 0), int(r.get("year") or 0)), reverse=True)

    merged_by_key = {key(record): record for record in base_records}
    for record in new_records:
        merged_by_key[key(record)] = record
    merged_records = sorted(merged_by_key.values(), key=lambda r: (int(r.get("relevance_score") or 0), int(r.get("cited_by_count") or 0), int(r.get("year") or 0)), reverse=True)

    new_json = run_dir / "sdot_drone_snowball_new_records.json"
    new_csv = run_dir / "sdot_drone_snowball_new_records.csv"
    merged_json = run_dir / "sdot_drone_literature_records_merged.json"
    summary_json = run_dir / "snowball_summary.json"
    queue_md = RESEARCH_DIR / f"sdot_drone_snowball_reading_queue_{version}.md"

    new_json.write_text(json.dumps(new_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    merged_json.write_text(json.dumps(merged_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(new_csv, new_records)
    write_queue(queue_md, new_records, args.queue_limit)

    summary = {
        "version": f"snowball_{version}",
        "generated_at": datetime.now().isoformat(),
        "base_records": len(base_records),
        "seed_count": len(seeds),
        "candidate_work_ids": len(candidates),
        "fetched_records": len(fetched),
        "new_records": len(new_records),
        "merged_records": len(merged_records),
        "failure_count": len(failures),
        "relation_counts_new": dict(Counter(record.get("snowball_relation", "") for record in new_records)),
        "top_new_records": [
            {
                "title": record["title"],
                "year": record.get("year"),
                "score": record.get("relevance_score"),
                "cited_by_count": record.get("cited_by_count"),
                "url": record.get("url"),
            }
            for record in new_records[:30]
        ],
        "outputs": {
            "new_json": str(new_json),
            "new_csv": str(new_csv),
            "merged_json": str(merged_json),
            "queue": str(queue_md),
        },
        "failures": failures[:50],
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BASE_DIR / "latest_snowball.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (BASE_DIR / "VERSIONS.md").open("a", encoding="utf-8") as f:
        f.write(f"- snowball_{version}: seeds {len(seeds)}, candidates {len(candidates)}, new {len(new_records)}, merged {len(merged_records)}, outputs `{run_dir}`\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build versioned D4D datasets from exported Google Sheet CSV snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


SPREADSHEET_ID = "1l_ThafA1n5Wue2BnPeJ1FPpiZvThG6X9iIPRuJsxR5o"
SPREADSHEET_TITLE = "D4D_SEOUL_참가자안내(260629/공개)"
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"

SHEETS = {
    "track_problems": {
        "gid": "1313109997",
        "tab": "B-2. 트랙별_문제",
        "raw_filename": "B-2_track_problems.csv",
    },
    "glossary": {
        "gid": "1682873298",
        "tab": "B-3. 용어집",
        "raw_filename": "B-3_glossary.csv",
    },
}

LOCAL_GLOSSARY_ADDITIONS = [
    {
        "category": "프로젝트 운영",
        "term": "Data Fusion",
        "english": "Data Fusion",
        "description": "여러 출처의 데이터를 같은 엔티티·시간·공간 기준으로 결합하는 것.",
        "related_tracks": ["T2", "T3", "T4"],
    },
    {
        "category": "프로젝트 운영",
        "term": "Entity",
        "english": "Entity",
        "description": "분석 대상이 되는 객체. 사람, 조직, 선박, 계정, 도메인, IP, 지명 등이 포함됩니다.",
        "related_tracks": ["T2"],
    },
    {
        "category": "프로젝트 운영",
        "term": "Dark Web",
        "english": "Dark Web",
        "description": "일반 검색엔진으로 접근되지 않고 특수 네트워크가 필요한 웹 영역. 위협 행위자, 유출정보, 범죄 인프라 탐지 소스로 다뤄질 수 있습니다.",
        "related_tracks": ["T2"],
    },
    {
        "category": "프로젝트 운영",
        "term": "Indicator",
        "english": "Indicator",
        "description": "위협이나 사건을 식별하는 단서. IP, 도메인, 이메일, 해시, 지갑주소 등이 포함됩니다.",
        "related_tracks": ["T2"],
    },
    {
        "category": "프로젝트 운영",
        "term": "Military Deployability",
        "english": "Military Deployability",
        "description": "군 환경에 실제 배치 가능한 정도. 보안, 권한, 감사, 네트워크, 현장 제약, 설명 가능성을 함께 봅니다.",
        "related_tracks": ["공통"],
    },
]


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


def split_lines(value: str) -> list[str]:
    return [line.strip() for line in clean(value).split("\n") if line.strip()]


def split_related_tracks(value: str) -> list[str]:
    parts = re.split(r"[·,/\n]+", clean(value))
    return [part.strip() for part in parts if part.strip()]


def split_types(value: str) -> list[str]:
    parts = re.split(r"[·/\n]+", clean(value))
    return [part.strip() for part in parts if part.strip()]


def split_bullets(value: str) -> list[str]:
    text = clean(value)
    if not text:
        return []
    lines = split_lines(text)
    bullets = []
    current = []
    for line in lines:
        normalized = line.lstrip("•- ").strip()
        if line.startswith("•") or (line.startswith("-") and current):
            if current:
                bullets.append(" ".join(current).strip())
            current = [normalized]
        else:
            if current:
                current.append(normalized)
            else:
                bullets.append(normalized)
    if current:
        bullets.append(" ".join(current).strip())
    return [bullet for bullet in bullets if bullet]


def slugify(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value).strip("-").lower()
    return value or "item"


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [[clean(cell) for cell in row] for row in csv.reader(f)]


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: json.dumps(row[field], ensure_ascii=False)
                    if isinstance(row.get(field), (list, dict))
                    else row.get(field, "")
                    for field in fields
                }
            )


def download_csv(raw_dir: Path, key: str) -> Path:
    sheet = SHEETS[key]
    target = raw_dir / sheet["raw_filename"]
    if target.exists() and target.stat().st_size > 0:
        return target
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={sheet['gid']}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as response:
        target.write_bytes(response.read())
    return target


def parse_anchor(raw: str) -> dict:
    lines = split_lines(raw)
    partners = []
    before_partner = []
    partner_mode = False
    for line in lines:
        if line == "-":
            partner_mode = True
            continue
        if partner_mode:
            partners.append(line)
        else:
            before_partner.append(line)
    expansions = [line.lstrip("+").strip() for line in before_partner if line.startswith("+")]
    titles = [line for line in before_partner if not line.startswith("+")]
    return {
        "track_title_en": titles[0] if titles else "",
        "track_title_ko": titles[1] if len(titles) > 1 else "",
        "expansions": expansions,
        "anchor_partners": partners,
        "raw": raw,
    }


def parse_problem_name(raw: str) -> tuple[str, str]:
    lines = split_lines(raw)
    if not lines:
        return "", ""
    if len(lines) == 1:
        return lines[0], ""
    return lines[0], lines[1]


def parse_track_problems(path: Path, version: str) -> tuple[list[dict], dict[str, dict]]:
    rows = read_csv(path)
    problems = []
    tracks = {}
    current_track_id = ""
    current_anchor_raw = ""
    counters: dict[str, int] = {}

    for index, row in enumerate(rows[3:], start=4):
        row = row + [""] * 8
        track_id, anchor_raw, problem_type, problem_name_raw, background, challenge, approach, notes = row[:8]
        if track_id:
            current_track_id = track_id
        if anchor_raw:
            current_anchor_raw = anchor_raw
        if not clean(problem_name_raw):
            continue
        if not current_track_id:
            continue

        anchor = parse_anchor(current_anchor_raw)
        tracks[current_track_id] = {
            "track_id": current_track_id,
            **anchor,
        }
        counters[current_track_id] = counters.get(current_track_id, 0) + 1
        name_ko, name_en = parse_problem_name(problem_name_raw)
        problem_id = f"{current_track_id}-{counters[current_track_id]:03d}"

        problems.append(
            {
                "id": problem_id,
                "track_id": current_track_id,
                "track_title_en": anchor["track_title_en"],
                "track_title_ko": anchor["track_title_ko"],
                "anchor_partners": anchor["anchor_partners"],
                "expansions": anchor["expansions"],
                "problem_type": clean(problem_type),
                "problem_type_tags": split_types(problem_type),
                "problem_name": clean(problem_name_raw),
                "problem_name_ko": name_ko,
                "problem_name_en": name_en,
                "background": clean(background),
                "challenge": clean(challenge),
                "example_approach": clean(approach),
                "example_approach_items": split_bullets(approach),
                "notes": clean(notes),
                "source": {
                    "spreadsheet_id": SPREADSHEET_ID,
                    "spreadsheet_title": SPREADSHEET_TITLE,
                    "spreadsheet_url": SPREADSHEET_URL,
                    "sheet": SHEETS["track_problems"]["tab"],
                    "gid": SHEETS["track_problems"]["gid"],
                    "row": index,
                    "version": version,
                },
            }
        )
    return problems, tracks


def parse_glossary(path: Path, version: str) -> list[dict]:
    rows = read_csv(path)
    terms = []
    current_category = ""
    for index, row in enumerate(rows[2:], start=3):
        row = row + [""] * 5
        category, term, english, description, related_tracks = row[:5]
        if category:
            current_category = category
        if not term:
            continue
        terms.append(
            {
                "id": f"term-{len(terms) + 1:03d}-{slugify(term)[:40]}",
                "category": current_category,
                "term": clean(term),
                "english": clean(english),
                "description": clean(description),
                "related_tracks": split_related_tracks(related_tracks),
                "source": {
                    "spreadsheet_id": SPREADSHEET_ID,
                    "spreadsheet_title": SPREADSHEET_TITLE,
                    "spreadsheet_url": SPREADSHEET_URL,
                    "sheet": SHEETS["glossary"]["tab"],
                    "gid": SHEETS["glossary"]["gid"],
                    "row": index,
                    "version": version,
                },
            }
        )
    return terms


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_track_markdown(path: Path, problems: list[dict], tracks: dict[str, dict], version: str) -> None:
    lines = [
        "# D4D Track Problem Dataset",
        "",
        f"- Version: `{version}`",
        f"- Source: [{SPREADSHEET_TITLE}]({SPREADSHEET_URL})",
        f"- Rows: {len(problems)} problem statements",
        "",
    ]
    for track_id in sorted(tracks):
        track = tracks[track_id]
        track_problems = [p for p in problems if p["track_id"] == track_id]
        lines.extend(
            [
                f"## {track_id}. {track['track_title_en']}",
                "",
                f"- Korean: {track['track_title_ko']}",
                f"- Anchor partners: {', '.join(track['anchor_partners']) or '-'}",
                f"- Problem count: {len(track_problems)}",
                "",
            ]
        )
        for problem in track_problems:
            lines.extend(
                [
                    f"### {problem['id']} · {problem['problem_name_ko']}",
                    "",
                    f"- English: {problem['problem_name_en'] or '-'}",
                    f"- Type: {problem['problem_type']}",
                    f"- Source row: {problem['source']['sheet']} row {problem['source']['row']}",
                    "",
                    "**Background**",
                    "",
                    problem["background"],
                    "",
                    "**Challenge**",
                    "",
                    problem["challenge"],
                    "",
                    "**Example Approach**",
                    "",
                    problem["example_approach"],
                    "",
                ]
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_glossary_markdown(path: Path, terms: list[dict], version: str) -> None:
    lines = [
        "# Glossary",
        "",
        "이 문서는 D4D Google Sheet의 `B-3. 용어집` 탭을 기준으로 생성한 용어집입니다.",
        "시트가 바뀔 수 있으므로 각 갱신은 `03_data/processed/versions/` 아래에 버전 스냅샷으로 남깁니다.",
        "",
        f"- Current source version: `{version}`",
        f"- Source: [{SPREADSHEET_TITLE}]({SPREADSHEET_URL})",
        f"- Source sheet: `{SHEETS['glossary']['tab']}`",
        "",
        "## Sheet Terms",
        "",
        "| 구분 | 용어 / 약어 | 영문 | 설명 | 관련 트랙 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for term in terms:
        lines.append(
            "| {category} | {term} | {english} | {description} | {tracks} |".format(
                category=term["category"].replace("\n", "<br>"),
                term=term["term"].replace("|", "\\|"),
                english=term["english"].replace("|", "\\|"),
                description=term["description"].replace("|", "\\|"),
                tracks="·".join(term["related_tracks"]),
            )
        )

    lines.extend(
        [
            "",
            "## Local Additions",
            "",
            "아래 항목은 프로젝트 운영을 위해 별도로 보강한 용어입니다.",
            "",
            "| 구분 | 용어 / 약어 | 영문 | 설명 | 관련 트랙 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for term in LOCAL_GLOSSARY_ADDITIONS:
        lines.append(
            "| {category} | {term} | {english} | {description} | {tracks} |".format(
                category=term["category"],
                term=term["term"].replace("|", "\\|"),
                english=term["english"].replace("|", "\\|"),
                description=term["description"].replace("|", "\\|"),
                tracks="·".join(term["related_tracks"]),
            )
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_versions_index(processed_root: Path) -> None:
    lines = [
        "# Dataset Versions",
        "",
        "이 문서는 Google Sheet 기반 D4D 데이터셋의 로컬 스냅샷 버전 목록입니다.",
        "`current` 심볼릭 링크는 최신 processed version을 가리킵니다.",
        "",
        "| Version | Problems | Glossary Terms | Generated At |",
        "| --- | ---: | ---: | --- |",
    ]
    versions_root = processed_root / "versions"
    for manifest_path in sorted(versions_root.glob("*/dataset_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        lines.append(
            f"| `{manifest['version']}` | {manifest['counts']['track_problem_statements']} | "
            f"{manifest['counts']['glossary_terms']} | {manifest['generated_at']} |"
        )
    (processed_root / "VERSIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_current_symlink(processed_root: Path, version_dir: Path) -> None:
    current = processed_root / "current"
    if current.exists() or current.is_symlink():
        if current.is_dir() and not current.is_symlink():
            shutil.rmtree(current)
        else:
            current.unlink()
    rel_target = os.path.relpath(version_dir, processed_root)
    current.symlink_to(rel_target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="/Users/mollykim/projects/D4D")
    parser.add_argument("--version", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--raw-dir", default="")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    raw_dir = Path(args.raw_dir) if args.raw_dir else project_root / "03_data/raw/google_sheets" / args.version
    processed_root = project_root / "03_data/processed"
    version_dir = processed_root / "versions" / args.version
    raw_dir.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)

    if args.download:
        for key in SHEETS:
            download_csv(raw_dir, key)

    track_csv = raw_dir / SHEETS["track_problems"]["raw_filename"]
    glossary_csv = raw_dir / SHEETS["glossary"]["raw_filename"]
    if not track_csv.exists() or not glossary_csv.exists():
        raise SystemExit(f"Missing raw CSV snapshot under {raw_dir}")

    problems, tracks = parse_track_problems(track_csv, args.version)
    glossary_terms = parse_glossary(glossary_csv, args.version)

    write_json(version_dir / "track_problem_statements.json", problems)
    write_json(version_dir / "tracks.json", tracks)
    write_json(version_dir / "glossary_terms.json", glossary_terms)

    problem_fields = [
        "id",
        "track_id",
        "track_title_en",
        "track_title_ko",
        "anchor_partners",
        "expansions",
        "problem_type",
        "problem_type_tags",
        "problem_name",
        "problem_name_ko",
        "problem_name_en",
        "background",
        "challenge",
        "example_approach",
        "example_approach_items",
        "notes",
        "source",
    ]
    glossary_fields = ["id", "category", "term", "english", "description", "related_tracks", "source"]
    write_csv(version_dir / "track_problem_statements.csv", problems, problem_fields)
    write_csv(version_dir / "glossary_terms.csv", glossary_terms, glossary_fields)
    write_track_markdown(version_dir / "track_problem_statements.md", problems, tracks, args.version)
    write_glossary_markdown(project_root / "00_admin/glossary.md", glossary_terms, args.version)
    write_track_markdown(
        project_root / "02_problem_statements/tracks/d4d_track_problem_dataset.md",
        problems,
        tracks,
        args.version,
    )

    manifest = {
        "version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "spreadsheet_id": SPREADSHEET_ID,
            "spreadsheet_title": SPREADSHEET_TITLE,
            "spreadsheet_url": SPREADSHEET_URL,
            "sheets": SHEETS,
            "raw_dir": str(raw_dir),
        },
        "counts": {
            "tracks": len(tracks),
            "track_problem_statements": len(problems),
            "glossary_terms": len(glossary_terms),
        },
        "outputs": {
            "track_problem_statements_json": str(version_dir / "track_problem_statements.json"),
            "track_problem_statements_csv": str(version_dir / "track_problem_statements.csv"),
            "glossary_terms_json": str(version_dir / "glossary_terms.json"),
            "glossary_terms_csv": str(version_dir / "glossary_terms.csv"),
            "track_markdown": str(version_dir / "track_problem_statements.md"),
            "project_track_markdown": str(project_root / "02_problem_statements/tracks/d4d_track_problem_dataset.md"),
            "project_glossary": str(project_root / "00_admin/glossary.md"),
        },
    }
    write_json(version_dir / "dataset_manifest.json", manifest)
    update_current_symlink(processed_root, version_dir)
    write_versions_index(processed_root)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

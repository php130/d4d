#!/usr/bin/env python3
"""Sequentially learn/summarize priority T3 papers.

This script:
1. matches curated priority paper titles against the T3 literature catalog,
2. downloads open PDFs when a direct PDF URL is available,
3. extracts text with pypdf or PyMuPDF,
4. calls Codex CLI to produce structured JSON paper notes,
5. writes a compact learning manifest.

It stores metadata, extracted text, and summaries for research use. It does not
redistribute full papers publicly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import textwrap
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
CODEX_BIN_CANDIDATES = [
    os.environ.get("CODEX_CLI_BIN", ""),
    "/Applications/Codex.app/Contents/Resources/codex",
    shutil.which("codex") or "",
]

PRIORITY_TITLES = [
    "What is Semantic Communication? A View on Conveying Meaning in the Era of Machine Intelligence",
    "A Survey on Semantic Communications for Intelligent Wireless Networks",
    "Semantic Communication Meets Edge Intelligence",
    "A6.2 - Multiplatform sensor fusion. Drawing a common tactical scenario.",
    "Data-Driven Distributed Common Operational Picture from Heterogeneous Platforms using Multi-Agent Reinforcement Learning",
    "Anomaly Detection in Maritime AIS Tracks: A Review of Recent Approaches",
    "Classification-Aided SAR and AIS Data Fusion for Space-Based Maritime Surveillance",
    "Revealing Dark Vessels in the Mauritius Exclusive Economic Zone (EEZ) Using Multi-Temporal SAR and AIS Data",
    "Sensors and AI Techniques for Situational Awareness in Autonomous Ships: A Review",
    "A Common Operational Picture in Support of Situational Awareness for Efficient Emergency Response Operations",
    "Application of Augmented Reality, Mobile Devices, and Sensors for a Combat Entity Quantitative Assessment Supporting Decisions and Situational Awareness Development",
    "Maritime information sharing environment deployment using the advanced multilayered Data Lake capabilities",
    "Deep Learning Enabled Semantic Communication Systems",
    "A survey on semantic communications: Technologies, solutions, applications and challenges",
    "Harnessing the power of Machine learning for AIS Data-Driven maritime Research: A comprehensive review",
    "AI in Maritime Security: Applications, Challenges, Future Directions, and Key Data Sources",
    "AI-Driven Tactical Communications and Networking for Defense: A Survey and Emerging Trends",
    "A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges",
    "Correctness is not Faithfulness in Retrieval Augmented Generation Attributions",
    "Provenance-Aware Knowledge Representation: A Survey of Data Models and Contextualized Knowledge Graphs",
    "Semantic Edge Computing and Semantic Communications in 6G Networks: A Unifying Survey and Research Challenges",
    "A Performance Cost/Benefit Analysis of Adaptive Computing in the Tactical Edge",
    "Detecting Intentional AIS Shutdown in Open Sea Maritime Surveillance Using Self-Supervised Deep Learning",
    "DarkVesselNet: Multi-Modal Remote Sensing and Trajectory Reasoning for Dark Vessel Detection",
    "Design of Antasena: an AI-powered maritime surveillance and anomaly detection system for security decision support",
    "BATMAN: A Brain-like Approach for Tracking Maritime Activity and Nuance",
    "Marine Vision-Based Situational Awareness Using Discriminative Deep Learning: A Survey",
    "Enhancing Maritime Cybersecurity through Operational Technology Sensor Data Fusion: A Comprehensive Survey and Analysis",
    "The common operational picture : A powerful enabler or a cause of severe misunderstanding?",
    "Partnering with technology: the importance of human machine teaming in future MDC2 systems",
    "Security-Aware Sensor Fusion with MATE: the Multi-Agent Trust Estimator",
    "From SLAM to Situational Awareness: Challenges and Survey",
    "Wireless Resource Management in Intelligent Semantic Communication Networks",
    "Semantic Communication for Edge Intelligence: Theoretical Foundations and Implications on Protocols",
    "A Survey on Goal-Oriented Semantic Communication: Techniques, Challenges, and Future Directions",
    "On the Resilience of Underwater Semantic Wireless Communications",
    "Wireless End-to-End Image Transmission System Using Semantic Communications",
    "Semantic Communication Systems for Speech Transmission",
    "Task-Oriented Multi-User Semantic Communications for VQA",
    "Maritime Autonomous Surface Ships: Architecture for Autonomous Navigation Systems",
]


def clean_filename(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z가-힣._-]+", "_", value).strip("_")
    return value[:100] or "paper"


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def load_catalog(root: Path) -> list[dict]:
    path = root / "03_data/processed/literature_t3/current/t3_deep_research_catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_record(records: list[dict], title: str) -> dict | None:
    target = normalize_title(title)
    exact = [r for r in records if normalize_title(r.get("title", "")) == target]
    if exact:
        return exact[0]
    contains = [r for r in records if target[:80] in normalize_title(r.get("title", ""))]
    if contains:
        return contains[0]
    words = set(re.findall(r"[a-z0-9]+", title.lower()))
    best = None
    best_score = 0
    for record in records:
        got = set(re.findall(r"[a-z0-9]+", record.get("title", "").lower()))
        score = len(words & got)
        if score > best_score:
            best = record
            best_score = score
    return best if best_score >= max(4, len(words) // 2) else None


def codex_bin() -> str:
    for candidate in CODEX_BIN_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("Codex CLI not found")


def download_pdf(url: str, path: Path) -> tuple[bool, str]:
    if not url:
        return False, "no pdf_url"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 D4D research",
                "Accept": "application/pdf,*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()
            ctype = response.headers.get("Content-Type", "")
        if len(data) < 1000:
            return False, f"too small: {len(data)} bytes"
        path.write_bytes(data)
        return True, f"downloaded {len(data)} bytes ({ctype})"
    except Exception as exc:
        return False, repr(exc)


def extract_pdf_text(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "", "missing pdf"
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages[:40]:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages)
        if len(text.strip()) > 1000:
            return text, f"pypdf pages={len(reader.pages)} chars={len(text)}"
    except Exception as exc:
        pypdf_error = repr(exc)
    else:
        pypdf_error = "short pypdf extraction"
    try:
        import fitz

        doc = fitz.open(str(path))
        pages = []
        for page in doc[:40]:
            pages.append(page.get_text())
        text = "\n".join(pages)
        if len(text.strip()) > 1000:
            return text, f"fitz pages={len(doc)} chars={len(text)}"
        return text, f"fitz short; pypdf={pypdf_error}"
    except Exception as exc:
        return "", f"extract failed; pypdf={pypdf_error}; fitz={repr(exc)}"


def build_prompt(record: dict, extracted_text: str, status: dict) -> str:
    payload = {
        "metadata": {
            "title": record.get("title"),
            "authors": record.get("authors"),
            "year": record.get("year"),
            "url": record.get("url"),
            "doi": record.get("doi"),
            "venue": record.get("venue"),
            "topic": record.get("topic_label"),
            "abstract": record.get("abstract", ""),
            "download_status": status,
        },
        "paper_text_excerpt": extracted_text[:45000],
    }
    return (
        "You are supporting a D4D hackathon deep-research workflow. "
        "Read the provided paper metadata/text and return one strict JSON object, no markdown. "
        "Do not quote long passages. Paraphrase. Focus on how this paper helps build "
        "'Resilient Maritime COP over Denied Networks' / a T3 semantic COP system.\n\n"
        "JSON schema:\n"
        "{\n"
        '  "title": string,\n'
        '  "read_status": "full_text"|"abstract_only"|"partial_text",\n'
        '  "one_line_takeaway": string,\n'
        '  "d4d_relevance": string,\n'
        '  "key_concepts": [string],\n'
        '  "input_data": [string],\n'
        '  "methods_or_architecture": [string],\n'
        '  "outputs_metrics": [string],\n'
        '  "prototype_hooks": [string],\n'
        '  "pitch_evidence": [string],\n'
        '  "limitations_risks": [string],\n'
        '  "confidence": "high"|"medium"|"low"\n'
        "}\n\n"
        f"INPUT:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def run_codex(prompt: str, output_path: Path, timeout: int = 180) -> tuple[bool, str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        codex_bin(),
        "exec",
        "--cd",
        str(PROJECT_ROOT),
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        "gpt-5.5",
        "--output-last-message",
        str(output_path),
        "-",
    ]
    try:
        proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=timeout)
        if proc.returncode != 0:
            return False, proc.stderr[-2000:] or proc.stdout[-2000:]
        return True, "ok"
    except Exception as exc:
        return False, repr(exc)


def markdown_note(note: dict, record: dict) -> str:
    def bullets(items):
        return "\n".join(f"- {x}" for x in items) if items else "- "

    return f"""# {note.get('title') or record.get('title')}

## Metadata

- Year: {record.get('year')}
- URL: {record.get('url')}
- DOI: {record.get('doi') or '-'}
- Read status: {note.get('read_status')}

## One-line Takeaway

{note.get('one_line_takeaway', '')}

## D4D Relevance

{note.get('d4d_relevance', '')}

## Key Concepts

{bullets(note.get('key_concepts', []))}

## Input Data

{bullets(note.get('input_data', []))}

## Methods Or Architecture

{bullets(note.get('methods_or_architecture', []))}

## Outputs / Metrics

{bullets(note.get('outputs_metrics', []))}

## Prototype Hooks

{bullets(note.get('prototype_hooks', []))}

## Pitch Evidence

{bullets(note.get('pitch_evidence', []))}

## Limitations / Risks

{bullets(note.get('limitations_risks', []))}

## Confidence

{note.get('confidence', '')}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--start", type=int, default=1, help="1-based priority index to start from")
    parser.add_argument("--skip-codex", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    records = load_catalog(root)
    raw_dir = root / "03_data/raw/literature_t3_learning" / version
    out_dir = root / "01_research/literature/t3_deep_research/paper_notes"
    json_dir = root / "03_data/processed/literature_t3_learning" / version
    text_dir = raw_dir / "extracted_text"
    pdf_dir = raw_dir / "pdfs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limit": args.limit,
        "papers": [],
    }

    selected = PRIORITY_TITLES[args.start - 1 : args.limit]
    for idx, title in enumerate(selected, start=args.start):
        record = find_record(records, title)
        if not record:
            manifest["papers"].append({"priority": idx, "requested_title": title, "ok": False, "error": "not found"})
            continue
        slug = f"{idx:02d}_{clean_filename(record['title'])}"
        pdf_path = pdf_dir / f"{slug}.pdf"
        text_path = text_dir / f"{slug}.txt"
        summary_json_path = json_dir / f"{slug}.json"
        note_path = out_dir / f"{slug}.md"

        downloaded, download_msg = download_pdf(record.get("pdf_url", ""), pdf_path)
        text = ""
        extract_msg = ""
        if downloaded:
            text, extract_msg = extract_pdf_text(pdf_path)
        if not text.strip():
            text = record.get("abstract", "")
            extract_msg = extract_msg or "abstract fallback"
        text_path.write_text(text, encoding="utf-8")
        status = {
            "downloaded_pdf": downloaded,
            "download_message": download_msg,
            "extract_message": extract_msg,
            "text_chars": len(text),
        }

        if args.skip_codex:
            note = {
                "title": record.get("title"),
                "read_status": "abstract_only" if not downloaded else "partial_text",
                "one_line_takeaway": record.get("abstract", "")[:300],
                "d4d_relevance": "Pending manual synthesis.",
                "key_concepts": [],
                "input_data": [],
                "methods_or_architecture": [],
                "outputs_metrics": [],
                "prototype_hooks": [],
                "pitch_evidence": [],
                "limitations_risks": [],
                "confidence": "low",
            }
            summary_json_path.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            prompt = build_prompt(record, text, status)
            ok, msg = run_codex(prompt, summary_json_path)
            if not ok:
                note = {
                    "title": record.get("title"),
                    "read_status": "abstract_only" if not downloaded else "partial_text",
                    "one_line_takeaway": record.get("abstract", "")[:300],
                    "d4d_relevance": f"Codex summarization failed: {msg}",
                    "key_concepts": [],
                    "input_data": [],
                    "methods_or_architecture": [],
                    "outputs_metrics": [],
                    "prototype_hooks": [],
                    "pitch_evidence": [],
                    "limitations_risks": [],
                    "confidence": "low",
                }
                summary_json_path.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                raw = summary_json_path.read_text(encoding="utf-8")
                try:
                    note = json.loads(raw)
                except Exception:
                    cleaned = raw.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
                        cleaned = re.sub(r"```$", "", cleaned).strip()
                    note = json.loads(cleaned)
                    summary_json_path.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")

        note_path.write_text(markdown_note(note, record), encoding="utf-8")
        manifest["papers"].append(
            {
                "priority": idx,
                "title": record.get("title"),
                "url": record.get("url"),
                "pdf_url": record.get("pdf_url"),
                "status": status,
                "summary_json": str(summary_json_path),
                "note_md": str(note_path),
            }
        )
        time.sleep(0.5)

    (json_dir / "learning_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = root / "03_data/processed/literature_t3_learning/current"
    latest.parent.mkdir(parents=True, exist_ok=True)
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(Path(version))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

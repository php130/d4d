#!/usr/bin/env python3
"""Export the S-DOT drone demo dataset into a Palantir/AIP handoff bundle.

This is not a proprietary Foundry import format. It is a clean, versioned
handoff bundle: CSV object tables, link tables, action definitions, and AIP
workflow cards that can be mapped into a Foundry Ontology or another graph/C2
backend.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "03_data" / "samples" / "sdot_drone_semantic_ops" / "mock_dataset.json"
OUT_DIR = ROOT / "07_deliverables" / "palantir" / "sdot_drone_semantic_ops"
OBJECT_DIR = OUT_DIR / "objects"


def jdump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return {"path": str(path.relative_to(OUT_DIR)), "records": len(rows), "sha256": sha256(path)}


def write_json(path: Path, payload: Any) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    records = len(payload) if isinstance(payload, list) else len(payload.keys()) if isinstance(payload, dict) else 1
    return {"path": str(path.relative_to(OUT_DIR)), "records": records, "sha256": sha256(path)}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def export_objects(dataset: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    file_manifest: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []

    asset_rows = [
        {
            "asset_id": asset["asset_id"],
            "asset_code": asset["asset_code"],
            "asset_type": asset["asset_type"],
            "sensor_modalities_json": jdump(asset.get("sensor_modalities", [])),
            "comm_state": asset.get("comm_state"),
            "battery_pct": asset.get("battery_pct"),
            "last_contact_time": asset.get("last_contact_time"),
            "local_cache_status": asset.get("local_cache_status"),
            "sdot_outbox_count": asset.get("sdot_outbox_count"),
        }
        for asset in dataset["drone_assets"]
    ]
    file_manifest.append(write_csv(OBJECT_DIR / "DroneAsset.csv", asset_rows))

    case_rows = [
        {
            "case_id": case["case_id"],
            "label_ko": case["label_ko"],
            "scenario_summary_ko": case.get("scenario_summary_ko"),
            "default_mode": case.get("default_mode"),
            "primary": case.get("primary"),
        }
        for case in dataset["simulation_cases"]
    ]
    file_manifest.append(write_csv(OBJECT_DIR / "SimulationCase.csv", case_rows))

    event_rows = []
    for event in dataset["semantic_events"]:
        event_rows.append({
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "severity": event["severity"],
            "asset_id": event["asset_id"],
            "case_ids_json": jdump(event.get("case_ids", [])),
            "time": event["time"],
            "summary": event["summary"],
            "why_it_matters": event.get("why_it_matters"),
            "recommended_action": event.get("recommended_action"),
            "priority": event["priority"],
            "raw_bytes": event.get("raw_bytes"),
            "semantic_bytes": event.get("semantic_bytes"),
            "priority_features_json": jdump(event.get("priority_features", {})),
            "evidence_refs_json": jdump(event.get("evidence_refs", [])),
        })
        links.append(link("DroneAsset", event["asset_id"], "SemanticEvent", event["event_id"], "asset_emits_event"))
        for case_id in event.get("case_ids", []):
            links.append(link("SimulationCase", case_id, "SemanticEvent", event["event_id"], "case_contains_event"))
        for ref in event.get("evidence_refs", []):
            target_type = evidence_type(dataset, ref)
            if target_type:
                links.append(link("SemanticEvent", event["event_id"], target_type, ref, "event_evidenced_by"))
    file_manifest.append(write_csv(OBJECT_DIR / "SemanticEvent.csv", event_rows))

    packet_rows = []
    for packet in dataset["semantic_packets"]:
        packet_rows.append({
            "packet_id": packet["packet_id"],
            "event_id": packet["event_id"],
            "asset_id": packet["asset_id"],
            "payload_tier": packet["payload_tier"],
            "case_ids_json": jdump(packet.get("case_ids", [])),
            "priority": packet["priority"],
            "bytes_raw_represented": packet.get("bytes_raw_represented"),
            "bytes_semantic": packet.get("bytes_semantic"),
            "requires_ack": packet.get("requires_ack"),
            "rejoin_audit_required": packet.get("rejoin_audit_required"),
        })
        links.append(link("SemanticEvent", packet["event_id"], "SemanticPacket", packet["packet_id"], "event_encoded_as_packet"))
        links.append(link("DroneAsset", packet["asset_id"], "SemanticPacket", packet["packet_id"], "asset_has_packet"))
    file_manifest.append(write_csv(OBJECT_DIR / "SemanticPacket.csv", packet_rows))

    observation_rows = []
    for observation in dataset["raw_observations"]:
        observation_rows.append({
            "observation_id": observation["observation_id"],
            "asset_id": observation["asset_id"],
            "source_id": observation.get("source_id"),
            "sensor_type": observation.get("sensor_type"),
            "time": observation.get("time"),
            "raw_ref": observation.get("raw_ref"),
            "raw_bytes": observation.get("raw_bytes"),
            "summary": observation.get("summary"),
            "retention_policy": observation.get("retention_policy"),
        })
        links.append(link("DroneAsset", observation["asset_id"], "RawObservation", observation["observation_id"], "asset_has_observation"))
    file_manifest.append(write_csv(OBJECT_DIR / "RawObservation.csv", observation_rows))

    detection_rows = []
    for detection in dataset["edge_detections"]:
        detection_rows.append({
            "detection_id": detection["detection_id"],
            "asset_id": detection["asset_id"],
            "candidate_type": detection.get("candidate_type"),
            "model_or_rule": detection.get("model_or_rule"),
            "confidence": detection.get("confidence"),
            "features_json": jdump(detection.get("features", {})),
            "observation_refs_json": jdump(detection.get("observation_refs", [])),
        })
        links.append(link("DroneAsset", detection["asset_id"], "EdgeDetection", detection["detection_id"], "asset_has_detection"))
        for observation_ref in detection.get("observation_refs", []):
            links.append(link("EdgeDetection", detection["detection_id"], "RawObservation", observation_ref, "detection_uses_observation"))
    file_manifest.append(write_csv(OBJECT_DIR / "EdgeDetection.csv", detection_rows))

    hypothesis_rows = []
    for hypothesis in dataset["jamming_hypotheses"]:
        hypothesis_rows.append({
            "hypothesis_id": hypothesis["hypothesis_id"],
            "asset_id": hypothesis["asset_id"],
            "time": hypothesis.get("time"),
            "label": hypothesis.get("label"),
            "score": hypothesis.get("score"),
            "inputs_json": jdump(hypothesis.get("inputs", {})),
            "caveat": hypothesis.get("caveat"),
        })
        links.append(link("DroneAsset", hypothesis["asset_id"], "JammingHypothesis", hypothesis["hypothesis_id"], "asset_has_hypothesis"))
    file_manifest.append(write_csv(OBJECT_DIR / "JammingHypothesis.csv", hypothesis_rows))

    eval_rows = []
    for evaluation in dataset["case_evaluations"].values():
        eval_id = f"eval_{evaluation['case_id']}"
        eval_rows.append({"evaluation_id": eval_id, **evaluation})
        links.append(link("SimulationCase", evaluation["case_id"], "CaseEvaluation", eval_id, "case_has_evaluation"))
    file_manifest.append(write_csv(OBJECT_DIR / "CaseEvaluation.csv", eval_rows))

    eval_point_rows = []
    for case_id, bundle in dataset["case_evaluation_series"].items():
        for point in bundle["series"]:
            point_id = f"eval_point_{case_id}_{point['t_seconds']:03d}"
            eval_point_rows.append({"point_id": point_id, "case_id": case_id, **point})
            links.append(link("SimulationCase", case_id, "CaseEvaluationPoint", point_id, "case_has_eval_point"))
    file_manifest.append(write_csv(OBJECT_DIR / "CaseEvaluationPoint.csv", eval_point_rows))

    kalman_rows = []
    for case_id, trace_bundle in dataset["kalman_estimator_traces"].items():
        for point in trace_bundle["trace"]:
            point_id = f"kalman_{case_id}_{point['t_seconds']:03d}"
            kalman_rows.append({
                "trace_point_id": point_id,
                "case_id": case_id,
                "time": point["time"],
                "t_seconds": point["t_seconds"],
                "innovation_nis": point["innovation_nis"],
                "update_decision": point["update_decision"],
                "gate_threshold": point["gate_threshold"],
                "measurement_sigma_m": point["measurement_sigma_m"],
                "position_sigma_major_m": point["position_sigma_major_m"],
                "estimate_error_m": point["estimate_error_m"],
                "reported_error_m": point["reported_error_m"],
                "prior_position_json": jdump(point["prior_position_m"]),
                "estimated_position_json": jdump(point["estimated_position_m"]),
                "reported_position_json": jdump(point["reported_position_m"]),
                "innovation_json": jdump(point["innovation_m"]),
                "semantic_meaning_ko": point["semantic_meaning_ko"],
            })
            links.append(link("SimulationCase", case_id, "KalmanTracePoint", point_id, "case_has_kalman_trace"))
    file_manifest.append(write_csv(OBJECT_DIR / "KalmanTracePoint.csv", kalman_rows))

    routing_rows = []
    for mode, result in dataset["routing_results"].items():
        for packet in result["packets"]:
            routing_id = f"route_{mode}_{packet['packet_id']}"
            routing_rows.append({
                "routing_id": routing_id,
                "network_mode": mode,
                "packet_id": packet["packet_id"],
                "event_id": packet["event_id"],
                "asset_id": packet["asset_id"],
                "decision": packet["decision"],
                "payload_tier": packet["payload_tier"],
                "priority": packet["priority"],
                "bytes_semantic": packet["bytes_semantic"],
                "bytes_raw_represented": packet["bytes_raw_represented"],
            })
            links.append(link("SemanticPacket", packet["packet_id"], "RoutingDecision", routing_id, "packet_has_routing_decision"))
    file_manifest.append(write_csv(OBJECT_DIR / "RoutingDecision.csv", routing_rows))

    audit_rows = []
    for audit in dataset["rejoin_audits"]:
        audit_rows.append({
            "audit_id": audit["audit_id"],
            "asset_id": audit["asset_id"],
            "case_id": audit["case_id"],
            "status": audit["status"],
            "discrepancy_m": audit["discrepancy_m"],
            "inside_uncertainty_envelope": audit["inside_uncertainty_envelope"],
            "prediction_before_rejoin_json": jdump(audit["prediction_before_rejoin"]),
            "simulated_truth_at_rejoin_json": jdump(audit["simulated_truth_at_rejoin"]),
            "expected_sync_order_json": jdump(audit["expected_sync_order"]),
        })
        links.append(link("DroneAsset", audit["asset_id"], "RejoinAudit", audit["audit_id"], "asset_has_rejoin_audit"))
        links.append(link("SimulationCase", audit["case_id"], "RejoinAudit", audit["audit_id"], "case_has_rejoin_audit"))
    file_manifest.append(write_csv(OBJECT_DIR / "RejoinAudit.csv", audit_rows))

    file_manifest.append(write_csv(OUT_DIR / "links.csv", links, ["source_type", "source_id", "target_type", "target_id", "relationship"]))
    return file_manifest, links


def link(source_type: str, source_id: str, target_type: str, target_id: str, relationship: str) -> dict[str, str]:
    return {
        "source_type": source_type,
        "source_id": source_id,
        "target_type": target_type,
        "target_id": target_id,
        "relationship": relationship,
    }


def evidence_type(dataset: dict[str, Any], ref: str) -> str | None:
    if any(item["observation_id"] == ref for item in dataset["raw_observations"]):
        return "RawObservation"
    if any(item["detection_id"] == ref for item in dataset["edge_detections"]):
        return "EdgeDetection"
    if any(item["hypothesis_id"] == ref for item in dataset["jamming_hypotheses"]):
        return "JammingHypothesis"
    return None


def ontology_model(dataset: dict[str, Any]) -> dict[str, Any]:
    object_types = [
        object_type("DroneAsset", "asset_id", ["asset_code", "asset_type", "comm_state", "battery_pct", "last_contact_time"]),
        object_type("SimulationCase", "case_id", ["label_ko", "scenario_summary_ko", "default_mode", "primary"]),
        object_type("SemanticEvent", "event_id", ["event_type", "severity", "time", "summary", "priority", "recommended_action"]),
        object_type("SemanticPacket", "packet_id", ["payload_tier", "priority", "bytes_semantic", "requires_ack", "rejoin_audit_required"]),
        object_type("RawObservation", "observation_id", ["sensor_type", "time", "raw_bytes", "summary", "retention_policy"]),
        object_type("EdgeDetection", "detection_id", ["candidate_type", "model_or_rule", "confidence"]),
        object_type("JammingHypothesis", "hypothesis_id", ["label", "score", "time", "caveat"]),
        object_type("CaseEvaluation", "evaluation_id", ["case_id", "max_residual_m", "max_nis", "false_alarm_risk", "confidence"]),
        object_type("CaseEvaluationPoint", "point_id", ["case_id", "t_seconds", "nis", "residual_m", "threshold_state", "action_hint_ko"]),
        object_type("KalmanTracePoint", "trace_point_id", ["case_id", "t_seconds", "innovation_nis", "update_decision", "estimate_error_m", "reported_error_m"]),
        object_type("RoutingDecision", "routing_id", ["network_mode", "decision", "payload_tier", "priority", "bytes_semantic"]),
        object_type("RejoinAudit", "audit_id", ["asset_id", "case_id", "status", "discrepancy_m", "inside_uncertainty_envelope"]),
    ]
    return {
        "bundle_type": "palantir_aip_handoff",
        "dataset_id": dataset["metadata"]["dataset_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Handoff model for mapping into Foundry Ontology/AIP. Not an official Palantir import specification.",
        "safety_boundary": dataset["metadata"]["safety_note"],
        "object_types": object_types,
        "relationship_types": [
            "asset_emits_event",
            "case_contains_event",
            "event_evidenced_by",
            "event_encoded_as_packet",
            "asset_has_observation",
            "asset_has_detection",
            "asset_has_hypothesis",
            "case_has_evaluation",
            "case_has_eval_point",
            "case_has_kalman_trace",
            "packet_has_routing_decision",
            "asset_has_rejoin_audit",
        ],
        "action_types": actions(),
    }


def object_type(name: str, primary_key: str, properties: list[str]) -> dict[str, Any]:
    return {"name": name, "primary_key": primary_key, "display_name": name, "properties": properties}


def actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": "approve_semantic_packet",
            "display_name_ko": "시맨틱 패킷 전송 승인",
            "target_object": "SemanticPacket",
            "parameters": ["operator_id", "approval_reason", "network_mode"],
            "expected_effect": "Set routing decision override and create an audit log entry.",
        },
        {
            "action_id": "mark_measurement_contested",
            "display_name_ko": "보고 위치 contested 표시",
            "target_object": "KalmanTracePoint",
            "parameters": ["operator_id", "reason_code"],
            "expected_effect": "Mark the measurement as contested when innovation gate rejects it.",
        },
        {
            "action_id": "request_rejoin_audit",
            "display_name_ko": "재연결 감사 요청",
            "target_object": "DroneAsset",
            "parameters": ["operator_id", "case_id", "priority"],
            "expected_effect": "Queue a RejoinAudit workflow and sync semantic packets before raw cache.",
        },
        {
            "action_id": "change_ddil_mode",
            "display_name_ko": "DDIL 모드 변경",
            "target_object": "SimulationCase",
            "parameters": ["operator_id", "new_network_mode", "valid_until"],
            "expected_effect": "Recompute routing decisions for the selected network mode.",
        },
    ]


def workflow_cards(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "card_id": "operator_situation_summary",
            "title_ko": "오퍼레이터 상황 요약",
            "input_objects": ["DroneAsset", "SimulationCase", "SemanticEvent", "KalmanTracePoint"],
            "prompt_intent": "선택 케이스에서 현재 드론 상태, contested measurement, 전송해야 할 S-DOT 패킷을 한국어로 요약합니다.",
            "guardrails": ["교란 원점/위치 추정 금지", "합성 데이터임을 명시", "확정 표현 대신 가설/신뢰도 표현 사용"],
        },
        {
            "card_id": "packet_priority_review",
            "title_ko": "S-DOT 패킷 우선순위 검토",
            "input_objects": ["SemanticEvent", "SemanticPacket", "RoutingDecision"],
            "prompt_intent": "DDIL 모드별로 어떤 패킷을 전송/보류/로컬 보존해야 하는지 근거와 함께 제안합니다.",
            "guardrails": ["원본 raw data 외부 공개 금지", "API key/token 출력 금지"],
        },
        {
            "card_id": "rejoin_audit_assistant",
            "title_ko": "재연결 감사 보조",
            "input_objects": ["RejoinAudit", "KalmanTracePoint", "RawObservation", "SemanticPacket"],
            "prompt_intent": "재연결 이후 예측 trace와 캐시 원본 간 차이를 감사하고 동기화 순서를 추천합니다.",
            "guardrails": ["실제 작전 위치 또는 실제 군사 데이터와 연결 금지"],
        },
    ]


def write_readme(dataset: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    object_lines = [
        f"- `{item['path']}`: {item['records']} records"
        for item in manifest["object_files"]
    ]
    lines = [
        "# S-DOT Drone Palantir/AIP Handoff Bundle",
        "",
        f"- Generated: {manifest['generated_at']}",
        f"- Source dataset: `{dataset['metadata']['dataset_id']}`",
        "- Status: synthetic hackathon demo handoff bundle",
        "",
        "## Purpose",
        "",
        "This bundle maps the S-DOT drone demo into object tables, relationship links, action definitions, and AIP workflow cards.",
        "",
        "It is intended for Foundry Ontology/AIP planning, transform prototyping, or any graph-backed C2 workflow. It is not an official Palantir import specification.",
        "",
        "## Contents",
        "",
        "- `objects/*.csv`: object tables for assets, cases, semantic events, packets, observations, hypotheses, Kalman trace points, routing decisions, and audits",
        "- `links.csv`: graph-style object relationships",
        "- `ontology_model.json`: proposed object/relationship/action model",
        "- `aip_workflow_cards.json`: AIP assistant workflow cards and guardrails",
        "- `bundle_manifest.json`: record counts and file hashes",
        "",
        "## Object Tables",
        "",
        *object_lines,
        "",
        "## Safety Boundary",
        "",
        dataset["metadata"]["safety_note"],
        "",
        "Do not connect this bundle to real military routes, real EW emitter details, sensitive infrastructure coordinates, or personal data.",
    ]
    readme = OUT_DIR / "README.md"
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": str(readme.relative_to(OUT_DIR)), "records": 1, "sha256": sha256(readme)}


def main() -> None:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OBJECT_DIR.mkdir(parents=True, exist_ok=True)

    files, links = export_objects(dataset)
    files.append(write_json(OUT_DIR / "ontology_model.json", ontology_model(dataset)))
    files.append(write_json(OUT_DIR / "aip_workflow_cards.json", workflow_cards(dataset)))

    manifest = {
        "bundle_id": "sdot_drone_semantic_ops_palantir_handoff_v0_1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(DATASET_PATH.relative_to(ROOT)),
        "dataset_id": dataset["metadata"]["dataset_id"],
        "safety_note": dataset["metadata"]["safety_note"],
        "object_files": [item for item in files if item["path"].startswith("objects/")],
        "relationship_count": len(links),
        "manifest_hash_note": "`bundle_manifest.json` is excluded from the file hash list to avoid self-referential hashing.",
        "files": files,
    }
    files.append(write_readme(dataset, manifest))
    manifest["files"] = files
    manifest["generated_file_count_excluding_manifest"] = len(files)
    write_json(OUT_DIR / "bundle_manifest.json", manifest)

    print(json.dumps({
        "bundle_dir": str(OUT_DIR),
        "bundle_id": manifest["bundle_id"],
        "dataset_id": manifest["dataset_id"],
        "object_files": len(manifest["object_files"]),
        "relationship_count": manifest["relationship_count"],
        "generated_file_count_excluding_manifest": manifest["generated_file_count_excluding_manifest"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

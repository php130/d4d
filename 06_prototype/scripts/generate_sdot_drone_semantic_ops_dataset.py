#!/usr/bin/env python3
"""Generate a drone-first S-DOT semantic transmission mock dataset.

The dataset is synthetic and intended for defensive hackathon simulation only.
It does not contain real drone routes, military assets, EW emitter data, or
sensitive coordinates.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "03_data" / "samples" / "sdot_drone_semantic_ops"
OUT_JSON = DATA_DIR / "mock_dataset.json"
OUT_JS = DATA_DIR / "mock_dataset.js"

BASE_TIME = datetime(2026, 7, 4, 3, 0, tzinfo=timezone.utc)

NETWORK_MODES = {
    "full_sync": {
        "label": "Full Sync",
        "bandwidth_kbps": 4096,
        "latency_ms": 80,
        "packet_loss_pct": 0.5,
        "send_threshold": 0.10,
        "defer_threshold": 0.05,
    },
    "delta_sync": {
        "label": "Delta Sync",
        "bandwidth_kbps": 512,
        "latency_ms": 220,
        "packet_loss_pct": 4,
        "send_threshold": 0.32,
        "defer_threshold": 0.18,
    },
    "semantic_summary": {
        "label": "Semantic Summary",
        "bandwidth_kbps": 96,
        "latency_ms": 950,
        "packet_loss_pct": 14,
        "send_threshold": 0.58,
        "defer_threshold": 0.36,
    },
    "store_forward": {
        "label": "Store Forward",
        "bandwidth_kbps": 24,
        "latency_ms": 1800,
        "packet_loss_pct": 35,
        "send_threshold": 0.84,
        "defer_threshold": 0.45,
    },
    "local_only": {
        "label": "Local Only",
        "bandwidth_kbps": 0,
        "latency_ms": None,
        "packet_loss_pct": 100,
        "send_threshold": 1.01,
        "defer_threshold": 1.01,
    },
}

NIS_WATCH_THRESHOLD = 9.21
NIS_CRITICAL_THRESHOLD = 16.0
HYPOTHESIS_WATCH_THRESHOLD = 0.60

PLATFORM_HANDOFF = {
    "bundle_id": "sdot_drone_semantic_ops_palantir_handoff_v0_1",
    "bundle_path": "07_deliverables/palantir/sdot_drone_semantic_ops",
    "handoff_type": "Foundry/AIP planning bundle",
    "official_import_spec": False,
    "object_tables": [
        "DroneAsset",
        "SimulationCase",
        "SemanticEvent",
        "SemanticPacket",
        "RawObservation",
        "EdgeDetection",
        "JammingHypothesis",
        "CaseEvaluation",
        "CaseEvaluationPoint",
        "KalmanTracePoint",
        "RoutingDecision",
        "RejoinAudit",
    ],
    "relationship_links": 225,
    "action_definitions": [
        "approve_semantic_packet",
        "mark_measurement_contested",
        "request_rejoin_audit",
        "change_ddil_mode",
    ],
    "aip_workflow_cards": [
        "operator_situation_summary",
        "packet_priority_review",
        "rejoin_audit_assistant",
    ],
    "guardrails_ko": [
        "공식 Palantir import spec이 아니라 Foundry/AIP 매핑용 handoff bundle입니다.",
        "모든 데이터는 합성이며 실제 군사 위치, EW 원점, 민감 인프라 좌표를 포함하지 않습니다.",
        "교란 판단은 확정이 아니라 방어적 가설 점수와 근거 체인으로 표현합니다.",
    ],
}


def iso(seconds: int) -> str:
    return (BASE_TIME + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


def round_dict(values: dict[str, float], digits: int = 3) -> dict[str, float]:
    return {key: round(value, digits) for key, value in values.items()}


def position_at(t: int, velocity: tuple[float, float, float], wind: tuple[float, float]) -> dict[str, float]:
    north = velocity[0] * t + wind[0] * t
    east = velocity[1] * t + wind[1] * t
    down = -120 + velocity[2] * t
    return round_dict({"north": north, "east": east, "down": down}, 2)


def uncertainty(t_since_contact: int, wind_sigma: float, accel_sigma: float = 0.08, vel_sigma: float = 0.9) -> dict[str, float]:
    sigma0 = 18.0
    sigma2 = sigma0**2 + vel_sigma**2 * t_since_contact**2 + 0.25 * accel_sigma**2 * t_since_contact**4 + wind_sigma**2 * t_since_contact**2
    major = math.sqrt(sigma2)
    minor = max(25.0, major * 0.42)
    return {"major": round(major, 2), "minor": round(minor, 2), "bearing_deg": 76}


def nis_score(residual_m: float, sigma_major_m: float) -> float:
    # Simplified 2D normalized innovation score for demo explainability.
    sigma = max(1.0, sigma_major_m * 0.55)
    return round((residual_m / sigma) ** 2, 2)


def jamming_score(inputs: dict[str, float]) -> float:
    score = (
        0.25 * inputs["gnss_quality_drop"]
        + 0.20 * inputs["link_quality_drop"]
        + 0.20 * inputs["normalized_position_residual"]
        + 0.15 * inputs["heartbeat_gap_score"]
        + 0.10 * inputs["imu_gnss_disagreement"]
        + 0.10 * inputs["context_risk"]
    )
    return round(min(1.0, max(0.0, score)), 3)


def score_event(features: dict[str, float]) -> float:
    weights = {
        "flight_safety": 0.25,
        "navigation_integrity": 0.24,
        "mission_relevance": 0.21,
        "link_survivability": 0.18,
        "provenance_audit": 0.12,
    }
    return round(sum(features[key] * weight for key, weight in weights.items()), 3)


def measurement_sigma_m(gnss_quality: str) -> float:
    if gnss_quality == "normal":
        return 6.0
    if gnss_quality == "nominal_but_inconsistent":
        return 6.0
    if gnss_quality == "degraded":
        return 18.0
    return 42.0


def predict_axis(state: list[float], covariance: list[list[float]], dt: float, accel_sigma: float = 0.35) -> tuple[list[float], list[list[float]]]:
    pos, vel = state
    p00, p01 = covariance[0]
    p10, p11 = covariance[1]
    q = accel_sigma**2
    q00 = 0.25 * dt**4 * q
    q01 = 0.5 * dt**3 * q
    q11 = dt**2 * q
    predicted_state = [pos + vel * dt, vel]
    predicted_covariance = [
        [p00 + dt * (p10 + p01) + dt**2 * p11 + q00, p01 + dt * p11 + q01],
        [p10 + dt * p11 + q01, p11 + q11],
    ]
    return predicted_state, predicted_covariance


def update_axis(state: list[float], covariance: list[list[float]], measurement: float, measurement_variance: float) -> tuple[list[float], list[list[float]], float, float]:
    innovation = measurement - state[0]
    innovation_variance = covariance[0][0] + measurement_variance
    k0 = covariance[0][0] / innovation_variance
    k1 = covariance[1][0] / innovation_variance
    updated_state = [state[0] + k0 * innovation, state[1] + k1 * innovation]
    p00, p01 = covariance[0]
    p10, p11 = covariance[1]
    updated_covariance = [
        [(1 - k0) * p00, (1 - k0) * p01],
        [p10 - k1 * p00, p11 - k1 * p01],
    ]
    # Keep the tiny 2x2 covariance symmetric for readability in the exported trace.
    off_diag = 0.5 * (updated_covariance[0][1] + updated_covariance[1][0])
    updated_covariance[0][1] = off_diag
    updated_covariance[1][0] = off_diag
    return updated_state, updated_covariance, innovation, innovation_variance


def build_kalman_trace(case_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 2:
        return {"case_id": case_id, "trace": []}
    first = rows[0]["reported_position_m"]
    second = rows[1]["reported_position_m"]
    dt0 = max(1, rows[1]["t_seconds"] - rows[0]["t_seconds"])
    north_state = [first["north"], (second["north"] - first["north"]) / dt0]
    east_state = [first["east"], (second["east"] - first["east"]) / dt0]
    north_cov = [[36.0, 0.0], [0.0, 2.25]]
    east_cov = [[36.0, 0.0], [0.0, 2.25]]
    trace = []
    previous_t = rows[0]["t_seconds"]

    for index, row in enumerate(rows):
        dt = 0 if index == 0 else row["t_seconds"] - previous_t
        previous_t = row["t_seconds"]
        if dt:
            north_state, north_cov = predict_axis(north_state, north_cov, dt)
            east_state, east_cov = predict_axis(east_state, east_cov, dt)

        prior_north = north_state[0]
        prior_east = east_state[0]
        reported = row["reported_position_m"]
        truth = row["truth_position_m"]
        sigma = measurement_sigma_m(row["gnss_quality"])
        measurement_variance = sigma**2
        innovation_n = reported["north"] - prior_north
        innovation_e = reported["east"] - prior_east
        innovation_variance_n = north_cov[0][0] + measurement_variance
        innovation_variance_e = east_cov[0][0] + measurement_variance
        innovation_nis = innovation_n**2 / innovation_variance_n + innovation_e**2 / innovation_variance_e
        update_used = innovation_nis <= NIS_WATCH_THRESHOLD
        if update_used:
            north_state, north_cov, _, _ = update_axis(north_state, north_cov, reported["north"], measurement_variance)
            east_state, east_cov, _, _ = update_axis(east_state, east_cov, reported["east"], measurement_variance)
            update_decision = "accepted"
            semantic_meaning = "보고 위치가 예측 공분산 안에 있어 추정기에 반영합니다."
        else:
            update_decision = "rejected_gate"
            semantic_meaning = "보고 위치가 예측 공분산을 벗어나 추정기는 관성/예측 상태를 유지합니다."

        estimate = {"north": north_state[0], "east": east_state[0], "down": truth["down"]}
        estimate_error_m = math.dist([estimate["north"], estimate["east"]], [truth["north"], truth["east"]])
        reported_error_m = math.dist([reported["north"], reported["east"]], [truth["north"], truth["east"]])
        position_sigma_major_m = 2 * math.sqrt(max(north_cov[0][0], east_cov[0][0]))
        trace.append({
            "time": row["time"],
            "t_seconds": row["t_seconds"],
            "prior_position_m": round_dict({"north": prior_north, "east": prior_east, "down": truth["down"]}, 2),
            "estimated_position_m": round_dict(estimate, 2),
            "reported_position_m": row["reported_position_m"],
            "truth_position_m": row["truth_position_m"],
            "innovation_m": round_dict({"north": innovation_n, "east": innovation_e, "norm": math.hypot(innovation_n, innovation_e)}, 2),
            "innovation_nis": round(innovation_nis, 2),
            "measurement_sigma_m": sigma,
            "position_sigma_major_m": round(position_sigma_major_m, 2),
            "estimate_error_m": round(estimate_error_m, 2),
            "reported_error_m": round(reported_error_m, 2),
            "update_decision": update_decision,
            "gate_threshold": NIS_WATCH_THRESHOLD,
            "semantic_meaning_ko": semantic_meaning,
        })

    max_innovation = max(trace, key=lambda item: item["innovation_nis"])
    max_estimate_error = max(trace, key=lambda item: item["estimate_error_m"])
    rejected_count = sum(1 for item in trace if item["update_decision"] == "rejected_gate")
    return {
        "case_id": case_id,
        "filter_name": "constant_velocity_kalman_filter_v0",
        "state_vector": ["north_m", "east_m", "north_velocity_mps", "east_velocity_mps"],
        "measurement": "reported_position_m",
        "gate_rule": "innovation_nis <= 9.21",
        "trace": trace,
        "summary": {
            "points": len(trace),
            "rejected_measurements": rejected_count,
            "max_innovation_nis": max_innovation["innovation_nis"],
            "max_innovation_time": max_innovation["time"],
            "max_estimate_error_m": max_estimate_error["estimate_error_m"],
            "max_estimate_error_time": max_estimate_error["time"],
        },
    }


def build_timeline(case_id: str) -> list[dict[str, Any]]:
    velocity = (12.0, 3.0, 0.0)
    wind_by_case = {
        "case_a_normal": (0.2, -0.1),
        "case_b_link_degraded": (0.3, -0.1),
        "case_c_gnss_jamming_suspected": (0.8, -0.35),
        "case_d_spoofing_like_inconsistency": (0.25, -0.05),
        "case_e_rejoin_audit": (0.8, -0.35),
    }
    wind = wind_by_case[case_id]
    last_contact = 40 if case_id in {"case_c_gnss_jamming_suspected", "case_e_rejoin_audit"} else 70 if case_id == "case_b_link_degraded" else 120
    rows = []
    for t in range(0, 121, 10):
        truth = position_at(t, velocity, wind)
        if t <= last_contact:
            predicted = truth
            t_gap = 0
        else:
            last = position_at(last_contact, velocity, wind)
            dt = t - last_contact
            predicted = round_dict({
                "north": last["north"] + velocity[0] * dt + wind[0] * dt,
                "east": last["east"] + velocity[1] * dt + wind[1] * dt,
                "down": last["down"] + velocity[2] * dt,
            }, 2)
            t_gap = dt
        ellipse = uncertainty(t_gap, wind_sigma=1.2 if case_id in {"case_c_gnss_jamming_suspected", "case_e_rejoin_audit"} else 0.4)
        reported = dict(truth)
        gnss_quality = "normal"
        link_quality = "normal"
        if case_id == "case_b_link_degraded" and t >= 70:
            link_quality = "degraded"
        if case_id in {"case_c_gnss_jamming_suspected", "case_e_rejoin_audit"} and 50 <= t <= 100:
            gnss_quality = "degraded"
            link_quality = "intermittent"
            reported["north"] += 90 + 2.2 * (t - 50)
            reported["east"] -= 70 + 1.4 * (t - 50)
        if case_id == "case_d_spoofing_like_inconsistency" and 60 <= t <= 90:
            gnss_quality = "nominal_but_inconsistent"
            link_quality = "degraded"
            reported["north"] += 40
            reported["east"] += 280
        residual = math.dist(
            [reported["north"], reported["east"]],
            [predicted["north"], predicted["east"]],
        )
        rows.append({
            "time": iso(t),
            "t_seconds": t,
            "truth_position_m": truth,
            "reported_position_m": round_dict(reported, 2),
            "predicted_position_m": predicted,
            "uncertainty_ellipse_m": ellipse,
            "residual_m": round(residual, 2),
            "nis": nis_score(residual, ellipse["major"]),
            "gnss_quality": gnss_quality,
            "link_quality": link_quality,
        })
    return rows


def build_dataset() -> dict[str, Any]:
    simulation_cases = [
        {
            "case_id": "case_a_normal",
            "label_ko": "정상 임무",
            "scenario_summary_ko": "예측 위치와 보고 위치가 일치하는 기준선입니다.",
            "default_mode": "full_sync",
            "primary": False,
        },
        {
            "case_id": "case_b_link_degraded",
            "label_ko": "통신 저하",
            "scenario_summary_ko": "위치는 안정적이지만 링크가 좁아져 원본 feed 대신 상태 카드가 필요합니다.",
            "default_mode": "semantic_summary",
            "primary": False,
        },
        {
            "case_id": "case_c_gnss_jamming_suspected",
            "label_ko": "GNSS 교란 의심",
            "scenario_summary_ko": "보고 위치와 예측 위치가 벌어지고 GNSS/link 품질이 함께 저하됩니다.",
            "default_mode": "semantic_summary",
            "primary": True,
        },
        {
            "case_id": "case_d_spoofing_like_inconsistency",
            "label_ko": "위치 불일치",
            "scenario_summary_ko": "GNSS-like 보고는 존재하지만 물리 예측과 IMU 연속성에 맞지 않습니다.",
            "default_mode": "semantic_summary",
            "primary": False,
        },
        {
            "case_id": "case_e_rejoin_audit",
            "label_ko": "재연결 감사",
            "scenario_summary_ko": "재연결 이후 단절 중 판단과 로컬 캐시 원본을 대조해야 합니다.",
            "default_mode": "store_forward",
            "primary": False,
        },
    ]
    timelines = {case["case_id"]: build_timeline(case["case_id"]) for case in simulation_cases}
    main_case = "case_c_gnss_jamming_suspected"
    main_row = timelines[main_case][7]
    spoof_row = next(row for row in timelines["case_d_spoofing_like_inconsistency"] if row["t_seconds"] == 80)
    jam_inputs = {
        "gnss_quality_drop": 0.72,
        "link_quality_drop": 0.58,
        "normalized_position_residual": min(1.0, main_row["nis"] / 20),
        "heartbeat_gap_score": 0.60,
        "imu_gnss_disagreement": 0.55,
        "context_risk": 0.42,
    }
    jam_score = jamming_score(jam_inputs)
    case_diagnostics = {}
    diagnostic_profiles = {
        "case_a_normal": {
            "label": "normal",
            "score": 0.08,
            "interpretation_ko": "예측과 수신 상태가 일치합니다. 원본 일부와 상태 요약을 모두 전송할 수 있습니다.",
        },
        "case_b_link_degraded": {
            "label": "link_degraded",
            "score": 0.38,
            "interpretation_ko": "위치는 안정적이지만 링크 품질이 낮아 원본 영상 대신 링크/상태 카드가 우선됩니다.",
        },
        "case_c_gnss_jamming_suspected": {
            "label": "jamming_suspected",
            "score": jam_score,
            "interpretation_ko": "GNSS 품질 저하, 링크 저하, 예측-수신 잔차가 함께 커져 교란 의심 가설을 올립니다.",
        },
        "case_d_spoofing_like_inconsistency": {
            "label": "spoofing_suspected",
            "score": 0.66,
            "interpretation_ko": "GNSS가 표면상 존재하지만 물리 예측/IMU와 맞지 않아 위치 불일치 가설을 올립니다.",
        },
        "case_e_rejoin_audit": {
            "label": "rejoin_audit",
            "score": 0.52,
            "interpretation_ko": "재연결 후 시맨틱 예측과 로컬 캐시 원본을 대조해야 합니다.",
        },
    }
    for case in simulation_cases:
        case_id = case["case_id"]
        max_row = max(timelines[case_id], key=lambda row: row["nis"])
        case_diagnostics[case_id] = {
            "case_id": case_id,
            "label": diagnostic_profiles[case_id]["label"],
            "score": diagnostic_profiles[case_id]["score"],
            "max_residual_m": max_row["residual_m"],
            "max_nis": max_row["nis"],
            "interpretation_ko": diagnostic_profiles[case_id]["interpretation_ko"],
        }

    case_evaluation_profiles = {
        "case_a_normal": {
            "false_alarm_risk": 0.03,
            "confidence": 0.92,
            "operator_decision_ko": "정상 감시를 유지하고 저율 상태 요약만 전송합니다.",
            "semantic_policy_ko": "Full Sync에서는 원본 일부를 허용하고, 저대역 모드에서는 상태 요약만 보냅니다.",
            "trigger_start_sec": None,
        },
        "case_b_link_degraded": {
            "false_alarm_risk": 0.16,
            "confidence": 0.76,
            "operator_decision_ko": "영상 feed 우선순위를 낮추고 링크 상태 카드를 먼저 전송합니다.",
            "semantic_policy_ko": "Raw video 대신 LINK_HEALTH_CARD와 상태 카드가 우선됩니다.",
            "trigger_start_sec": 70,
        },
        "case_c_gnss_jamming_suspected": {
            "false_alarm_risk": 0.22,
            "confidence": 0.68,
            "operator_decision_ko": "정확 위치가 아니라 예측 위치와 불확실성 타원으로 운용합니다.",
            "semantic_policy_ko": "NAV_HEALTH_CARD를 우선 전송하고 EO/IR 원본은 로컬 캐시에 보존합니다.",
            "trigger_start_sec": 50,
        },
        "case_d_spoofing_like_inconsistency": {
            "false_alarm_risk": 0.28,
            "confidence": 0.66,
            "operator_decision_ko": "보고 위치를 확정값으로 쓰지 않고 contested position으로 표시합니다.",
            "semantic_policy_ko": "NAV_INTEGRITY_CARD와 근거 체인을 raw feed보다 먼저 전송합니다.",
            "trigger_start_sec": 60,
        },
        "case_e_rejoin_audit": {
            "false_alarm_risk": 0.18,
            "confidence": 0.71,
            "operator_decision_ko": "재연결 후 예측 로그와 로컬 캐시 원본의 차이를 먼저 감사합니다.",
            "semantic_policy_ko": "REJOIN_AUDIT_CARD와 항법 로그를 먼저 동기화하고 EO/IR 원본은 후순위로 둡니다.",
            "trigger_start_sec": 50,
        },
    }
    case_evaluations = {}
    for case in simulation_cases:
        case_id = case["case_id"]
        rows = timelines[case_id]
        profile = case_evaluation_profiles[case_id]
        max_residual_row = max(rows, key=lambda row: row["residual_m"])
        max_nis_row = max(rows, key=lambda row: row["nis"])
        first_anomaly = next((
            row for row in rows
            if row["nis"] >= NIS_WATCH_THRESHOLD
            or row["gnss_quality"] not in {"normal"}
            or row["link_quality"] not in {"normal"}
        ), None)
        detection_latency = None
        if first_anomaly and profile["trigger_start_sec"] is not None:
            detection_latency = max(0, first_anomaly["t_seconds"] - profile["trigger_start_sec"])
        max_uncertainty = max(row["uncertainty_ellipse_m"]["major"] for row in rows)
        case_evaluations[case_id] = {
            "case_id": case_id,
            "prediction_model": "constant_velocity_with_wind_uncertainty_v0",
            "nis_threshold_watch": NIS_WATCH_THRESHOLD,
            "nis_threshold_critical": NIS_CRITICAL_THRESHOLD,
            "hypothesis_threshold_watch": HYPOTHESIS_WATCH_THRESHOLD,
            "max_residual_m": max_residual_row["residual_m"],
            "max_residual_time": max_residual_row["time"],
            "max_nis": max_nis_row["nis"],
            "max_nis_time": max_nis_row["time"],
            "max_uncertainty_major_m": round(max_uncertainty, 2),
            "first_anomaly_time": first_anomaly["time"] if first_anomaly else None,
            "detection_latency_sec": detection_latency,
            "false_alarm_risk": profile["false_alarm_risk"],
            "confidence": profile["confidence"],
            "operator_decision_ko": profile["operator_decision_ko"],
            "semantic_policy_ko": profile["semantic_policy_ko"],
        }

    def drop_score(value: str, degraded_value: float, inconsistent_value: float | None = None) -> float:
        if value == "normal":
            return 0.0
        if value == "intermittent":
            return max(degraded_value, 0.58)
        if value == "nominal_but_inconsistent" and inconsistent_value is not None:
            return inconsistent_value
        if value in {"degraded", "inconsistent"}:
            return degraded_value
        return degraded_value * 0.5

    case_evaluation_series = {}
    for case in simulation_cases:
        case_id = case["case_id"]
        rows = timelines[case_id]
        profile = case_evaluation_profiles[case_id]
        max_residual = max(1.0, max(row["residual_m"] for row in rows))
        max_uncertainty = max(1.0, max(row["uncertainty_ellipse_m"]["major"] for row in rows))
        series = []
        for row in rows:
            gnss_drop = drop_score(row["gnss_quality"], degraded_value=0.72, inconsistent_value=0.18)
            link_drop = drop_score(row["link_quality"], degraded_value=0.48)
            heartbeat_gap = 0.6 if row["link_quality"] == "intermittent" else 0.3 if row["link_quality"] == "degraded" else 0.0
            imu_gnss_disagreement = 0.82 if case_id == "case_d_spoofing_like_inconsistency" and row["t_seconds"] >= 60 else 0.55 if row["gnss_quality"] == "degraded" else 0.0
            context_risk = 0.42 if case_id in {"case_c_gnss_jamming_suspected", "case_e_rejoin_audit"} else 0.36 if case_id == "case_d_spoofing_like_inconsistency" else 0.08
            hypothesis_score = jamming_score({
                "gnss_quality_drop": gnss_drop,
                "link_quality_drop": link_drop,
                "normalized_position_residual": min(1.0, row["nis"] / 20),
                "heartbeat_gap_score": heartbeat_gap,
                "imu_gnss_disagreement": imu_gnss_disagreement,
                "context_risk": context_risk,
            })
            if row["nis"] >= NIS_CRITICAL_THRESHOLD:
                threshold_state = "critical"
            elif row["nis"] >= NIS_WATCH_THRESHOLD or hypothesis_score >= HYPOTHESIS_WATCH_THRESHOLD:
                threshold_state = "watch"
            elif row["gnss_quality"] != "normal" or row["link_quality"] != "normal":
                threshold_state = "degraded"
            else:
                threshold_state = "nominal"
            if threshold_state == "critical":
                action_hint = "항법 무결성 카드 우선"
            elif threshold_state == "watch":
                action_hint = "상태/근거 카드 전송"
            elif threshold_state == "degraded":
                action_hint = "링크 상태 카드 전송"
            else:
                action_hint = "저율 상태 요약"
            series.append({
                "time": row["time"],
                "t_seconds": row["t_seconds"],
                "residual_m": row["residual_m"],
                "residual_norm": round(row["residual_m"] / max_residual, 3),
                "nis": row["nis"],
                "nis_norm": round(min(1.0, row["nis"] / NIS_CRITICAL_THRESHOLD), 3),
                "uncertainty_major_m": row["uncertainty_ellipse_m"]["major"],
                "uncertainty_norm": round(row["uncertainty_ellipse_m"]["major"] / max_uncertainty, 3),
                "hypothesis_score": hypothesis_score,
                "threshold_state": threshold_state,
                "gnss_quality": row["gnss_quality"],
                "link_quality": row["link_quality"],
                "action_hint_ko": action_hint,
            })
        case_evaluation_series[case_id] = {
            "case_id": case_id,
            "chart_type": "normalized_time_series",
            "metrics": ["residual_norm", "nis_norm", "uncertainty_norm", "hypothesis_score"],
            "series": series,
            "notes_ko": "각 값은 한 화면 비교를 위해 0~1 범위로 정규화했습니다. 원 단위 값은 같은 row에 함께 보존됩니다.",
            "thresholds": {
                "nis_watch": NIS_WATCH_THRESHOLD,
                "nis_critical": NIS_CRITICAL_THRESHOLD,
                "hypothesis_watch": HYPOTHESIS_WATCH_THRESHOLD,
            },
        }

    kalman_estimator_traces = {
        case["case_id"]: build_kalman_trace(case["case_id"], timelines[case["case_id"]])
        for case in simulation_cases
    }

    source_catalog = [
        {
            "source_id": "synthetic_uav_telemetry",
            "label": "Synthetic UAV telemetry",
            "mock_notice": "비행 상태와 원격측정값은 시뮬레이션용 합성 데이터입니다.",
        },
        {
            "source_id": "synthetic_gnss_health",
            "label": "Synthetic GNSS health",
            "mock_notice": "품질값은 실제 GNSS 측정값이 아니라 합성 상태 구간입니다.",
        },
        {
            "source_id": "synthetic_link_monitor",
            "label": "Synthetic command/data link monitor",
            "mock_notice": "패킷 손실, heartbeat, 대역폭 값은 합성 시뮬레이션입니다.",
        },
        {
            "source_id": "synthetic_eoir_cache",
            "label": "Synthetic EO/IR raw cache",
            "mock_notice": "원본 영상은 byte 수와 참조값만으로 표현합니다.",
        },
        {
            "source_id": "synthetic_weather_context",
            "label": "Synthetic weather/wind context",
            "mock_notice": "기상/풍향은 불확실성 증가에만 쓰는 합성 맥락이며 공식 예보가 아닙니다.",
        },
    ]

    drone_assets = [
        {
            "asset_id": "uav_s1",
            "asset_code": "UAV-S1",
            "asset_type": "synthetic_quadcopter",
            "sensor_modalities": ["EO_IR", "GNSS", "IMU", "LINK_TELEMETRY"],
            "comm_state": "intermittent",
            "battery_pct": 64,
            "last_contact_time": iso(40),
            "local_cache_status": "raw_video_cached",
            "sdot_outbox_count": 4,
        },
        {
            "asset_id": "ugv_r1",
            "asset_code": "UGV-R1",
            "asset_type": "synthetic_ground_relay",
            "sensor_modalities": ["LINK_RELAY", "RF_CONTEXT"],
            "comm_state": "degraded",
            "battery_pct": 78,
            "last_contact_time": iso(70),
            "local_cache_status": "relay_logs_cached",
            "sdot_outbox_count": 2,
        },
        {
            "asset_id": "rf_s3",
            "asset_code": "RF-S3",
            "asset_type": "synthetic_rf_sensor",
            "sensor_modalities": ["RF_CONTEXT", "LINK_TELEMETRY"],
            "comm_state": "connected",
            "battery_pct": 92,
            "last_contact_time": iso(70),
            "local_cache_status": "summary_only",
            "sdot_outbox_count": 1,
        },
    ]

    raw_observations = [
        {
            "observation_id": "obs_status_001",
            "asset_id": "uav_s1",
            "source_id": "synthetic_uav_telemetry",
            "sensor_type": "STATUS_SUMMARY",
            "time": iso(20),
            "raw_ref": "mock://uav_s1/status/summary_030020",
            "raw_bytes": 96_000,
            "summary": "합성 정상 비행 상태입니다. 예측 위치와 보고 위치가 정렬되어 있습니다.",
            "retention_policy": "send_summary",
        },
        {
            "observation_id": "obs_eoir_001",
            "asset_id": "uav_s1",
            "source_id": "synthetic_eoir_cache",
            "sensor_type": "EO_IR",
            "time": iso(70),
            "raw_ref": "mock://uav_s1/eoir/frame_batch_030110",
            "raw_bytes": 18_000_000,
            "summary": "원본 EO/IR 프레임 묶음은 로컬 캐시에 보존됩니다. 시맨틱 요약 모드로 보내기에는 큽니다.",
            "retention_policy": "cache_until_rejoin_audit",
        },
        {
            "observation_id": "obs_gnss_012",
            "asset_id": "uav_s1",
            "source_id": "synthetic_gnss_health",
            "sensor_type": "GNSS_HEALTH",
            "time": iso(70),
            "raw_ref": "mock://uav_s1/gnss/health_030110",
            "raw_bytes": 82_000,
            "summary": "저하 구간에서 합성 GNSS 품질이 낮아졌습니다.",
            "retention_policy": "send_summary_hold_raw",
        },
        {
            "observation_id": "obs_link_014",
            "asset_id": "uav_s1",
            "source_id": "synthetic_link_monitor",
            "sensor_type": "LINK_TELEMETRY",
            "time": iso(72),
            "raw_ref": "mock://uav_s1/link/telemetry_030112",
            "raw_bytes": 240_000,
            "summary": "합성 패킷 손실과 heartbeat 공백이 증가했습니다.",
            "retention_policy": "send_summary_hold_raw",
        },
        {
            "observation_id": "obs_imu_011",
            "asset_id": "uav_s1",
            "source_id": "synthetic_uav_telemetry",
            "sensor_type": "IMU_STATE",
            "time": iso(70),
            "raw_ref": "mock://uav_s1/imu/state_030110",
            "raw_bytes": 120_000,
            "summary": "합성 관성 추정값이 저하된 GNSS 보고 위치와 벌어졌습니다.",
            "retention_policy": "send_summary_hold_raw",
        },
        {
            "observation_id": "obs_spoofing_like_021",
            "asset_id": "uav_s1",
            "source_id": "synthetic_gnss_health",
            "sensor_type": "GNSS_INCONSISTENCY",
            "time": iso(80),
            "raw_ref": "mock://uav_s1/gnss/inconsistent_030120",
            "raw_bytes": 140_000,
            "summary": "GNSS-like 보고는 존재하지만 관성/물리 예측과 맞지 않습니다.",
            "retention_policy": "send_summary_hold_raw",
        },
        {
            "observation_id": "obs_weather_020",
            "asset_id": "uav_s1",
            "source_id": "synthetic_weather_context",
            "sensor_type": "WEATHER_CONTEXT",
            "time": iso(60),
            "raw_ref": "mock://weather/wind_context_030100",
            "raw_bytes": 110_000,
            "summary": "합성 풍향 맥락이 예측 불확실성 증가에 반영됩니다.",
            "retention_policy": "context_summary",
        },
    ]

    edge_detections = [
        {
            "detection_id": "det_nav_residual_001",
            "asset_id": "uav_s1",
            "observation_refs": ["obs_gnss_012", "obs_link_014", "obs_imu_011"],
            "candidate_type": "NAVIGATION_RESIDUAL_SPIKE",
            "model_or_rule": "nis_residual_rule_v0",
            "confidence": 0.63,
            "features": {
                "normalized_innovation_squared": main_row["nis"],
                "threshold": NIS_WATCH_THRESHOLD,
                "residual_m": main_row["residual_m"],
                "heartbeat_gap_seconds": 18,
                "gnss_quality_drop": jam_inputs["gnss_quality_drop"],
                "link_quality_drop": jam_inputs["link_quality_drop"],
            },
        },
        {
            "detection_id": "det_nav_residual_002",
            "asset_id": "uav_s1",
            "observation_refs": ["obs_spoofing_like_021", "obs_imu_011"],
            "candidate_type": "POSITION_REPORT_INCONSISTENCY",
            "model_or_rule": "nis_residual_rule_v0",
            "confidence": 0.66,
            "features": {
                "normalized_innovation_squared": spoof_row["nis"],
                "threshold": NIS_WATCH_THRESHOLD,
                "residual_m": spoof_row["residual_m"],
                "gnss_present_but_inconsistent": 1.0,
                "imu_gnss_disagreement": 0.82,
            },
        }
    ]

    jamming_hypotheses = [
        {
            "hypothesis_id": "jam_hyp_uav_s1_001",
            "asset_id": "uav_s1",
            "time": iso(72),
            "label": "jamming_suspected" if jam_score >= 0.60 else "navigation_degraded",
            "score": jam_score,
            "inputs": jam_inputs,
            "caveat": "방어적 진단 가설일 뿐이며, 간섭원의 존재나 위치를 입증하지 않습니다.",
        },
        {
            "hypothesis_id": "jam_hyp_uav_s1_002",
            "asset_id": "uav_s1",
            "time": iso(80),
            "label": "spoofing_like_inconsistency",
            "score": 0.66,
            "inputs": {
                "gnss_quality_drop": 0.18,
                "link_quality_drop": 0.48,
                "normalized_position_residual": 1.0,
                "heartbeat_gap_score": 0.30,
                "imu_gnss_disagreement": 0.82,
                "context_risk": 0.36,
            },
            "caveat": "방어적 무결성 가설일 뿐이며, spoofing 주체나 발생원을 입증하지 않습니다.",
        }
    ]

    event_specs = [
        {
            "event_id": "evt_uav_s1_status_summary",
            "event_type": "STATUS_SUMMARY",
            "severity": "low",
            "asset_id": "uav_s1",
            "case_ids": ["case_a_normal"],
            "time": iso(20),
            "summary": "UAV-S1의 예측 상태와 보고 상태가 정상 비행 중 일치합니다.",
            "why_it_matters": "DDIL 또는 항법 저하가 시작되기 전의 기준 화면을 보여줍니다.",
            "recommended_action": "정상 원격측정과 저율 S-DOT 상태 요약을 유지합니다.",
            "evidence_refs": ["obs_status_001"],
            "raw_bytes": 96_000,
            "semantic_bytes": 360,
            "features": {"flight_safety": 0.38, "navigation_integrity": 0.42, "mission_relevance": 0.32, "link_survivability": 0.30, "provenance_audit": 0.24},
        },
        {
            "event_id": "evt_uav_s1_link_degraded",
            "event_type": "LINK_DEGRADED",
            "severity": "medium",
            "asset_id": "uav_s1",
            "case_ids": ["case_b_link_degraded", "case_c_gnss_jamming_suspected", "case_d_spoofing_like_inconsistency"],
            "time": iso(60),
            "summary": "UAV-S1 지휘/데이터 링크가 변경분 동기화에서 시맨틱 요약 수준으로 낮아졌습니다.",
            "why_it_matters": "원본 영상과 전체 원격측정이 도착한다고 가정할 수 없습니다.",
            "recommended_action": "원본 feed 우선순위를 낮추고 상태/임무 카드를 먼저 전송합니다.",
            "evidence_refs": ["obs_link_014"],
            "raw_bytes": 240_000,
            "semantic_bytes": 520,
            "features": {"flight_safety": 0.66, "navigation_integrity": 0.50, "mission_relevance": 0.64, "link_survivability": 0.88, "provenance_audit": 0.50},
        },
        {
            "event_id": "evt_uav_s1_gnss_degraded",
            "event_type": "GNSS_DEGRADED",
            "severity": "high",
            "asset_id": "uav_s1",
            "case_ids": ["case_c_gnss_jamming_suspected"],
            "time": iso(70),
            "summary": "UAV-S1 GNSS 품질이 낮아지고 예측 불확실성이 커졌습니다.",
            "why_it_matters": "상황판은 정확한 한 점이 아니라 불확실성 범위를 보여줘야 합니다.",
            "recommended_action": "예측 상태와 공분산을 사용하고, 압축된 항법 상태 패킷만 요청합니다.",
            "evidence_refs": ["obs_gnss_012", "obs_weather_020"],
            "raw_bytes": 192_000,
            "semantic_bytes": 640,
            "features": {"flight_safety": 0.82, "navigation_integrity": 0.91, "mission_relevance": 0.72, "link_survivability": 0.70, "provenance_audit": 0.62},
        },
        {
            "event_id": "evt_uav_s1_jamming_suspected",
            "event_type": "JAMMING_SUSPECTED",
            "severity": "high",
            "asset_id": "uav_s1",
            "case_ids": ["case_c_gnss_jamming_suspected"],
            "time": iso(72),
            "summary": "UAV-S1 항법·링크 지표가 가능한 교란 상황을 시사합니다.",
            "why_it_matters": "오퍼레이터는 드론 상태를 확정값이 아니라 불확실성과 감사 요구가 있는 가설로 다뤄야 합니다.",
            "recommended_action": "항법 상태 카드를 보내고 EO/IR 원본은 로컬에 보존한 뒤 재연결 감사를 준비합니다.",
            "evidence_refs": ["obs_gnss_012", "obs_link_014", "obs_imu_011", "det_nav_residual_001", "jam_hyp_uav_s1_001"],
            "raw_bytes": 18_442_000,
            "semantic_bytes": 920,
            "features": {"flight_safety": 0.90, "navigation_integrity": 0.94, "mission_relevance": 0.84, "link_survivability": 0.82, "provenance_audit": 0.78},
        },
        {
            "event_id": "evt_uav_s1_spoofing_suspected",
            "event_type": "SPOOFING_SUSPECTED",
            "severity": "high",
            "asset_id": "uav_s1",
            "case_ids": ["case_d_spoofing_like_inconsistency"],
            "time": iso(80),
            "summary": "UAV-S1의 GNSS-like 보고는 존재하지만 물리/관성 예측과 맞지 않습니다.",
            "why_it_matters": "유효해 보이는 위치도 기대 공분산을 초과하면 신뢰하기 어렵습니다.",
            "recommended_action": "보고 위치를 contested 상태로 표시하고, 원본 feed보다 잔차/근거 카드를 먼저 전송합니다.",
            "evidence_refs": ["obs_spoofing_like_021", "obs_imu_011", "det_nav_residual_002", "jam_hyp_uav_s1_002"],
            "raw_bytes": 402_000,
            "semantic_bytes": 820,
            "features": {"flight_safety": 0.88, "navigation_integrity": 0.93, "mission_relevance": 0.78, "link_survivability": 0.70, "provenance_audit": 0.78},
        },
        {
            "event_id": "evt_uav_s1_rejoin_audit_required",
            "event_type": "REJOIN_AUDIT_REQUIRED",
            "severity": "medium",
            "asset_id": "uav_s1",
            "case_ids": ["case_e_rejoin_audit"],
            "time": iso(120),
            "summary": "UAV-S1 재연결 후 예측값과 캐시 원본의 감사가 필요합니다.",
            "why_it_matters": "신뢰도를 복구하기 전에 시맨틱 예측을 캐시된 원본 원격측정과 대조해야 합니다.",
            "recommended_action": "캐시된 항법 로그를 먼저 동기화하고, 차이가 남으면 선택된 EO/IR 조각을 후순위로 동기화합니다.",
            "evidence_refs": ["obs_eoir_001", "obs_gnss_012", "obs_link_014"],
            "raw_bytes": 18_322_000,
            "semantic_bytes": 760,
            "features": {"flight_safety": 0.70, "navigation_integrity": 0.82, "mission_relevance": 0.66, "link_survivability": 0.56, "provenance_audit": 0.95},
        },
    ]

    semantic_events = []
    for spec in event_specs:
        features = spec.pop("features")
        semantic_events.append({
            **spec,
            "priority": score_event(features),
            "priority_features": features,
            "mock_notice": "Synthetic drone S-DOT event for safe hackathon simulation.",
        })

    semantic_packets = []
    for event in semantic_events:
        tier = {
            "STATUS_SUMMARY": "STATUS_CARD",
            "LINK_DEGRADED": "LINK_HEALTH_CARD",
            "GNSS_DEGRADED": "NAV_HEALTH_CARD",
            "JAMMING_SUSPECTED": "NAV_HEALTH_CARD",
            "SPOOFING_SUSPECTED": "NAV_INTEGRITY_CARD",
            "REJOIN_AUDIT_REQUIRED": "REJOIN_AUDIT_CARD",
        }[event["event_type"]]
        semantic_packets.append({
            "packet_id": "sdot_" + event["event_id"].replace("evt_", ""),
            "event_id": event["event_id"],
            "asset_id": event["asset_id"],
            "payload_tier": tier,
            "case_ids": event["case_ids"],
            "priority": event["priority"],
            "bytes_raw_represented": event["raw_bytes"],
            "bytes_semantic": event["semantic_bytes"],
            "requires_ack": event["event_type"] in {"JAMMING_SUSPECTED", "GNSS_DEGRADED"},
            "rejoin_audit_required": event["event_type"] in {"JAMMING_SUSPECTED", "REJOIN_AUDIT_REQUIRED"},
        })

    routing_results = {}
    for mode, config in NETWORK_MODES.items():
        packets = []
        sent = 0
        semantic_bytes_sent = 0
        raw_bytes_represented = 0
        for packet in semantic_packets:
            if mode == "local_only":
                decision = "hold_local"
            elif packet["priority"] >= config["send_threshold"]:
                decision = "send"
            elif packet["priority"] >= config["defer_threshold"]:
                decision = "defer"
            else:
                decision = "drop"
            if decision == "send":
                sent += 1
                semantic_bytes_sent += packet["bytes_semantic"]
                raw_bytes_represented += packet["bytes_raw_represented"]
            packets.append({**packet, "network_mode": mode, "decision": decision})
        raw_total = sum(event["raw_bytes"] for event in semantic_events)
        routing_results[mode] = {
            "mode": mode,
            "network": {key: value for key, value in config.items() if key not in {"send_threshold", "defer_threshold"}},
            "packets": packets,
            "metrics": {
                "events_sent": sent,
                "events_total": len(semantic_events),
                "raw_bytes_total_if_full_feed": raw_total,
                "raw_bytes_represented_by_sent_events": raw_bytes_represented,
                "semantic_bytes_sent": semantic_bytes_sent,
                "bytes_saved_pct_vs_full_feed": round(100 * (1 - semantic_bytes_sent / raw_total), 2) if raw_total else 0,
                "message_survival_rate": round(sent / len(semantic_events), 3),
            },
        }

    rejoin_audits = [
        {
            "audit_id": "audit_uav_s1_case_c",
            "asset_id": "uav_s1",
            "case_id": main_case,
            "status": "pending_rejoin",
            "prediction_before_rejoin": timelines[main_case][-1]["predicted_position_m"],
            "simulated_truth_at_rejoin": timelines[main_case][-1]["truth_position_m"],
            "discrepancy_m": timelines[main_case][-1]["residual_m"],
            "inside_uncertainty_envelope": timelines[main_case][-1]["residual_m"] <= timelines[main_case][-1]["uncertainty_ellipse_m"]["major"],
            "expected_sync_order": ["sdot_uav_s1_jamming_suspected", "sdot_uav_s1_gnss_degraded", "sdot_uav_s1_rejoin_audit_required"],
        }
    ]

    return {
        "metadata": {
            "dataset_id": "s_dot_drone_semantic_ops_mock_v0_6",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "display_name_ko": "S-DOT 드론 시맨틱 전송 시뮬레이션",
            "scenario_name": "Drone semantic transmission under GNSS/link degradation",
            "mock_dataset": True,
            "safety_note": "Synthetic drone flight, GNSS/link degradation, jamming hypothesis, and semantic packet data. No real routes, force posture, EW emitter data, or sensitive coordinates.",
            "schema_doc": "05_analysis/knowledge_graph/s_dot_drone_semantic_transmission_schema_v0_1.md",
            "operating_concept_doc": "02_problem_statements/hypotheses/s_dot_drone_jamming_operating_concept_20260704.md",
        },
        "algorithm_basis": {
            "prediction_model": {
                "name": "constant_velocity_with_wind_uncertainty_v0",
                "formula": "x_hat(t) = x_last + v_last * dt + wind_context * dt",
                "explain_ko": "마지막 신뢰 위치, 최근 속도, 합성 풍향/풍속 맥락으로 예측 위치를 계산합니다.",
            },
            "uncertainty_model": {
                "formula": "sigma^2 = sigma0^2 + vel_sigma^2*dt^2 + 0.25*accel_sigma^2*dt^4 + wind_sigma^2*dt^2",
                "explain_ko": "통신 단절 시간이 길어질수록 속도·가속·풍향 오차가 누적되어 불확실성 타원이 커집니다.",
            },
            "residual_model": {
                "formula": "residual = distance(reported_position, predicted_position)",
                "explain_ko": "수신 위치가 예측 가능한 물리 경로에서 얼마나 벗어났는지 계산합니다.",
            },
            "nis_model": {
                "formula": "NIS ~= (residual / (0.55 * sigma_major))^2",
                "watch_threshold": NIS_WATCH_THRESHOLD,
                "critical_threshold": NIS_CRITICAL_THRESHOLD,
                "explain_ko": "잔차가 현재 불확실성 범위 대비 과도한지 보는 단순화된 항법 무결성 지표입니다.",
            },
            "hypothesis_score_model": {
                "formula": "0.25*GNSS_drop + 0.20*Link_drop + 0.20*Residual + 0.15*Heartbeat_gap + 0.10*IMU_GNSS_disagreement + 0.10*Context_risk",
                "watch_threshold": HYPOTHESIS_WATCH_THRESHOLD,
                "explain_ko": "교란 의심은 단일 신호가 아니라 GNSS, 링크, 위치 잔차, heartbeat, IMU 불일치, 환경 맥락을 가중합한 방어적 가설 점수입니다.",
            },
            "kalman_filter_model": {
                "name": "constant_velocity_kalman_filter_v0",
                "formula": "predict: x_k = F*x_{k-1}; update only if innovation_nis <= 9.21",
                "state_vector": ["north_m", "east_m", "north_velocity_mps", "east_velocity_mps"],
                "explain_ko": "보고 위치를 항상 믿지 않고, 예측 공분산 대비 innovation이 과도하면 측정값을 게이트에서 차단하고 추정 상태를 유지합니다.",
            },
        },
        "platform_handoff": PLATFORM_HANDOFF,
        "simulation_cases": simulation_cases,
        "source_catalog": source_catalog,
        "control_intent": {
            "intent_id": "intent_drone_semantic_watch_01",
            "display_name_ko": "드론 시맨틱 감시 임무",
            "primary_objective": "드론 원본 영상/텔레메트리를 모두 전송할 수 없는 상황에서도 위치 예측, 불확실성, 링크/GNSS 상태, 교란 의심 근거를 시맨틱 패킷으로 유지한다.",
            "valid_until": iso(3600),
            "priority_weights": {"flight_safety": 0.25, "navigation_integrity": 0.24, "mission_relevance": 0.21, "link_survivability": 0.18, "provenance_audit": 0.12},
        },
        "drone_assets": drone_assets,
        "case_diagnostics": case_diagnostics,
        "case_evaluations": case_evaluations,
        "case_evaluation_series": case_evaluation_series,
        "kalman_estimator_traces": kalman_estimator_traces,
        "flight_timelines": timelines,
        "navigation_estimates": [
            {
                "estimate_id": "nav_uav_s1_case_c_t070",
                "asset_id": "uav_s1",
                "case_id": main_case,
                "time": main_row["time"],
                "prediction_model": "constant_velocity_with_wind_uncertainty_v0",
                "predicted_position_m": main_row["predicted_position_m"],
                "reported_position_m": main_row["reported_position_m"],
                "uncertainty_ellipse_m": main_row["uncertainty_ellipse_m"],
                "residual_m": main_row["residual_m"],
                "nis": main_row["nis"],
                "confidence": 0.61,
            }
        ],
        "network_modes": NETWORK_MODES,
        "bearer_states": [
            {"pace": "P", "label": "전술 데이터 링크", "status_by_mode": {"full_sync": "active", "delta_sync": "active", "semantic_summary": "degraded", "store_forward": "degraded", "local_only": "down"}},
            {"pace": "A", "label": "장거리/위성 백업", "status_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "candidate", "store_forward": "candidate", "local_only": "down"}},
            {"pace": "C", "label": "메시/중계 노드", "status_by_mode": {"full_sync": "standby", "delta_sync": "candidate", "semantic_summary": "candidate", "store_forward": "active", "local_only": "local"}},
            {"pace": "E", "label": "로컬 캐시/재연결 감사", "status_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "standby", "store_forward": "active", "local_only": "active"}},
        ],
        "raw_observations": raw_observations,
        "edge_detections": edge_detections,
        "jamming_hypotheses": jamming_hypotheses,
        "semantic_events": semantic_events,
        "semantic_packets": semantic_packets,
        "routing_results": routing_results,
        "custody_chains": [
            {
                "custody_id": "custody_evt_uav_s1_jamming_suspected",
                "event_id": "evt_uav_s1_jamming_suspected",
                "source_observation_refs": ["obs_eoir_001", "obs_gnss_012", "obs_link_014", "obs_imu_011"],
                "edge_encoder_version": "edge_semantic_encoder_v0",
                "packet_id": "sdot_uav_s1_jamming_suspected",
                "held_raw_refs": ["mock://uav_s1/eoir/frame_batch_030110"],
                "audit_status": "pending_rejoin",
            }
        ],
        "rejoin_audits": rejoin_audits,
        "context_layers": {
            "public_background": "Optional Seoul/public map context may be added later; primary demo uses local synthetic coordinates.",
            "safety_boundary": "No sensitive coordinates or real EW details.",
        },
        "briefing": {
            "headline": "S-DOT keeps drone mission meaning alive when raw telemetry, imagery, and exact position cannot survive the network.",
            "operator_summary": "Treat UAV-S1 as an uncertainty envelope, not an exact point. Send NAV_HEALTH_CARD first, hold raw EO/IR locally, and audit after rejoin.",
        },
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset = build_dataset()
    OUT_JSON.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_JS.write_text("window.__D4D_DRONE_SDOT_DATASET = " + json.dumps(dataset, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(json.dumps({
        "dataset": str(OUT_JSON),
        "dataset_js": str(OUT_JS),
        "dataset_id": dataset["metadata"]["dataset_id"],
        "simulation_cases": len(dataset["simulation_cases"]),
        "drone_assets": len(dataset["drone_assets"]),
        "semantic_events": len(dataset["semantic_events"]),
        "semantic_packets": len(dataset["semantic_packets"]),
        "case_evaluation_series": len(dataset["case_evaluation_series"]),
        "kalman_estimator_traces": len(dataset["kalman_estimator_traces"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

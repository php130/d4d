#!/usr/bin/env python3
"""Generate a deterministic mock dataset for the Resilient Maritime COP demo.

The values are synthetic and safe to redistribute. The source catalog explains
which real API/source type each mock record is modeled after, so live adapters
can replace the mock layer later without changing the semantic-event contract.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path("/Users/mollykim/projects/D4D")
SAMPLE_DIR = PROJECT_ROOT / "03_data/samples/resilient_maritime_cop"
APP_DATA_DIR = PROJECT_ROOT / "06_prototype/app/resilient_maritime_cop/data"


NETWORK_MODES = {
    "full_sync": {
        "label": "Full Sync",
        "bandwidth_kbps": 5000,
        "latency_ms": 80,
        "packet_loss_pct": 1,
        "send_threshold": 0.0,
        "defer_threshold": 0.0,
        "description": "Full event details and selected raw evidence can move.",
    },
    "delta_sync": {
        "label": "Delta Sync",
        "bandwidth_kbps": 900,
        "latency_ms": 220,
        "packet_loss_pct": 4,
        "send_threshold": 0.45,
        "defer_threshold": 0.25,
        "description": "Changed tracks, compact event deltas, and evidence refs move.",
    },
    "semantic_summary": {
        "label": "Semantic Summary",
        "bandwidth_kbps": 96,
        "latency_ms": 950,
        "packet_loss_pct": 14,
        "send_threshold": 0.72,
        "defer_threshold": 0.45,
        "description": "Only high-priority alert cards and object lists move.",
    },
    "store_forward": {
        "label": "Store Forward",
        "bandwidth_kbps": 24,
        "latency_ms": 1800,
        "packet_loss_pct": 35,
        "send_threshold": 0.88,
        "defer_threshold": 0.55,
        "description": "Most messages queue locally; only critical summaries move.",
    },
    "local_only": {
        "label": "Local Only",
        "bandwidth_kbps": 0,
        "latency_ms": None,
        "packet_loss_pct": 100,
        "send_threshold": 1.1,
        "defer_threshold": 0.0,
        "description": "No remote transmission. Local COP shows stale-data warnings.",
    },
}


def score(features: dict[str, float]) -> float:
    weights = {
        "mission_impact": 0.28,
        "urgency": 0.20,
        "confidence": 0.18,
        "trust": 0.14,
        "novelty": 0.10,
        "network_efficiency": 0.10,
    }
    return round(sum(features[k] * weights[k] for k in weights), 3)


def build_dataset() -> dict:
    source_catalog = [
        {
            "source_id": "mock_ais_tracks",
            "label": "Synthetic AIS-like vessel tracks",
            "real_replacement": ["data.go.kr maritime AIS", "Global Fishing Watch", "NOAA MarineCadastre AIS"],
            "source_rationale": "AIS is the cooperative maritime position-reporting layer. The mock fields mirror common AIS concepts: vessel id, time, lat/lon, speed, course, and freshness.",
            "mock_notice": "Synthetic records; no real MMSI or operator data.",
        },
        {
            "source_id": "mock_sar_detections",
            "label": "Synthetic SAR-like detection",
            "real_replacement": ["Copernicus Sentinel-1", "xView3", "Global Fishing Watch SAR detections"],
            "source_rationale": "SAR provides independent physical observation when AIS is missing, spoofed, or delayed. The mock record carries scene id, detection point, size hint, and match status.",
            "mock_notice": "Synthetic detection modeled after open SAR ship-detection workflows.",
        },
        {
            "source_id": "mock_weather_hazard",
            "label": "Synthetic maritime weather warning",
            "real_replacement": ["KMA APIHub", "Copernicus Marine", "NOAA/NCEP"],
            "source_rationale": "Weather affects vessel risk, sensor reliability, and operator urgency. The mock warning is represented as a time-bounded area hazard.",
            "mock_notice": "Synthetic warning; not an official forecast.",
        },
        {
            "source_id": "mock_osint_incident",
            "label": "Synthetic OSINT incident",
            "real_replacement": ["GDELT", "official maritime advisories", "ReliefWeb/HDX where relevant"],
            "source_rationale": "OSINT gives cited narrative context, but must not be treated as sensor truth. The mock record is an advisory-style citation stub.",
            "mock_notice": "Synthetic article/advisory metadata; URLs are not operational claims.",
        },
        {
            "source_id": "mock_network_state",
            "label": "Synthetic DDIL network states",
            "real_replacement": ["Cloudflare Radar", "Ookla Open Data", "RIPE Atlas", "Linux tc netem"],
            "source_rationale": "T3 differentiation comes from showing what survives under bandwidth, latency, packet loss, and link outage.",
            "mock_notice": "Synthetic network profile designed for repeatable demo behavior.",
        },
        {
            "source_id": "mock_operator_report",
            "label": "Synthetic operator report",
            "real_replacement": ["watchstander report", "field report", "radio/voice transcript after redaction"],
            "source_rationale": "Human reports are valuable but can conflict with sensor evidence, so the COP must model source trust and contradiction.",
            "mock_notice": "Synthetic report with no real person or unit information.",
        },
    ]

    vessels = [
        {
            "vessel_id": "vessel_haneul_77",
            "display_name": "Haneul-77",
            "masked_identifier": "MMSI-***-077",
            "type": "cargo",
            "identity_confidence": 0.81,
            "route_role": "northbound commercial track crossing monitored corridor",
        },
        {
            "vessel_id": "vessel_blue_maru_12",
            "display_name": "Blue Maru-12",
            "masked_identifier": "MMSI-***-112",
            "type": "fishing",
            "identity_confidence": 0.73,
            "route_role": "routine fishing track outside the warning corridor",
        },
        {
            "vessel_id": "vessel_daehan_rescue_3",
            "display_name": "Daehan Rescue-3",
            "masked_identifier": "CALLSIGN-***-R3",
            "type": "patrol_support",
            "identity_confidence": 0.94,
            "route_role": "friendly support asset with reliable reporting",
        },
    ]

    tracks = [
        {"track_id": "trk_h77_001", "vessel_id": "vessel_haneul_77", "time": "2026-07-04T01:40:00Z", "lat": 37.18, "lon": 125.44, "sog": 13.2, "cog": 42, "source": "mock_ais_tracks"},
        {"track_id": "trk_h77_002", "vessel_id": "vessel_haneul_77", "time": "2026-07-04T01:55:00Z", "lat": 37.25, "lon": 125.52, "sog": 13.5, "cog": 44, "source": "mock_ais_tracks"},
        {"track_id": "trk_h77_003", "vessel_id": "vessel_haneul_77", "time": "2026-07-04T02:05:00Z", "lat": 37.30, "lon": 125.58, "sog": 13.1, "cog": 43, "source": "mock_ais_tracks", "last_cooperative_point": True},
        {"track_id": "trk_bm12_001", "vessel_id": "vessel_blue_maru_12", "time": "2026-07-04T02:00:00Z", "lat": 37.06, "lon": 125.82, "sog": 7.4, "cog": 310, "source": "mock_ais_tracks"},
        {"track_id": "trk_dr3_001", "vessel_id": "vessel_daehan_rescue_3", "time": "2026-07-04T02:10:00Z", "lat": 37.50, "lon": 125.43, "sog": 18.0, "cog": 110, "source": "mock_ais_tracks"},
    ]

    observations = [
        {
            "observation_id": "obs_ais_gap_h77",
            "source_id": "mock_ais_tracks",
            "sensor_type": "AIS",
            "time": "2026-07-04T02:25:00Z",
            "location": {"lat": 37.36, "lon": 125.66},
            "claim": "No cooperative AIS update received for Haneul-77 after 02:05Z.",
            "raw_ref": "mock://ais/haneul_77#last_point=trk_h77_003",
            "raw_bytes": 420000,
        },
        {
            "observation_id": "obs_sar_unmatched_001",
            "source_id": "mock_sar_detections",
            "sensor_type": "SAR",
            "time": "2026-07-04T02:24:00Z",
            "location": {"lat": 37.41, "lon": 125.72},
            "claim": "Vessel-sized object detected 8.1 km from predicted Haneul-77 position; no AIS match inside gate.",
            "raw_ref": "mock://sar/scene_20260704_0224#det=1",
            "raw_bytes": 1480000,
        },
        {
            "observation_id": "obs_weather_001",
            "source_id": "mock_weather_hazard",
            "sensor_type": "WEATHER",
            "time": "2026-07-04T02:10:00Z",
            "location": {"lat": 37.32, "lon": 125.60},
            "claim": "Visibility reduced and wave hazard elevated across the corridor.",
            "raw_ref": "mock://weather/kma_style_warning#yellow_sea_corridor",
            "raw_bytes": 65000,
        },
        {
            "observation_id": "obs_osint_001",
            "source_id": "mock_osint_incident",
            "sensor_type": "OSINT",
            "time": "2026-07-04T01:35:00Z",
            "location": {"lat": 37.55, "lon": 125.95},
            "claim": "Open-source advisory reports temporary maritime inspection activity near the northern corridor.",
            "raw_ref": "mock://osint/gdelt_style/advisory_20260704_0135",
            "raw_bytes": 38000,
        },
        {
            "observation_id": "obs_network_001",
            "source_id": "mock_network_state",
            "sensor_type": "NETWORK",
            "time": "2026-07-04T02:18:00Z",
            "location": {"lat": 37.38, "lon": 125.63},
            "claim": "Ship-to-shore relay bandwidth dropped below semantic-summary threshold.",
            "raw_ref": "mock://network/link_alpha#state=semantic_summary",
            "raw_bytes": 21000,
        },
        {
            "observation_id": "obs_operator_lowtrust_001",
            "source_id": "mock_operator_report",
            "sensor_type": "HUMAN_REPORT",
            "time": "2026-07-04T02:28:00Z",
            "location": {"lat": 37.02, "lon": 125.10},
            "claim": "Unconfirmed voice report places Haneul-77 south of the corridor, conflicting with SAR/time-distance feasibility.",
            "raw_ref": "mock://operator/report_20260704_0228",
            "raw_bytes": 12000,
        },
    ]

    event_specs = [
        {
            "event_id": "evt_network_degraded_001",
            "event_type": "NETWORK_DEGRADED",
            "severity": "high",
            "time": "2026-07-04T02:18:00Z",
            "location": {"lat": 37.38, "lon": 125.63, "area": "Yellow Sea AOI"},
            "entity_refs": ["link_alpha"],
            "summary": "Ship-to-shore relay moved from delta sync to semantic summary.",
            "why_it_matters": "The COP can no longer move raw evidence reliably, so alert cards and evidence references must be prioritized.",
            "recommended_action": "Switch to semantic summary mode and queue raw evidence for store-forward sync.",
            "evidence_refs": ["obs_network_001"],
            "features": {"mission_impact": 0.82, "urgency": 0.86, "confidence": 0.78, "trust": 0.82, "novelty": 0.56, "network_efficiency": 0.94},
            "raw_bytes": 21000,
            "semantic_bytes": 690,
        },
        {
            "event_id": "evt_weather_hazard_001",
            "event_type": "WEATHER_HAZARD",
            "severity": "medium",
            "time": "2026-07-04T02:10:00Z",
            "location": {"lat": 37.32, "lon": 125.60, "area": "Yellow Sea AOI"},
            "entity_refs": ["area_yellow_sea_corridor"],
            "summary": "Reduced visibility and wave risk affect the monitored corridor.",
            "why_it_matters": "Weather raises route risk and lowers confidence in visual confirmation, making SAR/AIS disagreement more important.",
            "recommended_action": "Increase uncertainty on visual-only reports and prioritize non-cooperative detection evidence.",
            "evidence_refs": ["obs_weather_001"],
            "features": {"mission_impact": 0.62, "urgency": 0.67, "confidence": 0.78, "trust": 0.83, "novelty": 0.38, "network_efficiency": 0.86},
            "raw_bytes": 65000,
            "semantic_bytes": 740,
        },
        {
            "event_id": "evt_ais_gap_h77",
            "event_type": "AIS_GAP",
            "severity": "high",
            "time": "2026-07-04T02:25:00Z",
            "location": {"lat": 37.36, "lon": 125.66, "area": "Yellow Sea AOI"},
            "entity_refs": ["vessel_haneul_77"],
            "summary": "Haneul-77 has no cooperative AIS update after 02:05Z near the monitored corridor.",
            "why_it_matters": "The gap appears during network degradation and near a later SAR detection without AIS match.",
            "recommended_action": "Preserve a compact alert card and request independent confirmation.",
            "evidence_refs": ["obs_ais_gap_h77", "obs_network_001"],
            "features": {"mission_impact": 0.88, "urgency": 0.86, "confidence": 0.76, "trust": 0.72, "novelty": 0.74, "network_efficiency": 0.91},
            "raw_bytes": 420000,
            "semantic_bytes": 910,
        },
        {
            "event_id": "evt_sar_without_ais_001",
            "event_type": "SAR_WITHOUT_AIS",
            "severity": "critical",
            "time": "2026-07-04T02:24:00Z",
            "location": {"lat": 37.41, "lon": 125.72, "area": "Yellow Sea AOI"},
            "entity_refs": ["vessel_candidate_sar_001"],
            "summary": "SAR-like detection appears without an AIS candidate inside the time-distance gate.",
            "why_it_matters": "Independent physical evidence conflicts with the cooperative AIS picture and may indicate a dark-vessel candidate.",
            "recommended_action": "Route immediately as high-priority alert and queue raw SAR reference for later sync.",
            "evidence_refs": ["obs_sar_unmatched_001", "obs_ais_gap_h77", "obs_weather_001"],
            "features": {"mission_impact": 0.95, "urgency": 0.90, "confidence": 0.79, "trust": 0.76, "novelty": 0.88, "network_efficiency": 0.96},
            "raw_bytes": 1480000,
            "semantic_bytes": 980,
        },
        {
            "event_id": "evt_low_trust_report_001",
            "event_type": "LOW_TRUST_REPORT",
            "severity": "medium",
            "time": "2026-07-04T02:28:00Z",
            "location": {"lat": 37.02, "lon": 125.10, "area": "Yellow Sea AOI"},
            "entity_refs": ["vessel_haneul_77"],
            "summary": "Unconfirmed operator report conflicts with SAR/time-distance feasibility.",
            "why_it_matters": "Human reports are useful but must be weighted against sensor evidence and feasibility constraints.",
            "recommended_action": "Keep the report visible as contested evidence; do not let it overwrite the SAR/AIS alert.",
            "evidence_refs": ["obs_operator_lowtrust_001", "obs_sar_unmatched_001"],
            "features": {"mission_impact": 0.60, "urgency": 0.58, "confidence": 0.42, "trust": 0.35, "novelty": 0.72, "network_efficiency": 0.82},
            "raw_bytes": 12000,
            "semantic_bytes": 640,
        },
        {
            "event_id": "evt_osint_context_001",
            "event_type": "OSINT_INCIDENT",
            "severity": "medium",
            "time": "2026-07-04T01:35:00Z",
            "location": {"lat": 37.55, "lon": 125.95, "area": "Northern corridor context"},
            "entity_refs": ["area_yellow_sea_corridor"],
            "summary": "Open-source advisory context raises watch priority near the corridor.",
            "why_it_matters": "OSINT is not proof, but it gives cited context for why the area deserves monitoring.",
            "recommended_action": "Attach as context only; do not escalate without sensor corroboration.",
            "evidence_refs": ["obs_osint_001"],
            "features": {"mission_impact": 0.52, "urgency": 0.45, "confidence": 0.54, "trust": 0.52, "novelty": 0.63, "network_efficiency": 0.88},
            "raw_bytes": 38000,
            "semantic_bytes": 690,
        },
        {
            "event_id": "evt_composite_dark_vessel_review_001",
            "event_type": "PRIORITY_BRIEF",
            "severity": "critical",
            "time": "2026-07-04T02:30:00Z",
            "location": {"lat": 37.40, "lon": 125.70, "area": "Yellow Sea AOI"},
            "entity_refs": ["vessel_haneul_77", "vessel_candidate_sar_001"],
            "summary": "Composite alert: AIS gap, SAR-without-AIS, weather hazard, and degraded network converge.",
            "why_it_matters": "This is the highest-value message to preserve when the link can only carry one alert card.",
            "recommended_action": "Send composite alert card, keep raw evidence queued, and request independent confirmation when link recovers.",
            "evidence_refs": ["obs_ais_gap_h77", "obs_sar_unmatched_001", "obs_weather_001", "obs_network_001", "obs_osint_001"],
            "features": {"mission_impact": 0.97, "urgency": 0.92, "confidence": 0.80, "trust": 0.78, "novelty": 0.90, "network_efficiency": 0.98},
            "raw_bytes": 2004000,
            "semantic_bytes": 1150,
        },
    ]

    semantic_events = []
    evidence_bundles = []
    for spec in event_specs:
        priority = score(spec["features"])
        semantic_events.append({**{k: v for k, v in spec.items() if k not in {"features"}}, "priority": priority, "priority_features": spec["features"], "mock_notice": "Synthetic event for safe hackathon demo."})
        evidence_bundles.append(
            {
                "bundle_id": "eb_" + spec["event_id"].replace("evt_", ""),
                "event_id": spec["event_id"],
                "modality_slots": {
                    "ais": "available" if "obs_ais_gap_h77" in spec["evidence_refs"] else "not_used",
                    "sar": "available" if "obs_sar_unmatched_001" in spec["evidence_refs"] else "not_used",
                    "weather": "available" if "obs_weather_001" in spec["evidence_refs"] else "not_used",
                    "osint": "available" if "obs_osint_001" in spec["evidence_refs"] else "not_used",
                    "network": "available" if "obs_network_001" in spec["evidence_refs"] else "not_used",
                    "operator_report": "available" if "obs_operator_lowtrust_001" in spec["evidence_refs"] else "not_used",
                },
                "availability_mask": {
                    "ais": "obs_ais_gap_h77" in spec["evidence_refs"],
                    "sar": "obs_sar_unmatched_001" in spec["evidence_refs"],
                    "weather": "obs_weather_001" in spec["evidence_refs"],
                    "osint": "obs_osint_001" in spec["evidence_refs"],
                    "network": "obs_network_001" in spec["evidence_refs"],
                    "operator_report": "obs_operator_lowtrust_001" in spec["evidence_refs"],
                },
                "evidence_refs": spec["evidence_refs"],
                "confidence": spec["features"]["confidence"],
                "trust_score": spec["features"]["trust"],
                "freshness_seconds": 300 if spec["severity"] in {"high", "critical"} else 1800,
                "review_status": "needs_analyst_review" if spec["severity"] in {"high", "critical"} else "context_only",
                "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value.",
            }
        )

    routing_results = {}
    for mode, config in NETWORK_MODES.items():
        packets = []
        sent = 0
        semantic_bytes_sent = 0
        raw_bytes_represented = 0
        for event in semantic_events:
            if mode == "local_only":
                decision = "hold_local"
            elif event["priority"] >= config["send_threshold"]:
                decision = "send"
            elif event["priority"] >= config["defer_threshold"]:
                decision = "defer"
            else:
                decision = "drop"
            if decision == "send":
                sent += 1
                semantic_bytes_sent += event["semantic_bytes"]
                raw_bytes_represented += event["raw_bytes"]
            packets.append(
                {
                    "packet_id": "pkt_" + mode + "_" + event["event_id"].replace("evt_", ""),
                    "event_id": event["event_id"],
                    "network_mode": mode,
                    "payload_tier": "full_event" if mode == "full_sync" else "event_delta" if mode == "delta_sync" else "alert_card" if mode == "semantic_summary" else "critical_summary" if mode == "store_forward" else "local_cache",
                    "decision": decision,
                    "bytes_raw_estimate": event["raw_bytes"],
                    "bytes_semantic": event["semantic_bytes"] if decision == "send" else 0,
                }
            )
        raw_total = sum(event["raw_bytes"] for event in semantic_events)
        semantic_total = semantic_bytes_sent
        routing_results[mode] = {
            "mode": mode,
            "network": {k: v for k, v in config.items() if k not in {"send_threshold", "defer_threshold"}},
            "packets": packets,
            "metrics": {
                "events_sent": sent,
                "events_total": len(semantic_events),
                "raw_bytes_total_if_full_feed": raw_total,
                "raw_bytes_represented_by_sent_events": raw_bytes_represented,
                "semantic_bytes_sent": semantic_total,
                "bytes_saved_pct_vs_full_feed": round(100 * (1 - semantic_total / raw_total), 2) if raw_total else 0,
                "message_survival_rate": round(sent / len(semantic_events), 3),
            },
        }

    return {
        "metadata": {
            "dataset_id": "resilient_maritime_cop_mock_v0_1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario_name": "AIS silence and SAR mismatch under degraded ship-to-shore link",
            "mock_dataset": True,
            "safety_note": "Synthetic, redacted-style demo data. No real vessel identity, personal data, or operational claim.",
            "design_doc": "06_prototype/docs/resilient_maritime_cop_technical_design.md",
            "schema_doc": "05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md",
        },
        "scenario": {
            "aoi": {
                "name": "Yellow Sea training AOI",
                "bounds": {"lat_min": 36.95, "lat_max": 37.65, "lon_min": 125.05, "lon_max": 126.05},
                "center": {"lat": 37.32, "lon": 125.65},
            },
            "time_window": {"start": "2026-07-04T01:30:00Z", "end": "2026-07-04T03:00:00Z"},
            "narrative": "A cooperative AIS track goes stale, an independent SAR-like detection appears nearby, weather reduces confirmation options, and the network drops into semantic-summary mode.",
        },
        "source_catalog": source_catalog,
        "vessels": vessels,
        "tracks": tracks,
        "observations": observations,
        "evidence_bundles": evidence_bundles,
        "semantic_events": semantic_events,
        "network_modes": NETWORK_MODES,
        "routing_results": routing_results,
        "briefing": {
            "headline": "Critical dark-vessel review candidate should survive semantic-summary mode.",
            "grounded_claims": [
                {"claim": "Haneul-77 AIS is stale after 02:05Z.", "evidence_refs": ["obs_ais_gap_h77"]},
                {"claim": "A SAR-like detection appears without AIS match at 02:24Z.", "evidence_refs": ["obs_sar_unmatched_001"]},
                {"claim": "Weather and network degradation reduce raw-feed confirmation.", "evidence_refs": ["obs_weather_001", "obs_network_001"]},
                {"claim": "A conflicting human report should be retained but down-weighted.", "evidence_refs": ["obs_operator_lowtrust_001"]},
            ],
            "operator_summary": "Send the composite alert card first; queue raw SAR/AIS evidence for later sync; do not infer legal status without analyst review.",
        },
    }


def write_readme(dataset: dict) -> str:
    return f"""# Resilient Maritime COP Mock Dataset

- Dataset ID: `{dataset['metadata']['dataset_id']}`
- Generated: {dataset['metadata']['generated_at']}
- Scenario: {dataset['scenario']['narrative']}

## Safety

All values are synthetic. Vessel identifiers are masked-style placeholders. The data is meant to demonstrate architecture and routing behavior, not to make real maritime claims.

## Why This Dataset Exists

The live API collection workstream may produce real snapshots later. Until then, this dataset keeps the demo runnable and reproducible.

Each mock source states which real source type it can be replaced by:

- AIS-like tracks -> data.go.kr maritime AIS, Global Fishing Watch, NOAA AIS
- SAR-like detections -> Copernicus Sentinel-1, xView3, Global Fishing Watch SAR detections
- weather hazard -> KMA APIHub, Copernicus Marine, NOAA/NCEP
- OSINT incident -> GDELT and official advisories
- network state -> Cloudflare Radar, Ookla, RIPE Atlas, synthetic netem

## Files

- `mock_dataset.json`: full dataset used by the demo app
- app copy: `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.json`

## Key Demonstration

The same set of events is routed differently under each network mode:

- `full_sync`: all event details can move
- `delta_sync`: compact event deltas move
- `semantic_summary`: only high-priority alert cards survive
- `store_forward`: almost everything queues
- `local_only`: no remote transmission

This shows the T3 point: the project is not just maritime sensing; it is mission-aware communication under constrained links.
"""


def main() -> None:
    dataset = build_dataset()
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset_text = json.dumps(dataset, ensure_ascii=False, indent=2)
    dataset_js = "window.__D4D_MOCK_DATASET = " + dataset_text + ";\n"
    (SAMPLE_DIR / "mock_dataset.json").write_text(dataset_text + "\n", encoding="utf-8")
    (APP_DATA_DIR / "mock_dataset.json").write_text(dataset_text + "\n", encoding="utf-8")
    (APP_DATA_DIR / "mock_dataset.js").write_text(dataset_js, encoding="utf-8")
    (SAMPLE_DIR / "README.md").write_text(write_readme(dataset), encoding="utf-8")
    print(json.dumps({
        "dataset": str(SAMPLE_DIR / "mock_dataset.json"),
        "app_copy": str(APP_DATA_DIR / "mock_dataset.json"),
        "app_js_copy": str(APP_DATA_DIR / "mock_dataset.js"),
        "events": len(dataset["semantic_events"]),
        "observations": len(dataset["observations"]),
        "routing_modes": list(dataset["routing_results"].keys()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

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
CIVIL_INFRA_DATA_PATH = PROJECT_ROOT / "06_prototype/app/korea_civil_infra_cop/data/civil_infra_dataset.json"


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


def load_civil_infra_context() -> dict:
    """Load the Korea civil infra COP as a safe inset/reference layer.

    The source dataset intentionally keeps sensitive telecom, power, public IT,
    and protected-facility layers coarse or synthetic. This function preserves
    that boundary and imports only bounded public-safe context for the S-DOT map.
    """
    if not CIVIL_INFRA_DATA_PATH.exists():
        return {
            "schema": "korea_civil_infra_cop.missing",
            "display_mode": "not_loaded",
            "aoi": {"name": "Korea civil infrastructure context", "bounds": {"lat_min": 37.43, "lat_max": 37.69, "lon_min": 126.78, "lon_max": 127.16}},
            "safety_boundary": "Civil infrastructure dataset not found; S-DOT demo remains synthetic.",
            "layers": {"medical_facilities": [], "building_exposure_cells": [], "communications_context_cells": [], "power_it_aggregates": []},
            "semantic_events": [],
            "safety_rules": [],
            "source_catalog": [],
        }

    raw = json.loads(CIVIL_INFRA_DATA_PATH.read_text(encoding="utf-8"))
    layers = raw.get("layers", {})
    return {
        "schema": raw.get("schema", "korea_civil_infra_cop.v0.1"),
        "generated_at": raw.get("generated_at"),
        "display_mode": "map_inset_reference_layer",
        "aoi": raw.get("scenario", {}).get("aoi", {}),
        "safety_boundary": raw.get("scenario", {}).get("safety_boundary", ""),
        "use_note": "Used as authorized opportunistic bearer/resource context only; not a guaranteed military network or real force-support layer.",
        "layers": {
            "medical_facilities": layers.get("medical_facilities", [])[:6],
            "building_exposure_cells": layers.get("building_exposure_cells", [])[:5],
            "communications_context_cells": layers.get("communications_context_cells", []),
            "power_it_aggregates": layers.get("power_it_aggregates", []),
        },
        "semantic_events": raw.get("semantic_events", []),
        "safety_rules": raw.get("safety_rules", []),
        "source_catalog": raw.get("source_catalog", []),
    }


def build_dataset() -> dict:
    korea_civil_infra_context = load_civil_infra_context()
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
        {
            "source_id": "mock_unit_state",
            "label": "Synthetic isolated-unit state",
            "real_replacement": ["redacted SITREP", "training exercise telemetry", "unit-local COP export"],
            "source_rationale": "Real unit locations and readiness are sensitive. The mock layer shows the schema and routing behavior without operational disclosure.",
            "mock_notice": "Fully synthetic unit and readiness data.",
        },
        {
            "source_id": "mock_civil_comms_assets",
            "label": "Synthetic civil/public communications asset layer",
            "real_replacement": ["KCA public radio-station datasets", "Spectrum Map", "PS-LTE/LTE-M/LTE-R public references", "telco-provided emergency inventory"],
            "source_rationale": "Korea's dense communications environment can be modeled as candidate bearers only when lawful authority, authentication, power, backhaul, and priority policies are satisfied.",
            "mock_notice": "Synthetic assets; not real base-station, AP, or military network data.",
        },
        {
            "source_id": "mock_support_resources",
            "label": "Synthetic support and sustainment resources",
            "real_replacement": ["public hospital/facility datasets", "OSM/VWorld road context", "exercise logistics tables"],
            "source_rationale": "Support routing and resource allocation can be demonstrated with public facility context and synthetic military resources.",
            "mock_notice": "Synthetic support units and resource capacities.",
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

    observations.extend(
        [
            {
                "observation_id": "obs_unit_river1_readiness",
                "source_id": "mock_unit_state",
                "sensor_type": "UNIT_STATUS",
                "time": "2026-07-04T02:31:00Z",
                "location": {"lat": 37.23, "lon": 125.40},
                "claim": "River-1 entered intermittent contact; power at 42%, local COP cached, medical support priority elevated.",
                "raw_ref": "mock://unit/river_1/readiness_0231",
                "raw_bytes": 74000,
            },
            {
                "observation_id": "obs_intent_packet_001",
                "source_id": "mock_unit_state",
                "sensor_type": "MISSION_INTENT",
                "time": "2026-07-04T02:05:00Z",
                "location": {"lat": 37.32, "lon": 125.65},
                "claim": "Mission intent packet prioritizes continuity of local awareness, medical readiness, and critical comms restoration.",
                "raw_ref": "mock://hq/intent_packet/mission_continuity_alpha",
                "raw_bytes": 18000,
            },
            {
                "observation_id": "obs_civil_bearer_bridge7",
                "source_id": "mock_civil_comms_assets",
                "sensor_type": "INFRASTRUCTURE",
                "time": "2026-07-04T02:34:00Z",
                "location": {"lat": 37.48, "lon": 125.48},
                "claim": "Bridge-7 candidate relay has backup power and partial line-of-sight coverage, but requires emergency authorization.",
                "raw_ref": "mock://civil_comms/bridge_7/status_0234",
                "raw_bytes": 56000,
            },
            {
                "observation_id": "obs_support_route_medic",
                "source_id": "mock_support_resources",
                "sensor_type": "SUPPORT_RESOURCE",
                "time": "2026-07-04T02:36:00Z",
                "location": {"lat": 37.56, "lon": 125.82},
                "claim": "Medic-2 support option can reach the predicted River-1 corridor in 42 minutes if Route Blue remains open.",
                "raw_ref": "mock://support/medic_2/route_blue",
                "raw_bytes": 88000,
            },
        ]
    )

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

    event_specs.extend(
        [
            {
                "event_id": "evt_unit_isolated_river1",
                "event_type": "UNIT_ISOLATED",
                "severity": "critical",
                "time": "2026-07-04T02:31:00Z",
                "location": {"lat": 37.23, "lon": 125.40, "area": "Synthetic coastal training corridor"},
                "entity_refs": ["unit_river_1"],
                "summary": "River-1 shifted to intermittent contact with local COP only partially visible to HQ.",
                "why_it_matters": "HQ cannot treat the last known position as live truth; the command board must switch to predicted local COP with uncertainty.",
                "recommended_action": "Send only intent and critical support packets; keep local event log queued for rejoin.",
                "evidence_refs": ["obs_unit_river1_readiness", "obs_network_001", "obs_intent_packet_001"],
                "features": {"mission_impact": 0.98, "urgency": 0.94, "confidence": 0.82, "trust": 0.80, "novelty": 0.86, "network_efficiency": 0.98},
                "raw_bytes": 74000,
                "semantic_bytes": 870,
            },
            {
                "event_id": "evt_support_request_medical_power",
                "event_type": "SUPPORT_REQUEST",
                "severity": "high",
                "time": "2026-07-04T02:36:00Z",
                "location": {"lat": 37.34, "lon": 125.54, "area": "Predicted River-1 corridor"},
                "entity_refs": ["unit_river_1", "support_medic_2", "resource_power_pack_a"],
                "summary": "River-1 needs medical standby and power extension before the next contact window.",
                "why_it_matters": "Power depletion can break the local COP and S-DOT outbox before the unit physically moves out of range.",
                "recommended_action": "Rank Medic-2 and Comms Relay-3 as support options; reserve contact window for readiness and route packets.",
                "evidence_refs": ["obs_unit_river1_readiness", "obs_support_route_medic"],
                "features": {"mission_impact": 0.90, "urgency": 0.88, "confidence": 0.76, "trust": 0.78, "novelty": 0.64, "network_efficiency": 0.92},
                "raw_bytes": 162000,
                "semantic_bytes": 930,
            },
            {
                "event_id": "evt_civil_bearer_candidate_bridge7",
                "event_type": "CIVIL_BEARER_CANDIDATE",
                "severity": "medium",
                "time": "2026-07-04T02:34:00Z",
                "location": {"lat": 37.48, "lon": 125.48, "area": "Synthetic infrastructure layer"},
                "entity_refs": ["civil_comms_bridge_7", "unit_river_1"],
                "summary": "Bridge-7 is a candidate emergency bearer but is not automatically available.",
                "why_it_matters": "Dense Korean infrastructure may help continuity only if legal status, authentication, power, backhaul, and priority policies align.",
                "recommended_action": "Show as candidate bearer with authorization required; do not assume access.",
                "evidence_refs": ["obs_civil_bearer_bridge7", "obs_network_001"],
                "features": {"mission_impact": 0.72, "urgency": 0.62, "confidence": 0.68, "trust": 0.70, "novelty": 0.70, "network_efficiency": 0.90},
                "raw_bytes": 56000,
                "semantic_bytes": 760,
            },
            {
                "event_id": "evt_rejoin_window_predicted",
                "event_type": "REJOIN_WINDOW",
                "severity": "medium",
                "time": "2026-07-04T02:44:00Z",
                "location": {"lat": 37.38, "lon": 125.58, "area": "Predicted River-1 corridor"},
                "entity_refs": ["unit_river_1", "link_alpha"],
                "summary": "Next 90-second contact window is predicted near the River-1 corridor.",
                "why_it_matters": "The S-DOT queue must choose which messages to send before the window closes.",
                "recommended_action": "Transmit intent receipt, readiness snapshot, and support request before lower-priority evidence.",
                "evidence_refs": ["obs_network_001", "obs_unit_river1_readiness"],
                "features": {"mission_impact": 0.78, "urgency": 0.86, "confidence": 0.66, "trust": 0.70, "novelty": 0.58, "network_efficiency": 0.95},
                "raw_bytes": 45000,
                "semantic_bytes": 710,
            },
        ]
    )

    mission_intent = {
        "mission_id": "mission_continuity_alpha",
        "display_name": "Mission Continuity Alpha",
        "commander_intent": "Maintain local awareness, protect unit continuity, prioritize medical readiness and communications restoration under DDIL conditions.",
        "priority_weights": {
            "medical": 0.28,
            "communications": 0.24,
            "power": 0.20,
            "local_awareness": 0.18,
            "maritime_context": 0.10,
        },
        "constraints": [
            "No real unit data in demo",
            "Use public context data only",
            "Treat civil infrastructure as candidate bearer, not guaranteed access",
            "Human approval required for support decisions",
        ],
        "valid_until": "2026-07-04T04:00:00Z",
    }

    unit_nodes = [
        {
            "unit_id": "unit_river_1",
            "display_name": "River-1",
            "unit_type": "synthetic_coastal_team",
            "comm_state": "intermittent",
            "c2_mode": "delegated",
            "last_confirmed": {
                "time": "2026-07-04T02:31:00Z",
                "lat": 37.23,
                "lon": 125.40,
                "source": "obs_unit_river1_readiness",
            },
            "predicted_state": {
                "time": "2026-07-04T02:44:00Z",
                "lat": 37.38,
                "lon": 125.58,
                "confidence": 0.62,
                "uncertainty_km": 8.6,
                "likely_phase": "Phase 2: hold local COP and await contact window",
                "assumptions": ["follows intent corridor", "speed constrained by sea state", "power saving mode active"],
            },
            "branch_scenarios": [
                {"branch": "main_route_continue", "label": "주경로 지속", "probability": 0.52, "confidence_delta_per_10m": -0.06},
                {"branch": "hold_local_cop", "label": "은폐/대기하며 로컬 상황도 유지", "probability": 0.31, "confidence_delta_per_10m": -0.04},
                {"branch": "detour_to_support_node", "label": "지원 노드 우회", "probability": 0.17, "confidence_delta_per_10m": -0.08},
            ],
            "readiness": {
                "power_pct": 42,
                "medical_status": "yellow",
                "local_cop_cache": "valid_but_aging",
                "sdot_outbox": 6,
                "critical_supplies_hours": 7.5,
            },
        },
        {
            "unit_id": "unit_anchor_2",
            "display_name": "Anchor-2",
            "unit_type": "synthetic_support_observer",
            "comm_state": "degraded",
            "c2_mode": "collaborative",
            "last_confirmed": {"time": "2026-07-04T02:33:00Z", "lat": 37.53, "lon": 125.38, "source": "mock_unit_state"},
            "predicted_state": {"time": "2026-07-04T02:44:00Z", "lat": 37.51, "lon": 125.43, "confidence": 0.77, "uncertainty_km": 3.2, "likely_phase": "relay watch"},
            "branch_scenarios": [
                {"branch": "maintain_relay_watch", "label": "중계 감시 유지", "probability": 0.68, "confidence_delta_per_10m": -0.03},
                {"branch": "shift_to_bridge7_line", "label": "Bridge-7 방향 중계선 이동", "probability": 0.22, "confidence_delta_per_10m": -0.05},
                {"branch": "fall_back_power_save", "label": "전력 절약 대기", "probability": 0.10, "confidence_delta_per_10m": -0.04},
            ],
            "readiness": {"power_pct": 68, "medical_status": "green", "local_cop_cache": "fresh", "sdot_outbox": 2, "critical_supplies_hours": 13.0},
        },
    ]

    pace_bearer_ladder = [
        {
            "pace": "P",
            "label": "전술 IP망",
            "bearer_type": "tactical_ip",
            "role": "정상 연결 시 COP/근거 동기화",
            "availability_by_mode": {"full_sync": "active", "delta_sync": "active", "semantic_summary": "degraded", "store_forward": "degraded", "local_only": "down"},
            "risk_note": "실제 전술망 세부는 데모에 포함하지 않음.",
        },
        {
            "pace": "A",
            "label": "위성/장거리 백업",
            "bearer_type": "satellite_or_longhaul_backup",
            "role": "저속 명령 의도·readiness packet 전달",
            "availability_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "active", "store_forward": "degraded", "local_only": "down"},
            "risk_note": "전력·가시성·혼잡·교란 조건에 따라 품질 변동.",
        },
        {
            "pace": "C",
            "label": "승인형 민간/공공 bearer",
            "bearer_type": "authorized_opportunistic_bearer",
            "role": "PS-LTE/LTE-M/상용망/유선 백홀 후보",
            "availability_by_mode": {"full_sync": "standby", "delta_sync": "candidate", "semantic_summary": "candidate", "store_forward": "candidate", "local_only": "unavailable_without_authority"},
            "risk_note": "법적 권한, 인증, 전력, 백홀, 보안, 감청 위험 검토 필요.",
        },
        {
            "pace": "E",
            "label": "메시/스토어-포워드",
            "bearer_type": "mesh_store_forward_or_physical_sync",
            "role": "접속창 전까지 로컬 저장 후 재연결 감사",
            "availability_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "standby", "store_forward": "active", "local_only": "local_only"},
            "risk_note": "실시간 지휘가 아니라 임무 지속성과 사후 동기화에 초점.",
        },
    ]

    civil_comms_assets = [
        {
            "asset_id": "civil_comms_bridge_7",
            "display_name": "Bridge-7 Candidate Bearer",
            "bearer_type": "5G/LTE relay candidate",
            "owner_type": "civil_public_infra_synthetic",
            "lat": 37.48,
            "lon": 125.48,
            "legal_status": "emergency_order_required",
            "power_state": "backup_power_2h",
            "backhaul_state": "degraded_fiber",
            "auth_required": True,
            "priority_capable": True,
            "estimated_bandwidth_kbps": 256,
            "confidence": 0.62,
        },
        {
            "asset_id": "civil_comms_hill_3",
            "display_name": "Hill-3 Public Safety Relay",
            "bearer_type": "PS-LTE/LTE-M proxy",
            "owner_type": "public_safety_synthetic",
            "lat": 37.60,
            "lon": 125.76,
            "legal_status": "preauthorized_exercise_profile",
            "power_state": "generator_6h",
            "backhaul_state": "microwave_partial",
            "auth_required": True,
            "priority_capable": True,
            "estimated_bandwidth_kbps": 384,
            "confidence": 0.72,
        },
    ]

    support_options = [
        {
            "support_id": "support_medic_2",
            "display_name": "Medic-2 Support Option",
            "support_type": "medical_standby",
            "lat": 37.56,
            "lon": 125.82,
            "route_name": "Route Blue",
            "eta_minutes": 42,
            "route_risk": 0.34,
            "resource_cost": 0.38,
            "support_score": 0.82,
            "why_ranked": "Best medical coverage with acceptable route risk and no additional comms authorization dependency.",
        },
        {
            "support_id": "support_comms_relay_3",
            "display_name": "Comms Relay-3",
            "support_type": "mobile_relay",
            "lat": 37.44,
            "lon": 125.30,
            "route_name": "Route Green",
            "eta_minutes": 35,
            "route_risk": 0.41,
            "resource_cost": 0.46,
            "support_score": 0.78,
            "why_ranked": "Fastest communications restoration option, but weather and backhaul uncertainty reduce confidence.",
        },
        {
            "support_id": "support_power_pack_a",
            "display_name": "Power Pack A",
            "support_type": "power_extension",
            "lat": 37.50,
            "lon": 125.92,
            "route_name": "Route Amber",
            "eta_minutes": 58,
            "route_risk": 0.29,
            "resource_cost": 0.32,
            "support_score": 0.70,
            "why_ranked": "Useful for endurance, but less urgent than medical standby and comms relay.",
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

    sdot_messages = [
        {
            "message_id": "sdot_001",
            "family": "IntentUpdate",
            "from": "HQ",
            "to": "River-1",
            "event_id": "evt_unit_isolated_river1",
            "payload_tier": "T2_SEMANTIC",
            "priority": 0.94,
            "raw_bytes": 18000,
            "semantic_bytes": 520,
            "decision_value": "Keeps local decisions aligned with mission intent while disconnected.",
        },
        {
            "message_id": "sdot_002",
            "family": "ReadinessSnapshot",
            "from": "River-1",
            "to": "HQ",
            "event_id": "evt_support_request_medical_power",
            "payload_tier": "T3_PRIORITY_CARD",
            "priority": 0.89,
            "raw_bytes": 74000,
            "semantic_bytes": 610,
            "decision_value": "Changes support allocation because power and medical status are degrading.",
        },
        {
            "message_id": "sdot_003",
            "family": "SupportRequest",
            "from": "River-1",
            "to": "HQ",
            "event_id": "evt_support_request_medical_power",
            "payload_tier": "T3_PRIORITY_CARD",
            "priority": 0.87,
            "raw_bytes": 88000,
            "semantic_bytes": 690,
            "decision_value": "Triggers ranking of Medic-2, Comms Relay-3, and Power Pack A.",
        },
        {
            "message_id": "sdot_004",
            "family": "NetworkStateUpdate",
            "from": "Infrastructure Layer",
            "to": "HQ",
            "event_id": "evt_civil_bearer_candidate_bridge7",
            "payload_tier": "T2_SEMANTIC",
            "priority": 0.70,
            "raw_bytes": 56000,
            "semantic_bytes": 540,
            "decision_value": "Identifies Bridge-7 as possible but authorization-gated bearer.",
        },
        {
            "message_id": "sdot_005",
            "family": "RejoinWindow",
            "from": "HQ",
            "to": "River-1",
            "event_id": "evt_rejoin_window_predicted",
            "payload_tier": "T3_PRIORITY_CARD",
            "priority": 0.76,
            "raw_bytes": 45000,
            "semantic_bytes": 490,
            "decision_value": "Determines which queued bundles are sent during a 90-second contact window.",
        },
    ]

    rejoin_audit = {
        "audit_id": "audit_rejoin_river_1_preview",
        "status": "pending_contact_window",
        "prediction_before_rejoin": {
            "lat": unit_nodes[0]["predicted_state"]["lat"],
            "lon": unit_nodes[0]["predicted_state"]["lon"],
            "confidence": unit_nodes[0]["predicted_state"]["confidence"],
            "uncertainty_km": unit_nodes[0]["predicted_state"]["uncertainty_km"],
        },
        "expected_sync_order": ["sdot_001", "sdot_002", "sdot_003", "sdot_005", "sdot_004"],
        "open_questions": [
            "Did River-1 remain inside the predicted corridor?",
            "Did power saving preserve local COP until contact?",
            "Was Bridge-7 legally/technically available as a bearer?",
        ],
    }

    return {
        "metadata": {
            "dataset_id": "s_dot_mission_continuity_mock_v0_3",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario_name": "S-DOT mission continuity under isolated unit and degraded tactical network",
            "display_name_ko": "S-DOT 임무지속 COP",
            "sdot_definition": "S-DOT = Semantic Data On Tactical-network. This is a hackathon concept label, not an existing tactical-link standard.",
            "mock_dataset": True,
            "safety_note": "Synthetic, redacted-style demo data. No real unit location, force disposition, vessel identity, personal data, or operational claim.",
            "design_doc": "06_prototype/docs/resilient_maritime_cop_technical_design.md",
            "schema_doc": "05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md",
            "plan_doc": "02_problem_statements/hypotheses/s_dot_mission_continuity_cop_plan_20260704.md",
        },
        "scenario": {
            "aoi": {
                "name": "Synthetic coastal training AOI",
                "bounds": {"lat_min": 36.95, "lat_max": 37.65, "lon_min": 125.05, "lon_max": 126.05},
                "center": {"lat": 37.32, "lon": 125.65},
            },
            "time_window": {"start": "2026-07-04T01:30:00Z", "end": "2026-07-04T03:00:00Z"},
            "narrative": "River-1 becomes intermittently connected while maritime context, weather, support resources, and candidate civil/public bearers must be compressed into S-DOT semantic packets.",
        },
        "source_catalog": source_catalog,
        "mission_intent": mission_intent,
        "unit_nodes": unit_nodes,
        "pace_bearer_ladder": pace_bearer_ladder,
        "civil_comms_assets": civil_comms_assets,
        "korea_civil_infra_context": korea_civil_infra_context,
        "support_options": support_options,
        "sdot_messages": sdot_messages,
        "rejoin_audit": rejoin_audit,
        "vessels": vessels,
        "tracks": tracks,
        "observations": observations,
        "evidence_bundles": evidence_bundles,
        "semantic_events": semantic_events,
        "network_modes": NETWORK_MODES,
        "routing_results": routing_results,
        "briefing": {
            "headline": "S-DOT should preserve intent, readiness, and support requests when raw data cannot move.",
            "grounded_claims": [
                {"claim": "River-1 is intermittently connected and should be shown as predicted, not live.", "evidence_refs": ["obs_unit_river1_readiness", "obs_network_001"]},
                {"claim": "Mission intent prioritizes local awareness, medical readiness, and comms restoration.", "evidence_refs": ["obs_intent_packet_001"]},
                {"claim": "Bridge-7 is a candidate bearer only if authorization, power, backhaul, and authentication align.", "evidence_refs": ["obs_civil_bearer_bridge7"]},
                {"claim": "Medic-2 is the highest-ranked support option in the synthetic scenario.", "evidence_refs": ["obs_support_route_medic"]},
                {"claim": "Haneul-77 AIS is stale after 02:05Z.", "evidence_refs": ["obs_ais_gap_h77"]},
                {"claim": "A SAR-like detection appears without AIS match at 02:24Z.", "evidence_refs": ["obs_sar_unmatched_001"]},
                {"claim": "Weather and network degradation reduce raw-feed confirmation.", "evidence_refs": ["obs_weather_001", "obs_network_001"]},
            ],
            "operator_summary": "Send intent receipt, readiness snapshot, and support request before lower-priority evidence; queue raw AIS/SAR/context data for later sync; keep all unit/resource data synthetic in public demos.",
        },
    }


def build_dataset() -> dict:
    """Build the current Seoul urban-ground S-DOT demo dataset.

    This intentionally supersedes the earlier maritime mock dataset while
    keeping the historical generator code above for traceability.
    """
    korea_civil_infra_context = load_civil_infra_context()
    civil_layers = korea_civil_infra_context.get("layers", {})

    source_catalog = [
        {
            "source_id": "mock_unit_state",
            "label": "Synthetic urban unit state",
            "real_replacement": ["redacted SITREP", "training exercise telemetry", "unit-local COP export"],
            "source_rationale": "Real unit locations and readiness are sensitive. The mock layer shows the schema and routing behavior without operational disclosure.",
            "mock_notice": "Fully synthetic unit and readiness data over a public Seoul map.",
        },
        {
            "source_id": "mock_network_state",
            "label": "Synthetic DDIL network states",
            "real_replacement": ["Cloudflare Radar", "Ookla Open Data", "RIPE Atlas", "Linux tc netem"],
            "source_rationale": "T3 differentiation comes from showing what survives under bandwidth, latency, packet loss, and link outage.",
            "mock_notice": "Synthetic network profile designed for repeatable demo behavior.",
        },
        {
            "source_id": "mock_civil_comms_assets",
            "label": "Authorized opportunistic bearer candidates",
            "real_replacement": ["KCA public radio-station datasets", "PS-LTE/LTE-M/LTE-R public references", "telco-provided emergency inventory"],
            "source_rationale": "Korea's dense communications environment can be modeled as candidate bearers only when lawful authority, authentication, power, backhaul, and priority policies are satisfied.",
            "mock_notice": "Coarse or synthetic assets; not real base-station, AP, backbone, or military network data.",
        },
        {
            "source_id": "public_civil_infra_context",
            "label": "Korea civil infrastructure COP context",
            "real_replacement": ["HIRA/NMC hospital APIs", "OSM building footprints", "MOLIT building data", "MOIS aggregate public IT/power references"],
            "source_rationale": "Public hospitals, public map tiles, building footprints, and aggregate infrastructure cells provide protected-civilian and support context.",
            "mock_notice": "Sensitive infrastructure is aggregate/coarse only. Public hospitals are protected support nodes, not targets.",
        },
        {
            "source_id": "mock_weather_hazard",
            "label": "Synthetic urban weather / visibility warning",
            "real_replacement": ["KMA APIHub", "Open-Meteo", "data.go.kr weather"],
            "source_rationale": "Weather affects ground mobility, sensor confidence, and support route risk.",
            "mock_notice": "Synthetic warning; not an official forecast.",
        },
        {
            "source_id": "mock_osint_incident",
            "label": "Synthetic public advisory / OSINT context",
            "real_replacement": ["GDELT", "official safety advisories", "public emergency notices"],
            "source_rationale": "OSINT gives cited narrative context but must not be treated as sensor truth.",
            "mock_notice": "Synthetic advisory metadata; no operational claim.",
        },
        {
            "source_id": "mock_threat_assessment",
            "label": "Synthetic opposing-route assessment",
            "real_replacement": ["exercise injects", "approved training intelligence feed", "analyst-authored scenario branches"],
            "source_rationale": "The demo needs an opposing movement hypothesis, but real threat routes, order of battle, and tactical intelligence are sensitive.",
            "mock_notice": "Fully synthetic route candidates for UI and S-DOT prioritization only.",
        },
        {
            "source_id": "mock_support_resources",
            "label": "Synthetic support and sustainment resources",
            "real_replacement": ["public hospital/facility datasets", "OSM/VWorld road context", "exercise logistics tables"],
            "source_rationale": "Support routing and resource allocation are demonstrated with public facility context plus synthetic support resources.",
            "mock_notice": "Synthetic support units and resource capacities.",
        },
    ]

    observations = [
        {
            "observation_id": "obs_network_001",
            "source_id": "mock_network_state",
            "sensor_type": "NETWORK",
            "time": "2026-07-04T02:18:00Z",
            "location": {"lat": 37.535, "lon": 126.970},
            "claim": "Central Seoul link quality dropped below semantic-summary threshold near the Han River crossing corridor.",
            "raw_ref": "mock://network/seoul_link_alpha#state=semantic_summary",
            "raw_bytes": 21000,
        },
        {
            "observation_id": "obs_weather_001",
            "source_id": "mock_weather_hazard",
            "sensor_type": "WEATHER",
            "time": "2026-07-04T02:10:00Z",
            "location": {"lat": 37.540, "lon": 126.930},
            "claim": "Rain and reduced visibility raise movement risk across Mapo/Yeouido river-crossing routes.",
            "raw_ref": "mock://weather/kma_style_warning#seoul_river_crossing",
            "raw_bytes": 65000,
        },
        {
            "observation_id": "obs_osint_001",
            "source_id": "mock_osint_incident",
            "sensor_type": "OSINT",
            "time": "2026-07-04T01:35:00Z",
            "location": {"lat": 37.570, "lon": 126.985},
            "claim": "Public advisory context flags congestion and emergency-service access pressure around the central business district.",
            "raw_ref": "mock://osint/gdelt_style/seoul_cbd_advisory",
            "raw_bytes": 38000,
        },
        {
            "observation_id": "obs_operator_lowtrust_001",
            "source_id": "mock_operator_report",
            "sensor_type": "HUMAN_REPORT",
            "time": "2026-07-04T02:28:00Z",
            "location": {"lat": 37.504, "lon": 127.033},
            "claim": "Unconfirmed field report conflicts with predicted Alpha-1 branch timing and should remain contested.",
            "raw_ref": "mock://operator/seoul_report_20260704_0228",
            "raw_bytes": 12000,
        },
        {
            "observation_id": "obs_unit_alpha1_readiness",
            "source_id": "mock_unit_state",
            "sensor_type": "UNIT_STATUS",
            "time": "2026-07-04T02:31:00Z",
            "location": {"lat": 37.532, "lon": 126.980},
            "claim": "Alpha-1 entered intermittent contact; power at 42%, local COP cached, medical support priority elevated.",
            "raw_ref": "mock://unit/alpha_1/readiness_0231",
            "raw_bytes": 74000,
        },
        {
            "observation_id": "obs_intent_packet_001",
            "source_id": "mock_unit_state",
            "sensor_type": "MISSION_INTENT",
            "time": "2026-07-04T02:05:00Z",
            "location": {"lat": 37.5665, "lon": 126.9780},
            "claim": "Mission intent packet prioritizes civilian protection, unit continuity, medical readiness, and critical comms restoration.",
            "raw_ref": "mock://hq/intent_packet/urban_continuity_alpha",
            "raw_bytes": 18000,
        },
        {
            "observation_id": "obs_civil_bearer_han",
            "source_id": "mock_civil_comms_assets",
            "sensor_type": "INFRASTRUCTURE",
            "time": "2026-07-04T02:34:00Z",
            "location": {"lat": 37.535, "lon": 126.970},
            "claim": "Han River communications aggregate is a candidate bearer, but legal authority, authentication, power, backhaul, and security conditions are unresolved.",
            "raw_ref": "mock://civil_comms/han_river_aggregate/status_0234",
            "raw_bytes": 56000,
        },
        {
            "observation_id": "obs_support_route_medic",
            "source_id": "mock_support_resources",
            "sensor_type": "SUPPORT_RESOURCE",
            "time": "2026-07-04T02:36:00Z",
            "location": {"lat": 37.5672, "lon": 127.0057},
            "claim": "Medic-2 support option can stage near the public hospital corridor in 28 minutes if the north-central route remains open.",
            "raw_ref": "mock://support/medic_2/route_blue_seoul",
            "raw_bytes": 88000,
        },
        {
            "observation_id": "obs_civilian_exposure_cbd",
            "source_id": "public_civil_infra_context",
            "sensor_type": "URBAN_CONTEXT",
            "time": "2026-07-04T02:20:00Z",
            "location": {"lat": 37.570, "lon": 126.985},
            "claim": "CBD building density and civilian exposure are high, requiring deconfliction and emergency access preservation.",
            "raw_ref": "mock://civil_infra/building_exposure/bld_jongno_jung",
            "raw_bytes": 240000,
        },
        {
            "observation_id": "obs_medical_capacity_north",
            "source_id": "public_civil_infra_context",
            "sensor_type": "MEDICAL",
            "time": "2026-07-04T02:22:00Z",
            "location": {"lat": 37.579, "lon": 126.999},
            "claim": "Central and north-east hospitals provide overlapping public medical support capacity near the AOI.",
            "raw_ref": "mock://civil_infra/medical_capacity/north_central",
            "raw_bytes": 110000,
        },
        {
            "observation_id": "obs_public_it_power",
            "source_id": "public_civil_infra_context",
            "sensor_type": "PUBLIC_INFRA",
            "time": "2026-07-04T02:24:00Z",
            "location": {"lat": 37.552, "lon": 127.002},
            "claim": "Public IT and regional power dependency are continuity context only; exact protected-facility coordinates stay out of the COP.",
            "raw_ref": "mock://civil_infra/power_it/aggregate_context",
            "raw_bytes": 96000,
        },
        {
            "observation_id": "obs_opposing_axis_a",
            "source_id": "mock_threat_assessment",
            "sensor_type": "THREAT_ASSESSMENT",
            "time": "2026-07-04T02:39:00Z",
            "location": {"lat": 37.570, "lon": 126.985},
            "claim": "Synthetic assessment ranks opposing candidate axis A as the highest watch priority, with axis B and C retained as lower-confidence branches.",
            "raw_ref": "mock://scenario/opposing_axis_assessment/v0_5",
            "raw_bytes": 135000,
        },
    ]

    event_specs = [
        {
            "event_id": "evt_network_degraded_001",
            "event_type": "NETWORK_DEGRADED",
            "severity": "high",
            "time": "2026-07-04T02:18:00Z",
            "location": {"lat": 37.535, "lon": 126.970, "area": "Han River crossing corridor"},
            "entity_refs": ["link_seoul_alpha"],
            "summary": "Central Seoul link quality moved from delta sync to semantic summary.",
            "why_it_matters": "The command room can no longer assume raw map/evidence sync, so intent, readiness, support, and uncertainty packets must be prioritized.",
            "recommended_action": "Switch to semantic summary mode and queue raw context for store-forward sync.",
            "evidence_refs": ["obs_network_001"],
            "features": {"mission_impact": 0.84, "urgency": 0.86, "confidence": 0.78, "trust": 0.82, "novelty": 0.56, "network_efficiency": 0.94},
            "raw_bytes": 21000,
            "semantic_bytes": 690,
        },
        {
            "event_id": "evt_weather_hazard_001",
            "event_type": "WEATHER_HAZARD",
            "severity": "medium",
            "time": "2026-07-04T02:10:00Z",
            "location": {"lat": 37.540, "lon": 126.930, "area": "Mapo/Yeouido crossing belt"},
            "entity_refs": ["route_blue_seoul"],
            "summary": "Rain and reduced visibility increase ground movement and confirmation risk.",
            "why_it_matters": "Weather lowers confidence in visual-only reporting and can slow medical, power, and relay support options.",
            "recommended_action": "Increase route uncertainty and prioritize compact readiness/support packets.",
            "evidence_refs": ["obs_weather_001"],
            "features": {"mission_impact": 0.63, "urgency": 0.67, "confidence": 0.78, "trust": 0.83, "novelty": 0.38, "network_efficiency": 0.86},
            "raw_bytes": 65000,
            "semantic_bytes": 740,
        },
        {
            "event_id": "evt_urban_mobility_constraint",
            "event_type": "URBAN_MOBILITY_CONSTRAINT",
            "severity": "high",
            "time": "2026-07-04T02:21:00Z",
            "location": {"lat": 37.540, "lon": 126.930, "area": "Mapo/Yeouido river crossing belt"},
            "entity_refs": ["route_blue_seoul", "route_green_seoul"],
            "summary": "River-crossing movement constraints may delay support and rejoin windows.",
            "why_it_matters": "A support option that looks close on a map may be low value if crossings, weather, and congestion degrade movement.",
            "recommended_action": "Rank support as options, not automatic dispatch; keep human approval in the loop.",
            "evidence_refs": ["obs_weather_001", "obs_osint_001", "obs_civilian_exposure_cbd"],
            "features": {"mission_impact": 0.86, "urgency": 0.80, "confidence": 0.70, "trust": 0.70, "novelty": 0.66, "network_efficiency": 0.88},
            "raw_bytes": 180000,
            "semantic_bytes": 820,
        },
        {
            "event_id": "evt_opposing_axis_watch",
            "event_type": "OPPOSING_AXIS_WATCH",
            "severity": "high",
            "time": "2026-07-04T02:39:00Z",
            "location": {"lat": 37.570, "lon": 126.985, "area": "Synthetic north-to-CBD watch axis"},
            "entity_refs": ["opp_axis_a_north_cbd", "unit_anchor_2", "unit_relay_3"],
            "summary": "Synthetic opposing candidate axis A is the current watch priority, but it remains a probability branch rather than confirmed movement.",
            "why_it_matters": "Command staff need a visible route hypothesis without mistaking it for real-time tracking or verified intelligence.",
            "recommended_action": "Keep 12-2 on CBD watch, preserve 12-3 relay near the crossing aggregate, and transmit the axis summary only as a compact S-DOT watch card.",
            "evidence_refs": ["obs_opposing_axis_a", "obs_osint_001", "obs_civilian_exposure_cbd"],
            "features": {"mission_impact": 0.89, "urgency": 0.82, "confidence": 0.54, "trust": 0.64, "novelty": 0.74, "network_efficiency": 0.90},
            "raw_bytes": 135000,
            "semantic_bytes": 860,
        },
        {
            "event_id": "evt_civilian_exposure_cbd",
            "event_type": "CIVILIAN_EXPOSURE_DENSITY",
            "severity": "high",
            "time": "2026-07-04T02:20:00Z",
            "location": {"lat": 37.570, "lon": 126.985, "area": "Jongno/Jung CBD"},
            "entity_refs": ["bld_jongno_jung"],
            "summary": "CBD building density and civilian exposure are high around the central AOI.",
            "why_it_matters": "Urban ground support must preserve emergency access and avoid treating public civilian context as a targeting layer.",
            "recommended_action": "Use exposure as deconfliction and protection context only.",
            "evidence_refs": ["obs_civilian_exposure_cbd", "obs_osint_001"],
            "features": {"mission_impact": 0.88, "urgency": 0.78, "confidence": 0.76, "trust": 0.76, "novelty": 0.58, "network_efficiency": 0.84},
            "raw_bytes": 240000,
            "semantic_bytes": 760,
        },
        {
            "event_id": "evt_medical_capacity_north",
            "event_type": "MEDICAL_SUPPORT_CAPACITY",
            "severity": "high",
            "time": "2026-07-04T02:22:00Z",
            "location": {"lat": 37.579, "lon": 126.999, "area": "Central / north-east medical corridor"},
            "entity_refs": ["med_nmc", "med_snuh", "med_korea_anam"],
            "summary": "Public hospitals provide overlapping medical support context near the AOI.",
            "why_it_matters": "Protected civilian medical capacity is critical context for support planning, but not a military asset to command.",
            "recommended_action": "Show as protected support context and route Medic-2 staging through human approval.",
            "evidence_refs": ["obs_medical_capacity_north", "obs_support_route_medic"],
            "features": {"mission_impact": 0.90, "urgency": 0.84, "confidence": 0.80, "trust": 0.82, "novelty": 0.52, "network_efficiency": 0.86},
            "raw_bytes": 110000,
            "semantic_bytes": 780,
        },
        {
            "event_id": "evt_power_it_context",
            "event_type": "PUBLIC_IT_POWER_CONTEXT",
            "severity": "medium",
            "time": "2026-07-04T02:24:00Z",
            "location": {"lat": 37.552, "lon": 127.002, "area": "District aggregate continuity context"},
            "entity_refs": ["it_public_ops_seoul", "power_seoul_region"],
            "summary": "Public IT and power dependency are continuity context, not precise protected-facility data.",
            "why_it_matters": "Command staff need continuity awareness without exposing sensitive nodes or creating target-like maps.",
            "recommended_action": "Display district/regional aggregate only and keep exact sensitive facility coordinates out.",
            "evidence_refs": ["obs_public_it_power"],
            "features": {"mission_impact": 0.70, "urgency": 0.58, "confidence": 0.72, "trust": 0.78, "novelty": 0.54, "network_efficiency": 0.84},
            "raw_bytes": 96000,
            "semantic_bytes": 690,
        },
        {
            "event_id": "evt_unit_isolated_alpha1",
            "event_type": "UNIT_ISOLATED",
            "severity": "critical",
            "time": "2026-07-04T02:31:00Z",
            "location": {"lat": 37.532, "lon": 126.980, "area": "Synthetic central Seoul urban corridor"},
            "entity_refs": ["unit_alpha_1"],
            "summary": "Alpha-1 shifted to intermittent contact with local COP only partially visible to HQ.",
            "why_it_matters": "HQ cannot treat the last known position as live truth; the command board must switch to branch scenarios with uncertainty.",
            "recommended_action": "Send only intent and critical support packets; keep local event log queued for rejoin.",
            "evidence_refs": ["obs_unit_alpha1_readiness", "obs_network_001", "obs_intent_packet_001"],
            "features": {"mission_impact": 0.98, "urgency": 0.94, "confidence": 0.82, "trust": 0.80, "novelty": 0.86, "network_efficiency": 0.98},
            "raw_bytes": 74000,
            "semantic_bytes": 870,
        },
        {
            "event_id": "evt_support_request_medical_power",
            "event_type": "SUPPORT_REQUEST",
            "severity": "high",
            "time": "2026-07-04T02:36:00Z",
            "location": {"lat": 37.545, "lon": 126.965, "area": "Predicted Alpha-1 branch corridor"},
            "entity_refs": ["unit_alpha_1", "support_medic_2", "support_power_pack_a"],
            "summary": "Alpha-1 needs medical standby and power extension before the next contact window.",
            "why_it_matters": "Power depletion can break the local COP and S-DOT outbox before the unit physically moves out of the urban corridor.",
            "recommended_action": "Rank Medic-2 and Comms Relay-3 as support options; reserve contact window for readiness and route packets.",
            "evidence_refs": ["obs_unit_alpha1_readiness", "obs_support_route_medic"],
            "features": {"mission_impact": 0.90, "urgency": 0.88, "confidence": 0.76, "trust": 0.78, "novelty": 0.64, "network_efficiency": 0.92},
            "raw_bytes": 162000,
            "semantic_bytes": 930,
        },
        {
            "event_id": "evt_civil_bearer_candidate_han",
            "event_type": "CIVIL_BEARER_CANDIDATE",
            "severity": "medium",
            "time": "2026-07-04T02:34:00Z",
            "location": {"lat": 37.535, "lon": 126.970, "area": "Han River communications aggregate"},
            "entity_refs": ["civil_comms_han_river", "unit_alpha_1"],
            "summary": "Han River communications aggregate is a candidate emergency bearer but not automatically available.",
            "why_it_matters": "Dense Korean infrastructure may help continuity only if legal status, authentication, power, backhaul, security, and congestion conditions align.",
            "recommended_action": "Show as authorized opportunistic bearer candidate; do not assume access.",
            "evidence_refs": ["obs_civil_bearer_han", "obs_network_001"],
            "features": {"mission_impact": 0.74, "urgency": 0.64, "confidence": 0.68, "trust": 0.70, "novelty": 0.70, "network_efficiency": 0.90},
            "raw_bytes": 56000,
            "semantic_bytes": 760,
        },
        {
            "event_id": "evt_rejoin_window_predicted",
            "event_type": "REJOIN_WINDOW",
            "severity": "medium",
            "time": "2026-07-04T02:44:00Z",
            "location": {"lat": 37.545, "lon": 126.965, "area": "Predicted Alpha-1 branch corridor"},
            "entity_refs": ["unit_alpha_1", "link_seoul_alpha"],
            "summary": "Next 90-second contact window is predicted near the Alpha-1 branch corridor.",
            "why_it_matters": "The S-DOT queue must choose which messages to send before the window closes.",
            "recommended_action": "Transmit intent receipt, readiness snapshot, and support request before lower-priority evidence.",
            "evidence_refs": ["obs_network_001", "obs_unit_alpha1_readiness"],
            "features": {"mission_impact": 0.78, "urgency": 0.86, "confidence": 0.66, "trust": 0.70, "novelty": 0.58, "network_efficiency": 0.95},
            "raw_bytes": 45000,
            "semantic_bytes": 710,
        },
        {
            "event_id": "evt_priority_brief_urban_continuity",
            "event_type": "PRIORITY_BRIEF",
            "severity": "critical",
            "time": "2026-07-04T02:45:00Z",
            "location": {"lat": 37.555, "lon": 126.980, "area": "Central Seoul command view"},
            "entity_refs": ["unit_alpha_1", "civil_comms_han_river", "support_medic_2"],
            "summary": "Composite brief: Alpha-1 intermittent contact, route uncertainty, public medical context, and candidate bearer state converge.",
            "why_it_matters": "This is the highest-value command-continuity message when the link can only carry one alert card.",
            "recommended_action": "Send composite S-DOT card, queue raw map/building/context data, and prepare rejoin audit.",
            "evidence_refs": ["obs_unit_alpha1_readiness", "obs_network_001", "obs_support_route_medic", "obs_civilian_exposure_cbd", "obs_civil_bearer_han"],
            "features": {"mission_impact": 0.98, "urgency": 0.92, "confidence": 0.80, "trust": 0.80, "novelty": 0.86, "network_efficiency": 0.98},
            "raw_bytes": 2050000,
            "semantic_bytes": 1120,
        },
    ]

    mission_intent = {
        "mission_id": "urban_continuity_alpha",
        "display_name": "Urban Continuity Alpha",
        "commander_intent": "Maintain minimum local awareness, protect civilian access, preserve unit continuity, and prioritize medical readiness and communications restoration under DDIL conditions.",
        "priority_weights": {
            "civilian_protection": 0.24,
            "medical": 0.22,
            "communications": 0.22,
            "power": 0.16,
            "local_awareness": 0.16,
        },
        "constraints": [
            "No real unit data in demo",
            "Use Seoul public map/civil data as context only",
            "Treat civil infrastructure as candidate bearer, not guaranteed access",
            "Human approval required for support decisions",
        ],
        "valid_until": "2026-07-04T04:00:00Z",
    }

    operation_objective = {
        "operation_id": "op_seoul_shield_01",
        "display_name": "서울 도심 임무지속 방호",
        "primary_objective": "12-1의 로컬 상황도를 유지하고, 민간 응급 접근로를 보호하며, 상대 후보 기동축을 감시하면서 90초 재연결 창에 핵심 S-DOT 패킷을 동기화한다.",
        "end_state": "고립·간헐 접속 상황에서도 지휘 의도, 최소 상황도, 자원 상태, 예측 불확실성, 재연결 감사가 유지된다.",
        "current_phase": "Phase 2 · 간헐 접속/도심 이동 제약",
        "decision_focus": [
            "후보축 A 감시 우선순위 유지",
            "12-1 전력·의료 readiness 유지",
            "한강 통신 aggregate 승인 가능성 확인",
            "Medic-2와 Comms Relay-3 지원 옵션 보존",
        ],
        "protected_priorities": ["민간 응급 접근로", "공공 의료 거점", "불확실한 정보의 오판 방지"],
        "valid_until": "2026-07-04T04:00:00Z",
    }

    adversary_assessment = {
        "label": "상대 기동 후보축(합성)",
        "safety_note": "Demo-only synthetic opposing movement assumptions; not real intelligence, operational guidance, or a targeting layer.",
        "routes": [
            {
                "route_id": "opp_axis_a_north_cbd",
                "display_name": "후보축 A · 북부→CBD",
                "axis_code": "A",
                "likelihood": 0.56,
                "confidence": 0.54,
                "status": "watch",
                "points": [[37.650, 126.990], [37.610, 126.995], [37.570, 126.985], [37.545, 126.965]],
                "why": "공개 도심 혼잡 맥락과 통신 저하가 겹쳐 감시 우선순위가 가장 높음.",
            },
            {
                "route_id": "opp_axis_b_west_crossing",
                "display_name": "후보축 B · 서부 도하",
                "axis_code": "B",
                "likelihood": 0.29,
                "confidence": 0.46,
                "status": "secondary",
                "points": [[37.560, 126.815], [37.540, 126.930], [37.535, 126.970]],
                "why": "한강 도하/통신 aggregate와 연결되지만 기상·혼잡 때문에 불확실성이 큼.",
            },
            {
                "route_id": "opp_axis_c_east_medical",
                "display_name": "후보축 C · 동부 의료회랑 우회",
                "axis_code": "C",
                "likelihood": 0.15,
                "confidence": 0.38,
                "status": "low_confidence",
                "points": [[37.612, 127.098], [37.579, 126.999], [37.552, 127.002]],
                "why": "공공 의료/전력 aggregate 주변 경로라 보호 맥락상 모니터링만 유지.",
            },
        ],
    }

    unit_nodes = [
        {
            "unit_id": "unit_alpha_1",
            "unit_code": "12-1",
            "display_name": "12-1 기동팀",
            "unit_type": "synthetic_urban_team",
            "comm_state": "intermittent",
            "c2_mode": "delegated",
            "map_symbol": {"shape": "friendly_unit", "color_state": "amber", "pulse": "intermittent"},
            "last_confirmed": {"time": "2026-07-04T02:31:00Z", "lat": 37.532, "lon": 126.980, "source": "obs_unit_alpha1_readiness"},
            "predicted_state": {
                "time": "2026-07-04T02:44:00Z",
                "lat": 37.545,
                "lon": 126.965,
                "confidence": 0.62,
                "uncertainty_km": 2.4,
                "likely_phase": "Phase 2: hold local COP and await contact window",
                "assumptions": ["follows intent corridor", "ground movement constrained by crossings", "power saving mode active"],
            },
            "branch_scenarios": [
                {"branch": "main_route_continue", "label": "주경로 지속", "probability": 0.52, "confidence_delta_per_10m": -0.06},
                {"branch": "hold_local_cop", "label": "은폐/대기하며 로컬 상황도 유지", "probability": 0.31, "confidence_delta_per_10m": -0.04},
                {"branch": "detour_to_support_node", "label": "지원 노드 우회", "probability": 0.17, "confidence_delta_per_10m": -0.08},
            ],
            "readiness": {"power_pct": 42, "medical_status": "yellow", "local_cop_cache": "valid_but_aging", "sdot_outbox": 6, "critical_supplies_hours": 7.5},
        },
        {
            "unit_id": "unit_anchor_2",
            "unit_code": "12-2",
            "display_name": "12-2 감시팀",
            "unit_type": "synthetic_support_observer",
            "comm_state": "degraded",
            "c2_mode": "collaborative",
            "map_symbol": {"shape": "friendly_unit", "color_state": "blue", "pulse": "slow"},
            "last_confirmed": {"time": "2026-07-04T02:33:00Z", "lat": 37.570, "lon": 126.985, "source": "mock_unit_state"},
            "predicted_state": {"time": "2026-07-04T02:44:00Z", "lat": 37.566, "lon": 126.999, "confidence": 0.77, "uncertainty_km": 1.2, "likely_phase": "relay watch"},
            "branch_scenarios": [
                {"branch": "maintain_relay_watch", "label": "중계 감시 유지", "probability": 0.68, "confidence_delta_per_10m": -0.03},
                {"branch": "shift_to_medical_corridor", "label": "의료 회랑 방향 지원", "probability": 0.22, "confidence_delta_per_10m": -0.05},
                {"branch": "fall_back_power_save", "label": "전력 절약 대기", "probability": 0.10, "confidence_delta_per_10m": -0.04},
            ],
            "readiness": {"power_pct": 68, "medical_status": "green", "local_cop_cache": "fresh", "sdot_outbox": 2, "critical_supplies_hours": 13.0},
        },
        {
            "unit_id": "unit_relay_3",
            "unit_code": "12-3",
            "display_name": "12-3 중계팀",
            "unit_type": "synthetic_mobile_relay_reserve",
            "comm_state": "connected",
            "c2_mode": "collaborative",
            "map_symbol": {"shape": "friendly_unit", "color_state": "green", "pulse": "none"},
            "last_confirmed": {"time": "2026-07-04T02:35:00Z", "lat": 37.540, "lon": 126.930, "source": "mock_unit_state"},
            "predicted_state": {"time": "2026-07-04T02:44:00Z", "lat": 37.535, "lon": 126.970, "confidence": 0.81, "uncertainty_km": 0.9, "likely_phase": "hold relay option near authorized bearer candidate"},
            "branch_scenarios": [
                {"branch": "hold_relay_candidate", "label": "중계 후보지 유지", "probability": 0.61, "confidence_delta_per_10m": -0.03},
                {"branch": "shift_to_alpha_support", "label": "12-1 지원축 이동", "probability": 0.27, "confidence_delta_per_10m": -0.05},
                {"branch": "fallback_west_staging", "label": "서부 대기점 복귀", "probability": 0.12, "confidence_delta_per_10m": -0.04},
            ],
            "readiness": {"power_pct": 79, "medical_status": "green", "local_cop_cache": "fresh", "sdot_outbox": 1, "critical_supplies_hours": 16.0},
        },
    ]

    civil_comms_assets = [
        {
            "asset_id": "civil_comms_han_river",
            "display_name": "한강 통신 aggregate 후보",
            "bearer_type": "authorized LTE/PS-LTE/LTE-M candidate",
            "owner_type": "civil_public_infra_aggregate",
            "lat": 37.535,
            "lon": 126.970,
            "legal_status": "emergency_order_required",
            "power_state": "unknown_backup_power",
            "backhaul_state": "degraded_or_unknown",
            "auth_required": True,
            "priority_capable": True,
            "estimated_bandwidth_kbps": 256,
            "confidence": 0.62,
        },
        {
            "asset_id": "civil_comms_north_ridge",
            "display_name": "북측 능선 무선 coverage aggregate",
            "bearer_type": "coarse radio coverage candidate",
            "owner_type": "civil_public_infra_aggregate",
            "lat": 37.650,
            "lon": 126.990,
            "legal_status": "authority_required",
            "power_state": "aggregate_unknown",
            "backhaul_state": "aggregate_unknown",
            "auth_required": True,
            "priority_capable": False,
            "estimated_bandwidth_kbps": 128,
            "confidence": 0.55,
        },
    ]

    support_options = [
        {
            "support_id": "support_medic_2",
            "display_name": "Medic-2 지원 옵션",
            "support_type": "medical_standby",
            "lat": 37.5672,
            "lon": 127.0057,
            "route_name": "Route Blue",
            "eta_minutes": 28,
            "route_risk": 0.36,
            "resource_cost": 0.38,
            "support_score": 0.84,
            "assigned_to": "unit_alpha_1",
            "supports_objective": "12-1 의료 standby와 민간 응급 접근로 보호",
            "why_ranked": "Best protected medical-context alignment with acceptable route risk and no additional comms authorization dependency.",
        },
        {
            "support_id": "support_comms_relay_3",
            "display_name": "Comms Relay-3",
            "support_type": "mobile_relay",
            "lat": 37.535,
            "lon": 126.970,
            "route_name": "Route Green",
            "eta_minutes": 22,
            "route_risk": 0.44,
            "resource_cost": 0.48,
            "support_score": 0.79,
            "assigned_to": "unit_relay_3",
            "supports_objective": "한강 통신 aggregate 후보 검증과 재연결 창 확보",
            "why_ranked": "Fastest communications restoration option, but authorization and backhaul uncertainty reduce confidence.",
        },
        {
            "support_id": "support_power_pack_a",
            "display_name": "Power Pack A",
            "support_type": "power_extension",
            "lat": 37.552,
            "lon": 127.002,
            "route_name": "Route Amber",
            "eta_minutes": 35,
            "route_risk": 0.31,
            "resource_cost": 0.32,
            "support_score": 0.72,
            "assigned_to": "unit_alpha_1",
            "supports_objective": "12-1 로컬 COP 캐시와 S-DOT outbox 생존시간 연장",
            "why_ranked": "Useful for endurance, but less urgent than medical standby and comms relay.",
        },
    ]

    pace_bearer_ladder = [
        {"pace": "P", "label": "전술 IP망", "bearer_type": "tactical_ip", "role": "정상 연결 시 COP/근거 동기화", "availability_by_mode": {"full_sync": "active", "delta_sync": "active", "semantic_summary": "degraded", "store_forward": "degraded", "local_only": "down"}, "risk_note": "실제 전술망 세부는 데모에 포함하지 않음."},
        {"pace": "A", "label": "위성/장거리 백업", "bearer_type": "satellite_or_longhaul_backup", "role": "저속 명령 의도·readiness packet 전달", "availability_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "active", "store_forward": "degraded", "local_only": "down"}, "risk_note": "전력·가시성·혼잡·교란 조건에 따라 품질 변동."},
        {"pace": "C", "label": "승인형 민간/공공 bearer", "bearer_type": "authorized_opportunistic_bearer", "role": "PS-LTE/LTE-M/상용망/유선 백홀 후보", "availability_by_mode": {"full_sync": "standby", "delta_sync": "candidate", "semantic_summary": "candidate", "store_forward": "candidate", "local_only": "unavailable_without_authority"}, "risk_note": "법적 권한, 인증, 전력, 백홀, 보안, 감청 위험 검토 필요."},
        {"pace": "E", "label": "메시/스토어-포워드", "bearer_type": "mesh_store_forward_or_physical_sync", "role": "접속창 전까지 로컬 저장 후 재연결 감사", "availability_by_mode": {"full_sync": "standby", "delta_sync": "standby", "semantic_summary": "standby", "store_forward": "active", "local_only": "local_only"}, "risk_note": "실시간 지휘가 아니라 임무 지속성과 사후 동기화에 초점."},
    ]

    semantic_events = []
    evidence_bundles = []
    for spec in event_specs:
        priority = score(spec["features"])
        semantic_events.append({**{k: v for k, v in spec.items() if k != "features"}, "priority": priority, "priority_features": spec["features"], "mock_notice": "Synthetic event over a public Seoul map for safe hackathon demo."})
        refs = set(spec["evidence_refs"])
        evidence_bundles.append({
            "bundle_id": "eb_" + spec["event_id"].replace("evt_", ""),
            "event_id": spec["event_id"],
            "modality_slots": {
                "network": "available" if "obs_network_001" in refs else "not_used",
                "weather": "available" if "obs_weather_001" in refs else "not_used",
                "osint": "available" if "obs_osint_001" in refs else "not_used",
                "unit_status": "available" if "obs_unit_alpha1_readiness" in refs else "not_used",
                "civil_infra": "available" if any(ref.startswith("obs_civilian") or ref.startswith("obs_medical") or ref.startswith("obs_public") for ref in refs) else "not_used",
                "operator_report": "available" if "obs_operator_lowtrust_001" in refs else "not_used",
                "threat_assessment": "available" if "obs_opposing_axis_a" in refs else "not_used",
            },
            "availability_mask": {ref: True for ref in spec["evidence_refs"]},
            "evidence_refs": spec["evidence_refs"],
            "confidence": spec["features"]["confidence"],
            "trust_score": spec["features"]["trust"],
            "freshness_seconds": 300 if spec["severity"] in {"high", "critical"} else 1800,
            "review_status": "needs_analyst_review" if spec["severity"] in {"high", "critical"} else "context_only",
            "source_rationale": "Evidence bundle keeps public context, synthetic unit state, and uncertainty visible instead of flattening them into a single truth value.",
        })

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
            packets.append({
                "packet_id": "pkt_" + mode + "_" + event["event_id"].replace("evt_", ""),
                "event_id": event["event_id"],
                "network_mode": mode,
                "payload_tier": "full_event" if mode == "full_sync" else "event_delta" if mode == "delta_sync" else "alert_card" if mode == "semantic_summary" else "critical_summary" if mode == "store_forward" else "local_cache",
                "decision": decision,
                "bytes_raw_estimate": event["raw_bytes"],
                "bytes_semantic": event["semantic_bytes"] if decision == "send" else 0,
            })
        raw_total = sum(event["raw_bytes"] for event in semantic_events)
        routing_results[mode] = {
            "mode": mode,
            "network": {k: v for k, v in config.items() if k not in {"send_threshold", "defer_threshold"}},
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

    sdot_messages = [
        {"message_id": "sdot_001", "family": "IntentUpdate", "from": "지휘부", "to": "12-1", "event_id": "evt_unit_isolated_alpha1", "payload_tier": "T2_SEMANTIC", "priority": 0.94, "raw_bytes": 18000, "semantic_bytes": 520, "decision_value": "Keeps local decisions aligned with mission intent while disconnected."},
        {"message_id": "sdot_002", "family": "ReadinessSnapshot", "from": "12-1", "to": "지휘부", "event_id": "evt_support_request_medical_power", "payload_tier": "T3_PRIORITY_CARD", "priority": 0.89, "raw_bytes": 74000, "semantic_bytes": 610, "decision_value": "Changes support allocation because power and medical status are degrading."},
        {"message_id": "sdot_003", "family": "SupportRequest", "from": "12-1", "to": "지휘부", "event_id": "evt_support_request_medical_power", "payload_tier": "T3_PRIORITY_CARD", "priority": 0.87, "raw_bytes": 88000, "semantic_bytes": 690, "decision_value": "Triggers ranking of Medic-2, Comms Relay-3, and Power Pack A."},
        {"message_id": "sdot_004", "family": "NetworkStateUpdate", "from": "인프라 레이어", "to": "지휘부", "event_id": "evt_civil_bearer_candidate_han", "payload_tier": "T2_SEMANTIC", "priority": 0.70, "raw_bytes": 56000, "semantic_bytes": 540, "decision_value": "Identifies Han River aggregate as possible but authorization-gated bearer."},
        {"message_id": "sdot_005", "family": "RejoinWindow", "from": "지휘부", "to": "12-1", "event_id": "evt_rejoin_window_predicted", "payload_tier": "T3_PRIORITY_CARD", "priority": 0.76, "raw_bytes": 45000, "semantic_bytes": 490, "decision_value": "Determines which queued bundles are sent during a 90-second contact window."},
    ]

    rejoin_audit = {
        "audit_id": "audit_rejoin_alpha_1_preview",
        "status": "pending_contact_window",
        "prediction_before_rejoin": {
            "lat": unit_nodes[0]["predicted_state"]["lat"],
            "lon": unit_nodes[0]["predicted_state"]["lon"],
            "confidence": unit_nodes[0]["predicted_state"]["confidence"],
            "uncertainty_km": unit_nodes[0]["predicted_state"]["uncertainty_km"],
        },
        "expected_sync_order": ["sdot_001", "sdot_002", "sdot_003", "sdot_005", "sdot_004"],
        "open_questions": [
            "Did Alpha-1 remain inside the predicted branch corridor?",
            "Did power saving preserve local COP until contact?",
            "Was the Han River aggregate legally/technically available as a bearer?",
        ],
    }

    return {
        "metadata": {
            "dataset_id": "s_dot_seoul_ground_mission_continuity_mock_v0_5",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario_name": "S-DOT mission continuity in Seoul urban ground DDIL scenario",
            "display_name_ko": "S-DOT 서울 지상 임무지속 COP",
            "sdot_definition": "S-DOT = Semantic Data On Tactical-network. This is a hackathon concept label, not an existing tactical-link standard.",
            "mock_dataset": True,
            "safety_note": "Public Seoul map and civil context plus synthetic unit/resource/network data. No real unit location, force disposition, protected-facility coordinates, personal data, or operational claim.",
            "design_doc": "06_prototype/docs/s_dot_mission_continuity_implementation_20260704.md",
            "schema_doc": "05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md",
            "plan_doc": "02_problem_statements/hypotheses/s_dot_mission_continuity_cop_plan_20260704.md",
        },
        "scenario": {
            "aoi": {
                "name": "서울 도심 지상 AOI",
                "bounds": {"lat_min": 37.43, "lat_max": 37.69, "lon_min": 126.78, "lon_max": 127.16},
                "center": {"lat": 37.5665, "lon": 126.9780},
            },
            "time_window": {"start": "2026-07-04T01:30:00Z", "end": "2026-07-04T03:00:00Z"},
            "narrative": "12-1 becomes intermittently connected in a Seoul urban ground scenario while command staff monitor synthetic opposing route branches, public civil context, support resources, and candidate bearers through S-DOT semantic packets.",
        },
        "source_catalog": source_catalog,
        "operation_objective": operation_objective,
        "adversary_assessment": adversary_assessment,
        "mission_intent": mission_intent,
        "unit_nodes": unit_nodes,
        "pace_bearer_ladder": pace_bearer_ladder,
        "civil_comms_assets": civil_comms_assets,
        "korea_civil_infra_context": korea_civil_infra_context,
        "support_options": support_options,
        "sdot_messages": sdot_messages,
        "rejoin_audit": rejoin_audit,
        "vessels": [],
        "tracks": [],
        "urban_routes": [
            {"route_id": "route_blue_seoul", "label": "Route Blue", "points": [[37.5672, 127.0057], [37.555, 126.990], [37.545, 126.965]], "risk": 0.36},
            {"route_id": "route_green_seoul", "label": "Route Green", "points": [[37.535, 126.970], [37.540, 126.965], [37.545, 126.965]], "risk": 0.44},
            {"route_id": "route_amber_seoul", "label": "Route Amber", "points": [[37.552, 127.002], [37.555, 126.990], [37.545, 126.965]], "risk": 0.31},
        ],
        "observations": observations,
        "evidence_bundles": evidence_bundles,
        "semantic_events": semantic_events,
        "network_modes": NETWORK_MODES,
        "routing_results": routing_results,
        "briefing": {
            "headline": "S-DOT should preserve intent, readiness, support options, uncertainty, and rejoin audit when raw map/context data cannot move.",
            "grounded_claims": [
                {"claim": "Alpha-1 is intermittently connected and should be shown as predicted branch scenarios, not live tracking.", "evidence_refs": ["obs_unit_alpha1_readiness", "obs_network_001"]},
                {"claim": "Mission intent prioritizes civilian protection, medical readiness, local awareness, and comms restoration.", "evidence_refs": ["obs_intent_packet_001"]},
                {"claim": "Opposing movement is shown only as synthetic probability branches, with candidate axis A at the highest watch priority.", "evidence_refs": ["obs_opposing_axis_a", "obs_osint_001"]},
                {"claim": "Civil communication aggregates are candidate bearers only if authorization, authentication, power, backhaul, congestion, and security align.", "evidence_refs": ["obs_civil_bearer_han"]},
                {"claim": "Medic-2 is the highest-ranked support option in the synthetic Seoul scenario.", "evidence_refs": ["obs_support_route_medic", "obs_medical_capacity_north"]},
                {"claim": "Dense CBD exposure is deconfliction/protection context, not a targeting or force-disposition layer.", "evidence_refs": ["obs_civilian_exposure_cbd"]},
                {"claim": "Public IT/power dependencies remain aggregate-only continuity context.", "evidence_refs": ["obs_public_it_power"]},
                {"claim": "Weather and network degradation reduce raw-feed confirmation.", "evidence_refs": ["obs_weather_001", "obs_network_001"]},
            ],
            "operator_summary": "Send intent receipt, readiness snapshot, and support request before lower-priority context; queue raw map/building/context data for later sync; keep all unit/resource data synthetic in public demos.",
        },
    }


def write_readme(dataset: dict) -> str:
    return f"""# S-DOT Seoul Ground Mission Continuity COP Mock Dataset

- Dataset ID: `{dataset['metadata']['dataset_id']}`
- Generated: {dataset['metadata']['generated_at']}
- Scenario: {dataset['scenario']['narrative']}

## Safety

The base map and civil infrastructure context are public/open-source style Seoul context. Unit state, support resources, tactical network values, readiness, and allocation decisions are synthetic. The data is meant to demonstrate S-DOT architecture and routing behavior, not to disclose real force disposition, real readiness, protected-facility coordinates, or operational claims.

## Why This Dataset Exists

The live API collection workstream may produce real snapshots later. Until then, this dataset keeps the demo runnable and reproducible.

Each mock source states which real source type it can be replaced by:

- unit/readiness state -> redacted exercise telemetry or training data only
- civil/public comms assets -> KCA public radio-station data, Spectrum Map, PS-LTE/LTE-M/LTE-R references, or telco-provided emergency inventory
- support resources -> public facility context plus synthetic military support resources
- Seoul map/buildings -> OpenStreetMap building footprints, VWorld/MOLIT public map context
- public medical context -> HIRA/NMC public facility APIs
- aggregate public IT/power context -> MOIS/KPX aggregate public datasets
- weather hazard -> KMA APIHub, Open-Meteo, data.go.kr weather
- OSINT incident -> GDELT, official advisories, public emergency notices
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

This shows the T3 point: the project is not just a COP. It is mission-aware semantic transmission under constrained links.

## S-DOT Additions

- `mission_intent`: structured commander/staff intent and priority weights
- `unit_nodes`: synthetic isolated/intermittent units with confirmed vs predicted state
- `unit_nodes[].branch_scenarios`: probabilistic branch scenarios instead of exact tracking claims
- `pace_bearer_ladder`: Network/Bearer/PACE state that drives payload priority and C2 mode
- `civil_comms_assets`: candidate bearers with legal, power, backhaul, auth, and priority status
- `korea_civil_infra_context`: safe Korea civil infrastructure COP layer, imported only as protected/support context
- `urban_routes`: synthetic support routes over public Seoul map context
- `support_options`: ranked medical, power, and comms support options
- `sdot_messages`: semantic command/status/support packets with raw-vs-semantic bytes
- `rejoin_audit`: expected sync order and prediction-review questions
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
        "unit_nodes": len(dataset["unit_nodes"]),
        "support_options": len(dataset["support_options"]),
        "sdot_messages": len(dataset["sdot_messages"]),
        "routing_modes": list(dataset["routing_results"].keys()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

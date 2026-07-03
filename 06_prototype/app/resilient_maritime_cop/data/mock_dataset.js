window.__D4D_MOCK_DATASET = {
  "metadata": {
    "dataset_id": "resilient_maritime_cop_mock_v0_1",
    "generated_at": "2026-07-03T15:22:46.749610+00:00",
    "scenario_name": "AIS silence and SAR mismatch under degraded ship-to-shore link",
    "mock_dataset": true,
    "safety_note": "Synthetic, redacted-style demo data. No real vessel identity, personal data, or operational claim.",
    "design_doc": "06_prototype/docs/resilient_maritime_cop_technical_design.md",
    "schema_doc": "05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md"
  },
  "scenario": {
    "aoi": {
      "name": "Yellow Sea training AOI",
      "bounds": {
        "lat_min": 36.95,
        "lat_max": 37.65,
        "lon_min": 125.05,
        "lon_max": 126.05
      },
      "center": {
        "lat": 37.32,
        "lon": 125.65
      }
    },
    "time_window": {
      "start": "2026-07-04T01:30:00Z",
      "end": "2026-07-04T03:00:00Z"
    },
    "narrative": "A cooperative AIS track goes stale, an independent SAR-like detection appears nearby, weather reduces confirmation options, and the network drops into semantic-summary mode."
  },
  "source_catalog": [
    {
      "source_id": "mock_ais_tracks",
      "label": "Synthetic AIS-like vessel tracks",
      "real_replacement": [
        "data.go.kr maritime AIS",
        "Global Fishing Watch",
        "NOAA MarineCadastre AIS"
      ],
      "source_rationale": "AIS is the cooperative maritime position-reporting layer. The mock fields mirror common AIS concepts: vessel id, time, lat/lon, speed, course, and freshness.",
      "mock_notice": "Synthetic records; no real MMSI or operator data."
    },
    {
      "source_id": "mock_sar_detections",
      "label": "Synthetic SAR-like detection",
      "real_replacement": [
        "Copernicus Sentinel-1",
        "xView3",
        "Global Fishing Watch SAR detections"
      ],
      "source_rationale": "SAR provides independent physical observation when AIS is missing, spoofed, or delayed. The mock record carries scene id, detection point, size hint, and match status.",
      "mock_notice": "Synthetic detection modeled after open SAR ship-detection workflows."
    },
    {
      "source_id": "mock_weather_hazard",
      "label": "Synthetic maritime weather warning",
      "real_replacement": [
        "KMA APIHub",
        "Copernicus Marine",
        "NOAA/NCEP"
      ],
      "source_rationale": "Weather affects vessel risk, sensor reliability, and operator urgency. The mock warning is represented as a time-bounded area hazard.",
      "mock_notice": "Synthetic warning; not an official forecast."
    },
    {
      "source_id": "mock_osint_incident",
      "label": "Synthetic OSINT incident",
      "real_replacement": [
        "GDELT",
        "official maritime advisories",
        "ReliefWeb/HDX where relevant"
      ],
      "source_rationale": "OSINT gives cited narrative context, but must not be treated as sensor truth. The mock record is an advisory-style citation stub.",
      "mock_notice": "Synthetic article/advisory metadata; URLs are not operational claims."
    },
    {
      "source_id": "mock_network_state",
      "label": "Synthetic DDIL network states",
      "real_replacement": [
        "Cloudflare Radar",
        "Ookla Open Data",
        "RIPE Atlas",
        "Linux tc netem"
      ],
      "source_rationale": "T3 differentiation comes from showing what survives under bandwidth, latency, packet loss, and link outage.",
      "mock_notice": "Synthetic network profile designed for repeatable demo behavior."
    },
    {
      "source_id": "mock_operator_report",
      "label": "Synthetic operator report",
      "real_replacement": [
        "watchstander report",
        "field report",
        "radio/voice transcript after redaction"
      ],
      "source_rationale": "Human reports are valuable but can conflict with sensor evidence, so the COP must model source trust and contradiction.",
      "mock_notice": "Synthetic report with no real person or unit information."
    }
  ],
  "vessels": [
    {
      "vessel_id": "vessel_haneul_77",
      "display_name": "Haneul-77",
      "masked_identifier": "MMSI-***-077",
      "type": "cargo",
      "identity_confidence": 0.81,
      "route_role": "northbound commercial track crossing monitored corridor"
    },
    {
      "vessel_id": "vessel_blue_maru_12",
      "display_name": "Blue Maru-12",
      "masked_identifier": "MMSI-***-112",
      "type": "fishing",
      "identity_confidence": 0.73,
      "route_role": "routine fishing track outside the warning corridor"
    },
    {
      "vessel_id": "vessel_daehan_rescue_3",
      "display_name": "Daehan Rescue-3",
      "masked_identifier": "CALLSIGN-***-R3",
      "type": "patrol_support",
      "identity_confidence": 0.94,
      "route_role": "friendly support asset with reliable reporting"
    }
  ],
  "tracks": [
    {
      "track_id": "trk_h77_001",
      "vessel_id": "vessel_haneul_77",
      "time": "2026-07-04T01:40:00Z",
      "lat": 37.18,
      "lon": 125.44,
      "sog": 13.2,
      "cog": 42,
      "source": "mock_ais_tracks"
    },
    {
      "track_id": "trk_h77_002",
      "vessel_id": "vessel_haneul_77",
      "time": "2026-07-04T01:55:00Z",
      "lat": 37.25,
      "lon": 125.52,
      "sog": 13.5,
      "cog": 44,
      "source": "mock_ais_tracks"
    },
    {
      "track_id": "trk_h77_003",
      "vessel_id": "vessel_haneul_77",
      "time": "2026-07-04T02:05:00Z",
      "lat": 37.3,
      "lon": 125.58,
      "sog": 13.1,
      "cog": 43,
      "source": "mock_ais_tracks",
      "last_cooperative_point": true
    },
    {
      "track_id": "trk_bm12_001",
      "vessel_id": "vessel_blue_maru_12",
      "time": "2026-07-04T02:00:00Z",
      "lat": 37.06,
      "lon": 125.82,
      "sog": 7.4,
      "cog": 310,
      "source": "mock_ais_tracks"
    },
    {
      "track_id": "trk_dr3_001",
      "vessel_id": "vessel_daehan_rescue_3",
      "time": "2026-07-04T02:10:00Z",
      "lat": 37.5,
      "lon": 125.43,
      "sog": 18.0,
      "cog": 110,
      "source": "mock_ais_tracks"
    }
  ],
  "observations": [
    {
      "observation_id": "obs_ais_gap_h77",
      "source_id": "mock_ais_tracks",
      "sensor_type": "AIS",
      "time": "2026-07-04T02:25:00Z",
      "location": {
        "lat": 37.36,
        "lon": 125.66
      },
      "claim": "No cooperative AIS update received for Haneul-77 after 02:05Z.",
      "raw_ref": "mock://ais/haneul_77#last_point=trk_h77_003",
      "raw_bytes": 420000
    },
    {
      "observation_id": "obs_sar_unmatched_001",
      "source_id": "mock_sar_detections",
      "sensor_type": "SAR",
      "time": "2026-07-04T02:24:00Z",
      "location": {
        "lat": 37.41,
        "lon": 125.72
      },
      "claim": "Vessel-sized object detected 8.1 km from predicted Haneul-77 position; no AIS match inside gate.",
      "raw_ref": "mock://sar/scene_20260704_0224#det=1",
      "raw_bytes": 1480000
    },
    {
      "observation_id": "obs_weather_001",
      "source_id": "mock_weather_hazard",
      "sensor_type": "WEATHER",
      "time": "2026-07-04T02:10:00Z",
      "location": {
        "lat": 37.32,
        "lon": 125.6
      },
      "claim": "Visibility reduced and wave hazard elevated across the corridor.",
      "raw_ref": "mock://weather/kma_style_warning#yellow_sea_corridor",
      "raw_bytes": 65000
    },
    {
      "observation_id": "obs_osint_001",
      "source_id": "mock_osint_incident",
      "sensor_type": "OSINT",
      "time": "2026-07-04T01:35:00Z",
      "location": {
        "lat": 37.55,
        "lon": 125.95
      },
      "claim": "Open-source advisory reports temporary maritime inspection activity near the northern corridor.",
      "raw_ref": "mock://osint/gdelt_style/advisory_20260704_0135",
      "raw_bytes": 38000
    },
    {
      "observation_id": "obs_network_001",
      "source_id": "mock_network_state",
      "sensor_type": "NETWORK",
      "time": "2026-07-04T02:18:00Z",
      "location": {
        "lat": 37.38,
        "lon": 125.63
      },
      "claim": "Ship-to-shore relay bandwidth dropped below semantic-summary threshold.",
      "raw_ref": "mock://network/link_alpha#state=semantic_summary",
      "raw_bytes": 21000
    },
    {
      "observation_id": "obs_operator_lowtrust_001",
      "source_id": "mock_operator_report",
      "sensor_type": "HUMAN_REPORT",
      "time": "2026-07-04T02:28:00Z",
      "location": {
        "lat": 37.02,
        "lon": 125.1
      },
      "claim": "Unconfirmed voice report places Haneul-77 south of the corridor, conflicting with SAR/time-distance feasibility.",
      "raw_ref": "mock://operator/report_20260704_0228",
      "raw_bytes": 12000
    }
  ],
  "evidence_bundles": [
    {
      "bundle_id": "eb_network_degraded_001",
      "event_id": "evt_network_degraded_001",
      "modality_slots": {
        "ais": "not_used",
        "sar": "not_used",
        "weather": "not_used",
        "osint": "not_used",
        "network": "available",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": false,
        "sar": false,
        "weather": false,
        "osint": false,
        "network": true,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_network_001"
      ],
      "confidence": 0.78,
      "trust_score": 0.82,
      "freshness_seconds": 300,
      "review_status": "needs_analyst_review",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_weather_hazard_001",
      "event_id": "evt_weather_hazard_001",
      "modality_slots": {
        "ais": "not_used",
        "sar": "not_used",
        "weather": "available",
        "osint": "not_used",
        "network": "not_used",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": false,
        "sar": false,
        "weather": true,
        "osint": false,
        "network": false,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_weather_001"
      ],
      "confidence": 0.78,
      "trust_score": 0.83,
      "freshness_seconds": 1800,
      "review_status": "context_only",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_ais_gap_h77",
      "event_id": "evt_ais_gap_h77",
      "modality_slots": {
        "ais": "available",
        "sar": "not_used",
        "weather": "not_used",
        "osint": "not_used",
        "network": "available",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": true,
        "sar": false,
        "weather": false,
        "osint": false,
        "network": true,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_ais_gap_h77",
        "obs_network_001"
      ],
      "confidence": 0.76,
      "trust_score": 0.72,
      "freshness_seconds": 300,
      "review_status": "needs_analyst_review",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_sar_without_ais_001",
      "event_id": "evt_sar_without_ais_001",
      "modality_slots": {
        "ais": "available",
        "sar": "available",
        "weather": "available",
        "osint": "not_used",
        "network": "not_used",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": true,
        "sar": true,
        "weather": true,
        "osint": false,
        "network": false,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_sar_unmatched_001",
        "obs_ais_gap_h77",
        "obs_weather_001"
      ],
      "confidence": 0.79,
      "trust_score": 0.76,
      "freshness_seconds": 300,
      "review_status": "needs_analyst_review",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_low_trust_report_001",
      "event_id": "evt_low_trust_report_001",
      "modality_slots": {
        "ais": "not_used",
        "sar": "available",
        "weather": "not_used",
        "osint": "not_used",
        "network": "not_used",
        "operator_report": "available"
      },
      "availability_mask": {
        "ais": false,
        "sar": true,
        "weather": false,
        "osint": false,
        "network": false,
        "operator_report": true
      },
      "evidence_refs": [
        "obs_operator_lowtrust_001",
        "obs_sar_unmatched_001"
      ],
      "confidence": 0.42,
      "trust_score": 0.35,
      "freshness_seconds": 1800,
      "review_status": "context_only",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_osint_context_001",
      "event_id": "evt_osint_context_001",
      "modality_slots": {
        "ais": "not_used",
        "sar": "not_used",
        "weather": "not_used",
        "osint": "available",
        "network": "not_used",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": false,
        "sar": false,
        "weather": false,
        "osint": true,
        "network": false,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_osint_001"
      ],
      "confidence": 0.54,
      "trust_score": 0.52,
      "freshness_seconds": 1800,
      "review_status": "context_only",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    },
    {
      "bundle_id": "eb_composite_dark_vessel_review_001",
      "event_id": "evt_composite_dark_vessel_review_001",
      "modality_slots": {
        "ais": "available",
        "sar": "available",
        "weather": "available",
        "osint": "available",
        "network": "available",
        "operator_report": "not_used"
      },
      "availability_mask": {
        "ais": true,
        "sar": true,
        "weather": true,
        "osint": true,
        "network": true,
        "operator_report": false
      },
      "evidence_refs": [
        "obs_ais_gap_h77",
        "obs_sar_unmatched_001",
        "obs_weather_001",
        "obs_network_001",
        "obs_osint_001"
      ],
      "confidence": 0.8,
      "trust_score": 0.78,
      "freshness_seconds": 300,
      "review_status": "needs_analyst_review",
      "source_rationale": "Evidence bundle keeps source disagreements visible instead of overwriting them with a single truth value."
    }
  ],
  "semantic_events": [
    {
      "event_id": "evt_network_degraded_001",
      "event_type": "NETWORK_DEGRADED",
      "severity": "high",
      "time": "2026-07-04T02:18:00Z",
      "location": {
        "lat": 37.38,
        "lon": 125.63,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "link_alpha"
      ],
      "summary": "Ship-to-shore relay moved from delta sync to semantic summary.",
      "why_it_matters": "The COP can no longer move raw evidence reliably, so alert cards and evidence references must be prioritized.",
      "recommended_action": "Switch to semantic summary mode and queue raw evidence for store-forward sync.",
      "evidence_refs": [
        "obs_network_001"
      ],
      "raw_bytes": 21000,
      "semantic_bytes": 690,
      "priority": 0.807,
      "priority_features": {
        "mission_impact": 0.82,
        "urgency": 0.86,
        "confidence": 0.78,
        "trust": 0.82,
        "novelty": 0.56,
        "network_efficiency": 0.94
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_weather_hazard_001",
      "event_type": "WEATHER_HAZARD",
      "severity": "medium",
      "time": "2026-07-04T02:10:00Z",
      "location": {
        "lat": 37.32,
        "lon": 125.6,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "area_yellow_sea_corridor"
      ],
      "summary": "Reduced visibility and wave risk affect the monitored corridor.",
      "why_it_matters": "Weather raises route risk and lowers confidence in visual confirmation, making SAR/AIS disagreement more important.",
      "recommended_action": "Increase uncertainty on visual-only reports and prioritize non-cooperative detection evidence.",
      "evidence_refs": [
        "obs_weather_001"
      ],
      "raw_bytes": 65000,
      "semantic_bytes": 740,
      "priority": 0.688,
      "priority_features": {
        "mission_impact": 0.62,
        "urgency": 0.67,
        "confidence": 0.78,
        "trust": 0.83,
        "novelty": 0.38,
        "network_efficiency": 0.86
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_ais_gap_h77",
      "event_type": "AIS_GAP",
      "severity": "high",
      "time": "2026-07-04T02:25:00Z",
      "location": {
        "lat": 37.36,
        "lon": 125.66,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "vessel_haneul_77"
      ],
      "summary": "Haneul-77 has no cooperative AIS update after 02:05Z near the monitored corridor.",
      "why_it_matters": "The gap appears during network degradation and near a later SAR detection without AIS match.",
      "recommended_action": "Preserve a compact alert card and request independent confirmation.",
      "evidence_refs": [
        "obs_ais_gap_h77",
        "obs_network_001"
      ],
      "raw_bytes": 420000,
      "semantic_bytes": 910,
      "priority": 0.821,
      "priority_features": {
        "mission_impact": 0.88,
        "urgency": 0.86,
        "confidence": 0.76,
        "trust": 0.72,
        "novelty": 0.74,
        "network_efficiency": 0.91
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_sar_without_ais_001",
      "event_type": "SAR_WITHOUT_AIS",
      "severity": "critical",
      "time": "2026-07-04T02:24:00Z",
      "location": {
        "lat": 37.41,
        "lon": 125.72,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "vessel_candidate_sar_001"
      ],
      "summary": "SAR-like detection appears without an AIS candidate inside the time-distance gate.",
      "why_it_matters": "Independent physical evidence conflicts with the cooperative AIS picture and may indicate a dark-vessel candidate.",
      "recommended_action": "Route immediately as high-priority alert and queue raw SAR reference for later sync.",
      "evidence_refs": [
        "obs_sar_unmatched_001",
        "obs_ais_gap_h77",
        "obs_weather_001"
      ],
      "raw_bytes": 1480000,
      "semantic_bytes": 980,
      "priority": 0.879,
      "priority_features": {
        "mission_impact": 0.95,
        "urgency": 0.9,
        "confidence": 0.79,
        "trust": 0.76,
        "novelty": 0.88,
        "network_efficiency": 0.96
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_low_trust_report_001",
      "event_type": "LOW_TRUST_REPORT",
      "severity": "medium",
      "time": "2026-07-04T02:28:00Z",
      "location": {
        "lat": 37.02,
        "lon": 125.1,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "vessel_haneul_77"
      ],
      "summary": "Unconfirmed operator report conflicts with SAR/time-distance feasibility.",
      "why_it_matters": "Human reports are useful but must be weighted against sensor evidence and feasibility constraints.",
      "recommended_action": "Keep the report visible as contested evidence; do not let it overwrite the SAR/AIS alert.",
      "evidence_refs": [
        "obs_operator_lowtrust_001",
        "obs_sar_unmatched_001"
      ],
      "raw_bytes": 12000,
      "semantic_bytes": 640,
      "priority": 0.563,
      "priority_features": {
        "mission_impact": 0.6,
        "urgency": 0.58,
        "confidence": 0.42,
        "trust": 0.35,
        "novelty": 0.72,
        "network_efficiency": 0.82
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_osint_context_001",
      "event_type": "OSINT_INCIDENT",
      "severity": "medium",
      "time": "2026-07-04T01:35:00Z",
      "location": {
        "lat": 37.55,
        "lon": 125.95,
        "area": "Northern corridor context"
      },
      "entity_refs": [
        "area_yellow_sea_corridor"
      ],
      "summary": "Open-source advisory context raises watch priority near the corridor.",
      "why_it_matters": "OSINT is not proof, but it gives cited context for why the area deserves monitoring.",
      "recommended_action": "Attach as context only; do not escalate without sensor corroboration.",
      "evidence_refs": [
        "obs_osint_001"
      ],
      "raw_bytes": 38000,
      "semantic_bytes": 690,
      "priority": 0.557,
      "priority_features": {
        "mission_impact": 0.52,
        "urgency": 0.45,
        "confidence": 0.54,
        "trust": 0.52,
        "novelty": 0.63,
        "network_efficiency": 0.88
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    },
    {
      "event_id": "evt_composite_dark_vessel_review_001",
      "event_type": "PRIORITY_BRIEF",
      "severity": "critical",
      "time": "2026-07-04T02:30:00Z",
      "location": {
        "lat": 37.4,
        "lon": 125.7,
        "area": "Yellow Sea AOI"
      },
      "entity_refs": [
        "vessel_haneul_77",
        "vessel_candidate_sar_001"
      ],
      "summary": "Composite alert: AIS gap, SAR-without-AIS, weather hazard, and degraded network converge.",
      "why_it_matters": "This is the highest-value message to preserve when the link can only carry one alert card.",
      "recommended_action": "Send composite alert card, keep raw evidence queued, and request independent confirmation when link recovers.",
      "evidence_refs": [
        "obs_ais_gap_h77",
        "obs_sar_unmatched_001",
        "obs_weather_001",
        "obs_network_001",
        "obs_osint_001"
      ],
      "raw_bytes": 2004000,
      "semantic_bytes": 1150,
      "priority": 0.897,
      "priority_features": {
        "mission_impact": 0.97,
        "urgency": 0.92,
        "confidence": 0.8,
        "trust": 0.78,
        "novelty": 0.9,
        "network_efficiency": 0.98
      },
      "mock_notice": "Synthetic event for safe hackathon demo."
    }
  ],
  "network_modes": {
    "full_sync": {
      "label": "Full Sync",
      "bandwidth_kbps": 5000,
      "latency_ms": 80,
      "packet_loss_pct": 1,
      "send_threshold": 0.0,
      "defer_threshold": 0.0,
      "description": "Full event details and selected raw evidence can move."
    },
    "delta_sync": {
      "label": "Delta Sync",
      "bandwidth_kbps": 900,
      "latency_ms": 220,
      "packet_loss_pct": 4,
      "send_threshold": 0.45,
      "defer_threshold": 0.25,
      "description": "Changed tracks, compact event deltas, and evidence refs move."
    },
    "semantic_summary": {
      "label": "Semantic Summary",
      "bandwidth_kbps": 96,
      "latency_ms": 950,
      "packet_loss_pct": 14,
      "send_threshold": 0.72,
      "defer_threshold": 0.45,
      "description": "Only high-priority alert cards and object lists move."
    },
    "store_forward": {
      "label": "Store Forward",
      "bandwidth_kbps": 24,
      "latency_ms": 1800,
      "packet_loss_pct": 35,
      "send_threshold": 0.88,
      "defer_threshold": 0.55,
      "description": "Most messages queue locally; only critical summaries move."
    },
    "local_only": {
      "label": "Local Only",
      "bandwidth_kbps": 0,
      "latency_ms": null,
      "packet_loss_pct": 100,
      "send_threshold": 1.1,
      "defer_threshold": 0.0,
      "description": "No remote transmission. Local COP shows stale-data warnings."
    }
  },
  "routing_results": {
    "full_sync": {
      "mode": "full_sync",
      "network": {
        "label": "Full Sync",
        "bandwidth_kbps": 5000,
        "latency_ms": 80,
        "packet_loss_pct": 1,
        "description": "Full event details and selected raw evidence can move."
      },
      "packets": [
        {
          "packet_id": "pkt_full_sync_network_degraded_001",
          "event_id": "evt_network_degraded_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 21000,
          "bytes_semantic": 690
        },
        {
          "packet_id": "pkt_full_sync_weather_hazard_001",
          "event_id": "evt_weather_hazard_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 65000,
          "bytes_semantic": 740
        },
        {
          "packet_id": "pkt_full_sync_ais_gap_h77",
          "event_id": "evt_ais_gap_h77",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 420000,
          "bytes_semantic": 910
        },
        {
          "packet_id": "pkt_full_sync_sar_without_ais_001",
          "event_id": "evt_sar_without_ais_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 1480000,
          "bytes_semantic": 980
        },
        {
          "packet_id": "pkt_full_sync_low_trust_report_001",
          "event_id": "evt_low_trust_report_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 12000,
          "bytes_semantic": 640
        },
        {
          "packet_id": "pkt_full_sync_osint_context_001",
          "event_id": "evt_osint_context_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 38000,
          "bytes_semantic": 690
        },
        {
          "packet_id": "pkt_full_sync_composite_dark_vessel_review_001",
          "event_id": "evt_composite_dark_vessel_review_001",
          "network_mode": "full_sync",
          "payload_tier": "full_event",
          "decision": "send",
          "bytes_raw_estimate": 2004000,
          "bytes_semantic": 1150
        }
      ],
      "metrics": {
        "events_sent": 7,
        "events_total": 7,
        "raw_bytes_total_if_full_feed": 4040000,
        "raw_bytes_represented_by_sent_events": 4040000,
        "semantic_bytes_sent": 5800,
        "bytes_saved_pct_vs_full_feed": 99.86,
        "message_survival_rate": 1.0
      }
    },
    "delta_sync": {
      "mode": "delta_sync",
      "network": {
        "label": "Delta Sync",
        "bandwidth_kbps": 900,
        "latency_ms": 220,
        "packet_loss_pct": 4,
        "description": "Changed tracks, compact event deltas, and evidence refs move."
      },
      "packets": [
        {
          "packet_id": "pkt_delta_sync_network_degraded_001",
          "event_id": "evt_network_degraded_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 21000,
          "bytes_semantic": 690
        },
        {
          "packet_id": "pkt_delta_sync_weather_hazard_001",
          "event_id": "evt_weather_hazard_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 65000,
          "bytes_semantic": 740
        },
        {
          "packet_id": "pkt_delta_sync_ais_gap_h77",
          "event_id": "evt_ais_gap_h77",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 420000,
          "bytes_semantic": 910
        },
        {
          "packet_id": "pkt_delta_sync_sar_without_ais_001",
          "event_id": "evt_sar_without_ais_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 1480000,
          "bytes_semantic": 980
        },
        {
          "packet_id": "pkt_delta_sync_low_trust_report_001",
          "event_id": "evt_low_trust_report_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 12000,
          "bytes_semantic": 640
        },
        {
          "packet_id": "pkt_delta_sync_osint_context_001",
          "event_id": "evt_osint_context_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 38000,
          "bytes_semantic": 690
        },
        {
          "packet_id": "pkt_delta_sync_composite_dark_vessel_review_001",
          "event_id": "evt_composite_dark_vessel_review_001",
          "network_mode": "delta_sync",
          "payload_tier": "event_delta",
          "decision": "send",
          "bytes_raw_estimate": 2004000,
          "bytes_semantic": 1150
        }
      ],
      "metrics": {
        "events_sent": 7,
        "events_total": 7,
        "raw_bytes_total_if_full_feed": 4040000,
        "raw_bytes_represented_by_sent_events": 4040000,
        "semantic_bytes_sent": 5800,
        "bytes_saved_pct_vs_full_feed": 99.86,
        "message_survival_rate": 1.0
      }
    },
    "semantic_summary": {
      "mode": "semantic_summary",
      "network": {
        "label": "Semantic Summary",
        "bandwidth_kbps": 96,
        "latency_ms": 950,
        "packet_loss_pct": 14,
        "description": "Only high-priority alert cards and object lists move."
      },
      "packets": [
        {
          "packet_id": "pkt_semantic_summary_network_degraded_001",
          "event_id": "evt_network_degraded_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "send",
          "bytes_raw_estimate": 21000,
          "bytes_semantic": 690
        },
        {
          "packet_id": "pkt_semantic_summary_weather_hazard_001",
          "event_id": "evt_weather_hazard_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "defer",
          "bytes_raw_estimate": 65000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_semantic_summary_ais_gap_h77",
          "event_id": "evt_ais_gap_h77",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "send",
          "bytes_raw_estimate": 420000,
          "bytes_semantic": 910
        },
        {
          "packet_id": "pkt_semantic_summary_sar_without_ais_001",
          "event_id": "evt_sar_without_ais_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "send",
          "bytes_raw_estimate": 1480000,
          "bytes_semantic": 980
        },
        {
          "packet_id": "pkt_semantic_summary_low_trust_report_001",
          "event_id": "evt_low_trust_report_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "defer",
          "bytes_raw_estimate": 12000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_semantic_summary_osint_context_001",
          "event_id": "evt_osint_context_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "defer",
          "bytes_raw_estimate": 38000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_semantic_summary_composite_dark_vessel_review_001",
          "event_id": "evt_composite_dark_vessel_review_001",
          "network_mode": "semantic_summary",
          "payload_tier": "alert_card",
          "decision": "send",
          "bytes_raw_estimate": 2004000,
          "bytes_semantic": 1150
        }
      ],
      "metrics": {
        "events_sent": 4,
        "events_total": 7,
        "raw_bytes_total_if_full_feed": 4040000,
        "raw_bytes_represented_by_sent_events": 3925000,
        "semantic_bytes_sent": 3730,
        "bytes_saved_pct_vs_full_feed": 99.91,
        "message_survival_rate": 0.571
      }
    },
    "store_forward": {
      "mode": "store_forward",
      "network": {
        "label": "Store Forward",
        "bandwidth_kbps": 24,
        "latency_ms": 1800,
        "packet_loss_pct": 35,
        "description": "Most messages queue locally; only critical summaries move."
      },
      "packets": [
        {
          "packet_id": "pkt_store_forward_network_degraded_001",
          "event_id": "evt_network_degraded_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 21000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_weather_hazard_001",
          "event_id": "evt_weather_hazard_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 65000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_ais_gap_h77",
          "event_id": "evt_ais_gap_h77",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 420000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_sar_without_ais_001",
          "event_id": "evt_sar_without_ais_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 1480000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_low_trust_report_001",
          "event_id": "evt_low_trust_report_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 12000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_osint_context_001",
          "event_id": "evt_osint_context_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "defer",
          "bytes_raw_estimate": 38000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_store_forward_composite_dark_vessel_review_001",
          "event_id": "evt_composite_dark_vessel_review_001",
          "network_mode": "store_forward",
          "payload_tier": "critical_summary",
          "decision": "send",
          "bytes_raw_estimate": 2004000,
          "bytes_semantic": 1150
        }
      ],
      "metrics": {
        "events_sent": 1,
        "events_total": 7,
        "raw_bytes_total_if_full_feed": 4040000,
        "raw_bytes_represented_by_sent_events": 2004000,
        "semantic_bytes_sent": 1150,
        "bytes_saved_pct_vs_full_feed": 99.97,
        "message_survival_rate": 0.143
      }
    },
    "local_only": {
      "mode": "local_only",
      "network": {
        "label": "Local Only",
        "bandwidth_kbps": 0,
        "latency_ms": null,
        "packet_loss_pct": 100,
        "description": "No remote transmission. Local COP shows stale-data warnings."
      },
      "packets": [
        {
          "packet_id": "pkt_local_only_network_degraded_001",
          "event_id": "evt_network_degraded_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 21000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_weather_hazard_001",
          "event_id": "evt_weather_hazard_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 65000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_ais_gap_h77",
          "event_id": "evt_ais_gap_h77",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 420000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_sar_without_ais_001",
          "event_id": "evt_sar_without_ais_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 1480000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_low_trust_report_001",
          "event_id": "evt_low_trust_report_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 12000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_osint_context_001",
          "event_id": "evt_osint_context_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 38000,
          "bytes_semantic": 0
        },
        {
          "packet_id": "pkt_local_only_composite_dark_vessel_review_001",
          "event_id": "evt_composite_dark_vessel_review_001",
          "network_mode": "local_only",
          "payload_tier": "local_cache",
          "decision": "hold_local",
          "bytes_raw_estimate": 2004000,
          "bytes_semantic": 0
        }
      ],
      "metrics": {
        "events_sent": 0,
        "events_total": 7,
        "raw_bytes_total_if_full_feed": 4040000,
        "raw_bytes_represented_by_sent_events": 0,
        "semantic_bytes_sent": 0,
        "bytes_saved_pct_vs_full_feed": 100.0,
        "message_survival_rate": 0.0
      }
    }
  },
  "briefing": {
    "headline": "Critical dark-vessel review candidate should survive semantic-summary mode.",
    "grounded_claims": [
      {
        "claim": "Haneul-77 AIS is stale after 02:05Z.",
        "evidence_refs": [
          "obs_ais_gap_h77"
        ]
      },
      {
        "claim": "A SAR-like detection appears without AIS match at 02:24Z.",
        "evidence_refs": [
          "obs_sar_unmatched_001"
        ]
      },
      {
        "claim": "Weather and network degradation reduce raw-feed confirmation.",
        "evidence_refs": [
          "obs_weather_001",
          "obs_network_001"
        ]
      },
      {
        "claim": "A conflicting human report should be retained but down-weighted.",
        "evidence_refs": [
          "obs_operator_lowtrust_001"
        ]
      }
    ],
    "operator_summary": "Send the composite alert card first; queue raw SAR/AIS evidence for later sync; do not infer legal status without analyst review."
  }
};

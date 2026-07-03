# T3 Resilient Maritime COP Schema v0.1

- Created: 2026-07-03 KST
- Based on: T3 priority paper notes 01-40
- Purpose: prototype-ready semantic schema for "Resilient Maritime COP over Denied Networks"

## Design Principle

The COP should not treat sensor feeds as truth. It should treat every observation as a claim with source, time, confidence, trust, freshness, and provenance. Under denied or degraded networks, the system should transmit compact mission-relevant claims before raw data.

## Core Objects

| Object | Description | Key fields |
|---|---|---|
| `Vessel` | A real or hypothesized maritime entity | `vessel_id`, `mmsi`, `name`, `vessel_type`, `flag`, `identity_confidence` |
| `Track` | A time-varying kinematic state | `track_id`, `entity_id`, `lat`, `lon`, `sog`, `cog`, `heading`, `uncertainty`, `last_update` |
| `Observation` | A sensor/operator claim | `observation_id`, `source_id`, `sensor_type`, `time`, `location`, `observed_feature`, `raw_ref` |
| `EvidenceBundle` | Grouped evidence behind a COP assertion | `bundle_id`, `modality_slots`, `availability_mask`, `provenance`, `confidence`, `review_status` |
| `Event` | Operationally meaningful change or anomaly | `event_id`, `event_type`, `entity_id`, `time_window`, `severity`, `explanation` |
| `Alert` | Prioritized operator-facing item | `alert_id`, `event_id`, `priority`, `recommended_action`, `ack_status`, `assigned_to` |
| `SensorNode` | Reporting node or platform | `node_id`, `platform_type`, `owner`, `location`, `link_state`, `health_state` |
| `TrustState` | Trust estimate for a node, source, track, or event | `target_id`, `target_type`, `trust_score`, `trust_distribution`, `last_evidence` |
| `NetworkState` | Link and DDIL condition | `node_pair`, `bandwidth`, `latency`, `packet_loss`, `mode`, `observed_at` |
| `MissionContext` | Tasking and operational frame | `mission_id`, `area`, `rules`, `priority_assets`, `watch_conditions` |
| `C2State` | Stage of operational interpretation | `state_id`, `stage`, `valid_from`, `valid_until`, `intended_audience` |

## Evidence Bundle

```json
{
  "bundle_id": "eb_00042",
  "entity_id": "vessel_042",
  "semantic_type": "DARK_VESSEL_CANDIDATE",
  "time": "2026-07-03T12:00:00Z",
  "location": {"lat": 37.12, "lon": 126.51, "uncertainty_m": 800},
  "modality_slots": {
    "ais": {"status": "missing", "last_seen": "2026-07-03T10:47:00Z"},
    "sar": {"status": "detected", "scene_id": "s1_20260703_1200"},
    "eo": {"status": "unavailable", "reason": "cloud"},
    "operator_report": {"status": "none"}
  },
  "availability_mask": {
    "ais": true,
    "sar": true,
    "eo": false,
    "radar": false,
    "operator_report": false
  },
  "confidence": 0.74,
  "trust_score": 0.68,
  "freshness_seconds": 420,
  "provenance": [
    {"source": "sar_node_1", "method": "sar_detector_v0", "model_version": "0.1"},
    {"source": "ais_cache", "method": "gap_rule_v0", "window_minutes": 60}
  ],
  "review_status": "needs_analyst_review"
}
```

## Event Types

| Event type | Meaning | Initial detection logic |
|---|---|---|
| `AIS_GAP` | Vessel stopped transmitting AIS or is outside expected AIS coverage | last AIS age exceeds threshold and context says AIS should be visible |
| `SAR_WITHOUT_AIS` | SAR detects object without matching AIS | SAR detection has no AIS candidate within time-distance gate |
| `AIS_SPOOF_SUSPECTED` | Cooperative identity conflicts with independent evidence | AIS kinematics/type/location conflict with SAR/EO/radar/context |
| `ROUTE_DEVIATION` | Vessel deviates from expected route | observed route diverges from historical or planned route |
| `LOITERING` | Vessel remains in suspicious area | speed/location pattern persists within geofence |
| `RENDEZVOUS` | Multiple vessels show meeting behavior | trajectories converge with low speed and relevant duration |
| `LOW_TRUST_REPORT` | Source or track trust drops | report conflicts with expected visibility, physics, or other sources |
| `NETWORK_DEGRADED` | Link condition changes COP sync mode | bandwidth/latency/loss crosses threshold |

## Sync Modes

| Mode | Trigger | Payload |
|---|---|---|
| `full_sync` | healthy link | tracks, evidence, selected raw snippets |
| `delta_sync` | moderate bandwidth or latency pressure | changed tracks, event deltas, confidence updates |
| `semantic_summary` | severe bandwidth pressure | alert cards, object lists, priority events |
| `store_forward` | disconnected/intermittent | signed graph delta bundles queued for later sync |
| `local_only` | fully denied | local COP cache with stale-data warnings |

## Metrics

- `semantic_efficiency`: mission-relevant facts delivered per byte.
- `mission_message_throughput`: successful high-value COP messages per time window.
- `cop_freshness`: median and max age of trusted tracks/events.
- `alert_recall`: fraction of ground-truth threat/anomaly events surfaced to operator.
- `false_alert_rate`: incorrect or overconfident alert rate.
- `trace_completeness`: fraction of alerts with source, method, time, confidence, trust, and raw reference.
- `sync_recovery_time`: time until disconnected nodes converge after link restoration.
- `operator_triage_time`: time for operator to identify top risk and supporting evidence.

## Prototype Minimal Scope

Build the first demo around one scenario:

1. A vessel track is normal.
2. AIS disappears near a sensitive area.
3. SAR-like detection appears without an AIS match.
4. A low-trust human/operator report contradicts the track.
5. Network mode degrades from `full_sync` to `semantic_summary`.
6. COP preserves a high-priority alert card with evidence trace.
7. Link restores and store-forward graph deltas converge.


# Dataset Migration Review: COP v0.5 to Drone S-DOT v0.6

Date: 2026-07-04 KST

## Current Live Dataset

Current dataset:

- path: `/Users/mollykim/projects/D4D/03_data/samples/resilient_maritime_cop/mock_dataset.json`
- id: `s_dot_seoul_ground_mission_continuity_mock_v0_5`
- current focus: Seoul ground mission-continuity COP

Current top-level keys:

- `metadata`
- `scenario`
- `source_catalog`
- `operation_objective`
- `adversary_assessment`
- `mission_intent`
- `unit_nodes`
- `pace_bearer_ladder`
- `civil_comms_assets`
- `korea_civil_infra_context`
- `support_options`
- `sdot_messages`
- `rejoin_audit`
- `vessels`
- `tracks`
- `urban_routes`
- `observations`
- `evidence_bundles`
- `semantic_events`
- `network_modes`
- `routing_results`
- `briefing`

## Review Summary

The current dataset is valuable but centered on the wrong protagonist for the refined S-DOT interpretation.

The useful pieces are the semantic-transmission mechanics:

- network modes
- packet routing
- semantic event concept
- evidence/provenance concept
- rejoin audit concept
- raw-vs-semantic byte comparison

The pieces that should move out of the primary story:

- human unit tracking
- support/resource dispatch
- opposing ground route branches
- Seoul ground operation framing

## Migration Table

| Current key | Keep? | New v0.6 target | Decision |
|---|---:|---|---|
| `metadata` | yes | `metadata` | update dataset id and scenario name |
| `scenario` | partial | `simulation_cases` | replace one Seoul scenario with Case A-E |
| `source_catalog` | yes | `source_catalog` | update sources to drone/sensor/GNSS/link/weather |
| `operation_objective` | partial | `control_intent` | keep concept, rewrite around drone semantic mission |
| `mission_intent` | partial | `control_intent` | merge with operation objective |
| `network_modes` | yes | `network_modes` | keep as core |
| `routing_results` | yes | `routing_results` | recompute from drone semantic packets |
| `pace_bearer_ladder` | yes | `bearer_states` / `pace_bearer_ladder` | keep, update labels for drone control/data links |
| `observations` | yes | `raw_observations` | split into raw telemetry, EO/IR, GNSS, link, IMU, weather |
| `evidence_bundles` | yes | `custody_chains` + `evidence_bundles` | make provenance more explicit |
| `semantic_events` | yes | `semantic_events` | replace event types with drone/nav/link events |
| `sdot_messages` | yes | `semantic_packets` | rename and make payload tiers explicit |
| `rejoin_audit` | yes | `rejoin_audits` | expand with prediction-vs-truth discrepancy |
| `korea_civil_infra_context` | optional | `context_layers.public_background` | keep as optional map context only |
| `civil_comms_assets` | optional | `bearer_states` | keep as authorized bearer candidates if needed |
| `unit_nodes` | no primary | `optional_ground_context` | demote; not the protagonist |
| `support_options` | no primary | `optional_support_context` | demote; later sustainment extension |
| `adversary_assessment` | no primary | remove or optional scenario cue | remove from main S-DOT story |
| `urban_routes` | no primary | remove or map context | remove from first v0.6 |
| `vessels` | no | archive empty | leave empty or remove |
| `tracks` | no | `flight_states` | replace with drone state timeline |
| `briefing` | yes | `briefing` | rewrite around drone semantic transmission |

## New v0.6 Required Keys

```json
[
  "metadata",
  "simulation_cases",
  "source_catalog",
  "control_intent",
  "drone_assets",
  "flight_states",
  "navigation_estimates",
  "network_modes",
  "bearer_states",
  "raw_observations",
  "edge_detections",
  "jamming_hypotheses",
  "semantic_events",
  "semantic_packets",
  "routing_results",
  "custody_chains",
  "rejoin_audits",
  "context_layers",
  "briefing"
]
```

## New Event Taxonomy

Replace current ground/COP event types with:

- `STATUS_SUMMARY`
- `LINK_DEGRADED`
- `GNSS_DEGRADED`
- `NAVIGATION_RESIDUAL_SPIKE`
- `JAMMING_SUSPECTED`
- `SPOOFING_SUSPECTED`
- `EDGE_DETECTION_SUMMARY`
- `MISSION_INTENT_UPDATE`
- `RETURN_OR_HOLD_RECOMMENDATION`
- `REJOIN_AUDIT_REQUIRED`

## New Observation Taxonomy

Use:

- `EO_IR`
- `GNSS_HEALTH`
- `IMU_STATE`
- `LINK_TELEMETRY`
- `RF_CONTEXT`
- `WEATHER_CONTEXT`
- `EDGE_MODEL_OUTPUT`
- `OPERATOR_INTENT`

## New Packet Tiers

Use:

- `FULL_TELEMETRY`
- `STATE_DELTA`
- `NAV_HEALTH_CARD`
- `EDGE_DETECTION_CARD`
- `MISSION_INTENT_CARD`
- `REJOIN_AUDIT_CARD`
- `LOCAL_CACHE_ONLY`

## First Synthetic Scenario To Build

Build `case_c_gnss_jamming_suspected` first.

Minimum records:

- 1 drone asset: `UAV-S1`
- 1 relay/context asset: `UGV-R1` or `RF-S3`
- 60-120 timesteps of synthetic flight state
- 1 degraded GNSS window
- 1 intermittent command-link window
- 1 predicted path
- 1 residual spike
- 1 jamming hypothesis
- 3 semantic events
- 3 semantic packets
- 1 rejoin audit

## What Existing Data Can Support

Existing public Seoul civil layers may support:

- background map context
- weather/context overlays
- urban canyon/context risk, if kept coarse and non-sensitive

Existing support/resource data may support:

- later extension: recovery relay, landing/return support, battery/service context

Existing command COP UI can support:

- semantic event queue
- packet inspector
- evidence panel
- rejoin audit panel

## What Needs New Data

Required synthetic data:

- drone truth trajectory
- predicted trajectory
- uncertainty ellipse timeline
- GNSS quality timeline
- command link quality timeline
- IMU/GNSS disagreement timeline
- raw EO/IR byte-generation timeline
- semantic packet timeline
- rejoin discrepancy

Required public/non-sensitive data, optional:

- weather API snapshot
- terrain/building density context
- coarse map tiles

## Acceptance Criteria

The migrated dataset is ready when:

- the main object is a drone/sensor asset, not a human unit
- every semantic event explains which raw data it compressed
- every packet shows raw bytes represented and semantic bytes sent
- position is shown as prediction plus uncertainty, not exact truth
- jamming is represented as a hypothesis score, not a proven fact
- rejoin audit reconciles prediction with cached truth


# S-DOT Drone Semantic Transmission Schema v0.1

- Created: 2026-07-04 KST
- Purpose: drone/robot/sensor-first schema for the D4D S-DOT problem
- Scope: simulation and decision-support demo for denied/degraded/jammed networks

## Core Reframe

The project is no longer centered on human unit continuity. The primary object is a drone or unmanned sensor asset operating under uncertain positioning and degraded communications.

The command center should not claim exact control when the network is denied. It should maintain:

- a physics-based predicted drone state
- uncertainty bounds
- link/navigation health
- jamming or spoofing hypotheses
- mission-relevant semantic events
- provenance and rejoin audit

## Safety Boundary

This schema is for defensive simulation, training, and hackathon demonstration.

Do not include:

- real drone tasking routes
- real military unit positions
- real jamming locations or emitter parameters
- offensive EW tactics
- sensitive infrastructure coordinates
- personal data

Use:

- synthetic drone paths
- synthetic GNSS/link degradation
- public weather/topography context
- simplified physics and state estimation
- safe anomaly labels such as `nav_degraded`, `link_degraded`, `jamming_suspected`

## Product Thesis

S-DOT is a semantic transmission and operating layer for unmanned systems under DDIL and navigation uncertainty.

When raw telemetry, imagery, or full command/control cannot move, S-DOT transmits compact decision packets:

```text
Raw:
  EO/IR frames + telemetry + GNSS quality + RF/link logs + weather

Semantic:
  "UAV-S1 likely inside uncertainty ellipse E2; GNSS quality degraded;
   predicted-vs-observed residual exceeded threshold; send return/hold intent;
   raw imagery cached for rejoin audit."
```

## Core Objects

| Object | Description | Keep from old dataset? |
|---|---|---|
| `DroneAsset` | UAV/UGV/relay/sensor platform | new primary |
| `FlightState` | time-varying position, velocity, attitude, energy | new primary |
| `NavigationEstimate` | predicted state, covariance, uncertainty ellipse | new primary |
| `ControlIntent` | commander/operator intent, route envelope, safety constraints | adapted from `mission_intent` |
| `NetworkBearerState` | tactical/satellite/civil/mesh link status | adapted from `pace_bearer_ladder` |
| `RawObservation` | telemetry/image/RF/GNSS/weather input reference | adapted from `observations` |
| `EdgeDetection` | local model/rule output before semantic event | new primary |
| `SemanticEvent` | decision-relevant meaning unit | keep and refactor |
| `SemanticPacket` | actual S-DOT payload shaped by link mode | adapted from `sdot_messages` |
| `JammingHypothesis` | probability that GNSS/link degradation is caused by interference | new primary |
| `RejoinAudit` | comparison between predicted state and cached raw truth after reconnection | keep and refactor |
| `SimulationCase` | scenario definition for 3D demo | new primary |

## State Estimation Model

### State Vector

For a hackathon demo, a simplified 2.5D model is enough:

```text
x_t = [
  lat,
  lon,
  alt_m,
  v_north_mps,
  v_east_mps,
  v_down_mps,
  heading_deg,
  battery_pct,
  wind_north_mps,
  wind_east_mps
]
```

If implementing in a local Cartesian frame, prefer ENU/NED coordinates for calculation and convert to lat/lon only for display.

```text
x_t = [p_N, p_E, p_D, v_N, v_E, v_D, psi, battery, w_N, w_E]
```

### Physics Prediction

For short intervals:

```text
p_{t+dt} = p_t + v_t * dt + 0.5 * a_t * dt^2 + w_t * dt
v_{t+dt} = v_t + a_t * dt
```

Where:

- `p`: position in local N/E/D coordinates
- `v`: velocity
- `a`: commanded or estimated acceleration
- `w`: wind drift vector
- `dt`: timestep

This is not enough for a real autopilot, but it is enough for a command-room prediction envelope demo.

### Uncertainty Growth

When telemetry is missing, uncertainty should grow over time:

```text
sigma_pos(t)^2 =
  sigma_pos0^2
  + sigma_vel^2 * t^2
  + 0.25 * sigma_acc^2 * t^4
  + sigma_wind^2 * t^2
```

Practical demo interpretation:

- the longer the drone is disconnected, the larger the uncertainty ellipse
- bad weather/wind increases growth
- aggressive maneuvering increases growth
- poor prior GNSS quality increases initial uncertainty

### Kalman / EKF Form

Prediction:

```text
x_pred = f(x_prev, u_t, dt)
P_pred = F_t * P_prev * F_t^T + Q_t
```

Measurement update:

```text
y_t = z_t - H_t * x_pred
S_t = H_t * P_pred * H_t^T + R_t
K_t = P_pred * H_t^T * S_t^-1
x_upd = x_pred + K_t * y_t
P_upd = (I - K_t * H_t) * P_pred
```

Where:

- `x`: estimated state
- `P`: covariance
- `z`: incoming measurement
- `Q`: process noise
- `R`: measurement noise
- `y`: innovation/residual
- `S`: innovation covariance

### Residual-Based Anomaly Detection

Normalized Innovation Squared:

```text
NIS = y_t^T * S_t^-1 * y_t
```

If `NIS` exceeds a threshold, the received measurement is inconsistent with the predicted physical state.

Demo interpretation:

- small residual: normal drift
- moderate residual: poor GNSS/weather/telemetry quality
- large residual plus link/GNSS quality degradation: jamming or spoofing suspected
- large residual without RF/GNSS degradation: sensor error or unexpected maneuver

Use this as a hypothesis score, not proof.

## Jamming / Navigation Degradation Hypothesis

The system should not magically know jamming. It should infer a probability from multiple weak signals.

### Inputs

Use synthetic indicators:

- GNSS fix status
- satellite count
- HDOP/VDOP
- GNSS C/N0 quality bucket
- position residual / NIS
- command link SNR bucket
- packet loss
- heartbeat gap duration
- IMU/GNSS disagreement
- weather/wind penalty
- terrain/urban canyon context

### Score

Simple explainable demo score:

```text
jamming_score =
  0.25 * gnss_quality_drop
  + 0.20 * link_quality_drop
  + 0.20 * normalized_position_residual
  + 0.15 * heartbeat_gap_score
  + 0.10 * imu_gnss_disagreement
  + 0.10 * context_risk
```

Suggested labels:

```text
0.00 - 0.35: normal_or_environmental
0.35 - 0.60: navigation_degraded
0.60 - 0.80: jamming_suspected
0.80 - 1.00: severe_denial_suspected
```

Important:

This is a defensive diagnostic score. It should not claim source location or provide offensive EW guidance.

## S-DOT Semantic Compression

### Raw Inputs

Examples:

- EO/IR frame batch: 18 MB
- telemetry stream: 900 KB/min
- RF/link logs: 240 KB
- GNSS quality log: 80 KB
- weather tile: 120 KB
- local map tile/context: 500 KB

### Semantic Packet

Example:

```json
{
  "packet_id": "sdot_nav_001",
  "asset_id": "uav_s1",
  "event_type": "NAVIGATION_DEGRADED",
  "time": "2026-07-04T03:12:10Z",
  "predicted_position": {"x_m": 420, "y_m": -180, "alt_m": 120},
  "uncertainty_ellipse": {"major_m": 380, "minor_m": 140, "bearing_deg": 62},
  "jamming_score": 0.68,
  "confidence": 0.61,
  "why_it_matters": "drone cannot be treated as exactly located; mission packet should switch to intent-only mode",
  "recommended_action": "send mission intent update and hold raw evidence for rejoin audit",
  "evidence_refs": ["obs_gnss_012", "obs_link_014", "obs_imu_011"],
  "raw_bytes_represented": 19340000,
  "semantic_bytes": 920
}
```

## Event Types

| Event type | Meaning | Detection idea |
|---|---|---|
| `LINK_DEGRADED` | command/data link quality falls | packet loss, SNR, heartbeat gap |
| `GNSS_DEGRADED` | positioning quality drops | fix loss, satellite count, HDOP, C/N0 quality bucket |
| `NAVIGATION_RESIDUAL_SPIKE` | predicted vs received state mismatch | NIS exceeds threshold |
| `JAMMING_SUSPECTED` | multi-signal evidence suggests interference | score from GNSS/link/residual/context |
| `SPOOFING_SUSPECTED` | position appears valid but inconsistent with inertial/physics model | GNSS fix remains but residual/IMU disagreement rises |
| `EDGE_DETECTION_SUMMARY` | edge model detected relevant object/route/cue | local detector output, no raw imagery sent |
| `MISSION_INTENT_UPDATE` | operator sends compact intent under low bandwidth | valid-until, priorities, safe behavior |
| `RETURN_OR_HOLD_RECOMMENDATION` | platform should preserve safety/mission continuity | based on battery/link/uncertainty |
| `REJOIN_AUDIT_REQUIRED` | cached raw evidence must be reconciled later | semantic prediction and raw evidence diverge |

## Network Modes

| Mode | Trigger | Drone behavior | Payload |
|---|---|---|---|
| `full_sync` | healthy link | telemetry + selected raw snippets | detailed state, thumbnails, events |
| `delta_sync` | moderate degradation | changed fields only | state deltas, event deltas |
| `semantic_summary` | severe bandwidth pressure | no raw feed; event cards only | semantic events, uncertainty, evidence refs |
| `store_forward` | intermittent | cache raw; send critical cards | critical semantic packets |
| `local_only` | denied | local autonomy/safety behavior; no remote control claim | local log only |

## 3D Simulation Cases

The demo should show multiple cases instead of one linear story.

### Case A: Normal Mission

- GNSS stable
- link stable
- predicted path and actual path remain close
- S-DOT sends low-volume status summaries

### Case B: Link Degradation Only

- position remains reliable
- command link degrades
- raw video cannot move
- semantic event cards continue

### Case C: GNSS Jamming Suspected

- GNSS quality drops
- heartbeat becomes intermittent
- predicted state uncertainty grows
- residual exceeds threshold
- command center marks `jamming_suspected`

### Case D: Spoofing-Like Inconsistency

- GNSS appears present
- reported position diverges from IMU/physics prediction
- NIS spikes
- command center marks `spoofing_suspected` or `nav_residual_spike`

### Case E: Rejoin Audit

- connectivity returns
- cached raw telemetry is compared with predicted state
- system explains what was right/wrong
- trust and confidence update

## Demo UI Requirements

### Left panel: Scenario / Case Control

- choose Case A-E
- choose network mode
- choose wind/weather severity
- choose GNSS degradation level

### Center: 3D Drone Simulation

- 3D AOI
- predicted path
- actual/simulated path
- uncertainty ellipsoid or cone
- jamming/degradation zone as non-operational hypothesis overlay
- drone asset marker and sensor FOV

### Right panel: Operator Decision Board

- current mission intent
- drone asset health
- network/GNSS state
- jamming score
- residual/NIS
- semantic event queue
- packet inspector
- evidence/provenance chain

### Bottom: Raw vs Semantic Timeline

- raw telemetry/image/link bytes generated
- semantic bytes transmitted
- packets sent/deferred/held
- rejoin audit status

## Dataset Migration From v0.5

| Existing v0.5 field | New role |
|---|---|
| `operation_objective` | keep as `control_intent` / mission card |
| `mission_intent` | keep and rename/merge into `control_intent` |
| `network_modes` | keep |
| `routing_results` | keep but compute from drone events |
| `pace_bearer_ladder` | keep |
| `observations` | split into `raw_observations` and `edge_detections` |
| `semantic_events` | keep but replace event types with drone/nav/link events |
| `sdot_messages` | rename to `semantic_packets` |
| `rejoin_audit` | keep and expand |
| `korea_civil_infra_context` | keep as optional background/context only |
| `unit_nodes` | demote to optional ground observer/support context |
| `support_options` | demote to optional support context |
| `adversary_assessment` | remove from primary story; may become optional scenario cue |
| `urban_routes` | remove or use only as map context |
| `vessels`, `tracks` | keep empty or archive |

## Minimal v0.6 Dataset Shape

```json
{
  "metadata": {},
  "simulation_cases": [],
  "control_intent": {},
  "drone_assets": [],
  "flight_states": [],
  "navigation_estimates": [],
  "network_modes": {},
  "bearer_states": [],
  "raw_observations": [],
  "edge_detections": [],
  "jamming_hypotheses": [],
  "semantic_events": [],
  "semantic_packets": [],
  "routing_results": {},
  "custody_chains": [],
  "rejoin_audits": [],
  "context_layers": {}
}
```

## Evaluation Metrics

- `position_prediction_error_m`: distance between predicted and simulated actual state
- `uncertainty_coverage`: whether actual position stayed inside predicted envelope
- `jamming_detection_precision`: suspected jamming labels that are correct in simulation
- `jamming_detection_recall`: true simulated degradation cases surfaced
- `semantic_compression_ratio`: raw bytes represented / semantic bytes sent
- `mission_packet_survival_rate`: high-value packets delivered under DDIL
- `rejoin_audit_discrepancy`: difference between semantic prediction and cached raw truth
- `operator_time_to_diagnosis`: time to identify nav/link problem in UI

## Implementation Priorities

1. Build synthetic drone flight simulator dataset.
2. Implement prediction and uncertainty growth.
3. Implement residual/NIS anomaly score.
4. Implement jamming hypothesis score.
5. Convert raw observations into semantic events.
6. Build 3D simulation view.
7. Connect packet routing to network modes.
8. Show provenance and rejoin audit.


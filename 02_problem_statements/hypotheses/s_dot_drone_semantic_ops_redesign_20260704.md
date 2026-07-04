# S-DOT Drone Semantic Operations Platform Redesign

Date: 2026-07-04 KST

## Decision

The S-DOT project should be reframed from a primarily command-staff/unit-continuity COP into a drone/robot/sensor-first semantic transmission platform.

The current COP work remains useful, but it should become the receiving and decision-support layer. The main product story should move upstream:

> Drones, robots, EO/IR, RF, radar, and OSINT generate more data than a denied/degraded tactical network can move. S-DOT converts raw sensor feeds into mission-relevant semantic events at the edge, prioritizes them by mission intent and link state, transmits only what matters, and preserves provenance/rejoin audit for later review.

## Revised Problem Framing

### Old framing

How can headquarters continue to understand isolated units and support them with a mission-continuity COP under disconnected/degraded network conditions?

### Revised framing

How can unmanned and distributed sensing assets operate under disconnected/degraded tactical networks by converting raw sensor data into compact semantic packets that preserve:

- mission relevance
- source provenance
- confidence and uncertainty
- track/custody continuity
- prioritized transmission
- rejoin audit after connectivity returns

## What This Now Is

S-DOT is a mission-aware semantic compression and routing layer between unmanned sensing assets and C2/COP.

It is not primarily:

- a drone autopilot
- a swarm-control algorithm
- a real tactical network standard
- a real-time targeting system
- a real force-tracking product

It is primarily:

- an edge semantic encoder for drone/robot/sensor observations
- a DDIL-aware packet prioritization engine
- a source-provenance and custody layer
- a compact COP update mechanism
- a rejoin/audit workflow after intermittent links recover

## Target Platform Concept

Working name:

**S-DOT Edge Semantic Ops**

Korean description:

**드론·로봇·센서가 수집한 대용량 전장 데이터를 전술망 상태와 임무 의도에 맞춰 의미 단위로 압축·우선순위화·전송하는 엣지-지휘 연계 플랫폼**

## Platform Layers

### 1. Sensor / Unmanned Asset Layer

Synthetic demo assets:

- `UAV-S1`: EO/IR observation node
- `UAV-S2`: wide-area visual scan node
- `UGV-R1`: ground relay / local collector
- `RF-S3`: RF anomaly sensor
- `RAD-S4`: radar-like coarse detection node
- `OSINT-FEED`: public advisory/context feed

Role:

- produce raw or semi-processed observations
- cache local data when disconnected
- emit only semantic summaries when bandwidth is limited

### 2. Edge Semantic Encoder

Converts high-volume raw inputs into structured semantic objects.

Example:

```text
Raw input:
- EO/IR frame batch: 18 MB
- RF anomaly log: 240 KB
- local timestamp/GPS quality: 4 KB
- OSINT context card: 38 KB

Semantic output:
- event_type: ROUTE_CANDIDATE_WATCH
- entity_refs: [axis_a, uav_s1, rf_s3]
- confidence: 0.54
- uncertainty_radius_m: 900
- why_it_matters: affects mission watch priority
- evidence_refs: [obs_eoir_001, obs_rf_003, obs_osint_001]
- semantic_bytes: 860 B
```

Key design principle:

The edge does not need to send every pixel, frame, waveform, or log line. It sends what changed the command decision.

### 3. Mission Intent / Task Relevance Layer

Semantic compression must be task-aware.

The same observation can have different priority depending on current intent:

- protect a civilian access corridor
- maintain surveillance of a candidate route
- keep drone relay alive until rejoin window
- preserve evidence for later audit
- avoid overloading a low-bandwidth link

Required fields:

- mission objective
- current phase
- protected priorities
- valid-until
- confidence decay rule
- evidence retention policy

### 4. DDIL Network / Bearer Layer

The network state controls packet shape.

Modes:

- `full_sync`: raw thumbnails, event details, and evidence bundles can move
- `delta_sync`: changed fields and compact evidence references move
- `semantic_summary`: alert cards and object summaries move
- `store_forward`: only critical semantic cards move; raw evidence queues locally
- `local_only`: no remote transmission; local audit log continues

PACE/bearer candidates:

- tactical IP
- satellite/long-haul backup
- approved public/civil bearer candidate
- mesh/store-forward
- physical/local sync after rejoin

### 5. Semantic Packet Router

Ranks packets using:

- mission impact
- urgency
- confidence
- source trust
- novelty
- network efficiency
- custody value

Output:

- send
- defer
- hold local
- request targeted raw snippet
- queue for rejoin audit

### 6. Command COP / Review Layer

The command room should see:

- current mission objective
- sensor asset health
- link state
- semantic event queue
- confirmed vs predicted observations
- source provenance
- confidence/uncertainty
- what was transmitted vs held locally
- what must be audited after rejoin

The existing Seoul COP demo can be reused here, but the map should foreground unmanned/sensor assets rather than human unit nodes.

### 7. Rejoin Audit Layer

When connectivity returns:

- compare predicted semantic state with raw cached evidence
- sync only necessary raw excerpts
- flag disagreement between edge summaries and raw data
- preserve custody trail
- update confidence and trust scores

## New Core Data Model

### `sensor_assets`

Represents drones, robots, fixed sensors, or relay nodes.

Fields:

- `asset_id`
- `asset_code`
- `asset_type`
- `sensor_modalities`
- `comm_state`
- `battery_pct`
- `last_contact_time`
- `position`
- `local_cache_status`
- `sdot_outbox_count`

### `raw_observations`

Represents high-volume source data or source references.

Fields:

- `observation_id`
- `asset_id`
- `sensor_type`
- `time`
- `location`
- `raw_ref`
- `raw_bytes`
- `classification_safe_notice`
- `retention_policy`

### `edge_detections`

Represents local model/sensor results before final semantic event generation.

Fields:

- `detection_id`
- `observation_refs`
- `candidate_type`
- `confidence`
- `uncertainty`
- `model_or_rule`
- `edge_compute_cost`

### `semantic_events`

Represents decision-relevant meaning units.

Fields:

- `event_id`
- `event_type`
- `severity`
- `summary`
- `why_it_matters`
- `recommended_action`
- `evidence_refs`
- `source_assets`
- `confidence`
- `trust_score`
- `raw_bytes`
- `semantic_bytes`
- `priority`
- `transmission_decision_by_mode`

### `semantic_packets`

Represents actual S-DOT transmission units.

Fields:

- `packet_id`
- `event_id`
- `payload_tier`
- `network_mode`
- `decision`
- `bytes_semantic`
- `bytes_raw_represented`
- `expires_at`
- `requires_ack`
- `rejoin_audit_required`

### `custody_chain`

Represents provenance and continuity.

Fields:

- `custody_id`
- `event_id`
- `source_observation_refs`
- `edge_encoder_version`
- `packet_id`
- `sent_time`
- `received_time`
- `held_raw_refs`
- `audit_status`

## Demo Redesign

### Current demo elements to keep

- Seoul public map
- mission objective banner
- DDIL mode selector
- semantic event queue
- raw-vs-semantic packet inspector
- PACE/bearer ladder
- evidence bundle panel
- rejoin audit
- public/civil context as safe map context

### Current demo elements to de-emphasize

- human unit branch tracking as the main story
- support/resource dispatch as the primary outcome
- command-staff COP as the only visible product

### New demo elements to add

1. **Edge Sensor Feed Simulator**
   - shows mock EO/IR, RF, radar, and OSINT input sizes
   - shows what cannot be transmitted under each network mode

2. **Drone / Robot Asset Strip**
   - `UAV-S1`, `UAV-S2`, `UGV-R1`, `RF-S3`, `RAD-S4`
   - comm state, battery, cache, outbox

3. **Semantic Encoder Panel**
   - raw observation -> edge detection -> semantic event
   - visible byte reduction
   - evidence refs preserved

4. **S-DOT Packet Inspector**
   - payload tier comparison
   - what is sent, deferred, held local
   - why the router made the choice

5. **Custody / Provenance Panel**
   - which sensor generated the observation
   - which model/rule encoded it
   - what raw evidence remains cached
   - what must be audited after rejoin

6. **Command COP**
   - receives semantic events rather than raw feeds
   - shows route/watch hypotheses as uncertainty-aware overlays
   - separates confirmed, inferred, and predicted layers

## Revised Hackathon Storyline

Suggested pitch:

> Modern unmanned systems produce far more data than tactical networks can carry, especially under jamming, denial, and intermittent connectivity. S-DOT solves this by moving semantic meaning instead of raw data. A drone or robot does not stream everything; it sends compact, mission-relevant event cards with provenance, confidence, and audit hooks. Command staff can keep a minimum COP alive, and when the network rejoins, the system reconciles semantic predictions with cached raw evidence.

## Palantir / Local Split

### Use Palantir Foundry / AIP for

- ontology model: assets, observations, semantic events, packets, custody chain
- command review workflow
- analyst explanation and evidence review
- event prioritization action types
- AIP-assisted summarization and query over semantic events
- provenance-aware COP objects

### Build locally for demo

- sensor feed simulator
- edge semantic encoder mock
- DDIL network mode emulator
- map visualization
- packet inspector
- rejoin audit simulation
- public static demo

## V0.6 Implementation Direction

Goal:

Refactor the current Seoul COP demo into a drone/sensor-first S-DOT platform without throwing away the current work.

Tasks:

1. Add `sensor_assets` to the mock dataset.
2. Add `raw_observations` with EO/IR, RF, radar, OSINT, and network source types.
3. Add `edge_detections` as the intermediate layer between raw data and semantic events.
4. Change the map foreground from human unit nodes to drone/sensor nodes.
5. Keep `12-1` as an optional supported ground element, not the main protagonist.
6. Add semantic encoder panel.
7. Add custody/provenance panel.
8. Update event copy so each event clearly explains which sensor data was compressed.

## V0.7 Implementation Direction

Goal:

Make the demo feel like the actual S-DOT problem statement.

Tasks:

1. Add a raw feed vs semantic feed comparison timeline.
2. Add network-mode-dependent packet survival animation.
3. Add targeted raw snippet request workflow.
4. Add rejoin audit diff: semantic prediction vs cached raw evidence.
5. Add Palantir ontology export bundle.
6. Add a short presentation story around drone/robot data overload.

## Safety Boundary

The demo must not include:

- real military unit locations
- real drone tasking or tactical routes
- real sensitive infrastructure coordinates
- offensive targeting recommendations
- classified or restricted data
- personal data

The demo may include:

- public map context
- public civil context at safe granularity
- synthetic drone/sensor assets
- synthetic RF/EO/radar detections
- synthetic network degradation
- synthetic semantic packets
- synthetic rejoin audit

## One-Sentence Final Direction

S-DOT should be presented as a drone/robot/sensor-first semantic transmission layer that keeps command decisions possible when raw data cannot move.

# S-DOT Drone Jamming / DDIL Operating Concept

Date: 2026-07-04 KST

## New Direction

The project should now be framed as:

> A drone semantic transmission and navigation-integrity platform that keeps operators informed when command links, telemetry, and GNSS quality are degraded by DDIL or suspected interference.

The key question is not:

> Where is the unit?

The key question is:

> What can the command center still know, infer, transmit, and audit when a drone cannot reliably stream raw data or exact position?

## Core Problem

Drones and unmanned systems rely on multiple fragile assumptions:

- command link is available
- telemetry can be transmitted
- GNSS position is trustworthy
- raw EO/IR or sensor data can be streamed
- operator can see enough context to decide

Under jamming, interference, terrain masking, urban canyon effects, congestion, or network denial, these assumptions break.

S-DOT should preserve a minimum operating picture by transmitting semantic meaning:

- predicted position envelope
- navigation confidence
- link state
- GNSS integrity state
- sensor evidence summary
- jamming/spoofing hypothesis score
- mission intent update
- what raw evidence is cached for rejoin audit

## Product Definition

Product name:

**S-DOT Edge Semantic Ops**

Korean:

**드론 교란·단절 환경을 위한 시맨틱 전송 및 예측 상황판**

One-liner:

**드론이 원본 영상·텔레메트리·정확 위치를 계속 보낼 수 없을 때, 물리 예측과 센서 신뢰도 기반으로 위치 불확실성·교란 의심·임무 판단 패킷만 압축 전송하는 플랫폼**

## What The Hackathon Demo Should Show

### 1. 3D Drone Simulation

Purpose:

Show the user what is happening physically.

Visual elements:

- synthetic drone in 3D
- planned route
- predicted route
- simulated actual route
- uncertainty cone/ellipse
- sensor field of view
- degraded GNSS/link zone as a hypothesis overlay
- raw data generation meter

The 3D view should make the problem intuitive:

> The drone is still flying, but HQ no longer has exact truth. The predicted state keeps moving, uncertainty grows, and only semantic packets survive.

### 2. Operator Situation Board

Purpose:

Show what HQ/control can know and decide.

Panels:

- current mission intent
- drone health
- link state
- GNSS/navigation state
- predicted vs observed residual
- jamming hypothesis score
- semantic event queue
- raw vs semantic byte comparison
- provenance/evidence chain
- rejoin audit status

### 3. Case Selector

The demo should switch between cases:

- Normal flight
- Link degradation only
- GNSS degradation / jamming suspected
- spoofing-like position inconsistency
- rejoin audit

This lets reviewers see that S-DOT is not one hardcoded alert. It is a general method for DDIL drone operations.

## Key Scientific Claims

### Claim 1: HQ can maintain a predicted position, not exact truth.

Use a motion model:

```text
p_{t+dt} = p_t + v_t * dt + 0.5 * a_t * dt^2 + wind_t * dt
```

This produces a predicted state after telemetry loss.

### Claim 2: Uncertainty must grow while disconnected.

Use uncertainty growth:

```text
sigma_pos(t)^2 =
  sigma_pos0^2
  + sigma_vel^2 * t^2
  + 0.25 * sigma_acc^2 * t^4
  + sigma_wind^2 * t^2
```

This prevents the UI from pretending the drone's location is exact.

### Claim 3: Jamming cannot be directly assumed, but can be hypothesized.

Use residuals plus signal-quality indicators:

```text
NIS = y_t^T * S_t^-1 * y_t
```

If predicted state and received/claimed state disagree beyond expected covariance, the system raises a navigation integrity anomaly.

Then combine:

```text
jamming_score =
  0.25 * gnss_quality_drop
  + 0.20 * link_quality_drop
  + 0.20 * normalized_position_residual
  + 0.15 * heartbeat_gap_score
  + 0.10 * imu_gnss_disagreement
  + 0.10 * context_risk
```

The result is a hypothesis:

- normal/environmental
- navigation degraded
- jamming suspected
- severe denial suspected

It is not proof and should not claim emitter location.

### Claim 4: S-DOT value comes from byte economics.

Raw feed may be too heavy:

```text
EO/IR frame batch: 18 MB
telemetry/logs: 1 MB
weather/map context: 600 KB
```

Semantic packet:

```text
NAV_HEALTH_CARD: 920 B
```

The demo should show:

```text
raw bytes represented / semantic bytes sent
```

### Claim 5: Rejoin audit makes the system honest.

When the link returns:

- compare predicted state against cached raw telemetry
- show discrepancy
- update trust/confidence
- explain what the operator knew at the time

## Main Algorithm Modules

### Module A: Flight State Predictor

Inputs:

- last known position
- velocity
- heading
- wind
- timestep
- process noise

Outputs:

- predicted position
- predicted path
- uncertainty ellipse

### Module B: Navigation Integrity Monitor

Inputs:

- predicted state
- new GNSS/telemetry state if available
- covariance
- GNSS health
- IMU consistency

Outputs:

- residual
- NIS
- anomaly label

### Module C: Link / DDIL Monitor

Inputs:

- packet loss
- heartbeat gap
- latency
- bandwidth
- SNR bucket

Outputs:

- network mode
- allowed payload tiers

### Module D: Jamming Hypothesis Engine

Inputs:

- GNSS quality drop
- link quality drop
- residual score
- heartbeat gap
- IMU/GNSS disagreement
- context risk

Outputs:

- `jamming_score`
- label
- evidence refs
- caveat

### Module E: Semantic Encoder

Inputs:

- raw observations
- edge detections
- mission intent
- network mode

Outputs:

- semantic event
- semantic packet
- evidence refs
- raw bytes represented

### Module F: Packet Router

Inputs:

- semantic event priority
- network mode
- payload tier
- packet size

Outputs:

- send
- defer
- hold local
- request raw snippet
- audit after rejoin

## UI Rebuild Direction

### Main screen layout

```text
┌────────────────────────────────────────────────────────────┐
│ Mission Intent / Case Selector / Network Mode              │
├───────────────┬─────────────────────────┬──────────────────┤
│ Asset & Link  │ 3D Drone Simulation     │ Operator Board   │
│ Health        │ predicted vs actual     │ residual / score │
│               │ uncertainty envelope    │ packets / audit  │
├───────────────┴─────────────────────────┴──────────────────┤
│ Raw Feed vs Semantic Packet Timeline                       │
└────────────────────────────────────────────────────────────┘
```

### Keep from current demo

- Korean-first labels
- objective banner
- network mode selector
- semantic event queue
- packet inspector
- evidence/provenance display
- rejoin audit

### Replace or demote

- ground-unit markers become optional context
- support/resource routing becomes secondary
- adversary route axes are removed from the main story
- 2D Seoul map may remain as background, but 3D drone sim becomes primary

## Dataset Reset

New live dataset target:

```text
s_dot_drone_semantic_ops_mock_v0_6
```

Required top-level keys:

- `simulation_cases`
- `control_intent`
- `drone_assets`
- `flight_states`
- `navigation_estimates`
- `network_modes`
- `bearer_states`
- `raw_observations`
- `edge_detections`
- `jamming_hypotheses`
- `semantic_events`
- `semantic_packets`
- `routing_results`
- `custody_chains`
- `rejoin_audits`
- `context_layers`

## What To Tell Judges

We initially explored the C2/COP side, but refined the design to match S-DOT more closely:

> S-DOT is not just a map. It is the layer that lets drones and sensors keep contributing mission-relevant information when raw data and exact control cannot survive the network.

## Next Build Decision

Build v0.6 as a new drone-centric prototype slice:

1. Generate synthetic drone simulation data.
2. Add flight prediction and uncertainty.
3. Add NIS/residual anomaly calculation.
4. Add jamming hypothesis scoring.
5. Add semantic packet generation.
6. Build 3D drone simulation UI.
7. Reuse the existing packet/evidence/rejoin panels where possible.


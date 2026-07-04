# S-DOT Drone Simulation Prototype Roadmap

- Date: 2026-07-04 KST
- Target build: v0.6
- Goal: pivot the current S-DOT COP demo into a drone/sensor-first semantic transmission demo.
- Current status: v0.6 static demo implemented and deployed.

## Current Prototype Assessment

Current app:

- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop`
- public deployment: `d4d-cop-public`
- dataset id: `s_dot_seoul_ground_mission_continuity_mock_v0_5`

What is still useful:

- Korean command-board style
- objective banner
- DDIL network mode selector
- semantic event queue
- raw-vs-semantic packet comparison
- evidence panel
- PACE/Bearer concept
- rejoin audit concept
- public deployment pipeline

What no longer fits as the primary story:

- human unit branch tracking
- support/resource dispatch
- opposing route axes
- Seoul ground operation as the main scenario

## New Prototype Experience

The first screen should feel like a drone operations simulator, not only a staff COP.

Primary screen:

- 3D drone simulation in the center
- drone path, predicted path, and uncertainty envelope
- link/GNSS degradation overlays
- operator decision board on the right
- raw-vs-semantic packet timeline at the bottom
- case/network controls on the left

## Build Phases

### Phase 1: Data Generator v0.6

Create:

- `generate_sdot_drone_semantic_ops_dataset.py`

Outputs:

- `/Users/mollykim/projects/D4D/03_data/samples/sdot_drone_semantic_ops/mock_dataset.json`
- app copy under a prototype app data folder

Status:

- generator created at `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_sdot_drone_semantic_ops_dataset.py`
- dataset generated at `/Users/mollykim/projects/D4D/03_data/samples/sdot_drone_semantic_ops/mock_dataset.json`
- browser-ready JS generated at `/Users/mollykim/projects/D4D/03_data/samples/sdot_drone_semantic_ops/mock_dataset.js`
- app copy generated under `/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops/data`
- Palantir/AIP handoff metadata embedded in the dataset

Dataset fields:

- `simulation_cases`
- `control_intent`
- `drone_assets`
- `flight_states`
- `navigation_estimates`
- `network_modes`
- `raw_observations`
- `edge_detections`
- `jamming_hypotheses`
- `semantic_events`
- `semantic_packets`
- `custody_chains`
- `rejoin_audits`
- `algorithm_basis`
- `case_evaluations`
- `case_evaluation_series`
- `kalman_estimator_traces`
- `platform_handoff`

### Phase 2: Algorithm Engine

Implement deterministic demo algorithms:

- constant velocity / acceleration prediction
- wind drift
- uncertainty growth
- NIS residual
- jamming hypothesis score
- semantic packet priority score
- routing decision by DDIL mode

Keep parameters visible in the UI so judges can understand the basis.

### Phase 3: 3D Scene

Use Three.js.

Scene requirements:

- full-bleed central 3D scene
- drone model or simple drone mesh
- planned path
- predicted path
- simulated actual path
- uncertainty cone/ellipsoid
- sensor FOV
- degraded zone overlay as a hypothesis region
- time scrubber or play/pause

Important:

The 3D scene should not be a decorative card. It is the primary experience.

### Phase 4: Operator Board

Right panel:

- asset health
- link status
- GNSS status
- residual/NIS
- jamming hypothesis score
- current semantic event
- recommended operating mode

### Phase 5: S-DOT Packet Inspector

Show:

- raw bytes generated
- semantic bytes sent
- packet tier
- send/defer/hold-local decision
- evidence refs
- raw evidence held for audit

### Phase 6: Rejoin Audit

Show:

- predicted state before rejoin
- cached simulated truth after rejoin
- discrepancy distance
- whether actual path was inside uncertainty envelope
- confidence update
- raw evidence refs synced

## Initial Cases

### Case A: Normal Flight

Purpose:

Baseline. Shows prediction and telemetry align.

### Case B: Link Degradation

Purpose:

Shows raw video cannot move but semantic events survive.

### Case C: GNSS Jamming Suspected

Purpose:

Main scenario. Shows GNSS/link degradation, uncertainty growth, residual spike, and jamming hypothesis.

### Case D: Spoofing-Like Inconsistency

Purpose:

Shows why a valid-looking GNSS point may still be untrusted.

### Case E: Rejoin Audit

Purpose:

Shows system honesty after reconnection.

## Minimal Demo Story

1. UAV-S1 flies a synthetic route.
2. Network shifts from `full_sync` to `semantic_summary`.
3. GNSS quality drops and packet loss rises.
4. HQ prediction continues but uncertainty expands.
5. A new position update falls outside expected residual threshold.
6. S-DOT raises `JAMMING_SUSPECTED`.
7. Raw EO/IR remains cached.
8. A small `NAV_HEALTH_CARD` is transmitted.
9. Rejoin audit later compares cached raw truth with the prediction.

## Files To Add Next

Suggested app path:

- `/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops`

Status:

- app created at `/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops`
- deployed as `d4d-sdot-drone`
- active URL: https://bench-coverage-saving-membrane.trycloudflare.com

Suggested files:

- `index.html`
- `assets/app.js`
- `assets/styles.css`
- `data/mock_dataset.json`
- `data/mock_dataset.js`
- `server.js`
- `package.json`

Suggested script:

- `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_sdot_drone_semantic_ops_dataset.py`

## Reuse From Current App

Can reuse with adaptation:

- mode buttons
- event queue component
- packet table
- evidence panel
- glossary
- deployment server

Should rewrite:

- map rendering
- unit rendering
- support route rendering
- adversary axis rendering

## Validation Checklist

Data:

- JSON valid
- all semantic packets reference existing semantic events
- all semantic events reference existing observations/detections/hypotheses
- every simulation case has expected event types
- platform handoff bundle has 12 object tables and 225 relationship links with no missing references

Algorithm:

- uncertainty grows under disconnection
- NIS threshold flags designed anomaly case
- jamming score changes by case
- packet size savings are visible

UI:

- 3D scene renders nonblank
- drone/path/uncertainty visible
- case switch changes state
- algorithm evaluation and Kalman-style estimator panels render
- Foundry/AIP handoff panel renders on the public URL

Current public verification:

- active URL: https://bench-coverage-saving-membrane.trycloudflare.com
- screenshot: `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_handoff_public.png`
- network mode changes packet decisions
- raw-vs-semantic timeline updates
- no text overlaps on mobile/desktop

Safety:

- no real routes
- no real military assets
- no EW emitter location inference
- no sensitive coordinates

## 2026-07-04 Implementation Status

- v0.6 public prototype is deployed as `S-DOT Edge Semantic Ops`.
- Dataset id: `s_dot_drone_semantic_ops_mock_v0_6`.
- Dataset includes 5 simulation cases, 3 synthetic assets, 6 semantic events, and 6 semantic packets.
- Dataset includes `algorithm_basis` and `case_evaluations` for explainable scoring.
- Dataset includes `case_evaluation_series` with 13 time points per case for residual, NIS, uncertainty, and hypothesis-score trend rendering.
- Dataset includes `kalman_estimator_traces` with 13 time points per case for prediction/update/gate decisions.
- UI now filters semantic events and packets by selected case.
- UI includes an algorithm evaluation panel with max residual, max NIS, thresholds, detection latency, false alarm risk, confidence, operator decision, and semantic transmission policy.
- UI includes a normalized trend chart and jumps each non-normal case to the first meaningful degraded/watch/critical point.
- UI includes a Kalman-style estimator comparison showing innovation NIS, gate threshold, measurement sigma, 2-sigma position uncertainty, reported-position error, and estimate error.
- UI copy is Korean-first for case summaries, asset labels, evidence cards, and packet tiers.
- Palantir/AIP handoff bundle generated at `07_deliverables/palantir/sdot_drone_semantic_ops` with 12 object tables, 225 relationship links, 4 action definitions, and 3 AIP workflow cards.
- Public Playwright verification passed for desktop rendering and all 5 case switches.
- Current algorithm is intentionally explainable: synthetic kinematics, constant-velocity Kalman-style innovation gating, uncertainty growth, residual/NIS-style integrity indicators, defensive hypothesis scoring, and raw-vs-semantic byte comparison.

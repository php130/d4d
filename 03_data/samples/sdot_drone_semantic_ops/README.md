# S-DOT Drone Semantic Ops Dataset

Dataset framework for the revised S-DOT direction.

## Why This Exists

The previous demo dataset focused on a command COP for synthetic ground units in Seoul. That work is still useful as a receiving/decision layer, but the S-DOT problem statement is better framed around drones, robots, sensors, high-volume raw data, denied networks, and semantic transmission.

This folder defines the new dataset direction:

- drone/sensor assets
- predicted flight state
- GNSS/link degradation
- jamming or spoofing hypotheses
- raw observation references
- edge detections
- semantic events
- semantic packets
- custody/provenance chain
- rejoin audit

## Files

- `dataset_framework_v0_1.json`: target framework and sample objects for v0.6 dataset generation.
- `mock_dataset.json`: generated v0.6 synthetic drone S-DOT dataset.
- `mock_dataset.js`: browser-ready copy exposing `window.__D4D_DRONE_SDOT_DATASET`.

## Current Status

This is the active drone-first dataset track for the v0.6 public prototype.

Current live app:

- `/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops`
- dataset id: `s_dot_drone_semantic_ops_mock_v0_6`
- user-facing product: `S-DOT Edge Semantic Ops`

Generated v0.6 summary:

- 5 simulation cases
- 3 synthetic drone/sensor assets
- 6 semantic events
- 6 semantic packets
- case-specific event and packet filtering through `case_ids`
- `algorithm_basis` for the explainable prediction, uncertainty, residual/NIS, and hypothesis score models
- `case_evaluations` for max residual, max NIS, detection latency, false alarm risk, confidence, operator decision, and semantic transmission policy
- `case_evaluation_series` for normalized residual, NIS, uncertainty, and hypothesis score over time
- `kalman_estimator_traces` for constant-velocity Kalman-style prediction/update/gate decisions
- Palantir/AIP handoff bundle under `07_deliverables/palantir/sdot_drone_semantic_ops`
- `platform_handoff` summary for the public UI handoff panel
- main case: GNSS/link degradation with `JAMMING_SUSPECTED`
- NIS/residual and jamming hypothesis score included

## Direction Change

Old protagonist:

- human/ground unit under intermittent contact
- command room trying to preserve mission continuity

New protagonist:

- drone/robot/sensor node under GNSS/link degradation
- edge system trying to convert raw data into semantic packets
- command room seeing predicted position, uncertainty, link/GNSS health, and evidence trace

## What To Keep From The Old Dataset

Keep:

- `network_modes`
- `pace_bearer_ladder`
- `routing_results` concept
- `semantic_events` concept
- `sdot_messages` concept, renamed to `semantic_packets`
- `rejoin_audit` concept
- `korea_civil_infra_context` as optional public background
- current Korean-first UI copy style

Use only as optional context:

- `operation_objective`
- `mission_intent`
- `support_options`
- `unit_nodes`

Remove from primary storyline:

- adversary route assessment
- human unit branch tracking
- maritime vessel/track leftovers

## Scientific / Algorithmic Basis

The demo should be based on simple but explainable calculations:

- constant velocity or constant acceleration prediction
- wind-adjusted drift
- uncertainty growth over time
- Kalman/EKF-style prediction and measurement residual
- Normalized Innovation Squared (NIS)
- constant-velocity Kalman-style innovation gate
- GNSS/link degradation score
- defensive jamming hypothesis score
- spoofing-like position integrity hypothesis
- normalized time-series trend chart for operator explainability
- semantic compression ratio
- packet survival by DDIL mode
- rejoin audit discrepancy

## Minimal v0.6 Scenario

Case C should be the main hackathon demo:

1. `UAV-S1` flies a synthetic route.
2. Command link becomes intermittent.
3. GNSS quality drops.
4. Physics prediction continues but uncertainty expands.
5. A received or simulated position update diverges from the prediction.
6. NIS/residual threshold is exceeded.
7. System raises `JAMMING_SUSPECTED` as a hypothesis.
8. Raw EO/IR is held locally.
9. S-DOT sends only a `NAV_HEALTH_CARD`.
10. Rejoin audit later compares cached raw state against the semantic prediction.

## Safety

The dataset must remain synthetic. Do not include real drone routes, military assets, EW emitter details, or sensitive infrastructure coordinates.

## Public Demo Verification

The v0.6 public demo currently verifies:

- WebGL 3D drone scene
- case-specific event and packet filtering
- algorithm evaluation trend chart
- Kalman-style estimator comparison
- Foundry/AIP handoff panel with 12 object tables, 225 relationship links, 4 actions, and 3 workflow cards

Screenshot:

- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_handoff_public.png`

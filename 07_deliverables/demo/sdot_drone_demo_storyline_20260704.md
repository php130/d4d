# S-DOT Drone Demo Storyline

Date: 2026-07-04 KST

Public demo: https://bench-coverage-saving-membrane.trycloudflare.com

## One-Line Framing

S-DOT is a semantic transmission and navigation-integrity layer for unmanned assets operating under degraded, intermittent, or denied networks.

It is not an autopilot, not an offensive EW tool, and not proof of jamming. It preserves mission-relevant meaning, uncertainty, evidence, and auditability when raw sensor feeds cannot move reliably.

## Demo Narrative

Use the case selector from top to bottom.

1. Normal mission
   - Show planned, predicted, and reported tracks are close.
   - Explain that S-DOT does not transmit everything. It decides whether a status summary is worth sending under the selected network mode.

2. Link degradation
   - Switch to the link degradation case.
   - Point to the packet inspector: raw payload is large, but a small semantic packet can survive constrained bandwidth.
   - Message: "When the video feed cannot move, the command room still receives health, position confidence, and recommended handling."

3. GNSS jamming suspected
   - Switch to the GNSS degradation case.
   - Point to uncertainty growth, residual/NIS-style indicators, the Kalman estimator comparison, the algorithm evaluation trend chart, and the evidence chain.
   - Message: "The system does not claim jamming as fact. It raises a defensive hypothesis because predicted motion, reported GNSS, link health, and sensor evidence no longer agree."

4. Spoofing-like inconsistency
   - Switch to the spoofing-like case.
   - Emphasize the separation between reported position and predicted/physics-consistent state.
   - Message: "A clean-looking position can still be suspicious if it violates the asset's recent motion, IMU-like continuity, or sensor cross-check."

5. Rejoin audit
   - Switch to the rejoin audit case.
   - Explain that after reconnection, cached raw observations and semantic predictions are compared.
   - Message: "The value is not only real-time survival. It also gives a record of what was believed, why it was believed, and what changed after reconnection."

## What Judges Should Understand

- S-DOT reduces communication load by sending task-relevant semantic packets instead of raw sensor feeds.
- The core screen is a drone operator and command-room view, not a human unit tracking COP.
- The algorithmic basis is explainable: kinematic prediction, Kalman-style innovation gating, uncertainty growth, residual/NIS-style checks, link/GNSS health, packet priority, and rejoin audit.
- The output is decision support: confidence, uncertainty, false alarm risk, trend over time, evidence chain, packet decision, and recommended operator action.
- The same demo state can be mapped into a Foundry/AIP-style operating layer through the handoff bundle: assets, events, packets, hypotheses, trace points, routing decisions, and approval/audit actions.

## Safe Technical Boundary

All data is synthetic.

The demo avoids:

- real drone routes
- real military positions
- real emitter geolocation
- offensive jamming methods
- sensitive infrastructure coordinates

The phrase "jamming suspected" must be presented as a hypothesis score, not a confirmed attribution.

## Recommended 90-Second Script

"This is S-DOT, Semantic Data On Tactical-network. We reframed the project around unmanned systems because the problem statement is about sending only mission-critical meaning when tactical networks are degraded.

In the normal case, the drone track and reported position are aligned. When the link degrades, raw feeds become expensive or impossible to move, so S-DOT routes compact semantic packets: asset health, confidence, uncertainty, and evidence references.

In the GNSS degradation case, the operator sees that the reported position and predicted motion are diverging. The Kalman-style estimator compares the reported position against the predicted covariance and gates out a measurement when the innovation NIS exceeds the threshold. The trend chart shows residual, NIS, uncertainty, and hypothesis score moving together. The system does not assert jamming. It shows a defensive hypothesis score based on residuals, NIS-style indicators, link health, supporting observations, and false-alarm risk.

In the spoofing-like case, the reported position can look clean, but it conflicts with physics-consistent movement and cross-sensor evidence. That difference is what the command room needs to understand.

Finally, after reconnection, S-DOT performs a rejoin audit. It compares what the edge believed during disconnection against what actually arrived later. The result is a command continuity layer for drones: less raw data, more relevant meaning, uncertainty, provenance, and accountability."

## Palantir/AIP Handoff

Use the bottom `Foundry / AIP 연결 준비` panel when explaining how this demo would move into an operational platform. The panel is intentionally not a fake Palantir screen. It is a safe handoff summary showing what would become ontology objects, relationships, actions, and workflow cards.

- Path: `/Users/mollykim/projects/D4D/07_deliverables/palantir/sdot_drone_semantic_ops`
- Object tables: `DroneAsset`, `SimulationCase`, `SemanticEvent`, `SemanticPacket`, `RawObservation`, `EdgeDetection`, `JammingHypothesis`, `CaseEvaluation`, `CaseEvaluationPoint`, `KalmanTracePoint`, `RoutingDecision`, `RejoinAudit`
- Actions: approve semantic packet, mark measurement contested, request rejoin audit, change DDIL mode
- AIP workflow cards: operator summary, packet priority review, rejoin audit assistant
- Guardrail: this is not an official Palantir import spec. Actual Foundry ingestion should be mapped inside the hackathon tenant workflow.

## Next Build

- Extend the current constant-velocity Kalman filter into a nonlinear EKF/UKF variant.
- Calibrate wind and sensor-noise parameters against one public UAV dataset.
- Extend the evaluator with audit discrepancy and byte-savings charts.
- Convert the current handoff bundle into a Foundry-specific import pipeline if the hackathon tenant workflow allows it.

# S-DOT Drone Palantir/AIP Handoff Bundle

- Generated: 2026-07-04T08:34:23.352000+00:00
- Source dataset: `s_dot_drone_semantic_ops_mock_v0_6`
- Status: synthetic hackathon demo handoff bundle

## Purpose

This bundle maps the S-DOT drone demo into object tables, relationship links, action definitions, and AIP workflow cards.

It is intended for Foundry Ontology/AIP planning, transform prototyping, or any graph-backed C2 workflow. It is not an official Palantir import specification.

## Contents

- `objects/*.csv`: object tables for assets, cases, semantic events, packets, observations, hypotheses, Kalman trace points, routing decisions, and audits
- `links.csv`: graph-style object relationships
- `ontology_model.json`: proposed object/relationship/action model
- `aip_workflow_cards.json`: AIP assistant workflow cards and guardrails
- `bundle_manifest.json`: record counts and file hashes

## Object Tables

- `objects/DroneAsset.csv`: 3 records
- `objects/SimulationCase.csv`: 5 records
- `objects/SemanticEvent.csv`: 6 records
- `objects/SemanticPacket.csv`: 6 records
- `objects/RawObservation.csv`: 7 records
- `objects/EdgeDetection.csv`: 2 records
- `objects/JammingHypothesis.csv`: 2 records
- `objects/CaseEvaluation.csv`: 5 records
- `objects/CaseEvaluationPoint.csv`: 65 records
- `objects/KalmanTracePoint.csv`: 65 records
- `objects/RoutingDecision.csv`: 30 records
- `objects/RejoinAudit.csv`: 1 records

## Safety Boundary

Synthetic drone flight, GNSS/link degradation, jamming hypothesis, and semantic packet data. No real routes, force posture, EW emitter data, or sensitive coordinates.

Do not connect this bundle to real military routes, real EW emitter details, sensitive infrastructure coordinates, or personal data.

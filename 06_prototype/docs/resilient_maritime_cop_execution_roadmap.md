# Resilient Maritime COP Execution Roadmap

- Date: 2026-07-04 KST
- Purpose: turn research into hackathon deliverables
- Topic: T3 semantic COP / S-DOT-style maritime situation updates under denied networks

## North Star

Build a demo that proves one idea:

> Even when raw data and networks degrade, the commander-facing COP can preserve mission-relevant meaning, evidence, and trust.

This should not look like a generic maritime dashboard or generic chatbot. It should look like a C2/Battle Network prototype.

## Deliverable Stack

| Layer | Deliverable | Success criterion |
|---|---|---|
| Research base | literature synthesis and source/API plan | claims have evidence strength and caveats |
| Data contract | semantic event schema | live and mock sources can produce same event shape |
| Dataset | mock dataset with source rationale | demo runs without API keys |
| Routing | network-aware priority packets | mode change visibly changes send/defer/drop behavior |
| COP UI | map, queue, evidence, briefing | operator can answer "what matters and why" |
| Report | non-technical HTML explainer | user can explain the project to others |

## Roadmap

### Phase 0. Coordination and Safety

Status: complete for current prototype pass.

Tasks:

- Separate API-key work from prototype work.
- Do not expose `.env` values.
- Keep all demo data synthetic or redacted.
- Make the app run without live API dependencies.

Evidence:

- `/Users/mollykim/projects/D4D/00_admin/workstream_coordination.md`
- `/Users/mollykim/projects/D4D/08_ops/security_compliance/osint_ethics.md`

### Phase 1. Event Spine

Status: complete as mock implementation.

Tasks:

- Define `semantic_event` shape.
- Define source-to-event adapter pattern.
- Create mock AIS/SAR/weather/OSINT/network records.
- Validate every event has evidence refs.

Success criteria:

- `mock_dataset.json` parses.
- every event has evidence;
- every packet references an event;
- app can run from local server.

### Phase 2. MVP Demo

Status: implemented.

Tasks:

- COP map with event markers.
- network mode controls.
- priority event queue.
- evidence drawer.
- raw vs semantic byte comparison.
- grounded briefing.

Success criteria:

- changing network mode changes routing decisions;
- `semantic_summary` preserves only high-priority messages;
- `local_only` holds all messages locally;
- UI shows why an alert exists.

### Phase 3. First Live Connector

Recommended next step.

Pick one connector that has high demo value and low integration risk.

Recommended order:

1. KMA/weather connector -> `WEATHER_HAZARD`
2. GDELT connector -> `OSINT_INCIDENT`
3. data.go.kr AIS/port connector -> `AIS_GAP` or `PORT_ANOMALY`
4. VWorld/OSM context connector -> port/AOI geometry
5. GFW/Copernicus connector -> SAR or dark-vessel context

Why this order:

- weather and OSINT are easiest to turn into safe semantic events;
- AIS and SAR are more domain-central but may have access, format, and redistribution constraints;
- map/context data improves visual credibility but should not dominate the demo.

### Phase 4. Evaluation Pack

Add quantitative claims the judges can understand.

Metrics:

- `bytes_saved_pct_vs_full_feed`
- `message_survival_rate`
- `mission_message_throughput`
- `trace_completeness`
- `cop_freshness`
- `sync_recovery_time`
- `operator_triage_time`

Minimum evaluation:

- compare `full_sync`, `semantic_summary`, `store_forward`, and `local_only`;
- show which high-priority event survives;
- show how much raw data was represented by a compact alert card.

### Phase 5. Platform Mapping

If Palantir AIP is available:

- map `Vessel`, `Track`, `Observation`, `Event`, `Alert`, `EvidenceBundle`, `NetworkState`, `TrustState` into ontology objects;
- implement event extraction as Functions/Logic;
- implement "mark suspicious", "confirm identity", "request ISR", "publish semantic update" as object actions;
- use AIP Assist only as a grounded briefing layer over ontology objects.

If AIP is not available:

- use JSON/PostGIS-style records;
- keep event schema stable;
- simulate ontology relationships in the app.

## Specialized Research Still Needed

### 1. DDIL and Tactical Edge Networking

Research questions:

- How do C2 systems degrade under disconnected/intermittent/limited networks?
- What is a defensible application-layer abstraction without touching classified tactical links?
- How should store-forward and stale-data warnings be represented?

Needed output:

- 1-page DDIL design note;
- network mode thresholds for the demo;
- wording that avoids overclaiming tactical protocol fidelity.

### 2. AIS/SAR Fusion and Dark Vessel Triage

Research questions:

- What counts as AIS absence, AIS silence, spoofing, or coverage gap?
- How do SAR detection, AIS gate matching, and trajectory feasibility combine?
- How should the UI distinguish "review candidate" from "confirmed threat"?

Needed output:

- AIS/SAR event rules;
- false-positive caveats;
- dark-vessel evidence taxonomy.

### 3. Trust and Provenance

Research questions:

- How do we score source trust and track trust separately?
- How do we keep contradictory reports visible?
- How do we prevent LLM summaries from pretending citations are stronger than they are?

Needed output:

- trust score v0 formula;
- evidence bundle schema v0.2;
- briefing citation policy.

### 4. Semantic Communication Metrics

Research questions:

- What is the right metric if packet delivery is not the goal?
- How do we measure "meaning survived" without pretending it is a military-certified metric?

Needed output:

- `mission_message_throughput` definition;
- semantic payload tiers;
- raw-vs-semantic comparison table.

### 5. Palantir AIP Implementation Pattern

Research questions:

- Which parts should be ontology objects, functions, actions, and AIP Assist prompts?
- How can the demo avoid becoming just a chatbot?

Needed output:

- AIP object model diagram;
- object action list;
- function signatures for extraction/routing.

## Hackathon Storyline

1. Normal AIS track appears.
2. Network begins degrading.
3. AIS goes stale.
4. SAR-like detection appears without AIS match.
5. Weather reduces visual confirmation confidence.
6. A contradictory low-trust report arrives.
7. System sends only the composite alert card under semantic-summary mode.
8. Judge sees evidence, trust, and byte savings.

## Decision

Continue with T3 as the primary track.

Use T4 maritime data as the domain, but keep the differentiator in:

- semantic event extraction;
- priority routing;
- degraded network behavior;
- evidence and trust;
- commander-facing COP update.


# S-DOT Mission Continuity COP Plan

- Version: `20260704_ks`
- Problem name: `S-DOT 시맨틱 전송 | Semantic Data On Tactical-network`
- Product subtitle: `Mission Continuity COP for Isolated / DDIL Units`
- Track fit: T3 Battle Network, C2, Maritime Domain Awareness & Sustainment
- Current status: concept freeze and implementation planning
- Safety boundary: defensive C2 resilience, decision support, sustainment visibility, and semantic data transmission. No real unit locations, classified procedures, offensive targeting logic, or unauthorized network access.

## 1. Current Project Audit

### Existing Assets To Reuse

| Area | Existing project asset | Reuse decision |
| --- | --- | --- |
| T3 problem framing | `01_research/literature/t3_deep_research/architecture_options.md` | Keep. Reframe from maritime-only COP to S-DOT Mission Continuity COP. |
| Technical design | `06_prototype/docs/resilient_maritime_cop_technical_design.md` | Keep as v0.1 architecture. Extend objects from vessel-centric to unit/resource-centric. |
| Schema | `05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md` | Reuse `Observation`, `EvidenceBundle`, `Event`, `Alert`, `NetworkState`, `MissionContext`; add unit/resource objects. |
| DDIL research | `01_research/literature/t3_deep_research/ddil_isolated_tactical_research_20260704.md` | Core theory for isolation mode, PACE, DTN, store-forward, local COP. |
| Strategy/resource theory | `01_research/literature/t3_deep_research/strategy_tactics_resource_allocation_theory_20260704.md` | Core theory for C2 modes, COA cards, priority engine, sustainment forecast. |
| Contemporary conflict lessons | `01_research/literature/t3_deep_research/contemporary_conflict_lessons_for_isolated_units_20260704.md` | Use for pitch evidence: comms/GPS disruption, energy, logistics, IAMD/COP. |
| API/data matrix | `06_prototype/docs/data_api_integration_matrix_20260704.md` | Keep. Split live context data vs synthetic tactical data. |
| Current demo | `06_prototype/app/resilient_maritime_cop/` | Keep deployed prototype as UI/code base; evolve into command-center Mission Continuity board. |
| Current public URL | `07_deliverables/demo/public_deployment_20260704.md` | Keep as current external demo link and deployment runbook. |

### Existing Data/API Status

| Status | Source | Use In New Topic |
| --- | --- | --- |
| Passed | data.go.kr weather / KMA | weather hazard, route risk, sensor reliability |
| Passed | KMA APIHub sea forecast | maritime/coastal operating context |
| Passed | Open-Meteo Marine | fallback wave/sea-state |
| Passed | VWorld | geocoding, map context, infrastructure coordinates |
| Passed | Copernicus Sentinel-1 catalogue | satellite scene availability evidence, not ship detection by itself |
| Passed | NASA CMR | Earth/ocean collection discovery |
| Passed | OpenSanctions | optional entity risk-screening workflow with synthetic/redacted entities |
| Passed | Global Fishing Watch | vessel presence/context; not a threat label |
| Rate-limited | GDELT maritime | OSINT context with cache/backoff |
| Pending | SafetyData disaster messages | disaster/official alert context after approval |
| Existing datasets | Ukraine OSINT package, OSM critical infrastructure, weather, UCDP/GDELT | research/pitch evidence and optional scenario generation, not direct Korea tactical data |

### Main Gaps

The current project is strong on maritime COP and semantic transmission, but the new topic needs additional layers:

- `UnitNode`: isolated/intermittent units and local state.
- `IntentPacket`: commander/staff objective, priority, constraints, thresholds.
- `PredictedLocalCOP`: estimated route, mission phase, uncertainty, confidence decay.
- `ResourceGraph`: support units, hospitals, comm relays, power, fuel, medical, logistics.
- `CivilCommsInfrastructure`: commercial/PS-LTE/LTE-M/LTE-R/SATCOM/AP/backhaul assets as possible bearers.
- `SdotMessage`: semantic command/status/support packets with payload tiers.
- `AllocationEngine`: bandwidth, power, support route, nearby resource allocation.
- `RejoinAudit`: compare prediction vs actual local sync after reconnect.

## 2. Final Problem Framing

### Problem Statement

> In tactical DDIL environments, units and command rooms cannot rely on continuous raw data exchange. Build an S-DOT system that converts commands, local observations, resource states, and support needs into mission-relevant semantic packets so isolated units can continue decision-making and headquarters can maintain a predicted, uncertainty-aware COP until reconnection.

### Korean Pitch

> 통신 단절/거부 환경에서는 원본 영상, 센서 로그, 세부 보고가 모두 오가지 못한다. S-DOT은 원본 데이터를 억지로 보내는 대신 작전 의도, 우선순위, 핵심 상황 변화, 자원 요청, 위치 불확실성을 의미 단위로 압축해 전송하고, 통신이 끊긴 동안에도 사령부가 부대의 예상 상황과 지원 우선순위를 유지하도록 돕는 Mission Continuity COP이다.

### What We Are Building

Not:

- real military tactical data link clone
- autonomous command/targeting system
- real unit tracking system
- unauthorized use of civilian networks

But:

- semantic transmission layer
- degraded-network decision-support COP
- isolated-unit predicted state board
- resource/support allocation simulator
- Palantir-compatible ontology and workflow prototype

## 3. Three-Layer Product Model

### Layer 1. Unit / Edge Layer

The unit operates under commander intent but adapts tactically as the environment changes.

Objects:

- `UnitNode`
- `LocalCOPState`
- `ReadinessState`
- `LocalEventLog`
- `SdotOutbox`
- `SyncBundle`
- `PacePlan`

Core functions:

- maintain local COP when disconnected
- receive compressed `IntentPacket`
- create semantic status/support messages
- queue high-value sync bundles
- log evidence for later audit
- degrade payloads based on bandwidth and power

Demo states:

- `connected`
- `degraded`
- `intermittent`
- `isolated`
- `rejoin`

### Layer 2. Infrastructure / Deployment / Resource Layer

This layer models what resources can help the unit continue the mission.

Objects:

- `NetworkAsset`: 5G/LTE, PS-LTE, LTE-M, satellite, wired backhaul, AP, relay, mobile base station
- `InfrastructureNode`: port, road node, bridge, power node, hospital, shelter, logistics hub
- `SupportUnit`: medical, communications relay, logistics, evacuation, engineering
- `ResourcePackage`: battery, fuel, medical, water, food, repair kit, comms kit
- `RouteOption`: route, risk, travel time, road/weather status, comm coverage

Core functions:

- estimate connectivity options around a unit
- find support routes and fallback routes
- forecast power/supply exhaustion
- recommend support priority, not automated command
- show what is blocked by weather, infrastructure damage, bandwidth, or risk

### Layer 3. Command / Staff Situation Room

Command and staff need an uncertainty-aware view, not false real-time certainty.

Objects:

- `MissionIntent`
- `StaffDecision`
- `PredictedUnitState`
- `BranchScenario`
- `COACard`
- `SdotMessageQueue`
- `RejoinAudit`

Core functions:

- view confirmed vs predicted local COP
- send semantic mission updates
- prioritize which messages survive low bandwidth
- compare branch scenarios
- allocate support resources
- review what actually happened after rejoin

## 4. S-DOT Message Design

### Payload Tiers

| Tier | Network condition | Payload | Example |
| --- | --- | --- | --- |
| T0 Raw | healthy | raw tracks, imagery, full evidence | map tiles, images, logs |
| T1 Delta | degraded | changed fields only | route delta, readiness delta |
| T2 Semantic | low bandwidth | compact meaning packet | "Unit A likely in Phase 2, power 42%, needs relay" |
| T3 Priority Card | intermittent | top-priority alert/status only | intent update, medevac/support request, critical route block |
| T4 Store-forward | disconnected | queued bundle | evidence digest, local event log, sync bundle |
| T5 Local-only | fully isolated | no transmission | local COP and audit log only |

### Message Families

| Message | Sent by | Purpose |
| --- | --- | --- |
| `IntentUpdate` | HQ/staff | mission objective, priority weights, constraints, valid-until |
| `SituationDelta` | unit or sensor node | important change from local COP |
| `ReadinessSnapshot` | unit | power, supply, medical, equipment, personnel readiness as safe aggregate |
| `SupportRequest` | unit | needed resource type, urgency, time window, route constraints |
| `RouteRiskUpdate` | HQ or infrastructure layer | route block, weather, comm coverage, support feasibility |
| `NetworkStateUpdate` | network/infrastructure layer | bearer quality, outage, next contact window |
| `BranchScenario` | HQ/staff | likely future state A/B/C with confidence and assumptions |
| `RejoinBundle` | unit | local event log and evidence digest after reconnect |

### Priority Score

Initial hackathon scoring:

```text
sdot_priority =
  decision_impact
  * urgency
  * intent_relevance
  * confidence
  * freshness
  / (payload_bytes + power_cost + expected_delay)
```

Use this for:

- message queue ordering
- payload tier selection
- support request ordering
- rejoin sync ordering

## 5. Predicted Local COP

The command room should not claim to know an isolated unit's live position. It should show:

- last confirmed state
- predicted state
- uncertainty envelope
- confidence decay
- likely mission phase
- branch scenarios
- data gaps and assumptions

### Minimal Prediction Model

```text
predicted_state =
  last_confirmed_state
  + mission_plan
  + elapsed_time
  + movement constraints
  + terrain/weather effects
  + readiness/power constraints
  + communications contact probability
```

### UI Rule

Confirmed and predicted layers must be visually distinct:

- confirmed: solid marker
- predicted: translucent marker
- uncertainty: expanding halo/corridor
- stale risk: color/age badge
- unknown: explicit "not observed by HQ since last sync"

## 6. Resource Allocation And Support Planning

This is where the idea becomes larger than a COP.

### Allocation Targets

- bandwidth/contact-window allocation
- battery/power use
- sensor use
- support route selection
- nearby support unit positioning
- hospital/medical support route
- mobile comms relay or temporary base-station placement
- resupply timing and route

### Hackathon-Safe Optimizer

Use decision support, not automated military tasking.

```text
support_score =
  mission_value
  + urgency
  + unit_readiness_risk
  + route_feasibility
  + comms_restoration_value
  - travel_time
  - resource_cost
  - uncertainty_penalty
```

### First MVP Outputs

- top 3 support options
- route risk heat
- expected time to support
- bandwidth/power tradeoff
- why each option is recommended
- what data is missing

## 7. Korea Dense Infrastructure Hypothesis

### Hypothesis

Korea has dense wired, wireless, mobile, public-safety, maritime, rail, and building communications infrastructure. In a wartime or national emergency scenario, this could theoretically reduce tactical isolation if military/public authorities have legal authority, prearranged agreements, secure authentication, priority policies, power/backhaul resilience, and an orchestration layer.

### What Public Sources Support

- `전기통신사업법 제66조` provides a public legal basis for emergency securing of communications in national emergency contexts, including orders involving private telecommunications facilities and interconnection.
- `재난 및 안전관리 기본법 제34조의2` requires disaster-management institutions to prepare emergency communication means using wired, wireless, or satellite networks when disaster-site communications are cut.
- `재난안전통신망(PS-LTE)` is described by MOIS as a nationwide public-safety wireless network for police, fire, coast guard, and disaster-related agencies.
- National integrated public networks include PS-LTE, maritime LTE-M, and rail LTE-R; MOF notes the need for interoperation and resource sharing under disaster conditions.
- Public datasets exist for some communications infrastructure, such as KCA mountain-area mobile station data and wireless-station statistics.

### What This Does Not Mean

It does not mean the military can simply use every private AP/router/base station on demand without:

- statutory authority or emergency order
- prearranged agreements with operators/building owners
- device authentication and SIM/eSIM provisioning
- encryption and traffic separation
- priority/QoS configuration
- power and backhaul survivability
- privacy and lawful-use controls
- cyber hardening and auditing

### Product Translation

Model civilian/public infrastructure as candidate bearers, not as guaranteed connectivity.

`CivilCommsAsset` fields:

```json
{
  "asset_id": "civil_comms_001",
  "bearer_type": "5G|LTE|PS-LTE|LTE-M|wired|satcom|wifi_ap|mobile_relay",
  "owner_type": "telco|public_safety|maritime|rail|building|military",
  "legal_status": "preauthorized|emergency_order_required|not_available|unknown",
  "coverage_area": "geojson-or-radius",
  "power_state": "grid|backup|battery|unknown",
  "backhaul_state": "fiber|microwave|satellite|unknown|degraded",
  "auth_required": true,
  "priority_capable": true,
  "estimated_bandwidth_kbps": 256,
  "confidence": 0.62
}
```

Demo concept:

> "Korea Infrastructure Opportunistic Continuity Layer"  
> 사전 승인된 민간/공공 통신자원을 후보 bearer로 모델링하고, 각 자원의 법적 사용 가능성, 전력, 백홀, 보안, 커버리지, 신뢰도를 고려해 S-DOT 메시지가 이동할 가능성이 높은 경로를 추천한다.

## 8. Palantir Dev Tier vs Separate Development

### Use Palantir For

| Capability | Why Palantir fits |
| --- | --- |
| Data integration and normalization | files, CSV/JSON/API snapshots, geospatial/context data |
| Ontology | `UnitNode`, `MissionIntent`, `NetworkAsset`, `SupportUnit`, `SdotMessage`, `Alert`, `RejoinAudit` |
| Object relationships | unit assigned to mission, support unit can assist unit, route affected by hazard, message cites evidence |
| Workshop COP | map, alert inbox, object views, metrics |
| AIP Analyst / AIP Logic | citation-backed briefs, message classification, object updates, explanation generation |
| Human-in-the-loop actions | mark reviewed, approve intent update, assign support analysis, resolve conflict |
| Governance/audit | provenance, access control, action logs, safer demo story |

### Build Separately

| Capability | Why separate development is safer/faster |
| --- | --- |
| S-DOT priority/routing simulator | custom algorithm and UI iteration speed |
| Network degradation simulator | synthetic DDIL modes, contact windows, bandwidth/power tradeoff |
| Predicted local COP visualization | custom uncertainty envelope/corridor and animation |
| Resource allocation optimizer | custom scoring, route selection, support option ranking |
| Local/offline edge-unit mock | browser/local-first behavior, store-forward demo |
| Public web demo | external viewer access via local-deployer/Cloudflare without tenant permissions |
| API connector experiments | easier to test with `.env`, rate limits, snapshots, no platform permission blockers |

### Recommended Hybrid

1. Keep the local app as the polished public demo.
2. Build the data model so it is Palantir-compatible.
3. Create a Palantir import package from synthetic/public-safe CSV/JSON.
4. If Dev Tier access is stable, build an Ontology + Workshop mini-demo:
   - `UnitNode`
   - `NetworkAsset`
   - `SdotMessage`
   - `SupportOption`
   - `Alert`
   - `RejoinAudit`
5. Use AIP Logic for a narrow, safe function:
   - "Summarize current isolated-unit state with citations."
   - "Classify which S-DOT messages should be sent first."
   - "Explain why this support option is ranked #1."

Fallback if Palantir is blocked:

- local prototype still works;
- present Palantir-compatible ontology and CSV import design;
- show screenshots/notes from existing Foundry walkthrough as feasibility evidence.

## 9. Data Plan

### Use Now

| Data | Source | Role |
| --- | --- | --- |
| weather/sea state | KMA, data.go.kr, Open-Meteo | route/sensor/support risk |
| map/geocoding | VWorld, OSM/Overpass | AOI, infrastructure, routes |
| satellite availability | Copernicus catalogue, NASA CMR | "satellite data could be available" evidence |
| vessel/maritime context | GFW, synthetic AIS/SAR | maritime scenario continuity |
| public event context | GDELT cached, official notices | OSINT context |
| risk-screen context | OpenSanctions with synthetic entities | optional intelligence card |

### Collect Next

| Priority | Data | Candidate source | Purpose |
| --- | --- | --- | --- |
| P0 | Korean mobile/wireless infrastructure proxy | KCA mountain-area mobile station API, Spectrum Map, Seoul wireless station stats | civil comms asset layer |
| P0 | Hospitals/emergency medical facilities | public data portals / emergency medical institution datasets | support route/resource layer |
| P0 | Roads/routes/bridges | OSM Overpass, VWorld, public road datasets | route feasibility |
| P0 | Power/critical infrastructure proxies | OSM, public facility datasets | power/backhaul risk context |
| P1 | PS-LTE/LTE-M/LTE-R public docs and static references | MOIS, MOF, public-network policy docs | Korean infrastructure story |
| P1 | Internet outage/baseline | Cloudflare Radar, CAIDA IODA, RIPE Atlas, Ookla | network degradation context |
| P1 | Disaster alerts | SafetyData after approval, GDACS/EONET/USGS fallback | hazard/context layer |
| P2 | Satellite imagery/detection samples | xView3, Copernicus sample products | visual evidence layer |

### Keep Synthetic

| Synthetic item | Why |
| --- | --- |
| unit locations and movement | real unit data is sensitive |
| unit mission details | operationally sensitive |
| tactical comms state | real network/jamming data is unavailable/sensitive |
| support unit positioning | operationally sensitive |
| medical/resource capacities under war | should not be real or exact |
| commander decision thresholds | sensitive |
| hostile/threat labels | cannot safely infer from public data |

## 10. MVP Scenario

Use a synthetic Korea-adjacent coastal/island training AOI, not a real unit location.

1. HQ creates `MissionIntent`: maintain local awareness, preserve unit continuity, prioritize medical/power/comms support.
2. Unit A is operating with a local COP.
3. Network degrades from 5G/public bearer to low-bandwidth satellite/relay and then intermittent contact.
4. S-DOT changes payload tier: raw -> delta -> semantic card -> store-forward.
5. HQ shows confirmed last state and predicted local COP.
6. Unit generates `ReadinessSnapshot` and `SupportRequest`.
7. Infrastructure layer ranks support routes and candidate comms bearers.
8. Brief contact window opens; priority message queue sends top packets first.
9. Rejoin audit compares predicted route/state with actual local bundle.

## 11. Implementation Roadmap

### Phase 0. Freeze Concept

Deliverables:

- this plan
- one-page problem statement
- product name and pitch sentence

Decision:

- Main name: `S-DOT 시맨틱 전송`
- Product demo: `Mission Continuity COP`

### Phase 1. Schema And Dataset v0.2

Create:

- `UnitNode`
- `MissionIntent`
- `LocalCOPState`
- `PredictedUnitState`
- `NetworkAsset`
- `CivilCommsAsset`
- `SupportUnit`
- `ResourcePackage`
- `RouteOption`
- `SdotMessage`
- `SyncBundle`
- `RejoinAudit`

Use:

- current mock maritime dataset as source pattern
- synthetic unit/resource data
- live-safe weather/geocode/context snapshots

### Phase 2. S-DOT Engine

Build:

- payload tier selector
- message priority score
- queue simulator
- bytes saved / mission value retained metrics
- store-forward and contact-window behavior

### Phase 3. Command Board UI

Extend current demo:

- central map remains dominant
- add unit layer
- add confirmed vs predicted position
- add infrastructure/resource layer
- add S-DOT queue
- add C2 mode manager
- add support option ranking
- add rejoin audit timeline

### Phase 4. Palantir Track

If Dev Tier access is stable:

- create/import synthetic-safe datasets
- build ontology
- build Workshop object views
- add alert inbox
- use AIP Logic for brief/ranking explanation

If not stable:

- produce Palantir-compatible import package and ontology design
- continue local app.

### Phase 5. Pitch And Evaluation

Metrics:

- `mission_message_delivery`
- `semantic_compression_ratio`
- `decision_value_retained`
- `cop_freshness`
- `prediction_confidence_decay`
- `support_response_time`
- `sync_recovery_time`
- `evidence_trace_completeness`

## 12. Immediate Next Actions

1. Update current prototype dataset from maritime-only to mission-continuity v0.2.
2. Add `UnitNode`, `MissionIntent`, `SdotMessage`, `SupportOption`, `CivilCommsAsset` schema.
3. Add a new scenario script for isolated unit + support allocation.
4. Implement S-DOT priority queue and payload-tier comparison.
5. Add predicted local COP layer to map.
6. Add infrastructure/resource panel.
7. Prepare Palantir import CSV/JSON package.
8. Decide whether to build Foundry Workshop version or keep Palantir as ontology/AIP evidence layer.

## 13. Source References

### Project References

- `06_prototype/docs/resilient_maritime_cop_technical_design.md`
- `06_prototype/docs/data_api_integration_matrix_20260704.md`
- `05_analysis/knowledge_graph/t3_resilient_maritime_cop_schema_v0_1.md`
- `01_research/literature/t3_deep_research/ddil_isolated_tactical_research_20260704.md`
- `01_research/literature/t3_deep_research/strategy_tactics_resource_allocation_theory_20260704.md`
- `01_research/literature/t3_deep_research/contemporary_conflict_lessons_for_isolated_units_20260704.md`

### External References Checked

- Palantir AIP overview: https://palantir.com/docs/foundry/aip/overview/
- Palantir AIP Logic overview: https://palantir.com/docs/foundry/logic/overview/
- Palantir Workshop overview: https://palantir.com/docs/foundry/workshop/overview/
- Palantir OSDK React apps overview: https://palantir.com/docs/foundry/ontology-sdk-react-applications/overview/
- Palantir AIP features: https://palantir.com/docs/foundry/aip/aip-features/
- Palantir Developer access: https://palantir.com/docs/foundry/getting-started/overview/
- 전기통신사업법 제66조: https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000085371
- 전기통신사업법 제65조: https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000085244
- 재난 및 안전관리 기본법 제34조의2: https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000589596
- MOIS PS-LTE explainer: https://www.mois.go.kr/frt/sub/a06/b11/policyBriefingView/screen.do
- MOF national integrated public networks: https://www.mof.go.kr/doc/ko/selectDoc.do?bbsSeq=10&docSeq=46501&menuSeq=971
- KCA mountain mobile station API: https://www.data.go.kr/data/15067860/openapi.do
- Spectrum Map: https://www.spectrummap.kr/


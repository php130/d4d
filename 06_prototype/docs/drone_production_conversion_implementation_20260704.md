# Drone Production Conversion Demo Implementation

Date: 2026-07-04 KST

## Purpose

This prototype pivots D4D from a generic command-staff dashboard toward a sustainment decision tool:

> If wartime drone demand spikes, which public Korean factory candidates can supply each safe high-level part family, where should the parts converge for assembly, and how should the pipeline change if a predicted threat corridor makes some factories risky?

## Current Build

- Dataset generator: `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_drone_production_conversion_dataset.py`
- Processed dataset: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/drone_production_conversion_dataset.json`
- Full factory candidate capacity CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/full_factory_candidate_capacity_backdata.csv`
- Dynamic pipeline candidate shortlist CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_pipeline_candidate_shortlist.csv`
- Factory capacity backdata CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_capacity_backdata.csv`
- Factory route/capacity edge CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_route_capacity_edges.csv`
- Grid risk zone CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/grid_risk_zones.csv`
- Factory operational state CSV: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_operational_state.csv`
- Optimizer input v0.8 JSON: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_input_v0_8.json`
- Optimizer readiness report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_readiness_report_v0_8.md`
- Optimizer result v0.9 JSON: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_result_v0_9.json`
- Optimizer result report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_result_report_v0_9.md`
- Reconfiguration result v1.0 JSON: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/reconfiguration_result_v1_0.json`
- Reconfiguration result report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/reconfiguration_result_report_v1_0.md`
- Demo app: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion`
- App data fallback: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/drone_production_conversion_dataset.js`
- Optimization model design: `/Users/mollykim/projects/D4D/05_analysis/optimization/drone_production_optimization_model_20260704.md`
- Threat-responsive reconfiguration review: `/Users/mollykim/projects/D4D/05_analysis/optimization/threat_responsive_pipeline_reconfiguration_review_20260704.md`
- Optimization product guide: `/Users/mollykim/projects/D4D/06_prototype/docs/drone_production_optimization_product_guide_20260704.md`
- Factory capacity backdata plan: `/Users/mollykim/projects/D4D/06_prototype/docs/factory_capacity_backdata_plan_20260704.md`

Generated dataset:

| Item | Count |
| --- | ---: |
| Raw public factory rows scanned | 217,048 |
| Rich capacity backdata rows scanned | 198,235 |
| Full factory candidate pool | 29,616 |
| Dynamic pipeline shortlist rows | 8,829 |
| Map-visible factory candidates | 180 |
| Demo critical-resource candidates | 32 |
| Factory capacity backdata rows | 180 |
| Factory route/capacity edge rows | 126 |
| Grid risk zones | 15 |
| Grid degradation scenarios | 4 |
| Frozen order rows | 24 |
| In-transit shipment rows | 27 |
| Inventory/WIP rows | 180 |
| Scenarios | 3 |
| Part families | 8 |
| Component survival rows | 36 |
| Subcomponent constraint rows | 27 |
| Blockade phase curve rows | 18 |
| Critical-resource families | 4 |
| Assembly hubs | 3 |
| Routed road-like segments in active dataset | 223 |
| NGMS company-level emissions/energy records parsed | 777 |
| KEPCO large-load customer rows parsed | 44,122 |
| Direct demo factory energy matches | 15 |
| Direct demo resource energy matches | 1 |
| Regional energy/electricity context year | 2024 |

Optimizer input v0.8 export:

| Artifact | Count |
| --- | ---: |
| Nodes | 242 |
| Edges | 241 |
| Commodities | 40 |
| Demands | 108 |
| Capacities | 510 |
| Constraints | 109 |
| Inventory/WIP state rows | 180 |
| Frozen orders | 24 |
| In-transit shipments | 27 |
| Validation status | `pass_with_warnings` |

Optimizer result v0.9:

| Scenario | Feasible output | Gap | Route cost proxy | Weighted risk |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 6,428 | 3,572 | 6,690,700 | 0.120 |
| Western axis threat | 5,788 | 4,212 | 8,275,300 | 0.164 |
| Southern port disruption | 6,434 | 3,566 | 6,570,700 | 0.163 |

The app now loads `/data/optimizer_result_v0_9.js` and renders the Optimization Result section inside the Dataset drawer.

Reconfiguration result v1.0:

| Scenario | Level | Output delta | Cost delta | Risk delta | Added factories | Removed factories |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | monitor | 0 | 0 | 0.0000 | 0 | 0 |
| Western axis threat | emergency replan | -640 | 1,584,600 | 0.0440 | 34 | 31 |
| Southern port disruption | emergency replan | 6 | -120,000 | 0.0433 | 14 | 14 |

The app now loads `/data/reconfiguration_result_v1_0.js` and renders the Plan Delta / Reconfiguration section inside the Dataset drawer.

Full CSV candidate counts from keyword/rule extraction:

| Part family | Candidate rows |
| --- | ---: |
| Drone / final assembly | 143 |
| Flight stack / electronics | 5,031 |
| Battery / power | 1,046 |
| Motor / propulsion | 882 |
| Sensor / camera | 3,297 |
| Airframe / materials | 11,650 |
| Harness / connector | 1,282 |
| Test / packaging | 6,285 |

Full CSV critical-resource candidate counts from keyword/rule extraction:

| Resource family | Candidate rows |
| --- | ---: |
| Rare-earth / magnet feedstock | 109 |
| Battery material / cell recovery | 1,356 |
| Urban mining / e-waste metals | 1,166 |
| Composite / light-metal feedstock | 2,520 |

## Demo Behavior

The app shows:

- Korea map with candidate factories by part-family layer.
- Supplier selection is performed against the full 29,616-row candidate pool; the map layer then includes the balanced sample plus every selected supplier and resource-target factory.
- Satellite basemap using Esri World Imagery with boundary/place reference overlay.
- Critical-resource layer for rare-earth/magnet, battery recovery, urban-mining/e-waste metal, and composite feedstock candidates.
- Synthetic assembly hubs in Pyeongtaek, Daejeon, and Daegu.
- Animated resource-to-factory and part-to-assembly flow dots.
- Road-distance, duration, fuel, driver-hour, and estimated trip-cost fields for every active route.
- Energy/capacity evidence panel for each selected factory or resource node.
- Factory capacity tier, 30-day production estimate, capacity index, capacity confidence, workforce count, and manufacturing/building area evidence for selected factory nodes.
- Manufacturing-speed fields for selected factories: nominal daily output, surge daily output, setup days, minimum batch size, estimated yield, and process bottlenecks.
- Grid/power-risk proxy fields: regional load-serving risk zone, factory grid dependency score, outage output multiplier, backup-hour estimate, and grid-degradation scenarios.
- Operational state ledgers: frozen orders, in-transit shipments, and inventory/WIP rows for rolling-horizon reconfiguration constraints.
- Baseline plan and two threat-adjusted scenarios.
- Threat corridor overlay for predicted factory strike/logistics disruption.
- Rerouted paths when the threat scenario changes route preference.
- Per-part BOM bottleneck view.
- Selected node panel with product evidence, confidence, risk/assignment, and verification checklist.
- APAC allied sustainment C2 follow-on design notes.

## Critical-Material Extension

The user flagged a real design gap: drone output is not only a factory-conversion problem. Motors need magnet inputs, batteries need cell/material continuity, and flight-stack/harness production needs copper, PCB, and connector feedstock.

The v0.2 generator therefore creates upstream resource candidates from the same public factory registry text:

1. `rare_earth_magnet_recovery` feeds motor/propulsion candidates.
2. `battery_material_recovery` feeds battery/power candidates.
3. `metal_electronics_recycling` feeds flight-stack and harness candidates.
4. `carbon_composite_supply` feeds airframe/material candidates.

Important caveat: these rows are a triage queue for verification. A row containing `영구자석`, `네오디륨`, `폐배터리`, `전자스크랩`, or `비철금속` does not prove that the facility has current rare-earth extraction, separation, refining, or defense-grade material qualification capacity.

Relevant public-data/policy anchors:

- KICOX factory registry: company name, production item, industrial complex, and address.
- Korea Environment Corporation waste/recycling statistics: useful for recycling operator and performance calibration.
- Government critical-mineral recycling policy: basis for treating rare-earth permanent-magnet recycling and critical-mineral DB construction as a future integration path.

## Road-Distance and Logistics-Cost Design

The original v0.2 route logic used straight-line distance for selection and display. v0.3 keeps `straight_line_km` for comparison, but adds road-network fields to each factory-to-hub and resource-to-factory route:

- `road_distance_km`
- `duration_min`
- `route_geometry`
- `routing_provider`
- `routing_status`
- `fuel_liters_per_trip`
- `driver_hours_per_trip`
- `estimated_trip_cost_krw`

Current prototype mode:

1. `D4D_ROUTE_PROVIDER=osrm` calls OSRM route service for each unique origin-destination pair.
2. Results are cached in `/Users/mollykim/projects/D4D/03_data/raw/drone_production_conversion/road_route_cache_osrm.json`.
3. The app draws route polylines and animated flow dots along `route_geometry`.
4. If routing fails or the env var is not set, the generator falls back to a transparent road-distance estimate based on straight-line distance and a detour factor.

This is enough for a hackathon demo, but the production path should not depend on the public OSRM demo server.

Production-grade options:

| Option | Use When | Pros | Caveats |
| --- | --- | --- | --- |
| Self-host OSRM / Valhalla / GraphHopper | closed-network or no API-key environment | controllable, batch matrix friendly, offline-capable | OSM road freshness/coverage and Korean routing quality must be validated |
| Kakao Mobility Directions | Korean road distance/ETA and possible operational fit | local road network quality, driving directions | REST key required; usage/terms/cost review needed |
| NAVER Cloud Directions 5/15 | Korean map ecosystem and waypoint routing | local coverage and commercial support | client credentials, pricing, waypoint limits |
| Tmap API | logistics/vehicle routing in Korea | driving route, traffic/toll-oriented ecosystem | key, quota, and terms validation needed |

Recommended route dataset model:

| Entity | Fields |
| --- | --- |
| `RouteNode` | `node_id`, `node_type`, `lat`, `lon`, `address_source`, `snap_status`, `safety_precision` |
| `RouteMatrixEdge` | `origin_node_id`, `destination_node_id`, `vehicle_profile`, `provider`, `provider_version`, `road_distance_km`, `duration_min`, `toll_krw`, `route_geometry`, `fetched_at` |
| `VehicleProfile` | `vehicle_type`, `capacity_units`, `capacity_kg`, `fuel_efficiency_km_per_liter`, `driver_count`, `allowed_road_classes` |
| `CostModel` | `fuel_cost`, `labor_cost`, `toll_cost`, `risk_penalty`, `delay_penalty`, `stockout_penalty` |
| `OptimizedFlow` | `scenario_id`, `route_edge_id`, `quantity`, `trip_count`, `total_cost`, `risk_score`, `selected_reason` |

Optimization formulation:

```text
minimize sum(route_cost + risk_penalty + delay_penalty + stockout_penalty)
subject to:
  supplier capacity
  material availability
  vehicle capacity / trip count
  assembly hub capacity
  required BOM coverage
  scenario route-block or threat penalties
```

MVP implementation sequence:

1. Generate candidate factories/resource nodes.
2. Snap nodes to nearest road network.
3. Build OD pairs only for plausible category links, not all-to-all.
4. Fetch road distance/duration/geometry and cache results.
5. Compute per-trip fuel and driver-hour costs.
6. Rank candidate suppliers using `capacity`, `confidence`, `risk`, `road_distance_km`, and `estimated_trip_cost_krw`.
7. Upgrade from greedy selection to min-cost flow once vehicle capacity and inventory constraints are added.

## Energy / Capacity Evidence

The user proposed using factory electricity or energy use as a proxy for production capacity. This is directionally sound, but it should be treated as evidence of operating scale rather than proof of spare capacity.

Reasonable interpretation:

- A factory with high reported energy use is more likely to have real equipment, workforce routines, maintenance practices, and operating lines.
- For similar process categories, higher electricity demand can be a useful signal for production scale.
- If the system must choose between otherwise similar candidate factories, energy evidence is a defensible tie-breaker.

Limits:

- High electricity use can also mean inefficient equipment, heat-intensive processes, or low conversion flexibility.
- Public data usually does not expose each factory's live power draw, contracted demand, downtime, spare line capacity, or emergency grid resilience.
- Company-level emissions data may refer to a corporate entity or managed site, not necessarily the exact factory row from KICOX.

Implemented v0.5 fields:

- `energy_profile.match_type`: `ngms_company_direct` or `regional_industrial_proxy`
- `reported_energy_use_toe`
- `reported_ghg_emissions_tco2e`
- `regional_industrial_electricity_mwh`
- `regional_industrial_energy_toe`
- `estimated_power_intensity_score`
- `capacity_evidence_score`
- `factory_scale.employee_total`
- `factory_scale.land_area_m2`
- `factory_scale.manufacturing_area_m2`
- `factory_scale.building_area_m2`
- `factory_capacity_profile.capacity_tier`
- `factory_capacity_profile.capacity_index`
- `factory_capacity_profile.capacity_confidence`
- `factory_capacity_profile.predicted_output_units_30d`

Current sources:

| Source | Use | Limitation |
| --- | --- | --- |
| NGMS 명세서배출량정보공개 | company-level reported GHG emissions and energy use for large managed emitters | only large managed/allocated entities; exact factory-line matching remains uncertain |
| 한국에너지공단 에너지다소비사업자 에너지 사용 현황 | regional/sector electricity and energy context for large energy users | public file is aggregate context, not complete factory-level live consumption |
| KEPCO regional/industry electricity usage | future regional/industry trend and unit-price enrichment | generally aggregate; individual customer power use is not public |

How it affects selection:

The generator now estimates `capacity_units_30d` from `factory_capacity_profile.predicted_output_units_30d`, which combines public factory scale, workforce, production fit, and energy operating-scale evidence. Energy remains a light weighted term and does not dominate the estimate.

## Grid / Power-Risk Extension

v0.5 adds a power-continuity layer because factory selection can change if a regional load-serving area is degraded.

Implemented fields:

- `power_grid_risk_model`: source interpretation and safety boundary.
- `grid_risk_zones[]`: coarse province/city-cluster load-serving risk proxies from KEA industrial electricity, KEPCO large-load customer equipment context, and selected factory distribution.
- `grid_disruption_scenarios[]`: degradation cases with affected factory count, part-family exposure, and capacity at risk.
- `factory_candidates[].grid_risk_profile`: grid dependency score, outage output multiplier, backup-hour estimate, and verification needs.
- `plans[].selected_suppliers[].grid_dependency_score`: supplier-level grid risk term used in selection scoring.

Important boundary:

This is not a confirmed substation-to-factory dependency map. The KEPCO public file is aggregated into regional equipment/load context only. Exact customer-side feeder, substation, contracted power, backup generation, and restart-time dependencies require authorized utility/customer verification.

## Operational State Extension

v0.5 also adds the operating-state datasets needed for rolling-horizon reconfiguration:

- `frozen_orders[]`: released order quantities that should remain fixed until a freeze window expires.
- `in_transit_shipments[]`: shipment kind, route, progress, ETA, quantity, and threat response options.
- `inventory_wip[]`: finished goods, WIP, QA hold, committed quantity, available-to-ship, raw-material days, and max daily output.
- `factory_candidates[].manufacturing_profile`: daily/surge output, setup days, batch size, yield rate, and bottleneck notes.

Current values are synthetic placeholders anchored to the demo plan and public capacity proxy. Production use should replace them with ERP, MES, TMS, procurement, and warehouse feeds.

The production-grade model should continue expanding toward:

```text
capacity_evidence =
  reported energy / electricity scale
  + equipment and process match
  + recent operating status
  + workforce and shift availability
  + inventory/material availability
  + certifications and QA readiness
  + grid/fuel resilience
```

## Threat-Reroute Logic

The threat corridor is synthetic and demo-only.

For each scenario:

1. Measure each candidate factory's approximate distance to the predicted corridor.
2. Convert proximity and scenario probability into a risk score.
3. Penalize risky suppliers in selection and capacity.
4. Prefer inland assembly hubs when risk is elevated.
5. Mark adjusted routes as `rerouted`.

This demonstrates the user's requested behavior:

> If a probable enemy route suggests future strikes near specific factories, the system reconfigures factory sourcing and assembly flow.

## Threat-Responsive Reconfiguration Upgrade

The current demo is a scenario switcher. The intended product should become an event-driven reconfiguration engine.

Current fit:

- Threat scenarios already change supplier ranking and routing preference.
- Route and factory risk already affect selected suppliers.
- The UI can show rerouted flows.
- v0.5 now includes `frozen_orders[]`, `in_transit_shipments[]`, `inventory_wip[]`, `manufacturing_profile`, and `grid_risk_profile` as recourse-model inputs.

Required next upgrade:

1. Add live `ThreatEvent`, `NodeRiskState`, and `RouteRiskState` feeds.
2. Convert threat and grid events into node/route availability multipliers and risk-cost multipliers.
3. Connect the new frozen-order, in-transit, inventory/WIP, grid-risk, and manufacturing-speed ledgers to a rolling-horizon solver.
4. Add switching-cost constraints so the model does not recommend disruptive plan changes unless the benefit exceeds a command threshold.
5. Run interdiction-aware stress tests to find single points of failure in factories, material sources, routes, power-risk zones, and assembly hubs.
6. Display `PlanDelta`: factories removed/added, orders frozen, shipments held/rerouted, routes changed, extra cost, output preserved, and risk reduced.

Recommended algorithm name:

```text
Event-Driven Rolling-Horizon Robust Reconfiguration
```

Full formulation:

`/Users/mollykim/projects/D4D/05_analysis/optimization/threat_responsive_pipeline_reconfiguration_review_20260704.md`

## Data and Safety Boundary

The demo intentionally uses only safe high-level part families:

- airframe
- propulsion
- power
- flight stack
- sensor payload
- datalink/electronics
- harness
- QA/packaging

It does not include:

- weapons payloads
- munition design
- detailed drone build instructions
- real military intelligence
- verified mobilization orders
- sensitive facility coordinates
- verified rare-earth extraction or refining capacity claims

Every factory is shown as a public-data candidate requiring verification.

## Run

```bash
cd /Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion
PORT=8782 npm start
```

Open:

```text
http://localhost:8782
```

## Verification Commands

```bash
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/generate_drone_production_conversion_dataset.py
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/build_drone_optimizer_input.py
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_allocation_optimizer.py
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_reconfiguration_planner.py
python3 -m py_compile /Users/mollykim/projects/D4D/06_prototype/scripts/generate_drone_production_conversion_dataset.py
python3 -m py_compile /Users/mollykim/projects/D4D/06_prototype/scripts/build_drone_optimizer_input.py
python3 -m py_compile /Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_allocation_optimizer.py
python3 -m py_compile /Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_reconfiguration_planner.py
python3 -m json.tool /Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/drone_production_conversion_dataset.json >/dev/null
python3 -m json.tool /Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_input_v0_8.json >/dev/null
python3 -m json.tool /Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_result_v0_9.json >/dev/null
python3 -m json.tool /Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/reconfiguration_result_v1_0.json >/dev/null
node --check /Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/assets/app.js
node --check /Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/server.js
```

## APAC Allied Sustainment C2 Follow-On Direction

This should remain a second-stage extension after the Korean drone-production demo is stable.

Working theme:

> APAC 회색지대 거부환경 대응 동맹군 연합 지속지원 C2 시스템

Design direction:

1. Treat coalition equipment maintenance demand as a time-varying sustainment signal.
2. Represent APAC logistics nodes as aggregate resource pools, not sensitive facility-level data.
3. Fuse maintenance demand, local sourcing candidates, depot capacity, route risk, and communication-denial state.
4. Use min-cost flow or resilient routing to optimize allocation of repair parts, drone components, fuel-equivalent resources, and field kits.
5. Show local sourcing and distribution monitoring as a C2 layer: demand, source confidence, route viability, stockout risk, and reroute recommendation.
6. Keep gray-zone threat inputs as probabilistic indicators with citations and human approval, not autonomous tasking.

Potential future entities:

- `CoalitionUnit`
- `EquipmentType`
- `MaintenanceDemand`
- `LocalResourcePool`
- `Depot`
- `RouteSegment`
- `DeniedEnvironmentState`
- `AllocationPlan`
- `PartnerApproval`

Potential future algorithms:

- min-cost max-flow for supply allocation
- k-shortest resilient path routing
- scenario-based route interdiction stress test
- inventory stockout forecast
- confidence-weighted local sourcing ranker

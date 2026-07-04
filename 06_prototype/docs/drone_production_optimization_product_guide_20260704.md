# D4D Drone Production Optimization Product Guide

Date: 2026-07-04 KST
Dataset schema: `d4d.drone_production_conversion.v0.7`

## 1. Executive Position

The current D4D drone-production dataset is no longer just a factory list. It is a multi-layer wartime sustainment graph:

- factories and assembly hubs
- domestic recycling/resource candidates
- overseas raw-material sources and import ports
- maritime, port-to-factory, resource-to-factory, and factory-to-hub routes
- component, subcomponent, raw-material, inventory, WIP, frozen-order, in-transit, grid-risk, route-cost, and blockade-survival state

The product should therefore not be framed as a shortest-path app or a factory-ranking dashboard. The correct product framing is:

```text
wartime drone production continuity optimizer
```

The algorithmic backbone should be:

```text
Survival diagnostic + min-cost flow/MILP hybrid + rolling-horizon robust reconfiguration
```

For the hackathon, the safest and clearest story is:

1. **Current product:** diagnose bottlenecks, survival days, factory/resource candidates, route costs, and risk exposure.
2. **MVP optimizer:** allocate supply across candidate factories/routes while minimizing shortage, cost, risk, and ramp-up valley.
3. **Production optimizer:** replan repeatedly as threat, inventory, WIP, route, port, and grid state changes.

## 2. Current Data Snapshot

Authoritative local dataset:

- JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/drone_production_conversion_dataset.json`
- Public-data sample mirror: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/drone_production_conversion_dataset.json`
- Structure review: `/Users/mollykim/projects/D4D/06_prototype/docs/drone_production_dataset_structure_for_optimization_20260704.md`

Verified current counts:

| Layer | Current value |
| --- | ---: |
| Raw public factory rows | 217,048 |
| Capacity-source rows | 198,235 |
| Full factory candidate pool | 29,616 |
| Pipeline shortlist candidate rows | 8,829 |
| Map-visible factory candidates | 180 |
| Resource candidates | 32 |
| Assembly hubs | 3 |
| Scenarios | 3 |
| Component catalog | 12 |
| Subcomponent catalog | 9 |
| Raw-material catalog | 6 |
| Import ports | 4 |
| Foreign material sources | 6 |
| Maritime import route segments | 18 |
| Port-to-factory material route segments | 71 |
| Road-like routed segments | 223 |
| Frozen orders | 24 |
| In-transit shipments | 27 |
| Inventory/WIP rows | 180 |
| Grid risk zones | 15 |
| Grid disruption scenarios | 4 |

Baseline blockade headline:

| Metric | Current baseline |
| --- | --- |
| Weakest component bottleneck | `Camera / imaging module` |
| Deep subcomponent bottleneck | `CMOS imaging sensor` |
| Likely survival days | `8.0` days |
| Full-blockade likely producible volume | `26,663` units |
| Ramp-up valley | `D+9` to `D+73` |
| Valley daily shortage | `3,331` units/day |

Important caveat: these survival, inventory, WIP, and blockade values are synthetic defaults for product logic. They are not live ERP/MES/procurement truth.

## 3. Mental Model

Think of the dataset as a directed, multi-commodity graph.

### Nodes

| Node type | Dataset source | Product meaning |
| --- | --- | --- |
| Foreign material source | `foreign_material_sources[]` | overseas raw-material supply source |
| Import port | `import_ports[]` | inbound transshipment point |
| Domestic resource node | `resource_candidates[]` | recycling, recovery, material substitute candidate |
| Factory | `factory_candidates[]` | production/conversion candidate |
| Assembly hub | `assembly_hubs[]` | final convergence point |
| Grid risk zone | `grid_risk_zones[]` | coarse power-continuity risk context |
| Inventory pool | `inventory_wip[]` | initial stock, WIP, QA hold, committed quantity |

### Edges

| Edge type | Dataset source | Optimization role |
| --- | --- | --- |
| Maritime import | `plans[].maritime_import_route_segments[]` | overseas source to Korean port |
| Port-to-factory material | `plans[].port_to_factory_material_routes[]` | imported raw material to factory |
| Domestic resource-to-factory | `plans[].resource_route_segments[]` | domestic recovery/recycling to producer |
| Factory-to-assembly | `plans[].route_segments[]` | component flow to assembly hub |
| Component-to-subcomponent | `component_subcomponent_bom` | nested BOM constraint |
| Factory-to-grid-zone | `factory_candidates[].grid_risk_profile` | capacity derating under grid stress |

### Commodities

| Commodity layer | Dataset source | Why it matters |
| --- | --- | --- |
| Part family | `part_categories`, `bom` | high-level BOM and safe demo layer |
| Component | `component_catalog` | survival-days and ramp-up target |
| Subcomponent | `subcomponent_catalog` | chip/sensor/magnet bottleneck layer |
| Raw material | `raw_material_catalog`, `material_requirements` | rare-earth, battery, electronics, composite continuity |
| Finished drone equivalent | `target_drones`, `possible_drones_30d` | final output metric |

### State

| State | Dataset source | How optimizer uses it |
| --- | --- | --- |
| Inventory/WIP | `inventory_wip[]` | initial stock and available-to-ship balance |
| Frozen orders | `frozen_orders[]` | fixed commitments that cannot be freely reallocated |
| In-transit shipments | `in_transit_shipments[]` | rolling-horizon shipments already on the network |
| Grid risk | `grid_risk_profile`, `grid_disruption_scenarios[]` | factory capacity multiplier |
| Blockade survival | `component_survival_summary`, `subcomponent_survival_summary` | bottleneck and stockout horizon |

## 4. What Is Already Productized

The current app already supports the decision narrative:

1. **Where are candidate factories/resources?**
   Map-visible factories and resource candidates are shown on the Korea map.

2. **Which candidates look relevant?**
   Candidate scoring uses category fit, public factory evidence, capacity proxy, energy evidence, grid risk, route cost, and scenario risk.

3. **What routes are implied?**
   Road-like route segments contain distance, duration, geometry, fuel liters, driver hours, and estimated trip cost. Current routed provider is OSRM public demo server for road-like segments.

4. **What breaks first under blockade?**
   The Blockade Survival panel surfaces component/subcomponent bottlenecks, survival days, full-blockade producible volume, and ramp-up valley.

5. **What data is weak?**
   The dataset explicitly carries `data_limitations`, `verification_need`, source limitations, confidence scores, and synthetic-placeholder notes.

This is enough for a strong hackathon product demo if presented as a decision-support prototype, not as an authoritative mobilization system.

## 5. What Is Not Yet a Real Optimizer

The current implementation is still mostly:

```text
candidate extraction + scoring + scenario-specific generated plan + survival diagnostic
```

It is not yet:

```text
solver-backed global optimization
```

Missing pieces for a real optimization run:

| Missing piece | Why it matters |
| --- | --- |
| Explicit solver input table | Need a normalized `nodes`, `edges`, `commodities`, `constraints`, `state` bundle |
| Factory-part capability matrix | A factory can support more than one part/process with different setup and yield |
| Verified daily capacity | Public capacity proxy is not live mobilization capacity |
| Route capacity and vehicle fleet | Current route cost exists, but not truck count, driver shifts, route throughput |
| Inventory balance by time period | Needed for rolling-horizon decisions |
| Frozen/in-transit constraints in solver | Data exists, but must become hard constraints |
| Switching cost | Prevents unstable replan recommendations |
| Plan delta output | Product needs to explain what changed and why |
| Scenario probabilities | Robust/stochastic solver needs probability or uncertainty budgets |

## 6. Recommended Algorithm Stack

### Stage 0: Current Diagnostic Layer

Use the existing generated data exactly as now:

- show factory/resource candidates
- show route cost and road geometry
- show energy/capacity evidence
- show grid risk
- show blockade survival headline
- show component/subcomponent bottleneck ranking

This layer is deterministic and explainable. It is the product's "situational truth table."

### Stage 1: Deterministic Min-Cost Flow MVP

Use when factory activation choices are already filtered by shortlist.

Input:

- `logistics_route_edges.csv`
- `material_supply_backdata.csv`
- `factory_capacity_backdata.csv`
- `factory_operational_state.csv`
- `component_survival_backdata.csv`
- `subcomponent_constraints.csv`

Decision variables:

```text
flow[e,k] = quantity of commodity k moved on edge e
short[k]  = unmet demand for commodity k
```

Objective:

```text
minimize
  shortage_penalty
+ logistics_cost
+ route_risk_penalty
+ grid_risk_penalty
+ ramp_gap_penalty
```

Constraints:

```text
flow conservation
factory output cap
raw-material availability
component/subcomponent demand
route availability
inventory available-to-ship
```

Use this for the first solver-backed product feature because it gives tangible output without forcing every factory-conversion decision into a binary MILP.

### Stage 2: MILP for Factory Conversion and Ramp-Up

Use when the product needs to decide whether a factory should be activated or converted for a component.

Decision variables:

```text
activate[f,c] in {0,1}
produce[f,c,t] >= 0
ship[e,k,t] >= 0
inventory[n,k,t] >= 0
short[k,t] >= 0
trip[e,v,t] integer >= 0
```

Objective should be lexicographic:

1. minimize mission shortage and lateness
2. minimize deepest component/subcomponent stockout
3. minimize ramp-up valley depth and duration
4. minimize logistics, fuel, driver-hour, and risk cost
5. minimize grid-risk exposure and plan switching

Core constraints:

```text
BOM balance
subcomponent BOM balance
factory capacity
setup/ramp-up availability
raw-material supply
inventory/WIP balance
frozen order fixed allocation
in-transit shipment continuity
route capacity
vehicle capacity
grid degradation multiplier
scenario availability multiplier
```

### Stage 3: Rolling-Horizon Robust Reconfiguration

Use when threat, port, route, inventory, or grid state changes during execution.

Loop:

```text
1. ingest new event/state
2. update node and route availability multipliers
3. freeze near-term commitments and in-transit shipments
4. solve next horizon
5. emit plan delta
6. display changed factories/routes/orders/bottlenecks
```

This is the right home for:

- `ThreatEvent`
- `NodeRiskState`
- `RouteRiskState`
- `FrozenCommitment`
- `InTransitShipment`
- `PlanDelta`
- interdiction-aware stress tests

## 7. Product Integration

The product should expose the optimizer in five user-facing surfaces.

### 7.1 Mission Continuity Header

Purpose: answer "Can we keep producing?"

Show:

- likely survival days
- bottleneck component
- bottleneck subcomponent
- full-blockade producible volume
- D-day ramp-up valley
- daily shortage during valley

Current data source:

- `plans[].blockade_survival_headline`
- `plans[].blockade_phase_curve[]`

### 7.2 Bottleneck Workbench

Purpose: answer "What must we fix first?"

Show sorted rows from:

- `component_survival_summary[]`
- `subcomponent_survival_summary[]`
- `material_supply_backdata.csv`

Actions:

- increase inventory
- qualify alternate supplier
- accelerate domestic ramp-up
- reroute imported material
- verify substitute BOM

### 7.3 Map and Route Layer

Purpose: answer "Where does the plan physically move?"

Show:

- factories
- resource nodes
- ports
- assembly hubs
- factory-to-hub routes
- resource-to-factory routes
- port-to-factory routes
- route status and risk

Current data source:

- `plans[].route_segments[]`
- `plans[].resource_route_segments[]`
- `plans[].port_to_factory_material_routes[]`
- `plans[].maritime_import_route_segments[]`

### 7.4 Factory Decision Panel

Purpose: answer "Why this factory?"

Show:

- capability category and confidence
- 30-day predicted output
- daily/surge output
- setup days
- min batch
- yield estimate
- energy/capacity evidence
- grid dependency
- inventory/WIP
- verification checklist

Current data source:

- `factory_candidates[]`
- `factory_capacity_backdata.csv`
- `factory_operational_state.csv`

### 7.5 Plan Delta Panel

Purpose: answer "What changed after a threat or blockade event?"

Required new output:

```json
{
  "plan_delta": {
    "removed_factories": [],
    "added_factories": [],
    "rerouted_shipments": [],
    "frozen_orders_respected": [],
    "in_transit_actions": [],
    "output_preserved_units": 0,
    "extra_cost_krw": 0,
    "risk_reduction_score": 0,
    "new_bottleneck": ""
  }
}
```

This is the key product feature that turns the optimizer from a backend model into an executive decision tool.

## 8. Implementation Roadmap

### v0.8: Solver Input Export

Add a generated artifact:

```text
optimizer_input_v0_8.json
```

Required sections:

```text
nodes[]
edges[]
commodities[]
demands[]
capacities[]
inventory_state[]
frozen_commitments[]
in_transit_state[]
scenario_parameters[]
cost_parameters[]
```

No solver yet. The goal is normalized, testable optimizer input.

Implemented artifact:

- App data: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_input_v0_8.json`
- App readiness report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_readiness_report_v0_8.md`
- Sample mirror: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_input_v0_8.json`
- Sample readiness report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_readiness_report_v0_8.md`
- Builder: `/Users/mollykim/projects/D4D/06_prototype/scripts/build_drone_optimizer_input.py`

Current v0.8 export validation:

| Artifact | Count |
| --- | ---: |
| `nodes` | 242 |
| `edges` | 241 |
| `commodities` | 40 |
| `demands` | 108 |
| `capacities` | 510 |
| `constraints` | 109 |
| `inventory_wip` | 180 |
| `frozen_orders` | 24 |
| `in_transit_shipments` | 27 |

Validation status is `pass_with_warnings`.

Warnings to carry into v0.9:

- 231 operating-state rows are synthetic placeholders.
- 241 edge capacities currently use generated flow as a proxy.
- 180 factory capacities are public-data proxies, not verified spare capacity.

### v0.9: Deterministic Allocation Solver

Implement a simple LP/min-cost-flow layer:

- minimize shortage and route cost
- respect factory capacity
- respect material/subcomponent availability
- produce `optimization_result`
- render selected flows and shortages in the app

Output schema:

```text
plans[].optimization_result
plans[].optimization_result.selected_flows[]
plans[].optimization_result.shortages[]
plans[].optimization_result.binding_constraints[]
plans[].optimization_result.objective_breakdown
```

Implemented v0.9 artifact:

- App JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_v0_9.json`
- App JS: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_v0_9.js`
- App report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_report_v0_9.md`
- Sample JSON: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_result_v0_9.json`
- Sample report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/optimizer_result_report_v0_9.md`
- Runner: `/Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_allocation_optimizer.py`

Current v0.9 method:

```text
deterministic_greedy_min_shortage_then_route_score
```

This is not a full MILP. It fills demand from current candidate edges, preferring lower route score after shortage minimization. The route score currently combines cost proxy, route risk, grid dependency, and reroute penalty.

Current v0.9 validation:

| Artifact | Count |
| --- | ---: |
| Scenarios | 3 |
| Selected flows | 126 |
| Shortage rows | 42 |
| Binding constraints | 22 |

Scenario results:

| Scenario | Feasible output | Gap | Cost proxy | Risk | Main limiting constraint |
| --- | ---: | ---: | ---: | ---: | --- |
| `baseline` | 6,428 | 3,572 | 6,690,700 | 0.120 | Motor / Propulsion |
| `western_axis_threat` | 5,788 | 4,212 | 8,275,300 | 0.164 | Motor / Propulsion |
| `southern_port_disruption` | 6,434 | 3,566 | 6,570,700 | 0.163 | Motor / Propulsion |

Validation status is `pass_with_warnings`.

Warnings to carry into v1.0:

- v0.9 still searches only the current candidate edge pool.
- Cost is a trip-count proxy because fleet and vehicle-capacity data are not connected.
- Frozen orders and in-transit shipments are reported, but not yet enforced as hard recourse constraints.

### v1.0: Rolling-Horizon Reconfiguration

Add:

- threat/grid/port event input
- state update
- freeze-window handling
- in-transit handling
- switching cost
- plan delta UI

This is where the product becomes genuinely aligned with the wartime reconfiguration use case.

Implemented v1.0 Plan Delta prototype:

- App JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_v1_0.json`
- App JS: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_v1_0.js`
- App report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_report_v1_0.md`
- Sample JSON: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/reconfiguration_result_v1_0.json`
- Sample report: `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/reconfiguration_result_report_v1_0.md`
- Runner: `/Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_reconfiguration_planner.py`

Current v1.0 method:

```text
baseline_to_scenario_plan_delta_with_frozen_and_in_transit_review
```

Scenario deltas:

| Scenario | Level | Output delta | Cost delta | Risk delta | Added factories | Removed factories | Rerouted flows |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | monitor | 0 | 0 | 0.0000 | 0 | 0 | 0 |
| `western_axis_threat` | emergency_replan | -640 | 1,584,600 | 0.0440 | 34 | 31 | 31 |
| `southern_port_disruption` | emergency_replan | 6 | -120,000 | 0.0433 | 14 | 14 | 4 |

Validation status is `pass_with_warnings`.

Important limitation: v1.0 emits decision deltas and review actions. It does not yet enforce a full rolling-horizon MILP with switching-cost and freeze-window constraints.

## 9. Product Story for Demo

Use this story:

```text
The system does not claim to know exact classified mobilization capacity.
It builds a public-data supply-chain graph, estimates which parts and subparts fail first under blockade,
then recommends which factories, resource nodes, ports, and routes deserve verification or allocation first.
As threat/grid/logistics state changes, the next algorithm layer converts that state into availability/cost changes
and reoptimizes the production pipeline while preserving frozen orders and in-transit shipments.
```

This is defensible because it keeps the public-data limits visible while still showing a real operational decision loop.

## 10. Main Gaps to Track

| Gap | Current status | Product risk |
| --- | --- | --- |
| Live factory capacity | proxy only | overclaiming production readiness |
| ERP/MES inventory | synthetic | survival days can be misleading |
| Procurement and supplier contracts | absent | cannot know actual substitute availability |
| Vehicle fleet and driver schedule | absent | logistics cost is incomplete |
| Route capacity/tolls/traffic | partial | route cost may understate real constraints |
| Grid dependency | regional proxy | cannot infer exact feeder/substation dependency |
| Component substitution rules | high-level | optimizer cannot safely trade component variants |
| Solver-backed allocation | not implemented | current plan is generated/scored, not globally optimized |

The design should continue to label these as verification queues, not as proven facts.

# Drone Production Optimization Model

Date: 2026-07-04 KST

Objective:

> 전시 상황에서 최단 시간 내에, 최적 비용으로 필요한 드론 제작 역량을 확보하고 배분한다.

This document formalizes the optimization algorithm behind the D4D drone production-conversion demo. It maps the current v0.7 dataset to a mathematically defensible production, logistics, blockade-survival, and risk optimization model.

Companion review for threat-responsive reconfiguration:

- `/Users/mollykim/projects/D4D/05_analysis/optimization/threat_responsive_pipeline_reconfiguration_review_20260704.md`
- `/Users/mollykim/projects/D4D/06_prototype/docs/drone_production_optimization_product_guide_20260704.md`

## 1. Design Position

This problem should not be modeled as a single shortest-path or simple factory ranking problem. It is a coupled supply-chain optimization problem:

1. Demand differs by drone type.
2. Each drone type expands into a BOM.
3. Each BOM item can be made by different factories with different confidence, capacity, conversion lead time, energy evidence, and risk.
4. Resource nodes such as magnet feedstock, battery recovery, electronics scrap, and composites feed upstream part factories.
5. Road-network routing creates transport cost, fuel demand, driver-hour demand, and time delay.
6. Threat scenarios can reduce factory or route availability.
7. The output objective is multi-objective: maximize completed drones before deadline, minimize cost/time/risk, and preserve resilience.

The correct base model is a multi-period, multi-commodity, capacitated production-distribution MILP with scenario/robust extensions.

## 2. Literature Basis

| Need in D4D | Model family | Evidence |
| --- | --- | --- |
| Multiple parts moving from many factories to hubs | Multi-commodity distribution network design | Geoffrion and Graves formulated a multi-commodity capacitated distribution-system design MILP and used Benders decomposition on a large real distribution problem: [Management Science, 1974](https://pubsonline.informs.org/doi/10.1287/mnsc.20.5.822). |
| Time-phased production and inventory decisions | Dynamic lot sizing / production planning | Wagner and Whitin introduced the dynamic economic lot-size model for time-varying demand, setup, and holding costs: [Management Science, 1958](https://pubsonline.informs.org/doi/10.1287/mnsc.5.1.89). |
| Vehicle routing and transport cost | Vehicle routing problem | Dantzig and Ramser introduced the truck dispatching problem, the historical origin of VRP: [Management Science, 1959](https://pubsonline.informs.org/doi/10.1287/mnsc.6.1.80). |
| Uncertain capacity, demand, route disruption | Robust optimization | Bertsimas and Sim's "price of robustness" provides tractable control over conservatism in uncertain optimization: [Operations Research, 2004](https://ideas.repec.org/a/inm/oropre/v52y2004i1p35-53.html). |
| Facility and network decisions under uncertainty | Stochastic/robust facility location | Snyder reviews deterministic and stochastic facility location under uncertainty and points to stochastic programming foundations: [Facility Location Under Uncertainty](https://coral.ise.lehigh.edu/larry/files/pubs/stochloc.pdf). |
| Supply-chain network design under uncertainty | Robust supply-chain network design | Pishvaee et al. propose a robust MILP for closed-loop supply-chain network design under uncertain demand/transport costs: [Applied Mathematical Modelling, 2011](https://www.sciencedirect.com/science/article/pii/S0307904X10002623). |
| Practical implementation | CP-SAT / MIP / graph algorithms | Google OR-Tools provides constraint optimization, linear optimization, flow, graph, routing, and CP-SAT solvers: [OR-Tools overview](https://developers.google.com/optimization); CP-SAT is integer-only and requires integer-scaled constraints: [CP-SAT docs](https://developers.google.com/optimization/cp/cp_solver). |

Interpretation:

- MILP is the correct mathematical backbone for integrated planning.
- Min-cost flow is the correct fast subproblem for quantity allocation once factory/hub activation decisions are fixed.
- VRP is only needed when we optimize actual truck tours. The current dataset has point-to-point route costs; that is enough for MVP.
- Robust/stochastic optimization is necessary because wartime capacity, route safety, and demand are uncertain.

## 3. Current Dataset Mapping

Current dataset: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/drone_production_conversion_dataset.json`

| Model concept | Current field |
| --- | --- |
| Part family | `part_categories`, `bom.part_category` |
| BOM quantity | `bom.quantity_per_drone` |
| Factory candidate | `factory_candidates[]` |
| Factory capability | `factory.category`, `confidence`, `confidence_reasons` |
| Capacity proxy | `capacity_units_30d` |
| Energy evidence | `energy_profile.capacity_evidence_score`, `reported_energy_use_toe`, `reported_ghg_emissions_tco2e` |
| Critical resource node | `resource_candidates[]` |
| Assembly hub | `assembly_hubs[]` |
| Road route | `plans[].route_segments[]`, `plans[].resource_route_segments[]` |
| Route cost/time | `road_distance_km`, `duration_min`, `fuel_liters_per_trip`, `driver_hours_per_trip`, `estimated_trip_cost_krw` |
| Threat scenario | `plans[].threat`, `risk`, `status` |
| Component-level blockade survival | `plans[].component_survival_summary[]` |
| Subcomponent bottleneck | `plans[].subcomponent_survival_summary[]`, `component_subcomponent_bom` |
| Blockade phase curve | `plans[].blockade_phase_curve[]`, `blockade_survival_headline` |
| Raw-material supply | `raw_material_catalog`, `raw_material_supply_summary[]`, `material_supply_backdata.csv` |
| Overseas material route | `foreign_material_sources[]`, `import_ports[]`, `maritime_import_route_segments[]`, `port_to_factory_material_routes[]` |
| Grid risk | `grid_risk_zones[]`, `grid_disruption_scenarios[]`, `factory_candidates[].grid_risk_profile` |
| Operating state | `inventory_wip[]`, `frozen_orders[]`, `in_transit_shipments[]` |

Missing data needed for a stronger optimizer:

- expanded drone model families and model-specific BOMs
- verified production rate by factory and part family
- setup/conversion time by factory and part family
- minimum order batch size
- vehicle fleet and driver availability
- live inventory at resource/factory/hub nodes
- QA yield and rework rate
- shift schedule, labor constraints, grid reliability
- route capacity, toll, road restrictions, disruption probability
- substitute-component qualification and approved alternate BOM rules

## 4. Sets

Let:

- \(K\): drone types, e.g. short-range quadcopter, fixed-wing reconnaissance, training drone.
- \(I\): part/resource commodities, e.g. propulsion, battery, flight stack, airframe, magnet feedstock.
- \(F\): candidate factories.
- \(R\): upstream resource nodes.
- \(H\): assembly hubs.
- \(N = R \cup F \cup H\): all logistics nodes.
- \(E\): road-network edges or feasible origin-destination route arcs.
- \(T\): time periods, e.g. days or weeks.
- \(S\): scenarios, e.g. baseline, western-axis disruption, southern-port disruption.
- \(V\): vehicle profiles.

Current demo has one implicit drone type and \(T=1\) 30-day period. Production model should immediately generalize to multiple \(K\) and \(T\).

## 5. Parameters

Demand and BOM:

- \(D_{k,t}\): required quantity of drone type \(k\) by time \(t\).
- \(b_{i,k}\): units of part/resource \(i\) required per drone \(k\).
- \(w_k\): priority weight of drone type \(k\).

Factory capability:

- \(cap_{f,i,t}\): maximum output of part \(i\) at factory \(f\) during period \(t\).
- \(conf_{f,i}\): capability-confidence score.
- \(setup_{f,i}\): setup/conversion time.
- \(fix_{f,i}\): fixed conversion cost.
- \(var_{f,i}\): variable production cost per unit.
- \(yield_{f,i}\): usable output ratio after QA.
- \(eng_{f}\): energy/capacity evidence score.
- \(co2_{f,i}\): emissions factor or reported emissions proxy.

Resource supply:

- \(supply_{r,i,t}\): available upstream material \(i\) at resource node \(r\).
- \(qual_{r,i}\): quality/verification score for resource candidate.

Logistics:

- \(dist_e\): road distance of route \(e\).
- \(\tau_e\): travel time of route \(e\).
- \(fuel_e\): fuel liters per trip.
- \(driver_e\): driver hours per trip.
- \(cost_e\): per-trip logistics cost.
- \(vehcap_{v,i}\): vehicle capacity for commodity \(i\).
- \(routecap_{e,t,s}\): route capacity under scenario \(s\).
- \(risk_{e,s}\): route risk under scenario \(s\).

Scenario:

- \(p_s\): scenario probability.
- \(a_{f,t,s}\): factory availability multiplier.
- \(a_{e,t,s}\): route availability multiplier.
- \(demand_{k,t,s}\): scenario demand.

Penalties:

- \(P^{short}_k\): unmet-demand penalty.
- \(P^{late}_k\): lateness penalty.
- \(P^{risk}\): risk penalty.
- \(P^{co2}\): carbon/emissions penalty.

## 6. Decision Variables

Activation and conversion:

- \(y_{f,i} \in \{0,1\}\): factory \(f\) is activated for part \(i\).
- \(g_{h} \in \{0,1\}\): assembly hub \(h\) is active.

Production and supply:

- \(x_{f,i,t,s} \ge 0\): units of part \(i\) produced by factory \(f\).
- \(m_{r,i,t,s} \ge 0\): units of resource \(i\) recovered/supplied by resource node \(r\).
- \(q_{h,k,t,s} \ge 0\): assembled drones of type \(k\) at hub \(h\).

Transportation:

- \(z_{e,i,t,s} \ge 0\): quantity of commodity \(i\) shipped on route \(e\).
- \(n_{e,v,t,s} \in \mathbb{Z}_{+}\): number of vehicle trips on route \(e\) with vehicle \(v\).

Inventory and shortage:

- \(inv_{n,i,t,s} \ge 0\): inventory of commodity \(i\) at node \(n\).
- \(u_{k,t,s} \ge 0\): unmet demand of drone type \(k\).
- \(late_{k,t,s} \ge 0\): late output.

Robust/stochastic:

- \(\eta\), \(\xi_s\): CVaR auxiliary variables.

## 7. Objective Function

For wartime use, a lexicographic objective is more defensible than a single arbitrary weighted sum:

1. Maximize mission output before deadline.
2. Minimize shortage/lateness.
3. Minimize logistics and production cost.
4. Minimize risk concentration.
5. Minimize emissions/energy burden when it does not reduce urgent output.

Implementation form:

\[
\min
M_1 \sum_{s,t,k} p_s P^{short}_k u_{k,t,s}
+ M_2 \sum_{s,t,k} p_s P^{late}_k late_{k,t,s}
+ \sum_{s,t,f,i} p_s (fix_{f,i}y_{f,i} + var_{f,i}x_{f,i,t,s})
+ \sum_{s,t,e,i} p_s c_e z_{e,i,t,s}
+ \sum_{s,t,e,i} p_s P^{risk} risk_{e,s} z_{e,i,t,s}
+ \sum_{s,t,f,i} p_s P^{co2} co2_{f,i} x_{f,i,t,s}
\]

Use large \(M_1, M_2\) only if shortages and lateness must dominate cost. Otherwise use epsilon constraints:

\[
\sum_{h,t \le deadline_k} q_{h,k,t,s} \ge D_{k,s} - \epsilon_k
\]

then minimize cost among plans that meet acceptable output.

## 8. Core Constraints

### 8.1 BOM Balance at Assembly Hubs

For each hub, drone type, part, time, and scenario:

\[
\sum_{\text{in }e \to h} z_{e,i,t,s} + inv_{h,i,t-1,s}
\ge \sum_k b_{i,k} q_{h,k,t,s} + inv_{h,i,t,s}
\]

This is the bottleneck constraint. It prevents output if any required part family is missing.

### 8.2 Demand Satisfaction

\[
\sum_{h}\sum_{\tau \le t} q_{h,k,\tau,s} + u_{k,t,s} \ge D_{k,t,s}
\]

### 8.3 Factory Capacity

\[
x_{f,i,t,s} \le cap_{f,i,t} \cdot a_{f,t,s} \cdot y_{f,i}
\]

If conversion setup time matters:

\[
x_{f,i,t,s} = 0 \quad \forall t < setup_{f,i} \text{ when } y_{f,i}=1
\]

In MILP, implement with time-eligible activation variables:

\[
x_{f,i,t,s} \le cap_{f,i,t} \cdot y_{f,i,t-setup_{f,i}}
\]

### 8.4 Upstream Resource Capacity

\[
m_{r,i,t,s} \le supply_{r,i,t} \cdot qual_{r,i}
\]

Resource output must feed compatible factories:

\[
\sum_{\text{out }e:r \to f} z_{e,i,t,s} \le m_{r,i,t,s}
\]

### 8.5 Flow Conservation

For every non-assembly node \(n\):

\[
inv_{n,i,t,s}
= inv_{n,i,t-1,s}
+ production_{n,i,t,s}
+ \sum_{\text{in }e} z_{e,i,t,s}
- \sum_{\text{out }e} z_{e,i,t,s}
\]

where \(production_{n,i,t,s}\) is \(x_{f,i,t,s}\) for factories and \(m_{r,i,t,s}\) for resource nodes.

### 8.6 Vehicle and Driver Capacity

\[
z_{e,i,t,s} \le \sum_v vehcap_{v,i} n_{e,v,t,s}
\]

\[
\sum_{e,v} driver_e n_{e,v,t,s} \le DriverHours_{t}
\]

Fuel constraint:

\[
\sum_{e,v} fuel_e n_{e,v,t,s} \le FuelAvailable_t
\]

### 8.7 Route Capacity and Risk

\[
z_{e,i,t,s} \le routecap_{e,t,s} \cdot a_{e,t,s}
\]

If a route is forbidden under a scenario:

\[
a_{e,t,s}=0
\]

If not forbidden, risk enters as objective penalty rather than hard exclusion.

### 8.8 Assembly Hub Capacity

\[
\sum_k q_{h,k,t,s} \le HubCap_{h,t} \cdot g_h
\]

### 8.9 Carbon / Energy Budget

Optional, if policy requires:

\[
\sum_{f,i,t} co2_{f,i} x_{f,i,t,s} + \sum_{e,i,t} co2_e z_{e,i,t,s} \le CO2Budget_s
\]

In wartime, this should usually be a reporting constraint or soft penalty, not a hard blocker, unless energy/grid scarcity is the actual bottleneck.

## 9. Robust and Stochastic Extensions

### 9.1 Two-Stage Stochastic Model

First-stage decisions made before scenario realization:

- activate factories \(y_{f,i}\)
- activate hubs \(g_h\)
- pre-position inventory

Second-stage recourse after scenario \(s\):

- production \(x_{f,i,t,s}\)
- shipments \(z_{e,i,t,s}\)
- assembly \(q_{h,k,t,s}\)
- shortages \(u_{k,t,s}\)

Objective:

\[
\min fixed(y,g) + \sum_s p_s Q(y,g,s)
\]

where \(Q(y,g,s)\) is the scenario-specific MILP/LP recourse cost.

### 9.2 CVaR Risk Control

Expected cost alone is weak in wartime. Add CVaR for tail-risk shortage or cost:

\[
\min \eta + \frac{1}{1-\alpha}\sum_s p_s \xi_s
\]

\[
\xi_s \ge Loss_s - \eta,\quad \xi_s \ge 0
\]

Use this for high-impact scenarios: factory cluster disruption, port disruption, route interdiction, grid failure.

### 9.3 Budgeted Robust Optimization

Bertsimas-Sim style uncertainty can be applied to capacities and route times:

\[
cap_{f,i,t} \in [\bar{cap}_{f,i,t}-\hat{cap}_{f,i,t}, \bar{cap}_{f,i,t}]
\]

with uncertainty budget \(\Gamma\), meaning not every factory fails simultaneously. This is appropriate for threat and public-data uncertainty because it avoids worst-case overconservatism.

## 10. Algorithm Architecture

### Phase A: Candidate Graph Builder

Input:

- KICOX factory candidates
- resource candidates
- BOM
- assembly hubs
- road route matrix
- energy/capacity evidence
- threat scenario

Output:

- graph \(G=(N,E)\)
- compatible commodity arcs
- capacity and cost matrix
- scenario availability matrix

### Phase B: Fast Feasibility Plan

Use min-cost max-flow or LP relaxation:

1. Expand demand into BOM quantities.
2. Select compatible factory/resource arcs.
3. Use road cost and risk penalty as edge costs.
4. Compute feasible flow to assembly hubs.
5. Return bottleneck and unmet part families.

Purpose:

- fast judge/demo response
- sanity check data coverage
- warm start for MILP

### Phase C: Integrated MILP

Use MILP when we need:

- factory activation decisions
- setup lead times
- vehicle trips
- hub activation
- scenario recourse
- inventory and timing

Solver:

- Open-source MVP: OR-Tools CP-SAT for integer-heavy scheduling/activation, OR-Tools linear solver or HiGHS for LP/MIP where available.
- Production: Gurobi/CPLEX if licensing allows, because scenario MILP can become large quickly.

### Phase D: Decomposition

If the model becomes too large:

1. Master problem: factory/hub activation and conversion setup.
2. Subproblem: scenario-specific production and flow.
3. Use Benders cuts to iteratively refine activation decisions.

This follows the logic of multi-commodity distribution design by decomposition.

### Phase E: Rolling-Horizon Reoptimization

Run every planning cycle:

```text
for each planning refresh:
  ingest latest demand, factory verification, route status, inventory
  freeze already-issued orders and in-transit shipments
  reoptimize remaining horizon
  compare new plan vs current plan
  issue change recommendations only if benefit exceeds disruption threshold
```

This prevents the system from thrashing every time one data point changes.

## 11. Drone-Type-Specific BOM Extension

Current demo has one generic small-drone BOM. Production optimizer should support:

| Drone type | Example BOM behavior |
| --- | --- |
| quadcopter small | high motor count, battery-heavy, electronics/propulsion bottleneck |
| fixed-wing ISR | larger airframe, fewer motors, different sensor/navigation load |
| trainer/decoy | lower sensor quality, higher airframe/packaging volume |
| repair/refit kit | no full airframe, higher harness/electronics replacement rate |

Model:

\[
RequiredPart_{i,t} = \sum_k b_{i,k} D_{k,t}
\]

This lets command staff ask:

- If propulsion is scarce, which drone mix maximizes mission value?
- If sensors are scarce, which lower-sensor drone types remain feasible?
- If battery material is disrupted, what output mix is still possible?

## 12. Practical MVP Implementation Plan

### v0.5 Data Additions

Add files:

- `data/drone_types.json`
- `data/bom_lines.json`
- `data/vehicle_profiles.json`
- `data/conversion_profiles.json`
- `data/optimization_runs.json`
- `data/optimizer_input_v0_8.json`

Add fields:

- `factory_candidates[].capability_matrix[part_category]`
- `factory_candidates[].setup_days_by_part`
- `factory_candidates[].min_batch_units`
- `assembly_hubs[].daily_capacity_by_drone_type`
- `route_segments[].vehicle_profiles`
- `plans[].optimization_result`

Current v0.8 solver-input export exists at:

- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_input_v0_8.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_readiness_report_v0_8.md`

It validates the normalized graph contract before v0.9 solver work:

| Artifact | Count |
| --- | ---: |
| Nodes | 242 |
| Edges | 241 |
| Commodities | 40 |
| Demands | 108 |
| Capacities | 510 |
| Constraints | 109 |

Current v0.9 deterministic allocation result exists at:

- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_v0_9.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_report_v0_9.md`

It produces `selected_flows`, `shortages`, `binding_constraints`, `objective_breakdown`, and `plan_delta` for each scenario.

| Scenario | Feasible output | Gap | Cost proxy | Weighted risk |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 6,428 | 3,572 | 6,690,700 | 0.120 |
| Western axis threat | 5,788 | 4,212 | 8,275,300 | 0.164 |
| Southern port disruption | 6,434 | 3,566 | 6,570,700 | 0.163 |

Current v1.0 reconfiguration Plan Delta exists at:

- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_v1_0.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_report_v1_0.md`

It compares each scenario against baseline and emits added/removed factories, output/cost/risk deltas, frozen-order review actions, in-transit review actions, and human review checklists.

| Scenario | Level | Output delta | Cost delta | Risk delta |
| --- | --- | ---: | ---: | ---: |
| Baseline | monitor | 0 | 0 | 0.0000 |
| Western axis threat | emergency replan | -640 | 1,584,600 | 0.0440 |
| Southern port disruption | emergency replan | 6 | -120,000 | 0.0433 |

### v0.5 Algorithm

Implement a deterministic MILP/LP hybrid:

1. Use current candidate extraction.
2. Expand demand into part requirements.
3. Use route distance/cost and factory capacity evidence.
4. Solve min-cost flow for part allocation.
5. Compute bottleneck and plan cost.
6. Display objective breakdown:
   - drones feasible by deadline
   - total logistics cost
   - driver hours
   - fuel liters
   - highest-risk route
   - bottleneck part/resource

### v0.6 Algorithm

Add MILP activation:

- binary factory activation
- setup lead time
- hub capacity
- unmet-demand penalty

### v0.7 Algorithm

Add scenarios:

- baseline
- factory cluster disruption
- route disruption
- grid/energy constraint
- resource shortage

Use stochastic or robust formulation and show:

- baseline-optimal plan
- robust plan
- cost of robustness
- output preserved under disruption

## 13. Why This Is Defensible

The model is defensible because it decomposes the problem into accepted operations-research primitives:

- BOM expansion and lot sizing for time-phased production.
- Multi-commodity network flow for parts and resources.
- Facility activation and capacity constraints for factory conversion.
- Road routing and vehicle constraints for logistics.
- Robust/stochastic optimization for wartime uncertainty.
- Multi-objective optimization for output, time, cost, risk, and emissions.

The important engineering choice is not to overclaim precision. The current public data gives candidate capacity evidence, not verified mobilization capacity. The optimizer should therefore surface:

- data confidence
- direct vs proxy capacity evidence
- bottleneck sensitivity
- scenario regret
- verification queue

That makes the system useful for command-staff triage without pretending to know classified or non-public industrial capacity.

## 14. Recommended First Algorithm to Build

Build this first:

```text
Deterministic capacitated min-cost flow with BOM expansion
```

Reason:

- It directly uses current data.
- It is explainable to judges and operators.
- It is fast enough for interactive what-if sliders.
- It reveals bottlenecks immediately.
- It can later become the recourse subproblem inside robust/stochastic MILP.

Then add:

```text
MILP activation + setup time + vehicle trips
```

Then add:

```text
scenario robust optimization / CVaR
```

Do not start with full stochastic MILP. It will be harder to explain, harder to validate, and more likely to fail under hackathon time constraints.

## 15. Threat-Responsive Upgrade

For the user's intended wartime decision loop, the model must be interpreted as an event-driven reconfiguration system. The static version is not sufficient by itself.

Required upgrades:

1. Convert threat reports into node/route availability and risk-state updates.
2. Freeze committed orders and in-transit shipments.
3. Add switching cost so the plan does not churn after every alert.
4. Run rolling-horizon recourse every time material risk changes materially.
5. Run interdiction-aware stress tests offline to identify single points of failure.
6. Display plan delta: which factories, material sources, routes, and hubs changed and why.

Implementation name:

```text
Event-Driven Rolling-Horizon Robust Reconfiguration
```

The detailed formulation and research basis are in:

```text
/Users/mollykim/projects/D4D/05_analysis/optimization/threat_responsive_pipeline_reconfiguration_review_20260704.md
```

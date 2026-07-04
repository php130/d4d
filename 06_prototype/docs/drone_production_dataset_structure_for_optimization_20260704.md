# D4D Drone Production Dataset Structure for Optimization Review

Date: 2026-07-04 KST
Schema: `d4d.drone_production_conversion.v0.7`

## 1. 현재 데이터셋 한 줄 정의

D4D v0.7 데이터셋은 전시/봉쇄 상황에서 드론 부품 공급망을 평가하기 위한 공개데이터 기반 의사결정 그래프다. 공장 후보, 자원/원료 후보, 수입항, 해외 원료 source, 조립 허브, 도로/해상 route, 공장 Capa, 전력 리스크, 재고/WIP, 원자재 수급, 부품/서브부품 봉쇄 생존일수를 하나의 JSON과 CSV 묶음으로 제공한다.

안전 경계: 무장·탄두·표적·작전 경로·제작 세부 사양은 포함하지 않는다. 모든 공장/자원/재고/Capa 값은 후보/추정/데모 값이며 실제 의사결정 전 현장·계약·재고·법적 검증이 필요하다.

## 2. 규모

| 항목 | 수량 |
| --- | ---: |
| 원천 공장 row | 217,048 |
| Capa 산정용 rich 공장 row | 198,235 |
| 전체 후보 공장 pool | 29,616 |
| 지도 표시 공장 후보 | 180 |
| 지도 표시 자원 후보 | 32 |
| 부품군 | 8 |
| 원자재 카탈로그 | 6 |
| 부품 생존일수 component | 12 |
| 서브부품 constraint | 9 |
| 수입항 | 4 |
| 해외 원료 source | 6 |
| 조립 허브 | 3 |
| 시나리오 | 3 |
| 도로성 route edge | 223 |
| OSRM 도로 geometry/road summary 포함 route | 223 |
| 해상 수입 route | 18 |
| 항만-공장 원료 route | 71 |
| inventory/WIP row | 180 |
| frozen order row | 24 |
| in-transit shipment row | 27 |
| grid risk zone | 15 |

## 3. JSON Top-Level 구조

| Key | 의미 | 최적화에서의 역할 |
| --- | --- | --- |
| `factory_candidates[]` | 지도 표시 공장 후보 180개 | 생산 node, capacity node |
| `resource_candidates[]` | 국내 원료/회수 후보 32개 | upstream supply node |
| `assembly_hubs[]` | 조립 허브 | sink / final assembly node |
| `import_ports[]` | 수입항 | import transshipment node |
| `foreign_material_sources[]` | 해외 원료 source | external supply node |
| `plans[]` | 시나리오별 선택/경로/제약 결과 | scenario graph + solver input/output |
| `part_categories` | 8개 상위 부품군 | commodity family |
| `component_catalog` | 12개 세부 부품 생존일수 대상 | component-level commodity |
| `subcomponent_catalog` | 9개 칩/자석/센서 제약 | deep bottleneck commodity |
| `component_subcomponent_bom` | 부품→서브부품 BOM | nested capacity constraint |
| `raw_material_catalog` | 6개 원자재 | material commodity |
| `blockade_demand_model` | 소모 기반 일수요/봉쇄 모드 | demand scenario |
| `inventory_wip[]` | 공장별 재고/WIP | initial stock / committed state |
| `frozen_orders[]` | 동결 주문 | fixed commitment constraint |
| `in_transit_shipments[]` | 운송 중 물량 | rolling-horizon state |
| `grid_risk_zones[]` | 전력 리스크 권역 | capacity derating / resilience penalty |
| `routing_design` | route provider/한계 | route-cost evidence |

## 4. Plan-Level 구조

각 `plans[]` row는 하나의 시나리오다.

| Key | 의미 |
| --- | --- |
| `target_drones` | 30일 목표 수량 |
| `possible_drones_30d` | 공장 Capa와 원자재를 모두 반영한 30일 가능 수량 |
| `category_summary[]` | 부품군별 요구/할당/커버리지 |
| `selected_suppliers[]` | 선택된 부품 공장 |
| `route_segments[]` | 부품공장→조립허브 route |
| `resource_supply_summary[]` | 국내 자원/회수 후보 공급 요약 |
| `resource_route_segments[]` | 국내 자원→부품공장 route |
| `raw_material_supply_summary[]` | 원자재별 필요/재고/국내/수입/부족 |
| `maritime_import_route_segments[]` | 해외 source→수입항 해상 route |
| `port_to_factory_material_routes[]` | 수입항→공장 원료 route |
| `component_survival_summary[]` | 부품별 봉쇄 생존일수, 순소진, 램프업 gap |
| `subcomponent_survival_summary[]` | 칩/자석/센서 등 최심층 제약 생존일수 |
| `blockade_phase_curve[]` | Phase A / Valley / Phase B 생산가능 곡선 |
| `blockade_survival_headline` | 완전봉쇄 headline: 총 가능량, 병목, valley |

## 5. 주요 CSV 산출물

| CSV | Row 수 | 용도 |
| --- | ---: | --- |
| `full_factory_candidate_capacity_backdata.csv` | 29,617 | 전체 후보 공장 Capa/스코어 pool |
| `factory_pipeline_candidate_shortlist.csv` | 8,830 | 시나리오별 상위 후보 shortlist |
| `factory_capacity_backdata.csv` | 181 | 지도 표시 공장 Capa profile |
| `factory_route_capacity_edges.csv` | 127 | 부품공장→조립허브 route/capacity edge |
| `logistics_route_edges.csv` | 242 | 해상/항만/자원/공장/조립 통합 route edge |
| `material_supply_backdata.csv` | 19 | 원자재별 필요/가용/부족 |
| `material_import_routes.csv` | 90 | 해상 수입 + 항만-공장 material route |
| `component_survival_backdata.csv` | 37 | 부품별 생존일수/램프업 gap |
| `subcomponent_constraints.csv` | 28 | 칩/자석/센서 병목 |
| `blockade_phase_curve.csv` | 19 | 봉쇄 phase curve |
| `factory_operational_state.csv` | 232 | 재고/WIP/동결주문/운송중 상태 |
| `grid_risk_zones.csv` | 16 | 전력 리스크 권역 |
| `optimizer_input_v0_8.json` | 1 | solver용 nodes/edges/commodities/demands/capacities/state/constraints 정규화 |
| `optimizer_readiness_report_v0_8.md` | 1 | optimizer 입력 검증 결과와 v0.9 준비도 |
| `optimizer_result_v0_9.json` | 1 | 결정론적 allocation 결과: selected flows, shortages, binding constraints |
| `optimizer_result_report_v0_9.md` | 1 | 시나리오별 feasible output, gap, cost proxy, risk 요약 |
| `reconfiguration_result_v1_0.json` | 1 | baseline 대비 시나리오별 Plan Delta와 재구성 검토 액션 |
| `reconfiguration_result_report_v1_0.md` | 1 | output/cost/risk/factory 변화와 emergency replan 여부 |

## 6. 그래프 모델 관점

현재 데이터셋은 다층 multi-commodity flow 그래프로 볼 수 있다.

### Node Types

- `foreign_material_source`
- `import_port`
- `resource_node`
- `factory`
- `assembly_hub`
- `grid_zone`
- `inventory_pool`

### Edge Types

- `maritime_import`: 해외 source → 수입항
- `port_to_factory_material`: 수입항 → 부품 공장
- `domestic_resource_to_factory`: 국내 자원/회수 후보 → 부품 공장
- `factory_to_assembly_hub`: 부품 공장 → 조립 허브
- `component_to_subcomponent`: 부품 → 서브부품 BOM 제약
- `factory_to_grid_zone`: 공장 → 전력 리스크 권역

### Commodity Layers

- 상위 부품군: `part_categories`
- 세부 부품: `component_catalog`
- 서브부품: `subcomponent_catalog`
- 원자재: `raw_material_catalog`
- 완성 드론 수량: `target_drones`, `possible_drones_30d`

## 7. 현재 목적함수 후보

다음 최적화 알고리즘 검토에서 논의할 목적함수는 하나가 아니라 다목적이어야 한다.

1. 총 부족량 최소화

```text
minimize Σ unmet_demand[commodity]
```

2. 총 물류비 최소화

```text
minimize Σ flow[edge] * (fuel_cost + labor_cost + route_cost)
```

3. 리스크 가중 비용 최소화

```text
minimize Σ flow[edge] * route_risk_penalty + Σ factory_output * grid_risk_penalty
```

4. 봉쇄 생존일수 최대화

```text
maximize min_component survival_days
```

5. 램프업 골짜기 최소화

```text
minimize valley_depth_units_per_day * valley_duration_days
```

실제 구현은 weighted objective 또는 lexicographic objective가 적합하다.

## 8. 제약식 후보

| 제약 | 데이터 필드 |
| --- | --- |
| 부품별 수요 충족 | `category_summary.required_units`, `component_survival_summary.daily_demand_units` |
| 공장 Capa | `factory_capacity_profile.predicted_output_units_30d`, `selected_suppliers.adjusted_capacity_units_30d` |
| 원자재 가용량 | `raw_material_supply_summary.total_available_kg_30d` |
| 서브부품 가용량 | `subcomponent_survival_summary.effective_inventory_units` |
| 램프업 | `component_survival_summary.ramp_ready_day`, `ramp_gap_days` |
| 물류 route capacity/cost | `logistics_route_edges.csv` |
| 전력망 저하 | `grid_risk_profile.outage_output_multiplier`, `grid_dependency_score` |
| 동결 주문 | `frozen_orders[]` |
| 운송 중 물량 | `in_transit_shipments[]` |
| 재고/WIP 초기조건 | `inventory_wip[]` |
| 봉쇄 모드 | `blockade_demand_model.leakage_scenarios` |

## 9. 추천 알고리즘 단계

### MVP: Greedy + Score-Based Ranking

현재 구현은 이미 이 단계에 가깝다.

- 공장 후보를 capacity, confidence, risk, route cost로 정렬
- 부품군별 상위 후보를 선택
- 원자재와 route cost를 후처리로 계산

장점: 해커톤 데모에 빠르고 설명 가능하다.

한계: 다중 commodity 병목, 재고, 램프업, 동결 주문을 전역 최적화하지 못한다.

### Next: Min-Cost Flow

`logistics_route_edges.csv`를 edge table로 사용하고, 부품/원자재별 수요를 commodity로 두는 방식이다.

적합한 범위:

- 항만→공장 원료 배분
- 국내 자원→공장 배분
- 부품공장→조립허브 배분
- route cost/fuel/labor 최소화

한계:

- 여러 부품과 서브부품 BOM이 중첩되면 단순 min-cost flow만으로 부족하다.

### Recommended: Multi-Commodity MILP

최종 추천은 multi-commodity mixed-integer linear programming이다.

변수 예시:

```text
x[e,k,t] = time t에 edge e로 commodity k를 운송하는 양
y[f,p,t] = factory f가 component/part p를 생산하는 양
z[f,p]   = factory f를 part p 생산에 전환할지 여부
inv[k,t] = commodity k의 재고
short[k,t] = 미충족 수요
```

목적함수:

```text
minimize
  unmet_demand_penalty
+ logistics_cost
+ route_risk_penalty
+ grid_risk_penalty
+ ramp_gap_penalty
+ supplier_switching_penalty
```

핵심 제약:

```text
flow conservation
factory capacity
component BOM
subcomponent BOM
raw material availability
inventory balance
ramp-up availability
frozen-order fixed allocation
route availability / scenario disruption
```

### Scenario Layer: Robust / Stochastic Optimization

봉쇄/부분봉쇄/항만 스트레스/전력망 저하를 시나리오로 두고 robust objective를 추가한다.

```text
minimize expected_cost + λ * worst_case_shortfall
```

## 10. 다음 리뷰 질문

최적화 알고리즘 검토 시 다음 질문이 핵심이다.

1. 해커톤 MVP는 greedy/score로 유지할지, min-cost flow까지 갈지?
2. 완성부품, 서브부품, 원자재를 하나의 multi-commodity model에 넣을지, 단계별 solver로 나눌지?
3. `blockade_phase_curve`를 목적함수로 직접 넣을지, 대시보드 후처리 지표로 둘지?
4. 실시간 재계획은 몇 시간/며칠 단위 rolling horizon으로 볼지?
5. route cost는 유류비+운전시간만 쓸지, 통행료/차량적재/운전자 교대/위험 premium까지 넣을지?
6. 공장 전환 여부 `z[f,p]`를 binary로 두는 MILP까지 갈지, 우선 continuous allocation으로 단순화할지?

## 11. 공개 URL

- App: https://fair-extreme-gmbh-humanities.trycloudflare.com
- Dataset JSON: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/drone_production_conversion_dataset.json
- Logistics route edges: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/logistics_route_edges.csv
- Component survival: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/component_survival_backdata.csv
- Subcomponent constraints: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/subcomponent_constraints.csv
- Blockade phase curve: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/blockade_phase_curve.csv

## 12. Product/Algorithm Guide

The product-facing algorithm guide is maintained here:

- `/Users/mollykim/projects/D4D/06_prototype/docs/drone_production_optimization_product_guide_20260704.md`

## 13. Optimizer Input v0.8

Current normalized optimizer input:

- App JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_input_v0_8.json`
- App report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_readiness_report_v0_8.md`
- Builder: `/Users/mollykim/projects/D4D/06_prototype/scripts/build_drone_optimizer_input.py`

Validation summary:

| Artifact | Count |
| --- | ---: |
| Nodes | 242 |
| Edges | 241 |
| Commodities | 40 |
| Demands | 108 |
| Capacities | 510 |
| Constraints | 109 |
| Inventory/WIP | 180 |
| Frozen orders | 24 |
| In-transit shipments | 27 |

Status: `pass_with_warnings`.

The warnings are intentional product boundaries: operating-state rows are synthetic, edge capacities are flow-proxy capacities, and factory capacities are public-data proxies.

## 14. Optimizer Result v0.9

Current deterministic allocation result:

- App JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_v0_9.json`
- App JS: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_v0_9.js`
- App report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/optimizer_result_report_v0_9.md`
- Runner: `/Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_allocation_optimizer.py`

Validation summary:

| Artifact | Count |
| --- | ---: |
| Scenarios | 3 |
| Selected flows | 126 |
| Shortage rows | 42 |
| Binding constraints | 22 |

Status: `pass_with_warnings`.

Main result: the current candidate edge pool now bottlenecks on motor/propulsion coverage. This is useful because it tells the product what the next verification workflow must attack first: motor line conversion readiness, magnet/bearing supply, and alternate propulsion suppliers.

## 15. Reconfiguration Result v1.0

Current Plan Delta artifact:

- App JSON: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_v1_0.json`
- App JS: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_v1_0.js`
- App report: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/reconfiguration_result_report_v1_0.md`
- Runner: `/Users/mollykim/projects/D4D/06_prototype/scripts/run_drone_reconfiguration_planner.py`

Validation summary:

| Artifact | Count |
| --- | ---: |
| Scenarios | 3 |
| Frozen-order actions | 26 |
| In-transit actions | 81 |
| Emergency replan scenarios | 2 |

Status: `pass_with_warnings`.

Main result: both threat/disruption scenarios require emergency replan review. The product now shows what changed from baseline, including added/removed factories, cost/risk deltas, frozen-order conflicts, and in-transit shipment review counts.

# D4D Drone Production Continuity

전시 드론 수요가 급증했을 때, 공개 제조 데이터와 시나리오 기반 공급망 모델을 이용해 **어떤 부품이 병목인지, 어떤 공장 후보를 검증해야 하는지, 어떤 조달·조립 경로가 생산을 가장 오래 유지하는지** 판단하는 D4D 해커톤 프로젝트입니다.

현재 프로젝트의 중심은 초기 리서치용 워크스페이스가 아니라, 다음 데모입니다.

> 전시 드론 생산연속성 최적화 시스템<br>
> Drone Production Continuity & Factory Conversion Planner

## One-Line Pitch

부품이 흔들리면 드론이 흔들립니다. 이 시스템은 공장, 원료, 항만, 도로, 해상경로, BOM, 재고, 전력 리스크를 하나의 그래프로 묶고, 전시 상황에서 드론 생산을 계속 이어가기 위한 공장 전환과 조달 경로를 재계산합니다.

## Problem

전시 상황에서 드론은 소모품에 가까운 속도로 필요해질 수 있지만, 생산은 완성품 공장만으로 결정되지 않습니다.

- 모터, 배터리, 센서, flight stack, 하네스, 자석, 반도체 같은 부품과 원료가 병목이 될 수 있습니다.
- 한국은 해상 물류와 항만, 산업단지, 도로망, 전력 공급 리스크를 함께 고려해야 합니다.
- 실제 의사결정자는 단순한 공장 목록이 아니라 "30일 안에 몇 대를 만들 수 있는가", "무엇이 막히는가", "어디를 먼저 검증해야 하는가"를 알아야 합니다.

이 프로젝트는 공개 공장등록 데이터와 synthetic operational state를 결합해, 후보 공장과 공급 경로를 **검증 대기 큐**로 만들고 시나리오별 생산 가능량과 병목을 계산합니다.

## What This Demo Does

현재 프로토타입은 대한민국 지도 기반의 map-first 의사결정 캔버스입니다.

- 공개 공장등록 데이터에서 드론 부품군별 후보 공장을 추출합니다.
- 안전한 상위 수준 BOM으로 수요를 분해합니다.
- 원료 후보, 수입항, 항만-공장 경로, 공장-조립 경로를 연결합니다.
- OSRM 기반 도로거리, 소요시간, 유류량, 운전시간, 예상 trip cost를 붙입니다.
- 재고, WIP, 동결 주문, 운송 중 물량을 synthetic ledger로 표현합니다.
- baseline, western-axis threat, southern-port disruption 같은 시나리오를 비교합니다.
- `Drone Allocation Optimizer v0.9`로 생산 가능량, 부족분, 병목을 계산합니다.
- `Drone Reconfiguration v1.0`으로 위험 상황에서 제외/추가할 공장과 경로 변경 후보를 제안합니다.

## Current Demo Numbers

| Item | Value |
| --- | ---: |
| Raw factory rows | 217,048 |
| Capacity source rows | 198,235 |
| Full factory candidate pool | 29,645 |
| Scenario/category shortlist | 8,916 |
| Map-visible factories | 180 |
| Scenario active factories | about 50 |
| Optimizer nodes | 239 |
| Optimizer edges | 241 |
| Commodities | 40 |
| Constraints | 109 |
| Baseline feasible output | 6,428 / 10,000 |
| Baseline shortfall | 3,572 |
| Western-axis feasible output | 5,788 / 10,000 |
| Western-axis shortfall | 4,212 |
| Main bottleneck | Motor / Propulsion |

## Run the Main Prototype

```bash
cd 06_prototype/app/drone_production_conversion
npm install
PORT=8782 npm start
```

Open:

```text
http://localhost:8782
```

Validate the app bundle and demo data:

```bash
cd 06_prototype/app/drone_production_conversion
npm run check
```

## Main Files

| Path | Purpose |
| --- | --- |
| `06_prototype/app/drone_production_conversion/` | Main Leaflet web demo |
| `03_data/samples/drone_production_conversion/` | Processed demo dataset, route edges, optimizer inputs/results, reconfiguration outputs |
| `06_prototype/scripts/generate_drone_production_conversion_dataset.py` | Builds the production-conversion dataset |
| `06_prototype/scripts/build_drone_optimizer_input.py` | Builds optimizer graph input |
| `06_prototype/scripts/run_drone_allocation_optimizer.py` | Runs deterministic allocation optimizer |
| `06_prototype/scripts/run_drone_reconfiguration_planner.py` | Runs threat-responsive reconfiguration planner |
| `05_analysis/optimization/` | Optimization model and reconfiguration review notes |
| `07_deliverables/demo/drone_production_conversion_demo.md` | Demo walkthrough |
| `07_deliverables/demo/drone_production_conversion_presentation_script_5min_v4.md` | 5-minute pitch script |
| `02_problem_statements/hypotheses/wartime_drone_production_conversion_system_20260704.md` | Current product framing |

## Data Model

The demo is built around a safe, high-level sustainment model:

- `DroneDemand`: target output by time window and scenario
- `PartCategory`: non-sensitive part families such as airframe, propulsion, power, sensor, datalink, harness, packaging, QA
- `BOMLine`: high-level quantity and criticality per drone
- `Factory`: public factory record with address, product text, industry code, and approximate coordinate
- `CapabilityTag`: inferred candidate fit for a part family
- `ResourceCandidate`: upstream material, recycling, or feedstock candidate
- `AssemblyHub`: synthetic final/sub-assembly node
- `SupplyRoute`: maritime, port-to-factory, resource-to-factory, and factory-to-assembly route edge
- `Inventory/WIP/FrozenOrder/InTransitShipment`: synthetic operational state for rolling replan
- `PlanScenario`: baseline or disruption scenario with selected factories, routes, bottlenecks, and output curve

## Safety Boundary

This project is a decision-support prototype, not a drone manufacturing guide.

- It does not include weapon payloads, munition design, detailed build instructions, or tactical employment guidance.
- The BOM is limited to non-sensitive, high-level part families.
- Public companies are treated only as **candidate records for human verification**.
- Capacity, conversion readiness, and grid-risk fields are proxy signals, not confirmed operational facts.
- Synthetic threat corridors and disruption scenarios are demo assumptions, not intelligence.
- Any production use would require legal review, supplier consent/verification, secure data handling, and approved operational authority.

## Related Research Tracks

The repository still contains earlier and supporting research because it informed the final direction.

- `sdot_drone_semantic_ops`: drone/sensor semantic transmission under degraded networks
- `resilient_maritime_cop`: denied-network maritime COP and semantic updates
- `korea_civil_infra_cop`: Korean civil infrastructure COP prototype
- `literature_sdot_drone` and `literature_t3`: background research datasets
- `palantir/sdot_drone_semantic_ops`: Palantir-style ontology bundle for the S-DOT concept

These are useful references, but the current flagship demo is `drone_production_conversion`.

## Repository Layout

```text
D4D/
  00_admin/                 Event notes, rules, glossary, coordination
  01_research/              Source intake, OSINT/data research, literature notes
  02_problem_statements/    Problem framing and product hypotheses
  03_data/                  Processed datasets and demo samples
  04_platforms/             Palantir AIP, StealthMole, and platform-learning notes
  05_analysis/              Optimization and knowledge-graph analysis
  06_prototype/             Demo apps and dataset/optimizer scripts
  07_deliverables/          Demo guides, pitch scripts, deployment notes, visual checks
  08_ops/                   Runbooks, sync workflow, ethics and security checklist
```

## Source and Compliance Notes

Key public-data basis:

- 한국산업단지공단 전국등록공장현황 CSV
- 한국산업단지공단 공장등록생산정보조회서비스 candidate API
- Public/open geospatial and routing references
- Synthetic operational state for inventory, WIP, disruption, and threat scenarios

Operational guidance:

- Keep raw credentials and API keys out of git.
- Treat `.env.example` as the only committed environment-variable reference.
- Use public, synthetic, or permissioned data only.
- Keep source provenance and limitation notes visible in the demo and deliverables.

## Git Notes

The original upstream clone is `dizzikim-dev/D4D`. A working copy has also been pushed to `php130/d4d`.

Current GitHub sync helper:

```bash
./08_ops/scripts/git_sync_status.sh
```

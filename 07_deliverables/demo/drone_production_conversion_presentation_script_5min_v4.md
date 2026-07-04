# D4D 전시 드론 생산전환 시스템 발표 스크립트 5분 v4

## 발표 키 메시지

**부품이 흔들리면, 드론이 흔들린다.**  
저희는 전시 상황에서 드론 생산을 계속 유지하기 위해, 공장·원료·항만·도로·해상경로·BOM·재고·전력 리스크를 하나의 그래프로 묶고, 어떤 공장을 살리고 어떤 경로로 조달해야 하는지 계산하는 **전시 드론 생산연속성 최적화 시스템**을 만들었습니다.

---

## 0:00 - 0:30 · 훅

여러분, 전쟁에서 드론 생산의 핵심은 완성품 공장만이 아닙니다.  
**부품이 흔들리면, 드론이 흔들립니다.**

우크라이나 사례가 이걸 보여줍니다. 공개 분석에 따르면, 2024년 상반기 우크라이나의 UAS 관련 수입액 중 약 89%가 중국에서 들어왔습니다. 중국이 드론 부품과 희토류, 자석, 배터리 소재에 수출통제를 걸면, 최종 조립 능력이 있어도 생산은 바로 흔들립니다.

그럼 한국에서 전쟁이 발생했을 때, 지휘관은 이 질문에 어떻게 답할 수 있을까요?

**지금 이 순간, 우리는 드론을 계속 만들 수 있는가?  
부족하다면, 무엇이 병목이고 어디서 가져와야 하는가?**

---

## 0:30 - 1:20 · 문제

한국은 세 가지 급소를 동시에 가지고 있습니다.

첫째, 우리는 사실상 **섬**입니다.  
교역의 대부분이 바다를 통해 들어오기 때문에, 해상 봉쇄나 항만 교란이 발생하면 육로 대안이 거의 없습니다.

둘째, 드론 생산과 부품 제조 거점은 **전국에 흩어져 있습니다.**  
분산은 생존에는 유리하지만, 위기 상황에서는 어느 공장이 살아 있고, 어느 공장이 멈췄고, 어느 공장을 조립 허브로 써야 하는지 한눈에 보기 어렵습니다.

셋째, 드론은 국내에서 조립할 수 있어도, 그 안에 들어가는 모터, 배터리, 센서, 하네스, 반도체, 네오디뮴 자석 같은 핵심 부품과 원료는 외부 공급망에 걸려 있습니다.

그런데 실제 위기가 오면 지휘관에게 필요한 건 단순한 공장 목록이 아닙니다.  
**재고가 며칠 남았는지, 병목 부품이 무엇인지, 어느 공장을 전환할 수 있는지, 어떤 도로와 항만 경로가 가장 빠르고 싼지**를 동시에 판단해야 합니다.

---

## 1:20 - 2:20 · 솔루션 정체성

그래서 저희가 만든 것은 단순한 지도 대시보드가 아니라, **전시 드론 생산연속성 최적화 시스템**입니다.

현재 프로토타입의 핵심 데이터셋은 `d4d.drone_production_conversion.v0.8`입니다.  
한국산업단지공단 등록공장 데이터 217,048건과 capacity source row 198,235건을 기반으로, 드론 부품 생산 후보 공장 29,645개를 만들었습니다. 그중 시나리오별 route matrix 확장을 위해 8,916개 shortlist를 만들고, 지도에서는 180개 후보 공장과 약 50개의 활성 공장을 볼 수 있게 했습니다.

여기에 다음 데이터 레이어를 붙였습니다.

- 공장별 `factory_capacity_profile`: 생산 적합도, 면적, 종업원 수, 에너지 사용 proxy, 전력 리스크
- `logistics_route_edges.csv`: OSRM 기반 도로거리, 예상 시간, 유류 사용량, 운전시간, trip cost
- `material_import_routes.csv`: 일본·우방국 원료 source에서 한국 항만까지의 해상 경로와 항만-공장 원료 경로
- `component_subcomponent_bom`: 드론 1대를 만들기 위한 부품과 서브부품 제약
- `inventory_wip`, `frozen_orders`, `in_transit_shipments`: 재고, WIP, 동결 주문, 운송 중 물량 상태

즉, 이 시스템은 **공장 리스트를 보여주는 도구가 아니라, 공장-원료-항만-도로-해상경로-BOM을 연결한 생산연속성 그래프**입니다.

---

## 2:20 - 3:40 · 시나리오와 알고리즘

저희는 이 그래프를 세 가지 상황에서 돌려봤습니다.

첫째는 `baseline`입니다.  
현재 조달망이 유지되는 상황에서 30일 동안 목표 드론 10,000대를 만들 수 있는지 봅니다.

둘째는 `western_axis_threat`입니다.  
서부축 위협으로 일부 공장과 경로의 risk가 올라가는 상황입니다.

셋째는 `southern_port_disruption`입니다.  
남부 항만에 스트레스가 걸려 해상 수입과 항만-공장 원료 공급이 흔들리는 상황입니다.

이때 사용하는 최적화 입력은 `d4d.drone_optimizer_input.v0.8`입니다.  
여기에는 nodes 239개, edges 241개, commodities 40개, demands 108개, capacities 507개, constraints 109개가 들어갑니다.

그 위에서 `Drone Allocation Optimizer v0.9`를 돌리면, 단순히 가까운 공장을 고르는 것이 아니라 **부족분을 최소화하고, route cost와 risk를 함께 보는 deterministic allocation**을 수행합니다.

예를 들어 baseline 기준으로 목표는 30일 10,000대입니다.  
현재 후보 공급망으로 가능한 생산량은 6,428대, 부족분은 3,572대입니다.  
그리고 병목은 **Motor / Propulsion** 계열로 잡힙니다.

서부축 위협 시나리오에서는 가능한 생산량이 5,788대로 떨어지고, 부족분은 4,212대로 커집니다.  
이때 `Drone Reconfiguration v1.0`은 emergency replan을 띄우고, 34개 공장을 새로 후보로 올리고 31개 공장을 제외하라는 plan delta를 냅니다.

즉, 이 시스템은 “위험합니다”라고 경고만 하는 게 아니라,  
**어느 공장을 유지하고, 어느 공장을 빼고, 어떤 경로를 다시 봐야 하는지**까지 보여줍니다.

---

## 3:40 - 4:30 · 핵심 가치

지휘관이 이 화면에서 결정해야 하는 것은 세 가지입니다.

**무엇을, 어디서, 얼마나 빨리 확보할 것인가.**

우리가 국내에서 어느 정도 만들 수 있는 부품은 시간이 문제입니다.  
프레임, 포장, 하네스, 일부 배터리 팩, 일부 조립 공정은 전환 후보 공장을 찾고 capacity를 끌어올릴 수 있습니다.

하지만 정말 위험한 것은 당장 국내에서 대체하기 어려운 소수의 병목입니다.  
모터 계열에서는 네오디뮴 자석과 희토류 feedstock, 센서 계열에서는 광학 부품, flight stack에서는 일부 반도체와 제어 모듈이 문제가 됩니다.

그래서 저희 시스템은 원료 경로도 함께 봅니다.  
예를 들어 일본 서해안의 magnet buffer source에서 동해항으로 들어오는 해상 경로, 기타큐슈에서 부산항으로 들어오는 electronics feedstock 경로, 나고야에서 울산항으로 들어오는 composite/light-metal feedstock 경로를 지도 위에 표시합니다.

그리고 항만에서 끝나는 게 아니라, 항만에서 실제 부품 공장까지 가는 도로 경로를 계산합니다.  
도로거리, 소요시간, 유류 사용량, 운전시간, 예상 trip cost를 붙이기 때문에, 단순히 “가깝다”가 아니라 **비용과 시간 기준으로 조달 경로를 비교**할 수 있습니다.

---

## 4:30 - 5:00 · 클로징

정리하면, 저희가 만든 것은 전시 드론 생산을 위한 **map-first 의사결정 캔버스**입니다.

전체 후보 공장 29,645개에서 시작해, 지도 후보 180개, 시나리오별 활성 공장 약 50개로 좁히고, 공장별 capacity, 전력 리스크, 재고, BOM, 해상·도로 경로를 연결했습니다.

그리고 `Drone Allocation Optimizer v0.9`와 `Drone Reconfiguration v1.0`을 통해, 30일 목표 생산량 기준으로 가능한 생산량, 부족분, 병목, emergency replan을 계산합니다.

전쟁에서 중요한 것은 단순히 드론을 많이 만드는 것이 아닙니다.  
**부품이 흔들릴 때도 생산을 계속 이어가는 것**입니다.

저희 솔루션은 지휘관이 지금 무엇이 흔들리는지 보고, 그 즉시 어디서 조달하고 어떤 공장을 전환할지 결정하도록 돕습니다.

**전장을 보고, 조달을 다시 계산한다.  
그것이 저희 D4D 전시 드론 생산전환 시스템입니다.**

감사합니다.

---

## 발표 중 강조할 구현 명칭

- Product: 전시 드론 생산연속성 최적화 시스템
- Dataset: `d4d.drone_production_conversion.v0.8`
- Capacity model: `d4d.factory_capacity_profile.v0.1`
- Optimizer input: `d4d.drone_optimizer_input.v0.8`
- Allocation result: `Drone Allocation Optimizer v0.9`
- Replan result: `Drone Reconfiguration v1.0`
- Map layer: 전체 공장 180개 / 활성 공장 약 50개 / 조립·수집 convergence node 강조
- Route layer: maritime import, port-to-factory material, domestic resource-to-factory, factory-to-assembly
- Cost layer: road distance, duration, fuel liters, driver hours, estimated trip cost

## 숫자 체크리스트

| 항목 | 값 |
| --- | ---: |
| Raw factory rows | 217,048 |
| Capacity source rows | 198,235 |
| Full factory candidate pool | 29,645 |
| Scenario/category shortlist | 8,916 |
| Map-visible factories | 180 |
| Priority drone assembly seeds | 29 |
| Scenario active factories | 약 50 |
| Road-like routed segments | 223 |
| Maritime import routes | 18 |
| Port-to-factory material routes | 71 |
| Import ports | 4 |
| Allied/foreign material sources | 6 |
| Optimizer nodes | 239 |
| Optimizer edges | 241 |
| Commodities | 40 |
| Demands | 108 |
| Capacities | 507 |
| Constraints | 109 |
| Baseline feasible output | 6,428 / 10,000 |
| Baseline shortfall | 3,572 |
| Western-axis feasible output | 5,788 / 10,000 |
| Western-axis shortfall | 4,212 |
| Main bottleneck | Motor / Propulsion |

## 표현 주의사항

- 현재 프로토타입은 공개데이터와 synthetic operational state를 기반으로 한 **live-ready 구조**입니다. 발표에서는 “실시간 피드를 붙일 수 있는 구조”, “ERP/MES/TMS 연계형 상황판”이라고 표현하는 것이 안전합니다.
- 공장 capacity는 실제 동원 가능 capacity가 아니라 `capacity_index`, `capacity_confidence`, `predicted_output_units_30d` 기반의 공개데이터 proxy입니다.
- 희토류·자원 회수 노드는 실제 추출 가능 공장 확정 목록이 아니라, permit/process/material grade 검증이 필요한 candidate queue입니다.
- 해상 경로는 실제 군사 운송 지시가 아니라 public-demo logistics corridor입니다.


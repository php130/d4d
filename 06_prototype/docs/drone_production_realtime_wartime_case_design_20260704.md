# D4D Drone Production Realtime Wartime Case Design

Date: 2026-07-04 KST

Purpose:

전시 드론 생산전환 대시보드가 단순히 지도에 공장을 찍는 데서 끝나지 않고, 상황이 바뀔 때마다 생산 가능량, 부족량, 물류비, 위험도, 공장 선택, 운송 검토가 어떻게 바뀌는지 실시간 케이스처럼 보여주기 위한 설계다.

Safety boundary:

- 비무장 소형 정찰/훈련용 드론의 상위 부품군 수준만 다룬다.
- 무장, 공격 임무, 세부 제작 사양, 적 취약점 공략은 다루지 않는다.
- 실제 업체는 동원 대상이 아니라 `후보 / 검증 필요`로만 표시한다.
- 위협 경로는 실제 정보가 아니라 demo-only synthetic scenario로 표시한다.

## 1. Demo Goal

발표에서 보여줘야 하는 핵심은 다음 한 문장이다.

> 상황 시나리오가 바뀌면, 같은 데이터셋을 기반으로 알고리즘이 공장·경로·부족량·위험도를 다시 계산하고 UI가 즉시 다른 의사결정 카드로 바뀐다.

현재 앱에 붙인 구현 상태:

- Header scenario tabs: `Baseline`, `Threat Reroute`, `Port Stress`, `재생`
- Map case ticker: 현재 케이스의 이벤트 신호, UI 변화, 로직 변화, 운영자 행동을 표시
- Existing panels reused: `Optimization Result`, `Plan Delta / Reconfiguration`, `Active Flow Ledger`, `Raw Material / Import Routes`

## 2. Case Set

### Case A. Baseline / D+0 생산전환 발령

상황:

- 전시 수요 10,000대 / 30일이 들어온다.
- 아직 특정 도로, 항만, 공장 위협은 없다.
- 시스템은 기존 후보 공장과 원료 수급 경로로 먼저 생산 가능량을 계산한다.

현재 계산 결과:

| Metric | Value |
| --- | ---: |
| 30일 목표 | 10,000 |
| 최적화 가능 수량 | 6,428 |
| 부족량 | 3,572 |
| 물류비 proxy | 6,690,700 |
| 가중 route risk | 0.120 |
| 1순위 병목 | Motor / Propulsion |

UI 변화:

- 지도: 기본 공장 후보, 원료 회수 후보, 해상 수입 경로, 공장-조립 흐름 표시
- Optimization Result: 목표 대비 부족량과 Motor / Propulsion 병목 표시
- Plan Delta: `monitor`

로직 변화:

- 기존 후보 경로만 사용한다.
- 먼저 부족량을 줄이고, 그 다음 비용/위험 점수가 낮은 경로를 선택한다.
- 동결 주문과 운송 중 물량은 아직 변경 대상이 아니라 모니터링 대상으로 둔다.

발표 멘트:

> "이 화면은 전시 수요가 처음 들어왔을 때의 기본 계산입니다. 현재 후보망으로는 10,000대 중 약 6,428대까지 가능하고, 가장 먼저 막히는 곳은 모터/추진계입니다."

### Case B. Western Axis Threat / D+1 서부축 위험 상승

상황:

- 서부축 산업/물류 corridor의 위험이 상승한다.
- 일부 공장과 경로가 위험 패널티를 받는다.
- 시스템은 위험 corridor 근처 후보를 낮게 평가하고 대체 공장/경로를 찾는다.

현재 계산 결과:

| Metric | Value |
| --- | ---: |
| 최적화 가능 수량 | 5,788 |
| 목표 대비 부족량 | 4,212 |
| Baseline 대비 생산량 변화 | -640 |
| 물류비 proxy 변화 | +1,584,600 |
| 위험 변화 | +0.0440 |
| 추가 공장 | 34 |
| 제외 공장 | 31 |
| 재배치 flow | 31 |
| 동결 주문 충돌 | 19 |
| 운송 검토 | 14 |

UI 변화:

- 지도: 서부축 적색 synthetic threat corridor 표시
- 흐름선: rerouted flow가 더 많이 보임
- Plan Delta: `emergency_replan`
- 검토 카드: 동결 주문과 운송 중 물량의 재확인 항목 증가

로직 변화:

- `factoryRisk()`가 corridor와 거리 기반으로 risk를 올린다.
- allocation 결과는 위험이 큰 경로를 밀어내고, 대체 경로를 선택한다.
- v1.0 reconfiguration은 baseline과 비교해 추가/제외 공장, 비용, 위험, frozen order conflict를 계산한다.

발표 멘트:

> "위협 정보가 들어오면 지도에 위험 corridor가 뜨고, 시스템은 기존 계획을 그대로 밀어붙이지 않습니다. 생산량은 640대 줄고 비용은 늘지만, 위험이 높은 경로를 피해 재배치가 필요하다는 판단을 보여줍니다."

### Case C. Southern Port Disruption / D+2 남부 항만 차질

상황:

- 남부 항만 처리나 원료 유입 경로에 차질이 생긴다.
- 희토류 자석, 배터리 소재, 전자스크랩 같은 원료 feeder route가 함께 흔들릴 수 있다.
- 시스템은 해상 수입 경로, 항만-공장 경로, 국내 회수 후보를 함께 비교한다.

현재 계산 결과:

| Metric | Value |
| --- | ---: |
| 최적화 가능 수량 | 6,434 |
| 목표 대비 부족량 | 3,566 |
| Baseline 대비 생산량 변화 | +6 |
| 물류비 proxy 변화 | -120,000 |
| 위험 변화 | +0.0433 |
| 추가 공장 | 14 |
| 제외 공장 | 14 |
| 재배치 flow | 4 |
| 동결 주문 충돌 | 7 |
| 운송 검토 | 5 |

UI 변화:

- 지도: 남부 항만/물류 disruption corridor 표시
- Active Flow Ledger: 해상 수입 경로와 항만-공장 원료 경로를 함께 확인
- Raw Material / Import Routes: 원료 coverage와 국내 회수/재활용 후보 확인
- Plan Delta: 생산량 변화는 작지만 위험이 올라가므로 `emergency_replan`

로직 변화:

- 항만/남부권 feeder route risk를 반영한다.
- 원료 수급은 해외 수입, 국내 회수, 기존 공장 재고를 합산해 coverage를 계산한다.
- 일부 flow만 바뀌어도 동결 주문과 운송 중 물량 검토가 발생할 수 있다.

발표 멘트:

> "항만 차질은 단순히 길이 막히는 문제가 아니라 희토류 자석, 배터리 소재 같은 원료 투입에도 영향을 줍니다. 그래서 이 케이스에서는 해상 수입 경로와 국내 회수 후보를 같이 봐야 합니다."

## 3. Realtime Logic

실시간성은 다음 5단계로 보이면 된다.

```mermaid
flowchart LR
  A["상황 이벤트 입력"] --> B["시나리오 파라미터 변경"]
  B --> C["v0.9 배정 계산"]
  C --> D["v1.0 Plan Delta 계산"]
  D --> E["지도 / 카드 / 검토 명령 갱신"]
```

| Event input | Changed data field | Algorithm effect | UI effect |
| --- | --- | --- | --- |
| 수요 폭증 | `target_drones_30d` | 부족량과 병목 재계산 | 생산 가능량 / 부족량 카드 변경 |
| 공장권역 위협 | `threat.path`, `risk_radius_km`, `probability` | factory/route risk 상승 | threat corridor, rerouted flow 증가 |
| 항만 차질 | maritime route risk/capacity | 원료 feeder route 비용/위험 반영 | Raw Material / Import Routes 강조 |
| 전력망 저하 | grid availability multiplier | 공장 capa proxy 하향 | Grid / Power Risk 카드 강조 |
| 동결 주문 발생 | frozen order ledger | 계획 변경 가능 범위 축소 | Frozen order conflict 카드 생성 |
| 운송 중 물량 발생 | in-transit shipment ledger | 즉시 재배치 불가 물량 분리 | In-transit review 카드 생성 |

## 4. UI Behavior

현재 구현된 demo behavior:

1. Header에서 scenario를 선택한다.
2. `state.scenarioId`가 바뀐다.
3. `currentPlan()`, `currentOptimizationResult()`, `currentReconfigurationResult()`가 같은 scenario id를 기준으로 데이터를 다시 읽는다.
4. `renderAll()`이 지도, 경로, flow animation, 생산 카드, 조달 카드, Dataset drawer를 다시 그린다.
5. Case ticker가 현재 상황에서 UI/로직/운영자 판단이 무엇인지 한 문단으로 보여준다.

핵심 DOM / JS:

| Area | File / function |
| --- | --- |
| Scenario header tabs | `index.html#scenarioLiveTabs`, `renderScenarioLiveTabs()` |
| Live case ticker | `index.html#caseTicker`, `renderCaseTicker()` |
| Scenario switch | `setScenario()` |
| Auto playback | `toggleScenarioPlayback()`, `advanceScenarioPlayback()` |
| Optimization card | `renderOptimizationResultSummary()` |
| Plan delta card | `renderReconfigurationSummary()` |

## 5. Data Requirements For Next Version

현재 demo는 synthetic/proxy 값으로 충분히 시연 가능하지만, 운영급으로 가려면 다음 데이터가 필요하다.

| Need | Required data |
| --- | --- |
| 실제 도로 거리/시간 | OSRM/VWorld/국토부 도로망 기반 route matrix |
| 차량/운전 인력 비용 | 차량 적재량, 운전자 shift, 유류비, 운행 가능 시간 |
| 공장 capa 검증 | ERP/MES 생산량, 설비, 인력, 교대, QA capacity |
| 전력/에너지 판단 | 공장별 전력 사용량, 에너지 사용량, 탄소배출량, backup power |
| 원료/희토류 | 희토류 자석 재활용/회수 후보, 재고, 등급, 처리 lead time |
| 계획 안정성 | frozen order, WIP, in-transit shipment, switching cost |

## 6. v1.2 Candidate Case

Rare-earth / NdFeB magnet squeeze:

- Trigger: 희토류 자석 또는 NdFeB magnet 재고 survival days가 임계값 아래로 떨어짐
- Data affected: `subcomponent_constraints`, `resource_candidates`, `raw_material_supply_summary`
- Logic change: propulsion capa가 더 강하게 제한되고, 국내 회수/재활용 후보와 allied supply source를 우선 검토
- UI change: Critical Materials, Raw Material / Import Routes, Motor / Propulsion bottleneck card를 동시에 강조

현재 앱에는 희토류/자석 회수 후보와 NdFeB 제약 데이터가 들어가 있지만, 이 케이스만 별도로 v0.9/v1.0 계산한 scenario result는 아직 없다. 따라서 발표에서는 `차기 확장 케이스`로 설명하고, 다음 구현에서 `rare_earth_magnet_squeeze` scenario id를 추가하는 것이 맞다.

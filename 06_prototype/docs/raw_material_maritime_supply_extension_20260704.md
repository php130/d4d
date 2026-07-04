# Raw-Material Maritime Supply Extension

Date: 2026-07-04 KST
Dataset schema: `d4d.drone_production_conversion.v0.8`

## 목적

전시 상황에서 드론 생산전환은 공장 Capa만으로 결정되지 않는다. 각 공장이 보유한 기존 재고, 국내 원료 회수/재활용 후보, 해외 원료 수급로, 수입항 처리, 항만-공장 도로 이동, 드론 용도별 BOM/원료 소요량을 함께 묶어야 생산 가능 수량과 선제 신청 물량을 계산할 수 있다.

이 확장은 다음 질문에 답하기 위한 백데이터와 지도 레이어를 만든다.

- 현재 공장 재고와 국내 원료 후보만으로 30일 목표 물량을 만들 수 있는가?
- 희토류 자석, 배터리/Li 계열, 구리/PCB/커넥터, 복합재 등 병목 원료가 어디서 부족한가?
- 해외 원료가 필요하면 어느 수입항으로 들어와 어떤 공장까지 가야 하는가?
- 항만-공장 이동 거리, 시간, 유류비, 운전 인력 비용은 얼마나 드는가?
- 드론 용도 mix가 바뀌면 부품/원료 소요량이 어떻게 바뀌는가?

## 데이터셋 구성

Top-level additions:

- `raw_material_catalog`: 원자재 6종 정의, 색상, 연결 부품군, 수입 의존도, 검증 필요 항목
- `drone_mission_profiles`: 드론 용도별 안전한 상위 BOM/원료 kg per drone
- `default_drone_mission_mix`: 기본 수요 mix
- `import_ports`: 동해·포항·울산·부산 수입항 후보
- `foreign_material_sources`: 일본 측 원료 source/port demo nodes
- `allied_supply_sources`: 호주·캐나다·대만·미국·일본 협력 원료/부품 source hypothesis
- `maritime_corridor_model`: 공개 시연용 해상 corridor 안전 경계와 waypoint geometry 방식

Scenario-level additions:

- `raw_material_supply_summary`
- `maritime_import_route_segments`
- `port_to_factory_material_routes`
- `factory_capacity_possible_drones_30d`
- `raw_material_constrained_possible_drones_30d`

CSV exports:

- `material_supply_backdata.csv`: 시나리오별 원료 소요/가용/부족/수입의존/가능 드론 수량
- `material_import_routes.csv`: 해상 수입 route와 항만-공장 material feeder route
- `allied_supply_sources.csv`: 우방국/협력국 source, 일본 staging node, 연결 원료/부품, 근거 URL, 검증 필요 항목
- `logistics_route_edges.csv`: 해상 수입, 항만-공장, 국내 자원-공장, 부품공장-조립허브를 합친 통합 물류 route edge 테이블

## 현재 v0.8 산출 상태

| 항목 | 수량 |
| --- | ---: |
| 원자재 카탈로그 | 6 |
| 드론 용도/BOM mission profile | 3 |
| 수입항 후보 | 4 |
| 해외 원료 source node | 6 |
| 우방국/협력국 source hypothesis | 6 |
| 전체 해상 수입 route segment | 18 |
| 전체 항만-공장 material route | 71 |
| 전체 도로성 route edge | 223 |
| OSRM 도로 geometry/road summary 확보 route | 223 |
| 통합 logistics route CSV rows | 241 |
| baseline 해상 수입 route segment | 6 |
| baseline 항만-공장 material route | 24 |

## 원자재 카테고리

| Material ID | 용도 | 연결 부품군 | 수입 의존 |
| --- | --- | --- | --- |
| `ndfeb_magnet_feedstock` | NdFeB 자석 feedstock | propulsion | high |
| `lithium_battery_feedstock` | 배터리 셀/Li feedstock | power | high |
| `copper_electronics_feedstock` | 구리, PCB, 커넥터 | flight stack, harness | medium |
| `lightweight_airframe_feedstock` | 복합재, 탄소, 경량 금속 | airframe | medium |
| `optical_sensor_components` | 광학 센서, 렌즈, 이미징 부품 | sensor payload | high |
| `industrial_polymers_packaging` | 폴리머, 케이스, 포장재 | QA/packaging, assembly | low |

## 지도 UI 반영

앱 지도는 기존 공장/자원/조립허브 레이어를 유지하면서 다음을 추가했다.

- Layers drawer에 `Import / port-to-factory routes` 토글 추가
- 해외 원료 source node marker 추가
- 국내 수입항 marker 추가
- 해상 수입 route polyline 추가. v0.8부터 일본 항만-한국 항만 link는 단순 직선이 아니라 항만별 coarse sea waypoint 기반 geometry를 사용한다.
- 항만-공장 원료 feeder route polyline 추가
- Active Flow Ledger에 해상 수입 route와 항만-공장 원료 route 추가
- Active Flow Ledger와 route popup에 `OSRM routed`, 주요 도로 요약, 거리, 시간, 유류량, 1회 운송비 표시
- Dataset drawer에 `Raw Material / Import Routes` 섹션 추가
- Dataset drawer에 `Allied Supply Sources` 섹션 추가
- 공장 상세 drawer에 해당 공장의 raw-material inbound route 표시

## v0.8 해상 geometry 보정

문제: Maizuru/Niigata처럼 동해 쪽 항만은 크게 어색하지 않았지만, Nagoya/Yokohama/Kobe 등 일본 남·동부 항만은 이전 midpoint 방식에서 일본 육지를 관통하는 선으로 보였다.

해결:

- `SEA_CORRIDOR_WAYPOINTS`를 추가해 source별 해상 waypoint를 명시했다.
- `maritime_route_geometry()`가 source id별 waypoint를 우선 사용하도록 수정했다.
- 해상 `distance_nm`은 더 이상 직선거리 보정치가 아니라 waypoint polyline 구간별 haversine 합산값으로 계산한다.
- `route_geometry_source = coastal_waypoint_corridor_v0.2`를 route와 CSV에 기록한다.

예시 baseline route:

| Source | Route | Geometry points | Distance |
| --- | --- | ---: | ---: |
| `src_jp_nagoya_composite` | Nagoya -> Ulsan | 8 | 528.7 nm |
| `src_jp_yokohama_optics` | Yokohama -> Pohang | 9 | 685.0 nm |
| `src_jp_kobe_polymers` | Kobe -> Busan | 7 | 333.3 nm |

주의: 이 waypoint는 지도상 land-crossing을 피하기 위한 공개 데모 corridor다. 실제 운항/배선/보험/항만 slot 판단에는 AIS, port call, 선사 schedule, 승인된 maritime routing provider가 필요하다.

## 우방국/협력국 source hypothesis

이번 버전은 “국가 -> 일본 staging -> 한국 수입항 -> 국내 공장”으로 확장할 수 있도록 `allied_supply_sources`를 추가했다. 지도에는 일본-한국 구간만 기본 표시하고, 원거리 국가 source는 Dataset drawer/CSV에서 확인하도록 분리했다. 전 세계 marker를 기본 지도 bounds에 넣으면 한국·일본 판단 화면이 흐려지기 때문이다.

| Source | 연결 원료/부품 | 일본 staging |
| --- | --- | --- |
| Australia lithium/nickel | battery feedstock, battery cell | Niigata, Kobe |
| Australia rare earths | Nd-Pr/NdFeB magnet feedstock, motors | Maizuru |
| Canada battery minerals | lithium/copper feedstock, battery/electronics | Niigata |
| Taiwan semiconductor kits | MCU/IMU/CMOS/RF, FC/ESC/camera/VTX/RX | Yokohama, Kobe |
| United States semiconductors/critical materials | semiconductor kits, optical sensors, battery/magnet inputs | Yokohama |
| Japan midstream staging | optics, electronics, copper, magnet, battery, composite buffers | all Japan source nodes |

근거 자료:

- Japan METI: Japan-Korea Critical Minerals High Level Dialogue, 2025-12-17
- Korea MOFA: Korea chairmanship of MSP, 2024-06-27
- Korea MOFA: Australia NRFC investment in Arafura Nolans rare earths project, 2025-01-23
- Geoscience Australia: Critical minerals list and production/resource context, updated 2026-05-15
- Austrade: Opportunities in Korea for Australian critical minerals
- Canada: Canadian Critical Minerals Strategy annual report 2024
- Taiwan MOEA: semiconductor supply-chain partnerships and non-red drone supply-chain alliance
- USTR: supply-chain work covering semiconductors, batteries, critical minerals/materials, and permanent magnets

## 안전 경계

이 확장은 물류/생산 의사결정용 공개 시연 모델이다.

- 실제 선박 운용, 호송, 작전 경로, 군사적 보호 계획을 제공하지 않는다.
- 해상 route geometry는 coarse corridor이며 실제 선박 운용 지시로 쓰면 안 된다.
- 도로 route geometry는 OSRM/OpenStreetMap 기반 prototype 결과이며, 실제 배차/운송 계약 전에는 Kakao/NAVER/Tmap/자체 OSRM 등 승인된 provider로 재검증해야 한다.
- 해외 source, 월별 capacity, 항만 선택은 demo assumption이다.
- 우방국 source는 public research 기반 hypothesis이며 계약된 공급선, 수출허가, 통관 가능성, 품질 등급을 의미하지 않는다.
- 실제 적용에는 공급계약, 통관, 항만 처리능력, 품질 등급, 위험보험, 운송 보안, 법적 동원 권한 검증이 필요하다.

## 검증 결과

검증일: 2026-07-04 KST

- `python3 -m py_compile 06_prototype/scripts/generate_drone_production_conversion_dataset.py`: pass
- `node --check 06_prototype/app/drone_production_conversion/assets/app.js`: pass
- JSON dataset check: schema `d4d.drone_production_conversion.v0.8`
- Public URL data check: schema `d4d.drone_production_conversion.v0.8`, raw materials `6`, maritime routes `18`, material road routes `71`, allied sources `6`
- Public URL Nagoya route check: `8` geometry points, `coastal_waypoint_corridor_v0.2`, `528.7 nm`
- Road route quality check: `223/223` road-like route edges are `OSRM public demo server` routed and include `route_road_summary`
- Static UI check: `assets/app.js` passes `node --check`; browser visual check was blocked by local enterprise browser policy, so route geometry was verified through public JSON/CSV.

Public URLs:

- https://fair-extreme-gmbh-humanities.trycloudflare.com
- https://fair-extreme-gmbh-humanities.trycloudflare.com/data/drone_production_conversion_dataset.json
- https://fair-extreme-gmbh-humanities.trycloudflare.com/data/material_supply_backdata.csv
- https://fair-extreme-gmbh-humanities.trycloudflare.com/data/material_import_routes.csv
- https://fair-extreme-gmbh-humanities.trycloudflare.com/data/allied_supply_sources.csv
- https://fair-extreme-gmbh-humanities.trycloudflare.com/data/logistics_route_edges.csv

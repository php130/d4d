# Wartime Drone Production Conversion System

Date: 2026-07-04 KST

Status: new pivot candidate

Working title:

- Korean: 전시 드론 생산전환 의사결정 시스템
- English: Drone Production Continuity & Factory Conversion Planner
- Short name: D-Factory / DroneForge Korea

## 1. Direction Verdict

이 방향은 기존 지휘참모 대시보드나 드론 운용 아이디어보다 해커톤 아이템으로 더 선명하다.

이전 아이디어는 "상황을 잘 보는 COP"에 가까웠고, 시연이 자칫 일반 대시보드처럼 보일 위험이 있었다. 새 아이디어는 "전시 드론 수요가 폭증했을 때 어느 공장, 어느 부품, 어느 경로를 조합해야 생산량을 보존할 수 있는가"라는 구체적인 군수·지속지원 판단을 돕는다.

Track fit:

- T3 Battle Network, C2 & Sustainment: 전시 생산·수급·배분 의사결정
- T1 Autonomy, Unmanned Systems & Counter-UAS: 드론 공급 기반
- T2 OSINT & Defense Intelligence: 공개 공장·조달·공급망 데이터 융합

Best framing:

> 드론을 만드는 법이 아니라, 국가 위기 상황에서 공개 제조 데이터와 비상대비 자원관리 논리를 활용해 드론 생산망을 빠르게 재편하는 의사결정 지원 시스템.

Safety boundary:

- 무장, 탄두, 공격 임무, 세부 제작 사양은 다루지 않는다.
- BOM은 비무장 소형 정찰/훈련용 드론의 공개적·상위 부품군 수준으로만 사용한다.
- 실제 업체를 "동원 대상"이나 "군사용 전환 가능"으로 단정하지 않고, "후보/검증 필요"로 표시한다.

## 2. Why This Is Credible

### Korean institutional basis

행정안전부 비상대비 자원관리 설명은 전쟁 등 비상시에 필요한 인력, 군수·관수·민수용 물자 소요를 제출받고, 현지방문·서면조사로 공급능력을 판단한 뒤 기관·업체별, 대상자원별, 단계별, 지역별 동원 책임량을 부여해 동원계획을 수립한다고 설명한다.

Source: https://www.mois.go.kr/frt/sub/a06/b12/emergencyresource/screen.do

국가기록원 물자동원 설명은 통제운영을 물자의 생산·수리·가공·유통과정 등을 필요한 범위에서 통제하는 방식으로 설명한다. 즉 전시 생산전환은 법제도상 완전히 낯선 개념이 아니다.

Source: https://www.archives.go.kr/next/newsearch/listSubjectDescription.do?id=010230&sitePage=

### Public factory data basis

한국산업단지공단/팩토리온의 `공장등록생산정보조회서비스`는 회사명, 주소, 고용인원, 공장 등록일자, 업종명, 주생산품, 대표업종코드, 산업단지명을 제공한다. 전국등록공장현황 CSV는 회사명, 단지명, 생산품, 공장주소를 제공한다.

Sources:

- https://www.data.go.kr/data/15087611/openapi.do
- https://www.data.go.kr/data/15105482/fileData.do

Local feasibility check on `한국산업단지공단_전국등록공장현황_등록공장현황자료_20241231`:

- Total rows: 217,048 factories
- Direct drone keyword candidates: 371
- Electronics/PCB/control/communications candidates: 9,936
- Battery/power candidates: 1,905
- Motor/propulsion candidates: 1,249
- Camera/optical/video candidates: 3,774
- Airframe/material/molding candidates: 13,461
- Wire/harness/connector candidates: 2,113

This is only keyword-based and contains false positives. It proves dataset viability, not final eligibility.

### Contemporary wartime drone precedent

Ukraine's Ministry of Defence stated that by the end of 2024 it and the State Service of Special Communications and Information Protection procured over 1.5 million drones, and that Ukraine's 2025 defense industry capacity was approximately 4.5 million FPV drones.

Source: https://mod.gov.ua/en/news/glib-kanievskyi-in-2025-the-ministry-of-defence-plans-to-procure-4-5-million-fpv-drones

Ukraine also describes DOT-Chain Defence as a marketplace-like procurement flow where military units select equipment, order directly from manufacturers, and receive delivery while the Defence Procurement Agency handles payment and bureaucracy. In 2025 the MoD stated the average time from order to delivery was 10 days and planned to shift 70% of drone procurement to the platform.

Source: https://mod.gov.ua/en/news/45-billion-from-partners-over-3-million-strike-drones-more-ukrainian-weapons-key-ministry-of-defence-highlights

Brave1 Market describes a marketplace for frontline units and manufacturers, with UAVs, UGVs, EW/SIGINT, components, AI technologies, software, and other solutions listed.

Source: https://brave1.gov.ua/ministry-of-digital-transformation-and-brave1-launch-defense-technology-marketplace-for-the-military

### Analogous supply-chain matching precedents

Germany's SVI-Connect is a protected B2B platform for the security and defense industry. Its purpose is market transparency, structured partner search, and supply-chain networking; direct procurement is not the platform's role.

Source: https://www.svi-connect.com/

NIST MEP Supplier Scouting lets government agencies or companies submit a needed item, then searches the MEP National Network for U.S. manufacturers with relevant capabilities and business interest. NIST says this typically returns results in 30-45 days.

Source: https://www.nist.gov/mep/supply-chain/supplier-scouting

America Makes' crisis production response during COVID-19 used an online Exchange portal to match manufacturing capabilities with PPE needs and coordinated review of designs for safe use.

Source: https://www.americamakes.us/america-makes-completes-successful-scenario-testing-for-crisis-response-program/

## 3. Product Hypothesis

When wartime drone demand exceeds ordinary procurement capacity, staff need a system that decomposes drone demand into part families, matches those part families to public and verified manufacturing capacity, then proposes a production-conversion and assembly plan with evidence, confidence, and logistics constraints.

The product should answer:

> "If we need 10,000 additional small drones in 30 days, which Korean factories are candidate suppliers for each non-sensitive part family, which assembly hubs should receive them, and what bottleneck blocks output first?"

## 4. MVP User

Primary user:

- 국방부/방사청/지자체/산업부 합동 전시 생산전환 셀
- 군수·조달·작전지속 담당 참모
- 산업단지/제조업 지원기관 실무자

User decision:

- Which factories should be contacted first for verification?
- Which part family is the bottleneck?
- Which region is resilient if one industrial cluster is disrupted?
- Which assembly route minimizes time, risk, and supplier concentration?

## 5. Data Model

Core entities:

| Entity | Purpose | Key fields |
| --- | --- | --- |
| `DroneDemand` | Required output by type and time window | model_family, quantity, deadline, priority_area |
| `PartCategory` | Non-sensitive part family | airframe, propulsion, power, flight_stack, sensor_payload, datalink, harness, fastener, packaging, test |
| `BOMLine` | High-level parts per drone | part_category, quantity_per_drone, substitution_allowed, criticality |
| `Factory` | Public factory record | factory_id, company_name, address, lat/lon, industry_code, product_text, industrial_complex |
| `CapabilityTag` | Inferred or verified capability | category, evidence_source, confidence, false_positive_risk |
| `ConversionProfile` | How hard conversion may be | setup_days, tooling_needed, QA_required, training_required |
| `AssemblyHub` | Final or sub-assembly node | location, capacity, accepted_part_categories |
| `SupplyRoute` | Movement from factory to hub | distance, travel_time, disruption_risk, weather/traffic context |
| `Constraint` | Bottleneck rule | part_category, max_capacity, lead_time, import_dependency, QA_gate |
| `PlanScenario` | What-if plan | demand, selected_factories, routes, bottlenecks, output_curve |

## 6. High-Level Drone BOM for Demo

Use a safe, non-weaponized, high-level BOM. Do not include tactical specs, explosive payload, or detailed build instructions.

Example small quadcopter category BOM:

| Part family | Demo quantity per drone | Factory capability proxy |
| --- | ---: | --- |
| Airframe / frame | 1 set | plastic injection, carbon/composite, aluminum machining, molding |
| Propulsion | 4 motor sets | small motor, BLDC, precision machining, electronics assembly |
| Propellers / rotor consumables | 4+ units | plastic injection, composite molding |
| Power | 1 battery pack + charging support | battery pack, BMS, power electronics, chargers |
| Flight stack | 1 control board set | PCB, SMT, embedded electronics, sensors |
| Navigation/sensing | 1 sensor set | GNSS module, IMU, camera, optical module, sensor manufacturing |
| Datalink / communications | 1 radio/control link set | communications equipment, antenna, RF module, cable assembly |
| Wiring/harness/connector | 1 set | cable, harness, connector, wire assembly |
| Fasteners / brackets / packaging | 1 set | metalworking, brackets, cases, packaging |
| Test / QA | 1 pass | electronics test, mechanical inspection, environmental test |

For the hackathon, quantity is only used to run the matching and bottleneck logic. It should not be presented as a real military manufacturing recipe.

## 7. Public Data Source Plan

| Need | Recommended source | Use | Limitation |
| --- | --- | --- | --- |
| Factory candidate list | 한국산업단지공단 전국등록공장현황 CSV | Base factory list: company, product, address | No equipment list, no live capacity |
| Production/industry detail | 한국산업단지공단 공장등록생산정보조회서비스 | Company, address, employees, registration date, industry/product codes | API approval/call behavior must be verified |
| Land/building scale | 한국산업단지공단 공장등록필지정보조회서비스 | Land/building area proxy | Company/factory matching needed |
| Region-rich factory data | Local gov factory APIs, e.g. 경기도 공장등록 현황 | Some sources include WGS84 coordinates, employees, registration date, product, industry | Coverage varies by region |
| Defense baseline | 산업부/방사청 방산업체 현황 | Defense-qualified anchor suppliers | Small list; not drone-specific |
| Procurement signals | 조달청 나라장터 입찰공고/발주계획/계약 | Demand and supplier history for drones, batteries, electronics | API auth and next-gen Nara issues need handling |
| Smart manufacturing maturity | 스마트공장 공급기업/우수사례, KAMP manufacturing datasets | Proxy for digital/manufacturing readiness and process taxonomy | Usually not per-factory equipment inventory |
| Geocoding/map | VWorld or OSM/Nominatim fallback | Factory map, route distance | API keys must stay server-side |
| Road/weather/disruption | ITS traffic, KMA, SafetyData | Route risk context | Not essential for first MVP |
| Company enrichment | DART, KIPRIS, company websites | Public company status, patents, product evidence | Web crawling must be restrained and cited |

## 8. Matching Logic

### Capability extraction

Convert `company_name`, `product_text`, `industry_name`, and `industry_code` into part-family capability tags.

Example rules:

- `드론`, `무인기`, `UAV` -> direct drone / final assembly candidate
- `PCB`, `SMT`, `회로기판`, `전자부품`, `제어기` -> flight stack / electronics
- `배터리`, `전지`, `BMS`, `전원공급` -> power
- `모터`, `BLDC`, `프로펠러`, `감속기` -> propulsion
- `카메라`, `광학`, `렌즈`, `CCTV`, `영상` -> sensor payload
- `케이블`, `하네스`, `커넥터`, `전선` -> wiring
- `사출`, `금형`, `복합재`, `카본`, `알루미늄` -> airframe/material

False-positive defenses:

- Do not match address/building names for capability.
- Treat company-name-only keyword matches as low confidence unless product or industry also supports it.
- Exclude obvious unrelated meanings, e.g. `BMS프린텍` as print shop unless product text mentions battery management or power electronics.
- Keep all inferred tags as `candidate`, not `verified`.

### Factory scoring

Recommended v0 score:

```text
 product/industry match confidence
+ part criticality fit
+ employee/area scale proxy
+ industrial-cluster redundancy
+ geocoding confidence
- distance to selected assembly hub
- supplier concentration risk
- data staleness
- false-positive risk
```

### Plan optimization

MVP:

- Greedy rank factories by part category.
- Select top N per part family.
- Compute route distance to 1-3 assembly hubs.
- Find bottleneck as `min(part_supply / BOM_quantity_per_drone)`.

Post-MVP:

- Mixed-integer or min-cost flow optimization.
- Multi-scenario resilience: factory outage, port disruption, battery shortage, route closure.
- Human-in-the-loop approval and audit trail.

## 9. Demo UI

The existing Leaflet-based Korea map prototype can be reused. Replace the civil-infra layers with production-conversion layers.

Map layers:

- Direct drone/final assembly candidates
- Electronics/PCB/control candidates
- Battery/power candidates
- Motor/propulsion candidates
- Airframe/material/molding candidates
- Sensor/camera candidates
- Harness/connector candidates
- Assembly hubs
- Route/risk lines
- Bottleneck heatmap by region

Right panel:

- Selected factory candidate
- Public evidence: product text, industry, source, data date
- Inferred possible drone part family
- Confidence and false-positive warnings
- Verification checklist

Bottom panel:

- Demand scenario
- BOM bottleneck bar
- Proposed supplier set
- Route plan
- "What changes if Gyeonggi cluster capacity drops 30%?" scenario toggle

## 10. Recommended Hackathon MVP

### Day 0 preparation

1. Download and version `전국등록공장현황` CSV.
2. Build keyword/rule classifier for part-family tags.
3. Geocode a capped candidate set, e.g. top 1,000-3,000 records.
4. Create synthetic high-level drone BOM and demand scenarios.
5. Reuse the current Korea Leaflet app as the map shell.

### Day 1 build

1. Map candidate factories by category.
2. Show region-level supply capacity proxy.
3. Add assembly hub selector.
4. Compute bottleneck and route recommendations.
5. Generate one-page conversion brief.

### Demo story

1. Staff enters: "30 days, 10,000 small ISR/training drones, Seoul/West Coast priority."
2. System decomposes demand into safe part families.
3. It finds direct drone makers and non-drone factories that may supply airframe, electronics, power, propulsion, sensors, harness, packaging, and QA.
4. Map shows candidate clusters and route risk.
5. Bottleneck view says: "battery/power and flight-stack electronics are limiting output; here are the top verification calls."
6. Brief export lists evidence, assumptions, and what needs human verification.

## 11. Key Risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Public data lacks equipment age and machine inventory | User specifically wants 보유설비/연식 | Mark as unknown; infer only from registration date, industry/product, area; add verification workflow |
| Keyword false positives | Factory names and generic products can mislead | Use confidence, product-only matching, negative dictionaries, manual review queue |
| Sensitive defense implications | Could look like weapon production | Frame as defensive sustainment and non-weaponized drone supply; avoid payload/munition details |
| Real company reputational risk | We should not imply a company can/should be militarized | Use "candidate for verification" language and anonymize demo if needed |
| Logistics oversimplification | Distance alone is not routing capacity | MVP uses distance; later add traffic, road disruptions, port/warehouse nodes |
| API approval instability | data.go.kr APIs may be unauthorized or rate-limited | Keep file-data fallback and snapshot versioning |

## 12. Pitch Summary

> 전쟁이 나면 드론 수요는 하루 단위로 바뀌지만, 공급망은 공장·부품·원자재·품질검사·물류가 얽혀 있어 사람이 엑셀로 재편하기 어렵다. 우리는 공개 공장등록 데이터와 조달·지도·비상대비 자원관리 논리를 연결해, 드론 1대의 상위 부품군을 생산 가능한 국내 공장 후보와 매칭하고, 대한민국 지도 위에서 병목과 최적 수합 경로를 보여주는 전시 생산전환 의사결정 시스템을 만든다.

## 13. Immediate Next Steps

1. Create a `drone_production_conversion` dataset generator under `06_prototype/scripts/`.
2. Store the public CSV snapshot under `03_data/raw/` or keep only a processed, capped sample under `03_data/samples/`.
3. Build `factory_candidate.json` with part-family tags and confidence scores.
4. Fork the current `korea_civil_infra_cop` Leaflet app into `06_prototype/app/drone_production_conversion/`.
5. Prepare a 3-minute pitch around "bottleneck-first sustainment", not "more dashboard".


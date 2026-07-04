# Factory-Level Backdata Feasibility

Date: 2026-07-04
Project: D4D drone production conversion pipeline

## 결론

공장별 백데이터는 구축 가능하다. 다만 공개 데이터만으로 모든 공장의 실제 전력사용량, 실가동률, 여유 설비, 재고, 생산 Capa를 확정할 수는 없다. 따라서 데이터셋은 아래 3등급으로 분리해서 구축해야 한다.

1. Direct public evidence: 공장명, 위치, 업종, 생산품, 원자재, 면적, 종업원 수처럼 공장등록/공공데이터에서 직접 확보 가능한 항목.
2. Matched public evidence: 온실가스/에너지 다소비 사업자처럼 일부 대형 사업장에 대해 업체명/주소 매칭으로 붙일 수 있는 항목.
3. Estimated decision proxy: 전력/에너지 지역 통계, 업종 특성, 면적, 종업원, 생산품 키워드, 물류 접근성을 이용해 공장별 Capa 후보 점수로 추정해야 하는 항목.

## 공장별 필드별 구축 가능성

| 데이터 항목 | 공장별 백데이터 구축 | 판단 |
| --- | --- | --- |
| 공장명, 주소, 위치, 업종, 생산품 | 가능 | 전국 공장등록/산업단지·공장 표준데이터에서 직접 구축 가능 |
| 제조 가능한 드론 부품 분류 | 가능 | 생산품/업종/원자재 키워드를 `propulsion`, `power`, `flight_stack`, `airframe`, `harness`, `qa_packaging`, `drone_assembly` 등으로 매핑 |
| 공장 규모 | 부분 가능 | 제조시설면적, 부지면적, 건축면적, 종업원 수가 있으면 직접 사용 |
| 보유 설비 | 부분 가능 | 일부 지자체 데이터에는 설비 내용이 있으나 전국 단위로 균일하지 않음. 현장/기업자료 검증 필요 |
| 설비 연식 | 어려움 | 공개 공장등록 데이터에 균일하게 존재하지 않음. 설립연도, 등록일, 인증, 특허, 장비 도입 보조사업 이력으로 보조 추정 |
| 전력사용량 | 부분 가능 | KEPCO 공개 데이터는 주로 지역/법정동/업종 단위라 개별 공장 직접값은 제한적 |
| 에너지사용량 | 부분 가능 | 에너지다소비사업자, 산업부문 통계, 일부 마이크로데이터를 대형 사업장 중심으로 매칭 가능 |
| 탄소배출량 | 부분 가능 | NGMS/GIR 명세서 또는 할당대상업체 공개자료로 대형 배출업체 중심 매칭 가능 |
| 생산 Capa | 직접 공개는 어려움 | 면적, 종업원, 업종 적합도, 에너지 proxy, 납품/인증/특허/물류 점수로 `capacity_index`와 신뢰도 산출 |
| 재고, WIP, 수주/동결 물량 | 공개 데이터로 어려움 | 해커톤 데모에서는 시나리오 데이터로 구성, 실제 서비스는 ERP/MES/조달/현장 신고 연동 필요 |
| 희토류/배터리/금속 회수 가능 공장 | 가능 | 공장등록 생산품/원자재/업종 키워드와 재활용·폐기물 처리 관련 공개자료로 후보군 구축 가능 |
| 항만-공장 도로 거리/시간/비용 | 가능 | 좌표 기반 라우팅 API 또는 OSRM/ORS로 도로 거리, 시간, 유류비, 기사 시간비 산출 |

## 권장 데이터 모델

### factory_master

- `factory_id`
- `company_name`
- `address_public`
- `lat`, `lon`
- `province`, `city`
- `industry_code`, `industry_name`
- `product_text`
- `raw_materials_text`
- `part_category`
- `source`, `source_row`

### factory_capacity_profile

- `capacity_tier`: A/B/C/D
- `capacity_index`
- `capacity_confidence`
- `recommended_role`: primary / surge / backup / verify
- `predicted_output_units_30d`
- `nominal_daily_output_units`
- `surge_daily_output_units`
- `setup_days_estimate`
- `estimated_yield_rate`
- `missing_evidence`
- `verification_questions`

### factory_energy_profile

- `energy_match_type`: direct_company_match / direct_site_match / regional_industrial_proxy / unknown
- `reported_year`
- `reported_energy_use_toe`
- `reported_ghg_emissions_tco2e`
- `regional_industrial_electricity_mwh`
- `estimated_power_intensity_score`
- `capacity_evidence_score`
- `limitations`

### material_supply_profile

- `material_id`
- `material_label`
- `feeds_part_categories`
- `kg_per_drone_weighted`
- `required_kg_30d`
- `domestic_resource_supply_kg`
- `import_supply_kg_30d`
- `existing_factory_inventory_kg`
- `shortage_kg_30d`
- `coverage_ratio`

### factory_route_edges

- `from_node_id`
- `to_node_id`
- `route_type`
- `distance_km`
- `duration_min`
- `fuel_liters_per_trip`
- `estimated_trip_cost_krw`
- `routing_status`

## 현재 D4D v0.6 반영 상태

- 최신 데이터셋 schema: `d4d.drone_production_conversion.v0.6`
- 데모 공장: 180개
- 공장 Capa profile 부여: 180개
- 원천 공장 후보 풀: 29,616개
- Capa 산정용 공개 공장 row: 198,235개
- 직접 에너지/배출 매칭 공장: 15개
- 지역/업종 에너지 proxy 적용: 나머지 공장
- 원자재 카탈로그: 6종
- 수입항 후보: 4개
- 해외 원자재 소스: 6개
- 해상 수입 route segment: 18개
- 항만-공장 material route: 71개

생성 CSV:

- `06_prototype/app/drone_production_conversion/data/factory_capacity_backdata.csv`
- `06_prototype/app/drone_production_conversion/data/full_factory_candidate_capacity_backdata.csv`
- `06_prototype/app/drone_production_conversion/data/factory_route_capacity_edges.csv`
- `06_prototype/app/drone_production_conversion/data/factory_operational_state.csv`
- `06_prototype/app/drone_production_conversion/data/material_supply_backdata.csv`
- `06_prototype/app/drone_production_conversion/data/material_import_routes.csv`

## 의사결정에서의 해석

전력사용량이 많은 공장을 생산량이 높은 공장으로 보는 것은 보조 지표로는 유효하다. 하지만 단독 기준으로 쓰면 위험하다.

- 전력사용량이 높다는 것은 실제 생산 규모가 크다는 신호일 수 있다.
- 동시에 공정이 비효율적이거나 에너지 집약도가 높은 업종이라는 뜻일 수도 있다.
- 이미 풀가동 중이면 전시 전환 여유 Capa는 오히려 낮을 수 있다.
- 드론 부품 생산 가능성은 전력보다 설비 적합도, 품질 인증, 정밀가공 가능성, 인력, 원자재 재고, 물류 접근성이 함께 봐야 한다.

따라서 추천 산식은 다음과 같다.

```text
capacity_index =
  0.30 * production_fit_score
+ 0.20 * physical_scale_score
+ 0.15 * workforce_score
+ 0.15 * energy_operating_scale_score
+ 0.10 * logistics_access_score
+ 0.05 * certification_quality_score
+ 0.05 * transaction_history_score
```

전력/에너지는 `energy_operating_scale_score`로 넣되, 최종 판단은 `capacity_confidence`와 `missing_evidence`를 함께 표시해야 한다.

## 주요 공개 데이터 소스

- 공장 기본정보: 공공데이터포털 `전국산업단지및공장정보표준데이터`, 한국산업단지공단 `전국등록공장현황`
- 전력 proxy: 한국전력공사 `산업분류별 법정동별 전력사용량`, `업종별 전력사용량`
- 에너지 proxy/direct 후보: 한국에너지공단 `에너지다소비사업자 에너지 사용 현황`, `에너지사용 및 온실가스배출량 통계`
- 탄소배출 direct 후보: 온실가스종합정보센터/NGMS `명세서배출량정보공개`, `할당대상업체지정`
- 생산 규모 보조지표: KOSIS `광업제조업조사`

## 발표용 한 줄

공개 데이터만으로 공장별 실제 Capa를 확정하는 것은 어렵지만, 공장등록정보, 면적·종업원 수, 업종/생산품 적합도, 대형 사업장 에너지·배출 매칭, 지역 전력 proxy, 도로 물류비를 결합하면 전시 생산전환 후보 공장을 신뢰도와 검증 필요 항목이 붙은 백데이터로 구축할 수 있다.

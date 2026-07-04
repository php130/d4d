# Factory Capacity Backdata Plan

Date: 2026-07-04 KST

## Purpose

The drone production-conversion prototype should not claim exact factory output from public data alone. Public sources can, however, support a defensible per-factory capacity evidence layer:

> Which factories are likely to have enough scale, workforce, operating history, technical fit, and logistics access to become priority verification targets for drone-part production conversion?

This document defines which per-factory backdata can be built, which data sources support it, how to join it to the existing factory candidates, and how it should appear in the demo.

## Feasibility Summary

| Backdata family | Factory-level buildability | Confidence | Recommended use |
| --- | --- | --- | --- |
| Factory registry identity, product, industry, address | Build now | High | Base node identity and capability tagging |
| Building/land/factory scale | Build now where fields exist | Medium-high | Physical scale proxy |
| Employee/workforce scale | Build now from registry and insurance APIs where matched | Medium | Labor capacity proxy |
| Government procurement / delivery history | Build with API key and company-name matching | Medium | Evidence of real production and delivery execution |
| Financial scale | Build for legally matched corporations | Medium | Company size and continuity proxy |
| Certification / product compliance | Build with manufacturer-name matching | Medium | QA and regulated-product evidence |
| Patent / IP / design ownership | Build with company-name or corporation identifier matching | Low-medium | Technical capability signal, not output capacity |
| Energy / emissions | Build partially | Low-medium | Operating-scale and energy-risk evidence, not capacity proof |
| Exact equipment inventory, spare line capacity, live utilization | Not available from open public data | Low | Verification checklist item only |
| Exact monthly drone-part output capacity | Not directly available | Low | Estimate as model output, never as verified fact |

## Implemented v0.5 Backdata

The prototype now builds `factory_capacity_profile` for every demo factory candidate from the richer Korea Industrial Complex Corporation `전국등록공장현황_20200229` file. This is separate from the newer lightweight 2024 registry snapshot used earlier for broad product/address scanning.

Implemented fields:

- `factory_manage_no`
- `industry_code`, `industry_name`
- `raw_materials_text`
- `factory_size_label`
- `factory_scale.employee_total`
- `factory_scale.land_area_m2`
- `factory_scale.manufacturing_area_m2`
- `factory_scale.auxiliary_area_m2`
- `factory_scale.building_area_m2`
- `factory_capacity_profile.capacity_tier`
- `factory_capacity_profile.capacity_index`
- `factory_capacity_profile.capacity_confidence`
- `factory_capacity_profile.predicted_output_units_30d`
- `factory_capacity_profile.evidence.production_fit`
- `factory_capacity_profile.evidence.physical_scale`
- `factory_capacity_profile.evidence.workforce_scale`
- `factory_capacity_profile.evidence.energy_operating_scale`

Current v0.5 status:

| Item | Value |
| --- | ---: |
| Rich capacity source rows | 198,235 |
| Full factory candidate pool | 29,616 |
| Pipeline shortlist rows | 8,829 |
| Map-visible factories with employee count | 180 / 180 |
| Map-visible factories with manufacturing area | 180 / 180 |
| Direct factory energy matches in map layer | 15 |

The route-planning algorithm now carries `capacity_index`, `capacity_confidence`, and `capacity_tier` into each selected supplier row, so production-volume allocation is tied to the same evidence shown in the UI.

Exported algorithm tables:

| File | Rows | Purpose |
| --- | ---: | --- |
| `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/full_factory_candidate_capacity_backdata.csv` | 29,616 | Full candidate pool with capacity tier, predicted 30-day output, workforce, area, manufacturing-speed, energy, and grid-risk evidence |
| `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_pipeline_candidate_shortlist.csv` | 8,829 | Scenario/category shortlist for dynamic pipeline planning before expanding expensive road-route matrices |
| `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_capacity_backdata.csv` | 180 | One row per map-visible factory with capacity tier, predicted 30-day output, workforce, area, energy, and evidence scores |
| `/Users/mollykim/projects/D4D/03_data/samples/drone_production_conversion/factory_route_capacity_edges.csv` | 126 | Scenario-specific selected supplier edges with capacity, adjusted capacity, hub, road distance, duration, fuel, cost, risk, and route status |
| `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/full_factory_candidate_capacity_backdata.csv` | 29,616 | Public app-served copy of the full candidate pool |
| `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/factory_pipeline_candidate_shortlist.csv` | 8,829 | Public app-served copy of the dynamic pipeline shortlist |
| `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/factory_capacity_backdata.csv` | 180 | Public app-served copy of the map-visible factory capacity table |
| `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion/data/factory_route_capacity_edges.csv` | 126 | Public app-served copy of the capacity-route edge table |

These CSVs make the production-volume and supply-route algorithm auditable without requiring consumers to parse the full nested JSON dataset.

Important split:

- The route/supplier plan now selects factories from the full 29,616-row candidate pool.
- The map layer is bounded to 180 factories for usability, but it always includes every factory selected by the full-pool plans and resource feeder routes.

## Current Base Table

The current demo dataset already carries these fields per factory:

| Existing field | Meaning | Status |
| --- | --- | --- |
| `id` | Stable demo factory ID | Built |
| `company_name`, `display_name` | Public company/factory name | Built |
| `product_text` | Public production-item text | Built |
| `address_public`, `province`, `city`, `lat`, `lon` | Public location and derived coordinates | Built |
| `complex_name` | Industrial complex text when present | Built, often sparse |
| `category`, `category_label` | Drone part-family match | Built by keyword/rule extraction |
| `confidence`, `confidence_reasons` | Product-text matching confidence | Built |
| `capacity_units_30d` | Current demo capacity estimate | Built as synthetic/proxy estimate |
| `energy_profile` | Direct NGMS match or regional energy proxy | Built, sparse direct matches |

The next step is to replace the single `capacity_units_30d` proxy with a structured `factory_capacity_profile`.

## Proposed Factory Backdata Schema

```json
{
  "factory_capacity_profile": {
    "profile_version": "d4d.factory_capacity_profile.v0.1",
    "capacity_tier": "A|B|C|D|VERIFY_ONLY",
    "capacity_index": 0.0,
    "capacity_confidence": 0.0,
    "recommended_role": "primary|surge|backup|verification_queue",
    "evidence": {
      "production_fit": {},
      "physical_scale": {},
      "workforce_scale": {},
      "transaction_history": {},
      "financial_scale": {},
      "certification_quality": {},
      "technology_signal": {},
      "energy_operating_scale": {},
      "logistics_access": {}
    },
    "missing_evidence": [],
    "verification_questions": []
  }
}
```

## Source-to-Field Plan

| Source | Link | Key fields to extract | Join key | Backdata fields |
| --- | --- | --- | --- | --- |
| 한국산업단지공단 전국등록공장현황 | https://www.data.go.kr/data/15106170/fileData.do | company name, product item, industry name/code, raw materials, address, factory management number, employees, land/building/manufacturing area where present | factory management number, normalized company name + address | `production_fit`, `physical_scale`, base `workforce_scale` |
| 경기도 공장등록 현황 | https://www.data.go.kr/data/15057023/openapi.do | company name, product, industry, land area, building area, employees, factory size, registration date, WGS84 coordinates | normalized company name + road/lot address | regional enrichment for Gyeonggi candidates |
| 근로복지공단 고용/산재보험 현황정보 | https://www.data.go.kr/data/15059256/openapi.do | workplace name, address, worker count, insurance establishment date, insurance status | normalized workplace name + address | `workforce_scale`, operating-status freshness |
| 조달청 나라장터 계약정보서비스 | https://www.data.go.kr/data/15129427/openapi.do | supplier/company, product name, contract date, amount, demand agency, contract type | normalized supplier name; business ID if accessible | `transaction_history` |
| 조달업체별 계약납품요구 실적통계 | https://www.data.go.kr/data/15050795/fileData.do | supplier, yearly delivery/order count, amount | supplier ID or normalized company name | production/delivery execution proxy |
| 금융위원회 기업 재무정보 | https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15043459 | revenue, assets, liabilities, capital, operating profit | corporation registration number where available | `financial_scale` |
| KTL 안전인증제품정보 | https://www.data.go.kr/data/15095131/fileData.do | manufacturer, product category/name/model, certification number/date/result | normalized manufacturer name | `certification_quality` |
| 지식재산처 등록원부 실시간 정보 조회 | https://www.data.go.kr/data/15124946/openapi.do | applicant/right holder, patent/design/trademark record, registration data | company/corporation identifier or normalized applicant name | `technology_signal` |
| NGMS emissions/energy public data | https://www.data.go.kr/data/15148894/fileData.do | company/site name, reported energy use, emissions, year | normalized company/site name + region | `energy_operating_scale` |
| KEA/KEPCO regional energy/electricity data | https://www.data.go.kr/data/15127341/fileData.do | region/industry energy and electricity context | province + industry category | fallback energy proxy |

## Scoring Model

Use separate scores for capacity and confidence.

```text
capacity_index =
  0.25 * production_fit_score
+ 0.18 * physical_scale_score
+ 0.17 * workforce_score
+ 0.14 * transaction_history_score
+ 0.10 * financial_scale_score
+ 0.08 * certification_quality_score
+ 0.04 * technology_signal_score
+ 0.04 * logistics_access_score
```

Energy should not dominate the index. It should be a tie-breaker and risk signal:

```text
operational_priority =
  capacity_index
* capacity_confidence
+ 0.04 * energy_operating_scale_score
- route_cost_penalty
- threat_risk_penalty
- missing_evidence_penalty
```

Recommended tiering:

| Tier | Rule of thumb | Demo interpretation |
| --- | --- | --- |
| A | capacity index >= 0.78 and confidence >= 0.70 | Primary conversion candidate |
| B | capacity index >= 0.62 and confidence >= 0.55 | Surge or alternate supplier |
| C | capacity index >= 0.45 | Backup / monitoring candidate |
| D | weak scale or weak product fit | Low-priority candidate |
| VERIFY_ONLY | strong keyword match but missing scale/workforce evidence | Keep on map, do not select automatically |

## Join and Entity Resolution

Public data will not share one universal factory ID, so matching should be conservative.

Recommended matching levels:

| Match level | Rule | Use |
| --- | --- | --- |
| `exact_factory_id` | Same factory management number or source-native ID | Safe direct join |
| `company_address_exact` | Normalized company name + normalized road/lot address | Strong join |
| `company_region_industry` | Normalized company name + province/city + similar industry/product text | Medium join |
| `company_only` | Company/manufacturer name only | Weak join; use only as evidence candidate |
| `aggregate_proxy` | Province + industry category | Fallback context only |

Every enriched field should carry:

```json
{
  "value": 123,
  "source": "source name",
  "match_level": "company_address_exact",
  "matched_name": "matched public name",
  "matched_address": "matched public address",
  "retrieved_at": "2026-07-04",
  "limitations": []
}
```

## Fields to Add Per Factory

```json
{
  "factory_scale": {
    "land_area_m2": null,
    "building_area_m2": null,
    "manufacturing_area_m2": null,
    "factory_size_label": null,
    "registration_date": null,
    "industrial_complex": null,
    "physical_scale_score": 0.0
  },
  "workforce_profile": {
    "registry_employee_count": null,
    "insurance_worker_count": null,
    "insurance_established_date": null,
    "workforce_score": 0.0
  },
  "transaction_profile": {
    "public_contract_count_3y": 0,
    "public_contract_amount_3y_krw": 0,
    "drone_adjacent_contract_count": 0,
    "last_contract_date": null,
    "transaction_history_score": 0.0
  },
  "financial_profile": {
    "revenue_krw": null,
    "total_assets_krw": null,
    "capital_krw": null,
    "fiscal_year": null,
    "financial_scale_score": 0.0
  },
  "quality_technology_profile": {
    "certification_count": 0,
    "relevant_certification_count": 0,
    "patent_or_design_count": 0,
    "certification_quality_score": 0.0,
    "technology_signal_score": 0.0
  }
}
```

## Implementation Path

### MVP, 1-2 days

1. Done: extend the generator to keep factory area and employee columns from the KICOX/full factory rows where available.
2. Done: normalize company names for energy matching and keep source-native factory management number where available.
3. Done: build `factory_scale`, workforce evidence, and improved `production_fit_score`.
4. Done: replace the current opaque `capacity_units_30d` derivation with `capacity_index`, `capacity_confidence`, and `capacity_tier`.
5. Done: show the tier and evidence breakdown in the selected-node drawer.

### Second pass, 2-4 days

1. Add Gyeonggi API enrichment for candidates in Gyeonggi-do because it exposes stronger fields and WGS84 coordinates.
2. Add Worker's Compensation/Employment Insurance worker-count matching.
3. Add procurement contract and delivery-history enrichment.
4. Add certification-product matching for electronics, batteries, power devices, cameras, and regulated products.

### Later / production-grade

1. Add corporation-number or business-ID based entity resolution where legally accessible.
2. Add DART/financial API enrichment for larger firms.
3. Add human verification workflow: call, survey, or secure intake form for equipment list, line availability, QA readiness, inventory, and emergency power.
4. Move selection from heuristic scoring to min-cost flow using capacity tiers as supplier constraints.

## UI Placement

The map should keep the current clean layout. Capacity evidence belongs inside the selected-node drawer:

```text
Capacity Tier: B / Surge candidate
Capacity Index: 0.67
Confidence: 0.61

Evidence:
- Production fit: 0.82, product keyword match
- Physical scale: 0.71, building/manufacturing area available
- Workforce: 0.58, registry employee count available
- Transaction history: 0.32, no recent public delivery match
- Energy: regional proxy only

Missing:
- Exact equipment inventory
- Spare line capacity
- Shift availability
- QA certification for defense-grade use
```

## Key Caveat

This backdata can identify and rank candidates for verification. It should not be presented as verified mobilization capacity, live spare capacity, or guaranteed monthly drone-part output.

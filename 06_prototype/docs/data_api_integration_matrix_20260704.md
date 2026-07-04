# Data/API Integration Matrix for Resilient Maritime COP

- Date: 2026-07-04 KST
- Scope: T3 Resilient Maritime COP over Denied Networks
- Current basis:
  - `/Users/mollykim/projects/D4D/01_research/osint_sources/api_collection_tracker.md`
  - `/Users/mollykim/projects/D4D/03_data/processed/api_smoke_tests/20260704_080458/smoke_report.json`
  - `/Users/mollykim/projects/D4D/06_prototype/docs/resilient_maritime_cop_technical_design.md`

## 1. Integration Principle

이 프로젝트에서 API를 붙이는 기준은 "데이터가 많다"가 아니라 "COP를 갱신할 semantic event를 만들 수 있다"입니다.

모든 source는 아래 순서로 연결합니다.

```text
API/file/raw sample
  -> raw snapshot
  -> normalized observation
  -> semantic event
  -> evidence bundle
  -> priority packet
  -> COP UI / briefing
```

데모에서 반드시 지켜야 할 원칙:

- real source는 context/evidence로 쓰고, 위험 판단은 synthetic/masked entity에 적용합니다.
- 실제 선박, 회사, 개인을 적대 행위자나 불법 행위자로 단정하지 않습니다.
- API key, token, account credential은 `.env`에만 두고 산출물에는 쓰지 않습니다.
- raw snapshot은 내부 검증용으로만 보관하고, 발표/시연에는 익명화된 event만 사용합니다.

## 2. Recommended MVP Data Stack

24시간 해커톤 기준으로 가장 안정적인 조합입니다.

| Slot | Use first | Why | Fallback |
| --- | --- | --- | --- |
| AOI/map | VWorld + static AOI | 지도/좌표/항만 context | static GeoJSON, OSM/Natural Earth |
| Weather/METOC | KMA APIHub sea forecast + data.go.kr KMA | 이미 smoke passed, `WEATHER_HAZARD` 생성 가능 | Open-Meteo Marine |
| Sea state | Open-Meteo Marine | key 없이 wave/SST가 바로 나옴 | synthetic sea-state risk |
| OSINT | GDELT | citation-backed incident context | hand-curated official notice snippets |
| Network | synthetic network simulator | T3 정체성을 가장 확실히 보여줌 | Cloudflare Radar/Ookla baseline later |
| Vessel/AIS | GFW vessel presence + synthetic AIS tracks | GFW token is now issued, but specific AIS-off/dark-vessel labels still need synthetic truth | data.go.kr AIS/Port-MIS, NOAA AIS later |
| SAR/dark vessel | synthetic SAR detection + Copernicus catalogue evidence | product search는 됐지만 ship detection 모델은 별도 필요 | xView3/GFW SAR later |
| Risk screen | OpenSanctions | smoke passed, watchlist/risk-list demo 가능 | static sanctions sample |

## 3. API-by-API Decision

### 3.1 Use Immediately in the Demo

| Source | Current status | Attach as | Event types | Implementation note |
| --- | --- | --- | --- | --- |
| data.go.kr 기상청 단기예보 | `passed` | weather observation adapter | `WEATHER_HAZARD` | AOI 격자 좌표를 고정하고 초단기실황/단기예보에서 풍속, 강수, 시정성 context를 추출 |
| KMA APIHub short sea forecast | `passed` | maritime forecast adapter | `WEATHER_HAZARD`, `SEA_STATE_RISK` | 해상구역 reg code를 AOI에 매핑하고 파고/풍향/풍속/해상특보성 문구를 event severity로 변환 |
| Open-Meteo Marine | `passed` | no-key sea-state fallback | `SEA_STATE_RISK` | Busan/Yellow Sea 등 demo coordinate 기준 hourly wave_height, SST를 저장 |
| VWorld geocode | `passed` | map/geocoding support | COP base/context | 항만/주소/기관 위치를 좌표화할 때 사용. 응답 저장 조건은 VWorld 이용조건을 확인하고 최소 snapshot만 유지 |
| Copernicus Data Space Sentinel-1 catalogue | `passed` | SAR scene availability evidence | `SAR_DARK_VESSEL_CANDIDATE` support | 현재는 "해당 시간/지역에 SAR scene이 존재한다"는 근거까지만 사용. 실제 ship detection은 synthetic/xView3/GFW로 보완 |
| NASA Earthdata CMR | `passed` | ocean/weather collection discovery | `OCEAN_STATE`, `WEATHER_HAZARD` support | 바로 실시간 event를 만들기보다는 collection shortlist와 evidence metadata에 사용 |
| OpenSanctions match | `passed` | entity risk screening | `SANCTION_OR_WATCHLIST_MATCH` | 실제 국내 선박명을 넣지 말고 synthetic company/vessel name 또는 documented sample로 UI 흐름만 시연 |
| Global Fishing Watch 4Wings | `passed` | vessel presence / traffic density adapter | `AIS_DENSITY_CHANGE`, `AIS_GAP` support | token 발급 완료. 특정 선박을 위협으로 단정하지 말고 AOI/time bin 단위의 vessel presence evidence로 우선 사용 |

### 3.2 Connect After Blocker Clears

| Source | Current blocker | Attach as | Event types | Required next step |
| --- | --- | --- | --- | --- |
| SafetyData 긴급재난문자 | approval pending | disaster/official alert adapter | `DISASTER_ALERT`, `OSINT_INCIDENT` | 승인 후 endpoint connector 구현, 해상/항만/기상 관련 메시지만 필터링 |
| data.go.kr 해양수산부 AIS/Port-MIS | application/list verification needed | vessel/port adapter | `AIS_GAP`, `ROUTE_DEVIATION`, `PORT_ANOMALY` | 신청 승인/목록 확인 후 10건 smoke test, real identity masking rule 적용 |
| 나라장터 | unauthorized after issue | procurement/supply-chain context | `SUPPLY_CHAIN_CONTEXT` | 해커톤 MVP에서는 후순위. T3 sustainment story를 강화할 때만 재시도 |

### 3.3 Good Later, Not Required for MVP

| Source | Why useful | Why not MVP-critical |
| --- | --- | --- |
| StealthMole | dark web, Telegram, credential exposure, ransomware/leak monitoring으로 port/logistics/telecom/government cyber-risk context를 만들 수 있음 | maritime COP의 1차 센서는 아니며, API endpoint/signing docs 확인 전까지 smoke test가 어려움. Raw credential/PII는 demo에 부적합하므로 aggregate/redacted event로만 사용 |
| Cloudflare Radar Outage API | real-world outage signal로 `NETWORK_DEGRADATION` 설명력 강화 | 해상 tactical link 자체를 직접 측정하지 않으므로 synthetic simulator가 여전히 필요 |
| Ookla Open Data | 지역별 mobile/fixed bandwidth baseline | quarterly tile dataset이라 전처리가 무겁고 실시간 link 상태가 아님 |
| RIPE Atlas | reachability/latency evidence | probe coverage가 해상 작전 링크와 직접 일치하지 않을 수 있음 |
| UN/LOCODE / World Port Index | port normalization, port capability | 정적 reference라 connector 부담은 낮지만 MVP의 핵심 차별점은 아님 |
| xView3 | SAR ship detection research/evaluation sample | 데이터 용량과 전처리가 무거움. dark vessel event 검증용으로는 좋음 |
| Copernicus Marine | current/wave/SST 고품질 해양 상태 | account/tooling과 gridded data 처리가 필요. Open-Meteo/KMA로 MVP 가능 |

## 4. What Each API Should Produce

### 4.1 Weather and Sea-State APIs

Input:

- KMA/data.go.kr forecast or observation rows
- KMA APIHub sea forecast text rows
- Open-Meteo Marine hourly wave/SST JSON

Normalize to:

```json
{
  "observation_id": "obs_weather_001",
  "source": "kma_apihub_sea_forecast",
  "sensor_type": "WEATHER_API",
  "time": "2026-07-04T03:00:00Z",
  "location": {"area": "Yellow Sea AOI"},
  "claim": "wave height or wind condition exceeds scenario threshold",
  "raw_ref": "raw://kma_apihub/20260704/sample.txt#line=..."
}
```

Extract:

- `WEATHER_HAZARD` when wind/wave/rain/hazard text exceeds threshold.
- `SEA_STATE_RISK` when wave height/SST/current increases sensor or route risk.

### 4.2 Vessel/AIS APIs

Input:

- data.go.kr AIS/Port-MIS when approved
- GFW vessel presence when token is available
- synthetic AIS tracks until then

Normalize to:

```json
{
  "observation_id": "obs_ais_001",
  "source": "synthetic_ais_or_live_ais",
  "sensor_type": "AIS",
  "time": "2026-07-04T02:18:00Z",
  "entity_ref": "vessel_hash_077",
  "location": {"lat": 37.35, "lon": 125.61},
  "claim": "cooperative vessel position report",
  "raw_ref": "raw://ais/..."
}
```

Extract:

- `AIS_GAP`: last_seen is older than expected interval.
- `ROUTE_DEVIATION`: position/speed/heading deviates from baseline route.
- `PORT_ANOMALY`: port arrival/departure/waiting time deviates from baseline.

Safety rule:

- mask MMSI, callsign, vessel name, owner, operator before demo output.
- never label a real vessel as suspicious. Use "requires review" language.

### 4.3 SAR / EO APIs

Input:

- Copernicus Sentinel-1 catalogue product metadata
- later: GFW SAR detections or xView3 detections
- current: synthetic SAR-only detection

Normalize to:

```json
{
  "observation_id": "obs_sar_001",
  "source": "copernicus_catalogue_plus_synthetic_detection",
  "sensor_type": "SAR",
  "time": "2026-07-04T02:24:00Z",
  "location": {"lat": 37.41, "lon": 125.72},
  "claim": "vessel-sized object candidate exists without cooperative AIS match",
  "raw_ref": "raw://copernicus/sentinel1_product_id"
}
```

Extract:

- `SAR_DARK_VESSEL_CANDIDATE` only when SAR-like detection has no AIS match within distance/time gate.

Important limitation:

- Copernicus catalogue alone does not equal dark vessel detection.
- To claim "SAR detected a vessel", we need a ship-detection layer: GFW SAR detections, xView3 labels/model output, or clearly synthetic detection.

### 4.4 OSINT / Official Advisory APIs

Input:

- GDELT maritime query
- SafetyData when approved
- official public advisories/RSS snippets

Normalize to:

```json
{
  "observation_id": "obs_osint_001",
  "source": "gdelt_or_official_notice",
  "sensor_type": "OSINT",
  "time": "2026-07-04T01:40:00Z",
  "location": {"area": "Yellow Sea AOI"},
  "claim": "public report mentions maritime disruption near AOI",
  "citation_url": "https://...",
  "raw_ref": "raw://gdelt/..."
}
```

Extract:

- `OSINT_INCIDENT`: incident/advisory is near AOI and within time window.
- `DISASTER_ALERT`: official disaster/safety message affects maritime/port/logistics conditions.

Safety rule:

- OSINT is context, not proof.
- Keep citation and source reliability visible.

### 4.5 Network State APIs and Synthetic Simulator

Input:

- synthetic link schedule for MVP
- later: Cloudflare Radar outages, Ookla baseline, RIPE Atlas latency/reachability

Normalize to:

```json
{
  "observation_id": "obs_network_001",
  "source": "synthetic_link_simulator",
  "sensor_type": "NETWORK",
  "time": "2026-07-04T02:18:00Z",
  "entity_ref": "link_alpha",
  "claim": "bandwidth degraded to 96 kbps with elevated packet loss",
  "metrics": {
    "bandwidth_kbps": 96,
    "latency_ms": 950,
    "packet_loss_pct": 14
  }
}
```

Extract:

- `NETWORK_DEGRADED`
- route mode: `full_sync`, `delta_sync`, `semantic_summary`, `store_forward`, `local_only`

This is the most important T3 layer. Even with perfect maritime data, the project becomes a normal MDA dashboard unless network impairment changes what gets transmitted.

## 5. Public Data vs Synthetic Data

### 5.1 Can Be Public / Live

| Data need | Public/API source | Use |
| --- | --- | --- |
| weather nowcast/forecast | data.go.kr KMA, KMA APIHub | `WEATHER_HAZARD` |
| marine wave/SST | Open-Meteo Marine, KMA APIHub, later Copernicus Marine | `SEA_STATE_RISK` |
| map/geocoding | VWorld, OSM/static GeoJSON | COP base/context |
| satellite scene availability | Copernicus Data Space catalogue | evidence that SAR/EO data is available over AOI |
| ocean collection discovery | NASA CMR | source discovery/evidence metadata |
| sanctions/watchlist matching | OpenSanctions | risk-screen workflow |
| public news context | GDELT, official advisories | `OSINT_INCIDENT` |
| internet outage/baseline | Cloudflare Radar, Ookla, RIPE Atlas | network realism/context |

### 5.2 Public but Not Yet Ready in This Project

| Data need | Source | Current issue | Fallback |
| --- | --- | --- | --- |
| live/historical vessel track | data.go.kr AIS/Port-MIS | approval/application verification not complete | synthetic AIS tracks |
| fishing/vessel presence/SAR detection | Global Fishing Watch | token issued, presence bins passed; still not a ground-truth threat label | synthetic AIS/SAR, NOAA AIS sample |
| disaster alert | SafetyData | approval pending | official notice snippets, synthetic disaster alert |
| procurement/sustainment | 나라장터 | authorization issue | static procurement context or omit from MVP |

### 5.3 Should Be Synthetic for Hackathon Safety and Reliability

| Synthetic data | Why synthetic is better | How to label |
| --- | --- | --- |
| hostile/suspicious vessel behavior | public data cannot safely claim intent or threat | "synthetic scenario vessel", "requires analyst review" |
| AIS-off/dark vessel ground truth | real dark-vessel truth is not public and needs classified/paid/processed sources | "synthetic SAR-only detection" |
| tactical denied network state | real military network/jamming state is not public and should not be emulated as classified protocol | "synthetic link impairment" |
| commander decision/rules of engagement | sensitive operational logic is not public | "demo triage recommendation" |
| mission priority weights | unit/mission-specific and potentially sensitive | "demo scoring weights" |
| fused threat label | attribution requires evidence/legal standard | "risk indicator", not "confirmed threat" |
| raw vessel identity in suspicious story | privacy/safety/legal risk | hashed/masked vessel IDs |

## 6. Concrete Build Order

### Step 1. Keep current mock dataset as the stable demo backbone

Do not remove synthetic AIS, SAR, and network records. They guarantee that the demo works even if API calls fail.

Output:

- `03_data/samples/resilient_maritime_cop/mock_dataset.json`

### Step 2. Add live weather overlay first

Connect:

- data.go.kr KMA
- KMA APIHub sea forecast
- Open-Meteo Marine fallback

Output:

- `03_data/processed/resilient_maritime_cop/observations/weather_observations.json`
- `WEATHER_HAZARD` events

Reason:

- already smoke-tested;
- easy to explain;
- increases realism without safety issues.

### Step 3. Add network simulator as first-class data

Connect:

- local synthetic link schedule
- optional Cloudflare/Ookla context later

Output:

- `03_data/processed/resilient_maritime_cop/observations/network_observations.json`
- `NETWORK_DEGRADED` events
- routing result per mode

Reason:

- this is the T3 differentiator.

### Step 4. Add OSINT with citation and rate-limit fallback

Connect:

- GDELT with conservative query/rate handling
- curated official notice snippets if 429 occurs

Output:

- `OSINT_INCIDENT` events with citation URLs

Reason:

- useful for evidence drawer and briefing.

### Step 5. Add AIS/port only after access is stable

Connect:

- data.go.kr AIS/Port-MIS if approved
- GFW 4Wings vessel presence bins now

Output:

- `AIS_GAP`
- `ROUTE_DEVIATION`
- `PORT_ANOMALY`

Reason:

- high value, but access and privacy risks require fallback.

### Step 6. Add SAR evidence carefully

Connect:

- Copernicus catalogue for scene availability
- synthetic detection for MVP
- later GFW SAR/xView3 for actual detection layer

Output:

- `SAR_DARK_VESSEL_CANDIDATE`

Reason:

- "catalogue product exists" is not "ship detected"; do not overclaim.

### Step 7. Add OpenSanctions as optional risk-screen card

Connect:

- OpenSanctions `/match/default`

Output:

- `SANCTION_OR_WATCHLIST_MATCH`

Reason:

- good intelligence-copilot flavor, but not essential to the degraded-network thesis.

## 7. MVP Event Coverage Matrix

| Event | Live/API source now | Synthetic needed | MVP recommendation |
| --- | --- | --- | --- |
| `WEATHER_HAZARD` | yes: data.go.kr/KMA/Open-Meteo | no | implement live |
| `SEA_STATE_RISK` | yes: KMA/Open-Meteo | optional | implement live or fallback |
| `NETWORK_DEGRADED` | partially: external outage/baseline later | yes | synthetic first |
| `OSINT_INCIDENT` | yes but GDELT 429 occurred | yes fallback snippets | implement with cache/rate limit |
| `AIS_GAP` | not stable yet | yes | synthetic first, swap to AIS later |
| `ROUTE_DEVIATION` | not stable yet | yes | synthetic first |
| `PORT_ANOMALY` | not stable yet | yes | synthetic or static port context |
| `SAR_DARK_VESSEL_CANDIDATE` | catalogue yes, detection no | yes | synthetic detection + Copernicus catalogue evidence |
| `SANCTION_OR_WATCHLIST_MATCH` | yes: OpenSanctions | use synthetic entity | optional stretch |

## 8. Final Recommendation

For the next implementation pass:

1. Add live weather and sea-state connector.
2. Keep synthetic AIS/SAR/network as demo backbone.
3. Add GDELT with cached fallback snippets.
4. Add Copernicus catalogue metadata as evidence, not detection.
5. Add OpenSanctions only as a separate "risk context" panel.
6. Use GFW for AOI vessel presence now, but wait for SafetyData/AIS approvals before replacing the synthetic vessel/event layer.

This gives a credible demo now, while keeping a clean path to real data later.

## 9. Additional Public API Candidates

추가 API는 "실제 공개 데이터로 semantic event를 늘릴 수 있는가" 기준으로만 붙입니다. 아래 후보는 이번 리서치에서 바로 응답 또는 공식 문서 기준으로 검토한 것입니다.

| Priority | Source | Access | Extractable data | Candidate events | Demo value |
| --- | --- | --- | --- | --- | --- |
| P0 | KMA/data.go.kr 기상특보 조회서비스 | existing data.go.kr key, separate API application may be needed | 특보 현황, 통보문, 예비특보, 강풍/풍랑/태풍/폭풍해일 등 해역 특보 | `OFFICIAL_WEATHER_WARNING`, `SEA_STATE_RISK` | KMA forecast보다 "공식 경보"라 COP evidence로 강함 |
| P0 | GDACS RSS/API | no key | cyclone, earthquake, tsunami, flood, volcano alert level, location, severity | `REGIONAL_HAZARD_ALERT`, `TSUNAMI_CONTEXT` | APAC 해역 태풍/지진/쓰나미 context를 빠르게 붙일 수 있음 |
| P0 | NASA EONET | no key; smoke reachable | open natural events, event category, geometry, source links | `NATURAL_HAZARD_CONTEXT`, `OSINT_INCIDENT` | 재난/태풍/화산/산불 등 broad hazard context |
| P0 | USGS Earthquake GeoJSON | no key; smoke reachable | recent quake magnitude, depth, location, tsunami flag/product links | `EARTHQUAKE_TSUNAMI_CONTEXT` | 해상/항만 위험도에 쓰기 좋고 구현이 매우 쉬움 |
| P0 | NOAA NDBC realtime files | no key; smoke reachable | buoy wind, gust, wave height/period, pressure, air/water temp | `SEA_STATE_OBS`, `SENSOR_RELIABILITY_CONTEXT` | KMA/Open-Meteo와 교차 검증용. 다만 APAC 커버리지는 제한적 |
| P0 | OSM Overpass | no key but rate-limited | port/harbour/pier, ferry terminal, road/rail/logistics nodes, critical POI | `PORT_CONTEXT`, `LOGISTICS_NODE_CONTEXT` | 지도 context와 AOI bootstrap에 좋음. 캐시해서 사용 |
| P1 | NASA FIRMS | free MAP_KEY by email | VIIRS/MODIS active fire or thermal anomaly near port/coast | `PORT_FIRE_THERMAL_ANOMALY`, `OSINT_INCIDENT` | 항만 화재/연기/물류중단 시나리오에 좋은 근거 |
| P1 | Cloudflare Radar Outages | free Cloudflare API token | country/location internet outages, anomaly cause/scope/duration | `NETWORK_DEGRADATION_CONTEXT` | T3의 denied/low-bandwidth story를 현실 outage context로 보강 |
| P1 | CAIDA IODA | public API | country/ASN/region outage time series and alerts | `NETWORK_OUTAGE_CONTEXT` | Cloudflare와 별도 출처로 network degradation evidence 강화 |
| P1 | Copernicus Marine Toolbox | account/toolbox setup | currents, wave, sea surface temperature, salinity, sea level variables | `SEA_STATE_RISK`, `ROUTE_RISK_CONTEXT` | Open-Meteo보다 고급 해양장. 전처리 시간이 더 듦 |
| P1 | UN/LOCODE | public static downloads | ports/locations codes, country, function, status, coordinates where provided | `PORT_NORMALIZATION` | 항만명/국가/코드 정규화에 안정적 |
| P1 | NGA World Port Index | public static dataset | port location, facilities, services, physical characteristics | `PORT_CAPABILITY_CONTEXT` | port anomaly 설명에 배경 데이터로 좋음 |
| P2 | RIPE Atlas | public metadata/results; new measurements need account/credits | probe reachability, latency, traceroute, DNS/HTTP/TLS measurements | `NETWORK_REACHABILITY_EVIDENCE` | 실제 인터넷 측정 근거. 해상 tactical link와는 직접 매핑하지 않기 |
| P2 | ReliefWeb API v2 | pre-approved appname required as of 2025-11 | curated humanitarian reports/disasters | `HUMANITARIAN_CONTEXT`, `OSINT_INCIDENT` | 좋지만 사전 등록이 필요해서 MVP 즉시성은 낮음 |
| P2 | NOAA CO-OPS | no key | tide, water level, current, predictions for US stations | `TIDE_CURRENT_RISK` | 미국 항만 데모에는 강함. 한국/APAC AOI에는 직접성 낮음 |

### Best Additions for This Project

1. `KMA 기상특보`: 지금 weather layer를 "관측/예보"에서 "공식 경보"까지 끌어올립니다.
2. `GDACS + EONET + USGS`: 재난 context를 무료/no-key로 늘릴 수 있고, SafetyData 승인 전 fallback으로 좋습니다.
3. `Cloudflare Radar + IODA`: T3의 핵심인 네트워크 저하/두절을 현실적인 external context로 보강합니다.
4. `UN/LOCODE + World Port Index + Overpass`: live event는 아니지만 항만/물류/지도 정규화가 좋아집니다.
5. `NASA FIRMS`: 항만 화재/열원/산불 연기 같은 disruption scenario를 붙이기 좋습니다.

주의:

- 이 후보들은 "상황 근거"로 쓰고, 실제 위협 판정 라벨은 계속 synthetic/masked entity에만 붙입니다.
- GFW vessel presence는 실제 데이터로 쓰되, "AIS-off 의심 선박"이라는 정답 라벨은 synthetic scenario에서 만듭니다.
- Overpass, GDELT, ReliefWeb, Cloudflare Radar 등은 rate/usage policy를 고려해 캐시 우선으로 사용합니다.

## 10. Source References Checked

- Cloudflare Radar Outages: https://developers.cloudflare.com/radar/investigate/outages/
- CAIDA IODA API: https://api.ioda.inetintel.cc.gatech.edu/v2/
- Copernicus Data Space APIs: https://dataspace.copernicus.eu/analyse/apis
- Copernicus Marine Data Store: https://data.marine.copernicus.eu/products
- GDACS feed reference: https://www.gdacs.org/feed_reference.aspx
- Global Fishing Watch API docs: https://globalfishingwatch.org/our-apis/documentation
- NASA EONET API: https://eonet.gsfc.nasa.gov/
- NASA FIRMS API key: https://firms.modaps.eosdis.nasa.gov/api/map_key/
- NOAA CO-OPS API: https://api.tidesandcurrents.noaa.gov/api/prod/
- NOAA NDBC realtime data guide: https://www.ndbc.noaa.gov/faq/rt_data_access.shtml
- Ookla Open Data on AWS: https://registry.opendata.aws/speedtest-global-performance/
- OpenStreetMap Overpass API: https://dev.overpass-api.de/overpass-doc/en/
- OpenSanctions API docs: https://www.opensanctions.org/docs/api/
- NASA CMR Search API docs: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
- ReliefWeb API: https://apidoc.reliefweb.int/
- RIPE Atlas API: https://atlas.ripe.net/docs/apis/rest-api-reference/
- UN/LOCODE: https://unece.org/trade/uncefact/unlocode
- USGS Earthquake API: https://earthquake.usgs.gov/fdsnws/event/1/
- VWorld Geocoder reference: https://www.vworld.kr/dev/v4dv_geocoderguide2_s001.do
- data.go.kr KMA short-term forecast API: https://www.data.go.kr/data/15084084/openapi.do
- data.go.kr KMA weather warning API: https://www.data.go.kr/data/15000415/openapi.do
- GDELT data/API overview: https://www.gdeltproject.org/data.html

# Resilient Maritime COP over Denied Networks: Data/API Plan

Last reviewed: 2026-07-03

## Project Frame

Working title:

- Resilient Maritime COP over Denied Networks
- 거부환경 해상 COP 의미 전송 시스템

Core idea:

통신 대역폭이 낮거나 일부 노드가 끊긴 상황에서 AIS, SAR/위성, OSINT, 기상, 항만/물류, 네트워크 상태 데이터를 원문 그대로 보내지 않고, 작전적으로 의미 있는 이벤트로 압축해 COP를 갱신합니다.

This is a T3 project with T4 data:

- Main track: T3 Battle Network, C2 & Sustainment
- Data domain: T4 Maritime Domain Awareness
- Differentiator: "지도 대시보드"가 아니라 "저대역/거부환경에서 살아남는 의미 이벤트 전송"

## Target Semantic Events

이 프로젝트에서 원본 데이터를 그대로 보내지 않고 아래 이벤트 형태로 바꾸는 것이 핵심입니다.

| Event type | Trigger examples | Minimum fields |
| --- | --- | --- |
| `AIS_GAP` | 선박이 일정 시간 이상 AIS 미송신, 예상 항로와 불일치 | vessel_id, last_seen, gap_duration, last_position, predicted_position, confidence |
| `ROUTE_DEVIATION` | 정상 항로/속도/목적지 패턴에서 이탈 | vessel_id, current_track, expected_track, deviation_score, reason |
| `SAR_DARK_VESSEL_CANDIDATE` | SAR ship detection exists but AIS match missing | detection_id, location, timestamp, size_hint, nearest_ais_distance, confidence |
| `WEATHER_HAZARD` | 태풍, 고파고, 강풍, 저시정, 위험 해류 | area, hazard_type, severity, valid_time, source |
| `PORT_ANOMALY` | 항만 입출항/물동량/대기시간 이상 | port_id, anomaly_type, baseline, observed, severity |
| `OSINT_INCIDENT` | 뉴스/SNS/공식공지에서 해상 도발, 사고, 봉쇄, 훈련, 파업 등 포착 | event_id, actor, location, time, summary, citation |
| `SANCTION_OR_WATCHLIST_MATCH` | 선박/회사/소유주가 제재·감시목록과 유사 | entity, matched_list, match_score, identifiers |
| `NETWORK_DEGRADATION` | 특정 링크/노드 대역폭 저하, 지연 증가, 패킷 손실, 단절 | link_id, affected_area, bandwidth, latency, packet_loss, status |
| `PRIORITY_BRIEF` | 제한된 통신 상황에서 먼저 보내야 할 요약 | priority_score, event_refs, compressed_message, recommended_action |

## Minimum Viable Data Stack

24시간 해커톤 기준으로는 아래 조합이 가장 현실적입니다.

### Stack A: Korea-centered demo

| Layer | Source | Why it matters |
| --- | --- | --- |
| AIS / vessel | 해양수산부 AIS, 선박 AIS 동적정보, 해운항만물류정보시스템 선박관제정보 | AIS gap, 입출항, 항만 이상징후 |
| Weather / ocean | 기상청 API허브, 기상자료개방포털, KHOA/국립해양조사원, NIFS | 기상 위험, 해류/조위/파고, 작전환경 |
| Port / logistics | 해양수산통계 OPENAPI, Port-MIS 계열 데이터, 항만공사 공공데이터 | 항만 혼잡, 물동량 이상, 보급/지속지원 |
| Map / base layers | VWorld, 국가공간정보포털, OpenStreetMap | COP 지도 레이어 |
| OSINT | GDELT, 공공기관 공지/RSS, 뉴스 검색, 해양수산부/해경/기상청 공지 | 근거 있는 사건 요약 |
| Network state | KCA 무선국/기지국, OpenCelliD, Ookla open data, synthetic link simulator | 거부환경/저대역폭 상황 모델링 |

### Stack B: International demo

| Layer | Source | Why it matters |
| --- | --- | --- |
| AIS / vessel | Global Fishing Watch, MarineTraffic, AISHub, NOAA MarineCadastre AIS | vessel activity, AIS density, historical tracks |
| SAR / dark vessel | Copernicus Sentinel-1, Global Fishing Watch SAR detections, xView3, Ship Detection Webmap | AIS-off suspect detection |
| Weather / ocean | Copernicus Marine, NOAA/NCEP/NOMADS, NASA Earthdata/FIRMS | sea state, currents, SST, thermal/fire anomalies |
| Port / logistics | UN/LOCODE, World Port Index, port authority datasets | ports, facilities, port calls, logistics nodes |
| OSINT / events | GDELT, ACLED, HDX/ReliefWeb, official advisories | incident timeline and citations |
| Network state | RIPE Atlas, Cloudflare Radar, Ookla open data, OpenCelliD, synthetic impairment | live/realistic communications constraint layer |
| Risk lists | OpenSanctions, OFAC, EU sanctions, UN lists | vessel/company/owner risk matching |

## Data/API Candidates by Function

### 1. Vessel Movement and AIS

| Source | Access | What to collect | Event use |
| --- | --- | --- | --- |
| 해양수산부 AIS 정보 / 선박 AIS 동적정보 | data.go.kr API/file | MMSI/callsign, lat/lon, speed, heading, timestamp | `AIS_GAP`, `ROUTE_DEVIATION` |
| 해양수산부 해운항만물류정보시스템 선박관제정보 | data.go.kr file/API | port entry/exit time, callsign, port name | `PORT_ANOMALY`, port context |
| MarineTraffic | commercial API | real-time/historical vessel positions, port calls, vessel particulars | high-quality AIS demo if access exists |
| Global Fishing Watch APIs | API token | vessel presence, fishing effort, vessel identity, SAR vessel detections | AIS density, dark vessel candidate |
| NOAA MarineCadastre AIS | public downloads | U.S. historical AIS tracks and density | offline AIS processing practice |
| AISHub | member API | live AIS in JSON/XML/CSV | fallback live AIS if membership available |

### 2. SAR / EO / Dark Vessel Detection

| Source | Access | What to collect | Event use |
| --- | --- | --- | --- |
| Copernicus Data Space / Sentinel-1 | OAuth/API | SAR scenes over AOI/time window | `SAR_DARK_VESSEL_CANDIDATE` |
| Sentinel Hub APIs | OAuth/API | rendered tiles, statistical API, EO processing | fast map overlay / thumbnails |
| Global Fishing Watch SAR detections | API | vessel detections from SAR imagery | dark vessel event without building SAR model |
| xView3 | open dataset | SAR ship detections with AIS/context labels | model/evaluation background, sample detections |
| Ship Detection Webmap | public webmap | current Sentinel-1 ship detections | visual demo/reference, not necessarily bulk API |
| NASA/USGS Earthdata/EarthExplorer | account/API | Landsat/VIIRS/MODIS and EO metadata | context imagery and environmental corroboration |

### 3. Weather, Ocean, and Environmental Hazards

| Source | Access | What to collect | Event use |
| --- | --- | --- | --- |
| 기상청 API허브 | API key | weather warnings, satellite/radar, maritime weather, aviation weather | `WEATHER_HAZARD` |
| 기상자료개방포털 | API/file | observations, climate, forecast data | baseline and historical validation |
| KHOA / 국립해양조사원 | API/key | tides, currents, sea level, coastal observations | route risk, port approach risk |
| NIFS OPEN API | API key | ocean observations, red tide, sea temperature | environmental context |
| Copernicus Marine Data Store | API/account | currents, waves, SST, salinity, sea level | international sea-state layer |
| NOAA/NCEP/NOMADS | public API | GFS, wave, weather forecast products | global weather fallback |
| NASA FIRMS | API/account optional | active fire/thermal anomalies | port/shore event corroboration |

### 4. Port, Logistics, and Sustainment

| Source | Access | What to collect | Event use |
| --- | --- | --- | --- |
| 해양수산통계 OPENAPI | API key | maritime statistics, port/fisheries indicators | port baseline/anomaly |
| Port-MIS / 해운항만물류정보시스템 data | public/data.go.kr | port entry/exit, vessel control info | port anomaly and sustainment |
| 인천/부산/울산/여수광양 항만공사 공공데이터 | public/API varies | cargo volume, berthing, lock/weather, vessel arrival/departure | port status |
| UN/LOCODE | public download | standardized port/location code | normalize port identifiers |
| World Port Index | public dataset | port facilities, coordinates, services | COP base layer and port capability |
| 국토교통부 교통소통/돌발/사고 API | data.go.kr API | road speed, incidents, disruptions | land-side logistics constraint |

### 5. OSINT Events, Advisories, and Narrative Evidence

| Source | Access | What to collect | Event use |
| --- | --- | --- | --- |
| GDELT | no key / BigQuery | news events, locations, themes, URLs | `OSINT_INCIDENT`, citation timeline |
| ACLED | account/API | political violence/protest/conflict events | regional instability context |
| HDX / ReliefWeb | public/API | disaster/humanitarian updates | disaster and port disruption context |
| Official advisories | RSS/web | coast guard, weather, maritime safety, port authority notices | high-trust citations |
| OpenSanctions / OFAC / EU / UN sanctions | API/download | vessel/company/person sanctions matches | `SANCTION_OR_WATCHLIST_MATCH` |

### 6. Network State and Denied-Network Simulation

This layer is what makes the project T3 instead of a maritime dashboard.

| Source / Tool | Access | What to collect or simulate | Event use |
| --- | --- | --- | --- |
| RIPE Atlas | public/API/account | probes, latency, reachability, status checks | realistic connectivity degradation examples |
| Cloudflare Radar Outage API | public/API | internet outages, anomalies by location | `NETWORK_DEGRADATION` external signal |
| Ookla Open Data | public S3/AWS | mobile/fixed performance by tile: download/upload/latency | baseline bandwidth/latency map |
| OpenCelliD | API token | cell tower locations by operator/country | cellular coverage proxy |
| KCA/Korean wireless station datasets | data.go.kr/file | 3G/4G/5G base stations, mountain/park coverage | Korea-specific coverage proxy |
| Mininet / Linux `tc netem` | local simulator | bandwidth, delay, packet loss, link failure | demo impairment engine |
| ns-3 / CORE / EMANE / OMNeT++ | local simulator | tactical/edge network simulation | deeper post-hackathon version |
| Synthetic network topology | local generated | node, link, bandwidth, priority class | reliable 24h fallback |

## Semantic Compression Inputs

For each event, preserve enough information to support decisions without shipping raw data.

Recommended compact event payload:

```json
{
  "event_id": "evt-20260703-001",
  "event_type": "AIS_GAP",
  "priority": 0.86,
  "where": {"lat": 34.72, "lon": 125.20, "area": "Yellow Sea"},
  "when": "2026-07-03T11:05:00Z",
  "who": {"vessel_id": "hashed_mmsi", "name": "masked"},
  "what": "AIS transmission gap exceeded expected interval near high-risk route",
  "why_it_matters": "Route deviation overlaps weather hazard and recent OSINT incident",
  "evidence": [
    {"source": "AIS", "ref": "ais_row_10291"},
    {"source": "KMA", "ref": "weather_alert_441"},
    {"source": "GDELT", "url": "https://example.org/source"}
  ],
  "recommended_action": "Prioritize SAR/EO confirmation and monitor nearest port calls"
}
```

## Priority Scoring Features

| Feature group | Example features |
| --- | --- |
| Mission impact | proximity to protected area, port, chokepoint, shipping lane |
| Confidence | number of corroborating sources, sensor agreement, source reliability |
| Urgency | event recency, speed toward AOI, weather window, expected time-to-impact |
| Network cost | bytes required, current link capacity, retransmission risk |
| Novelty | deviation from baseline, new entity, rare pattern |
| Safety/legal | PII risk, sensitive source risk, redistributability |

## Recommended First Collection Order

1. `data.go.kr`: 해양수산부 AIS/선박관제/항만 데이터와 국토교통부 돌발상황 API 확인
2. `KMA APIHub`: 해상/태풍/예특보/위성 metadata 확인
3. `GDELT`: APAC maritime keywords and AOI news/event timeline
4. `VWorld` + `OpenStreetMap`: base map and port/AOI layer
5. `Copernicus Marine`: wave/current/SST global forecast layer
6. `Global Fishing Watch`: AIS vessel presence and SAR detections if token is available
7. `Cloudflare Radar` + `Ookla Open Data`: network degradation realism layer
8. `OpenSanctions`: vessel/company/entity risk matching
9. `Copernicus Sentinel-1` or `xView3`: SAR dark vessel evidence layer

Implementation runbook:

- `08_ops/runbooks/resilient_maritime_cop_data_connection_guide.md`

## Hackathon Build Recommendation

Must build:

- Synthetic network impairment model: bandwidth, latency, packet loss, link down
- Event extraction from at least 3 sources: AIS/port, weather/ocean, OSINT
- Semantic event schema with citation/provenance
- Priority queue that decides what gets transmitted first
- COP map + timeline + compressed briefing

Should build if time allows:

- SAR dark vessel candidate from xView3/GFW/Copernicus
- Port/logistics anomaly
- OpenSanctions entity matching
- Network dashboard showing raw bytes saved vs event bytes transmitted

Avoid:

- Real tactical protocol recreation
- RF/jamming detection claims without data
- Link-16 emulation
- Raw AIS replay dashboard without semantic compression
- LLM answer without evidence links

## API Keys / Accounts to Prepare

Highest priority:

- data.go.kr
- KMA APIHub
- VWorld
- Global Fishing Watch
- Copernicus Data Space / Sentinel Hub
- NASA Earthdata
- OpenSanctions

Nice to have:

- MarineTraffic
- ACLED
- Space-Track
- OpenCelliD
- RIPE Atlas
- UN Comtrade

## Source Links

- Global Fishing Watch API docs: https://globalfishingwatch.org/our-apis/documentation
- Copernicus Data Space APIs: https://dataspace.copernicus.eu/analyse/apis
- Copernicus Marine Data Store: https://data.marine.copernicus.eu/products
- Copernicus Sentinel-1: https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-1
- xView3 maritime detection dataset: https://iuu.xview.us/
- NOAA MarineCadastre AIS: https://coast.noaa.gov/digitalcoast/tools/ais.html
- MarineCadastre vessel traffic hub: https://hub.marinecadastre.gov/pages/vesseltraffic
- 해양수산통계 OPENAPI: https://www.mof.go.kr/statPortal/api/idx/main.do
- UN/LOCODE: https://unece.org/trade/cefact/unlocode-code-list-country-and-territory
- World Port Index: https://data.humdata.org/dataset/world-port-index
- RIPE Atlas: https://atlas.ripe.net/
- Cloudflare Radar Outage API: https://developers.cloudflare.com/radar/investigate/outages/
- Ookla Open Data: https://registry.opendata.aws/speedtest-global-performance/
- OpenCelliD: https://www.opencellid.org/

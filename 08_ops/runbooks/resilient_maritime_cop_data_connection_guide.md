# Resilient Maritime COP Data Connection Guide

Last reviewed: 2026-07-03

이 문서는 `Resilient Maritime COP over Denied Networks` 데모를 만들 때 데이터/API를 어떤 우선순위로 연결할지 정리한 실행 가이드입니다.

핵심 원칙:

- 먼저 "데이터를 많이 붙이기"가 아니라 "COP를 갱신할 semantic event"를 만듭니다.
- 모든 source adapter는 `raw snapshot -> normalized record -> semantic event -> priority packet -> COP update` 흐름을 따릅니다.
- API key가 없어도 돌아가는 fallback stack을 먼저 만들고, key가 확보되는 순서대로 live source를 교체합니다.
- T3 정체성은 `NETWORK_DEGRADATION`, `PRIORITY_ROUTING`, `bytes saved`, `message survived`에서 드러나야 합니다.

## Target Flow

```text
Source APIs / Files
  -> Raw Snapshot
  -> Normalized Entities
  -> Semantic Events
  -> Priority Routing
  -> Compressed Messages
  -> COP Map / Timeline / Briefing
```

## Shared Output Schema

모든 connector는 최종적으로 아래 형태의 JSON event를 만들면 됩니다.

```json
{
  "event_id": "evt-001",
  "event_type": "AIS_GAP",
  "priority": 0.86,
  "severity": "high",
  "confidence": 0.74,
  "time": "2026-07-03T11:05:00Z",
  "location": {
    "lat": 34.72,
    "lon": 125.20,
    "area": "Yellow Sea"
  },
  "entities": [
    {
      "type": "vessel",
      "id": "hashed_mmsi",
      "label": "masked vessel"
    }
  ],
  "summary": "AIS transmission gap exceeded expected interval near high-risk route.",
  "why_it_matters": "The gap overlaps a weather hazard and recent OSINT incident near a chokepoint.",
  "evidence": [
    {
      "source": "AIS",
      "ref": "raw://ais/20260703/sample.csv#row=104"
    },
    {
      "source": "KMA",
      "ref": "raw://weather/20260703/kma_alert.json"
    }
  ],
  "recommended_action": "Prioritize SAR/EO confirmation and monitor nearest port calls.",
  "raw_bytes": 18420,
  "event_bytes": 712
}
```

## Priority Ladder

### P0. Build the Event Spine First

Do this before integrating any external API.

| Task | Output | Why |
| --- | --- | --- |
| Define AOI | `scenario/aoi.geojson` | 모든 API query 범위를 통일 |
| Define timeframe | `scenario/time_window.json` | AIS, weather, news, network 상태를 같은 시간축에 정렬 |
| Define event schema | `semantic_events.schema.json` | source가 달라도 COP update를 통일 |
| Generate synthetic network states | `network_state.jsonl` | API 없이도 T3 데모 가능 |
| Generate seed scenario | `scenario_seed.json` | 발표 흐름을 통제 |

Recommended AOI candidates:

- Yellow Sea / 서해 NLL 인근: 한국 맥락이 강함
- Busan Strait / 대한해협: 항만/해상교통/기상 연결이 쉬움
- South China Sea: APAC gray-zone narrative가 강함

### P1. Connect No-Key / Low-Friction Sources

API key 발급을 기다리는 동안 바로 붙입니다.

| Source | Connector role | Semantic events | Notes |
| --- | --- | --- | --- |
| GDELT | maritime news/event query | `OSINT_INCIDENT` | citation 데모에 좋음 |
| OpenStreetMap / Overpass | ports, coastlines, facilities | COP base layer, port context | 무거운 query 주의 |
| UN/LOCODE | port code normalization | port entity mapping | 항만명 정규화 |
| World Port Index | port facility/capability | `PORT_CONTEXT` | 항만 능력/시설 설명 |
| Cloudflare Radar Outage API | internet outage/anomaly | `NETWORK_DEGRADATION` | T3 network realism |
| Ookla Open Data | baseline bandwidth/latency | `NETWORK_BASELINE` | tile data라 전처리 필요 |
| NOAA MarineCadastre AIS sample | AIS processing practice | `AIS_GAP`, `ROUTE_DEVIATION` | 미국 해역 샘플이지만 알고리즘 테스트에 좋음 |
| xView3 | SAR ship detection sample | `SAR_DARK_VESSEL_CANDIDATE` | 다운로드/용량 확인 필요 |
| Natural Earth | base map | COP background | public domain |

P1 목표:

- 외부 key 없이도 "데이터 수집 -> semantic event -> priority queue -> COP"가 끝까지 돈다.
- 발표 데모가 API 장애에도 살아남는다.

### P2. Connect Korean Core APIs

국내 데모를 선명하게 만드는 핵심입니다. `data.go.kr`, `KMA APIHub`, `VWorld` key가 있으면 먼저 연결합니다.

| Source | Env var | Connector role | Semantic events |
| --- | --- | --- | --- |
| data.go.kr 해양수산부 AIS/선박관제 | `DATA_GO_KR_SERVICE_KEY` | vessel movement and port entry/exit | `AIS_GAP`, `ROUTE_DEVIATION`, `PORT_ANOMALY` |
| data.go.kr 국토교통부 돌발/교통 | `DATA_GO_KR_SERVICE_KEY` | land-side logistics disruption | `LOGISTICS_CONSTRAINT` |
| KMA APIHub | `KMA_APIHUB_KEY` | maritime weather, warnings, radar/satellite metadata | `WEATHER_HAZARD` |
| VWorld | `VWORLD_API_KEY` | geocoding, base map, coordinate support | COP map layer |
| KHOA/NOSC/NIFS | `NOSC_API_KEY`, `NIFS_API_KEY` | tides, currents, ocean observations | `SEA_STATE_RISK` |

P2 smoke tests:

1. 해양/AIS 또는 선박관제 API에서 10 records를 받아 raw JSON/CSV 저장
2. KMA에서 AOI 인근 예특보 또는 해상 기상 record 1건 저장
3. VWorld/OSM으로 항만 좌표를 지도에 찍기
4. 위 3개를 같은 timeline에 올려 `WEATHER_HAZARD + AIS_GAP` composite event 만들기

### P3. Connect International Maritime Intelligence

해상 MDA 품질을 크게 올리는 단계입니다.

| Source | Env var | Connector role | Semantic events |
| --- | --- | --- | --- |
| Global Fishing Watch | `GLOBAL_FISHING_WATCH_TOKEN` | vessel presence, fishing effort, SAR detections | `AIS_DENSITY_CHANGE`, `SAR_DARK_VESSEL_CANDIDATE` |
| Copernicus Data Space / Sentinel Hub | `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET` | Sentinel-1/2 imagery search/render | `SAR_DARK_VESSEL_CANDIDATE`, map evidence |
| Copernicus Marine | account/token if needed | currents, waves, SST, sea level | `SEA_STATE_RISK` |
| NASA Earthdata / FIRMS | `NASA_EARTHDATA_TOKEN` | thermal/fire anomalies, EO metadata | `THERMAL_ANOMALY`, context |
| OpenSanctions | `OPENSANCTIONS_API_KEY` | vessel/company/entity screening | `SANCTION_OR_WATCHLIST_MATCH` |

P3 smoke tests:

1. GFW vessel presence or SAR detection query for AOI/time window
2. Copernicus product search for Sentinel-1 scene over AOI
3. OpenSanctions entity screen for one sample company/vessel name
4. Convert each response to event objects with evidence links

### P4. Add Premium / Approval-Based Sources

이 단계는 있으면 좋지만, 없어도 MVP가 돌아가야 합니다.

| Source | Env var | Use | Fallback |
| --- | --- | --- | --- |
| MarineTraffic | `MARINETRAFFIC_API_KEY` | high-quality AIS and port calls | GFW, NOAA AIS, data.go.kr AIS |
| AISHub | custom token | live AIS | NOAA AIS sample, GFW |
| ACLED | `ACLED_CLIENT_ID`, `ACLED_CLIENT_SECRET` | conflict/protest events | GDELT |
| Space-Track | `SPACE_TRACK_USERNAME`, `SPACE_TRACK_PASSWORD` | satellite/SSA context | CelesTrak no-key TLE |
| KISA C-TAS | `KISA_CTAS_EXPORT_KEY`, `KISA_CTAS_ORG_KEY` | cyber threat indicators | KISA public notices, OpenSanctions |

## Connector Implementation Pattern

Each connector should expose the same three functions.

```python
def fetch_raw(aoi, time_window, env) -> list[RawRecord]:
    ...

def normalize(raw_records) -> list[NormalizedRecord]:
    ...

def extract_events(normalized_records, context) -> list[SemanticEvent]:
    ...
```

Recommended folder layout:

```text
06_prototype/scripts/connectors/
  gdelt.py
  osm.py
  data_go_kr.py
  kma.py
  vworld.py
  global_fishing_watch.py
  copernicus.py
  opensanctions.py
  network_synthetic.py
  priority_router.py
```

Recommended data layout:

```text
03_data/raw/api_snapshots/<source>/<YYYYMMDD_HHMMSS>/
03_data/processed/resilient_maritime_cop/normalized/
03_data/processed/resilient_maritime_cop/events/
03_data/processed/resilient_maritime_cop/cop_updates/
03_data/samples/resilient_maritime_cop/
```

Current smoke-test runner:

```bash
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/smoke_test_api_sources.py
```

The runner reads `.env`, writes small raw samples under `03_data/raw/api_snapshots/<YYYYMMDD_HHMMSS>/`, and writes the status report under `03_data/processed/api_smoke_tests/<YYYYMMDD_HHMMSS>/smoke_report.json`. It prints status only, never key values.

## Priority Routing Logic

Once events exist, apply a small scoring model:

```text
priority =
  0.30 * mission_impact
  0.20 * urgency
  0.20 * confidence
  0.15 * novelty
  0.10 * network_cost_efficiency
  0.05 * safety_score
```

Network-aware routing:

| Network state | Send |
| --- | --- |
| Normal | full event + evidence summary |
| Degraded | high-priority events + compact evidence refs |
| Severely degraded | top-N critical events only |
| Link down | queue locally, send digest when link recovers |

Demo metrics:

- raw bytes vs semantic bytes
- number of events dropped/deferred/sent
- time-to-COP-update
- number of citation-backed events
- operator-visible risk changes

## Recommended Build Order

### Day-before or pre-hackathon

1. Put available keys into `.env`.
2. Build `network_synthetic.py`.
3. Build `gdelt.py`.
4. Build `osm.py` or static port layer.
5. Build one Korean API connector: preferably `data_go_kr.py` or `kma.py`.
6. Build `priority_router.py`.
7. Save one complete sample scenario under `03_data/samples/resilient_maritime_cop/`.

### Hackathon MVP

1. Load AOI and seed scenario.
2. Collect or load AIS/port sample.
3. Collect or load weather hazard.
4. Collect GDELT OSINT event.
5. Generate network degradation event.
6. Extract semantic events.
7. Route by priority.
8. Render COP map/timeline/briefing.
9. Show bytes saved and dropped/deferred event behavior.

### Stretch

1. Add GFW SAR detection or xView3 sample.
2. Add OpenSanctions watchlist match.
3. Add Copernicus/Sentinel evidence thumbnail.
4. Add Palantir AIP ontology mapping:
   - `Vessel`
   - `Port`
   - `Observation`
   - `SemanticEvent`
   - `NetworkLink`
   - `COPUpdate`

## How to Explain the Data Stack in Pitch

Use this framing:

> We are not trying to stream every raw feed into the COP. In a denied or degraded network, raw data dies first. Our system extracts operationally meaningful events, attaches provenance, scores priority under network constraints, and updates the commander’s COP with the information most likely to change a decision.

Avoid saying:

- "We made a maritime dashboard."
- "We detect jamming."
- "We implement tactical datalink protocols."
- "The LLM knows what happened."

Say instead:

- "We preserve decision-relevant meaning under bandwidth loss."
- "The COP updates from compact, citation-backed semantic events."
- "Network state changes what gets transmitted first."
- "Raw sources are retained locally; only high-value event packets cross constrained links."

## First Five Integration Tickets

1. `network_synthetic`: generate link states and bandwidth profiles.
2. `gdelt_connector`: fetch maritime OSINT events and citations for AOI.
3. `weather_connector`: fetch KMA or fallback weather hazard records.
4. `ais_port_connector`: fetch data.go.kr or load sample AIS/port records.
5. `priority_router`: rank events and emit `sent`, `deferred`, `dropped` queues.

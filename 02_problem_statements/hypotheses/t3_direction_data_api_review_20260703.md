# T3 Direction Review: Data/API Implications

Last updated: 2026-07-03

## Reviewed Direction

논문 리서치 산출물 기준으로 현재 프로젝트 방향성은 타당합니다.

> Resilient Maritime COP over Denied Networks는 해상 데이터를 많이 보여주는 대시보드가 아니라, 통신 제한 상황에서도 작전적으로 의미 있는 이벤트만 살아남게 하는 semantic COP 시스템입니다.

핵심 주장은 다음과 같습니다.

| Design claim | Why it matters for API collection |
| --- | --- |
| COP의 핵심은 원본 데이터가 아니라 임무 의미 유지 | API 수집도 raw feed 확보보다 `semantic event` 추출 가능성을 기준으로 우선순위화 |
| AIS는 truth가 아니라 claim source | AIS 단독보다 기상, OSINT, 위성/SAR, 항만, 포트/지도 context를 함께 수집 |
| 거부환경 대응은 network-aware routing으로 보여줘야 함 | 실제/합성 네트워크 상태 데이터를 별도 1급 데이터로 관리 |
| LLM/RAG는 판단자가 아니라 근거 브리핑 인터페이스 | 모든 API record는 citation/provenance/freshness 필드를 남겨야 함 |
| 해커톤 MVP는 full-sync, delta-sync, semantic-summary, store-and-forward 모드가 보여야 함 | 각 source connector는 raw snapshot과 event packet byte size를 함께 기록 |

## Data Priority

| Priority | Data family | Target event | Current preferred sources |
| --- | --- | --- | --- |
| P0 | Weather / METOC | `WEATHER_HAZARD` | data.go.kr 기상청 단기예보, KMA APIHub |
| P0 | OSINT events | `OSINT_INCIDENT` | GDELT, 공식 공지/RSS |
| P0 | Network state | `NETWORK_DEGRADATION` | synthetic network simulator, Cloudflare Radar, Ookla Open Data |
| P1 | Vessel / AIS / port | `AIS_GAP`, `ROUTE_DEVIATION`, `PORT_ANOMALY` | data.go.kr 해양수산부/Port-MIS, Global Fishing Watch, NOAA AIS |
| P1 | Map / geocoding / port layers | COP base layer, AOI context | VWorld, OSM, UN/LOCODE, World Port Index |
| P2 | SAR / EO evidence | `SAR_DARK_VESSEL_CANDIDATE` | Copernicus Sentinel-1, GFW SAR, xView3 |
| P2 | Ocean state | `SEA_STATE_RISK` | KHOA/NOSC/NIFS, Copernicus Marine, NASA Earthdata |
| P3 | Risk lists | `SANCTION_OR_WATCHLIST_MATCH` | OpenSanctions, OFAC/EU/UN public lists |

## What This Means Operationally

1. API 발급의 성공 기준은 "키가 있다"가 아니라 "raw snapshot을 받아 semantic event로 변환할 수 있다"입니다.
2. 각 API는 아래 4단계 상태를 계속 기록합니다.
   - `credential_stored`
   - `key_issued`
   - `smoke_test_passed`
   - `event_extraction_ready`
3. API가 안 되면 같은 event를 만들 수 있는 fallback source를 즉시 붙입니다.
4. 실제 선박/회사/개인을 적대 행위자로 단정하지 않고, 해커톤 데모 위험 이벤트는 synthetic 또는 masked entity로 표시합니다.

## Near-Term Collection Target

먼저 아래 6개 event가 만들어지면 데모 골격은 충분합니다.

| Event | Minimum live/snapshot source | Fallback |
| --- | --- | --- |
| `WEATHER_HAZARD` | data.go.kr 기상청 단기예보 or KMA APIHub | static sample |
| `OSINT_INCIDENT` | GDELT | hand-curated citation snippets |
| `NETWORK_DEGRADATION` | synthetic link schedule | Cloudflare/Ookla later |
| `AIS_GAP` | data.go.kr AIS/Port-MIS or GFW | synthetic AIS track |
| `PORT_ANOMALY` | Port-MIS/항만공사/World Port Index | synthetic port delay |
| `SAR_DARK_VESSEL_CANDIDATE` | Copernicus/GFW/xView3 | synthetic SAR-only detection |

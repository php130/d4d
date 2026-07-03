# API Collection Tracker

Last updated: 2026-07-04

목적: `Resilient Maritime COP over Denied Networks` 데모에 필요한 API 계정, 키, smoke test, event 변환 준비 상태를 계속 갱신합니다.

키와 비밀번호는 문서에 쓰지 않고 `/Users/mollykim/projects/D4D/.env`에만 저장합니다.

## Account / Key Status

| Priority | Service | Env credentials | Key/token env | Status | Next action |
| --- | --- | --- | --- | --- | --- |
| P0 | 공공데이터포털 | `DATA_GO_KR_USERNAME`, `DATA_GO_KR_PASSWORD` | `DATA_GO_KR_SERVICE_KEY` | `key_issued`; REST API 5건 승인; 기상 smoke passed | AIS/Port-MIS 신청 결과 재확인 및 나라장터 재시도 |
| P0 | 기상청 API허브 | `KMA_APIHUB_USERNAME`, `KMA_APIHUB_EMAIL`, `KMA_APIHUB_PASSWORD` | `KMA_APIHUB_KEY` | `key_issued`; 해상예보 API 신청 완료; smoke passed | 기상특보 endpoint 추가 신청 |
| P0 | VWorld | `VWORLD_USERNAME`, `VWORLD_PASSWORD` | `VWORLD_API_KEY` | `key_issued`; smoke passed | COP base map/geocoding connector 작성 |
| P1 | 재난안전데이터 공유플랫폼 | `SAFETYDATA_USERNAME`, `SAFETYDATA_PASSWORD` | `SAFETYDATA_API_KEY` | `application_pending`: 행정안전부_긴급재난문자 | 승인 후 key/API URL 확인; 추가 신청은 현재 사이트 알림으로 보류 |
| P1 | Global Fishing Watch | `GLOBAL_FISHING_WATCH_EMAIL`, `GLOBAL_FISHING_WATCH_PASSWORD` | `GLOBAL_FISHING_WATCH_TOKEN` | `blocked_email_verification` | 이메일 인증 후 API token 생성 |
| P2 | Copernicus Data Space | `COPERNICUS_DATASPACE_EMAIL`, `COPERNICUS_DATASPACE_PASSWORD` | `COPERNICUS_ACCESS_TOKEN` | `token_issued`; Sentinel-1 OData smoke passed | 토큰 자동 갱신 helper 작성; Sentinel-1 AOI query 작성 |
| P2 | NASA Earthdata | `NASA_EARTHDATA_USERNAME`, `NASA_EARTHDATA_PASSWORD` | `NASA_EARTHDATA_TOKEN` | `token_issued`; CMR smoke passed | ocean wind / SST / VIIRS 후보 collection shortlist 작성 |

## data.go.kr Approved APIs

| Public data PK | API | Status | Smoke test | Event use |
| --- | --- | --- | --- | --- |
| 15084084 | 기상청_단기예보 조회서비스 | approved | passed | `WEATHER_HAZARD` |
| 15129394 | 조달청_나라장터 입찰공고정보서비스 | approved | `Unauthorized` immediately after issue | procurement / supply chain event |
| 15058815 | 조달청_나라장터 공공데이터개방표준서비스 | approved | pending | procurement / contract context |
| 15116876 | 대한무역투자진흥공사_국가 목록 | approved | pending | country/entity normalization |
| 15134045 | 대한무역투자진흥공사_미국 글로벌 이슈 모니터링 정보 | approved | pending | OSINT/regulatory context |

## Known Non-data.go.kr-Key Targets

아래는 공공데이터포털 상세 페이지가 `LINK` 유형이라 원 제공기관에서 별도 신청해야 합니다.

| Source | Linked site | Event use | Status |
| --- | --- | --- | --- |
| 국토교통부_교통소통정보 | ITS OpenAPI | `LOGISTICS_CONSTRAINT` | separate key needed |
| 국토교통부_돌발상황정보 | ITS OpenAPI | `LOGISTICS_CONSTRAINT` | separate key needed |
| 행정안전부_공유플랫폼_재난대응기관 | safetydata.go.kr | response agency context | separate login/application needed |

## Non-data.go.kr API Progress

| Service | Dataset/API | Status | Smoke test | Event use |
| --- | --- | --- | --- | --- |
| 기상청 API허브 | 단기 해상예보 `/url/fct_afs_do.php` | applied / enabled | passed: HTTP 200 | `WEATHER_HAZARD`, `SEA_STATE_RISK` |
| VWorld | Address/geocoding API | existing dev key found | passed: address lookup returned `OK` | COP base layer / geocoding |
| Copernicus Data Space | OData token + Sentinel-1 catalogue | token issued | passed: Sentinel-1 product query returned sample product | `SAR_DARK_VESSEL_CANDIDATE` |
| NASA Earthdata | EDL bearer token + CMR collection search | token issued | passed: CMR collection query returned sample collection | `OCEAN_STATE`, `WEATHER_HAZARD` |
| GDELT | DOC API maritime query | no key needed | failed: HTTP 429 on latest run | `OSINT_INCIDENT` |
| Open-Meteo Marine | Busan marine forecast | no key needed | passed: wave/SST hourly fields returned | `SEA_STATE_RISK` |
| 재난안전데이터 공유플랫폼 | 행정안전부_긴급재난문자 | approval pending | pending | `OSINT_INCIDENT`, `DISASTER_ALERT` |
| Global Fishing Watch | API access token | blocked | email not verified | `AIS_GAP`, `SAR_DARK_VESSEL_CANDIDATE` |

## Latest Smoke Run

| Run | Script | Report | Result summary |
| --- | --- | --- | --- |
| `20260704_002947` | `06_prototype/scripts/smoke_test_api_sources.py` | `03_data/processed/api_smoke_tests/20260704_002947/smoke_report.json` | Passed: data.go.kr weather, KMA sea forecast, VWorld, Open-Meteo Marine, Copernicus Sentinel-1, NASA CMR. Blocked: GFW email verification, SafetyData approval. Failed transiently: GDELT HTTP 429. |

## Collection Log

| Date | Service | Action | Result |
| --- | --- | --- | --- |
| 2026-07-03 | 공공데이터포털 | General key issued and stored | success |
| 2026-07-03 | 공공데이터포털 | 기상청 단기예보 smoke test | success: `NORMAL_SERVICE` |
| 2026-07-03 | 공공데이터포털 | 나라장터 입찰공고 smoke test | follow-up: `Unauthorized` immediately after approval |
| 2026-07-03 | Credential store | User-provided account credentials stored in `.env` | success |
| 2026-07-03 | 기상청 API허브 | Login, API key stored, short sea forecast API applied | success; smoke test HTTP 200 |
| 2026-07-03 | VWorld | Existing developer key found and stored | success; geocoding smoke test `OK` |
| 2026-07-03 | Copernicus Data Space | OData access token generated and stored | success; Sentinel-1 catalogue query returned sample |
| 2026-07-03 | NASA Earthdata | Bearer token generated through logged-in profile and stored | success; CMR query returned sample collection |
| 2026-07-03 | 재난안전데이터 공유플랫폼 | 행정안전부_긴급재난문자 API use application submitted | approval pending |
| 2026-07-03 | Global Fishing Watch | Login attempted for API token page | blocked: account email not verified |
| 2026-07-04 | API smoke test script | Added and ran `smoke_test_api_sources.py` | 6 passed, 2 blocked, 1 transient failure |
| 2026-07-04 | 공공데이터포털 | 해양수산부_선박 AIS 동적정보 application form filled and confirmation attempted | final application-list verification needed; Chrome control timed out after confirm |

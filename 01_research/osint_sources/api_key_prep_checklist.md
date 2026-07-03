# API Key Prep Checklist

Last reviewed: 2026-07-01

이 문서는 D4D 해커톤 전에 미리 계정/API key/client credential을 발급받아 둘 후보를 정리한 것입니다. 목적은 해커톤 당일 데이터 수집 파이프라인을 바로 실행할 수 있게 만드는 것입니다.

## Storage Rule

- 실제 key, token, client secret은 이 저장소에 쓰지 않습니다.
- 로컬에서는 프로젝트 루트의 `.env`에만 저장합니다.
- 공유용 예시는 `.env.example`만 사용합니다.
- public repo, 발표자료, 스크린샷, 데모 영상에 key/token이 노출되지 않도록 합니다.

## Priority 0: Must Prepare First

| Service | Credential type | Where to get it | Covers / useful for | Notes |
| --- | --- | --- | --- | --- |
| 공공데이터포털 | OpenAPI 인증키 | https://www.data.go.kr/ | 방위사업청, 나라장터, 행안부 일부, KOTRA, 국토교통부, 소방청, 기상청 일부 API | 활용신청 후 인증키 발급. PC에서 신청 권장. D4D에서 가장 범용적 |
| 기상청 API허브 | API 인증키 | https://apihub.kma.go.kr/ | 위성, 레이더, 해양관측, 항공기상, 지진/화산, 예특보, 수치모델 | 회원가입 필요. 일반회원 일 호출/용량 제한 있음. 휴대전화 인증 필요 가능 |
| AI Hub | API key / aihubshell key | https://www.aihub.or.kr/devsport/apishell/list.do | 국방 합성데이터, 영상/교통/재난/로봇/자연어 데이터 다운로드 | 데이터셋별 다운로드 승인 필요. 대용량 저장공간 필요 |
| VWorld | API key | https://www.vworld.kr/dev/v4dv_static_s001.do | 지도, 공간정보, 2D/3D 배경지도, 지오코딩 | 지도 기반 데모에 유용. 서비스명/URL 등 입력 필요 |

## Priority 1: Strongly Recommended for T2/T4

| Service | Credential type | Where to get it | Covers / useful for | Notes |
| --- | --- | --- | --- | --- |
| 재난안전데이터 공유플랫폼 | 회원가입 + 활용신청 | https://www.safetydata.go.kr/ | 재난문자, 대피소, 침수, 긴급구조, 재난대응기관 | OpenAPI는 회원가입 및 활용 신청 필요 |
| 생활안전지도 | 인증키 | https://www.safemap.go.kr/dvct/openAPI.do | 안전지도, 대피장소, 사고통계, 생활안전 공간 레이어 | 별도 개발자센터에서 인증키 발급 |
| Global Fishing Watch | API access token | https://globalfishingwatch.org/our-apis/ | AIS-derived vessel activity, fishing effort, vessel presence | 비상업적 사용 중심. 계정 생성 후 API key 요청 |
| MarineTraffic | API key / API service | https://servicedocs.marinetraffic.com/ | 실시간/과거 AIS, vessel positions, vessel info, port calls | 상용/계약 기반 가능성 큼. My API Services 또는 sales/CSM 경유 |
| OpenSky Network | OAuth2 client_id/client_secret | https://opensky-network.org/data/api | ADS-B 항적, 항공기 상태, 공중 ISR 데모 | 기본 인증은 더 이상 사용하지 않음. Account page에서 API client 생성 |
| OpenSanctions | API key | https://www.opensanctions.org/api/ | 제재, PEP, entity screening, 공급망 리스크 | hosted API는 key 필요. 학술/비영리/저널리즘은 무료 key 가능 |

## Priority 2: Useful for Satellite / Space / Maritime

| Service | Credential type | Where to get it | Covers / useful for | Notes |
| --- | --- | --- | --- | --- |
| Copernicus Data Space / Sentinel Hub | OAuth client / access token | https://dataspace.copernicus.eu/ | Sentinel 위성영상, EO Browser, Sentinel Hub APIs | 계정에서 OAuth client 등록 후 token 발급 |
| NASA Earthdata | Earthdata Login token | https://urs.earthdata.nasa.gov/ | NASA Earth observation, FIRMS/CMR/LAADS 등 | profile에서 Generate Token. Bearer token으로 사용 |
| USGS EarthExplorer / M2M | ERS account + application token | https://m2m.cr.usgs.gov/ | Landsat/USGS imagery search/download | M2M application token 방식 확인 필요 |
| Space-Track | Account login | https://www.space-track.org/auth/createAccount | satellite catalog, SSA, TLE/GP data | 개인/기관별 계정 필요. username/password 공유 금지 |
| CelesTrak | Usually no key for public TLE | https://celestrak.org/ | TLE/GP orbital data | 대부분 공개 URL로 가능. Space-Track 연동 도구는 Space-Track 계정 필요 |
| 국립해양조사원 국가해양위성센터 | 인증Key | https://nosc.go.kr/openapi/actionOpenApiIssue.do | 해양위성/해양환경 API | 별도 인증Key 발급 |
| 국립수산과학원 OPEN API | 인증키 | https://www.nifs.go.kr/openApi/actionOpenapiInfoList.do | 정선해양관측, 적조, 해양환경 | 홈페이지에서 key 발급. 일부 API 제공중단 여부 확인 필요 |
| 해양수산 빅데이터플랫폼 VadaHub | API key / 활용신청 가능성 | https://www.vadahub.go.kr/bigdata/openApi/index.do | 해양수산 공간정보 API 기반 지도서비스 | 서비스별 신청/약관 확인 필요 |

## Priority 3: Useful but May Need Approval or Non-immediate Setup

| Service | Credential type | Where to get it | Covers / useful for | Notes |
| --- | --- | --- | --- | --- |
| KISA C-TAS | 계정 승인 + Export Key/OrgKey for API | https://ctas.krcert.or.kr/index | 악성IP/도메인, 위협정보, 보안공지, AI데이터셋 | 개방형은 회원가입 후 사용 가능. API 연동은 승인/기관 정보 필요 가능 |
| ACLED | myACLED account + OAuth token | https://acleddata.com/api-documentation/getting-started | conflict/protest/political violence event data | 계정 필요. 기관 이메일이 접근 범위에 유리할 수 있음 |
| UN Comtrade | API subscription key | https://comtradedeveloper.un.org/ | 국가별/품목별 무역 데이터, 공급망 리스크 | 무료 key 가능. 호출량 제한/프리미엄 구분 확인 |

## Priority 4: Usually No Key Needed, But Good to Bookmark

| Service | Access | Useful for | Notes |
| --- | --- | --- | --- |
| GDELT | Public files/API/BigQuery | 뉴스 이벤트, 지리코딩, 타임라인 | 인증 없이 시작 가능. 대량 처리 설계 필요 |
| HDX Humanitarian Data Exchange | Public dataset/API for many resources | 재난/분쟁/인도주의 지표 | 일부 dataset별 라이선스 확인 |
| OpenStreetMap / Overpass | Public API | 도로, 건물, POI, 항만/공항/시설 | 무거운 쿼리는 제한. ODbL 준수 |
| Natural Earth | Public download | 지도 배경, 국가/해안선 | public domain |
| OFAC / EU sanctions list | Public download/search | 제재/공급망 스크리닝 | OpenSanctions와 함께 검증용으로 사용 |
| NOAA MarineCadastre AIS | Public download | AIS 분석 연습 | 미국 해역 중심 |

## Recommended Issuance Order

1. 공공데이터포털
2. 기상청 API허브
3. AI Hub
4. VWorld
5. 재난안전데이터 공유플랫폼
6. 생활안전지도
7. Global Fishing Watch
8. OpenSky Network
9. Copernicus Data Space
10. NASA Earthdata
11. OpenSanctions
12. MarineTraffic
13. UN Comtrade
14. ACLED
15. Space-Track
16. KISA C-TAS

## Suggested Environment Variables

```bash
DATA_GO_KR_SERVICE_KEY=
KMA_APIHUB_KEY=
AIHUB_API_KEY=
VWORLD_API_KEY=
SAFETYDATA_API_KEY=
SAFEMAP_API_KEY=
GLOBAL_FISHING_WATCH_TOKEN=
MARINETRAFFIC_API_KEY=
OPENSKY_CLIENT_ID=
OPENSKY_CLIENT_SECRET=
COPERNICUS_CLIENT_ID=
COPERNICUS_CLIENT_SECRET=
NASA_EARTHDATA_TOKEN=
USGS_M2M_APP_TOKEN=
SPACE_TRACK_USERNAME=
SPACE_TRACK_PASSWORD=
OPENSANCTIONS_API_KEY=
UN_COMTRADE_PRIMARY_KEY=
ACLED_CLIENT_ID=
ACLED_CLIENT_SECRET=
NIFS_API_KEY=
NOSC_API_KEY=
KISA_CTAS_EXPORT_KEY=
KISA_CTAS_ORG_KEY=
```

## First API Smoke Tests to Build

미리 key가 확보되면 아래 순서로 작은 수집 스크립트를 만드는 것이 좋습니다.

1. `data.go.kr`: 방위사업청 방산업체 지정현황 또는 나라장터 입찰공고 10건 조회
2. `KMA APIHub`: 특정 지역/해역 예특보 또는 위성/레이더 metadata 조회
3. `VWorld`: 주소/좌표 변환 또는 지도 tile/static map 호출
4. `OpenSky`: 특정 bounding box의 항공기 상태 1회 조회
5. `Global Fishing Watch`: AOI 기준 vessel/fishing stats 조회
6. `OpenSanctions`: 업체명 1개 batch screening
7. `NASA Earthdata`: token 인증 확인 및 FIRMS/CMR 접근 테스트


# OSINT Source Catalog for D4D

Last reviewed: 2026-06-29

이 문서는 D4D 해커톤에서 국방/안보 문제를 다룰 때 참고할 수 있는 국내외 공개 데이터와 OSINT 소스의 1차 카탈로그입니다. 목적은 "가장 멋진 데이터"를 찾는 것이 아니라, 24시간 해커톤에서 빠르게 검증 가능한 입력 데이터를 확보하고, 여러 소스를 연결해 의사결정 가능한 인텔리전스를 만드는 것입니다.

## Operating Assumptions

- 주최 측 기본 데이터셋은 제공되지 않는다고 가정합니다.
- 공개 데이터, 공개 API, 합성 데이터, 샘플 데이터 중심으로 접근합니다.
- 원본 raw data는 외부 공개/재배포하지 않습니다.
- API key, token, credential은 저장소에 저장하지 않습니다.
- 개인정보, 얼굴 식별 정보, 계정 정보, 정밀 위치정보는 데모에서 마스킹합니다.
- 실제 시스템에 영향을 주는 수집/테스트는 하지 않습니다.

## Fast Shortlist

해커톤 당일 바로 쓰기 좋은 조합입니다.

| Use case | Recommended sources | Why |
| --- | --- | --- |
| 방산 공급망 노출 조기경보 | 방위사업청 공공데이터, 나라장터, KOTRA, OpenSanctions, KISA/KrCERT, StealthMole | 방산업체/조달/해외시장/제재/사이버 노출 신호를 연결하기 좋음 |
| 해상 회색지대 조기경보 | 해양수산부 AIS, MarineTraffic, Global Fishing Watch, KHOA/바다누리, KMA, NASA/Copernicus, GDELT | 선박 이동, 항만/해역 환경, 뉴스 이벤트, 위성/기상 신호를 융합 가능 |
| 공중/우주 ISR 코파일럿 | OpenSky, CelesTrak, Space-Track, KMA/KMA API Hub, Copernicus, NASA Earthdata | 항적, 위성 궤도, 기상, 위성영상, 공개 이벤트를 연결 가능 |
| 재난/거부환경 C2 | 재난안전데이터 공유플랫폼, 생활안전지도, 소방안전 빅데이터, KMA, NASA FIRMS, ITS 교통정보 | 재난·화재·교통·기상 신호를 지휘통제/대피/지속지원 문제로 연결 가능 |
| OSINT 인텔 코파일럿 | GDELT, ACLED, HDX, OpenStreetMap, Natural Earth, OpenSanctions, KISA, public news/RSS | 자연어 질의, citation, event timeline, map/graph 데모에 적합 |

## Korea: Defense and Procurement

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| 방위사업청 공공데이터 개방현황 | https://www.dapa.go.kr/dapa/index.do?menuSeq=3092 | 군수품 조달정보, 국내/외 조달계획, 입찰공고, 계약정보, 방산업체, 특허, 용어사전 등 | 방산 공급망, 조달 인텔리전스, 국방 사업 동향 분석 | 개별 데이터는 data.go.kr에서 API/파일 여부 확인 필요 |
| 방위사업청 방산업체 지정현황 | https://www.data.go.kr/data/15081929/fileData.do | CSV, XML/JSON 변환 API | 방산 공급망 watchlist의 seed list | 업체명 정규화 필요 |
| 방위사업청 국내조달 조달계획 | https://www.data.go.kr/data/15050919/fileData.do | CSV, XML/JSON 변환 API | 조달 수요, 품목/일정 기반 시장 신호 | 실시간성보다는 계획 데이터 |
| 방위사업청 국방전자조달 사전의향서 | https://www.data.go.kr/data/15119858/fileData.do | CSV, XML/JSON 변환 API | 신규 조달요구 품목, 시장 수요 사전 파악 | 공란 필드 존재 가능 |
| 방위사업청 신기술 입찰공고 사업 | https://www.data.go.kr/data/15089079/fileData.do | 파일 데이터 | 국방 R&D/신기술 방향성 파악 | 원문 공고 세부 확인 필요 |
| 방위사업청 국방통합 용어사전 | https://www.data.go.kr/data/15089127/fileData.do | 파일 데이터 | glossary 확장, 국방 문서 해석 | 용어 중 민감한 맥락은 공개 범위 내에서만 사용 |
| 국방부 국방통계연보 | https://www.data.go.kr/data/15050545/fileData.do | PDF | 국방 일반현황, 정책/인사/군수/시설 통계 배경자료 | PDF 추출 필요 |
| 조달청 나라장터 입찰공고정보서비스 | https://www.data.go.kr/data/15129394/openapi.do | REST API, JSON/XML | 방산 외 공공 조달 연계, 특정 기술/품목 발주 신호 | data.go.kr API key 필요 |
| 조달청 나라장터 공공데이터개방표준서비스 | https://www.data.go.kr/data/15058815/openapi.do | 입찰/낙찰/계약 API | 공급망/업체/계약 관계 분석 | 조회기간 제한/부하 정책 확인 필요 |
| KOTRA 해외정보/공공데이터 | https://www.kotra.or.kr/subList/20000006759 | 해외시장뉴스, 국가/산업/규제 정보, 일부 API | 방산 수출국/공급망/규제 리스크 | 일부 서비스 로그인 필요 |
| KOTRA 국가 목록 API | https://www.data.go.kr/data/15116876/openapi.do | 국가/지역 기초 정보 API | 국가 단위 메타데이터 보강 | API key 필요 |
| KOTRA 미국 글로벌 이슈 모니터링 정보 | https://www.data.go.kr/data/15134045/openapi.do | 이슈 모니터링 API | 글로벌 공급망/규제/관세 이슈 브리핑 | 국가별 유사 API 추가 탐색 필요 |

## Korea: Maritime, Ocean, AIS

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| 해양수산부 AIS 정보 | https://www.data.go.kr/data/15141997/fileData.do | AIS CSV, XML/JSON 변환 API | T4 MDA, 선박 이상징후, 선박 위치 샘플 | 공개 샘플 규모 제한 가능 |
| 해양수산부 선박 AIS 동적정보 | https://www.data.go.kr/data/15129186/fileData.do | AIS 동적정보, XML/JSON 변환 API | 항로/속도/위치 기반 데모 | row 수가 작을 수 있어 샘플용 |
| MarineTraffic | https://marinetraffic.com/ | AIS vessel tracking, API docs at servicedocs.marinetraffic.com | 실시간/과거 선박 위치, port calls, vessel particulars | 상용/과금 가능성 높음. 약관 확인 필요 |
| MarineTraffic AIS API docs | https://servicedocs.marinetraffic.com/ | Vessel positions, historical track, ports, vessel info API | 유료 접근 가능 시 데모 품질 향상 | API key 필요 |
| Global Fishing Watch | https://globalfishingwatch.org/ | Global AIS-derived vessel activity, fishing activity datasets | 불법조업/해상민병대/선박행동 분석 아이디어 | API/다운로드 정책 확인 필요 |
| Global Fishing Watch AIS vessel presence | https://globalfishingwatch.org/platform-update/global-ais-vessel-presence-dataset/ | AIS vessel presence from 2012 to recent delay | 해상 활동 밀도, vessel type, flag filter | 개인 선박 정밀 추적보다는 집계 분석에 적합 |
| 국립해양조사원 바다누리/해양정보 | http://www.khoa.go.kr/oceangrid/ | 조위, 해류, 수온, 염분, 예측정보 등 | 해상작전 환경, AIS 이상탐지 보조 변수 | 일부 API 개편/대체서비스 확인 필요 |
| 국립해양조사원 국가해양위성센터 | https://nosc.go.kr/ | 해양위성/해양환경 관련 API key 발급 메뉴 | 위성 기반 해양환경, 해양 색/수온 등 | 계정/API key 필요 가능 |
| 해양수산 빅데이터플랫폼 VadaHub | https://www.vadahub.go.kr/ | 해양수산 데이터, 격자 지도, Open API | 해양공간/항만/생태/이용현황 융합 | 인증키/활용신청 필요 가능 |
| 국립수산과학원 OPEN API | https://www.nifs.go.kr/openApi/actionOpenapiInfoList.do | 실시간 해양관측, 정선해양 등 | 해양환경 변수 보강 | 품질처리 전 데이터 주의 |
| NOAA AccessAIS / MarineCadastre | https://coast.noaa.gov/digitalcoast/tools/ais.html | U.S. vessel traffic data by geography/time | AIS 데이터 처리/시각화 연습에 좋음 | 미국 해역 중심 |
| NOAA Marine Cadastre Vessel Traffic | https://hub.marinecadastre.gov/pages/vesseltraffic | U.S. vessel traffic downloads/maps | AIS heatmap, transit count 분석 | 미국 해역 중심 |

## Korea: Weather, Disaster, Fire, Public Safety

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| 기상자료개방포털 | https://data.kma.go.kr/ | 지상/해양/고층/항공 관측, 예특보, 기후통계 | 작전환경, 해상/공중/재난 변수 | 일부 API는 data.go.kr 활용신청 |
| 기상청 API허브 | https://apihub.kma.go.kr/ | 위성 16개 채널, 지표면온도, 산불탐지 등 산출물 | 위성/기상/산불/재난 조기경보 | 회원/API key 필요 가능 |
| 재난안전데이터 공유플랫폼 | https://www.safetydata.go.kr/ | 재난문자, 대피소, 침수, 저수지수위, 긴급구조정보 등 | C2, 재난 대응, 지속지원, 대피/위험도 분석 | API별 접근조건 확인 |
| 행정안전부 재난대응기관 API | https://www.data.go.kr/data/15139684/openapi.do | 재난대응기관 정보, 일 1회 갱신 | 대응기관 네트워크, incident routing | data.go.kr API key 필요 |
| 생활안전지도 | https://www.safemap.go.kr/ | 재난안전, 치안, 기반시설, 보건, 교통, 환경, 시설안전 지도 | 지역 위험도, 대피/시설/재난 맥락 | 서비스/API 신청 필요 가능 |
| 생활안전지도 OpenAPI Data | https://safemap.go.kr/opna/data/dataListRenew.do | 대피장소, 재난보험시설물, 사고통계 등 XML API | 지도 기반 안전/위험 레이어 | 일부 서비스별 신청 |
| 소방안전 빅데이터 플랫폼 | https://bigdata-119.kr/ | 소방안전/소방산업 관련 데이터 | 화재·구조·구급 패턴, 재난 대응 | 이용조건 확인 |
| 소방청 공공데이터 개방 | https://www.nfa.go.kr/nfa/releaseinformation/0011 | 화재정보, 위험물, 구조구급, 119 신고 현황 | 재난/화재/긴급구조 시나리오 | 상세 데이터는 data.go.kr 탐색 |
| 소방청 119 신고 전화 유형 | https://www.data.go.kr/data/15061186/fileData.do | 연도별 119 신고 유형 통계 | 재난 수요/부하 예측 샘플 | 통계성 데이터 |
| 소방청 119 신고 지령시스템 운영 현황 | https://www.data.go.kr/data/15052715/fileData.do | 신고 접수/지령 처리 현황 | 긴급대응 워크플로우 배경 | 오래된 데이터일 수 있음 |
| NASA FIRMS | https://www.earthdata.nasa.gov/data/tools/firms | Global near-real-time active fire/hotspot data | 산불/폭발/열원 징후, 재난 경보 | 화재/열원 오탐 가능, 해석 주의 |

## Korea: Communications, RF, Space

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| 전파누리 | https://www.spectrummap.kr/ | 주파수 이용현황, 무선국 정보, 통계 | 통신 인프라, 거부환경, 산악/도서 통신 커버리지 | 세부 다운로드/API 확인 필요 |
| 과기정통부 공공데이터 제공 | https://www.msit.go.kr/user/ifm/publicDataProvd3.do?mId=72&mPid=70&sCode=user | 과기정통부/소속기관/산하기관 데이터 제공목록 | 통신/전파/우주 데이터 발굴 시작점 | 데이터별 신청 |
| 중앙전파관리소 위성방송현황조사 | https://www.data.go.kr/data/15090111/fileData.do | 한반도 감시범위 내 방송통신 위성명, 궤도위치, 주파수 등 | 위성/전파 환경, 공중·우주 ontology | 방송통신 위성 중심 |
| 중앙전파관리소 비정지궤도위성 궤도면 정보 | https://www.data.go.kr/data/15150466/fileData.do | 비정지궤도위성 궤도경사각, 원지점 등 | 우주감시, 위성 운영/충돌 리스크 배경 | ITU 등록정보 기반 공란 가능 |
| KCA 산악지역 무선국현황(국립공원) | https://www.data.go.kr/data/15133028/fileData.do | 3G/4G/5G 무선국 위치, 위경도 | 산악/도서 작전 통신 가용성 추정 | 비식별/부분공개 가능성 |
| KCA 산악지역 기지국현황(군립공원) | https://www.data.go.kr/data/15133040/fileData.do | 군립공원 이동통신 기지국 정보 | 산악 통신 커버리지, T1/T3 거부환경 | 최신성 확인 필요 |
| KARI 공공데이터개방 | https://www.kari.re.kr/kor/contents/84 | 연구보고서, 기술/특허, 일부 Open API 안내 | 우주/항공 레퍼런스와 기술 배경 | 위성 원자료 직접 개방과는 다를 수 있음 |
| KARI 위성영상 소개 | https://kari.re.kr/kor/64/video/SG/SG | 위성영상/OPEN KARI 안내 | 국내 위성 맥락 조사 | 실제 영상 접근 조건 확인 필요 |

## Korea: Geospatial, Transport, AI/Synthetic Data

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| 공공데이터포털 | https://www.data.go.kr/ | 국내 공공 데이터/API 통합 검색 | 모든 국내 데이터 탐색의 출발점 | API key/활용신청 필요 다수 |
| 국가중점데이터 | https://www.data.go.kr/tcs/eds/selectCoreDataListView.do | 국가 핵심 데이터 목록 | 신뢰도 높은 공공 데이터 탐색 | 주제별 세부 확인 필요 |
| 브이월드 | https://www.vworld.kr/ | 2D/3D 지도, 국가공간정보, 공간정보 다운로드 | 지도/지형/시설/공간 분석 | API key 필요 가능 |
| 국가공간정보포털 | https://www.nsdi.go.kr/ | 국가공간정보, SHP/지도 데이터 | 지형, 행정구역, 시설 기반 지도 | 데이터별 라이선스 확인 |
| 국토교통부 교통소통정보 | https://www.data.go.kr/data/15040463/openapi.do | 도로별 실시간 속도 정보 API | 물류/지속지원/대피 경로 시뮬레이션 | data.go.kr API key 필요 |
| 국토교통부 돌발상황정보 | https://www.data.go.kr/data/15040465/openapi.do | 사고, 고장, 낙하물, 침수, 공사 등 돌발정보 API | C2/지속지원/재난 대응 | 실시간 API 정책 확인 |
| 국토교통부 CCTV 화상자료 | https://www.data.go.kr/data/15040466/openapi.do | 도로 CCTV 영상 API | 교통/재난 상황 확인 | 개인정보/영상 노출 주의 |
| ITS 국가교통정보센터 | https://www.its.go.kr/ | 국가 교통정보 포털 | 교통/물류/대피 경로 | API 신청/제한 확인 |
| AI Hub | https://www.aihub.or.kr/ | AI 학습 데이터, 오픈 API, 국방/재난/교통/로봇/영상 데이터 | 합성 데이터, CV/LLM/RAG 실험 | 회원가입/사용신청/라이선스 확인 |
| AI Hub 군 경계 작전 환경 합성데이터 | https://aihub.or.kr/aihubdata/data/view.do?aihubDataSe=data&dataSetSn=71856 | 국방 경계 작전 합성 이미지 | T1/T5 CV 데모, 합성 데이터 기반 모델 평가 | 다운로드 조건/라이선스 확인 |

## Korea: Cyber and Threat Intelligence

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| KISA 보호나라/KrCERT | https://www.boho.or.kr/ | 보안공지, 취약점, 침해사고, C-TAS 안내 | T2 사이버 위협 브리핑, 취약점/보안공지 RAG | 일부 데이터는 게시판 크롤링보다 공공데이터/API 확인 권장 |
| KISA C-TAS | https://ctas.krcert.or.kr/index | 사이버 위협정보 공유, 가입/승인 후 이용 | IOC, 악성코드, 악성이메일, 위협정보 연동 | 승인 필요, 부당 사용 금지 |
| C-TAS 안내 | https://www.kisa.or.kr/1020604 | C-TAS 사업내용, 위협정보 공유 | 운영/정책 배경 | 실제 데이터 접근은 회원 승인 필요 |
| C-TAS Export API 활용 안내 | https://www.boho.or.kr/kr/bbs/view.do?bbsId=B0000132&menuNo=205022&nttId=25824 | Export API 활용 사례 | 내부 위협DB/대시보드 연결 아이디어 | 기관 가입/키 필요 |
| KISA 보호나라KrCERT 게시판기본 | https://www.data.go.kr/data/15155789/fileData.do | 게시판 기본 데이터, XML/JSON 변환 API | 보안공지/취약점 RAG seed | 게시판별 상세 본문 추가 확인 필요 |

## Global: Maritime, Aviation, Space, Earth Observation

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| NOAA AccessAIS | https://coast.noaa.gov/digitalcoast/tools/ais.html | U.S. vessel traffic by geography/time | AIS 분석 연습, heatmap, 이상행동 baseline | 미국 해역 중심 |
| Global Fishing Watch | https://globalfishingwatch.org/ | Global AIS/fishing activity | 불법조업, 해상민병대, 선박 활동 패턴 | 약관/API 확인 |
| OpenSky Network | https://opensky-network.org/ | ADS-B, Mode-S, ADS-C, FLARM, VHF data | 공중 ISR, 항공기 항적, 비정상 접근 이벤트 | 역사 데이터는 접근 조건 다름 |
| OpenSky API | https://opensky-network.org/data | Live/historical aircraft position API | 지도/타임라인 데모에 적합 | rate limit/로그인 정책 확인 |
| CelesTrak | https://celestrak.org/ | TLE/GP orbital data, satellite catalog | 위성 궤도/우주상황인식, 공중·우주 ontology | 궤도 계산 이해 필요 |
| CelesTrak NORAD GP Element Sets | https://celestrak.org/NORAD/elements/ | Active satellites, GEO, debris 등 GP/TLE | 위성 접근/가시성/궤도 시각화 | military-sensitive 해석은 공개 범위 내 |
| Space-Track | https://www.space-track.org/ | Space object catalog, SSA data | 우주감시/위성 추적 | 계정/약관 필요 |
| Copernicus Data Space Ecosystem | https://dataspace.copernicus.eu/ | Sentinel missions and EO data | 위성영상, SAR, 해상/지상 변화 탐지 | 계정/쿼터 확인 |
| Copernicus Sentinel Hub APIs | https://dataspace.copernicus.eu/analyse/apis | REST APIs for raw/rendered/statistical satellite imagery | 빠른 EO 데모, 지도 레이어 | credentials 필요 |
| NASA Earthdata | https://www.earthdata.nasa.gov/ | NASA Earth observation archive/tools | 위성/기상/환경 데이터 | 계정 필요 데이터 존재 |
| USGS EarthExplorer | https://earthexplorer.usgs.gov/ | Landsat, aerial photos, cartographic products | 위성영상/지형/변화 탐지 | USGS account 필요 가능 |
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/ | MODIS/VIIRS active fire/thermal anomaly | 산불/열원/폭발 가능 신호 | 열원은 원인 단정 금지 |

## Global: Events, Conflict, Humanitarian, Geospatial

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| GDELT Project | https://www.gdeltproject.org/ | Global news/events, 300+ event categories, geocoded, updates every 15 min | 뉴스 기반 OSINT event timeline, early warning | 자동 추출 오탐/중복 검증 필요 |
| GDELT data access | https://www.gdeltproject.org/data.html | Raw files, Analysis Service, BigQuery | 대량 뉴스/이벤트 분석 | query 설계 필요 |
| ACLED | https://acleddata.com/ | Political violence/protest events | 분쟁/시위/폭력 이벤트 지도, 안정성 분석 | 라이선스/가입/인용 규정 확인 |
| HDX Humanitarian Data Exchange | https://data.humdata.org/ | Crisis/humanitarian datasets | 재난/분쟁/인도주의 맥락 | 출처별 품질 차이 |
| HDX HAPI | https://data.humdata.org/hapi | Standardized humanitarian indicators API | 자동 워크플로/대시보드 | API 범위 확인 |
| OpenStreetMap | https://www.openstreetmap.org/ | Roads, buildings, POIs, infrastructure | 지도/경로/시설/항만/공항/대피소 | ODbL 준수, 품질 지역차 |
| Overpass API | https://wiki.openstreetmap.org/wiki/Overpass_API | OSM custom data extraction | 특정 AOI 시설/도로/항만 추출 | 무거운 query 제한 주의 |
| Natural Earth | https://www.naturalearthdata.com/ | Public domain vector/raster basemap | 빠른 지도 배경/국경/해안선 | 고정밀 작전지도는 아님 |

## Global: Sanctions, Trade, Supply Chain

| Source | URL | Data / API | D4D relevance | Caveats |
| --- | --- | --- | --- | --- |
| OpenSanctions | https://www.opensanctions.org/ | Sanctions, PEPs, persons/entities of interest from many sources | 업체/선박/조직 screening, 공급망 리스크 | 오탐 가능, due diligence 대체 불가 |
| OpenSanctions API | https://www.opensanctions.org/api/ | Search/batch screening API | 이름/회사/선박 엔티티 매칭 | API key/요금제 확인 |
| OFAC Sanctions List Service | https://ofac.treasury.gov/sanctions-list-service | SDN and consolidated list downloads | 제재/거래상대 리스크 | 미국 제재 중심 |
| OFAC Sanctions Search | https://sanctionssearch.ofac.treas.gov/ | Sanctions search UI | 수동 확인/검증 | due diligence 대체 불가 |
| EU Consolidated Financial Sanctions List | https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions | EU sanctions list | 유럽 제재 리스크 | 데이터 형식 확인 필요 |
| EU Sanctions Map | https://www.sanctionsmap.eu/ | EU sanctions map and lists | 국가/정책 맥락 브리핑 | 법적 해석은 전문가 검토 |
| UN Comtrade | https://comtrade.un.org/ | Global trade statistics by product/partner | 방산/이중용도 공급망, 국가별 무역 흐름 | HS code mapping 필요 |
| UN Comtrade Trade Data | https://comtradeplus.un.org/TradeFlow | Data preview/API with free key limits | 자동 수집 가능 | 무료 API call/record 제한 |

## Candidate Data Pipelines

### 1. Defense Supply Chain Exposure Watch

Input:

- 방산업체 지정현황
- 나라장터/방위사업청 조달계획
- KOTRA 국가/시장/규제 정보
- OpenSanctions/OFAC/EU sanctions
- KISA/KrCERT 보안공지
- StealthMole credential exposure signal if available

Output:

- 업체별 리스크 카드
- 제재/국가/조달/사이버 노출 근거
- "조사 우선순위" 점수와 추천 조치

### 2. Maritime Gray-zone Early Warning

Input:

- AIS: 해양수산부, MarineTraffic, Global Fishing Watch, NOAA sample
- Ocean/weather: KHOA, VadaHub, KMA
- Satellite/fire/EO: NASA FIRMS, Copernicus, NASA Earthdata
- News/events: GDELT, ACLED

Output:

- 특정 해역/항만의 이상징후 타임라인
- 선박 활동 밀도/항로 변화
- 뉴스/기상/항만/선박 신호 기반 warning brief

### 3. Air and Space ISR Fusion Copilot

Input:

- OpenSky aircraft tracks
- CelesTrak/Space-Track satellite orbit data
- KMA aviation/weather/satellite data
- Copernicus/NASA imagery
- GDELT news events

Output:

- AOI 기반 공중/우주 상황 요약
- 비정상 접근 이벤트 후보
- 항적/궤도/기상/뉴스 citation view

### 4. Disaster and Denied-environment C2

Input:

- 재난안전데이터 공유플랫폼
- 생활안전지도
- 소방안전 빅데이터/119 통계
- KMA weather alerts
- NASA FIRMS thermal anomalies
- ITS traffic/incident data

Output:

- 재난/침수/화재/교통/대피소 통합 상황도
- 통신/교통 단절 시 우회 경로 또는 우선 대응기관 추천
- C2 briefing and runbook

## Next Validation Checklist

- [ ] `01_research/osint_sources/api_key_prep_checklist.md` 기준으로 미리 발급 가능한 key/token/account를 확보한다.
- [ ] API key 없이 바로 다운로드 가능한 데이터와 신청이 필요한 데이터를 구분한다.
- [ ] 각 소스의 라이선스/약관/재배포 가능 여부를 확인한다.
- [ ] 해커톤 데모에 쓸 수 있는 샘플 100~1,000 rows를 만든다.
- [ ] 개인정보/정밀 위치정보/민감정보가 포함되는지 확인한다.
- [ ] T2/T4 후보 문제별로 최소 데이터 조합 2개를 골라 실제 호출 테스트를 한다.
- [ ] citation/provenance 필드를 공통 스키마로 설계한다.

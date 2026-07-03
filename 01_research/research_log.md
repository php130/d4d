# Research Log

| Date | Source | Type | Key Takeaway | Follow-up |
| --- | --- | --- | --- | --- |
| 2026-06-29 | D4D Luma event page | Event page | T2 OSINT & Defense Intelligence가 현재 니즈와 가장 잘 맞음 | 문제정의 후보 3개 만들기 |
| 2026-06-29 | Palantir AIP docs | Platform docs | AIP는 data/ontology 위에 workflow, agent, eval을 올리는 구조 | AIP 용어와 가능한 데모 구조 정리 |
| 2026-06-29 | StealthMole Darkweb Tracker page | Platform page | 검색, 필터, 데이터 캔버스, 연결 분석, 지도, API 통합이 핵심 기능 | 실제 접근 가능 여부와 테스트 계정 확인 |
| 2026-06-29 | D4D_SEOUL Google Sheet | Google Sheet | 트랙별 문제 23개와 용어 88개를 versioned dataset으로 구축 | T2 후보 문제 우선순위 평가 |
| 2026-06-29 | D4D hackathon rules and data Q&A | Rules / Q&A | 기밀정보 금지, raw data 재배포 금지, 제출물 보안, 주최측 기본 데이터셋 미제공 원칙 확인 | 데이터 소스 탐색과 제출물 체크리스트에 반영 |
| 2026-06-29 | Domestic/international OSINT source scan | Web research | 방산 조달, AIS/해양, 기상·위성, 재난안전, 통신·전파, 사이버, 제재/무역 데이터 카탈로그 구축 | 우선 후보 API 3~5개 실제 호출 테스트 |
| 2026-07-01 | OpenAlex/arXiv literature seed collection | Scholarly metadata | 15개 topic, 32개 query로 논문 메타데이터 265건 수집, 중복 제거 후 228건 구축 | first reading queue 기반으로 핵심 논문 skim/extraction |
| 2026-07-03 | Google Sheet refresh and Discord track explanations | Sheet / Discord brief | 최신 시트 기준 세부과제 변경 없음. 디스코드 설명은 트랙 의도와 T3/T4 경계 해석을 보강 | T4 maritime gray-zone topic을 T4 또는 T3/COP 관점으로 이중 프레이밍 |
| 2026-07-03 | T3 semantic COP deep research | Scholarly metadata / snowball | T3 focused query 28개와 OpenAlex snowball로 raw 464건, deduped 418건 수집. reading queue, concept map, architecture, dataset candidates, pitch evidence 작성 | Priority A 논문부터 skim/extraction 진행 |
| 2026-07-01 | OSINT API key issuance scan | Web research | 사전 발급 가능한 API key/token/account 후보를 우선순위별 체크리스트로 정리 | Priority 0~1부터 계정/키 발급 후 smoke test 스크립트 작성 |
| 2026-06-29 | Palantir / StealthMole platform materials | Official docs / website / YouTube | Palantir AIP 학습 브리프, Build with AIP 예제 인덱스, StealthMole 제품 브리프, YouTube 영상 인덱스 구축 | 핵심 영상 caption 기반 summary card 작성 |
| 2026-07-01 | Palantir Foundry D4D tenant | Live Chrome walkthrough | Home, Apps menu, Compass, Data Connection, Pipeline Builder, Ontology Manager, Object Explorer, Workshop, AIP Logic, Code Repositories, Training의 실제 진입점과 생성 메뉴 확인 | 샘플 pipeline/object/module을 사용자 확인 후 deeper walkthrough |
| 2026-07-01 | Palantir Foundry installed examples | Live example execution | AIP Now Ontology의 Reference Landing Page, Route Alert Inbox, Route Overview, Flights Map, Aircraft Gantt, Ticket with Comments, Metrics/GeoJSON/Time Series pipelines 실행 확인 | Route Alert ontology/action type과 pipeline node schema를 더 깊게 확인 |
| 2026-07-01 | Palantir Foundry Route Alert workflow | Live deep dive | Route Alert object 23 properties, 4 action types, Route Alert Comment object, Metrics & Alerts pipeline outputs, Flights Map table mode를 추적 | AIP Logic/Analyst/Vertex Graph 예제 확인 |
| 2026-07-03 | Resilient Maritime COP data/API plan | Web research / architecture planning | T3 Semantic COP/S-DOT 주제에 맞춰 AIS, SAR, 기상, 항만, OSINT, 네트워크 상태 데이터를 semantic event 중심으로 재구성 | 최소 데이터 스택으로 smoke test와 synthetic scenario 설계 |
| 2026-07-03 | Resilient Maritime COP connection guide | Implementation planning | API key 없는 fallback부터 국내 core API, 국제 maritime intelligence, premium source까지 단계별 연결 순서와 connector 패턴 정의 | First five integration tickets 구현 |

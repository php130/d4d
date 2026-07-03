# Palantir Foundry Live Walkthrough

Date: 2026-07-01  
Workspace: D4D hackathon Foundry tenant  
Method: read-only Chrome walkthrough using the user's signed-in session

## Purpose

이 문서는 Palantir Foundry를 "기능명 암기"가 아니라 실제 해커톤 작업으로 연결하기 위한 기능 지도입니다. 사용자가 나중에 "AIS 데이터를 올려줘", "위협 알림 대시보드를 만들어줘", "ontology에 객체를 추가해줘"처럼 요청했을 때 어느 앱에서 어떤 흐름으로 처리할지 빠르게 판단하는 것이 목표입니다.

이런 방식은 보통 아래 표현을 섞어서 부를 수 있습니다.

- Capability mapping: 플랫폼이 실제로 무엇을 할 수 있는지 기능 단위로 지도화
- Affordance mapping: 화면이 사용자에게 어떤 행동을 허용하는지 UI 단위로 정리
- Task-based walkthrough: 실제 과업을 가정하고 앱/탭/버튼 흐름을 따라가며 학습
- Platform reverse onboarding: 공식 온보딩을 수동으로 다시 구성해 우리 과제에 맞게 재해석

이번 작업은 `task-based walkthrough + capability mapping`에 가깝습니다.

## Safety Scope

- 실제 데이터 업로드, 프로젝트 생성, 예제 설치, 저장, 삭제, 권한 변경은 수행하지 않았습니다.
- 메뉴 열기, 앱 이동, 화면 스냅샷 읽기, 생성 버튼의 선택지 확인까지만 수행했습니다.
- AIP Assist나 LLM 입력창에는 워크스페이스/개인 정보를 보내지 않았습니다.

## High-Level Mental Model

Foundry에서 해커톤 데모를 만들 때의 기본 흐름은 아래처럼 보는 것이 좋습니다.

1. Data Connection 또는 Pipeline Builder로 공개 데이터, CSV, JSON, 문서, API 결과를 가져온다.
2. Pipeline Builder, Code Workspaces, Code Repositories, Jupyter 등으로 데이터를 정제한다.
3. Ontology Manager에서 객체, 속성, 관계, 액션을 설계한다.
4. Object Explorer, Contour, Map, Vertex 등으로 데이터를 탐색한다.
5. AIP Logic, AIP Analyst, AIP Chatbot Studio, AIP Evals로 AI 분석/분류/평가를 얹는다.
6. Workshop으로 지도, 알림함, 지표판, 객체 상세 화면 같은 운영 앱을 만든다.

## Home / Narrative

Route: `/workspace/narrative/`

첫 화면은 개인 홈과 추천 앱 포털 역할을 합니다. 확인된 주요 진입점은 아래와 같습니다.

| Area | Observed items | D4D use |
| --- | --- | --- |
| Get started | Start speedrun, View training tracks, Install examples, Join Developer Community | 공식 튜토리얼과 예제 설치 시작점 |
| Recommended apps | Projects & files, Data Connection, Pipeline Builder, Contour, Ontology Manager, Workshop, AIP Logic, Code Repositories | 해커톤 작업의 핵심 앱 묶음 |
| AIP Assist | "How do I get my data into Foundry?", "How do I build my Ontology?", "How do I build an application?" | Foundry 사용법 질의 가능. 단, 민감한 워크스페이스/데이터 내용 입력 전 확인 필요 |

## Applications Menu Inventory

Home의 Apps 메뉴에서 확인한 앱 카테고리입니다. 나중에 "이 기능 어디서 하냐"를 찾을 때 이 표를 먼저 봅니다.

| Category | Apps observed | D4D relevance |
| --- | --- | --- |
| Administration | Control Panel, Resource Management, Upgrade Assistant | 권한/리소스/운영 설정. 해커톤에서는 보통 직접 변경하지 않음 |
| Analytics & Operations | AIP Analyst, Contour, Fusion, Insight, Map, Notepad, Quiver, Vertex | 분석, 지도, 그래프, 노트, 운영 화면 |
| Application development | Carbon workspaces, Custom Widgets, Examples, Machinery, Slate, Solution Designer, Workshop | 데모 앱, 커스텀 UI, 예제 앱 |
| Data integration | Artifacts, Build Schedules, Builds, Code Repositories, Code Workspaces, Compute Modules, Data Connection, Data Health, Data Lineage, HyperAuto, Jupyter, Pipeline Builder, RStudio, Time Series Catalog, VS Code | 데이터 수집, 변환, 코드 작업, lineage |
| Developer toolchain | DevOps, Developer Console, Global Branching, Marketplace | 개발/배포/패키지 관리 |
| Models | AIP Chatbot Studio, AIP Document Intelligence, AIP Evals, AIP Logic, Model Catalog, Model Studio, Modeling Objectives | LLM/모델/평가/문서 AI |
| Ontology | Automate, Foundry Rules, Object Explorer, Ontology Manager, Value Types, Workflow Lineage | 객체 모델, 규칙, 자동화, 탐색 |
| Security & governance | Approvals, Checkpoints, Cipher, Projects & files, Sensitive Data Scanner | 보안, 승인, 민감정보 스캔, 파일 관리 |
| Support | AI FDE, Issues, Linter, Training, Walkthroughs | 학습과 문제 해결 |

## Core App Notes

### Projects & Files / Compass

Route: `/workspace/compass/home`

역할: Foundry 안의 프로젝트, 폴더, 파일, 데이터셋, 앱 산출물을 찾고 관리하는 파일 시스템/카탈로그입니다.

확인한 화면 요소:

- Tabs: All files, Your project, Shared with you, Data Catalog, Trash
- Search: 전체 포트폴리오, 프로젝트, 폴더, 파일 검색
- Filters: Types, Status, Portfolios, Projects, Tags, Organizations, Sort
- New menu: New project, New portfolio
- D4D 해커톤 조직과 개인 프로젝트, `AIP Now Ontology` marketplace installation, 예제 폴더/파이프라인/문서가 보임

D4D에서의 사용:

- 새 산출물의 위치를 찾거나, 예제 리소스를 열거나, 데이터셋/파이프라인/앱 산출물을 탐색할 때 출발점
- 새 프로젝트나 포트폴리오 생성은 가능하지만, 실제 생성 전 사용자 확인 필요

### Data Connection

Route: `/workspace/data-ingestion-app/splash`

역할: 외부 시스템 연결, 정적 파일 업로드, 직접 데이터 입력/생성의 시작점입니다.

확인한 화면 요소:

- Tabs: Data Connection, Sources, Syncs, Agents, Listeners, External stacks
- Button: New source
- Setup actions:
  - Connect to external system
  - Upload static data
  - Input or generate data

D4D에서의 사용:

- 공개 API, 데이터베이스, 클라우드 스토리지, CSV/JSON 파일 같은 input을 Foundry에 넣을 때 우선 확인
- 해커톤에서는 원본 raw data 재배포 금지 원칙이 있으므로, 업로드 전 데이터 민감도와 샘플 범위를 확인해야 함

### Pipeline Builder

Route: `/workspace/builder`

역할: 코드 없이 또는 적은 코드로 데이터 정제/조인/변환/LLM 처리 pipeline을 만드는 앱입니다.

확인한 화면 요소:

- Button: New pipeline
- Search pipelines
- 예제 pipeline:
  - GeoJSON Extraction Pipeline
  - Metrics and Alerts Pipeline
  - Time Series Sync | Event Pipeline
  - Time Series Sync | Sensor Pipeline
  - Ontology Preparation Pipeline
- 추천 학습 예제:
  - No-code data cleaning
  - Parse different data formats
  - Transform geospatial data
  - Parse PDFs with LLMs
  - Use LLMs to classify data

D4D에서의 사용:

- AIS, 기상, 위성 메타데이터, 조달, OSINT 문서, 제재 리스트 등을 공통 schema로 정리
- 해상/드론/센서 과제에서는 time series 또는 GeoJSON 변환 pipeline이 특히 중요

### Ontology Manager

Route: `/workspace/ontology/home/discover`

역할: 데이터셋을 실제 작전/분석 객체와 관계로 바꾸는 핵심 모델링 앱입니다.

확인한 리소스:

- Object types: 11
- Link types: 13
- Action types: 6
- Functions: 315
- Shared properties, Groups, Interfaces, Value types, Health issues, Cleanup, Ontology configuration

New menu에서 확인한 생성 가능 항목:

| Item | Meaning | D4D example |
| --- | --- | --- |
| Object type | 데이터셋/모델을 작전 객체로 매핑 | Vessel, Port, ThreatActor, Incident, Sensor |
| Link type | 객체 간 관계 생성 | Vessel visited Port, Actor used Domain |
| Action type | 사용자가 ontology에 writeback하는 통제된 액션 | Mark alert reviewed, Assign investigation |
| Shared property | 여러 객체가 공유하는 공통 속성 | confidence, source_url, last_seen |
| Group | ontology taxonomy | Maritime, Cyber, Logistics |
| Interface | 추상 타입 기반 개발 | TrackableAsset, AlertableEntity |
| Function | 코드로 객체 수정/계산 정의 | risk score, anomaly reason |
| Value type | 속성값 제약 | latitude/longitude, severity enum |
| Ontology as Code repository | 코드로 ontology entity 생성 | 반복 가능한 모델 관리 |

D4D에서의 사용:

- "어떤 객체와 관계를 만들어야 하나"가 결정되면 가장 먼저 여기를 봄
- Palantir 데모의 차별점은 단순 dashboard보다 ontology 기반의 object/action/workflow를 보여주는 데 있음

### Object Explorer / Hubble

Route: `/workspace/hubble`

역할: Ontology 객체를 검색하고 탐색하는 앱입니다.

확인한 샘플 ontology: `AIP Now Ontology`

| Object type | Count | Notes | D4D analogy |
| --- | ---: | --- | --- |
| [Example] Carrier | 14 | 항공사와 fleet metrics | Fleet owner, organization |
| [Example] Airport | 178 | 공항 geospatial properties | Port, base, facility |
| [Example] Route Alert | 14 | 운영 alert, status, assignment | Maritime/cyber/threat alert |
| [Example] Flight | 1.7M | 2023년 미국 commercial passenger flights | AIS event, sortie, movement event |
| [Example] Flight Sensor | 594 | Flight-linked sensor readings and time series | Vessel/drone/sensor telemetry |
| [Example] Route | 1.3K | 출발/도착 기반 derived route | Voyage, patrol route, supply route |
| [Example] Runway | 471 | 공항 내 활주로 | Pier, berth, runway, facility segment |
| [Example][Log] Update Route Alert Status | 0 | Action logging object | Action audit log |
| [Example] Route Alert Comment | 0 | Alert comment object | Analyst note/comment |
| [Example] Explainer | 24 | Workshop 설명용 callout | Demo annotation/help object |
| [Example] Aircraft | 5.5K | Aircraft properties | Vessel, drone, vehicle |

D4D에서의 사용:

- 해커톤 샘플 모델을 빠르게 이해하는 reference ontology
- 해상 과제라면 `Flight -> AIS event`, `Airport -> Port`, `Route -> Voyage`, `Route Alert -> Threat Alert`, `Flight Sensor -> Sensor Reading`으로 치환 가능

### Workshop

Route: `/workspace/module/splash`

역할: 운영자가 실제로 보는 앱 화면을 point-and-click 방식으로 만드는 앱입니다.

확인한 생성 옵션:

- New module
- Blank module
- Inbox template
- Map template
- Metrics template

확인한 reference examples:

- Vega charts in Workshop
- Common Operating Picture with geospatial data
- Data-rich custom object view
- Bulk edit Object Sets with Loop layout

D4D에서의 사용:

- Common Operating Picture: 지도 기반 상황판
- Inbox: 경보/검토 큐
- Metrics: 위험도, 변화량, coverage, confidence dashboard
- Object view: 선박/위협행위자/사건 상세 페이지

### AIP Logic

Route: `/workspace/logic-app`

역할: Ontology 위에서 no-code/low-code AI function을 만들어 분류, 추출, 편집, 보고서 생성을 수행하는 앱입니다.

확인한 화면 요소:

- Button: New logic / Create new logic function
- 설명: no-code Ontology functions, model/tool usage, Actions 또는 Automations와 연동
- 관련 reference examples:
  - Cross-validate Images and Documents using AIP
  - Build feedback loops in AIP Logic
  - Use AIP Logic to classify and edit objects

D4D에서의 사용:

- OSINT 문서에서 entity extraction
- AIS/센서 이상 탐지 결과에 reason code 부여
- Alert severity/risk score 계산
- analyst brief 초안 생성
- human-in-the-loop action과 연결

### Code Repositories

Route: `/workspace/code`

역할: 코드 기반 transform, app, logic, package를 관리하는 개발 앱입니다.

확인한 화면 요소:

- Button: New repository
- Pull requests section
- 안내: Python transforms in Code Repositories는 legacy로 안내되며 VS Code workspaces가 권장됨

D4D에서의 사용:

- 복잡한 Python/SQL/TypeScript 작업이나 OSDK/custom frontend가 필요할 때
- 단순 데이터 정제는 Pipeline Builder나 Code Workspaces/VS Code 흐름을 먼저 검토

### Contour

Route: `/workspace/contour-app/splash`

역할: 대규모 데이터셋을 필터, 조인, 시각화로 분석하고 결과를 pipeline에 다시 기여하는 분석 앱입니다.

D4D에서의 사용:

- 빠른 데이터 탐색
- 후보 컬럼/분포/이상값 확인
- 발표용 정적 분석 결과보다는 pipeline/ontology로 넘길 전처리 탐색에 적합

### Training

Route: `/workspace/training`

역할: Foundry 내 학습 트랙 모음입니다.

확인한 트랙:

- Application Developer
- Frontend & OSDK Developer
- Data Analyst
- Data Engineer
- AI Engineer
- Data Scientist

우선순위 높은 트랙:

| Track | Why |
| --- | --- |
| Data Engineer | Data Connection, Pipeline Builder, geospatial transform, PDF/LLM parsing, S3/Postgres 연결 |
| AI Engineer | AIP workflow, Agent Studio, LLM classification, PDF parsing, semantic search, AIP Logic, feedback loop |
| Application Developer | Workshop, common operating picture, operational app demo |
| Frontend & OSDK Developer | 커스텀 앱이 필요할 때만 후순위 |

## Request-To-App Routing

나중에 사용자가 아래처럼 요청하면 이 매핑을 기준으로 작업을 시작합니다.

| User request pattern | First app to inspect | Likely build path |
| --- | --- | --- |
| "데이터 업로드해줘" | Data Connection | Upload static data 또는 New source |
| "CSV/JSON 정리해줘" | Pipeline Builder | New pipeline, schema normalize, output dataset |
| "PDF/문서에서 정보 추출해줘" | Pipeline Builder, AIP Document Intelligence | LLM parsing, entity extraction, citation columns |
| "객체 모델 만들어줘" | Ontology Manager | Object type, link type, shared property |
| "선박/항구/위협 관계를 보여줘" | Object Explorer, Vertex, Workshop | Ontology 탐색 후 graph/map view |
| "지도 기반 상황판 만들어줘" | Workshop | Map template, object set, filters, object details |
| "알림/큐/검토 화면 만들어줘" | Workshop, Ontology Manager | Inbox template, Alert object, Action type |
| "위험도 점수 만들어줘" | AIP Logic, Pipeline Builder | Function 또는 pipeline transform |
| "분석관용 브리프 만들어줘" | AIP Logic, AIP Analyst, Workshop | evidence retrieval, summary, action/report |
| "챗봇/코파일럿 만들어줘" | AIP Chatbot Studio, AIP Logic | ontology-grounded chatbot or embedded assistant |
| "모델 결과 평가해줘" | AIP Evals | test set, expected answers, eval metrics |
| "코드로 자동화해줘" | Code Workspaces, VS Code, Code Repositories | Python/SQL/TS transform or OSDK integration |

## D4D Demo Blueprints

### Maritime Domain Awareness

1. Data Connection: AIS sample, port list, weather, sanctions list, incident/news feed.
2. Pipeline Builder: normalize vessel IDs, geocode ports, join weather and route events.
3. Ontology Manager: `Vessel`, `Port`, `Voyage`, `AISPosition`, `WeatherCell`, `Alert`, `Source`.
4. AIP Logic: anomaly reason, confidence, recommended next check.
5. Workshop: map template + alert inbox + vessel detail page.

### OSINT / Defense Intelligence

1. Data Connection: public reports, sanctions, procurement, breach/exposure sample, domain/IP intelligence.
2. Pipeline Builder: entity extraction and source normalization.
3. Ontology Manager: `ThreatActor`, `Alias`, `Domain`, `Organization`, `Incident`, `CredentialExposure`, `Source`.
4. AIP Logic: risk summary, source-cited brief, false-positive checks.
5. Workshop: investigation inbox + graph/object detail + report generation action.

### C2 / Sustainment

1. Data Connection: asset inventory, mission locations, route/weather/disruption sources.
2. Pipeline Builder: join by route/time/location.
3. Ontology Manager: `Asset`, `Unit`, `Mission`, `Route`, `SupplyItem`, `Disruption`, `Decision`.
4. AIP Logic: impact score and mitigation recommendation.
5. Workshop: common operating picture + decision log.

## Next Exploration Targets

아직 실제 생성/저장 없이 메뉴만 확인한 상태입니다. 사용자 확인 후 다음 순서로 deeper walkthrough를 진행하면 좋습니다.

1. Pipeline Builder에서 샘플 pipeline 하나를 열어 node 종류, input/output, publish 흐름 확인
2. Ontology Manager에서 예제 object type 하나를 열어 property/link/action mapping 화면 확인
3. Workshop의 Map 또는 Inbox template을 열어 화면 구성 요소 확인
4. AIP Analyst/AIP Chatbot Studio/AIP Evals 접근 가능 여부 확인
5. Map, Vertex, Quiver 앱에서 geospatial/graph/analytics 표현 방식 확인


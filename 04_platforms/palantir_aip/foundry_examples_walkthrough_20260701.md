# Palantir Foundry Example Execution Walkthrough

Date: 2026-07-01  
Workspace: D4D hackathon Foundry tenant  
Mode: read-only walkthrough of installed examples and runnable applications

## Summary

실제 동작 예제를 확인하는 방향은 맞습니다. Foundry는 문서만 읽으면 개념이 추상적으로 남기 쉽고, 해커톤에서는 "어떤 input을 넣으면 어떤 pipeline/ontology/app output이 나오는가"가 더 중요합니다.

이번 walkthrough에서는 `Build with AIP` 포털, 이미 설치된 `AIP Now Ontology` Marketplace installation, Workshop apps, object views, Pipeline Builder 예제를 확인했습니다.

## Safety Scope

- 새 예제 설치, 데이터 업로드, deploy, propose, send, comment 작성, status 변경은 수행하지 않았습니다.
- 이미 설치된 Marketplace installation 안의 앱/파이프라인/데이터셋을 read-only로 열고 안전한 UI toggle/filter만 눌렀습니다.
- `Send`, `Deploy`, `Propose`, `Install`처럼 side effect가 가능한 버튼은 누르지 않았습니다.

## Build With AIP Portal

Route: `/workspace/now/platform`

확인 결과:

- 포털은 처음 로딩 직후 `Awesome AIP Workflow` placeholder 카드가 보일 수 있습니다.
- 약 3-5초 뒤 실제 예제 카드가 로딩됩니다.
- 총 90개 안팎의 예제 링크가 확인되었습니다.
- 개별 상세 페이지 일부는 `Lorem ipsum` placeholder 본문으로 렌더링되고, `Install` 버튼이 보이지 않았습니다.
- 따라서 현재 tenant에서는 새 예제 install flow가 완전히 노출되지 않았거나, 상세 페이지/설치 기능이 제한되어 있을 가능성이 있습니다.

확인된 주요 카테고리:

- Featured
- Nvidia Blueprints
- AI Starter Pack
- Document Suite
- Reference Implementation
- Writeback & Decision Automation
- Media & Image Workflows
- Application Building
- External Integrations
- Data Engineering
- Analytics and Visualizations

해커톤 관련성이 높은 예제:

| Example | D4D relevance |
| --- | --- |
| Build a common operating picture with geospatial data | 지도 기반 COP, maritime/domain awareness |
| End-to-end alerting workflow | alert 생성, triage, action flow |
| Use AIP Logic to classify and edit objects | 분류, object update, human-in-the-loop |
| Build with AIP Chatbot Studio | analyst/copilot demo |
| Semantic Search with Palantir-Provided Models | RAG/search over reports and evidence |
| Parse PDFs with LLMs in Pipeline Builder | OSINT reports, manuals, procurement docs |
| Transform geospatial data in Pipeline Builder | AIS, ports, weather, facilities, routes |
| Create a dynamic inbox application for task triaging in Workshop | alert queue / task triage |
| Graphically explore relationships in your Ontology with a Vertex Graph | threat graph, vessel/entity network |
| Visualize time series data within a geospatial map | sensor/time series + map |

## Installed Example Package

Installed product: `AIP Now Ontology`  
Location: Compass / Projects & files  
Status: Marketplace installation, locked for safe upgrades

The installed package contains actual runnable resources:

- Reference Foundation Landing Page
- Applications
- Object Views
- Composable Modules
- Data sources and ontology output folders
- Pipeline Builder examples
- Notepad documentation
- Dataset previews

This package is currently more useful than the `Build with AIP` install portal because it already has runnable apps and pipelines.

## Runnable Workshop Apps

### Reference Foundation Landing Page

Type: Workshop module  
Status: opened successfully

What it shows:

- Foundation data overview
- Links to datasets and ontology equivalents
- Data shapes: semantic objects, high-scale events, operations tickets, time series, geospatial, media sets, long text
- Example datasets:
  - Aircraft
  - Airports
  - Carriers
  - Routes
  - Flights
  - Route Alerts
  - Sensor readings
  - Sensors
  - Events
  - Runways

D4D use:

- This is the "starter ontology + reference data index" pattern.
- For our own demo, create a similar landing page for `D4D OSINT / Maritime Reference Foundation`.

### Basic Inbox | Route Alert Inbox

Type: Workshop application  
Status: opened successfully; filter interaction tested

Observed UI:

- Title: `Routes Alert Inbox`
- Intro: routes with one or more open alerts related to recent performance
- Tabs/filters: `All Alerts`, `Assigned to Me`, `Filter`
- Route alert list:
  - route title
  - alert title
  - priority
  - additional alert count
- Embedded object view:
  - route properties
  - average delays
  - flight count
  - linked departure/destination airports
  - linked flights
  - linked route alert

Interaction tested:

- Clicking `Filter` changed the screen from placeholder rows to actual alert rows and embedded object details.
- No writeback action was performed.

D4D use:

- Direct template for a threat/incident/OSINT alert inbox.
- Replace `Route` with `Vessel`, `Port`, `Organization`, `ThreatActor`, or `Asset`.
- Replace `Route Alert` with `Maritime Anomaly`, `Credential Exposure`, `Supply Disruption`, or `Drone Detection Alert`.

## Runnable Object Views

### Basic Metric Cards | Route Overview

Type: Workshop object view  
Status: opened successfully

Observed UI:

- Object selector for a route
- Warning for incomplete data history
- Conditional metric cards:
  - Distance
  - Flight Time
  - Delays
  - Carriers
- Map component
- Weekly flight volume chart

D4D use:

- Vessel/route/asset health summary page.
- Useful for "show me the current operational picture for this route/asset" demos.

### Linked Filters with Map and Charts | Flights Map

Type: Workshop object view / map analytics app  
Status: opened successfully

Observed UI:

- Global filter that responds to map selection and chart interaction
- Route flight volume chart
- Map/Table switch
- Map layers:
  - Routes by Flight Volume
  - Runways by Length
- Layer visibility guidance

D4D use:

- Common operating picture pattern.
- Good basis for AIS route volume, port congestion, anomaly heatmap, sensor coverage, or weather overlay demos.

### Map and Gantt Charts | Aircraft

Type: Workshop object view  
Status: opened successfully

Observed UI:

- Aircraft selector
- Asset properties:
  - tail number
  - carrier
  - manufactured year
  - seats
  - cargo
  - daily flights
- Flight Review / Flight History sections
- Gantt-style event timeline
- Selectable flight events

D4D use:

- Asset schedule/timeline view.
- Can map to drone sorties, patrol routes, vessel voyage history, maintenance windows, or logistics movement.

### Ticket with Comments | Route Alert

Type: Workshop object view  
Status: opened successfully; no comment submitted

Observed UI:

- Alert selector
- Alert explanation:
  - route
  - metric change
  - risk score
  - cancellation rate
  - similar alerts
- Object comments section:
  - search comments/actions
  - refresh
  - comment input
  - `Send` button disabled until input

D4D use:

- Analyst review / decision-support page.
- Good pattern for human-in-the-loop adjudication: summarize evidence, show risk, compare similar alerts, allow comments/status actions.

## Pipeline Builder Examples

### Metrics and Alerts Pipeline

Status: opened successfully in read-only mode

Observed:

- Pipeline Builder displays: `Viewing pipeline in read-only mode due to user permissions`
- Outputs:
  - `Route Alert Comment`: 7/7 columns mapped
  - `Route Alerts`: 23/23 columns mapped
- Major pipeline groups/nodes:
  - Prepare Flight Data
  - Calculate Metrics For Periods
  - Calculate Change and Apply Thresholds
  - Prepare Display Values
- Uses ontology outputs under Tickets and Alerts.

D4D use:

- Core pattern for creating alert objects from data.
- For maritime: calculate anomaly metrics from AIS/weather/port events, then create `MaritimeAlert`.
- For OSINT: calculate exposure/risk metrics from source evidence, then create `ThreatAlert`.

### GeoJSON Extraction Pipeline

Status: opened successfully in read-only mode

Observed:

- Inputs include airports and raw GeoJSON/runway data.
- Major pipeline steps:
  - Parse GeoJSON
  - Clean Columns
  - Join Airports
  - Ontology Columns
- Outputs:
  - `Runway <> Airport Mapping`: 2/2 columns mapped
  - `Runways`: 6/6 columns mapped

D4D use:

- Pattern for geospatial asset/facility ingestion.
- For maritime: parse port boundaries, maritime zones, shipping lanes, AOIs, sensor footprints.

### Time Series Sync | Sensor Pipeline

Status: opened successfully in read-only mode

Observed:

- Inputs include sensor readings and unit mappings.
- Major pipeline steps:
  - Join Series Units
  - Augment sensor object data
  - Create Sensor Objects
  - Timeseries Columns
- Outputs:
  - `[Example] Sensors`: 6/6 columns mapped
  - `[Example] Time Series Sync | Sensor Readings`: required columns mapped

D4D use:

- Pattern for sensor fusion or telemetry.
- For drone/maritime: sensor object + readings model.

### Time Series Sync | Event Pipeline

Status: opened successfully in read-only mode

Observed:

- Inputs include flights and several time series properties.
- Major pipeline steps:
  - Union
  - Join Arrival and Departure
  - Generate backing dataset
- Output:
  - `[Example] Time Series Sync | Events`

D4D use:

- Pattern for event timelines tied to operational objects.
- For D4D: AIS pings, drone detections, incident timestamps, communications events, maintenance events.

## Practical Build Pattern For D4D

Based on the runnable examples, a strong Palantir demo should look like this:

1. Start with a reference foundation page that explains datasets and object model.
2. Use Pipeline Builder to transform raw/source data into ontology objects.
3. Create alerts using metrics, threshold changes, or AIP classification.
4. Present alerts in a Workshop inbox.
5. Let the analyst inspect object context, linked evidence, map, timeline, and similar alerts.
6. Add a ticket/comment/status action only when safe and needed.

## Installation Guidance

New example installation should be handled carefully:

- Installing examples likely creates projects, folders, datasets, pipelines, ontology objects, and Workshop modules.
- These resources may be locked by Marketplace for safe upgrades.
- Install should be done only after confirming:
  - exact example name
  - destination project/space
  - whether it will create or overwrite resources
  - whether it will add sample data

Current status:

- No new example was installed in this walkthrough.
- Existing `AIP Now Ontology` installation is sufficient for many D4D demo patterns.
- The Build with AIP individual detail pages did not expose a reliable install button during this pass.

## Recommended Next Runs

1. Open `Basic Inbox | Route Alert Inbox` and trace from selected alert to source pipeline and ontology action type.
2. Open `Ticket with Comments | Route Alert` and inspect available action/writeback controls without submitting.
3. Open `Flights Map` and test layer toggles/map-table switch.
4. Open `Metrics and Alerts Pipeline` and select individual nodes to preview schemas.
5. Inspect Ontology Manager for `Route Alert`, `Route Alert Comment`, and associated Action Types.
6. If the user approves workspace changes, try installing one small Build with AIP example and record the install wizard.


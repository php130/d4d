# Topic Selection Recommendation

Date: 2026-07-03

## Recommendation

Pick **T4-002. OSINT 기반 해상 회색지대 사전 징후 조기탐지 / Gray-zone Early Warning** as the primary topic.

Use **T4-001. 비정형 데이터 기반 해상 불법·위장 선박 자동 탐지** as a supporting module if the team needs a more concrete detection demo.

Working title:

> Maritime Gray-zone Early Warning Copilot

Korean title:

> 해상 회색지대 조기경보 코파일럿

## Why This Topic

| Criterion | Assessment |
| --- | --- |
| Problem fit | APAC/Korea security context is clear. Maritime gray-zone activity, illegal vessels, AIS-off behavior, port/logistics signals are plausible defense/security concerns. |
| Data availability | More workable than many tracks. AIS samples, MarineTraffic, Global Fishing Watch, NOAA AIS, KMA/KHOA weather/ocean data, GDELT/news, OpenStreetMap, satellite references can be combined. |
| Demo clarity | Map + timeline + risk score + evidence citations is easy for judges to understand in 3 minutes. |
| Technical execution | Can be implemented as a data fusion and intelligence workflow without hardware. Synthetic samples can fill data gaps. |
| Military deployability | Maritime Domain Awareness is a known operational need. Output can be framed as analyst triage, not autonomous action. |
| Safety/compliance | Uses public or synthetic data. Avoids sensitive credential/dark web handling unless explicitly available and allowed. |
| Platform fit | Can map cleanly to Palantir-style ontology: vessel, port, event, source, indicator, risk assessment. Also fits OSINT tools if available. |

## Core Product Hypothesis

Analysts do not need another raw AIS map. They need a system that connects weak public signals and explains why a maritime area deserves attention.

The product should answer:

> "In this area and time window, what early signals suggest abnormal maritime activity, and what evidence supports that assessment?"

## Minimal Demo

### Input

- Area of interest: sea area, port, or bounding box
- Time window
- Optional keywords: militia, illegal fishing, sanctions, port surge, vessel name, route

### Data

- AIS or vessel movement sample
- Weather/ocean data
- News/OSINT event feed
- Port/geospatial context
- Optional satellite/SAR reference layer or synthetic dark-vessel event

### Processing

- Detect AIS gaps, loitering, route deviation, rendezvous-like proximity, port concentration, suspicious timing
- Join with weather/ocean conditions
- Join with news or event signals
- Score risk as investigation priority, not guilt
- Preserve citation/provenance for every claim

### Output

- Map view
- Timeline
- Top suspicious events
- Evidence table with source links
- 1-page intelligence brief
- Recommended analyst follow-up

## Demo Story

1. User selects an APAC maritime area.
2. System loads public/synthetic vessel activity and OSINT events.
3. It detects weak indicators: AIS gap, abnormal loitering, route deviation, port-related signal, news/event spike.
4. It produces a ranked list of investigation candidates with citations.
5. It generates a short operational brief.

## Why Not Other Topics First

### T2-003 Supply-chain Credential Exposure

Strong topic if StealthMole access is available. Without platform/data access, it risks becoming either too generic or too sensitive. Keep as backup.

### T2-001 Fusion Intel Copilot

Too broad. It can become a generic chat UI unless the team anchors it to a concrete domain. T4 gives that concrete domain.

### T3 AIP Air & Space Ontology Builder

Good if Palantir AIP access is confirmed. Otherwise it may become a synthetic ontology demo with weaker operational pull.

### T1 Counter-UAS

Clear defense relevance, but good demos often need hardware, sensor data, or CV datasets. It is higher execution risk.

### T5 AI Wargame Tutor

Buildable, but judging risk is that it looks like a generic training chatbot unless domain content and simulation quality are strong.

## Preparation Priorities

1. Build a small vessel/event sample dataset.
2. Define the risk indicators and scoring rules.
3. Prepare a map + timeline UI mock or prototype.
4. Prepare a one-page generated intelligence brief format.
5. Keep all data public, synthetic, or safely anonymized.

## Backup Choice

If StealthMole access is strong and maritime data access is weak, switch to:

> T2-003. 방산 공급망 자격증명 노출 조기경보

The same architecture still applies:

- entities
- indicators
- source confidence
- risk scoring
- evidence-backed brief


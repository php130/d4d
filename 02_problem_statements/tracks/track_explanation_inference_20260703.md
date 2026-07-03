# Track Explanation Inference

Date: 2026-07-03

This document turns the Discord track explanations into concrete project implications.

## T1 | Autonomy, Unmanned Systems & Counter-UAS

### What This Track Is Really Asking

T1 is not just "build a drone demo." It is asking how unmanned systems survive and remain useful in contested environments:

- one operator controlling multiple systems
- degraded GPS and communications
- complex terrain
- electronic warfare
- detection and response against hostile drones
- human-machine teaming with clear intervention points

### Strong Project Shapes

1. **Counter-UAS Decision Support Simulator**
   - Inputs: synthetic drone tracks, RF/EO/IR/radar-like detections, city/no-fly-zone context
   - Output: threat classification, confidence, response recommendation, collateral damage warning
   - Strength: meaningful without needing real drones

2. **Terrain-aware UAV Route Planner**
   - Inputs: terrain map, communication quality assumptions, threat zones
   - Output: route that balances cover, communication, mission time, exposure
   - Strength: good APAC/Korea relevance because mountains, coasts, urban areas matter

3. **Multi-UxV Mission Allocation UI**
   - Inputs: 3-5 simulated assets, mission objectives, asset health
   - Output: task allocation, operator alerting, mission success metrics
   - Strength: directly matches Multi-UxV Control

### Risks

- Real hardware or sensor data can become a blocker.
- Pure CV drone detection can look like a generic object detection project.
- The demo must show operational decision support, not only model output.

### Implication For Us

High defense meaning, but higher execution risk. Use T1 only if the team has hardware/simulation capacity or strong sensor data.

## T2 | OSINT & Defense Intelligence

### What This Track Is Really Asking

T2 is about turning fragmented information into defensible intelligence. Collection alone is not enough. The expected output is probably:

- source-grounded answers
- relationship analysis
- knowledge graph
- entity resolution
- confidence and provenance
- early warning
- analyst workflow

### Strong Project Shapes

1. **Defense Supply-chain Exposure Watch**
   - Inputs: defense supplier domains, public procurement, sanctions, CTI/dark-web signals if available
   - Output: supplier risk ranking, exposure evidence, recommended action
   - Strength: very concrete if StealthMole access is available

2. **Threat Actor Knowledge Graph**
   - Inputs: aliases, emails, wallets, Telegram handles, reports
   - Output: resolved entities, relationship graph, confidence
   - Strength: good technical differentiation

3. **Fusion Intel Copilot**
   - Inputs: natural-language question, multiple OSINT modules
   - Output: cited answer, graph, timeline, uncertainty
   - Strength: broad platform fit

### Risks

- A generic LLM chat UI will be weak.
- Dark-web or credential data can create compliance risk.
- Without real platform/data access, T2-003 may become too hypothetical.

### Implication For Us

T2 is strong as a backup if StealthMole access is confirmed. It also provides the architecture pattern for our maritime project: graph + evidence + risk scoring + brief.

## T3 | Battle Network, C2, Maritime Domain Awareness & Sustainment

### What This Track Is Really Asking

T3 is about making commanders understand and act on fragmented data. It is less about one algorithm and more about the system that connects:

- sensors
- OSINT
- tactical data
- logistics
- C2 workflows
- natural-language querying
- low-bandwidth or denied-network constraints

### Strong Project Shapes

1. **Natural Language COP**
   - Inputs: synthetic tracks, AIS, weather, incidents, assets
   - Output: map, entity list, natural-language answers, commander brief
   - Strength: clear Palantir/AIP fit

2. **S-DOT Semantic Transmission Demo**
   - Inputs: high-volume sensor event stream
   - Output: compact semantic messages for low-bandwidth tactical network
   - Strength: technically differentiated

3. **APAC Sustainment C2**
   - Inputs: ports, weather, routes, stocks, disruption events
   - Output: alternate route, resupply risk, logistics priority
   - Strength: meaningful but requires careful scenario design

4. **MDA-to-C2 Bridge**
   - Inputs: maritime anomaly events
   - Output: COP layer, commander brief, recommended follow-up
   - Strength: bridges T3 and T4

### Risks

- T3 can become too broad.
- Without a concrete scenario, "COP" becomes just a dashboard.
- A C2 demo needs a decision workflow, not only visualization.

### Implication For Us

If we build maritime gray-zone early warning, we can frame it as T3 by emphasizing COP/C2:

> "A maritime anomaly intelligence layer that turns AIS/OSINT/weather signals into commander-ready COP updates."

## T4 | Maritime Domain Awareness

### What This Track Is Really Asking

T4 is asking for maritime intelligence, not just vessel tracking. The hard part is recognizing weak indicators:

- AIS-off or suspicious AIS gaps
- dark vessel behavior
- rendezvous or ship-to-ship patterns
- port/logistics anomalies
- maritime militia or illegal fishing signals
- satellite/SAR/OSINT correlation
- uncertainty-aware threat prioritization

### Strong Project Shapes

1. **AIS + OSINT Gray-zone Early Warning**
   - Inputs: AIS sample, news/events, port/geospatial context, weather/ocean
   - Output: ranked warning candidates, evidence, timeline, brief
   - Strength: best balance of meaning and feasibility

2. **Dark Vessel Detection Workbench**
   - Inputs: AIS gaps, Sentinel/SAR references, synthetic dark-vessel events
   - Output: suspected dark-vessel tracks and confidence
   - Strength: high MDA relevance

3. **Maritime Militia Activity Dashboard**
   - Inputs: vessel clusters, rendezvous events, OSINT reports
   - Output: cluster behavior, suspicious activity timeline
   - Strength: direct gray-zone relevance

4. **Port Logistics Anomaly Early Warning**
   - Inputs: port calls, vessel density, news, weather, logistics indicators
   - Output: port risk signals and explanation
   - Strength: useful if AIS data is limited

### Risks

- Real-time AIS may be paid or limited.
- SAR/EO data processing can be heavy.
- Need avoid claiming a vessel is hostile; frame as investigation priority.

### Implication For Us

This remains the best primary topic:

> Maritime Gray-zone Early Warning Copilot

Submit as T4 if the focus is MDA and anomaly detection.

## T5 | Force Readiness, Training & Simulation

### What This Track Is Really Asking

T5 is about improving human readiness under constraints:

- fewer people
- shorter service periods
- complex systems
- limited instructors
- need for repeated decision training
- after-action feedback
- offline/on-device use

### Strong Project Shapes

1. **LLM Tactical Instructor**
   - Inputs: doctrine snippets, scenario, trainee decision
   - Output: critique, next question, doctrine-grounded explanation

2. **MDMP Training Assistant**
   - Inputs: mission, enemy, terrain, troops, time, civilians
   - Output: planning prompts, COA comparison, risks

3. **AAR Generator**
   - Inputs: simulation logs or decisions
   - Output: after-action review, lessons, follow-up drills

4. **On-device Manual RAG**
   - Inputs: local manuals, procedures, offline model
   - Output: offline Q&A with citation

### Risks

- Easy to look like a generic chatbot.
- Needs good scenario design and evaluation metrics.
- Military doctrine content must stay public and non-sensitive.

### Implication For Us

Good fallback if data access collapses, but it needs strong instructional design to be compelling.

## Cross-track Synthesis

The strongest strategic pattern across all tracks is:

> Convert fragmented signals into decision-ready intelligence with provenance, confidence, and recommended next action.

This applies to:

- T2 intelligence copilot
- T3 COP/C2
- T4 maritime gray-zone warning
- T5 training/AAR

For our project, the best narrow expression is:

> **T4 Maritime Gray-zone Early Warning Copilot**

The best flexible pitch is:

> **A source-grounded MDA intelligence layer that detects weak maritime gray-zone signals and turns them into commander-ready COP updates.**


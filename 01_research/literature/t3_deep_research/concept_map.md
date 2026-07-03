# Concept Map: Resilient Maritime COP over Denied Networks

Last updated: 2026-07-03

## One-line Concept

Convert maritime and OSINT signals into compact semantic events, prioritize them under degraded communications, and update a commander-ready COP with evidence and uncertainty.

## Core Concepts

### Common Operational Picture (COP)

A shared operational view that helps multiple actors understand the same situation and coordinate decisions.

For the demo:

- map layer
- entity list
- event timeline
- risk priority
- evidence/citation table
- natural-language brief

Failure mode:

- A map with dots is not enough.
- A COP must support a decision: investigate, monitor, alert, reroute, request more data.

### Semantic Communication

Sending meaning or task-relevant information rather than raw data reconstruction.

For the demo:

- Do not send full AIS history, raw news, or imagery.
- Send event messages like:

```json
{
  "event_type": "AIS_GAP_NEAR_PORT",
  "entity": "VESSEL_042",
  "location": "bbox/grid",
  "time_window": "2026-07-03T12:00Z/2026-07-03T13:00Z",
  "priority": 0.82,
  "confidence": 0.71,
  "reason": "AIS gap occurred near prior loitering area under low visibility",
  "sources": ["AIS_SAMPLE", "KMA_WEATHER", "NEWS_EVENT"]
}
```

### Denied / Degraded Network

An operating condition where bandwidth, latency, reliability, or connectivity is impaired.

For the demo:

- bandwidth budget slider
- packet/event drop simulation
- priority queue
- delayed event delivery
- compare raw transmission vs semantic event transmission

### Sensor / OSINT Fusion

Combining structured and unstructured signals into a single event model.

Possible inputs:

- AIS track
- weather/ocean condition
- port/geospatial context
- news or GDELT-like event
- synthetic SAR/dark-vessel indicator
- analyst note

### Maritime Domain Awareness (MDA)

Understanding maritime activity relevant to safety, security, economy, and defense.

For the demo:

- AIS anomaly
- AIS-off gap
- loitering
- rendezvous-like proximity
- route deviation
- port concentration
- suspicious event/news correlation

### Provenance

The trace of where each claim came from and how it was transformed.

For the demo:

- every event has source IDs
- every brief sentence links to event/source rows
- generated recommendations are separated from observed facts

## System Chain

```text
Raw/source data
  -> entity extraction
  -> event detection
  -> semantic event encoding
  -> priority scoring
  -> degraded-network transmission simulation
  -> COP update
  -> source-grounded brief
```

## Key Design Principle

The product should not claim:

> "This vessel is hostile."

It should claim:

> "This event deserves analyst attention because these public/synthetic signals coincide."

## Suggested Event Types

| Event type | Meaning | Sources |
| --- | --- | --- |
| `AIS_GAP` | Vessel stopped transmitting AIS for an unusual period | AIS |
| `ROUTE_DEVIATION` | Vessel path deviates from expected corridor | AIS, route baseline |
| `LOITERING` | Low-speed repeated movement in area | AIS |
| `RENDEZVOUS_CANDIDATE` | Two or more vessels close in space/time | AIS |
| `PORT_ACTIVITY_SPIKE` | Vessel density or activity around a port changes | AIS, port data |
| `WEATHER_MASKING_CONDITION` | Low visibility or adverse weather may reduce observation | weather/ocean |
| `OSINT_EVENT_NEARBY` | News/social/open-source event near AOI | GDELT/news |
| `SYNTHETIC_DARK_VESSEL` | Simulated SAR-only detection without AIS match | synthetic/SAR sample |

## Evaluation Ideas

| Question | Possible metric |
| --- | --- |
| Does semantic transmission reduce data volume? | bytes/events sent under bandwidth budget |
| Does priority routing preserve important events? | high-priority event delivery rate |
| Does COP remain usable under degradation? | number of actionable events retained |
| Is the brief grounded? | percent of claims with source/event IDs |
| Is uncertainty visible? | confidence/provenance shown for each event |


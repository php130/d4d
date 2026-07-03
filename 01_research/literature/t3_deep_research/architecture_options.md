# Architecture Options

Last updated: 2026-07-03

## Recommended Architecture

### Option A: Semantic Event COP

This is the recommended hackathon architecture.

```text
AIS / OSINT / Weather / Synthetic SAR
  -> normalizers
  -> event detectors
  -> semantic event encoder
  -> priority scorer
  -> network degradation simulator
  -> COP map + timeline
  -> grounded brief generator
```

### Why This Is Best

- It fits T3 directly: C2, COP, sensor/OSINT fusion, semantic data transmission.
- It uses the user's telecom background without requiring RF expertise.
- It can be demonstrated with public/synthetic data.
- It can be pitched as T3, while using T4 maritime data as the domain.

### Minimal Components

| Component | Minimum behavior |
| --- | --- |
| Data loader | Load sample AIS/events/weather from JSON/CSV |
| Event detector | Produce 5-8 event types from sample data |
| Semantic encoder | Convert raw rows into compact event messages |
| Priority scorer | Score based on severity, confidence, freshness, operational relevance |
| Network simulator | Simulate bandwidth cap and event drops/delays |
| COP UI | Map/list/timeline/event detail |
| Brief generator | Produce evidence-grounded summary |

## Option B: Natural Language COP

Focus:

- natural-language query over COP entities and events
- "What changed in the last hour?"
- "Which events should I investigate first?"

Strength:

- strong Palantir/AIP story
- easy to show value

Risk:

- can look like a generic chatbot unless the event model is solid

Use if:

- the team has strong LLM/RAG implementation capacity
- AIP-like tooling is available

## Option C: S-DOT Compression Benchmark

Focus:

- compare raw transmission vs semantic event transmission
- show data-volume savings and retained operational value

Strength:

- technically distinct
- strongly aligned with `S-DOT`

Risk:

- can become too abstract if there is no visual COP/use case

Use if:

- judges respond well to communications/network framing
- team can make a clear metric demo

## Option D: Maritime C2 Decision Workflow

Focus:

- event -> commander decision -> follow-up task
- monitor, escalate, request satellite, notify patrol, reroute logistics

Strength:

- best military deployability story

Risk:

- needs careful phrasing to avoid overclaiming operational authority

Use if:

- domain mentors emphasize command workflow

## Proposed MVP

Build Option A with a small piece of Option B.

### MVP Flow

1. Select scenario: "APAC maritime gray-zone activity under degraded network."
2. Load synthetic/public sample data.
3. Generate events:
   - AIS gap
   - loitering
   - rendezvous candidate
   - weather masking condition
   - OSINT nearby event
4. Simulate bandwidth drop.
5. Show that raw updates are dropped, but semantic priority events still update the COP.
6. Generate a brief with citations.

### Pitch Sentence

> We are not building another vessel tracker. We are building a semantic event layer that keeps commander-relevant maritime intelligence alive when the network cannot carry raw data.


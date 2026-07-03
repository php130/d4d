# T3 Deep Research Plan

Last updated: 2026-07-03

## Research Theme

**Resilient Maritime COP over Denied Networks**  
**거부환경 해상 COP 의미 전송 시스템**

This project frames T3 through a communications/C2 lens and uses maritime data as the operating domain.

Core question:

> When bandwidth is constrained or links are degraded, can we send mission-relevant semantic events instead of raw sensor/data streams, then update a commander-ready Common Operational Picture with evidence and uncertainty?

## Track Fit

| D4D problem | Fit |
| --- | --- |
| `T3-001 Sensor Fusion & NL COP` | Main fit. Multi-source events become a natural-language-queryable COP. |
| `T3-005 Semantic Data On Tactical-network` | Main fit. Raw data is converted into compact semantic event messages. |
| `T4-001 Illegal & Disguised Vessels` | Data/domain module. AIS/SAR/OSINT signals become maritime anomaly events. |
| `T4-002 Gray-zone Early Warning` | Scenario module. Weak maritime signals are ranked as investigation priorities. |

## Research Pillars

1. **COP / C2 / Situational Awareness**
   - What a COP is supposed to do
   - How sensor/event data should support commander decisions
   - Why dashboards fail when they do not encode decision workflow

2. **Semantic Communication**
   - What it means to send "meaning" rather than raw bits
   - Task-oriented transmission
   - Communication-computation tradeoff
   - How to explain S-DOT without overclaiming military protocol implementation

3. **Tactical / Degraded Networks**
   - Bandwidth limits
   - intermittent links
   - edge processing
   - priority routing
   - resilient information flow

4. **Maritime Domain Awareness**
   - AIS anomaly detection
   - dark vessel detection
   - SAR/AIS fusion
   - maritime OSINT
   - port/logistics anomaly signals

5. **RAG / Provenance / Briefing**
   - Citation-grounded intelligence briefs
   - source provenance
   - hallucination and attribution risk
   - evidence tables

## Research Outputs

| Output | File |
| --- | --- |
| Raw and processed paper metadata | `03_data/processed/literature_t3/current/` |
| Search/snowball run log | `03_data/raw/literature_t3/20260703_221550/collection_run_log.json` |
| Curated reading queue | `01_research/literature/t3_deep_research/t3_first_reading_queue.md` |
| Concept map | `01_research/literature/t3_deep_research/concept_map.md` |
| Architecture options | `01_research/literature/t3_deep_research/architecture_options.md` |
| Dataset candidates | `01_research/literature/t3_deep_research/dataset_candidates.md` |
| Pitch evidence | `01_research/literature/t3_deep_research/pitch_evidence.md` |

## Collection Method

1. Query OpenAlex and arXiv across 7 focused topic groups.
2. Use OpenAlex `referenced_works` and `related_works` for shallow snowball discovery.
3. Store metadata only: title, abstract, year, DOI/URL, open access flag, citation count, topic mapping.
4. Score records using relevance terms such as semantic communication, COP, command and control, AIS, dark vessel, MDA, edge intelligence, provenance.
5. Manually curate a reading queue because automatic scores can over-rank generic AI/IoT papers.

## Current Collection Snapshot

- Version: `20260703_221550`
- Raw records: 464
- Deduped records: 418
- Seed records: 322
- Snowball fetches: 180
- Topics: 7
- Queries: 28

## Immediate Reading Order

1. Semantic communication fundamentals
2. COP/C2/situational awareness papers
3. Maritime AIS/SAR/MDA papers
4. Edge/prioritization papers
5. RAG/provenance papers

Reason:

The demo architecture depends first on a defensible concept: **raw data -> semantic event -> prioritized transmission -> COP update -> grounded brief**.

## Working Definition For Hackathon

Semantic transmission in this project means:

> Extracting a compact operational event from raw or high-volume data, attaching priority/confidence/provenance, and transmitting that event when raw data cannot be moved reliably.

This avoids overclaiming physical-layer communication research. It is implementable in 24 hours as an application-layer semantic event protocol.


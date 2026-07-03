# A survey on semantic communications: Technologies, solutions, applications and challenges

## Metadata

- Year: 2023
- URL: https://doi.org/10.1016/j.dcan.2023.05.010
- DOI: 10.1016/j.dcan.2023.05.010
- Read status: abstract_only

## One-line Takeaway

Semantic communications shifts scarce-link networking from transmitting raw bits to transmitting task-relevant meaning, which fits a denied-network maritime COP where ships exchange intent, tracks, alerts, and uncertainty instead of full sensor feeds.

## D4D Relevance

The paper provides a core conceptual basis for a T3 semantic COP: extract mission-relevant meaning at the edge, encode it compactly, and preserve receiver usefulness under low bandwidth, disruption, and contested wireless conditions. Its emphasis on robustness, adaptability, reliability, UAV communications, and remote-sensing fusion maps directly to maritime operations with intermittent SATCOM, RF denial, and heterogeneous sensors.

## Key Concepts

- semantic communications
- semantic extraction
- semantic encoding
- semantic segmentation
- meaning-oriented throughput
- robust and adaptive wireless networking
- remote sensing and sensor fusion

## Input Data

- source information in wireless networks
- UAV communication data
- remote-sensing imagery or derived features
- fused sensing products
- application-specific semantic content rather than raw payloads

## Methods Or Architecture

- survey of semantic communication architecture and characteristics
- semantic extraction before transmission
- semantic encoding to reduce payload while preserving meaning
- semantic segmentation for structured interpretation
- solution categories organized around efficiency, robustness, adaptability, and reliability
- application review across UAVs, remote sensing, transportation, and healthcare

## Outputs / Metrics

- meaningful information delivered to the receiver
- improved effective transmission throughput
- efficiency
- robustness
- adaptability
- reliability

## Prototype Hooks

- implement an edge semantic extractor that converts AIS, radar, EO/IR, and operator reports into compact COP facts
- transmit priority-ranked semantic deltas instead of raw sensor streams during degraded connectivity
- encode tracks, intent, confidence, provenance, and recommended actions as T3 messages
- use semantic segmentation concepts to separate vessel, route, anomaly, and threat-relevant content from imagery
- design receiver-side COP reconstruction around mission meaning, uncertainty, and freshness rather than packet completeness
- add link-aware adaptation so the same COP can degrade from imagery to objects to alerts as bandwidth collapses

## Pitch Evidence

- The survey frames semantic communication as a way to maximize useful information delivery in wireless networks, supporting the denied-network COP argument.
- Its listed technologies map cleanly to a prototype pipeline: extract meaning, encode meaning, transmit meaning, reconstruct COP state.
- The UAV and remote-sensing applications provide adjacent evidence for maritime ISR, unmanned platforms, and distributed sensor fusion.
- The paper explicitly highlights efficiency, robustness, adaptability, and reliability, which are the right evaluation themes for contested maritime communications.

## Limitations / Risks

- Only the abstract was available, so specific algorithms, datasets, and quantitative results were not verified.
- The paper is a broad survey, not a maritime COP implementation.
- Claims about throughput and usefulness need prototype-specific metrics before being used as performance evidence.
- Semantic systems can fail if sender and receiver models diverge or use inconsistent ontologies.
- Security, adversarial manipulation, provenance, and trust handling are not detailed in the provided excerpt.
- Operational acceptance may require explainable semantic compression so commanders understand what was omitted.

## Confidence

medium

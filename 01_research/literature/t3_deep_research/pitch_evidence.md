# Pitch Evidence

Last updated: 2026-07-03

This file captures evidence points for slides and speaking notes. Use paraphrases, not long quotes.

## Claim 1: Future C2 has too much heterogeneous data for raw dashboards.

Supporting literature:

- A6.2 - Multiplatform sensor fusion. Drawing a common tactical scenario  
  https://doi.org/10.5162/ettc2024/a6.2
- Data-Driven Distributed Common Operational Picture from Heterogeneous Platforms using Multi-Agent Reinforcement Learning  
  http://arxiv.org/abs/2411.05683v1
- Application of Augmented Reality, Mobile Devices, and Sensors for Combat Entity Quantitative Assessment Supporting Decisions and Situational Awareness Development  
  https://doi.org/10.3390/app9214577

How to use:

> Modern C2 has to fuse heterogeneous platforms and sensors into a shared picture. The problem is not only visualization; it is deciding which information deserves attention.

## Claim 2: Semantic communication provides a defensible frame for sending task-relevant meaning instead of raw data.

Supporting literature:

- What is Semantic Communication? A View on Conveying Meaning in the Era of Machine Intelligence  
  https://doi.org/10.23919/jcin.2021.9663101
- A Survey on Semantic Communications for Intelligent Wireless Networks  
  https://doi.org/10.1007/s11277-022-10111-7
- Semantic Communication Meets Edge Intelligence  
  https://doi.org/10.1109/mwc.004.2200050
- Deep Learning Enabled Semantic Communication Systems  
  https://doi.org/10.1109/tsp.2021.3071210

How to use:

> Under bandwidth constraints, operational value comes from transmitting what a receiver needs to decide, not necessarily reconstructing every raw observation.

## Claim 3: Maritime awareness is a strong test domain because AIS alone is incomplete.

Supporting literature:

- Anomaly Detection in Maritime AIS Tracks: A Review of Recent Approaches  
  https://doi.org/10.3390/jmse10010112
- Classification-Aided SAR and AIS Data Fusion for Space-Based Maritime Surveillance  
  https://doi.org/10.3390/rs13010104
- Revealing Dark Vessels in the Mauritius Exclusive Economic Zone Using Multi-Temporal SAR and AIS Data  
  http://dx.doi.org/10.1109/igarss52108.2023.10282208
- AI in Maritime Security: Applications, Challenges, Future Directions, and Key Data Sources  
  https://doi.org/10.3390/info16080658

How to use:

> AIS gaps, dark vessels, and multi-source maritime surveillance make MDA a natural domain for semantic event fusion.

## Claim 4: Grounded intelligence needs provenance, not just fluent LLM text.

Supporting literature:

- Provenance-Aware Knowledge Representation: A Survey of Data Models and Contextualized Knowledge Graphs  
  https://doi.org/10.1007/s41019-020-00118-0
- A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges  
  https://doi.org/10.3390/bdcc9120320
- Correctness is not Faithfulness in Retrieval Augmented Generation Attributions  
  https://doi.org/10.1145/3731120.3744592

How to use:

> A commander brief should separate observed facts, inferred events, uncertainty, and recommendations. Every generated claim should trace back to an event and source.

## Suggested Pitch Framing

Problem:

> In a degraded network, raw AIS, sensor, weather, and OSINT feeds cannot all reach the COP. The commander still needs the right events, at the right time, with evidence.

Solution:

> We convert raw feeds into semantic maritime events, prioritize them by operational relevance, transmit them under bandwidth constraints, and update a source-grounded COP.

Demo:

> In our scenario, raw updates are dropped as bandwidth degrades, but high-priority semantic events still reach the COP and produce an evidence-backed brief.


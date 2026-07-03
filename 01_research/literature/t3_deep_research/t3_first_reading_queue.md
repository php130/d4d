# T3 First Reading Queue

Last updated: 2026-07-03

This queue is curated from the 418-record T3 deep research catalog. It prioritizes papers that help design a hackathon demo, not only papers with high citation counts.

## Priority A: Read First

### 1. What is Semantic Communication? A View on Conveying Meaning in the Era of Machine Intelligence

- Year: 2021
- URL: https://doi.org/10.23919/jcin.2021.9663101
- Use: Explains the shift from bit-level transmission to meaning/task-oriented communication.
- D4D extraction: Use this to justify why raw AIS/sensor/video streams can be replaced by compact operational events in constrained networks.

### 2. A Survey on Semantic Communications for Intelligent Wireless Networks

- Year: 2022
- URL: https://doi.org/10.1007/s11277-022-10111-7
- Use: Survey of semantic communication techniques, applications, and challenges.
- D4D extraction: Pull vocabulary for "semantic encoder", "task", "meaning", "receiver utility", and performance evaluation.

### 3. Semantic Communication Meets Edge Intelligence

- Year: 2022
- URL: https://doi.org/10.1109/mwc.004.2200050
- Use: Connects semantic communication with edge intelligence.
- D4D extraction: Supports the claim that event extraction can happen near sensors or data sources before transmission.

### 4. A6.2 - Multiplatform sensor fusion. Drawing a common tactical scenario.

- Year: 2024
- URL: https://doi.org/10.5162/ettc2024/a6.2
- Use: Directly discusses heterogeneous platforms and a common tactical scenario.
- D4D extraction: Use for COP framing and the need to fuse heterogeneous platforms into shared tactical awareness.

### 5. Data-Driven Distributed Common Operational Picture from Heterogeneous Platforms using Multi-Agent Reinforcement Learning

- Year: 2024
- URL: http://arxiv.org/abs/2411.05683v1
- Use: Military-relevant distributed COP framing from heterogeneous platforms.
- D4D extraction: Useful for explaining distributed COP, information overload, and uncertainty in command-and-control.

### 6. Anomaly Detection in Maritime AIS Tracks: A Review of Recent Approaches

- Year: 2022
- URL: https://doi.org/10.3390/jmse10010112
- Use: Core AIS anomaly review.
- D4D extraction: Turn AIS anomalies into semantic event types: gap, loitering, deviation, rendezvous, speed/course anomaly.

### 7. Classification-Aided SAR and AIS Data Fusion for Space-Based Maritime Surveillance

- Year: 2020
- URL: https://doi.org/10.3390/rs13010104
- Use: Practical SAR/AIS fusion for maritime surveillance.
- D4D extraction: Supports the "AIS alone is incomplete; fuse satellite/SAR and AIS" argument.

### 8. Revealing Dark Vessels in the Mauritius Exclusive Economic Zone (EEZ) Using Multi-Temporal SAR and AIS Data

- Year: 2023
- URL: http://dx.doi.org/10.1109/igarss52108.2023.10282208
- Use: Dark vessel detection example with SAR + AIS.
- D4D extraction: Use as a concrete analogous scenario for gray-zone maritime warning.

### 9. Sensors and AI Techniques for Situational Awareness in Autonomous Ships: A Review

- Year: 2020
- URL: https://doi.org/10.1109/tits.2020.3023957
- Use: Maritime situational awareness and sensor integrity.
- D4D extraction: Use to define maritime situational awareness and sensor fusion needs.

### 10. A Common Operational Picture in Support of Situational Awareness for Efficient Emergency Response Operations

- Year: 2017
- URL: https://doi.org/10.18488/journal.102.2017.21.10.35
- Use: COP in multi-agency dynamic response.
- D4D extraction: Good non-military public safety analogue for shared situational awareness.

## Priority B: Read If Time Allows

### 11. Application of Augmented Reality, Mobile Devices, and Sensors for Combat Entity Quantitative Assessment Supporting Decisions and Situational Awareness Development

- Year: 2019
- URL: https://doi.org/10.3390/app9214577
- Use: Tactical decision support and sensor/mobile data.
- D4D extraction: Useful for UI/field decision support language.

### 12. Maritime information sharing environment deployment using advanced multilayered Data Lake capabilities

- Year: 2022
- URL: https://doi.org/10.31217/p.36.2.13
- Use: Maritime information sharing between agencies.
- D4D extraction: Helps justify information-sharing architecture.

### 13. Deep Learning Enabled Semantic Communication Systems

- Year: 2021
- URL: https://doi.org/10.1109/tsp.2021.3071210
- Use: Technical semantic communication foundation.
- D4D extraction: Read for conceptual grounding, not for implementation detail.

### 14. A survey on semantic communications: Technologies, solutions, applications and challenges

- Year: 2023
- URL: https://doi.org/10.1016/j.dcan.2023.05.010
- Use: Alternative broad survey.
- D4D extraction: Compare definitions and evaluation metrics.

### 15. Harnessing the power of Machine learning for AIS Data-Driven maritime Research: A comprehensive review

- Year: 2024
- URL: https://doi.org/10.1016/j.tre.2024.103426
- Use: ML over AIS data.
- D4D extraction: Good for feature engineering and model candidates.

### 16. AI in Maritime Security: Applications, Challenges, Future Directions, and Key Data Sources

- Year: 2025
- URL: https://doi.org/10.3390/info16080658
- Use: Maritime security survey and data source overview.
- D4D extraction: Use for D4D source catalog and pitch background.

### 17. AI-Driven Tactical Communications and Networking for Defense: A Survey and Emerging Trends

- Year: 2025
- URL: http://arxiv.org/abs/2504.05071v1
- Use: Defense-specific tactical communication survey.
- D4D extraction: Use carefully because it is arXiv/preprint-like; good for vocabulary and trend framing.

### 18. A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges

- Year: 2025
- URL: https://doi.org/10.3390/bdcc9120320
- Use: RAG metrics and challenges.
- D4D extraction: Use for grounded brief evaluation and hallucination mitigation.

### 19. Correctness is not Faithfulness in Retrieval Augmented Generation Attributions

- Year: 2025
- URL: https://doi.org/10.1145/3731120.3744592
- Use: Explains why answer correctness and citation faithfulness differ.
- D4D extraction: Use to justify evidence table and source-grounded briefing requirements.

### 20. Provenance-Aware Knowledge Representation: A Survey of Data Models and Contextualized Knowledge Graphs

- Year: 2020
- URL: https://doi.org/10.1007/s41019-020-00118-0
- Use: Provenance-aware knowledge representation.
- D4D extraction: Supports source/provenance fields in the event graph.

## What To Extract From Each Paper

For every paper, capture:

- Definition or concept we can reuse
- Input data types
- Output data types
- Evaluation metric
- Diagram/architecture idea
- Dataset/code link
- One concrete sentence that supports the pitch
- One limitation or risk

Use `../paper_note_template.md` for notes.


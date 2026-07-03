# A Survey on Goal-Oriented Semantic Communication: Techniques, Challenges, and Future Directions

## Metadata

- Year: 2024
- URL: https://doi.org/10.1109/access.2024.3381967
- DOI: 10.1109/access.2024.3381967
- Read status: abstract_only

## One-line Takeaway

Goal-oriented semantic communication supports sending only mission-relevant information needed for task success, reducing bandwidth, power use, and delay.

## D4D Relevance

Directly relevant as a conceptual backbone for a T3 semantic COP: instead of replicating all maritime sensor data over denied or degraded links, the COP can transmit prioritized semantic state updates tied to operational goals such as threat awareness, route safety, blue-force tracking, and search-and-rescue coordination.

## Key Concepts

- goal-oriented semantic communication
- task-driven information selection
- semantic relevance
- 6G and semantic networking integration
- bandwidth, power, and latency reduction
- communication for autonomous systems
- semantic communication challenges and future directions

## Input Data

- mission or task objectives
- semantically relevant features extracted from raw data
- network constraints such as bandwidth, delay, and power limits
- 6G/SemCom research literature
- autonomous transportation-style use cases

## Methods Or Architecture

- survey of goal-oriented SemCom concepts, frameworks, trends, use cases, and research challenges
- task-success-oriented communication model
- semantic filtering before transmission
- tight coupling between communication design and end-user task execution
- future research framing for theories, algorithms, and implementations

## Outputs / Metrics

- task execution success
- power consumption reduction
- bandwidth consumption reduction
- transmission delay reduction
- semantic relevance of transmitted information

## Prototype Hooks

- implement a mission-goal layer that ranks COP updates by operational relevance
- encode maritime events as compact semantic messages rather than raw feeds
- adapt update frequency and detail level based on link quality and task urgency
- use semantic compression for AIS, radar, EO/IR, weather, and intelligence summaries
- build a T3 policy engine that decides what must be transmitted, delayed, summarized, or dropped under denial

## Pitch Evidence

- The paper positions goal-oriented SemCom as a way to maintain task performance while reducing power, bandwidth, and latency demands.
- It supports the core hackathon argument that degraded networks require meaning-aware communication, not just lower-bitrate data transport.
- Its 6G/autonomous-system framing maps well to contested maritime operations where machines and humans need shared actionable state, not full-fidelity raw data.

## Limitations / Risks

- Only abstract text was available, so detailed taxonomy, algorithms, and evaluation results could not be verified.
- Survey paper, not a maritime COP implementation or field trial.
- Likely assumes future 6G capabilities that may not exist in denied naval environments.
- Does not directly address adversarial jamming, deception, intermittent custody transfer, or cross-domain security constraints in the provided excerpt.

## Confidence

medium

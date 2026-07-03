# First Reading Queue

Last updated: 2026-07-01

이 문서는 자동 수집된 228개 논문 메타데이터에서 D4D 문제와 바로 연결될 가능성이 높은 논문을 사람이 읽기 좋은 순서로 추린 1차 큐입니다. 자동 점수가 높은 범용 AI 논문은 일부 제외하고, 트랙 문제와 데이터/데모 연결성이 높은 문헌을 우선했습니다.

## T1. Autonomy, Unmanned Systems & Counter-UAS

1. Survey on Anti-Drone Systems: Components, Designs, and Challenges (2021)  
   https://doi.org/10.1109/access.2021.3065926  
   Why: Counter-UAS 시스템 구성요소, 탐지/추적/대응 방식의 큰 그림을 잡기 좋습니다.

2. Defending Airports from UAS: A Survey on Cyber-Attacks and Counter-Drone Sensing Technologies (2020)  
   https://doi.org/10.3390/s20123537  
   Why: 공항 방어 맥락이지만 저고도 소형 UAS 탐지와 counter-drone sensing을 이해하기 좋습니다.

3. Deep Learning on Multi Sensor Data for Counter UAV Applications: A Systematic Review (2019)  
   https://doi.org/10.3390/s19224837  
   Why: RF/EO/IR/radar 등 다중 센서와 딥러닝 기반 counter-UAV 적용을 봅니다.

4. Simultaneous Localization and Mapping (SLAM) and Data Fusion in Unmanned Aerial Vehicles: Recent Advances and Challenges (2022)  
   https://doi.org/10.3390/drones6040085  
   Why: 지형 인지형 자율성, GPS 제한 환경, UAV data fusion에 연결됩니다.

5. A survey of cyber security threats and solutions for UAV communications and flying ad-hoc networks (2022)  
   https://doi.org/10.1016/j.adhoc.2022.102894  
   Why: 무선침묵 IFF, replay/MITM, UAV 통신 보안 문제를 잡는 배경자료입니다.

## T2. OSINT & Defense Intelligence

1. Cyber Threat Intelligence Mining for Proactive Cybersecurity Defense: A Survey and New Perspectives (2023)  
   https://doi.org/10.1109/comst.2023.3273282  
   Why: CTI 수집, 분석, mining, proactive defense를 포괄하는 T2 핵심 survey입니다.

2. A Survey on Knowledge Graphs: Representation, Acquisition, and Applications (2021)  
   https://doi.org/10.1109/tnnls.2021.3070843  
   Why: OSINT 지식그래프, entity/relation modeling, provenance 구조의 기반입니다.

3. Exploring the Potential of Large Language Models for Improving Digital Forensic Investigation Efficiency (2024)  
   http://arxiv.org/abs/2402.19366  
   Why: LLM을 조사/분석 워크플로우에 넣는 방법을 볼 수 있습니다.

4. Advanced Persistent Threats based on Supply Chain Vulnerabilities: Challenges, Solutions and Future Directions (2024)  
   https://doi.org/10.36227/techrxiv.170594149.97651781/v1  
   Why: 방산 공급망 자격증명 노출 조기경보와 직접 연결됩니다.

5. OSINT intelligence analysis knowledge graph / provenance / citation 계열은 추가 수동 검색 필요  
   Note: 자동 수집 결과만으로는 OSINT-specific LLM citation 논문이 부족했습니다. 다음 패스에서 `OSINT analyst copilot`, `intelligence analysis provenance`, `explainable OSINT`, `source credibility OSINT` 키워드로 보강합니다.

## T3. Battle Network, C2 & Sustainment

1. A Review on Internet of Things for Defense and Public Safety (2016)  
   https://doi.org/10.3390/s16101644  
   Why: defense/public safety IoT와 C2/sensor network의 기초를 잡는 데 좋습니다.

2. Application of Augmented Reality, Mobile Devices, and Sensors for a Combat Entity Quantitative Assessment Supporting Decisions and Situational Awareness Development (2019)  
   https://doi.org/10.3390/app9214577  
   Why: 전장 상황인식, 센서, decision support를 연결합니다.

3. A Semantics-Based Common Operational Command System for Multiagency Disaster Response (2020)  
   https://doi.org/10.1109/tem.2020.3013109  
   Why: semantic 기반 COP/C2 설계는 군 C2뿐 아니라 재난/다기관 대응으로도 전이됩니다.

4. A Survey on Semantic Communications for Intelligent Wireless Networks (2022)  
   https://doi.org/10.1007/s11277-022-10111-7  
   Why: T3 S-DOT/전술망 시맨틱 전송의 기본 개념을 잡습니다.

5. What is Semantic Communication? A View on Conveying Meaning in the Era of Machine Intelligence (2021)  
   https://doi.org/10.23919/jcin.2021.9663101  
   Why: "원본 전송" 대신 "의미 전송"이라는 문제의식을 설명하기 좋습니다.

6. Engineering Semantic Communication: A Survey (2023)  
   https://doi.org/10.1109/access.2023.3243065  
   Why: 실제 시스템 구현 관점의 시맨틱 통신 survey입니다.

## T4. Maritime Domain Awareness

1. Anomaly Detection in Maritime AIS Tracks: A Review of Recent Approaches (2022)  
   https://doi.org/10.3390/jmse10010112  
   Why: AIS anomaly detection의 가장 직접적인 starting point입니다.

2. How big data enriches maritime research: a critical review of Automatic Identification System (AIS) data applications (2019)  
   https://doi.org/10.1080/01441647.2019.1649315  
   Why: AIS를 어떤 문제에 어떻게 쓰는지 넓게 이해할 수 있습니다.

3. Satellite mapping reveals extensive industrial activity at sea (2024)  
   https://doi.org/10.1038/s41586-023-06825-8  
   Why: AIS가 꺼진 활동이나 숨겨진 해상 활동을 위성으로 보완하는 관점입니다.

4. Synthetic Aperture Radar (SAR) for Ocean: A Review (2023)  
   https://doi.org/10.1109/jstars.2023.3310363  
   Why: SAR 기반 dark vessel, 해상 감시, 위성 데이터 활용의 기초입니다.

5. LS-SSDD-v1.0: A Deep Learning Dataset Dedicated to Small Ship Detection from Large-Scale Sentinel-1 SAR Images (2020)  
   https://doi.org/10.3390/rs12182997  
   Why: Sentinel-1 SAR 기반 소형 선박 탐지 dataset로 프로토타입 후보입니다.

6. AI in Maritime Security: Applications, Challenges, Future Directions, and Key Data Sources (2025)  
   https://doi.org/10.3390/info16080658  
   Why: maritime security와 key data source를 함께 정리한 최신 review입니다.

## T5. Force Readiness, Training & Simulation

1. Artificial Intelligence in the Military: An Overview of the Capabilities, Applications, and Challenges (2023)  
   https://doi.org/10.1155/2023/8676366  
   Why: 군사 AI 적용 범위를 넓게 이해하는 첫 문헌입니다.

2. An Overview of Serious Games (2014)  
   https://doi.org/10.1155/2014/358152  
   Why: AI 워게임 교관, 전술 훈련 시뮬레이터의 교육 설계 배경입니다.

3. Exploring Large Language Model based Intelligent Agents: Definitions, Methods, and Prospects (2024)  
   http://arxiv.org/abs/2401.03428  
   Why: AI tutor/agent workflow 설계에 도움이 됩니다.

4. A Survey of Large Language Models (2026)  
   https://doi.org/10.1007/s11704-026-60308-3  
   Why: LLM 기술 배경을 한 번에 잡는 survey입니다. 단, 범용 문헌이라 D4D 적용점만 추출합니다.

5. On-device/offline RAG는 추가 수동 검색 필요  
   Note: 자동 수집 결과가 범용 LLM 쪽으로 치우쳤습니다. `small language model on-device RAG`, `edge LLM offline retrieval`, `military training simulator LLM` 키워드로 보강합니다.

## Cross-cutting: LLM Reliability, Citation, Provenance

1. Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context (2024)  
   http://arxiv.org/abs/2403.05530  
   Why: 긴 context를 다루는 LLM의 가능성과 한계를 보는 참고자료입니다.

2. Datasets for Large Language Models: A Comprehensive Survey (2024)  
   https://doi.org/10.21203/rs.3.rs-3996137/v1  
   Why: RAG/LLM 데이터셋 설계와 평가 포인트를 볼 수 있습니다.

3. Citation/provenance/eval 문헌은 다음 패스에서 강화 필요  
   Query candidates: `retrieval augmented generation citation evaluation`, `RAG hallucination attribution`, `provenance aware question answering`, `source-grounded LLM`.

## Immediate Reading Order

1. T4 AIS anomaly review
2. T2 CTI mining survey
3. T1 anti-drone systems survey
4. T3 semantic communication survey
5. T2 knowledge graph survey
6. T4 SAR for Ocean review
7. T5 AI in the Military overview

이 순서가 좋은 이유: 해커톤의 데이터 접근성과 데모 가능성을 가장 빨리 판단하게 해줍니다.


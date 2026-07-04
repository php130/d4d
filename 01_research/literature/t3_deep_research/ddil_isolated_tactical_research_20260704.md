# DDIL / Isolated Tactical Environment Research Pack

- Version: `20260704_ks`
- Scope: T3 resilient maritime COP, C2, semantic data transmission, sustainment under physically or network-isolated conditions
- Research mode: public/open sources only
- Safety boundary: defensive resilience, decision support, emergency continuity, and C2 robustness. This note intentionally avoids actionable radio parameters, intrusion methods, offensive EW guidance, targeting procedures, or classified/controlled operational details.

## One-Line Thesis

고립 환경 대응은 "끊긴 통신을 어떻게든 복구한다"가 아니라, **통신이 끊겨도 지휘관 의도, 최소 작전상황도, 우선순위 메시지, 근거 기록, 복귀 후 동기화가 살아남도록 시스템과 작전 방식을 함께 설계하는 것**이다.

## Why This Matters For D4D T3

현재 D4D T3 데모는 `Resilient Maritime COP over Denied Networks` 방향이다. 여기에 DDIL/고립 환경 리서치를 붙이면 데모의 의미가 더 선명해진다.

- 기존 메시지: 네트워크가 열악할 때 raw data 대신 semantic event를 보낸다.
- 보강 메시지: 네트워크가 완전히 끊겨도 local COP, commander intent, PACE ladder, store-forward sync, stale-data warning으로 작전 의미를 유지한다.
- KT/통신사 관점 차별점: 단순 지도를 만드는 것이 아니라, 통신 상태를 작전 의사결정의 1급 데이터로 올린다.

## Key Terms

| Term | Meaning | D4D Interpretation |
| --- | --- | --- |
| DDIL / DIL | Denied/Degraded/Disconnected, Intermittent, Limited/Low-bandwidth | 연결이 없거나, 느리거나, 짧은 창으로만 열리는 상태 |
| Tactical edge | 중앙 클라우드/본부와 안정 연결되지 않는 현장 말단 | 함정, 해안 감시소, 이동 지휘소, UAV/USV/UGV, 휴대 단말 |
| Mission command | 세부 지시가 끊겨도 지휘관 의도 안에서 하급 제대가 판단하는 방식 | 시스템에 "의도 카드"와 위임/전환 기준을 넣는 UX |
| PACE plan | Primary, Alternate, Contingency, Emergency 통신 수단의 단계적 계획 | 링크 상태에 따라 전송 채널/형식/주기를 바꾸는 ladder |
| DTN | Delay/Disruption Tolerant Networking | 지금 못 보내면 저장하고, 연결 창이 생기면 우선순위대로 전달 |
| Store-carry-forward | 노드가 데이터를 저장했다가 이동/재연결 시 전달 | 해상/도서/재난 현장의 물리적 전달 또는 이동 relay 모델 |
| MANET / mesh | 이동 노드 간 자율 네트워크 | 지휘소-함정-드론-차량 간 임시 네트워크 개념 |
| Semantic communication | 원시 비트가 아니라 임무에 필요한 의미를 우선 전달 | full track/video 대신 alert, delta, confidence, evidence digest |
| Local-first / CRDT | 오프라인에서 각 노드가 독립 작업 후 나중에 병합 | disconnected COP의 충돌 병합과 감사 기록 |
| Stale data | 오래되어 더 이상 현 상황을 대표하지 못할 수 있는 정보 | 지도 위 모든 contact에 freshness와 uncertainty를 표시 |

## Research Takeaways

1. **작전 방식부터 바뀌어야 한다.** AFDP 1-1, RAND, EABO 계열 문헌은 contested/degraded 환경에서 중앙 집중적 지시보다 commander intent, shared understanding, delegated authority, decentralized execution이 중요하다고 본다.
2. **통신 설계는 PACE + mission priority로 해야 한다.** CISA/MITRE의 PACE 자료와 DARPA MINC/DyNAMO는 "무슨 링크가 살아 있나"보다 "중요 정보가 적시에 적절한 사람에게 가는가"를 중심에 둔다.
3. **기술 핵심은 DTN, edge computing, local-first sync다.** RFC 9171/4838, CMU tactical cloudlets, OGC disconnected networks, CRDT/local-first 문헌이 모두 같은 패턴을 제시한다: local cache, priority queue, asynchronous sync, conflict resolution.
4. **데모는 full-sync 실패를 숨기면 안 된다.** 좋은 COP는 끊긴 정보를 숨기지 않고 `last seen`, `confidence`, `source trust`, `missing evidence`, `sync backlog`를 보여준다.
5. **Semantic data transmission은 DDIL에서 더 설득력이 커진다.** 영상/대용량 원자료가 못 가는 상황에서도 `who/where/why/so-what` 의미 카드가 살아남으면 지휘통제 가치가 있다.
6. **재난통신은 군사 DDIL의 좋은 공개 프록시다.** FEMA, NIST PSCR, ITU, ETC/WFP는 민간 재난 환경에서 고립 지역 통신, 임시 인프라, 사용자 중심 정보교환을 다룬다. D4D에서는 민군 겸용 레퍼런스로 쓰기 좋다.
7. **한국 맥락은 TICN, PS-LTE, 5G, 이동형 기지국, 도서/해상/산악 지형을 연결하면 좋다.** 국내 공개 연구는 한국군 기반통신망, 전술통신체계, 재난안전통신망, 5G 활용 방향을 배경 근거로 삼을 수 있다.

## Tactical Operating Pattern Under Isolation

### 1. Before Isolation: Pre-Position Meaning

- 지휘관 의도, 임무 목적, 금지/주의 조건, 보고 우선순위를 `Intent Packet`으로 사전 배포한다.
- 작전 구역 지도 타일, 항로/항만/기상/선박 baseline, 모델, 규칙, 연락망을 local cache로 배포한다.
- PACE 계획을 단순한 연락처 목록이 아니라 "언제 어떤 수준의 데이터를 보낼지"로 정의한다.
- 각 노드가 혼자 남았을 때 수행할 최소 기능을 정한다: observe, classify, alert, log, brief, sync.

### 2. During Degradation: Shed Non-Essential Load

- raw stream 전송을 줄이고 `track delta`, `alert card`, `evidence digest`, `status heartbeat` 중심으로 바꾼다.
- 낮은 우선순위 데이터는 store-forward queue에 넣고, high-priority event만 보낸다.
- 지도에는 링크 품질과 데이터 신선도 저하를 함께 표시한다.
- LLM/briefing 기능은 외부 reach-back 없이 local COP와 cached docs만 사용한다.

### 3. During Complete Isolation: Local Autonomy

- 중앙 판단을 기다리지 않고 local intent 안에서 observation, triage, report preparation을 계속한다.
- 모든 판단은 나중에 검토할 수 있도록 evidence, timestamp, model/rule version, operator note와 함께 기록한다.
- 지도는 "현재 확정 정보"가 아니라 "마지막 관측 기반 추정 상태"임을 명확히 표시한다.
- 단말/노드별로 임무 로그와 sync bundle을 만든다.

### 4. During Intermittent Contact: Opportunistic Sync

- 연결 창이 열리면 priority queue 순서대로 전송한다.
- 중복 원자료보다 `delta`, `conflict`, `high-value alert`, `commander intent update`를 먼저 보낸다.
- 패킷 단위 성공률보다 `mission-message delivery`를 지표로 삼는다.

### 5. After Rejoin: Reconcile And Audit

- 각 노드의 local COP를 병합하면서 충돌을 덮어쓰지 않고 claim/evidence 단위로 보존한다.
- `who knew what when`을 재구성해 AAR, 책임성, 모델 개선에 쓴다.
- stale decision, false alert, missing data를 별도 review queue로 올린다.

## Recommended Demo Additions

| Demo Feature | What It Shows | Why It Matters |
| --- | --- | --- |
| Isolation mode switch | Connected, Degraded, Intermittent, Isolated, Rejoin | 네트워크 상태가 작전 상태판의 핵심 변수임을 보여줌 |
| PACE ladder panel | Primary/Alternate/Contingency/Emergency 채널과 payload tier | 통신 계획을 UI에서 실행 가능한 정책으로 표현 |
| Commander intent card | mission goal, constraints, decision thresholds | 통신 두절 시 local 판단 기준 제공 |
| Local COP cache | 노드별 마지막 상황도와 stale age | 중앙 연결이 없어도 최소 상황 인식 유지 |
| Sync bundle queue | 보낼 메시지, 보류 이유, 우선순위, 예상 크기 | DTN/store-forward를 시각적으로 설명 |
| Semantic payload comparator | raw bytes vs semantic event bytes vs retained utility | S-DOT/semantic transmission의 해커톤 메시지 강화 |
| Conflict reconciliation drawer | AIS/SAR/UAV/operator report 불일치 병렬 표시 | fusion이 "정답 하나"가 아니라 증거 관리임을 보여줌 |
| Source trust overlay | sensor health, link status, source reliability | 오탐/스푸핑/누락 가능성을 숨기지 않음 |
| Rejoin timeline | 고립 중 발생한 이벤트가 복귀 후 병합되는 흐름 | AAR와 감사 가능성 제공 |

## Data Objects To Add

```json
{
  "intent_packet": {
    "mission_id": "maritime_cop_demo_001",
    "commander_intent": "Maintain maritime awareness and prioritize suspicious AIS-off contacts near protected lanes.",
    "decision_thresholds": ["high_confidence_dark_vessel", "port_approach_anomaly", "loss_of_primary_link"],
    "constraints": ["public/open data only", "no raw sensitive data redistribution"],
    "valid_until": "2026-07-05T09:00:00Z"
  }
}
```

```json
{
  "pace_plan": {
    "primary": {"channel": "broadband_api", "payload": "track+evidence+map_tiles"},
    "alternate": {"channel": "low_bandwidth_ip", "payload": "track_delta+alert_card"},
    "contingency": {"channel": "store_forward_window", "payload": "priority_bundle"},
    "emergency": {"channel": "manual_or_physical_transfer", "payload": "intent_status_and_critical_alerts"},
    "switch_triggers": ["latency_ms>2000", "packet_loss>30%", "no_contact_minutes>15"]
  }
}
```

```json
{
  "sync_bundle": {
    "bundle_id": "bundle_node_a_042",
    "created_at": "2026-07-04T11:35:00Z",
    "origin_node": "coastal_node_a",
    "priority": "high",
    "ttl_minutes": 120,
    "contains": ["alert_17", "track_delta_vessel_042", "evidence_digest_09"],
    "size_bytes": 4812,
    "delivery_state": "queued_until_contact"
  }
}
```

```json
{
  "cop_claim": {
    "entity_id": "vessel_042",
    "claim": "AIS-off contact detected near route alpha",
    "source": "synthetic_sar_node_1",
    "confidence": 0.78,
    "observed_at": "2026-07-04T11:12:00Z",
    "received_at": "2026-07-04T11:31:00Z",
    "freshness_seconds": 1140,
    "conflicts_with": ["ais_claim_331"],
    "provenance": ["sar_scene_20260704_a", "association_rule_v0.2"]
  }
}
```

## Source Index

### P0: Doctrine, Official Programs, And Standards

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P0 | CMU SEI, Networking at the Tactical and Humanitarian Edge | https://www.sei.cmu.edu/blog/networking-at-the-tactical-and-humanitarian-edge/ | DIL/DDIL framing, data/protocol/connection shaping, caching, DTN | Architecture justification for graceful degradation |
| P0 | RFC 9171, Bundle Protocol Version 7 | https://www.rfc-editor.org/rfc/rfc9171.html | Store-carry-forward overlay for stressed networks | `sync_bundle` model and delayed delivery simulation |
| P0 | RFC 4838, Delay-Tolerant Networking Architecture | https://www.rfc-editor.org/rfc/rfc4838.html | DTN architecture assumptions and design vocabulary | Technical backbone for intermittent maritime links |
| P0 | OGC Testbed-13 Disconnected Networks Engineering Report | https://docs.ogc.org/per/17-026r1.html | DDIL geospatial services, caching, async, compression, GeoPackage | Offline map/COP data design |
| P0 | DARPA MINC | https://www.darpa.mil/research/programs/mission-integrated-network-control | Mission-aware routing of critical data across comms/compute/storage | Pitch: "critical data finds a path" |
| P0 | DARPA DyNAMO | https://www.darpa.mil/research/programs/dynamic-network-adaptation-for-mission-optimization | Dynamic adaptation across heterogeneous networks | PACE policy engine and network-of-networks framing |
| P0 | DARPA EdgeCT | https://www.darpa.mil/research/programs/edge-directed-cyber-technologies-for-reliable-mission-communication | Mission-aware resilience at WAN edge using endpoint/enclave capabilities | Edge-side mitigation pattern |
| P0 | DARPA SHARE transition note | https://www.darpa.mil/news/2023/communications-tactical-edge | Secure/resilient sharing at tactical edge, TAK transition | Demonstrate handheld/geospatial app relevance |
| P0 | AFDP 1-1 Mission Command | https://www.doctrine.af.mil/Portals/61/documents/AFDP_1-1/AFDP%201-1%20Mission%20Command.pdf | Commander intent, shared understanding, decentralized execution in degraded comms | `intent_packet` and UI language |
| P0 | RAND, Distributed Operations in a Contested Environment | https://www.rand.org/content/dam/rand/pubs/research_reports/RR2900/RR2959/RAND_RR2959.pdf | Delegated authorities, mission orders, trust/shared understanding | Operational argument for isolated local decision support |
| P0 | USMC Tentative Manual for EABO, 2nd ed. | https://www.marines.mil/Portals/1/Docs/230509-Tentative-Manual-For-Expeditionary-Advanced-Base-Operations-2nd-Edition.pdf | Austere, temporary, distributed maritime operations | Maritime/island isolation scenario framing |
| P0 | USMC EABO overview | https://www.marines.mil/News/News-Display/Article/2708120/expeditionary-advanced-base-operations-eabo/ | High-level EABO concept summary | Non-technical background for deck |
| P0 | A Concept for Stand-In Forces | https://www.hqmc.marines.mil/Portals/142/Users/183/35/4535/211201_A%20Concept%20for%20Stand-In%20Forces.pdf | Distributed forces in contested maritime spaces | T3/T4 gray-zone maritime alignment |
| P0 | Department of the Navy Information Superiority Vision | https://media.defense.gov/2020/May/18/2002302013/-1/-1/1/DON_INFORMATION_SUPERIORITY.PDF | Naval mesh, DDIL-functioning network ambition | Naval C2 and mesh vocabulary |
| P0 | ALSSA Space Degraded/Contested Operations Study | https://www.alssa.mil/Portals/9/Documents/studies/sdco_study_2017.pdf | GPS/SATCOM degraded context | Avoid overreliance on space-enabled services |
| P0 | CISA PACE Plan Emergency Communications Ecosystem | https://www.cisa.gov/resources-tools/resources/leveraging-pace-plan-emergency-communications-ecosystem | Primary/Alternate/Contingency/Emergency planning | Civil emergency source for `PACE ladder` |
| P0 | MITRE, Building PACE Capabilities for the Current Threat Environment | https://www.mitre.org/sites/default/files/2026-01/PR-25-2966-building-pace-capabilities-for-the-current-threat-environment_0.pdf | Modern PACE planning, critical functions, degraded circuits | 2026-current PACE reference |
| P0 | NIST Public Safety Communications Research Roadmap | https://www.nist.gov/ctl/ctl-roadmaps/public-safety-communications-research-roadmap | coverage, secure exchange, situational awareness, mission critical voice | Public-safety analogue for tactical resilience |
| P0 | FEMA Disaster Emergency Communications | https://www.fema.gov/about/offices/response/disaster-emergency-communications | Mobile response support and emergency comms continuity | Disaster isolated-area analogy |
| P0 | ITU National Emergency Telecommunication Plans guideline | https://www.itu.int/en/ITU-D/Emergency-Telecommunications/Documents/2019/NETP_Global_guideline.pdf | National-level emergency telecom planning | Policy background for Korea/public-sector framing |
| P0 | WFP Emergency Telecommunications Cluster | https://www.wfp.org/emergency-telecommunications-cluster | Connectivity as critical aid in crises | Humanitarian DDIL language |
| P0 | ETC Connectivity as Aid Standards | https://www.etcluster.org/document/connectivity-aid-standards | Safe, inclusive, accountable crisis connectivity | Data ethics/privacy framing |

### P1: Tactical Networking And Edge Computing Research

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P1 | Combining Software-Defined and Delay-Tolerant Approaches in Last-Mile Tactical Edge Networking | https://people.computing.clemson.edu/~jmarty/projects/lowLatencyNetworking/papers/FutureMilitaryBattlefields/CombiningSDNAndDTNfortheFutureMilitaryBF.pdf | SDN + DTN for tactical last mile | Network policy simulator ideas |
| P1 | CMU SEI Tactical Cloudlets | https://www.sei.cmu.edu/projects/tactical-cloudlets-bringing-the-cloud-to-the-tactical-edge/ | Data filtering, formatting, staging at edge | Local edge node and pre-processing story |
| P1 | Tactical Cloudlets paper | https://elijah.cs.cmu.edu/DOCS/lewis-milcom2014.pdf | Forward-deployed cloudlet architecture | Demo local cache/edge inference |
| P1 | Opportunistic Peer-to-Peer Mobile Cloud Computing at the Tactical Edge | https://sites.pitt.edu/~weigao/publications/milcom14-mcc.pdf | Opportunistic computation among mobile devices under DIL | Node-to-node sync and task offload |
| P1 | Dispersed Computing for Tactical Edge in Future Wars | https://onlinelibrary.wiley.com/doi/10.1155/2021/8899186 | Distributed computing under tactical constraints | Edge architecture literature |
| P1 | SMARTNet: Improving Tactical Situational Awareness and C2 | https://www.dst.defence.gov.au/sites/default/files/basic_pages/documents/ICSILP18_IntSes-Judd_et_al-SMARTNet.pdf | Semantic management of tactical information overload | Priority scoring and information triage |
| P1 | SMARTNet ICCRTS paper | https://dodccrp-testorg.squarespace.com/s/24th_ICCRTS_paper_40.pdf | Tactical comms management research | Follow-up for message broker/policy detail |
| P1 | Semantically Managed Autonomous and Resilient Tactical Networks | https://dodccrp-testorg.squarespace.com/s/23rd_ICCRTS_paper_73.pdf | Autonomous, semantic network management | Link between semantic metadata and network adaptation |
| P1 | QoI Source Selection in Tactical Networks | https://c4i.gmu.edu/~pcosta/F15/data/fileserver/file/472250/filename/Paper_1570112881.pdf | Quality of information source selection | Source trust and evidence ranking |
| P1 | Frontiers of C2 paper on battlespace information management | https://dodccrp-testorg.squarespace.com/s/paper_34.pdf | C2 agility and DIL information management | COP overload and C2 agility framing |
| P1 | DDS at the Tactical Edge whitepaper | https://www.omg.org/news/whitepapers/DDS-Tactical-Edge-Whitepaper.pdf | Pub-sub, QoS, intermittent connectivity at edge | Pub-sub data distribution option |
| P1 | NATO Information Management over Disadvantaged Grids | https://www.sto.nato.int/document/information-management-over-disadvantaged-grids/ | Low bandwidth, variable throughput, unreliable tactical grids | NATO vocabulary and coalition angle |
| P1 | NATO Adaptive Information Processing and Distribution in Disadvantaged Tactical Networks | https://www.sto.nato.int/document/adaptive-information-processing-and-distribution-in-disadvantaged-tactical-networks-to-support-command-and-control/ | Adaptive information processing/distribution for C2 | S-DOT and priority policy framing |
| P1 | NATO IST-193 Edge Computing at the Tactical Edge | https://www.fkie.fraunhofer.de/en/press-releases/nato-sto-ist-193.html | Edge computing research for tactical edge | Coalition edge research direction |
| P1 | RFC 3561 AODV | https://www.rfc-editor.org/rfc/rfc3561.html | Ad hoc routing baseline | Background only; do not implement in hackathon |
| P1 | RFC 7181 OLSRv2 | https://www.rfc-editor.org/rfc/rfc7181.html | Proactive MANET routing baseline | Background only; use simulator abstraction |

### P1: Semantic Communication, Local-First, And Sync

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P1 | What is Semantic Communication? | https://doi.org/10.23919/jcin.2021.9663101 | Meaning-oriented communication concept | Explain semantic event layer |
| P1 | A Survey on Semantic Communications | https://www.sciencedirect.com/science/article/pii/S2352864823000925 | Technologies, applications, challenges | Literature backup for S-DOT |
| P1 | Semantic Communications for Future Internet | https://arxiv.org/abs/2207.00427 | Semantic communication taxonomy | Payload tiering |
| P1 | Tutorial-Cum-Survey on Semantic and Goal-Oriented Semantic Communication | https://arxiv.org/abs/2308.01913 | Goal-oriented/task-relevant communication | Mission utility metric |
| P1 | Towards Goal-Oriented Semantic Communications | https://arxiv.org/html/2304.00848v3 | Goal/task-oriented formulation | `mission-message throughput` metric |
| P1 | Task-Oriented Multi-User Semantic Communications for VQA | https://doi.org/10.1109/lwc.2021.3136045 | Multi-modal task-oriented semantic transmission | Image/text alert card analogy |
| P1 | Local-First Software essay | https://www.inkandswitch.com/essay/local-first/ | Offline-capable collaboration principles | Disconnected COP UX |
| P1 | Local-First Software PDF | https://martin.kleppmann.com/papers/local-first.pdf | CRDT and local-first design | Sync/conflict resolution foundations |
| P1 | CRDT original report | https://inria.hal.science/inria-00609399v2/document | Conflict-free replicated data types | Rejoin merge concept |
| P1 | CRDT.tech | https://crdt.tech/ | CRDT overview and references | Implementation reading queue |
| P2 | Ditto CRDT/offline-first guide | https://www.ditto.com/blog/how-to-build-robust-offline-first-apps-a-technical-guide-to-conflict-resolution-with-crdts-and-ditto | Practical conflict handling vocabulary | Product framing only |
| P2 | RxDB downsides of offline-first | https://rxdb.info/downsides-of-offline-first.html | Offline-first tradeoffs | Risk section: conflict/security/storage complexity |

### P1: Maritime And COP-Specific References

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P1 | Maritime Operations in Denied, Intermittent, and Low-Bandwidth Environments | https://www.dodccrp.org/events/18th_iccrts_2013/post_conference/papers/088.pdf | Maritime DIL application pattern | Direct T3/T4 maritime fit |
| P1 | Maritime Domain Awareness C4I paper | https://c4i.gmu.edu/eventsInfo/reviews/2010/papers/Brown_MDA_TSN_C4I_final_enhanced_10Mar2010.pdf | MDA and C4I sharing patterns | COP information-sharing background |
| P1 | Domain Awareness Superiority Is the Future of Military Intelligence | https://www.armyupress.army.mil/Journals/Military-Review/English-Edition-Archives/November-December-2021/Ryder-Domain-Awareness/ | Domain awareness across MDA and intelligence | Narrative support |
| P1 | Maritime Domain Awareness On Demand | https://trid.trb.org/View/2582395 | Low-cost sensors, tactical networking, edge processing for USCG | Coastal sensor deployment idea |
| P1 | AIS Track Anomaly Review already in project notes | https://doi.org/10.3390/jmse10010112 | AIS anomaly approaches | Local anomaly detector |
| P1 | SAR/AIS Fusion already in project notes | https://doi.org/10.3390/rs13010104 | Space-based SAR + AIS association | Synthetic SAR-AIS conflict demo |
| P1 | AI in Maritime Security data sources | https://doi.org/10.3390/info16080658 | Maritime AI applications and data sources | Dataset sourcing |
| P2 | OGC Marine Domain / DDIL mention | https://www.un.org/globalgeospatial/sites/default/files/2023-01/Agenda%20item%207d_no.1.pdf | Marine geospatial standardization context | Standards narrative |

### P1: Korea / Domestic Context

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P1 | 군 전술통신체계의 현재와 미래 기술 발전 방안에 대한 고찰 | https://www.kais99.org/jkais/journal/Vol25no07/Vol25no07p30.pdf | TICN, ANASIS-II, future tactical comms, AI C2 | Korean defense comms background |
| P1 | 미래 전술통신체계개발을 위한 고려사항 연구 | https://koreascience.kr/article/JAKO201831262479879.pdf | Tactical comms constraints and future considerations | Domestic limitations/context |
| P1 | 한국군 기반통신망 분석 및 발전 방향 | https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002597300 | Fixed/mobile networks, TICN, satellite, All-IP direction | Korea-specific C2 comms framing |
| P1 | ETRI 국방 블록체인 기술 동향 | https://www.etri.re.kr/webzine/20210129/sub03.html | Korean explanation of tactical DIL conditions | Domestic DIL vocabulary |
| P1 | 미래 대대급 전술 네트워크 구축을 위한 5G 기반 네트워크 활용방안 | https://journal.dcs.or.kr/xml/28567/28567.pdf | 5G tactical network use considerations | KT background bridge |
| P1 | KIDA, 5G 전국망 시대 군이 준비해야 할 것들 | https://www.kida.re.kr/cmm/viewBoardImageFile.do?idx=44439 | Commercial 5G and defense user identification/use | KT/5G angle |
| P1 | PS-LTE disaster safety network policy study | https://scispace.com/pdf/a-study-on-the-public-safety-long-term-evolution-disaster-1iq5xi1cf5.pdf | Public safety LTE policy and broadband public safety | Civil-military emergency comms analogy |
| P1 | Highway PS-LTE adoption/operation study | https://www.codil.or.kr/filebank/original/RK/OTKCRK240280/OTKCRK240280.pdf | PS-LTE operational adoption | Public infrastructure resilience |
| P2 | 국방 PS-LTE와 재난안전망 통합 위기대응 거버넌스 | https://www.earticle.net/Article/A479087 | Civil-military mobile base station resource integration | Policy idea for public-sector pitch |
| P2 | YTN, drone emergency network demo | https://science.ytn.co.kr/program/view.php?key=202502101116329403&mcd=0082 | Drone-based temporary network for disaster sites | Demo inspiration; not scholarly evidence |
| P2 | Hanwha Systems TICN overview | https://www.hanwhasystems.com/kr/business/defense/c5i/communication01.do | Public product-level TICN explanation | Terms/background only |

### P2: Insight / Industry / Practitioner Writing

| Priority | Source | URL | What To Extract | D4D Use |
| --- | --- | --- | --- | --- |
| P2 | Federal News Network, tactical edge AI and comms in disconnected environments | https://federalnewsnetwork.com/commentary/2026/04/the-tactical-edge-is-now-deploying-ai-and-communications-in-disconnected-environments/ | Minimal viable capability, graceful degradation | Product narrative |
| P2 | Army Line of Departure, Operationalizing AI at the Tactical Edge | https://www.lineofdeparture.army.mil/Journals/Warrant-Officer-Journal/Archive/March-2026/Operationalizing-AI-at-the-Tactical/ | Edge AI instead of cloud dependency | Current 2026 military practitioner framing |
| P2 | REDCOM DDIL communications | https://www.redcom.com/communications-in-ddil-environments/ | Vendor framing of interoperable resilient comms | Market vocabulary only |
| P2 | Appian DDIL environments | https://appian.com/blog/2024/operating-in-dod-ddil-environments | DDIL application design framing | Product risks/tradeoffs |
| P2 | QinetiQ PACE planning | https://www.qinetiq.com/en/blogs/how-to-build-a-pace-plan-that-works | PACE pitfalls and practical framing | UI checklist ideas |
| P2 | MinIO tactical edge | https://www.min.io/blog/from-data-to-dominance-at-the-tactical-edge | Edge storage and disconnected data management | Storage pitch vocabulary |
| P2 | DON CIO, cloud tools for tactical edge | https://www.doncio.navy.mil/chips/ArticleDetails.aspx?ID=15161 | Low bandwidth, high latency, disconnects from broader network | Naval cloud-to-edge framing |
| P2 | FedGovToday, AI/computing to battlefield edge | https://fedgovtoday.com/industry-insights/why-the-pentagon-is-pushing-ai-and-computing-to-the-battlefield-edge | Disconnected/air-gapped operations, simplified deployment | Presentation-level insight |
| P2 | SAIC naval enterprise to tactical edge | https://www.saic.com/perspectives/all-domain-warfighting/naval-enterprise-tactical-edge-innovation | Naval tactical edge interoperability narrative | Industry framing only |

## How To Translate This Into The Current Demo

### New Scenario Script

1. Normal COP: AIS, weather, synthetic SAR/UAV, OSINT event streams update the central map.
2. Degraded link: bandwidth drops; raw evidence thumbnails stop syncing, but semantic event cards continue.
3. Intermittent link: updates queue as DTN bundles; high-priority dark-vessel alert jumps the queue.
4. Isolated node: coastal node maintains local COP using cached map/model/intent; stale data warning appears.
5. Rejoin: queued bundles merge; one AIS/SAR conflict appears in review; briefing assistant summarizes what changed and what is still uncertain.

### Metrics To Show

| Metric | Definition | Why Judges Care |
| --- | --- | --- |
| Mission-message delivery | Delivered high-priority messages / generated high-priority messages | Better than raw packet delivery for C2 |
| Semantic compression ratio | raw bytes / semantic event bytes | Shows telecom/S-DOT value |
| COP freshness | median/critical contact age since last trusted observation | Prevents false confidence |
| Sync convergence time | time to merge local COP after rejoin | Shows resilience |
| Evidence completeness | percent of alerts with source, time, confidence, provenance | Shows trustworthy AI |
| Operator triage time | time to identify highest-risk contact | Demonstrates usability |

### Architecture Implications

- Add a `NetworkState` object: bandwidth, packet loss, latency, outage state, next contact window.
- Add a `TransmissionPolicy` object: payload tier, priority threshold, queue behavior, TTL.
- Add a `LocalNodeState` object: cached map coverage, model version, last sync, pending bundles.
- Add an `IntentPacket` object: mission goal, constraints, decision thresholds, expiry.
- Add a `RejoinAudit` object: merged bundles, conflicts, overwritten fields, unresolved claims.

## First Reading Queue

1. CMU SEI, Networking at the Tactical and Humanitarian Edge.
2. RFC 9171 Bundle Protocol Version 7.
3. OGC Testbed-13 Disconnected Networks Engineering Report.
4. DARPA MINC and DyNAMO program pages.
5. AFDP 1-1 Mission Command and RAND distributed operations report.
6. CMU Tactical Cloudlets and Opportunistic P2P Mobile Cloud Computing.
7. Local-First Software and CRDT original report.
8. SMARTNet / semantic tactical information management papers.
9. Korea tactical communications survey papers.
10. CISA/MITRE PACE planning documents.

## Open Questions For Follow-Up

- D4D demo에서 "고립 노드"를 함정, 해안 감시소, 이동 지휘소 중 무엇으로 잡을까?
- PACE 단계별 payload를 어떤 크기로 가정할까? 예: 5MB raw, 50KB evidence digest, 2KB alert card.
- local-first 병합은 CRDT까지 구현할까, 아니면 event-sourcing + deterministic merge로 데모할까?
- Palantir AIP/Foundry를 쓰게 되면 ontology action으로 `Publish semantic update`, `Mark stale`, `Resolve conflict`를 어떻게 모델링할까?
- 한국형 맥락을 강화하려면 재난안전통신망/PS-LTE/이동형 기지국을 민군 겸용 resilience story로 넣을까?

## Recommended Hackathon Framing

> "이 시스템은 링크가 안정적일 때 더 많은 데이터를 보여주는 COP가 아니라, 링크가 무너질 때도 작전상 의미와 판단 근거를 잃지 않는 COP입니다. 통신 상태를 단순 장애가 아니라 C2 의사결정의 핵심 입력으로 다루고, PACE/DTN/local-first/semantic event를 결합해 고립 후 복귀까지 설명합니다."


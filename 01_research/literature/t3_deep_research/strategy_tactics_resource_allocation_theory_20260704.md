# Strategy, Tactics, And Resource Allocation Theory For Mission Continuity COP

- Version: `20260704_ks`
- Scope: theoretical foundations for D4D T3 `Mission Continuity COP`
- Research mode: public/open doctrine, academic literature, and operations research references
- Safety boundary: this note is for defensive resilience, C2 support, sustainment visibility, and decision-support design. It avoids actionable targeting, force employment recipes, offensive tactics, or classified/controlled procedures.

## Executive Synthesis

고립 부대 지원 솔루션을 이론적으로 잡으면 다음 구조가 가장 탄탄하다.

```text
Strategy: 목적/수단/방법/위험을 정렬한다.
Operational art: 전략 목적을 작전 설계와 단계로 바꾼다.
Mission command: 통신두절 상황에서도 하위 부대가 의도 안에서 판단한다.
C2 agility: 상황 변화에 따라 의사결정권/정보공유/상호작용 방식을 바꾼다.
Resource allocation: 제한된 전력, 통신, 센서, 보급, 시간, 분석 역량을 우선순위에 따라 배분한다.
Value of information: 모든 데이터가 아니라 의사결정을 바꾸는 정보를 먼저 보낸다.
Sustainment theory: 보급/전력/의료/정비가 작전 지속성과 자유행동을 만든다.
```

D4D 데모는 이 이론들을 다음 한 문장으로 번역하면 된다.

> 사령부는 고립 부대를 실시간으로 통제할 수 없지만, 지휘 의도와 자원 제약을 기준으로 예상 상황, 위험, 동기화 우선순위, 보급/전력 지속성을 관리할 수 있다.

## Theory Map

| Layer | Core Question | Main Frameworks | Product Translation |
| --- | --- | --- | --- |
| Strategy | 무엇을 달성해야 하는가? | Ends-Ways-Means-Risk, theory of victory, center of gravity | `Mission Objective`, `Risk Posture`, `Success Criteria` |
| Operational art | 전략을 어떤 작전 구조로 바꿀까? | operational approach, decisive points, lines of effort, phasing, culmination | `Branch Scenario`, `Decision Point`, `Phase Timeline` |
| Tactical execution | 현장에서는 무엇을 해야 하나? | mission command, commander's intent, MDMP/JOPP, COA comparison | `Intent Card`, `COA Cards`, `Local Decision Rules` |
| C2 architecture | 누가 판단하고 누가 무엇을 알아야 하나? | C2 Agility, C2 Approach Space, Power to the Edge, OODA | `Decision Rights`, `Info Sharing Mode`, `HQ/Edge Sync` |
| Resource allocation | 부족한 것을 어디에 먼저 쓸까? | operations research, optimization, MCDA/AHP, scheduling, portfolio choice | `Priority Engine`, `Resource Allocation Panel` |
| Information allocation | 어떤 정보를 먼저 보낼까? | value of information, quality of information, CCIR/PIR/FFIR, semantic comms | `Mission-Message Queue`, `Evidence Priority` |
| Sustainment | 얼마나 오래 버틸 수 있나? | ADP/JP sustainment, operational reach, freedom of action, endurance | `Readiness Forecast`, `Supply Burn-Down`, `Power Uptime` |

## 1. Strategy: Ends, Ways, Means, Risk

전략 이론의 가장 실용적인 형태는 Arthur Lykke식 `Ends-Ways-Means-Risk`다. 공개 Joint Planning 자료도 joint planning을 military ways and means, associated risk와 연결한다. 해커톤에서는 이것을 무기나 공격 계획이 아니라 `미션 목표-가능 수단-제약-위험` 정렬 문제로 바꿔 쓰면 된다.

### D4D Translation

| Strategy Item | Demo Field |
| --- | --- |
| Ends | `mission_goal`: maintain local maritime awareness, protect isolated unit continuity |
| Ways | `method`: local COP, semantic sync, PACE, prediction, rejoin audit |
| Means | `resources`: bandwidth, power, sensors, operators, cached data, supply |
| Risk | `risk_score`: stale data, power loss, supply exhaustion, unknown threat, link uncertainty |

### Design Implication

사령부 상황판은 단순히 "상태"가 아니라 "목표 대비 부족한 수단과 증가하는 위험"을 보여줘야 한다.

## 2. Operational Art: Linking Strategy To Tactical Reality

Operational art/design은 전략 목표를 실제 작전 설계로 바꾸는 사고 체계다. JP 3-0/5-0 계열은 operational art, campaign/contingency planning, joint functions를 다루며, 관련 공개 자료들은 end state, center of gravity, decisive points, lines of operation/effort, tempo, phasing, transitions, culmination 같은 요소를 반복적으로 제시한다.

D4D에서는 `center of gravity`를 공격 대상으로 쓰지 말고, **우리 시스템이 보호해야 하는 작전 지속성의 중심**으로 재해석하는 편이 안전하고 유용하다.

### D4D Translation

| Operational Art Concept | Safe Product Translation |
| --- | --- |
| End state | 고립 부대가 재연결 전까지 최소 COP와 임무 의도를 유지 |
| Decisive point | 통신 단절, 전력 임계치, 보급 임계치, 재연결 창 |
| Line of effort | comms continuity, sustainment continuity, local awareness, rejoin audit |
| Phasing | connected -> degraded -> intermittent -> isolated -> rejoin |
| Culmination | 전력/보급/정보 신선도 하락으로 더 이상 임무 지속 불가한 지점 |

## 3. Mission Command: Intent Survives Disconnection

Mission command는 고립 부대 주제의 핵심 이론이다. ADP 6-0 계열은 지휘관 의도, 임무형 명령, 하위 제대의 주도성, 분산 실행을 강조한다. 전술망이 끊기면 세부 통제가 아니라 의도와 판단 기준이 살아남아야 한다.

### D4D Translation

- `Commander Intent Card`: 목적, 우선순위, 금지조건, 위험 허용 범위, 유효기간.
- `Local Decision Rule`: 연결이 없을 때 현장 노드가 어떤 상태를 기록/보고/보류할지.
- `Authority Mode`: HQ-controlled, delegated, local-autonomous, rejoin-review.

### Product Principle

> 고립 상황의 UX는 "명령을 새로 받는 화면"이 아니라 "이미 받은 의도를 기준으로 현재 판단 가능한 범위를 보여주는 화면"이어야 한다.

## 4. Planning And COA Analysis: Options, Not One Prediction

MDMP, JOPP, AFPP, NATO AJP-5 모두 공통적으로 mission analysis, COA development, COA analysis/wargaming, COA comparison, approval/order production 흐름을 갖는다. 고립 부대 예상 상황도 역시 하나의 미래를 단정하면 안 되고, 여러 branch scenario를 비교해야 한다.

### D4D Translation

| Planning Concept | Demo Feature |
| --- | --- |
| Mission analysis | unit mission, constraints, last known COP, resource state |
| COA development | likely branch A/B/C after isolation |
| COA analysis/wargaming | expected route, power burn, supply risk, comm window probability |
| COA comparison | risk/utility matrix |
| Orders/update | intent packet or policy update bundle |

### Minimal COA Scoring Model

```text
COA score =
  mission_value
  - stale_data_risk
  - power_depletion_risk
  - supply_shortfall_risk
  - comms_uncertainty_risk
  + rejoin_probability
```

This should be presented as decision support, not automated command.

## 5. C2 Agility: Change The C2 Mode As Conditions Change

NATO SAS-085 and CCRP C2 literature define agility as the ability to cope with and exploit changes in circumstances. C2 Agility is especially useful for our demo because it treats C2 as a configurable approach, not a single hierarchy. The key dimensions commonly used in this literature include allocation of decision rights, interaction patterns, and distribution of information.

### D4D Translation

| C2 Mode | When | Decision Rights | Information Pattern |
| --- | --- | --- | --- |
| Centralized | connected, low uncertainty | HQ approves major decisions | rich COP, raw + semantic |
| Collaborative | degraded but stable | HQ and local node coordinate | semantic deltas + evidence |
| Delegated | intermittent | local node acts within intent | priority bundle + status |
| Local autonomous | isolated | local node acts and logs | local COP only |
| Rejoin | restored | HQ reviews/merges | audit + conflict resolution |

### Design Implication

The product should not simply display `network degraded`. It should recommend the corresponding C2 mode and show what changed: decision rights, payload tier, sync cadence, and review requirements.

## 6. OODA / Sensemaking: Decision Tempo Without False Certainty

The OODA loop is often simplified as observe-orient-decide-act. For the demo, the more useful framing is that isolation breaks the observation loop and increases orientation uncertainty. The solution should preserve orientation by keeping local context, intent, and evidence trails alive.

### D4D Translation

- Observe: last confirmed COP, local observations, sensor/evidence claims.
- Orient: confidence decay, branch scenario, source trust, sustainment risk.
- Decide: COA comparison, threshold alerts, human approval.
- Act: sync priority, resource allocation, intent update, rejoin audit.

## 7. Operations Research: Allocation Under Scarcity

Operations Research (OR) originated partly from wartime problems and is now used for scarce-resource allocation, equipment/process selection, deployment optimization, logistics, and decision support. For D4D, OR gives us a respectable theoretical base for "which message/resource/action should get priority?"

### Useful OR Families

| OR Method | Meaning | D4D Use |
| --- | --- | --- |
| Linear/integer optimization | allocate limited resources under constraints | bandwidth, power, analyst attention, supply priority |
| Knapsack/portfolio selection | choose highest-value items under capacity | which sync bundles to send during a 90-second link window |
| Scheduling | order tasks under time/resource constraints | recharge, sensor collection, sync, maintenance |
| Queueing theory | model waiting lines and service capacity | message backlog, analyst review queue, resupply queue |
| Search theory | allocate search effort under uncertainty | search/rescue or reconnect probability visualization |
| Decision analysis | choose under uncertainty using utility/risk | branch scenario comparison |
| MCDA/AHP | compare alternatives by weighted criteria | COA comparison dashboard |
| Robust optimization | choose plans that survive uncertainty | plan that works across weather/link/power variation |
| Markov decision process | sequential decisions under uncertainty | optional advanced future work |
| Simulation / wargaming | explore outcomes under assumptions | non-operational scenario replay for demo |

### Hackathon-Ready Allocation Problem

```text
Given:
  limited contact window = 90 seconds
  bandwidth = 20 kbps
  queued bundles = 18
  power remaining = 42%
  mission priority weights = intent packet

Choose:
  which bundles to send first
  what payload tier to use
  which local tasks to delay

Optimize:
  expected mission value delivered
  while limiting stale-data, power, and evidence-loss risk
```

This is safe, visual, and aligned with telecom/resource-allocation expertise.

## 8. Value And Quality Of Information

Value of Information asks whether additional information would change a decision enough to justify the cost of collecting/transmitting it. Quality of Information adds timeliness, reliability, accuracy, completeness, and relevance. In DDIL, this is more important than raw throughput.

### D4D Translation

Each message gets a score:

```text
message_priority =
  decision_impact
  * urgency
  * confidence
  * intent_relevance
  * freshness
  / transmission_cost
```

Potential fields:

- `decision_impact`: would this change HQ/local action?
- `freshness`: is the data still useful?
- `confidence`: does the evidence support it?
- `intent_relevance`: does it relate to the mission intent?
- `transmission_cost`: bytes/time/power required.
- `review_need`: does a human need to see it?

## 9. Sustainment: Operational Reach, Freedom Of Action, Endurance

Sustainment doctrine frames logistics, personnel services, and health support as what gives forces operational reach, freedom of action, and endurance. For isolated-unit support, this is one of the strongest arguments for the product: a unit can lose mission continuity through power, water, fuel, medical, repair, or communications resource depletion before it loses physical position.

### D4D Translation

| Sustainment Concept | Demo Field |
| --- | --- |
| Operational reach | how long/unit can remain useful from current location |
| Freedom of action | whether unit has enough comms/power/supply options |
| Endurance | time until critical resource crosses threshold |
| Anticipation | forecast burn-down and resupply/reconnect needs |
| Responsiveness | how fast priority support can be routed |
| Economy | use scarce bandwidth/power only where mission value is high |

## 10. Proposed Theoretical Architecture

```text
Intent Packet
  -> sets mission weights and risk tolerance

Local COP + NetworkState + ReadinessState
  -> estimates current confirmed/predicted state

Decision Criteria
  -> mission value, urgency, confidence, freshness, cost, risk

Priority Engine
  -> ranks messages, resources, COAs

C2 Mode Manager
  -> centralized / collaborative / delegated / local autonomous / rejoin

Mission Continuity Board
  -> shows what is confirmed, predicted, stale, missing, and queued
```

## Product Requirements Derived From Theory

| Requirement | Theory Source | Why It Matters |
| --- | --- | --- |
| Show `ends/ways/means/risk` for each isolated unit | strategy theory / JP 5-0 | Prevents status board from becoming disconnected from purpose |
| Show branch scenarios, not one future | operational art / COA analysis | Avoids false precision |
| Put commander intent in structured form | mission command | Enables local autonomy under isolation |
| Switch C2 mode with network state | C2 Agility | Makes degraded operations explicit |
| Prioritize messages by decision value | VOI/QoI / semantic comms | Reduces bandwidth waste |
| Track power/supply/readiness as COP layers | sustainment doctrine | Shows actual mission endurance |
| Keep evidence and provenance | decision analysis / COP theory | Supports review and trust |
| Compare predicted vs actual after rejoin | wargaming / learning loop | Improves future prediction |

## Source Index

### Doctrine / Military Theory

| Priority | Source | URL | Use |
| --- | --- | --- | --- |
| P0 | JP 5-0 Joint Planning | https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/ | Ways/means/risk, joint planning, campaign/contingency planning |
| P0 | JP 5-0 PDF mirror from Executive Services Directorate | https://www.esd.whs.mil/Portals/54/Documents/FOID/Reading%20Room/Joint_Staff/18-F-1152_JP_5-0_Joint_Planning_2020.pdf | Public accessible PDF for planning vocabulary |
| P0 | JP 3-0 Joint Campaigns and Operations page | https://www.jcs.mil/doctrine/joint-doctrine-pubs/3-0-operations-series/ | Operational art, joint functions, campaign operations |
| P0 | JP 3-0 PDF mirror | https://dnnlgwick.blob.core.windows.net/portals/14/Courses/Maritime%20Staff%20Operators%20Course/9.%20JP%203-0%20-%20Joint%20Campaigns%20and%20Operations%20Web%20Page%20Excerpt.pdf | Joint campaign/operations reference |
| P0 | ADP 6-0 Mission Command overview | https://books.apple.com/us/book/army-doctrine-publication-adp-6-0-mission-command-command/id1484228585 | Mission command, C2, command art/science |
| P0 | War Room on ADP 6-0 | https://warroom.armywarcollege.edu/articles/new-doctrine-mission-command/ | Mission command as decentralized decision/execution |
| P0 | ADP 4-0 Sustainment public PDF | https://www.globalsecurity.org/military/library/policy/army/adp/4-0/adp4_0.pdf | Sustainment, operational reach, freedom of action, endurance |
| P0 | MCDP 1 Warfighting | https://www.marines.mil/portals/1/publications/mcdp%201%20warfighting.pdf | Friction, uncertainty, fluidity, human factors |
| P1 | Center of Gravity discussion, Army University Press | https://www.armyupress.army.mil/Journals/Military-Review/Online-Exclusive/2017-Online-Exclusive-Articles/The-Center-of-Gravity/ | COG concept and caution |
| P1 | Defining Centers of Gravity | https://www.armyupress.army.mil/Portals/7/military-review/Archives/English/MilitaryReview_20070831_art012.pdf | COG, decisive point distinction |
| P1 | Operational Art and Tactics of the U.S. Army | https://www.nids.mod.go.jp/english/publication/briefing/pdf/2021/briefing_e202106.pdf | Operational art elements |
| P1 | AFDP 5-0 Planning | https://www.doctrine.af.mil/Portals/61/documents/AFDP_5-0/AFDP5-0Planning.pdf | Planning steps, COA analysis/wargaming |
| P1 | Army MDMP handbook | https://api.army.mil/e2/c/downloads/2023/11/17/f7177a3c/23-07-594-military-decision-making-process-nov-23-public.pdf | Mission analysis, COA analysis, wargaming |
| P1 | NATO AJP-5 Allied Joint Doctrine for Operational-Level Planning | https://www.coemed.org/files/stanags/01_AJP/AJP-5_EDA_V2_E_2526.pdf | Allied planning and COA analysis |

### C2 / Decision Theory

| Priority | Source | URL | Use |
| --- | --- | --- | --- |
| P0 | NATO SAS-085 Final Report on C2 Agility | https://dodccrp.org/sas-085/sas-085_report_final.pdf | C2 agility theory |
| P0 | NATO SAS-085 overview | https://dodccrp.org/files/SAS-085_Overview.pdf | Short C2 agility explanation |
| P0 | Understanding Command and Control | https://www.dodccrp.org/files/Alberts_UC2.pdf | C2 approach, sensemaking, value view |
| P0 | Power to the Edge | https://edocs.nps.edu/dodpubs/org/CCRP/Alberts_Power.pdf | Edge-enabled C2 concepts |
| P1 | C2 by Design handbook | https://dodccrp-testorg.squarespace.com/s/c2bydesign.pdf | Allocating decision rights and adapting C2 approach |
| P1 | C2 Agility: Next Steps | https://publications.sto.nato.int/publications/STO%20Technical%20Reports/STO-TR-SAS-104/%24%24TR-SAS-104-ALL.pdf | Practice-oriented C2 agility cases |
| P1 | NATO C2 resilience in contested environments | https://www.japcc.org/essays/nato-command-and-control-resilience-in-contested-environments/ | C2 resilience and agility under contestation |
| P1 | The Future of the Command Post | https://c2coe.org/download/the-future-of-the-command-post-part-1/ | Future operational command post design |

### Operations Research / Resource Allocation

| Priority | Source | URL | Use |
| --- | --- | --- | --- |
| P0 | NPS Operations Analysis overview | https://nps.edu/web/or/operations-analysis-360 | OR for scarce resource allocation and deployment |
| P0 | Fifty Years of Operations Research in Defense | https://www.sciencedirect.com/science/article/pii/S0377221723009694 | Modern defense OR survey |
| P0 | NPS OR publications | https://nps.edu/web/or/publications | Search theory, logistics, OR references |
| P0 | National Academies, OR and Intelligence Analysis | https://www.nationalacademies.org/read/13062/chapter/5 | Decision analysis and value of information |
| P1 | Resource allocation in military operations, FFI | https://www.ffi.no/en/publications-archive/resource-allocation-in-military-operations-optimization-using-a-genetic-algorithm | Military operation scheduling/resource allocation as optimization |
| P1 | Theory of Search, USCG NAVCEN | https://navcen.uscg.gov/sites/default/files/pdf/Theory_of_Search.pdf | Search planning under uncertainty |
| P1 | Search Theory mathematical overview | https://www.metsci.com/wp-content/uploads/2019/08/Search-Theory-A-Mathematical-Theory-for-Finding-Lost-Objects.pdf | Search allocation background |
| P1 | Present State of Lanchester Theory | https://pubsonline.informs.org/doi/10.1287/opre.12.2.344 | Combat modeling history and limitations |
| P1 | Military Operations Research book | https://link.springer.com/content/pdf/10.1007/978-1-4615-6275-7.pdf | Quantitative decision-making in military context |
| P1 | Theories and Methods of Military Operations Research in Big Data Era | https://www.atlantis-press.com/article/55912662.pdf | Game theory, programming, queuing, Lanchester overview |
| P1 | Criteria and tactical decision-making | https://sciendo.com/pdf/10.2478/raft-2021-0024 | Criteria selection for tactical alternatives |
| P2 | MCDA applied in military problems | https://www.researchgate.net/publication/359176329_Bibliometric_studies_on_Multi-Criteria_Decision_Analysis_MCDA_Methods_Applied_in_Military_Problems | Military MCDA bibliography |
| P2 | AHP method overview | https://pmc.ncbi.nlm.nih.gov/articles/PMC4690361/ | AHP as multi-criteria method |

### Sustainment / Contested Logistics

| Priority | Source | URL | Use |
| --- | --- | --- | --- |
| P0 | ADP 4-0 Sustainment | https://www.globalsecurity.org/military/library/policy/army/adp/4-0/adp4_0.pdf | Operational reach, freedom of action, endurance |
| P0 | JP 4-0 Joint Logistics | https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/4-0-Logistics-Series/ | Joint logistics doctrine source page |
| P1 | RAND on implications of fighting in Ukraine | https://www.rand.org/content/dam/rand/pubs/research_reports/RRA3100/RRA3141-2/RAND_RRA3141-2.pdf | Contested logistics and dispersed posture |
| P1 | U.S. Army tactical energy in Ukraine | https://api.army.mil/e2/c/downloads/2026/03/30/c260713f/no-26-1116-powering-the-front-tactical-energy-delivery-and-management-in-the-ukraine-war.pdf | Energy as tactical resource |
| P1 | RAND Europe wartime innovation and adaptation | https://www.rand.org/randeurope/research/projects/2025/innovation-adaptation-at-war-cm.html | Innovation/adaptation as resource and organization issue |

## Recommended Reading Order

1. JP 5-0 / JP 3-0 executive summaries for strategy and operational art vocabulary.
2. ADP 6-0 / Mission Command explainer for intent-based decentralized decision-making.
3. NATO SAS-085 C2 Agility overview for changing C2 modes under degraded conditions.
4. NPS Operations Analysis overview and FFI resource allocation report for OR framing.
5. National Academies value-of-information chapter for message priority logic.
6. ADP 4-0 / JP 4-0 for sustainment/readiness language.
7. MCDP 1 Warfighting for friction, uncertainty, and why prediction must show uncertainty.

## Recommended D4D Framing

> Mission Continuity COP applies strategy, C2 agility, and operations research to DDIL environments. It helps commanders align mission intent with scarce resources, switch C2 modes as connectivity degrades, prioritize information by decision value, and forecast how long isolated units can remain effective.


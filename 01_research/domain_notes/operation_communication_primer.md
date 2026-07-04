# Operation Communication Primer for D4D T3 COP

- Date: 2026-07-04 KST
- Scope: public, unclassified doctrine-level concepts only
- Purpose: explain how "operations" are commonly directed, updated, reported, and visualized so the D4D COP demo does not feel like a generic map dashboard.

## 1. Safety Boundary

This note does not describe classified command systems, real unit procedures, real tactical nets, weapons employment details, or rules of engagement. It summarizes public doctrine-level concepts to help a non-specialist understand why the demo is structured around:

- command intent;
- operation orders;
- situation reports;
- event reports;
- common operational picture updates;
- degraded-network prioritization.

## 2. The Core Idea

In simple terms, military operations are not usually "one message goes out and everyone just follows it."

They are closer to a continuous loop:

```text
higher guidance / mission
  -> planning
  -> warning order
  -> operation order
  -> execution
  -> reports and COP updates
  -> decisions / adjustments
  -> fragmentary order or new order
  -> continued assessment
```

The important point for our project:

> A command post does not only transmit raw data. It turns changing facts into shared understanding, decisions, and updates.

That is exactly why a semantic COP demo makes sense. It is not just showing vessel dots; it is turning messy observations into decision-relevant operational messages.

## 3. Key Terms in Plain Korean

| Term | Plain explanation | Why it matters to our demo |
| --- | --- | --- |
| C2, Command and Control | 지휘관이 권한과 방향을 행사하고, 참모/시스템이 이를 실행 가능하게 만드는 체계 | 우리 데모의 큰 주제 |
| Command Post | 작전 정보를 모으고, 판단하고, 지시/보고를 관리하는 지휘소 | 데모 화면의 상황판 컨셉 |
| COP, Common Operational Picture | 여러 출처의 상황을 공통으로 이해할 수 있게 만든 작전상황도 | 중앙 지도 |
| Commander Intent | 세부 지시가 끊겨도 하급 부대가 무엇을 달성해야 하는지 알게 하는 지휘관 의도 | 저대역/통신두절 상황에서 핵심 |
| CCIR | 지휘관이 결정을 내리기 위해 반드시 알아야 하는 중요 정보 요구 | priority score의 군사용 해석 |
| PIR / FFIR / EEFI | 적/위협 관련 정보, 아군 관련 정보, 보호해야 할 아군 정보 | 이벤트 분류와 안전 필터 |
| WARNO / WARNORD | 곧 작전명령이 올 수 있으니 준비하라는 경고명령 | early warning / heads-up |
| OPORD | 작전 수행을 위한 본 명령 | 전체 작전 기준선 |
| FRAGO / FRAGORD | 기존 작전명령 중 바뀐 부분만 빠르게 전달하는 단편명령 | 상황 변화에 따른 update |
| SITREP | 현재 부대/상황 상태를 정리해 보고하는 상황보고 | 정기/주기적 업데이트 |
| SPOTREP | 즉시 알릴 가치가 있는 사건/관측을 짧게 보고 | semantic event와 가장 유사 |
| Running Estimate | 참모들이 자기 분야의 현재 판단을 계속 업데이트하는 추정/판단 자료 | evidence bundle + confidence/trust |
| Battle Rhythm | 회의, 보고, 결심, 업데이트가 언제 돌아가는지 정한 반복 주기 | command board의 시간축 |

## 4. How an Operation Is Typically Communicated

### 4.1 Before Execution: Guidance and Orders

At a high level, planning begins from a mission or guidance from a higher echelon. Staffs analyze the situation, risks, available resources, constraints, and the commander's desired end state.

Common outputs:

| Output | Meaning | Demo analogy |
| --- | --- | --- |
| Planning guidance | 어떤 문제를 풀어야 하는지 방향을 주는 초기 지침 | scenario definition |
| WARNORD | 하급 조직이 미리 준비하게 하는 heads-up | early warning card |
| OPORD | 상황, 임무, 실행, 지원, 지휘/통신을 담은 기준 명령 | baseline operational plan |
| Annex / overlay | 세부 기능별 부속 문서나 지도 layer | map layers / evidence layers |

The classic public order structure is often explained as five major parts:

```text
1. Situation
2. Mission
3. Execution
4. Sustainment
5. Command and Signal
```

For our demo, this means the situation board should not only show "what happened." It should show:

- where it happened;
- why it matters;
- what mission/effect it affects;
- what action or decision may be needed;
- what evidence supports the claim;
- whether the message can survive the current network.

### 4.2 During Execution: Reports and Updates

Once execution starts, information moves upward, downward, and sideways:

| Direction | Examples | Purpose |
| --- | --- | --- |
| Higher to lower | OPORD, FRAGO, priorities, constraints | direct action and synchronize effort |
| Lower to higher | SITREP, SPOTREP, LOGSTAT, requests | update commander and staff |
| Lateral | coordination messages, handover, shared COP updates | synchronize adjacent/supporting units |
| Staff internal | running estimates, decision support, assessment updates | help the commander decide |

This is where our T3 concept becomes relevant:

- in a good network, raw feeds and full evidence can move;
- in a degraded network, only the most decision-relevant reports should move;
- in a disconnected network, local logs queue until store-forward sync is possible.

### 4.3 After a Change: FRAGO or Decision Update

If the situation changes, the organization often does not rewrite the entire order. It can issue a fragmentary order that changes only the necessary pieces.

For our demo:

- a new `AIS_GAP` or `SAR_WITHOUT_AIS` event is like a report that may trigger attention;
- a `PRIORITY_BRIEF` is like a compact staff update for a commander;
- a network-mode change determines whether the update is sent, deferred, dropped, or kept local.

## 5. Message Types Relevant to Our Demo

| Message family | What it means | Direct mapping in our demo |
| --- | --- | --- |
| Warning / early notice | Something may require preparation | `OSINT_INCIDENT`, `WEATHER_HAZARD`, early warning card |
| Order / direction | What must be done and by whom | not implemented as real orders; represented as recommended action |
| Fragmentary update | Change to previous plan/order | event update under degraded network |
| Situation report | Periodic status | COP summary and event list |
| Spot report | Immediate event report | one semantic event |
| Intelligence summary | assessed threat/context | evidence bundle and grounded briefing |
| Logistics status | sustainment/readiness | future T3 sustainment extension |
| Request for information/support | asks higher/supporting org for help | future action workflow |
| Network status | whether the C2 link can carry data | network mode and routing decision |

## 6. Why This Matters for the D4D Demo

The current demo should be described as:

> A command-post aid that converts raw observations into report-like semantic events, preserves evidence, and decides what can still be transmitted when the network degrades.

It is not:

- a real command system;
- a targeting tool;
- a replacement for commander judgment;
- a tactical radio emulator;
- a classifier that declares real vessels hostile.

## 7. What Data We Should Add Next

To make the demo feel more operationally grounded, add a small reference layer of "operation communication objects."

Recommended objects:

| Object | Purpose | Example fields |
| --- | --- | --- |
| `CommandIntent` | why this operation exists | purpose, key tasks, end state, constraints |
| `CCIR` | what information matters most | question, category, trigger condition, priority |
| `OperationalMessage` | generic message envelope | message type, precedence, sender, receiver, time, body refs |
| `SpotReportLikeEvent` | immediate event report | who/what/where/when/why, confidence, evidence refs |
| `SituationReport` | periodic status | area status, friendly status, notable changes, requests |
| `FragmentaryUpdate` | change to existing plan | changed item, effective time, affected units/entities |
| `NetworkStatus` | message survivability | bandwidth, latency, loss, mode, routing policy |
| `DecisionPoint` | commander decision trigger | condition, options, required data, deadline |

These do not need to be real military data. For hackathon safety, they should be synthetic and mapped to public doctrine concepts.

## 8. How to Explain It in the Pitch

Use this phrasing:

> In a command post, data is useful only if it changes shared understanding or supports a decision. Public doctrine describes operations as a continuous cycle of planning, preparing, executing, and assessing. Orders set intent and direction; reports update the situation; the COP keeps everyone aligned. Our system focuses on the moment when the network degrades: it decides which report-like semantic events still need to reach the command board.

## 9. Public References

- U.S. Army ADP 5-0, The Operations Process: https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN18126-ADP_5-0-000-WEB-3.pdf
- U.S. Army FM 6-0, Commander and Staff Organization and Operations: https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN35404-FM_6-0-000-WEB-1.pdf
- U.S. Army FM 6-99, U.S. Army Report and Message Formats, public reference copy: https://digitalcommons.unl.edu/usarmyfieldmanuals/51/
- CJCSM 3130.02, Joint Planning and Execution Policies and Procedures: https://www.jcs.mil/Portals/36/Documents/Library/Manuals/CJCSM%203130.02.pdf
- Marine Corps MCRP 2-10A.7, Reconnaissance Reports Guide: https://www.marines.mil/Portals/1/Publications/MCRP%202-10A.7%20GN.pdf

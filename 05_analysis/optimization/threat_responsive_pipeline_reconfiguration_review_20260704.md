# Threat-Responsive Pipeline Reconfiguration Review

Date: 2026-07-04 KST

Question:

> 전시 상황에서 적 침투 또는 위협 예측이 발생하면 공정 파이프라인, 물자 이동, 보급로 변경을 즉시 의사결정에 반영할 수 있는 알고리즘인가?

Short answer:

The current optimization direction is correct, but it must be upgraded from a static scenario planner into an event-driven resilient reconfiguration system. The current model already has the right primitives: scenarios, route risk, factory availability, robust/stochastic optimization, CVaR, and rolling-horizon reoptimization. It is not yet sufficient for an intelligent adversary unless we add interdiction-aware stress testing and plan-change constraints.

## 1. Current Fit Assessment

| Requirement | Current model status | Judgment |
| --- | --- | --- |
| Predicted threat changes factory selection | Present in demo as synthetic threat corridors and risk penalties | Directionally correct |
| Predicted threat changes route selection | Present through route risk, rerouted status, road-cost fields | Directionally correct |
| Material/resource pipeline changes | Present through resource-to-factory routes | Directionally correct |
| Multi-period reaction over time | Described, not implemented | Needs upgrade |
| Existing orders and in-transit shipments frozen | Described only in rolling-horizon pseudocode | Needs explicit constraints |
| Intelligent adversary / interdiction | Mentioned only as route interdiction scenario | Needs DAD/DAO or interdiction stress test |
| Rapid real-time decision loop | Not formalized enough | Needs event-driven architecture |
| Avoid excessive plan churn | Mentioned as benefit threshold | Needs switching-cost constraints |
| Recovery after disruption | Not formalized | Needs recovery-state model |

Verdict:

The base model is appropriate, but the operational algorithm should be framed as:

```text
Event-Driven Rolling-Horizon Robust Reconfiguration
```

not merely:

```text
static min-cost supply plan
```

## 2. Research Basis

| D4D need | Research basis | Relevance |
| --- | --- | --- |
| Intelligent adversary can interdict nodes/routes | Alderson, Brown, Carlyle, Wood describe defender-attacker-defender models for infrastructure defense, including transportation-network defense and decomposition algorithms: [NPS/INFORMS paper](https://calhoun.nps.edu/server/api/core/bitstreams/cd3dda33-20ca-4dda-bb1f-aa01228d8063/content). | Use for stress-testing which factory/route loss would damage drone output most. |
| Operator must respond after attack/damage | Brown and Craparo formulate defender-attacker-operator optimization where attacker maximizes damage and operator minimizes effects after attack: [DAO optimization paper](https://faculty.nps.edu/gbrown/docs/Brown-ImplementingDefenderAttackerOperatorDAO-2023.pdf). | Directly maps to “enemy acts, logistics operator replans.” |
| Network interdiction is a formal class of sequential games | Song's Encyclopedia of Optimization chapter summarizes sequential network interdiction games, max-flow interdiction, bilevel optimization, and decomposition: [Network Interdiction: Models and Methods](https://link.springer.com/rwe/10.1007/978-3-030-54621-2_731-1). | Use for critical-route/factory vulnerability analysis, not enemy tactical guidance. |
| Supply chains need dynamic reconfiguration under cascading disruption | Brusset et al. propose an optimal-control model for dynamic supply-chain reconfiguration and ripple-effect analysis: [International Journal of Production Economics, 2023](https://ideas.repec.org/a/eee/proeco/v263y2023ics0925527323001676.html). | Use for repeated reconfiguration as disruptions propagate across suppliers. |
| Disruption literature supports resilience and future research agenda | Katsaliaki, Galetsi, Kumar review supply-chain disruptions and resilience and identify gaps as disruption frequency/impact increases: [Annals of Operations Research](https://ideas.repec.org/a/spr/annopr/v319y2022i1d10.1007_s10479-020-03912-1.html). | Supports resilience framing and need for monitoring/recovery planning. |
| Facility disruptions can be full shutdown or reduced capacity | A hybrid robust-stochastic supply-chain model explicitly handles facility shutdown or reduced capacity and supply/demand interruptions: [Transportation Research Part B, 2017](https://www.sciencedirect.com/science/article/abs/pii/S0191261516306567). | Maps to factory partially degraded vs unavailable. |
| Recovery speed and duration can be decision variables | A risk-averse two-stage stochastic model studies investment to adjust recovery speed/duration of disrupted production capacity: [Transportation Research Part E, 2021](https://ideas.repec.org/a/eee/transe/v152y2021ics136655452100154x.html). | Supports modeling repair/recovery effort and temporary workarounds. |
| Robust optimization controls conservatism under uncertain capacity/time | Bertsimas-Sim robust optimization controls the price of robustness: [Operations Research, 2004](https://ideas.repec.org/a/inm/oropre/v52y2004i1p35-53.html). | Use for uncertain route risk, factory capacity, and public-data confidence. |

## 3. Correct Threat-Responsive Model

The threat-responsive model needs four layers:

1. **Monitor:** ingest threat alerts, route disruptions, factory verification updates, energy/grid status, inventory and in-transit status.
2. **Belief update:** convert events into probability and availability changes.
3. **Reoptimization:** solve a rolling-horizon recourse problem with frozen commitments and switching costs.
4. **Stress test:** run interdiction/robust scenarios to identify critical nodes and recommend redundancy.

The model should not encode detailed enemy tactics. It should treat threat inputs as probabilistic risk fields over factories, resource nodes, hubs, and routes.

## 4. Event-to-Optimization Translation

Let an event \(o_t\) arrive at time \(t\):

- suspicious movement near industrial cluster
- route disruption
- port stress
- grid outage risk
- verified factory capacity change
- resource shortage

Convert it into model parameters:

\[
h_{n,t} = P(\text{node }n\text{ degraded} \mid o_{1:t})
\]

\[
h_{e,t} = P(\text{route }e\text{ degraded} \mid o_{1:t})
\]

Then update:

\[
a_{n,t,s} = 1 - \rho_n h_{n,t,s}
\]

\[
a_{e,t,s} = 1 - \rho_e h_{e,t,s}
\]

\[
routecap_{e,t,s} = \bar{routecap}_{e,t}(1-\lambda_e h_{e,t,s})
\]

\[
riskcost_{e,t,s} = \bar{riskcost}_{e,t} + \beta_e h_{e,t,s}
\]

where:

- \(h\): threat probability or disruption belief
- \(a\): availability multiplier
- \(\rho,\lambda,\beta\): calibrated sensitivity

This makes threat prediction directly affect:

- factory capacity
- route capacity
- route cost
- risk penalty
- hub preference
- supplier ranking

## 5. Rolling-Horizon Reconfiguration MILP

At decision time \(\tau\), solve over horizon \(t=\tau,\dots,\tau+H\).

Objective:

\[
\min
\text{shortage penalty}
+ \text{lateness penalty}
+ \text{production cost}
+ \text{logistics cost}
+ \text{risk penalty}
+ \text{switching cost}
+ \text{recovery cost}
\]

The missing term from the current design is switching cost:

\[
C^{switch}
= \sum_{f,i,t} \kappa^x_{f,i}|x_{f,i,t}^{new}-x_{f,i,t}^{old}|
+ \sum_{e,i,t} \kappa^z_{e,i}|z_{e,i,t}^{new}-z_{e,i,t}^{old}|
+ \sum_{h,k,t} \kappa^q_{h,k}|q_{h,k,t}^{new}-q_{h,k,t}^{old}|
\]

Why this matters:

- A plan that changes every time a threat score moves by 5% is not operationally usable.
- Switching suppliers has verification, contracting, tooling, packaging, labor, and transport overhead.
- In-transit shipments cannot be instantly reassigned.

Linearization:

\[
d^x_{f,i,t} \ge x_{f,i,t}^{new}-x_{f,i,t}^{old}
\]

\[
d^x_{f,i,t} \ge x_{f,i,t}^{old}-x_{f,i,t}^{new}
\]

\[
C^{switch}_x = \sum \kappa^x d^x
\]

Apply the same pattern for route and hub plan changes.

## 6. Frozen Commitments and In-Transit Constraints

Orders already issued:

\[
x_{f,i,t}^{new} \ge x_{f,i,t}^{committed}
\quad \forall t \le freezeWindow
\]

Shipments already loaded:

\[
z_{e,i,t}^{new} = z_{e,i,t}^{intransit}
\quad \forall e,i,t \text{ already dispatched}
\]

If a route becomes unsafe after dispatch:

\[
z_{e,i,t}^{new} \le z_{e,i,t}^{intransit} + z_{e,i,t}^{reroutable}
\]

This distinguishes:

- future plans that can change
- committed orders that are expensive to change
- in-transit flows that are physically constrained

## 7. Interdiction-Aware Stress Test

For operational decision support, run a safe vulnerability model:

\[
\max_{A \subseteq N \cup E, |A| \le B}
\min_{x,z,q}
Loss(x,z,q \mid A)
\]

Interpretation:

- The outer maximization is not used to guide attacks.
- It identifies which factories/routes are single points of failure.
- The inner minimization is the operator's best recovery plan after those losses.

Output:

- top critical factories by output loss if unavailable
- top critical routes by output loss if unavailable
- redundancy gap by part family
- recommended pre-activation or pre-positioning

This should be shown as a resilience stress test, not as enemy targeting logic.

## 8. Reconfiguration Trigger Policy

Do not automatically change the plan for every alert. Use a decision threshold:

\[
Benefit(Replan) - Cost(Switch) - Risk(NewPlan) \ge \theta
\]

where:

- `Benefit(Replan)` = reduced shortage/lateness/risk under updated threat belief
- `Cost(Switch)` = operational disruption from changing suppliers/routes
- `Risk(NewPlan)` = residual risk and data uncertainty
- \(\theta\) = command approval threshold

Recommended trigger levels:

| Level | Condition | Action |
| --- | --- | --- |
| Watch | risk score changes, no bottleneck impact | update dashboard only |
| Warn | expected bottleneck or route exposure increases | prepare alternate plan, do not execute |
| Replan | feasible output drops or critical route/factory crosses threshold | issue recommended reconfiguration |
| Emergency | route/factory unavailable or deadline infeasible | execute pre-approved fallback plan |

## 9. How to Upgrade Current D4D Implementation

### v0.5: Event-Responsive Recourse

Add data objects:

- `ThreatEvent`
- `NodeRiskState`
- `RouteRiskState`
- `FrozenCommitment`
- `InTransitShipment`
- `PlanDelta`
- `ReconfigurationRun`

Add route/factory fields:

- `availability_multiplier`
- `risk_probability`
- `risk_cost_multiplier`
- `recovery_time_days`
- `switching_cost_krw`
- `freeze_until_day`

Algorithm:

1. Receive event.
2. Update node/route risk states.
3. Recompute min-cost flow with frozen commitments.
4. Compare against current plan.
5. Display plan delta and decision threshold.

### v0.6: Scenario Robust Plan

Use scenario set:

- baseline
- west industrial cluster degradation
- southern port disruption
- grid stress
- rare-earth/magnet feedstock shortage
- battery material shortage
- road corridor closure

For each scenario:

- solve recourse plan
- compute output preserved
- compute cost of robustness
- compute regret vs baseline plan

### v0.7: Interdiction/Fortification Stress Test

Run offline or on demand:

- remove top \(B\) nodes/routes by adversarial stress test
- solve operator recourse
- identify single points of failure
- recommend redundancy:
  - alternate supplier verification
  - alternate assembly hub
  - material pre-positioning
  - route diversification
  - backup energy source

## 10. Final Technical Judgment

The existing algorithm family is appropriate if framed correctly:

```text
MILP / min-cost flow / robust-stochastic recourse / rolling-horizon reoptimization
```

It is incomplete if framed as:

```text
static supplier ranking with one threat penalty
```

The project objective requires the former. The next implementation should therefore prioritize:

1. event-to-risk-state conversion
2. rolling-horizon recourse
3. switching-cost and frozen-commitment constraints
4. interdiction-aware stress testing
5. scenario regret and cost-of-robustness display

This keeps the model aligned with the operational intent: when threat assumptions change, the system can immediately show which factory, material source, route, and assembly hub decisions should change, and what the cost/risk tradeoff is.

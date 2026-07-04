# Recent Battlefield Scenarios For D4D T3

- Last checked: 2026-07-04 KST
- Purpose: turn current-war OSINT into hackathon-ready, non-classified, defensible scenarios.
- Preferred theme: C2/COP resilience under degraded communications.

## Scenario Ranking

| Rank | Scenario | Theater | Why meaningful | Data availability | Hackathon fit |
|---:|---|---|---|---|---|
| 1 | Rail and energy infrastructure strike resilience COP | Ukraine | modern wars increasingly pressure logistics, power, and transport rather than only front lines | high | strongest for KT/network + T3 |
| 2 | Strait of Hormuz maritime disruption COP | Israel-Iran / Gulf | chokepoint crisis, vessel incidents, GNSS interference, dark activity, oil/shipping impact | medium-high | strongest T3/MDA fit |
| 3 | Air-defense saturation and warning prioritization | Ukraine or Israel-Iran | missile/UAV waves overwhelm sensors and decision cycles | high for Ukraine, medium for Israel-Iran | strong demo, avoid tactical intercept optimization |
| 4 | Black Sea maritime corridor risk monitor | Ukraine / Black Sea | AIS, port strikes, merchant shipping, sanctions, dark-vessel behavior | medium | direct MDA extension |
| 5 | Civilian-harm-aware incident fusion copilot | Israel-Iran / Ukraine | supports responsible development and avoids purely kinetic framing | medium | strong ethics, T2/T3 hybrid |

## 1. Rail And Energy Infrastructure Strike Resilience COP

**Problem statement**

When missile/UAV strikes, air raid alerts, fire detections, and infrastructure reports arrive simultaneously, local operators and commanders need a common picture of which rail, energy, bridge, water, and hospital assets are likely affected, what evidence supports the assessment, and which messages should be sent first over degraded links.

**What the demo should show**

- A map of oblasts / infrastructure nodes.
- Incoming events from ACLED/GDELT/missile datasets/FIRMS.
- OSM infrastructure graph: rail stations, substations, power plants, bridges, hospitals.
- A prioritization engine that compresses "raw data" into a few semantic alert cards.
- Network modes: full sync, delta sync, semantic summary, store-forward, local-only.
- Analyst drawer: each alert has evidence refs, confidence, source disagreement, and recommended non-kinetic actions.

**Data to use first**

- ACLED Ukraine Conflict Monitor.
- GDELT event/news queries.
- Massive Missile Attacks on Ukraine dataset.
- CSIS Russian Firepower Strike Tracker.
- alerts.in.ua active/historical alerts if token approved.
- NASA FIRMS hotspots.
- OSM rail/power/hospital/bridge layers.
- HDX Ukraine admin boundaries.
- KSE/UNOSAT/OHCHR as impact context.

**Why it is good for you**

This does not require deep weapons engineering. It lets you explain the system as "Waze + emergency room triage + military situation board": when the network is bad, the system decides which updates are most important and preserves the evidence trail.

## 2. Strait Of Hormuz Maritime Disruption COP

**Problem statement**

During a Gulf crisis, maritime incidents, vessel dark activity, GNSS interference, port advisories, oil price shocks, and military warnings can arrive from different sources. Operators need a maritime COP that fuses advisories, AIS movement, incident reports, and satellite/fire proxies into risk zones and ship-priority alerts.

**What the demo should show**

- Strait of Hormuz / Gulf of Oman map.
- UKMTO/JMIC/MARAD incident cards.
- Vessel traffic density or mock AIS tracks.
- Dark-activity or delayed-AIS warnings.
- FIRMS/Sentinel evidence proxy for fires or port damage.
- Semantic network compression for ship-to-shore communications.

**Data to use first**

- UKMTO recent incidents.
- JMIC advisory PDFs via UKMTO.
- MARAD MSCI alerts.
- MarineTraffic/AISStream/Global Fishing Watch if license allows.
- NASA FIRMS for thermal anomalies.
- Copernicus Sentinel-1/2 for port and vessel-area imagery.
- EIA/FRED oil indicators for strategic impact.
- ACLED/GDELT for regional conflict events.

**Why it is good for D4D**

This is closest to T3/T4 MDA. It is also visually compelling: vessels, chokepoints, advisories, and degraded communications make a very clear demo.

**Main risk**

AIS and commercial maritime data can be license-restricted. For the hackathon, use mock vessel tracks first, then replace only the metadata layer with permitted live/public feeds.

## 3. Air-Defense Saturation And Warning Prioritization

**Problem statement**

Mass UAV/missile waves create too many events for human operators and communication links. A system should group wave reports, identify likely affected regions, track warning duration, and prioritize warnings to critical infrastructure without suggesting intercept tactics.

**What the demo should show**

- Timeline of attack waves.
- Alert-duration by region.
- "What changed since last sync?" summary.
- Infrastructure exposure score.
- Short command briefing generated from evidence.

**Data to use first**

- Ukraine: Massive Missile Attacks dataset, CSIS tracker, MDAA tracker, alerts.in.ua, ISIS Shahed reports.
- Israel-Iran: ACLED, Airwars, Iran-Israel OSINT dataset as seed only, GDELT, CTP/ISW.
- FIRMS and Sentinel for post-event corroboration.

**Safe boundary**

Focus on warning, resilience, and impact assessment. Do not model air-defense placement, interceptor allocation, or strike path optimization.

## 4. Black Sea Maritime Corridor Risk Monitor

**Problem statement**

Ports, grain routes, sanctioned tankers, AIS gaps, and drone/USV attacks create a dynamic maritime risk picture. A COP should help analysts understand which routes or ports are becoming riskier and why.

**Data to use first**

- ACLED Ukraine/Black Sea events.
- MarineTraffic/AISStream/Global Fishing Watch if permitted.
- Gard/Skuld maritime security updates.
- UN Trade and Development AIS Black Sea deck for methods.
- FIRMS/Sentinel for port fire/damage proxies.
- OSM ports and maritime infrastructure.

**Demo angle**

Show "route confidence" and "evidence trace" rather than predicting ship attacks.

## 5. Civilian-Harm-Aware Incident Fusion Copilot

**Problem statement**

Public war data often mixes claims, counterclaims, civilian harm, and infrastructure damage. A responsible intelligence copilot should keep uncertainty visible, protect sensitive identities, and separate verified evidence from claims.

**Data to use first**

- Airwars methodology and incident research.
- ACLED events.
- OHCHR / ReliefWeb / HDX reports.
- GDELT source links.
- FIRMS/Sentinel as physical evidence proxies.

**Demo angle**

For each incident, display:

- What happened.
- What sources say.
- What is uncertain.
- Civilian/infrastructure risk.
- What data must not be shown publicly.

## Recommended Hackathon Product Direction

Build **Resilient Operational Picture for Infrastructure and Maritime Disruption**:

1. Start with Ukraine rail/energy as the data-rich MVP.
2. Reuse the same architecture for Hormuz maritime disruption as a second "theater pack."
3. Keep the core product theater-agnostic:
   - event ingestion
   - evidence bundling
   - infrastructure/entity graph
   - risk scoring
   - semantic compression
   - COP dashboard
   - briefing generator

## One-Sentence Pitch

When modern battlefields generate more data than degraded networks and human teams can handle, this system turns public OSINT, satellite proxies, and infrastructure context into evidence-backed priority alerts that still survive low-bandwidth command networks.

## MVP Dataset Shape

```json
{
  "event_id": "evt_2026_ukr_rail_001",
  "theater": "ukraine",
  "time": "2026-05-15T02:30:00Z",
  "event_type": "infrastructure_strike_report",
  "location": {
    "lat": 49.99,
    "lon": 36.23,
    "admin_area": "Kharkiv Oblast"
  },
  "affected_entities": [
    {"entity_id": "rail_node_123", "type": "rail_station"},
    {"entity_id": "power_substation_045", "type": "power"}
  ],
  "evidence_refs": [
    {"source": "ACLED", "ref": "event row or URL"},
    {"source": "GDELT", "ref": "article URL"},
    {"source": "FIRMS", "ref": "hotspot id"},
    {"source": "OSM", "ref": "way/node id"}
  ],
  "confidence": 0.72,
  "civilian_risk": "medium",
  "network_priority": 0.88,
  "recommended_action": "Send semantic summary now; queue raw evidence for store-forward sync."
}
```

## Next Research Questions

1. Which source gives the best legally reusable event layer for the demo: ACLED export, GDELT, or Kaggle/Petro?
2. Can alerts.in.ua token access be obtained before the hackathon?
3. Which AIS option is legally usable for a public demo: MarineTraffic screenshots, AISStream, Global Fishing Watch, or fully synthetic tracks?
4. Can we build a simple FIRMS area query for Ukraine and Hormuz AOIs without exposing API keys?
5. Can the current mock COP demo accept "theater packs" so Ukraine and Hormuz scenarios share the same UI?

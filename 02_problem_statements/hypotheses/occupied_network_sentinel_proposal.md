# Occupied Network Sentinel Proposal

- Created: 2026-07-04 KST
- Input case file: `/Users/mollykim/.codex/attachments/0a4143ac-a2e1-4a34-aa39-1979ebc15da8/우크라이나_통신고립_사례연구.xlsx`
- Recommended niche: detect and explain whether a newly restored or degraded network path is safe to use.

## One-Line Problem

In occupied or contested areas, the most dangerous network state is not always "offline." It is **"online, but routed through hostile infrastructure."**

## Why This Is A Niche Worth Taking

The Ukraine case study shows several kinds of communication isolation:

- Viasat: a single management plane allowed mass modem compromise.
- Mariupol: power loss killed cellular service before or alongside physical destruction.
- Kherson: internet returned, but traffic was forcibly rerouted through Crimea/Russia.
- Starlink: technical resilience improved, but governance/geofencing created availability gaps.
- Bakhmut / Avdiivka: isolated positions fell back to ad hoc phones and fragmented withdrawal communication.
- EW jamming: the spectrum itself became unreliable, including friendly interference.

Among these, Kherson-style rerouting is especially attractive for a D4D project because it is:

- technically network-centric, matching KT / telecom background;
- important but less crowded than generic drone/COP projects;
- non-kinetic and defensible under hackathon safety rules;
- data-friendly, because BGP, outage, censorship, and traceroute indicators can be collected from public APIs;
- productizable as a dashboard and copilot, not just research.

## Unresolved Gap

Existing tools can detect pieces of the problem:

- BGP route changes.
- Internet outages.
- censorship anomalies.
- traffic drops.
- VPN/app reachability.

But the operator still has to answer a practical question:

> "For this town / ISP / relay point, is the currently available connection normal, degraded, hostile-routed, censored, or too risky for sensitive communication?"

That translation layer is the gap.

## Product Concept

**Occupied Network Sentinel** is a connectivity-trust copilot for contested or liberated areas.

It does not merely ask whether the internet works. It scores whether the connection is safe enough for different use cases:

- public bulletin
- humanitarian coordination
- medical logistics
- journalist evidence upload
- resistance/civil society communication
- command/status reporting

## MVP User

Primary:

- military/civil emergency communications officer
- telecom restoration team
- humanitarian field coordination team

Secondary:

- OSINT analyst
- local government continuity team
- liberated-area restoration task force

## MVP Question

For a selected AOI such as Kherson, Mariupol, Odesa, Kharkiv, or Kramatorsk:

1. Is the network down?
2. If it is back, did the upstream AS/path change suspiciously?
3. Is traffic now passing through a hostile or censorship-heavy jurisdiction?
4. Are key apps/sites showing OONI-style anomalies?
5. Are power/strike events nearby likely to explain the outage?
6. What communication mode should be used now?

## Data Sources

| Signal | Source candidates | Role |
|---|---|---|
| BGP path / origin AS | RIPE RIS, RIPEstat BGP State, Cloudflare Radar routing, BGPStream | detects forced rerouting, hijack-like path changes, upstream changes |
| active reachability | RIPE Atlas ping/traceroute/DNS/TLS, IODA active probing | tells whether an area/prefix is reachable |
| traffic drop/outage | IODA, Cloudflare Radar Outage Center, NetBlocks-style reports if available | outage and restoration signal |
| censorship / tampering | OONI Explorer/API, OONI AWS open data | detects blocked sites/apps and anomalies |
| local context | GDELT, UCDP, ACLED, ISW links, Ukraine OSINT dataset | explains whether outage correlates with strike, occupation, or power loss |
| infrastructure context | OSM rail/power/hospital/bridge data | shows who is affected |

## Trust Score

The system should output a simple state:

| State | Meaning | Example action |
|---|---|---|
| `normal` | expected Ukrainian/global routing; low censorship anomaly | normal public coordination |
| `degraded` | packet loss/outage/power issue, but no hostile route evidence | send semantic summaries; queue raw evidence |
| `hostile_routed` | upstream/origin/path moved through hostile-controlled AS/jurisdiction | avoid sensitive traffic; use deniable/anonymous fallback |
| `censored` | OONI anomalies or app/site blocks elevated | switch bridges/VPN/alternate protocols |
| `unknown` | data sparse or conflicting | use public-only traffic and wait for corroboration |
| `offline` | no reliable network route | LoRa/FM/SMS/Starlink/physical courier fallback |

## MVP Demo Flow

1. Select an AOI: Kherson.
2. Show timeline:
   - normal Ukrainian upstream
   - blackout
   - restored but now Miranda Media/Rostelecom path
   - app/site censorship anomalies
3. The system generates an analyst card:
   - `Network is available but hostile-routed`
   - evidence: BGP path change, traffic restoration through Crimea/Russia, OONI anomalies, local occupation event
   - recommended communication policy:
     - public messages only on this path
     - do not send identity-sensitive data
     - use Starlink / trusted relay / store-forward for sensitive payloads
     - broadcast evacuation info as signed low-bandwidth public packet
4. Simulate degraded network modes:
   - full sync: send all evidence
   - semantic summary: send trust score + evidence refs
   - store-forward: queue raw evidence
   - offline: emit QR/LoRa/FM-ready bulletin packet

## Why It Fits The Existing D4D Dataset

Already collected:

- Ukraine conflict/event layer: UCDP, GDELT.
- infrastructure context: OSM AOI critical infrastructure.
- missile/UAV pressure: public missile attack tables.
- ISW links and weather context.

Next data to add:

- RIPE RIS / RIPEstat historical BGP state for selected Ukrainian ASNs.
- RIPE Atlas traceroute/ping data where public probes exist.
- OONI measurements for occupied or contested regions.
- IODA/Cloudflare outage data.

## Why This Is Better Than A Generic COP

Generic COP:

- "Here are many events on a map."

Occupied Network Sentinel:

- "This city is connected again, but using the connection may expose users. Here is why, and here is the safest communication mode."

That is a clearer product wedge.

## Hackathon Build Scope

Build a browser demo with:

- AOI selector.
- network trust timeline.
- BGP route-change evidence panel.
- OONI/censorship anomaly panel.
- local conflict/power context panel.
- communication-mode recommendation.
- low-bandwidth semantic packet preview.

## Safety Boundaries

- Do not provide real-time evasion instructions for active covert operations.
- Do not identify individual users, devices, journalists, resistance groups, or homes.
- Do not ingest raw private messages or social media accounts.
- Use historical/delayed or synthetic route data in the demo.
- Focus on humanitarian, restoration, and command-continuity use cases.

## Pitch

**Occupied Network Sentinel helps commanders, telecom teams, and humanitarian coordinators distinguish between "offline," "safe enough," and "connected but dangerous" networks in contested areas, then recommends the minimum-risk communication mode.**

# Korea Wartime Public Sources And S-DOT Use

- Created: 2026-07-04
- Scope: public/open-source basis for a Korea-context S-DOT Mission Continuity COP
- Safety boundary: this note does not describe real operational plans, real unit locations, target lists, routes of attack, rules of engagement, or classified/all-source intelligence. Use it only for high-level scenario framing, civil-support context, and synthetic demo data generation.

## Bottom Line

Public sources do not provide a usable answer to "how Korea would fight a war" at the operational-plan level. Real OPLANs, force dispositions, wartime routes, prioritization rules, and rules of engagement are not public and should not be reconstructed for a hackathon.

What is public and useful:

1. national security and defense strategy themes;
2. alliance command and deterrence structure;
3. integrated defense, mobilization, civil defense, emergency communication, and disaster-response legal frameworks;
4. public infrastructure, weather, transport, medical, shelter, communications, maritime, and geospatial datasets;
5. public doctrine and research on C2, DDIL, mission command, JADC2, semantic communication, and resilient logistics.

For S-DOT, this means the demo should model a public-safe scenario:

> command intent, civil-support constraints, degraded communications, resource allocation, stale/predicted COP, and rejoin audit under uncertainty.

It should not model:

> actual Korean war plans, offensive targeting, real military movement, or exact sensitive infrastructure dependencies.

## Publicly Inferable Strategic Priorities

These are safe, high-level priorities inferred from public strategy documents, law, official pages, and public commentary. They should be expressed as scenario assumptions, not as claims about a real current war plan.

| Priority | Public basis | S-DOT interpretation |
| --- | --- | --- |
| Deter and, if deterrence fails, defend the Republic of Korea | ROK-U.S. Combined Forces Command public mission page; national security strategy documents | Keep the product framed as defensive continuity and decision support. |
| Protect sovereignty, territory, and citizens | ROK national security strategy; civil defense and emergency guidance | Put citizen safety, shelter, emergency medical, and critical-service continuity into the COP. |
| Maintain combined/alliance defense readiness | CFC/USFK public materials, SCM statements, public OPCON discussions | Model coalition/C2 interoperability abstractly, not real command procedures. |
| Respond to nuclear and missile threats | public discussion of the ROK Three-Axis system, KAMD, extended deterrence | Use only as background. Do not implement strike-planning, target selection, or weapons effects. |
| Maintain C2 and shorten decision cycles | Defense Innovation 4.0 / JADC2 public materials | Make S-DOT a decision-quality-per-byte layer for DDIL networks. |
| Mobilize national resources in emergency | Emergency Resources Management Act, MOIS emergency-resource materials, MND national mobilization page | Use public/synthetic logistics and support-resource objects. |
| Integrate civil, government, police, fire, and military response | Integrated Defense Act and MOIS emergency-preparedness guidance | Model multi-agency COP and requests, not military-only tracking. |
| Sustain operations and restore services | logistics/sustainment public articles and disaster-response data | Include power, medical, transport, fuel, communications restoration, and route feasibility. |

## Public Sources To Track

### Strategy And Policy

| Source | Link | What it gives | Use in project |
| --- | --- | --- | --- |
| ROK National Security Strategy, 2023 | https://www.mofa.go.kr/us-en/brd/m_4511/view.do?seq=761766 | high-level security objectives, alliance, defense modernization, North Korea threat framing | public strategic assumptions and pitch language |
| Defense White Paper 2022, MND | https://www.mnd.go.kr/cop/pblictn/selectPublicationUser.do?publicationSeq=1040&siteId=mnd&id=mnd_020704000000&componentId=14&categoryId=0 | defense posture, Three-Axis, integrated defense, OPCON, defense innovation context | background only; do not treat as current OPLAN |
| Defense Innovation 4.0, MND pages | https://www.mnd.go.kr/mnd/179/subview.do | AI science-tech force, JADC2, military structure modernization | justify semantic COP / C2 modernization |
| Korea.kr Defense Innovation 4.0 summary | https://www.korea.kr/multi/visualNewsView.do?newsId=148912349 | public summary of AI-based next-generation C2/JADC2 direction | accessible citation for pitch |
| Korea.kr 2026 new-security innovation briefing | https://www.korea.kr/news/policyNewsView.do?newsId=148967227 | current-administration emphasis on AI, drones, new-security companies | versioned current-policy signal |
| CSIS on South Korea's offensive strategy | https://www.csis.org/analysis/south-koreas-offensive-military-strategy-and-its-dilemma | public analysis of Three-Axis/PISU dilemma | caveat slide: deterrence vs escalation risk |
| CFR on South Korea's Three-Axis system | https://www.cfr.org/articles/south-koreas-revitalized-three-axis-system | concise public explainer | background only, no implementation logic |

### Alliance, CFC, OPCON, Sustainment

| Source | Link | What it gives | Use in project |
| --- | --- | --- | --- |
| ROK-U.S. Combined Forces Command | https://www.usfk.mil/About/CFC/ | public CFC mission: deter aggression and defend ROK | high-level command context |
| USFK / USTRANSCOM contested logistics talks, 2025 | https://www.usfk.mil/Media/Newsroom/News/Article/4217144/us-south-korea-advance-contested-logistics-planning-in-seoul-talks/ | public signal that combined mobility/logistics readiness matters | sustainment-support layer justification |
| DLA / Army sustainment on Korean Peninsula | https://www.army.mil/article/224707/battlefield_sustainment_on_the_korean_peninsula | public article on operational-level sustainment | safe logistics background |
| CRS: U.S.-South Korea Alliance issues | https://www.everycrsreport.com/reports/IF13246.html | current alliance issues, OPCON, strategic flexibility, burden-sharing | current external policy context |
| NBR OPCON transition explainer | https://www.nbr.org/publication/setting-the-record-straight-on-opcon-transition-in-the-u-s-rok-alliance/ | public framing of OPCON transition misconceptions | explain why exact command relationships should stay abstract |

### Law, Mobilization, Civil Defense

| Source | Link | What it gives | Use in project |
| --- | --- | --- | --- |
| Integrated Defense Act | https://law.go.kr/LSW/lsInfoP.do?lsiSeq=105680 | total-defense concept and integration of national defense elements | model civil-government-military coordination |
| Emergency Resources Management Act | https://www.law.go.kr/lsInfoP.do?lsiSeq=92342 | legal basis for preparing and managing personnel/material resources in emergencies | public-safe resource categories |
| MOIS emergency resource management | https://www.mois.go.kr/frt/sub/a06/b12/emergencyresource/screen.do | lists broad resource classes including transport, communication supplies, medical, fuel | synthetic resource graph schema |
| MOIS emergency-preparedness work | https://www.mois.go.kr/frt/sub/a06/b12/mainBusiness/screen.do | public emergency training, wartime citizen guidance, CBRN/disaster training | civil-support scenario layer |
| MND national mobilization | https://mnd.go.kr/mnd/275/subview.do | public description of rapid transition to wartime mobilization posture | abstract mobilization phase in scenario |
| 2025 emergency citizen action guide, MOIS | https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000327&nttId=119703 | public citizen guidance | public-safety COP layer |

### Public Data/API Candidates

| Data/API | Link | Use | Caveat |
| --- | --- | --- | --- |
| Civil defense shelters | https://www.data.go.kr/data/15155067/openapi.do | shelter capacity and location context | show aggregate or selected public-safe examples |
| Emergency medical institutions | https://www.data.go.kr/data/15000563/openapi.do | medical support and capacity context | avoid implying military medical routing |
| Hospitals/clinics | https://www.data.go.kr/data/15000736/openapi.do | broader medical facility layer | public context only |
| MOLIT traffic flow | https://www.data.go.kr/data/15040463/openapi.do | route feasibility / congestion proxy | peacetime feed, not wartime reliability |
| Police traffic flow | https://www.data.go.kr/data/15087120/openapi.do | route condition proxy | key/IP restrictions may apply |
| MOLIT CCTV | https://www.data.go.kr/data/15040466/openapi.do | road/weather observation context | do not store raw video in submission |
| Emergency disaster messages | https://www.data.go.kr/data/15134001/openapi.do | official alerts and affected area context | cache minimally; avoid PII |
| KMA weather warnings | https://www.data.go.kr/data/15000415/openapi.do | hazard warnings by area/sea zone | already compatible with route/risk layer |
| KMA short-range forecast | https://www.data.go.kr/data/15084084/openapi.do | 5km grid weather forecast | support route/weather risk |
| KMA APIHub | https://apihub.kma.go.kr/ | weather and maritime weather APIs | API key and terms required |
| VWorld | https://www.vworld.kr/ | national spatial data, map, geocoding, downloads | currently already connected in project |
| VWorld data download | https://www.vworld.kr/dtmk/dtmk_ntads_s001.do | roads, buildings, boundaries, public spatial layers | choose non-sensitive layers |
| Disaster Safety Data Platform | https://www.safetydata.go.kr/ | disaster datasets and APIs | sign-up/approval may be required |
| KCA mountain-area mobile station finder | https://www.data.go.kr/data/15067860/openapi.do | public radio/mobile-station information for mountain areas | do not use for vulnerability mapping; aggregate for bearer candidate demo |
| Spectrum Map / 전파누리 | https://www.spectrummap.kr/ | spectrum and radio-station public info | aggregate and avoid sensitive claims |
| MND reserve training status | https://www.data.go.kr/data/15038297/fileData.do | public reserve training statistics | trend/background only |
| MND defense IT standards list | https://www.data.go.kr/data/3034718/openapi.do | public defense IT standards metadata | ontology/interoperability vocabulary |

## What Should Be Synthetic In The Demo

Use synthetic data for:

- real military units, unit location, readiness, equipment, supply, casualties, movement, and mission status;
- commander intent or orders;
- support-unit locations, military hospital routing, fuel/ammunition/sustainment stocks;
- exact base-station priority/availability during wartime;
- network authorization, preemption, routing policy, and restoration priority;
- real OPLAN phases, ROE, target lists, fire planning, or attack/defense routes;
- adversary capabilities beyond public, non-actionable scenario labels.

Use public data for:

- civilian geospatial base layers;
- public roads, weather, ports, shelters, hospitals, and emergency alerts;
- public communication-infrastructure proxies where allowed;
- public maritime/AIS/satellite catalog context when relevant;
- public law and policy references.

## Safe Scenario Template For S-DOT

Use abstract phases:

1. Crisis / warning: HQ sends mission intent, priority weights, and data-minimization policy.
2. Initial disruption: communications degrade; COP switches from raw/event sync to semantic deltas.
3. Isolation: edge unit uses local COP and cached intent; HQ sees last-confirmed state plus uncertainty envelope.
4. Intermittent contact: S-DOT sends heartbeat, support request, and highest-priority evidence digest first.
5. Civil-support coordination: COP overlays shelter, medical, weather, road, power, and comms restoration context.
6. Rejoin: local event log and predicted-state audit are reconciled; confidence and assumptions are reviewed.

## S-DOT Data Model Implications

Add or maintain these objects:

- `StrategicAssumption`: public source, date, confidence, caveat.
- `LegalPolicyConstraint`: public law/policy source, allowed demo use, prohibited use.
- `CivilSupportAsset`: shelter, hospital, transport, emergency alert, public comms proxy.
- `SyntheticUnitNode`: synthetic-only unit state with confirmed/predicted separation.
- `MobilizationResourceClass`: broad resource class from MOIS, never real inventory.
- `C2Mode`: connected, degraded, intermittent, isolated, rejoin.
- `PublicSourceEvidence`: citation, retrieval date, relevance, freshness.

## Versioning Notes

- Comprehensive security/defense strategies can change by administration. Treat all strategy documents as versioned sources.
- As of this note, a publicly accessible 2023 ROK National Security Strategy and 2022 Defense White Paper are strong baseline documents, while 2026 public materials show active emphasis on AI, drones, and new-security innovation.
- Re-check MND, MOFA, Korea.kr, USFK, CRS, KIDA, and major think tanks before final submission.

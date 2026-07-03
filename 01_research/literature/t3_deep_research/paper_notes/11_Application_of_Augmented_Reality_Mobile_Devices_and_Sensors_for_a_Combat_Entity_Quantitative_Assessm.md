# Application of Augmented Reality, Mobile Devices, and Sensors for a Combat Entity Quantitative Assessment Supporting Decisions and Situational Awareness Development

## Metadata

- Year: 2019
- URL: https://doi.org/10.3390/app9214577
- DOI: 10.3390/app9214577
- Read status: abstract_only

## One-line Takeaway

The paper frames a mobile COP as an edge decision-support tool that fuses location, mission, sensor, and GIS context into personalized tactical awareness and threat assessment.

## D4D Relevance

Useful as a land-domain precedent for a resilient maritime COP: it supports the idea that tactical users can carry a distributed, personalized COP on mobile devices, perform local analytics, and maintain situational awareness even when higher-echelon systems or networks are constrained. For a T3 semantic COP, its concepts map to edge-first maritime entity tracking, semantic threat scoring, route/task assistance, and compact synchronization of mission-relevant facts over denied or intermittent networks.

## Key Concepts

- mobile common operational picture
- augmented reality tactical visualization
- blue-force tracking
- reconnaissance data fusion
- GIS and vector data fusion
- threat-level estimation
- path finding and movement scheduling
- tactical smartphone decision support
- personalized situational awareness
- dynamic mobile networks

## Input Data

- force location data
- unit composition and tasking data
- mission plans, checkpoints, and movement tasks
- mobile device sensor/location data
- reconnaissance observations
- GIS topographic and vector layers
- terrain and tactical context
- threat-related contextual data

## Methods Or Architecture

- distributed mobile COP platform for tactical smartphones
- augmented reality interface for contextual tactical overlays
- fusion of mission data with GIS/topographic/vector data
- on-device algorithms for route/path finding and movement assistance
- combat potential and threat-level evaluation methods
- location tracking and blue-force tracking services
- mission-critical function organization for field users

## Outputs / Metrics

- personalized mobile COP view
- AR-based visualization of threats, tasks, and checkpoints
- blue-force tracking outputs
- reconnaissance fusion outputs
- terrain evaluation for mission planning and execution
- path and movement assistance recommendations
- threat-level estimates
- improved orientation and decision support claimed, but detailed quantitative metrics are not available from the provided abstract

## Prototype Hooks

- Implement an edge mobile maritime COP client that can operate with intermittent connectivity
- Represent vessels, contacts, tracks, tasks, hazards, and reports as compact semantic objects
- Fuse AIS, radar, EO/IR, acoustic, and human reports into a local tactical picture
- Add on-device maritime threat scoring for suspicious approach, spoofing, loitering, or route deviation
- Use map/AR overlays for boarding teams, port security, or coastal patrol users
- Prioritize sync of small semantic deltas instead of full imagery or raw sensor feeds
- Provide route and checkpoint assistance for patrol, intercept, or escort missions
- Maintain role-personalized COP views for commanders, watchstanders, and mobile teams

## Pitch Evidence

- Shows that mobile devices can host meaningful tactical decision-support algorithms, not only display remote COP data
- Supports the design claim that local fusion and analytics improve awareness when network access is dynamic or degraded
- Provides precedent for combining tracking, mission data, GIS layers, and threat evaluation in one mobile COP workflow
- Strengthens the case for a semantic COP that sends mission-relevant assessments and entities rather than raw data streams

## Limitations / Risks

- Only abstract-level evidence was available, so implementation details and validation results are uncertain
- The paper appears focused on land combat and crisis-management scenarios, not maritime operations
- Assumes availability of mobile networks during missions, while denied maritime networks may be more intermittent or contested
- Threat models and evaluation algorithms may not transfer directly to maritime contacts, vessels, or spoofing behaviors
- AR features may be less central than robust map-based COP and low-bandwidth synchronization for maritime command use

## Confidence

medium

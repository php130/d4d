# A Common Operational Picture in Support of Situational Awareness for Efficient Emergency Response Operations

## Metadata

- Year: 2017
- URL: https://doi.org/10.18488/journal.102.2017.21.10.35
- DOI: 10.18488/journal.102.2017.21.10.35
- Read status: partial_text

## One-line Takeaway

A COP is most valuable when it turns fragmented multi-agency reports into shared situational awareness, role-relevant coordination, and faster decisions under uncertainty.

## D4D Relevance

The paper gives a strong requirements and evaluation frame for a Resilient Maritime COP over Denied Networks: build semantic sharing around who needs what information, preserve crisis memory, tolerate infrastructure loss, reduce information overload, and measure whether the COP improves shared awareness, coordination speed, and mission effectiveness.

## Key Concepts

- common operational picture
- situational awareness levels: perception, comprehension, projection
- shared situational awareness
- team situational awareness
- network enabled capabilities
- network-centric operations
- dynamic emergency response information systems
- role transferability
- information validity and timeliness
- information overload
- interoperability across organizations
- self-synchronization

## Input Data

- multi-agency emergency reports
- geospatial incident information
- responder locations and status
- resource and asset availability
- environmental and hazard context
- communications and coordination logs
- sensor or field observations
- plans, roles, tasks, and responsibilities

## Methods Or Architecture

- literature review of emergency response, COP, SA, and network-enabled concepts
- DERMIS design premises for flexible emergency response systems
- NEC value chain linking network robustness to information sharing, shared awareness, self-synchronization, and operational effects
- distinction between individual, shared, and team situational awareness
- role-aware information filtering while preserving access to broader context
- central information repository with crisis memory and event logs
- support for lateral, upward, and downward information flow rather than only hierarchical control

## Outputs / Metrics

- reduced dispatch, preparation, and information-decision delays
- improved information quality and timeliness
- higher shared situational awareness
- better coordination across agencies
- faster command speed
- mission effectiveness
- qualitative and quantitative COP assessment basis
- logs for after-action review and system improvement

## Prototype Hooks

- Model maritime entities, reports, tasks, roles, confidence, and timestamps as a semantic COP graph.
- Implement role-based views that filter overload but allow drill-down to all relevant context.
- Add crisis-memory logging so disconnected actions, observations, and decisions can be replayed and synchronized later.
- Use confidence, provenance, and freshness metadata to handle conflicting reports over degraded links.
- Design for local-first operation with eventual synchronization across denied or intermittent networks.
- Map NEC value-chain metrics into demo telemetry: connectivity, information sharing, shared awareness, coordination latency, and mission outcome.
- Support transfer of watch roles and command responsibilities during degraded operations.

## Pitch Evidence

- The paper identifies poor information sharing, communication gaps, and lack of a COP as major barriers to emergency response.
- It argues that shared situational awareness depends on timely, relevant, interoperable information across organizations.
- It supports moving beyond rigid hierarchy toward network-enabled coordination in dynamic crises.
- It explicitly notes that technology may fail during major emergencies, making resilience and restoration of essential network capabilities important.
- It frames COP value in operational terms: faster decisions, better coordination, and improved emergency response outcomes.

## Limitations / Risks

- The paper is a broad literature review, not a maritime-specific implementation study.
- It emphasizes concepts and recommendations more than tested system architecture or quantitative results.
- Network-centric approaches can worsen information overload if filtering, provenance, and validation are weak.
- Information quality validation remains difficult when reports conflict or arrive through degraded channels.
- Institutional policies, roles, and trust arrangements are as important as technology for cross-organization sharing.
- Assumptions from emergency response may need adaptation for contested maritime environments and denied networks.

## Confidence

medium

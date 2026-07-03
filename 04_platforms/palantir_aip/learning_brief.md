# Palantir AIP / Foundry Learning Brief

Last reviewed: 2026-06-29

## Why It Matters For D4D

Palantir AIP/Foundry is useful in this hackathon because the core problem is not just "ask an LLM" but "connect messy operational data, model it as real-world objects, reason over it, and deliver a decision workflow." For D4D, that means turning OSINT, maritime, disaster, air/space, or procurement data into an operational app that can support a military/security decision.

## Mental Model

Think of the Palantir workflow as five layers:

1. Data integration
   - Bring in files, databases, APIs, documents, geospatial data, sensor/event feeds, or synthetic data.

2. Data transformation
   - Clean and normalize source data into datasets.
   - Extract entities from unstructured text/documents when needed.

3. Ontology
   - Convert datasets into operational objects and relationships.
   - Examples for D4D: `Organization`, `Vessel`, `Port`, `ThreatActor`, `CredentialExposure`, `Incident`, `Sensor`, `Mission`, `Asset`, `Alert`.

4. AI / decision logic
   - Use AIP Analyst, AIP Logic, semantic search, RAG, functions, agents, and evals to answer questions or perform workflow steps.
   - Keep citations/provenance visible.

5. Operational application
   - Use Workshop, dashboards, maps, object views, alerts, actions, and reports to show how an analyst/operator would actually use the result.

## Core Concepts To Learn

| Concept | What it means | D4D use |
| --- | --- | --- |
| Foundry | Palantir's data integration and operations platform | Bring public/synthetic data into a governed workspace |
| AIP | AI Platform layer for using LLMs/agents over enterprise data and ontology | Build an analyst/copilot workflow with citations |
| Ontology | Object/relationship model over operational data | Model vessels, actors, incidents, assets, alerts |
| Object Type | A class of operational object | `ThreatActor`, `Company`, `Vessel`, `Incident` |
| Link Type | Relationship between object types | `Actor uses Alias`, `Vessel visited Port`, `Company won Contract` |
| Action | A controlled writeback or workflow step on ontology objects | Mark alert reviewed, assign investigation, create report |
| Workshop | App-building surface for operational dashboards/apps | Build a COP, risk dashboard, investigation UI |
| AIP Analyst | Natural language analysis over data/ontology | Ask "What changed in this AOI this week?" |
| AIP Logic / Functions | Reusable logic that can call models/tools and act on objects | Risk scoring, extraction, classification, report generation |
| AIP Evals | Evaluation framework for AI workflows | Compare prompts/retrieval/risk scoring output |
| OSDK | Ontology SDK for custom apps | Optional if the team builds a custom frontend |
| Provenance / governance | Source, access control, audit, policy | Required for military deployability and safe demo |

## D4D Object Model Seeds

### T2 OSINT / Defense Intelligence

Objects:

- `Source`
- `Report`
- `ThreatActor`
- `Alias`
- `Domain`
- `IPAddress`
- `Wallet`
- `CredentialExposure`
- `Organization`
- `Incident`
- `RiskAssessment`

Relationships:

- `ThreatActor uses Alias`
- `Alias appears in Source`
- `Domain linked to Incident`
- `Wallet receives funds from Wallet`
- `Organization exposed by CredentialExposure`
- `RiskAssessment cites Source`

### T4 Maritime Domain Awareness

Objects:

- `Vessel`
- `Port`
- `AISPosition`
- `Voyage`
- `Anomaly`
- `WeatherCell`
- `SanctionsEntity`
- `NewsEvent`

Relationships:

- `Vessel visited Port`
- `Vessel emitted AISPosition`
- `Vessel associated with SanctionsEntity`
- `Anomaly observed near Port`
- `NewsEvent references Vessel/Port`

### T3 C2 / Sustainment

Objects:

- `Asset`
- `Unit`
- `Location`
- `Mission`
- `SupplyItem`
- `Route`
- `Disruption`
- `MaintenanceNeed`
- `Decision`

Relationships:

- `Asset assigned to Mission`
- `Route affected by Disruption`
- `Unit requires SupplyItem`
- `Decision cites Evidence`

## Palantir Learning Path For This Week

1. Day 1: Ontology basics
   - Understand object types, properties, links, actions.
   - Draft D4D object models for T2/T4/T3.

2. Day 2: Data pipeline basics
   - Learn ingestion and transformation patterns.
   - Practice with CSV/JSON from D4D dataset and OSINT catalog.

3. Day 3: AIP analysis and RAG
   - Learn how natural language analysis, semantic search, citations, and LLM-backed transformations fit together.
   - Draft prompts for intelligence brief generation.

4. Day 4: Workshop / Common Operating Picture
   - Learn how to show object sets on maps, dashboards, object views, and alert queues.
   - Build a mock screen plan for the demo.

5. Day 5: Evals, governance, pitch
   - Define 5-10 test questions and expected safe outputs.
   - Prepare explainability, audit, privacy, and military deployability talking points.

## Most Relevant Build With AIP Examples

See `build_examples_index.md` for a longer list. Highest priority examples:

- Build with AIP Agent Studio
- Build a common operating picture with geospatial data
- End-to-end alerting workflow
- Evaluate Retrieval-Augmented Generation methods
- Semantic Search
- Use AIP Logic to classify and edit objects
- Control your Workshop with embedded AIP Agent copilots
- Transform geospatial data in Pipeline Builder
- Parse PDFs / documents with LLMs in Pipeline Builder
- Graphically explore relationships in your Ontology with Vertex Graph

## D4D Demo Pattern

For a Palantir-based D4D demo, aim for this sequence:

1. Load or simulate public data.
2. Map it into ontology objects and relationships.
3. Show an operational view: map, graph, queue, timeline, or object page.
4. Ask an AIP-powered question.
5. Return a citation-backed brief.
6. Let the analyst take an action: assign, mark reviewed, request more evidence, generate report.
7. Show eval/safety/governance story: no raw sensitive data in submission, provenance retained, human-in-the-loop.

## Open Questions

- Does the hackathon provide a real Palantir workspace/enrollment URL?
- Which Palantir apps are enabled for participants: AIP Analyst, Workshop, Pipeline Builder, Agent Studio, Evals, OSDK?
- Can participants import CSV/JSON directly?
- Are external API calls allowed from the Palantir environment?
- Is there a sample ontology or starter pack provided by Palantir/D4D?

## Sources

- https://www.palantir.com/docs
- https://www.palantir.com/docs/foundry/aip/overview/
- https://www.palantir.com/docs/foundry/aip-analyst/overview/
- https://www.palantir.com/docs/foundry/aip-evals/overview/
- https://www.palantir.com/docs/foundry/security/overview/
- https://build.palantir.com/


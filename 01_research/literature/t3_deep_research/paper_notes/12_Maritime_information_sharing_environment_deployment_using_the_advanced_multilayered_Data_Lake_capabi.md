# Maritime information sharing environment deployment using the advanced multilayered Data Lake capabilities

## Metadata

- Year: 2022
- URL: https://doi.org/10.31217/p.36.2.13
- DOI: 10.31217/p.36.2.13
- Read status: partial_text

## One-line Takeaway

EFFECTOR shows a practical maritime COP architecture that turns heterogeneous AIS, satellite, UAV, METOC, and legacy-system feeds into CISE-compatible shared data lakes with semantic reasoning for a richer Recognized Maritime Picture.

## D4D Relevance

Highly relevant to a T3 semantic COP: it provides an end-to-end pattern for resilient maritime information sharing across agencies, with schema-on-read data lakes, CISE/eCISE adapters, RDF/SPARQL semantic graphs, edge UAV processing, and publish/pull/push exchange patterns that can be adapted for degraded or denied networks.

## Key Concepts

- Common Information Sharing Environment
- CISE/eCISE interoperability
- multilayered maritime Data Lake
- Recognized Maritime Picture
- semantic COP
- Linked Data
- RDF triples
- SPARQL querying and rule inference
- schema-on-read storage
- data fusion and anomaly alerts
- C2/C3i integration
- edge processing on UAVs
- SAT-AIS and EO vessel detection
- METOC enrichment
- publish-subscribe and pull/push information exchange

## Input Data

- AIS and SAT-AIS vessel data
- D-AIS/SPIRE vessel messages
- SAR imagery from Sentinel-1, TerraSAR-X, and Radarsat-2
- optical satellite imagery from Deimos
- Copernicus Marine Service METOC data including sea temperature, currents, wind, waves, and bathymetry
- UAV RGB and thermal video feeds
- UAV detection and tracking JSON messages
- coastal radar and VTS-style feeds referenced as legacy inputs
- VTMIS, NMSW, C2/C3i, and other maritime legacy-system data
- CISE/eCISE messages for vessel, task, aircraft, event, risk, location, and related entities

## Methods Or Architecture

- Layered Data Lake with input/output, storage, ontology, data fusion, and CISE adaptation layers
- Kafka ingestion for streaming maritime messages
- Apache NiFi routing, processing, and semantic data flows
- HDFS raw storage with schema-on-read design
- Apache Atlas metadata indexing and governance
- Elasticsearch and Kibana for indexed analysis and visualization
- RMLMapper-based JSON-to-RDF transformation
- RDF4J triple store for semantic graph persistence
- SPARQL rules for reasoning over short time windows, including vessel behavior inference
- CISE adapters translating legacy data into shared maritime service/entity models
- C2 platform integration with MUSCA, ENGAGE, and SeaMIS
- UAV onboard object detection and tracking using Jetson AGX Xavier to reduce bandwidth dependence

## Outputs / Metrics

- More accurate shared Common Operational Picture / Recognized Maritime Picture
- CISE-compatible vessel, task, aircraft, incident, risk, and location information exchange
- Alerts for abnormal vessel behavior and future alarms
- Dashboards and reports for maritime operators
- Detected and tracked vessel entities from UAV feeds
- Satellite-assisted identification of non-reporting or position-faking vessels
- Operational-trial evaluation across France, Portugal, and Greece
- Survey KPAs covering data lake semantics, interoperability, data-source integration, fusion and analytics, C2, decision support, and legal/ethical compliance
- 64 evaluation responses including end users, technical partners, and external practitioners
- Reported strong user ratings for interoperability, CISE standardization, dashboard/reporting, satellite/METOC integration, and legacy-system improvement

## Prototype Hooks

- Use CISE/eCISE as the semantic message envelope for a T3 maritime COP data model
- Implement a local-first data lake node that can cache raw sensor feeds and synchronize when links recover
- Represent COP entities as RDF triples so disconnected nodes can merge observations later with fewer schema conflicts
- Use SPARQL rules for explainable tactical inferences such as course change, anomaly, rendezvous, dark vessel, or collision-risk indicators
- Adopt NiFi-style flow processors for ingest, normalize, route, and replay pipelines over intermittent links
- Add edge UAV detection that sends compact JSON/RDF track messages when video bandwidth is denied
- Use publish-subscribe plus pull/push exchange modes to support both connected operations and delayed retrieval
- Store provenance and metadata for every track, detection, and alert to support trust scoring in contested conditions
- Fuse AIS, SAR/optical detections, METOC, and UAV observations to detect spoofing or non-cooperative vessels
- Expose dashboards as generated views over semantic state rather than as the primary source of truth

## Pitch Evidence

- The paper validates the architecture in operational maritime trials involving multiple national settings and C2 systems.
- It demonstrates that heterogeneous sources can be harmonized into CISE/eCISE-compatible exchanges rather than requiring a single monolithic COP platform.
- The semantic layer directly supports a T3 story: machine-readable context, reasoning, inference, and cross-organization queries over distributed repositories.
- The UAV design is strong evidence for denied-network resilience because onboard detection reduces dependence on continuous high-bandwidth video links.
- The combination of AIS with satellite imagery is useful pitch evidence for detecting dark or deceptive vessels in a contested maritime picture.
- Evaluation KPAs explicitly include Data Lake and Semantics, interoperability, decision support, data fusion, and integration of novel surveillance systems.

## Limitations / Risks

- The architecture assumes significant infrastructure such as Kafka, NiFi, HDFS, RDF4J, Elasticsearch, CISE nodes, and adapters, which may be heavy for tactical disconnected deployments.
- Operational trials appear survey-heavy; the excerpt does not provide hard latency, bandwidth, packet-loss, or contested-network performance metrics.
- SPARQL mini-batch reasoning used a 10-minute window, which may be too slow for some tactical engagements unless tuned.
- CISE/eCISE alignment helps interoperability in European maritime contexts but may require mapping to NATO, national, or coalition data models.
- Semantic graph quality depends on correct mappings, entity resolution, timestamps, and provenance handling across noisy sources.
- Satellite and optical inputs have coverage, revisit, weather, cloud, and latency constraints.
- UAV edge detection reduces bandwidth needs but still depends on model accuracy, sensor quality, weather, and reliable transmission of compact messages.
- Cybersecurity, access control, and trust management are mentioned indirectly but not deeply addressed in the provided text.

## Confidence

high

# DarkVesselNet: Multi-Modal Remote Sensing and Trajectory Reasoning for Dark Vessel Detection

## Metadata

- Year: 2026
- URL: http://arxiv.org/abs/2606.00445v1
- DOI: -
- Read status: partial_text

## One-line Takeaway

DarkVesselNet frames dark-vessel detection as auditable multi-modal evidence fusion, not as a single black-box classifier or proof of illegal activity.

## D4D Relevance

Highly relevant to a Resilient Maritime COP over Denied Networks because it shows how to build a semantic COP that can reason across incomplete AIS, SAR, optical imagery, trajectory gaps, context layers, and uncertainty. Its strongest contribution for a T3 semantic COP is the traceable alert model: every maritime object or anomaly should carry evidence provenance, modality availability, confidence, ambiguity, and analyst-review status.

## Key Concepts

- Dark vessel detection as evidence disagreement
- SAR and AIS fusion
- Optical context as optional confirmation
- AIS missingness and trajectory gaps
- TGARD-style gap and rendezvous reasoning
- Pi-DPM-inspired anomaly scoring
- Geospatial foundation model adapter
- Missingness-aware fusion
- Evidence trace schema
- Calibration and human review
- Label taxonomy separating observation from legal conclusion

## Input Data

- Sentinel-1 SAR chips
- Sentinel-2 optical imagery
- AIS trajectories with time, latitude, longitude, speed over ground, and course over ground
- AOI queries
- Cloud masks and optical band ratios such as NDVI and NDWI
- Coastline, port, and infrastructure context layers
- SAR acquisition timestamps
- AIS matching windows
- Modality availability masks

## Methods Or Architecture

- Pipeline ingests AOI, SAR, optical, AIS, and context evidence
- SAR preprocessing includes Lee filtering for speckle reduction
- Optical preprocessing includes cloud masking and band-ratio features
- GeoBackbone adapter normalizes outputs from Prithvi-2, Clay, SatMAE++, DOFA, SatlasNet, and RemoteCLIP-style encoders into patch tokens
- AIS reasoning uses Haversine distance, gap duration, feasible movement envelopes, and rendezvous-style checks
- Fusion architecture preserves modality-specific embeddings and availability masks
- Anomaly head pools scene tokens and AIS features to produce an alert logit and reconstructed trajectory segment
- Alert output is intended to include probability, evidence trace, sensor availability, AIS association, anomaly evidence, and uncertainty
- Evaluation design separates SAR detection, AIS matching, trajectory anomaly quality, fusion performance, calibration, and trace completeness

## Outputs / Metrics

- Dark-vessel alert probability or calibrated evidence score
- Evidence trace for analyst review
- Review queue ranking
- SAR vessel detection metrics such as mAP and recall by vessel length
- Near-shore false positive breakdown
- AIS match precision and recall
- AIS gap or rendezvous precision
- End-to-end alert precision and recall
- Expected calibration error and reliability diagrams
- Trace completeness
- Coregistration error
- Repository-local validation showing 15 passing tests for operators and tensor contracts

## Prototype Hooks

- Represent every COP entity as a semantic evidence bundle with SAR, AIS, optical, trajectory, and context slots
- Add modality availability masks so the COP distinguishes missing data from negative evidence
- Implement AIS gap detection and required-speed sanity checks as first-pass denied-network reasoning
- Create a lightweight alert trace schema with scene id, timestamp, AIS candidates, matching distance, gap evidence, optical availability, context, model version, and calibration bucket
- Use low-bandwidth alert cards that transmit structured evidence summaries instead of raw imagery when networks are degraded
- Expose ambiguity explicitly when multiple AIS tracks could explain one SAR detection
- Separate labels in the COP ontology: SAR object, vessel candidate, AIS matched vessel, AIS unmatched vessel, dark-vessel alert, and externally confirmed illegal activity
- Use fusion ablations in the demo to show how alerts change when AIS, optical, or trajectory evidence is unavailable
- Use calibrated ordinal confidence such as low, medium, high when validation data is weak
- Position the prototype as analyst triage, not autonomous enforcement

## Pitch Evidence

- The paper directly supports the claim that maritime COP resilience requires reasoning over disagreement between cooperative and non-cooperative sensors
- SAR provides physical observation when AIS is absent, spoofed, delayed, or unavailable
- AIS absence is treated as uncertain evidence rather than proof, which is important for ethical and operational credibility
- The architecture is designed for missing modalities, matching denied-network realities where not every node has all data
- Trace-producing alerts align with command needs: explain what was seen, what was missing, what matched, what was ambiguous, and why the alert was prioritized
- Repository-grounded tests support the feasibility of a hackathon prototype even without full live-data integration
- The paper’s taxonomy gives language for briefing stakeholders without overclaiming: the system finds review-worthy evidence patterns, not legal guilt

## Limitations / Risks

- Current evidence is mainly software-grounded, not a validated operational benchmark result
- No claimed xView3 leaderboard-scale performance
- No live AIS or SAR ingest is established in the provided text
- Foundation model benefits for SAR remain unproven and need modality-specific ablation
- AIS absence can result from coverage gaps, equipment failure, legal non-carriage, or timing issues
- Near-shore clutter, infrastructure, buoys, platforms, wakes, and small boats can cause false positives
- Optical imagery is limited by clouds, daylight, glint, revisit timing, and spatial resolution
- AIS spoofing is not fully handled by the described implementation
- A raw anomaly score is not necessarily calibrated probability
- The system cannot infer intent or legal status without external human and institutional review

## Confidence

high

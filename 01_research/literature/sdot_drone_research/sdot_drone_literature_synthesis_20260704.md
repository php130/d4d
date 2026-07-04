# S-DOT Drone Literature Synthesis

- Date: 2026-07-04 KST
- Collection run: `20260704_164224`
- Metadata sources: OpenAlex Works API, arXiv API
- Raw records: 1,771
- Deduped records: 1,343
- Snowball new records: 446
- Merged metadata records after snowball: 1,789
- arXiv retry new records: 111
- Final combined metadata records: 1,900

## Output Files

- Full records JSON: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/20260704_164224/sdot_drone_literature_records.json`
- Full records CSV: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/20260704_164224/sdot_drone_literature_records.csv`
- Topic summary: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/20260704_164224/sdot_drone_topic_summary.json`
- Reading queue: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_first_reading_queue_20260704_164224.md`
- Catalog: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_research_catalog_20260704_164224.md`
- Snowball queue: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_snowball_reading_queue_20260704_165653.md`
- arXiv retry queue: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_arxiv_retry_queue_20260704_170558.md`
- Final combined corpus: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/final_20260704_170558/sdot_drone_literature_records_final.json`
- Algorithm evidence matrix: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_algorithm_evidence_matrix_20260704.md`
- Top paper extraction notes: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_top_paper_extraction_notes_20260704.md`
- Priority source access and algorithm notes: `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_priority_source_access_and_algorithm_notes_20260704.md`
- Public dataset/simulator catalog: `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_public_dataset_simulator_catalog_20260704.md`
- GNSS/RF/link dataset catalog: `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_gnss_rf_link_dataset_catalog_20260704.md`
- GNSS/RF/link dataset candidate JSON: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/gnss_rf_link_dataset_candidates_20260704.json`
- GNSS/RF/link dataset smoke-test report: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/dataset_smoke_tests/20260704_173915/dataset_smoke_test_report.md`
- v0.7 algorithm/data requirements: `/Users/mollykim/projects/D4D/06_prototype/docs/s_dot_drone_v0_7_algorithm_and_data_requirements_20260704.md`

## Collection Coverage

Initial query topic counts:

- GNSS jamming / spoofing detection and integrity: 225
- Semantic communications for UAV / edge: 180
- UAV GNSS-denied navigation: 146
- Kalman residual / NIS / integrity monitoring: 137
- Resilient UAV communications under jamming: 131
- UAV networks, DDIL, DTN, intermittent links: 121
- Edge AI / compression / video semantic transmission: 112
- Provenance, trust, C2, decision support: 105
- UAV simulation / digital twin / 3D validation: 98
- UAV sensor fusion and tracking: 88

Final combined source counts:

- OpenAlex: 1,619
- arXiv: 281

Note:

arXiv rate-limited the first run after the first several topics. A slower retry completed later and added 111 new arXiv records.

Snowball note:

The first OpenAlex snowball run followed references and related works from 120 high-scoring seed papers. It fetched 446 new records and expanded the merged metadata base to 1,789 records. The strongest additions are terrain-aided navigation, visual-inertial odometry, RAIM/INS spoofing detection, and GPS-denied localization.

arXiv retry note:

A slower retry over the rate-limited topics added 111 new arXiv records without failures. The final combined metadata corpus now contains 1,900 records.

## Core Technical Thesis

The revised S-DOT demo should be defended by four connected research pillars:

1. **Semantic communications**
   - Do not transmit all raw data.
   - Transmit task-relevant meaning, goals, or event summaries.
   - Use raw evidence references and rejoin audit to preserve accountability.

2. **GNSS-denied / GNSS-degraded UAV navigation**
   - Last known position plus velocity, heading, IMU, wind, visual/terrain cues, and covariance can sustain a prediction envelope.
   - The command board must show uncertainty, not exact location.

3. **Residual-based integrity monitoring**
   - Kalman/EKF-style prediction can be compared against GNSS/telemetry updates.
   - A large innovation/residual can trigger a navigation-integrity anomaly.
   - NIS is a defensible first implementation for the demo.

4. **DDIL / resilient UAV communications**
   - Link state should control payload tier.
   - Full raw feed, deltas, semantic cards, store-forward, and local-only modes are distinct operating states.

## Implementation-Relevant Theory

### 1. Prediction under lost telemetry

Use local NED/ENU coordinates instead of lat/lon for calculation.

```text
p_{t+dt} = p_t + v_t * dt + 0.5 * a_t * dt^2 + wind_t * dt
```

Demo use:

- predict drone path after last contact
- draw predicted route in 3D
- drive uncertainty growth

### 2. Uncertainty growth

```text
sigma_pos(t)^2 =
  sigma_pos0^2
  + sigma_vel^2 * t^2
  + 0.25 * sigma_acc^2 * t^4
  + sigma_wind^2 * t^2
```

Demo use:

- uncertainty cone/ellipse expands as disconnect time increases
- worse wind and maneuvering increase uncertainty
- UI avoids false precision

### 3. Kalman/EKF residual

Prediction:

```text
x_pred = f(x_prev, u_t, dt)
P_pred = F_t * P_prev * F_t^T + Q_t
```

Innovation:

```text
y_t = z_t - H_t * x_pred
S_t = H_t * P_pred * H_t^T + R_t
```

Normalized Innovation Squared:

```text
NIS = y_t^T * S_t^-1 * y_t
```

Demo use:

- large residual/NIS means reported state is inconsistent with predicted dynamics
- if combined with GNSS/link quality degradation, raise `JAMMING_SUSPECTED`
- if GNSS looks normal but residual is large, raise `SPOOFING_SUSPECTED` or `NAVIGATION_RESIDUAL_SPIKE`

### 4. Jamming hypothesis score

Do not claim proof. Use a defensive hypothesis score:

```text
jamming_score =
  0.25 * gnss_quality_drop
  + 0.20 * link_quality_drop
  + 0.20 * normalized_position_residual
  + 0.15 * heartbeat_gap_score
  + 0.10 * imu_gnss_disagreement
  + 0.10 * context_risk
```

Demo use:

- output label: normal, navigation degraded, jamming suspected, severe denial suspected
- show evidence refs
- include caveat: not proof of emitter source/location

### 5. Semantic packet economics

S-DOT value should be shown as byte economics:

```text
raw_bytes_represented / semantic_bytes_sent
```

Demo use:

- raw EO/IR frame batch can be represented by a sub-1KB semantic card
- packet inspector shows what was sent, deferred, or held local
- rejoin audit explains what raw evidence remains cached

## Top Reading Queue by Use

### GNSS / Spoofing / UAV Integrity

1. [SemperFi: Anti-spoofing GPS Receiver for UAVs](https://doi.org/10.14722/ndss.2022.23071)
   - Use for: UAV spoofing detection/mitigation framing, GPS receiver resilience.

2. [GNSS-denied geolocalization of UAVs by visual matching of onboard camera images with orthophotos](http://arxiv.org/abs/2103.14381v2)
   - Use for: GNSS-denied localization alternatives and visual map matching.

3. [Detecting Signal Spoofing Attack in UAVs Using Machine Learning Models](https://doi.org/10.1109/access.2021.3089847)
   - Use for: ML-based spoofing detection feature ideas.

4. [GNSS-denied unmanned aerial vehicle navigation: analyzing computational complexity, sensor fusion, and localization methodologies](https://doi.org/10.1186/s43020-025-00162-z)
   - Use for: survey taxonomy of GNSS-denied navigation methods.

5. [UAV Positioning Using GNSS: A Review of the Current Status](https://doi.org/10.3390/drones10020091)
   - Use for: system-level GNSS positioning constraints for UAVs.

### Residual / Kalman / Integrity Monitoring

1. [Two-Step Trajectory Spoofing Algorithm for Loosely Coupled GNSS/IMU and NIS Sequence Detection](https://doi.org/10.1109/access.2019.2927539)
   - Use for: NIS sequence detection and spoofing-residual concepts.

2. [Tight Fusion of a Monocular Camera, MEMS-IMU, and Single-Frequency Multi-GNSS RTK for Precise Navigation in GNSS-Challenged Environments](https://doi.org/10.3390/rs11060610)
   - Use for: multi-sensor fusion in GNSS-challenged environments.

3. [GNSS Integrity Monitoring Schemes for Terrestrial Applications in Harsh Signal Environments](https://doi.org/10.1109/mits.2020.2994076)
   - Use for: integrity monitoring concepts under harsh signal conditions.

### Semantic Communications / Edge

1. [Goal-Oriented Semantic Communications for 6G Networks](https://doi.org/10.1109/iotm.001.2300269)
   - Use for: task/goal-oriented communication framing.

2. [Distributed Machine Learning for UAV Swarms: Computing, Sensing, and Semantics](https://doi.org/10.1109/jiot.2023.3341307)
   - Use for: UAV swarm computing/sensing/semantics bridge.

3. [Emerging Trends in UAVs: From Placement, Semantic Communications to Generative AI for Mission-Critical Networks](https://doi.org/10.1109/tce.2024.3434971)
   - Use for: UAV + semantic communications + mission-critical networks.

4. [Personalized Saliency in Task-Oriented Semantic Communications: Image Transmission and Performance Analysis](https://doi.org/10.1109/jsac.2022.3221990)
   - Use for: image transmission as task-oriented semantic compression.

### UAV Network Resilience

1. [A Hierarchical Detection and Response System to Enhance Security Against Lethal Cyber-Attacks in UAV Networks](https://doi.org/10.1109/tsmc.2017.2681698)
   - Use for: UAV network monitoring and operator response concept.

2. [Unjammable and Resilient Communications for UAV Swarms: A Hybrid FSO/mmWave Approach](https://doi.org/10.1109/gcet68529.2025.11450673)
   - Use for: resilient communication alternatives, with caution not to overbuild hardware scope for hackathon.

### Simulation / Digital Twin

1. [Urban Digital Twins for Sustainable Smart Cities: A Systematic Literature Review of UAV-Assisted MEC, Federated Intelligence, and Semantic Communications](https://doi.org/10.36227/techrxiv.176948217.76093650/v1)
   - Use for: digital-twin + UAV + semantic communications bridge, but likely broader than our defense demo.

## Design Implications for v0.6 Demo

### Keep the demo explainable

Use deterministic formulas and expose values:

- residual
- NIS
- uncertainty ellipse
- jamming hypothesis score
- raw bytes represented
- semantic bytes transmitted

### Avoid overclaiming

Do not say:

- "jamming location detected"
- "drone location is known exactly"
- "control is maintained under total denial"

Say:

- "jamming suspected"
- "position represented as uncertainty envelope"
- "semantic mission state survives; raw data waits for rejoin"

### Rebuild the data model first

Required v0.6 objects:

- `drone_assets`
- `flight_timelines`
- `navigation_estimates`
- `raw_observations`
- `edge_detections`
- `jamming_hypotheses`
- `semantic_events`
- `semantic_packets`
- `custody_chains`
- `rejoin_audits`

### Rebuild the UI around two views

1. 3D simulation:
   - physical drone movement
   - predicted vs reported path
   - uncertainty envelope
   - degradation case overlay

2. operator board:
   - link/GNSS health
   - residual/NIS
   - jamming hypothesis
   - packet routing
   - evidence/provenance

## Research Gaps

Need follow-up collection/reading:

1. Full-text reading for the 32 selected papers in `sdot_drone_top_paper_extraction_notes_20260704.md`.
2. Specific public-feature datasets for UAV RF/GNSS jamming detection. Initial source accessibility is now smoke-tested, but labeled tactical end-to-end timelines are still not public and should remain synthetic.
3. Three.js/WebGL references for uncertainty ellipsoid/cone visualization and operator-safe confidence display.
4. More C2/operator trust literature around false precision, uncertainty display, and warning fatigue.
5. Decide whether v0.7 validates against EuRoC/UZH-FPV/TartanAir/Mid-Air or remains fully synthetic.

Update:

The public GNSS/RF/link dataset scan is now captured in `sdot_drone_gnss_rf_link_dataset_catalog_20260704.md`. The conclusion is that public GNSS/RF datasets are useful for feature-range calibration and citations, but the end-to-end drone S-DOT mission timeline should remain synthetic.

Dataset smoke-test update:

`dataset_smoke_test_20260704_173915` checked 14 GNSS/RF/link candidates and confirmed 13 accessible metadata/page/API sources. The only failed source was `uav_lora_avalanche` due to a ScienceDirect HTTP 403. No large RF/IQ/UBX/RINEX source files were downloaded. For v0.7, prioritize Yunnan GNSS interference/spoofing or AERPAW Dataset-12 for small feature-range inspection before any broader ingestion.

## Immediate Next Engineering Step

Extend the v0.6 prototype into v0.7 using the generated dataset:

- dataset: `/Users/mollykim/projects/D4D/03_data/samples/sdot_drone_semantic_ops/mock_dataset.json`
- script: `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_sdot_drone_semantic_ops_dataset.py`

Recommended v0.7 additions:

- wind/weather factor in prediction uncertainty
- visual/VIO evidence placeholder
- Korean operator explanation panel for residual/NIS and packet priority
- packet decision formula display
- rejoin audit drilldown
- innovation/NIS detail object with thresholds and degrees of freedom
- packet priority component breakdown
- rejoin audit error budget

The public v0.5 COP should remain available as a reference, but it should no longer be treated as the primary S-DOT demo.

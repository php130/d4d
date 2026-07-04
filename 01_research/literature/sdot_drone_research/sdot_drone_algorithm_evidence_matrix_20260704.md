# S-DOT Drone Algorithm Evidence Matrix

- Date: 2026-07-04 KST
- Evidence base:
  - Initial metadata run: 1,343 deduped records
  - Snowball run: 446 new records
  - Merged metadata set: 1,789 records
- Scope: map literature evidence to implementable v0.6 demo modules.

## Status

This is a metadata-driven technical matrix, not a full paper-by-paper review. It uses paper titles, abstracts, metadata, and DOI/arXiv links to decide the first implementation basis. Full extraction notes should follow for the top 20-30 papers.

## Module 1: Flight State Prediction and Uncertainty Envelope

### Implementation

Use a simple kinematic model in local NED/ENU coordinates:

```text
p_{t+dt} = p_t + v_t * dt + 0.5 * a_t * dt^2 + wind_t * dt
```

Maintain uncertainty growth:

```text
sigma_pos(t)^2 =
  sigma_pos0^2
  + sigma_vel^2 * t^2
  + 0.25 * sigma_acc^2 * t^4
  + sigma_wind^2 * t^2
```

### Evidence

- [Design of an Extended Kalman Filter for UAV Localization](https://doi.org/10.1109/idc.2007.374554)
- [Semi-Aerodynamic Model Aided Invariant Kalman Filtering for UAV Full-State Estimation](http://arxiv.org/abs/2310.01844)
- [SMART-TRACK: A Novel Kalman Filter-Guided Sensor Fusion for Robust UAV Object Tracking in Dynamic Environments](https://doi.org/10.1109/jsen.2024.3505939)

### Demo Requirement

The 3D scene must not show one exact location after link loss. It must show:

- last confirmed state
- predicted path
- uncertainty cone/ellipse
- elapsed time since last reliable contact

## Module 2: GNSS-Denied / GNSS-Degraded Navigation Alternatives

### Implementation

The demo does not need to implement full visual localization, but it should show that alternatives exist and can become evidence sources:

- visual matching against orthophotos
- visual-inertial odometry
- terrain-aided navigation
- LiDAR/UWB/mechanical antenna alternatives
- graph-optimization-based sensor fusion

### Evidence

- [GNSS-denied geolocalization of UAVs by visual matching of onboard camera images with orthophotos](http://arxiv.org/abs/2103.14381v2)
- [Gnss-denied unmanned aerial vehicle navigation: analyzing computational complexity, sensor fusion, and localization methodologies](https://doi.org/10.1186/s43020-025-00162-z)
- [Tight Fusion of a Monocular Camera, MEMS-IMU, and Single-Frequency Multi-GNSS RTK for Precise Navigation in GNSS-Challenged Environments](https://doi.org/10.3390/rs11060610)
- [UAV Navigation With Monocular Visual Inertial Odometry Under GNSS-Denied Environment](https://doi.org/10.1109/tgrs.2023.3323519)
- [A Pragmatic Approach to the Design of Advanced Precision Terrain-Aided Navigation for UAVs and Its Verification](https://doi.org/10.3390/rs12091396)
- [GPS-denied navigation using location estimation and texel image correction](https://doi.org/10.1117/12.2664119)
- [GOMSF: Graph-Optimization Based Multi-Sensor Fusion for robust UAV Pose estimation](https://doi.org/10.1109/icra.2018.8460193)

### Demo Requirement

Represent these as `raw_observations` and `edge_detections`, not as full algorithms:

- `obs_imu_011`
- `obs_eoir_001`
- `det_nav_residual_001`
- future: `det_visual_match_001`

## Module 3: Residual / NIS Integrity Monitoring

### Implementation

Use normalized innovation squared:

```text
y_t = z_t - H_t * x_pred
S_t = H_t * P_pred * H_t^T + R_t
NIS = y_t^T * S_t^-1 * y_t
```

Thresholding:

- low NIS: expected noise
- high NIS: reported state inconsistent with prediction
- high NIS + GNSS/link degradation: `JAMMING_SUSPECTED`
- high NIS + nominal GNSS but IMU disagreement: `SPOOFING_SUSPECTED`

### Evidence

- [Two-Step Trajectory Spoofing Algorithm for Loosely Coupled GNSS/IMU and NIS Sequence Detection](https://doi.org/10.1109/access.2019.2927539)
- [GPS spoofing detection using RAIM with INS coupling](https://doi.org/10.1109/plans.2014.6851498)
- [GNSS Spoofing Detection Based on Coupled Visual/Inertial/GNSS Navigation System](https://doi.org/10.3390/s21206769)
- [GNSS Integrity Monitoring Schemes for Terrestrial Applications in Harsh Signal Environments](https://doi.org/10.1109/mits.2020.2994076)
- [Feasibility of Fault Exclusion Related to Advanced RAIM for GNSS Spoofing Detection](https://doi.org/10.33012/2017.15193)

### Demo Requirement

The operator board should show:

- residual in meters
- NIS
- threshold
- label
- evidence refs

Current v0.6 synthetic dataset already includes:

- residual: `166.01m`
- NIS: `25.0`
- event: `JAMMING_SUSPECTED`

## Module 4: Jamming / Spoofing Hypothesis Engine

### Implementation

Use a weighted diagnostic score:

```text
jamming_score =
  0.25 * gnss_quality_drop
  + 0.20 * link_quality_drop
  + 0.20 * normalized_position_residual
  + 0.15 * heartbeat_gap_score
  + 0.10 * imu_gnss_disagreement
  + 0.10 * context_risk
```

Labels:

- `normal_or_environmental`
- `navigation_degraded`
- `jamming_suspected`
- `severe_denial_suspected`

### Evidence

- [SemperFi: Anti-spoofing GPS Receiver for UAVs](https://doi.org/10.14722/ndss.2022.23071)
- [Detecting Signal Spoofing Attack in UAVs Using Machine Learning Models](https://doi.org/10.1109/access.2021.3089847)
- [Enhanced Machine Learning Ensemble Approach for Securing Small Unmanned Aerial Vehicles From GPS Spoofing Attacks](https://doi.org/10.1109/access.2024.3359700)
- [A Slowly Varying Spoofing Algorithm Avoiding Tightly-Coupled GNSS/IMU With Multiple Anti-Spoofing Techniques](https://doi.org/10.1109/tvt.2022.3174406)
- [Maximum-Likelihood Power-Distortion Monitoring for GNSS-Signal Authentication](https://doi.org/10.1109/taes.2018.2848318)
- [Capture of UAVs Through GPS Spoofing](https://doi.org/10.1109/gws.2018.8686727)

### Demo Requirement

Do not claim:

- emitter location
- confirmed jamming
- offensive EW inference

Use:

- `jamming_score`
- `jamming_suspected`
- caveat: defensive diagnostic hypothesis only

## Module 5: S-DOT Semantic Encoder

### Implementation

Convert large raw data into decision-relevant packets:

```text
raw EO/IR + telemetry + GNSS health + link logs
-> semantic event
-> NAV_HEALTH_CARD / LINK_HEALTH_CARD / REJOIN_AUDIT_CARD
```

### Evidence

- [Goal-Oriented Semantic Communications for 6G Networks](https://doi.org/10.1109/iotm.001.2300269)
- [Distributed Machine Learning for UAV Swarms: Computing, Sensing, and Semantics](https://doi.org/10.1109/jiot.2023.3341307)
- [Emerging Trends in UAVs: From Placement, Semantic Communications to Generative AI for Mission-Critical Networks](https://doi.org/10.1109/tce.2024.3434971)
- [Personalized Saliency in Task-Oriented Semantic Communications: Image Transmission and Performance Analysis](https://doi.org/10.1109/jsac.2022.3221990)

### Demo Requirement

Show byte economics:

- raw bytes represented
- semantic bytes sent
- decision: send/defer/hold local
- evidence refs preserved

Current v0.6 example:

- event: `evt_uav_s1_jamming_suspected`
- raw represented: `18,442,000 bytes`
- semantic packet: `920 bytes`
- packet tier: `NAV_HEALTH_CARD`

## Module 6: DDIL / Packet Router

### Implementation

Payload tier depends on network mode:

- `full_sync`: detailed state and raw snippets
- `delta_sync`: state deltas
- `semantic_summary`: semantic event cards
- `store_forward`: critical cards, raw cache held
- `local_only`: local logs only

### Evidence

- [A Hierarchical Detection and Response System to Enhance Security Against Lethal Cyber-Attacks in UAV Networks](https://doi.org/10.1109/tsmc.2017.2681698)
- [User-Centric View of Unmanned Aerial Vehicle Transmission Against Smart Attacks](https://doi.org/10.1109/tvt.2017.2785414)
- [Unjammable and Resilient Communications for UAV Swarms: A Hybrid FSO/mmWave Approach](https://doi.org/10.1109/gcet68529.2025.11450673)

### Demo Requirement

Network mode selector must directly change:

- packet survival
- semantic bytes sent
- held-local evidence
- rejoin audit requirements

## Module 7: Rejoin Audit / Provenance

### Implementation

When connectivity returns:

- compare predicted state to cached truth
- calculate discrepancy
- check whether truth stayed inside uncertainty envelope
- sync raw nav log before EO/IR snippets
- update trust/confidence

### Evidence

- [Provenance-Aware Knowledge Representation: A Survey of Data Models and Contextualized Knowledge Graphs](existing T3 queue; see earlier project notes)
- [GNSS Integrity Monitoring Schemes for Terrestrial Applications in Harsh Signal Environments](https://doi.org/10.1109/mits.2020.2994076)
- [GPS spoofing detection using RAIM with INS coupling](https://doi.org/10.1109/plans.2014.6851498)

### Demo Requirement

The demo should make uncertainty accountable:

- what HQ predicted
- what raw cache later showed
- what differed
- which semantic packet was justified at the time

## Module 8: 3D Simulation / Digital Twin

### Implementation

Use synthetic simulation, not real coordinates:

- planned route
- actual/simulated path
- predicted path
- uncertainty cone/ellipse
- drone FOV
- degraded GNSS/link zone as hypothesis overlay

### Evidence

- [Urban Digital Twins for Sustainable Smart Cities: A Systematic Literature Review of UAV-Assisted MEC, Federated Intelligence, and Semantic Communications](https://doi.org/10.36227/techrxiv.176948217.76093650/v1)
- [UAV-Assisted MEC / digital twin records from metadata run](file:///Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/20260704_164224/sdot_drone_literature_records.csv)

### Demo Requirement

The 3D view is not decoration. It is the primary proof that:

- drone continues physically
- HQ state becomes predictive
- uncertainty expands
- raw data cannot fully move
- semantic packets maintain decision value

## Implementation Priority

1. Implement 3D drone path and uncertainty envelope.
2. Display residual/NIS and jamming hypothesis score.
3. Add packet inspector using current v0.6 dataset.
4. Add rejoin audit panel.
5. Add case switcher: normal, link-degraded, GNSS degraded, spoofing-like, rejoin.
6. Add paper/evidence tooltip or appendix for algorithm basis.

## Gaps To Close

1. Full reading notes for the top 20-30 papers.
2. Slower arXiv retry for later topics.
3. More primary sources for military DDIL/DTN doctrine.
4. Public benchmark datasets for drone trajectories and GNSS-degraded simulation.
5. Visual references for 3D uncertainty ellipsoid/cone rendering.

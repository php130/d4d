# S-DOT Drone Top Paper Extraction Notes

- Date: 2026-07-04 KST
- Corpus: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/final_20260704_170558/sdot_drone_literature_records_final.json`
- Corpus size: 1,900 records
- Scope: first-pass extraction from titles, abstracts, metadata, DOI/arXiv links, and project evidence mapping.
- Safety boundary: use spoofing/jamming papers only for defensive diagnosis, integrity monitoring, uncertainty handling, and operator warning. Do not implement offensive spoofing, emitter localization, or attack optimization.

## What This Means For The Hackathon

The S-DOT demo should be framed as:

> A drone mission continuity layer that converts degraded raw telemetry, GNSS/link health, sensor residuals, and local evidence into compact semantic packets so the operator can maintain a probabilistic operating picture under DDIL and jamming-suspected conditions.

The strongest technical spine is:

1. Predict drone state from the last trusted state using a kinematic/EKF-style model.
2. Track uncertainty growth instead of showing a fake exact position.
3. Compare reported GNSS/location against predicted and inertial/visual evidence.
4. Use residual/NIS/RAIM-style integrity checks to trigger `GNSS_DEGRADED`, `JAMMING_SUSPECTED`, or `SPOOFING_SUSPECTED`.
5. Compress raw observations into task-relevant S-DOT semantic packets.
6. Store raw evidence locally when links are degraded.
7. On rejoin, audit predicted state versus cached truth and revise trust.

## Implementation Spine

### State Prediction

Use local ENU/NED coordinates for the demo:

```text
p(t + dt) = p(t) + v(t) * dt + 0.5 * a(t) * dt^2 + wind(t) * dt
```

For uncertainty:

```text
sigma_pos(t)^2 =
  sigma_pos0^2
  + sigma_vel^2 * t^2
  + 0.25 * sigma_acc^2 * t^4
  + sigma_wind^2 * t^2
  + sigma_link_gap^2
```

### Residual And Integrity

Use the Kalman innovation form:

```text
y_t = z_t - H_t * x_pred
S_t = H_t * P_pred * H_t^T + R_t
NIS_t = y_t^T * S_t^-1 * y_t
```

Operator-level interpretation:

| Pattern | Meaning In Demo |
|---|---|
| Low residual, low NIS | Location report is consistent |
| High residual, high NIS, poor GNSS CN0 | GNSS degradation or jamming suspected |
| High residual, high NIS, GNSS appears nominal, IMU/VIO disagreement | spoofing-like inconsistency suspected |
| Link heartbeat gap + growing uncertainty | predictive-only COP mode |

### S-DOT Packet Decision

Semantic packet type should be selected by mission relevance and network condition:

```text
packet_priority =
  mission_criticality
  + nav_integrity_risk
  + link_degradation
  + time_since_contact
  + operator_relevance
  - raw_payload_cost
```

Minimum packet fields:

```json
{
  "asset_id": "UAV-S1",
  "event_type": "JAMMING_SUSPECTED",
  "last_confirmed_time": "synthetic",
  "predicted_position": {"x_m": 0, "y_m": 0, "z_m": 120},
  "uncertainty_radius_m": 180,
  "residual_m": 166.01,
  "nis": 25.0,
  "link_state": "intermittent",
  "gnss_state": "degraded",
  "recommended_operator_action": "continue mission under predictive-only mode",
  "evidence_refs": ["obs_imu_011", "obs_gnss_017", "obs_link_009"]
}
```

## Priority Papers And Extraction Notes

### 1. SemperFi: Anti-spoofing GPS Receiver for UAVs

- Link: https://doi.org/10.14722/ndss.2022.23071
- Module: GNSS spoofing detection and recovery
- Why it matters: shows UAV GPS can be attacked and that recovery requires more than simple anomaly warning.
- Demo use: justify a `SPOOFING_SUSPECTED` state that falls back to predicted/VIO/IMU evidence instead of trusting raw GNSS.
- Algorithm hook: EKF-based failsafe, legitimate signal tracking, recovery logic.
- Caution: do not reproduce attack mechanics; cite only for defensive anti-spoofing need.

### 2. GPS Spoofing Detection Using RAIM With INS Coupling

- Link: https://doi.org/10.1109/plans.2014.6851498
- Module: RAIM/INS residual integrity
- Why it matters: provides a clean basis for residual-based detection using GPS and inertial navigation.
- Demo use: implement the NIS/residual panel and explain why high residual means the operator should distrust the location report.
- Algorithm hook: residual-based RAIM monitor coupled with INS.
- Caution: use as integrity monitoring, not as a claim of confirmed attacker identity.

### 3. Two-Step Trajectory Spoofing Algorithm For Loosely Coupled GNSS/IMU And NIS Sequence Detection

- Link: https://doi.org/10.1109/access.2019.2927539
- Module: NIS integrity thresholding
- Why it matters: explicitly connects GNSS/IMU fusion and NIS sequence detection.
- Demo use: support the `nis`, `threshold`, `residual_m`, and `spoofing_like_inconsistency` fields.
- Algorithm hook: innovation sequence monitoring.
- Caution: paper includes offensive spoofing framing. Keep the demo on defensive detection and audit.

### 4. GNSS Integrity Monitoring Schemes For Terrestrial Applications In Harsh Signal Environments

- Link: https://doi.org/10.1109/mits.2020.2994076
- Module: integrity monitoring under multipath/NLOS/degraded signals
- Why it matters: not every GNSS anomaly is jamming. Urban multipath and NLOS can degrade GNSS too.
- Demo use: add an explicit caveat field: `hypothesis: jamming_suspected`, not `jamming_confirmed`.
- Algorithm hook: integrity risk, measurement-domain and position-domain monitoring.
- Caution: helps avoid overclaiming.

### 5. Recent Advances On Jamming And Spoofing Detection In GNSS

- Link: https://doi.org/10.3390/s24134210
- Module: GNSS threat taxonomy
- Why it matters: provides a broad survey of modern detection methods.
- Demo use: create an appendix table for `jamming`, `spoofing`, `multipath`, `sensor_fault`, and `normal degradation`.
- Algorithm hook: classify detection evidence by signal quality, navigation consistency, and multi-sensor comparison.
- Caution: survey-level evidence, not a single implemented method.

### 6. GNSS/GPS Spoofing And Jamming Identification Using Machine Learning And Deep Learning

- Link: http://arxiv.org/abs/2501.02352
- Module: ML-based threat classification
- Why it matters: supports a later v0.7 classifier when enough labeled synthetic data exists.
- Demo use: for now, show rule-based scoring; mark ML classifier as future extension.
- Algorithm hook: supervised classifier over signal/navigation features.
- Caution: ML needs labeled data. Do not imply production readiness from a small synthetic dataset.

### 7. Detecting Signal Spoofing Attack In UAVs Using Machine Learning Models

- Link: https://doi.org/10.1109/access.2021.3089847
- Module: lightweight ML spoofing detection
- Why it matters: proposes UAV spoofing detection using ML feature sets.
- Demo use: justify the `feature_vector` object in future dataset versions.
- Algorithm hook: SVM and model comparison over navigation/sensor features.
- Caution: hackathon v0.6 should not depend on a trained ML model unless labels are controlled.

### 8. Enhanced Machine Learning Ensemble Approach For Securing Small UAVs From GPS Spoofing Attacks

- Link: https://doi.org/10.1109/access.2024.3359700
- Module: small-UAV spoofing detection without extra heavy hardware
- Why it matters: aligns with edge constraints and small drone payload limits.
- Demo use: support the idea that local feature-based detection is plausible on constrained platforms.
- Algorithm hook: ensemble classifier over GPS/sensor observations.
- Caution: treat as optional v0.8, after rule-based integrity and synthetic labels are stable.

### 9. PerDet: Machine-Learning-Based UAV GPS Spoofing Detection Using Perception Data

- Link: https://doi.org/10.3390/rs14194925
- Module: perception-data-based detection
- Why it matters: uses non-GNSS perception data to compensate for GPS weakness.
- Demo use: add `obs_camera`, `obs_imu`, `obs_barometer`, and `obs_magnetometer` evidence slots.
- Algorithm hook: feature fusion from onboard perception streams.
- Caution: do not claim detection from video alone in v0.6.

### 10. 3D Radio Map-Based GPS Spoofing Detection And Mitigation For Cellular-Connected UAVs

- Link: https://doi.org/10.1109/tmlcn.2023.3316150
- Module: cellular-connected UAV integrity cross-check
- Why it matters: relevant to the KT/civil-infra angle, but in a safer drone-network framing.
- Demo use: later add `civil_bearer_observation` as a weak evidence source, not a guaranteed military priority network.
- Algorithm hook: compare expected radio map/channel context with claimed UAV state.
- Caution: real carrier data is not public; use synthetic radio-map cells only.

### 11. GNSS Jamming Detection Of UAV Ground Control Station Using Random Matrix Theory

- Link: https://doi.org/10.1016/j.icte.2020.10.001
- Module: jamming detection from signal statistics
- Why it matters: supports the idea that jamming can be inferred statistically, not only by manual operator judgment.
- Demo use: add `signal_statistic_score` as a future field, separate from position residual.
- Algorithm hook: hypothesis testing on signal statistics.
- Caution: do not infer jammer location.

### 12. A Survey On Coping With Intentional Interference In Satellite Navigation For Manned And Unmanned Aircraft

- Link: https://doi.org/10.1109/comst.2019.2949178
- Module: interference taxonomy and mitigation overview
- Why it matters: good background for why GNSS denial is a real flight safety problem.
- Demo use: cite in the pitch deck problem background.
- Algorithm hook: organize mitigations into detection, exclusion, fusion, and fallback navigation.
- Caution: broad survey, not an implementation recipe.

### 13. A Review Of UAV Autonomous Navigation In GPS-Denied Environments

- Link: https://doi.org/10.1016/j.robot.2023.104533
- Module: GPS-denied navigation landscape
- Why it matters: supports the shift from ground-unit COP to drone-first S-DOT.
- Demo use: justify visual, inertial, LiDAR, UWB, terrain, and cooperative localization evidence types.
- Algorithm hook: navigation stack taxonomy.
- Caution: broad review; use to choose modules, not to claim final algorithm performance.

### 14. GNSS-Denied UAV Indoor Navigation With UWB Incorporated Visual Inertial Odometry

- Link: https://doi.org/10.1016/j.measurement.2022.112256
- Module: VIO plus UWB fusion
- Why it matters: shows GNSS-denied navigation can combine short-term visual-inertial estimation with another ranging source.
- Demo use: future case for indoor/urban canyon operations.
- Algorithm hook: VIO + UWB fusion.
- Caution: UWB infrastructure may not exist in the hackathon scenario. Keep as optional evidence source.

### 15. UAV Navigation With Monocular Visual Inertial Odometry Under GNSS-Denied Environment

- Link: https://doi.org/10.1109/tgrs.2023.3323519
- Module: monocular VIO for GNSS-denied UAVs
- Why it matters: direct support for an onboard visual-inertial fallback.
- Demo use: represent VIO as a local estimate with drift, not as exact truth.
- Algorithm hook: point-line fusion, adaptive backend optimization.
- Caution: monocular VIO can drift; show confidence decay.

### 16. GNSS-Denied Geolocalization Of UAVs By Visual Matching Of Onboard Camera Images With Orthophotos

- Link: http://arxiv.org/abs/2103.14381v2
- Module: visual geolocalization against maps
- Why it matters: supports the concept that a drone can produce location hypotheses even without GNSS.
- Demo use: add `visual_match_candidate` as semantic evidence when EO imagery aligns with a map tile.
- Algorithm hook: Monte Carlo localization and image-to-map matching.
- Caution: public map imagery may be stale; use synthetic or open non-sensitive map tiles.

### 17. A Pragmatic Approach To The Design Of Advanced Precision Terrain-Aided Navigation For UAVs And Its Verification

- Link: https://doi.org/10.3390/rs12091396
- Module: terrain-referenced navigation
- Why it matters: helps explain non-GNSS location recovery using terrain and INS.
- Demo use: optional terrain/elevation cue in a non-sensitive synthetic AOI.
- Algorithm hook: INS/GNSS/TRN integrated navigation with filtering.
- Caution: Korea-specific elevation/military route use should be avoided in public demo.

### 18. GPS-Denied Navigation Using Location Estimation And Texel Image Correction

- Link: https://doi.org/10.1117/12.2664119
- Module: image correction and GPS-denied location estimation
- Why it matters: another concrete example of vision-supported GPS-denied navigation.
- Demo use: future visual matching case in the 3D simulator.
- Algorithm hook: image-based correction to location estimates.
- Caution: metadata-level extraction only; read full paper before implementation.

### 19. GOMSF: Graph-Optimization Based Multi-Sensor Fusion For Robust UAV Pose Estimation

- Link: https://doi.org/10.1109/icra.2018.8460193
- Module: graph optimization for pose fusion
- Why it matters: provides a stronger alternative to a simple EKF when fusing VIO and global references.
- Demo use: keep EKF-like implementation for v0.6, cite graph optimization as v1.0 path.
- Algorithm hook: align local VIO frame with global reference through graph optimization.
- Caution: likely too much for hackathon implementation unless using an existing library.

### 20. An Integrated GNSS/LiDAR-SLAM Pose Estimation Framework For Large-Scale Map Building In Partially GNSS-Denied Environments

- Link: https://doi.org/10.1109/tim.2020.3024405
- Module: GNSS/LiDAR-SLAM switching/fusion
- Why it matters: good model for partially denied environments, not only full blackout.
- Demo use: show `mode: full_sync`, `degraded`, `predictive_only`, and `rejoin` transitions.
- Algorithm hook: use GNSS when reliable, LiDAR-SLAM when GNSS is denied, correct drift on rejoin.
- Caution: LiDAR data is heavy; semantic packets should summarize, not stream raw point clouds.

### 21. Design Of An Extended Kalman Filter For UAV Localization

- Link: https://doi.org/10.1109/idc.2007.374554
- Module: EKF fallback localization
- Why it matters: simple and explainable basis for predicted-state demo.
- Demo use: implement constant-velocity/acceleration prediction with uncertainty growth.
- Algorithm hook: EKF prediction and measurement update.
- Caution: demo should label state as prediction once GPS/link is stale.

### 22. Semi-Aerodynamic Model Aided Invariant Kalman Filtering For UAV Full-State Estimation

- Link: http://arxiv.org/abs/2310.01844
- Module: aerodynamic and wind-aware state estimation
- Why it matters: supports adding wind and airspeed terms to the prediction model.
- Demo use: include weather/wind as an uncertainty growth factor.
- Algorithm hook: invariant Kalman filtering on Lie groups with multi-rate sensors.
- Caution: implement simplified kinematics first; full InEKF is a later research track.

### 23. SMART-TRACK: A Novel Kalman Filter-Guided Sensor Fusion For Robust UAV Object Tracking In Dynamic Environments

- Link: https://doi.org/10.1109/jsen.2024.3505939
- Module: tracking under intermittent measurements
- Why it matters: conceptually close to DDIL, where measurements vanish and return.
- Demo use: show prediction during gaps and reacquisition after rejoin.
- Algorithm hook: high-frequency Kalman estimates guide reacquisition.
- Caution: object tracking differs from self-localization, but the gap/reacquisition pattern transfers.

### 24. Robust Localization For Secure Navigation Of UAV Formations Under GNSS Spoofing Attack

- Link: https://doi.org/10.1109/tase.2022.3208662
- Module: cooperative localization and formation redundancy
- Why it matters: S-DOT can extend from one drone to swarm/team operation.
- Demo use: future multi-drone case where neighboring assets cross-check location hypotheses.
- Algorithm hook: distributed procedure using redundancy in sensing information.
- Caution: do not implement adversarial tactics; use for defensive redundancy.

### 25. Distributed Machine Learning For UAV Swarms: Computing, Sensing, And Semantics

- Link: https://doi.org/10.1109/jiot.2023.3341307
- Module: UAV swarm semantics and distributed learning
- Why it matters: connects sensing, edge intelligence, communication, and semantic summarization.
- Demo use: justify why local edge inference sends events instead of raw video.
- Algorithm hook: distributed learning and semantic communication for UAV swarms.
- Caution: do not overbuild swarm ML for v0.6.

### 26. Goal-Oriented Semantic Communications For 6G Networks

- Link: https://doi.org/10.1109/iotm.001.2300269
- Module: S-DOT semantic packet philosophy
- Why it matters: gives a clear theoretical basis for task/goal-oriented communication.
- Demo use: packet inspector should compare raw bytes versus mission-relevant semantic bytes.
- Algorithm hook: semantic level and effectiveness level, not just bit-level throughput.
- Caution: adapt concept to tactical DDIL without claiming 6G deployment.

### 27. Personalized Saliency In Task-Oriented Semantic Communications: Image Transmission And Performance Analysis

- Link: https://doi.org/10.1109/jsac.2022.3221990
- Module: image saliency and semantic compression
- Why it matters: provides a concrete image-transmission example for sending the important parts first.
- Demo use: future EO/IR packet can send object/event summary before raw frames.
- Algorithm hook: saliency-aware semantic encoding.
- Caution: current demo can show simulated byte savings; real saliency model comes later.

### 28. Emerging Trends In UAVs: From Placement, Semantic Communications To Generative AI For Mission-Critical Networks

- Link: https://doi.org/10.1109/tce.2024.3434971
- Module: UAVs in mission-critical networks
- Why it matters: bridges UAV placement, semantic communications, reliability, and latency constraints.
- Demo use: pitch deck evidence for why drone S-DOT belongs in T3/S-DOT, not only T1 autonomy.
- Algorithm hook: knowledge-driven/semantic approaches for mission-critical network constraints.
- Caution: high-level review.

### 29. A Novel Data Forwarding Strategy For A Drone Delay Tolerant Network With Range Extension

- Link: https://doi.org/10.3390/electronics8060659
- Module: DTN/store-forward routing
- Why it matters: supports store-forward behavior when links are intermittent.
- Demo use: implement packet states: `sent`, `deferred`, `held_local`, `sync_on_rejoin`.
- Algorithm hook: waypoint-aware data forwarding.
- Caution: delivery-drone assumptions differ from tactical drone missions; use the DTN principle only.

### 30. A Hierarchical Detection And Response System To Enhance Security Against Lethal Cyber-Attacks In UAV Networks

- Link: https://doi.org/10.1109/tsmc.2017.2681698
- Module: UAV network anomaly response
- Why it matters: supports multi-level detection at asset and ground-station layers.
- Demo use: separate drone-local diagnosis from command-board diagnosis.
- Algorithm hook: classify normal, abnormal, suspect, malicious behavior.
- Caution: cybersecurity scope is broader than GNSS/link degradation.

### 31. User-Centric View Of Unmanned Aerial Vehicle Transmission Against Smart Attacks

- Link: https://doi.org/10.1109/tvt.2017.2785414
- Module: adaptive transmission under attack
- Why it matters: supports operator-facing risk-aware transmission decisions.
- Demo use: network mode should affect packet priority and transmit/hold decisions.
- Algorithm hook: game/RL framing for jamming/spoofing/eavesdropping risk.
- Caution: do not build attacker optimization in public demo.

### 32. Unjammable And Resilient Communications For UAV Swarms: A Hybrid FSO/mmWave Approach

- Link: https://doi.org/10.1109/gcet68529.2025.11450673
- Module: resilient bearer alternatives
- Why it matters: useful for the PACE/bearer ladder concept.
- Demo use: show alternate bearers as capability slots, not assumed availability.
- Algorithm hook: hybrid optical/mmWave communication.
- Caution: physical alignment and weather constraints are nontrivial; do not claim universal resilience.

## Immediate Design Decisions

### Keep In v0.6

- synthetic drone trajectory
- last trusted state
- predicted state
- uncertainty envelope
- residual/NIS
- jamming/spoofing suspicion labels
- raw-vs-semantic byte comparison
- packet hold/send/store-forward decisions
- rejoin audit

### Add In v0.7

- wind/weather parameter in prediction
- visual/VIO evidence placeholder
- configurable GNSS quality metrics
- packet priority formula displayed in Korean UI
- synthetic radio-map/civil-bearer observation as weak evidence
- operator explanation panel: "why this packet was sent"

### Do Not Add To Public Demo

- real military routes or assets
- real EW emitter location
- attack recipes
- raw sensitive data redistribution
- claims of confirmed jamming from synthetic evidence

## Data Implications

### Required Synthetic Data

- `flight_truth`: hidden simulated truth for audit
- `reported_gnss`: potentially degraded/spoofing-like measurements
- `imu_dead_reckoning`: drift-prone local estimate
- `link_health`: latency, packet loss, heartbeat gap
- `gnss_health`: CN0 proxy, satellite count proxy, fix type
- `weather_context`: wind vector, visibility, precipitation proxy
- `semantic_events`: compressed event cards
- `semantic_packets`: byte-size, priority, evidence refs, transmission status
- `rejoin_audit`: predicted-vs-truth discrepancy

### Optional Public Datasets For Later Validation

- EuRoC MAV Dataset: visual-inertial baseline
- UZH-FPV Dataset: aggressive flight
- TartanAir / Mid-Air: synthetic visual and weather variation
- Blackbird: aggressive UAV perception
- MUN-FRL VIL: camera/LiDAR/IMU/RTK
- AirSim or PX4/Gazebo: controlled simulation generation

See:

- `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_public_dataset_simulator_catalog_20260704.md`

## Next Reading Order

1. RAIM/INS and NIS papers: implement defensible residual panel.
2. GPS-denied navigation reviews: define evidence channels.
3. semantic communications papers: refine S-DOT packet schema.
4. DDIL/DTN routing papers: refine send/hold/store-forward behavior.
5. simulator/dataset docs: decide whether v0.7 uses public trajectory data or remains synthetic.

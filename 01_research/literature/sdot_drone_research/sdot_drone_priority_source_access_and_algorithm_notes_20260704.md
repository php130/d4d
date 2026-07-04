# S-DOT Drone Priority Source Access And Algorithm Notes

- Date: 2026-07-04 KST
- Purpose: identify which priority papers/sources are strong enough to support the v0.7 demo logic.
- Scope: source access check plus implementation-oriented extraction.
- Method: official paper pages, open PDFs/HTML where available, arXiv pages, DOI/ION abstracts, and existing 1,900-record metadata corpus.

## Source Access Status

| Priority | Source | Access Status | Best Use In Demo | Source |
|---|---|---|---|---|
| P0 | SemperFi: Anti-spoofing GPS Receiver for UAVs | Official NDSS page and PDF accessible | spoofing-resistant UAV framing; defensive recovery/diagnostic motivation | https://www.ndss-symposium.org/ndss-paper/auto-draft-220/ |
| P0 | GPS Spoofing Detection Using RAIM with INS Coupling | Official ION abstract accessible; full paper requires ION access/credit | residual/RAIM framing; integrity-risk wording | https://www.ion.org/publications/abstract.cfm?articleID=11749 |
| P0 | Recent Advances on Jamming and Spoofing Detection in GNSS | MDPI full HTML accessible | taxonomy of jamming/spoofing detection methods; ML caveat | https://www.mdpi.com/1424-8220/24/13/4210 |
| P0 | A review of UAV autonomous navigation in GPS-denied environments | open-access PDF accessible | navigation method taxonomy and simulator/metric framing | https://sure.sunderland.ac.uk/id/eprint/16820/1/1-s2.0-S0921889023001720-main.pdf |
| P0 | Goal-Oriented Semantic Communications for 6G Networks | arXiv full text accessible | semantic/effectiveness-level communication theory | https://arxiv.org/abs/2210.09372 |
| P0 | GNSS-denied geolocalization of UAVs by visual matching of onboard camera images with orthophotos | arXiv full text accessible | visual-map localization evidence source | https://arxiv.org/abs/2103.14381 |
| P1 | A Pragmatic Approach to the Design of Advanced Precision Terrain-Aided Navigation for UAVs and Its Verification | MDPI full HTML accessible | INS/GNSS/TRN fallback and federated filter framing | https://www.mdpi.com/2072-4292/12/9/1396 |
| P1 | Personalized Saliency in Task-Oriented Semantic Communications | arXiv full text accessible | EO/IR semantic compression and task-oriented packet design | https://arxiv.org/abs/2209.12274 |
| P1 | GNSS/GPS Spoofing and Jamming Identification Using ML/DL | arXiv full text accessible | future labeled classifier track, not v0.7 core | https://arxiv.org/abs/2501.02352 |
| P1 | TartanAir: A Dataset to Push the Limits of Visual SLAM | arXiv + official dataset accessible | simulation validation for visual/VIO/weather conditions | https://arxiv.org/abs/2003.14338 |
| P1 | AirSim: High-Fidelity Visual and Physical Simulation | arXiv + GitHub/docs accessible | future controlled simulation source | https://arxiv.org/abs/1705.05065 |
| P2 | Two-Step Trajectory Spoofing Algorithm for Loosely Coupled GNSS/IMU and NIS Sequence Detection | OpenAlex says OA; only metadata/abstract-level access confirmed locally | NIS concept only; avoid offensive algorithm detail | https://doi.org/10.1109/access.2019.2927539 |
| P2 | Distributed Machine Learning for UAV Swarms | DOI metadata; full text not confirmed locally | longer-term swarm/edge semantics framing | https://doi.org/10.1109/jiot.2023.3341307 |
| P2 | UAV Navigation With Monocular VIO Under GNSS-Denied Environment | DOI metadata; full text not confirmed locally | future VIO algorithm detail | https://doi.org/10.1109/tgrs.2023.3323519 |

## Practical Source Ranking

For the hackathon, use P0/P1 sources as the defensible basis. P2 sources can remain in the bibliography, but do not rely on them for claims unless full text is obtained later.

Recommended source stack:

1. **SemperFi + RAIM/INS + Recent GNSS detection survey** for navigation-integrity threat framing.
2. **GPS-denied navigation review + visual matching + terrain-aided navigation** for fallback navigation evidence sources.
3. **Goal-oriented semantic communications + personalized saliency** for S-DOT packet philosophy.
4. **TartanAir/AirSim/EuRoC/UZH-FPV** for validation/simulation resources.

## Algorithm Notes

### A. Prediction Is A Confidence Envelope, Not A Tracked Truth

Use the command board to show:

- `last_trusted_state`
- `predicted_state`
- `reported_state`
- `uncertainty_ellipse`
- `time_since_trusted_contact_sec`

The operator should see that the asset continues to move physically while HQ confidence decays. This is stronger than pretending that the drone's exact location remains known.

Recommended v0.7 formula:

```text
x_t = [p_N, p_E, p_D, v_N, v_E, v_D, yaw, battery, wind_N, wind_E]

p_{t+dt} = p_t + v_t * dt + 0.5 * a_t * dt^2 + wind_t * dt
v_{t+dt} = v_t + a_t * dt
```

Uncertainty:

```text
P_pred = F * P_prev * F^T + Q

sigma_pos^2 =
  sigma_pos0^2
  + sigma_vel^2 * t_gap^2
  + 0.25 * sigma_acc^2 * t_gap^4
  + sigma_wind^2 * t_gap^2
  + sigma_bearer_gap^2
```

Implementation decision:

- v0.6 can remain deterministic.
- v0.7 should store `P_pred` or a simplified covariance proxy, not only `uncertainty_ellipse_m`.

### B. Integrity Check Uses Innovation, Not Raw Distance Alone

The current demo uses residual meters and simplified NIS. v0.7 should represent the actual innovation components:

```text
y = z - H * x_pred
S = H * P_pred * H^T + R
NIS = y^T * S^-1 * y
```

Recommended threshold handling:

| Measurement Dimension | 95% Chi-square | 99% Chi-square | Use |
|---|---:|---:|---|
| 2D position | 5.99 | 9.21 | current v0.6 threshold maps to 2D 99% |
| 3D position | 7.81 | 11.34 | use if altitude is part of the measurement |

Operator language:

- Korean UI should say `측정값이 예측 가능한 범위를 벗어남`.
- Avoid `jamming confirmed`.
- Use `교란 의심`, `위치 무결성 저하`, `GNSS-like 위치 불일치`.

### C. Jamming/Spoofing Is A Hypothesis Layer

Do not infer source, emitter, or intent. S-DOT should produce a defensive diagnostic score.

Recommended v0.7 score:

```text
hypothesis_score =
  0.20 * gnss_cn0_drop
  + 0.15 * satellite_count_drop
  + 0.15 * hdop_vdop_degradation
  + 0.20 * min(1, NIS / NIS_critical)
  + 0.10 * heartbeat_gap_score
  + 0.10 * packet_loss_score
  + 0.10 * imu_vio_gnss_disagreement
```

Labeling:

```text
0.00-0.35 normal_or_environmental
0.35-0.60 navigation_degraded
0.60-0.80 jamming_or_spoofing_suspected
0.80-1.00 severe_navigation_integrity_risk
```

This broadens the current v0.6 score by splitting GNSS quality into interpretable subfeatures.

### D. Semantic Packet Priority Should Be Explainable

Goal-oriented semantic communication supports the idea that the payload should be judged by task effectiveness, not raw bit fidelity.

Recommended v0.7 packet score:

```text
packet_priority =
  0.25 * flight_safety
  + 0.22 * navigation_integrity_risk
  + 0.18 * mission_relevance
  + 0.15 * link_survivability
  + 0.10 * time_sensitivity
  + 0.10 * audit_value
```

Routing:

| Priority | Full Sync | Delta Sync | Semantic Summary | Store Forward | Local Only |
|---:|---|---|---|---|---|
| >= 0.80 | send raw excerpt + semantic | send semantic + key deltas | send semantic | queue critical card | local cache |
| 0.55-0.80 | send semantic | send semantic | send if bytes fit | queue | local cache |
| 0.30-0.55 | send low-priority | defer | defer | queue | local cache |
| < 0.30 | defer | defer | hold | hold | local cache |

Operator UI should show the score components, not only the final score.

### E. Visual/VIO/Terrain Evidence Should Be Weak Evidence Sources

For v0.7, do not implement full visual localization unless time permits. Add the evidence slots first:

```json
{
  "evidence_id": "vio_uav_s1_001",
  "source_type": "VISUAL_INERTIAL_ODOMETRY",
  "drift_rate_m_per_min": 18.0,
  "supports_state_ref": "nav_pred_uav_s1_t080",
  "confidence": 0.58,
  "limitations": ["lighting_change", "texture_poor_scene"]
}
```

```json
{
  "evidence_id": "visual_match_uav_s1_001",
  "source_type": "ORTHOIMAGE_MATCH",
  "candidate_position_m": {"north": 830, "east": 145, "down": -118},
  "match_score": 0.62,
  "map_age_days": 180,
  "confidence": 0.50
}
```

This lets the demo say: "there are alternate local evidence sources, but each has uncertainty."

### F. Rejoin Audit Is A Core Differentiator

Rejoin audit should verify:

- what HQ predicted during denial
- what the drone cached locally
- whether actual/cached truth stayed inside the predicted envelope
- which semantic packets were justified at the time
- which thresholds were too sensitive or too loose

Minimum v0.7 audit metrics:

```text
discrepancy_m = distance(predicted_position, cached_truth_position)
contained_in_envelope = discrepancy_m <= uncertainty_major_m
semantic_justification = evidence_refs available and timestamped
threshold_adjustment = new_threshold - old_threshold
```

## v0.7 Paper-To-Feature Mapping

| Demo Feature | Primary Evidence | Implementation |
|---|---|---|
| GNSS spoofing/jamming problem framing | SemperFi, Recent Advances GNSS survey | show `GNSS/link integrity risk`, not exact attacker conclusion |
| Residual/NIS panel | RAIM/INS, NIS sequence papers | store `innovation_vector`, `S`, `NIS`, `df`, threshold |
| GPS-denied navigation fallback | GPS-denied navigation review, visual matching, terrain-aided nav | add VIO/visual/TRN evidence placeholders |
| Semantic packet economics | Goal-oriented SemCom, personalized saliency | raw bytes vs semantic bytes; packet priority by task value |
| 3D sim validation path | TartanAir, AirSim, EuRoC, UZH-FPV | keep synthetic v0.6; add optional dataset validation path |

## Claims Safe For Presentation

Safe:

- "S-DOT maintains mission continuity under degraded communications by transmitting task-relevant semantic state."
- "The command board represents location as a prediction envelope when telemetry is stale."
- "High residual/NIS plus degraded GNSS/link health raises a defensive jamming/spoofing suspicion."
- "Raw evidence is cached and reconciled after rejoin."

Not safe:

- "We detect jammer location."
- "We guarantee drone control under total denial."
- "We identify enemy EW assets."
- "The predicted position is ground truth."

## Next Full-Read Targets

1. Obtain full access to the RAIM/INS PLANS paper if possible.
2. Verify full text for Two-Step NIS sequence detection from IEEE Access or author manuscript.
3. Read the SemperFi PDF in detail for architecture and evaluation caveats.
4. Read the MDPI terrain-aided navigation details for federated filter cases.
5. Extract exact data requirements from arXiv semantic communication papers for packet scoring.

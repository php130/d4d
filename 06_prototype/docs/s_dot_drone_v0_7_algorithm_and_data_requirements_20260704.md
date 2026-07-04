# S-DOT Drone v0.7 Algorithm And Data Requirements

- Date: 2026-07-04 KST
- Based on: v0.6 prototype, 1,900-record literature corpus, priority source access note
- Goal: turn the current 3D demo from a plausible simulation into a more defensible algorithm-backed demo.

## v0.7 Product Framing

S-DOT is not just compression. It is a mission-continuity layer for unmanned assets under DDIL and navigation uncertainty.

v0.7 should show four linked claims:

1. A drone can continue moving while command only has stale/degraded data.
2. Command should see prediction envelopes, not fake exact positions.
3. S-DOT can prioritize semantic packets when raw telemetry/video cannot move.
4. Rejoin audit can compare predictions against cached truth and improve trust.

## Required Data Additions

### 1. Prediction Model Configuration

Add:

```json
{
  "prediction_model_config": {
    "model_id": "cv_wind_ekf_proxy_v0_7",
    "frame": "local_ned",
    "state_vector": ["p_n", "p_e", "p_d", "v_n", "v_e", "v_d", "yaw", "battery", "wind_n", "wind_e"],
    "process_noise": {
      "sigma_position_m": 18.0,
      "sigma_velocity_mps": 0.9,
      "sigma_acceleration_mps2": 0.08,
      "sigma_wind_mps": 1.2,
      "sigma_bearer_gap_m": 20.0
    },
    "notes_ko": "단절 시간이 길어질수록 위치 불확실성이 커지는 예측 모델입니다."
  }
}
```

Reason:

- Current v0.6 stores `prediction_model` as a string.
- v0.7 needs visible parameters so judges can see the calculation basis.

### 2. GNSS Quality Metrics

Add to each relevant timestep or observation:

```json
{
  "gnss_quality_metrics": {
    "fix_type": "degraded",
    "satellite_count": 5,
    "cn0_dbhz_mean": 24.0,
    "hdop": 3.8,
    "vdop": 5.1,
    "quality_bucket": "poor",
    "staleness_sec": 18
  }
}
```

Reason:

- Current v0.6 has `gnss_quality` categories.
- Literature and operator explanation need interpretable subfeatures.
- These remain synthetic and must be labeled as such.

### 3. Innovation / NIS Check

Add:

```json
{
  "innovation_check": {
    "check_id": "nis_uav_s1_t070",
    "asset_id": "uav_s1",
    "time": "2026-07-04T03:01:10Z",
    "measurement_type": "2d_position",
    "innovation_vector_m": {"north": 166.0, "east": -98.0},
    "innovation_covariance_diag_m2": {"north": 2809.0, "east": 1225.0},
    "nis": 25.0,
    "degrees_of_freedom": 2,
    "threshold_95": 5.99,
    "threshold_99": 9.21,
    "threshold_state": "critical",
    "interpretation_ko": "보고 위치가 예측 가능한 범위를 크게 벗어났습니다."
  }
}
```

Reason:

- Current v0.6 already calculates NIS but hides the innovation details.
- The operator panel should show why a measurement is contested.

### 4. Link / Bearer Metrics

Add:

```json
{
  "bearer_metrics": {
    "bearer_id": "synthetic_tactical_ip",
    "mode": "semantic_summary",
    "bandwidth_kbps": 96,
    "latency_ms": 950,
    "packet_loss_pct": 14,
    "heartbeat_gap_sec": 18,
    "snr_bucket": "low",
    "routing_policy": "semantic_first"
  }
}
```

Reason:

- S-DOT routing should be visibly tied to link conditions.
- This keeps the KT/civil-infra angle available as a bearer catalog without claiming guaranteed military priority access.

### 5. Alternate Navigation Evidence

Add weak evidence slots, even if no full VIO/TRN algorithm runs:

```json
{
  "alternate_navigation_evidence": [
    {
      "evidence_id": "vio_uav_s1_001",
      "source_type": "VISUAL_INERTIAL_ODOMETRY",
      "supports_estimate_id": "nav_uav_s1_t070",
      "drift_rate_m_per_min": 18.0,
      "confidence": 0.58,
      "limitations_ko": ["조도 변화", "특징점 부족", "누적 드리프트"]
    },
    {
      "evidence_id": "visual_match_uav_s1_001",
      "source_type": "ORTHOIMAGE_MATCH",
      "candidate_position_m": {"north": 830, "east": 145, "down": -118},
      "match_score": 0.62,
      "confidence": 0.50,
      "limitations_ko": ["지도 노후화", "가림", "유사 지형"]
    }
  ]
}
```

Reason:

- Visual/VIO/TRN are real research-backed alternatives, but v0.7 should avoid pretending they are fully implemented.

### 6. Packet Priority Breakdown

Add:

```json
{
  "packet_priority_breakdown": {
    "flight_safety": 0.92,
    "navigation_integrity_risk": 0.88,
    "mission_relevance": 0.74,
    "link_survivability": 0.69,
    "time_sensitivity": 0.77,
    "audit_value": 0.66,
    "weighted_priority": 0.80,
    "routing_decision": "send_semantic_hold_raw",
    "operator_reason_ko": "항법 무결성 위험이 높고 링크가 좁아 NAV_HEALTH_CARD를 원본보다 먼저 보냅니다."
  }
}
```

Reason:

- Judges should see why a packet was sent or held.
- This is the product value of S-DOT.

### 7. Rejoin Audit Error Budget

Add:

```json
{
  "rejoin_error_budget": {
    "audit_id": "audit_uav_s1_t120",
    "prediction_ref": "nav_uav_s1_t110",
    "cached_truth_ref": "truth_uav_s1_t110",
    "discrepancy_m": 86.2,
    "uncertainty_major_m": 172.0,
    "contained_in_envelope": true,
    "semantic_packet_refs": ["sdot_nav_001"],
    "raw_cache_refs": ["mock://uav_s1/eoir/frame_batch_030110"],
    "trust_update": "prediction_model_retained",
    "audit_summary_ko": "재연결 후 확인한 실제 경로가 예측 타원 안에 있었으므로 당시 시맨틱 판단은 유지됩니다."
  }
}
```

Reason:

- Rejoin audit is the clearest way to show that S-DOT is honest about uncertainty.

## UI Requirements

### Main 3D Scene

Add or refine:

- last trusted position marker
- predicted path
- reported GNSS path
- actual cached truth path, hidden until rejoin case
- uncertainty ellipse/cone
- stale telemetry timer
- mode badge: `정상`, `저하`, `예측 운용`, `재연결 감사`

### Operator Board

Korean labels:

| English Object | Korean Label |
|---|---|
| Prediction Envelope | 예측 범위 |
| Reported Position | 수신 위치 |
| Last Trusted State | 마지막 신뢰 상태 |
| Innovation Residual | 예측-수신 잔차 |
| NIS | 정규화 잔차 지표 |
| GNSS Quality | GNSS 품질 |
| Bearer State | 링크/전송 상태 |
| Semantic Packet | 시맨틱 패킷 |
| Rejoin Audit | 재연결 감사 |

### Packet Inspector

Show:

- raw bytes generated
- semantic bytes sent
- semantic compression ratio
- packet priority components
- decision: `전송`, `지연`, `로컬 보존`, `재연결 후 동기화`
- evidence refs

### Explanation Panel

Add short Korean explanations:

- "왜 교란 의심인가?"
- "왜 정확 위치가 아니라 예측 범위인가?"
- "왜 원본 대신 시맨틱 패킷인가?"
- "재연결 후 무엇을 검증하는가?"

## Algorithm Parameters To Expose

| Parameter | Current v0.6 | v0.7 Recommendation |
|---|---:|---:|
| NIS watch threshold | 9.21 | keep as 2D 99% threshold |
| NIS critical threshold | 16.0 | keep for demo critical state |
| GNSS quality drop | category | split into CN0/satellite/HDOP/VDOP proxy |
| Link drop | packet loss + mode | add heartbeat/SNR bucket |
| Wind | case-level profile | store in `prediction_model_config` and timeline |
| Packet priority | event score | add weighted component breakdown |
| Audit | summary | add discrepancy/error-budget object |

## Implementation Order

1. Extend data generator with v0.7 objects while keeping v0.6 fields backward compatible.
2. Regenerate `mock_dataset.json` and `mock_dataset.js`.
3. Add operator explanation panel in Korean.
4. Add NIS/innovation detail view.
5. Add packet priority breakdown to packet inspector.
6. Add rejoin audit error-budget panel.
7. Optionally add TartanAir/EuRoC validation notes; do not ingest heavy datasets unless needed.

## Safety Requirements

Use only:

- synthetic trajectories
- synthetic GNSS/link degradation
- public dataset references
- defensive diagnostic labels

Do not add:

- real military coordinates
- real drone tasking route
- jammer location inference
- EW attack details
- sensitive infrastructure or PII

## Verification Gates

Before v0.7 is considered done:

1. JSON validates.
2. All case switches still work.
3. Every semantic packet has evidence refs.
4. Every `jamming_suspected` label includes caveat text.
5. NIS values show thresholds and degrees of freedom.
6. UI Korean labels fit on desktop and mobile.
7. Rejoin audit distinguishes prediction from cached truth.
8. Public deployment is refreshed and visually checked.

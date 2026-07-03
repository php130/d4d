# D4D T3 2차 웨이브 Synthesis

표기: `[초록]`은 abstract-only caveat, `[부분]`은 partial_text, `[전문]`은 full_text.

## 추가로 강화된 주장 7개

1. **COP 복원력은 통신만이 아니라 엣지 컴퓨팅 배치 문제다.**  
   2차 웨이브는 semantic edge/split inference와 adaptive tactical edge 배치를 결합해, raw feed 전송보다 센서 근처에서 semantic event를 만들고 링크 상태에 따라 모델/서비스 위치를 바꾸는 설계를 강화한다. [21 부분, 22 초록]

2. **AIS 부재는 단순 결측이 아니라 확률적 증거다.**  
   AIS silence 예측, SAR-AIS 불일치, modality availability mask가 추가되며, "AIS 없음 = 불법"이 아니라 "검토할 evidence disagreement"로 다뤄야 한다는 주장이 강해졌다. [23 초록, 24 부분]

3. **Dark vessel/이상행동은 label이 아니라 증거 번들이다.**  
   DarkVesselNet, Antasena, BATMAN은 vessel object에 SAR/AIS/optical/context/trajectory/provenance/confidence/review status를 붙이는 쪽으로 COP 설계를 밀어준다. Antasena는 RF 95.3% accuracy, 94.7% precision, 94.2% recall, 96.8% ROC-AUC를 보고했다. [24 부분, 25 부분, 26 초록]

4. **신뢰·사이버 상태가 COP fusion의 1급 객체가 된다.**  
   MATE는 agent trust와 track trust를 확률분포로 유지하고 trust-weighted fusion을 수행한다. 보고된 실험은 adversary-driven OSPA error 94% 감소, compromised-agent detection 약 90%다. 단, CARLA 기반이라 해상 적용은 전환 필요하다. [31 부분] OT sensor fusion은 cyber anomaly를 maritime COP event로 통합하는 근거를 추가한다. [28 초록]

5. **COP 자체의 의미 불일치가 위험이다.**  
   2차 웨이브는 COP를 단일 지도 화면이 아니라 current picture, plan, forecast, COA, prepared package로 분리해야 한다고 강화한다. PCOP/offline bundle, C2 stage, time validity, intended audience 태깅이 새로 중요해졌다. [29 초록, 30 초록, 32 초록, 40 초록]

6. **네트워크 스케줄링 기준은 bit throughput이 아니라 mission-message throughput이다.**  
   semantic confidence, KB matching, goal relevance, value/age of information으로 COP update를 send/summarize/defer/drop해야 한다는 근거가 추가됐다. [33 초록, 34 초록, 35 초록]

7. **멀티모달 semantic payload의 실험적 근거가 보강됐다.**  
   Underwater SAGE는 이미지 대신 compact text semantics를 보내고, CLIPScore가 moderate corruption에서도 유지됨을 보였다. 예: character substitution 15% 부근에서 약 60%에서 50%로 하락했고, word deletion은 50% 부근까지 상대적으로 견딤. [36 전문] 이미지 segmentation/GAN, speech DeepSC-S, VQA multi-user SemCom은 image/speech/question-answer COP payload로 확장할 근거를 준다. [37-39 초록]

## 데모 설계에 새로 반영할 요소

- Scenario: AIS silence + SAR detection + spoofed/low-trust report + degraded link.
- Semantic evidence bundle: `object_id`, `time`, `location`, `source`, `modality_slots`, `availability_mask`, `confidence`, `trust_score`, `provenance`, `semantic_type`, `C2_stage`, `review_status`.
- Denied-network simulator: bandwidth cap, packet drop, field corruption, stale update, delayed sync를 넣고 raw feed vs semantic delta vs semantic+trust를 비교.
- Tiered payload: full image -> caption/segmentation -> object list -> alert card 순으로 degrade.
- Trust fusion layer: reporter trust와 track trust를 분리하고, AIS/SAR/EO/RF/human report 불일치를 표시.
- Operator UI: observed state, planned event, forecast, recommendation을 분리하고 alert마다 evidence trace 제공.
- Metrics: bandwidth saved, latency, mission-message throughput, AoI/VoI, anomaly precision/recall, calibration, trace completeness, operator decision accuracy.

## 통신사/KT 관점 차별화 포인트

- 망 제공자에서 semantic COP transport provider로 포지셔닝: Mbps가 아니라 mission-message delivery, semantic QoS, freshness, confidence-aware routing을 제공.
- MEC/edge orchestration 차별화: 선박, 항만, 해안기지, UAV/USV relay 근처에서 inference/fusion 서비스를 동적으로 배치.
- KB-aware routing: 수신 노드가 해당 ontology/mission package를 이해할 수 있는지 확인하고 message detail level을 조정.
- Store-forward semantic sync: DDIL 환경에서 graph delta, PCOP bundle, alert card 중심으로 끊겼다 붙는 해상망을 운영.
- Trust/cyber overlay: 통신사 관점의 link state, RF anomaly, node health를 COP trust score와 결합해 단순 연결성 이상의 가치를 제공.

## 위험/한계 업데이트

- 21-40 중 full_text는 36번뿐이고, 다수는 `[초록]` 근거라 수치·구현·평가 세부는 검증 필요.
- AIS silence는 위성 기하, 수신 실패, 장비 고장, 합법적 미탑재와 구분해야 한다.
- GAN/Stable Diffusion 재구성은 그럴듯한 거짓 시각 정보를 만들 수 있으므로 synthetic visual은 관측 사실과 분리해야 한다.
- MATE는 CARLA urban driving 기반이라 maritime sensor coverage, sparse observability, long gap, coordinated deception에 재검증 필요.
- semantic KB/ontology mismatch가 coalition/legacy 환경의 핵심 실패 모드가 될 수 있다.
- adaptive edge orchestration은 discovery, migration, startup, coordination overhead가 denial 상황에서 오히려 부담이 될 수 있다.
- CLIPScore 등 semantic similarity만으로 mission assurance를 대체하면 안 된다.

## Next Action

1. 2차 웨이브 기반 demo schema를 먼저 고정: evidence bundle + trust fields + PCOP metadata.
2. AIS silence/SAR mismatch/dark vessel alert의 end-to-end mock pipeline을 만든다.
3. denied-network simulator로 raw vs semantic delta vs semantic+trust 3조건을 비교한다.
4. dashboard는 alert trace, trust, modality availability, observed/plan/forecast 분리를 우선 구현한다.
5. `[초록]` 근거 논문 중 23, 28, 29, 33-40은 full text 확보 후 claim strength를 재분류한다.


# T3 Deep Research Learning Synthesis

- Generated: 2026-07-03 23:12 KST
- Focus: Resilient Maritime COP over Denied Networks
- Source base: 40 priority paper notes under `paper_notes/`
- Evidence caution: papers marked `abstract_only` are useful for direction, but not for strong quantitative claims.

## 핵심 결론 7개

1. COP의 핵심은 모든 데이터를 보내는 것이 아니라 임무 의미를 유지하는 것이다.
   의미통신 문헌은 bit-perfect delivery보다 mission-relevant meaning, importance, freshness, task utility를 기준으로 전송해야 한다고 본다. T3 데모는 원시 영상/로그 대신 `track_delta`, `intent`, `confidence`, `anomaly`, `provenance`를 우선 전송하는 구조가 맞다. 근거: 01, 02, 13, 14. 단, 03, 14는 초록 기반이다.

2. 해양 COP는 AIS 단일 소스에 의존하면 안 된다.
   AIS는 유용하지만 누락, 스푸핑, 지연, 의도적 비활성화가 가능하다. SAR, EO/IR, 레이더, UAV, METOC, 운용자 보고를 함께 묶고, 각 주장에 출처와 신뢰도를 붙여야 한다. 근거: 04, 07, 08, 09, 12, 16. 07, 08, 16은 초록 기반이다.

3. 분산형 COP는 해커톤 데모에 충분히 설득력 있다.
   MARL 기반 분산 COP 연구는 각 에이전트가 부분 관측만 갖고도 압축 메시지와 시간 메모리로 COP를 유지하는 패턴을 제시한다. 해양에서는 함정, UAV, USV, 연안 노드를 에이전트로 모델링하면 된다. 근거: 05.

4. 표준/온톨로지 계층이 데모의 신뢰도를 높인다.
   STANAG 4676은 track, sensor, evidence, confidence, transformation을 표현하는 데 적합하고, CISE/eCISE와 RDF/SPARQL 기반 데이터레이크는 기관 간 해양 정보 공유 패턴을 제공한다. 근거: 04, 12, 20.

5. Denied network 대응은 네 가지 모드로 보여주는 것이 좋다.
   `full_sync -> delta_sync -> semantic_summary -> store_and_forward`로 단계적으로 품질을 낮추되, 중요한 접촉, 위협, 불확실성은 유지한다. 근거: 01, 02, 04, 12, 17.

6. LLM/RAG는 COP의 판단자가 아니라 근거 있는 브리핑 인터페이스로 제한해야 한다.
   RAG 관련 노트는 provenance, latency, uncertainty, safety를 강조한다. citation correctness와 faithfulness는 다르므로, 생성 요약에는 실제 검색 컨텍스트와 출처 체인을 기록해야 한다. 근거: 18, 19. 둘 다 초록 기반이다.

7. 가장 강한 데모 메시지는 "네트워크가 끊겨도 작전 의미는 유지된다"이다.
   원시 데이터 손실을 숨기지 말고, COP가 어떤 데이터를 못 받았고 어떤 의미는 유지했는지 UI에서 드러내야 한다. 지표도 packet delivery만이 아니라 COP freshness, track confidence, semantic fidelity, alert recall, operator decision latency로 잡는 편이 좋다.

## 2차 웨이브에서 추가된 핵심 보강

1. COP 복원력은 통신만이 아니라 엣지 컴퓨팅 배치 문제다.
   Semantic edge/split inference와 adaptive tactical edge 배치가 추가되면서, 센서 근처에서 semantic event를 만들고 링크 상태에 따라 모델/서비스 위치를 바꾸는 설계가 더 강해졌다.

2. AIS 부재는 단순 결측이 아니라 확률적 증거다.
   AIS silence, SAR-AIS 불일치, modality availability mask를 통해 "AIS 없음 = 불법"이 아니라 "검토할 evidence disagreement"로 다뤄야 한다.

3. Dark vessel/이상행동은 label이 아니라 증거 번들이다.
   SAR, AIS, optical, trajectory, context, provenance, confidence, review status를 한 객체에 묶는 evidence bundle 설계가 더 설득력 있어졌다.

4. 신뢰·사이버 상태가 COP fusion의 1급 객체가 된다.
   reporter trust와 track trust를 분리하고, link state/RF anomaly/node health 같은 통신사 관점 신호를 COP trust score와 결합할 수 있다.

5. 네트워크 스케줄링 기준은 bit throughput이 아니라 mission-message throughput이다.
   semantic confidence, knowledge-base matching, goal relevance, value/age of information으로 COP update를 send/summarize/defer/drop하는 메시지 스케줄러가 KT 관점 차별화 포인트가 된다.

6. Operator UI는 observed/current, plan, forecast, recommendation을 분리해야 한다.
   COP가 오해를 만들 수 있으므로 PCOP/offline bundle, C2 stage, time validity, intended audience 태깅이 중요하다.

7. 멀티모달 semantic payload는 tiered payload로 구현하는 편이 좋다.
   full image -> caption/segmentation -> object list -> alert card 순으로 degrade시키고, GAN/Stable Diffusion식 재구성은 관측 사실과 분리해야 한다.

## 해커톤 데모 아키텍처

### 시나리오

해역 내 의심 선박이 AIS를 끄거나 스푸핑하고, SATCOM/RF 링크가 간헐적으로 차단된다. 여러 노드는 서로 완전한 데이터를 공유하지 못하지만, 최소 의미 단위의 COP를 동기화해 "누가 어디에 있고, 왜 의심스러운지, 어떤 근거가 있는지"를 유지한다.

### 구성 흐름

1. Edge sensing nodes
   - 함정, 연안, UAV, 가상 위성 노드.
   - 입력: AIS, SAR detection, radar-like track, EO/UAV detection, METOC, operator report.
   - 출력: 원시 데이터가 아니라 `semantic_observation`.

2. Semantic extractor
   - 원시 관측을 다음 구조로 변환한다.

```json
{
  "entity": "vessel_042",
  "event": "SAR_DETECTION_WITHOUT_AIS",
  "location": [37.12, 126.51],
  "time": "2026-07-03T12:00:00Z",
  "confidence": 0.78,
  "priority": "high",
  "source": "sar_node_1",
  "provenance": ["sar_scene_id", "model_version", "match_rule"]
}
```

3. Local COP graph
   - 각 노드가 자체 RDF/JSON-LD 스타일 그래프를 유지한다.
   - track, sensor, evidence, confidence, freshness, contradiction을 저장한다.
   - 연결 복구 시 named graph 또는 nanopublication-like bundle로 병합한다.

4. Denied-network policy engine
   - 네트워크 상태에 따라 전송 수준을 바꾼다.
   - 정상: track + evidence + selected raw thumbnails.
   - 저대역: track delta + anomaly + confidence.
   - 심각한 제한: object list 또는 alert card.
   - 차단: local cache only.
   - 복구: store-and-forward sync.

5. Fusion and conflict resolver
   - AIS와 SAR/레이더/UAV가 충돌하면 정답으로 덮어쓰지 않고 claim들을 병렬 유지한다.
   - 예: AIS says vessel type = cargo, SAR classifier says small craft, 위치 차이 3km -> spoofing suspicion.

6. Operator COP UI
   - 지도 위 contact, anomaly, freshness, confidence를 표시한다.
   - "왜 의심?" 패널에 출처, 마지막 수신 시간, 충돌한 증거, 누락된 데이터를 보여준다.
   - network denial slider 또는 scripted outage로 실시간 변화 시연을 구성한다.

7. RAG briefing assistant
   - "현재 가장 위험한 접촉은?" 같은 질문에 cached COP graph와 reports만 사용한다.
   - 답변마다 source support와 generation-time retrieval log를 분리 표시한다.

8. Trust/cyber overlay
   - reporter trust와 track trust를 분리한다.
   - AIS/SAR/EO/RF/operator report 불일치를 표시한다.
   - 통신사 관점의 link state, RF anomaly, node health를 fusion 신뢰도에 반영한다.

## 데이터, 모델, 평가지표

### 데이터

- AIS track: MMSI, 위치, SOG/COG, heading, timestamp, vessel type.
- SAR/EO/UAV synthetic detections: bounding box 또는 point detection, class hypothesis, timestamp.
- Radar-like track: range/bearing 또는 lat/lon, uncertainty ellipse.
- METOC/geofence: weather, sea state, EEZ/MPA/exclusion zone, shipping lane.
- Operator reports: 짧은 텍스트 contact report.
- Network telemetry: bandwidth, packet drop, latency, outage windows.

초록 기반 근거 주의: AIS anomaly review(06), SAR-AIS classification(07), dark vessel detection(08), AIS ML review(15), maritime AI security review(16)는 세부 benchmark 수치가 노트에 없다.

### 모델

- Rule baseline:
  - AIS off near geofence.
  - SAR detection without AIS match.
  - course deviation.
  - impossible speed/location jump.
  - stale track risk.
- ML option:
  - AIS route anomaly: one-class SVM, isolation forest, sequence autoencoder 중 하나.
  - SAR/AIS association: time-distance gate + vessel class consistency.
  - Confidence model: source type, range, weather, age, cross-source agreement.
- Semantic communication:
  - 전송 payload를 raw feed와 semantic delta로 비교한다.
  - 실제 RF 모델은 단순화해도 된다: packet drop, bandwidth cap, delay queue.
- RAG:
  - hybrid retrieval: keyword + vector + structured graph query.
  - citation faithfulness audit: 생성 시 실제로 제공된 context id를 기록한다.

### 평가지표

- COP completeness: ground truth 대비 유지된 핵심 contact/event 비율.
- COP freshness: contact별 마지막 신뢰 가능한 update age.
- Track quality: 위치 오차, identity consistency, false track count.
- Alert quality: dark vessel/anomaly precision, recall, false alarm rate.
- Semantic efficiency: 동일 임무 성과 대비 전송 byte 감소율.
- Resilience: outage 동안 high-priority event 전달 성공률, 복구 후 sync convergence time.
- Mission-message throughput: 전송된 bit 수가 아니라 성공적으로 전달된 임무 메시지 수.
- Evidence trace completeness: alert마다 source/provenance/trust/freshness가 얼마나 완비됐는지.
- RAG quality: answer usefulness, source correctness, attribution faithfulness, stale-data warning rate.
- Operator metric: threat triage time, explanation click depth, overload 감소.

## Palantir AIP 또는 일반 데이터 플랫폼 구현 구성요소

### Palantir AIP 기준

- Ontology:
  - `Vessel`, `Track`, `Observation`, `Sensor`, `Event`, `Alert`, `Area`, `Mission`, `NetworkState`, `Evidence`.
- Foundry pipelines:
  - AIS/SAR/UAV/operator report ingest.
  - schema normalization.
  - dedup/entity resolution.
  - confidence/freshness scoring.
- Object model actions:
  - mark suspicious, confirm identity, request ISR, publish semantic update.
- AIP Logic / Functions:
  - anomaly rules, SAR-AIS association, priority scoring, sync policy simulation.
- AIP Assist:
  - COP briefing over governed ontology objects.
  - mandatory provenance and freshness references.
- Operational UI:
  - map, timeline, network degradation panel, evidence panel, alert queue.

### 일반 데이터 플랫폼 기준

- Ingestion:
  - Kafka/Redpanda 또는 파일 replay.
  - NiFi-style processor는 데모에서는 Python/FastAPI jobs로 대체 가능.
- Storage:
  - PostGIS for tracks/geofence.
  - object store for raw snippets.
  - graph DB 또는 RDF store for provenance-aware COP.
- Processing:
  - stream processor for deltas.
  - anomaly service.
  - fusion/conflict resolver.
  - trust scoring service.
  - network policy simulator.
- API:
  - `/observations`, `/tracks`, `/alerts`, `/sync-bundles`, `/brief`.
- Frontend:
  - MapLibre/Deck.gl 지도.
  - denied-network slider.
  - evidence/provenance drawer.
- RAG:
  - vector DB + structured SQL/graph retrieval.
  - generation-time context logging.

## 2주 준비 로드맵

1. 1-2일차: 데모 범위 고정
   - 해역, 선박 수, denial 이벤트, 성공 지표 결정.
   - "AIS 스푸핑 + SAR 미매칭 + 링크 차단" 한 가지 메인 스토리로 제한.

2. 3-4일차: 데이터셋/시뮬레이터 제작
   - AIS-like tracks 생성 또는 공개 AIS 샘플 정리.
   - SAR/UAV/radar synthetic detections 생성.
   - network outage schedule 생성.

3. 5-6일차: COP 데이터 모델
   - Vessel, Track, Observation, Event, Evidence, Confidence 스키마 구현.
   - provenance와 freshness를 필수 필드로 강제.

4. 7-8일차: fusion/anomaly
   - AIS-SAR association.
   - dark vessel rule.
   - course deviation/stale track rule.
   - confidence score 계산.

5. 9-10일차: denied-network sync
   - full/delta/summary/store-and-forward 모드 구현.
   - bandwidth cap별 payload 크기와 COP 품질 기록.

6. 11일차: RAG briefing
   - "상위 위험 접촉", "근거", "불확실성", "다음 ISR 요청" 질의 구현.
   - citation correctness와 retrieval context log 분리.

7. 12일차: UI
   - 지도, alert queue, evidence drawer, network mode panel.
   - raw feed가 끊겨도 semantic COP가 유지되는 장면 구성.

8. 13일차: 평가/리허설
   - 정상망 vs denied network 비교표 생성.
   - byte reduction, alert recall, freshness, sync recovery time 산출.

9. 14일차: 발표 패키징
   - 3분 데모 스크립트.
   - 아키텍처 한 장.
   - 리스크와 한계 한 장.
   - 초록 기반 근거와 full/partial text 근거를 명확히 구분.

## 가장 조심해야 할 리스크

1. AIS를 truth로 취급하는 것.
   AIS는 claim source일 뿐이다. 스푸핑, 누락, 지연 가능성을 UI와 모델에 반영해야 한다.

2. Semantic compression이 중요한 증거를 버리는 것.
   데모에서는 raw를 안 보내더라도 source fingerprint, thumbnail id, model version, timestamp는 유지해야 한다.

3. RAG 답변의 과신.
   출처가 맞아 보여도 실제 생성에 쓰였는지는 별도 문제다. retrieval log 기반 faithfulness audit을 남겨야 한다. 이 근거는 19번 노트의 초록 기반이다.

4. 그래프/RDF 과설계.
   RDF, named graph, nanopublication은 설득력 있지만 해커톤에서는 JSON-LD 스타일 envelope로 시작하고, SPARQL은 핵심 질의 몇 개만 구현하는 편이 낫다.

5. 실시간 전술 성능을 과장하는 것.
   SAR revisit, cloud/weather, RF jamming, sensor latency는 데모에서 단순화된다. 발표에서는 operational prototype이 아니라 resilience pattern demo로 말해야 한다.

6. 초록 기반 노트의 근거 강도 혼동.
   초록 기반 노트: 03, 06, 07, 08, 11, 14, 15, 16, 18, 19. 이들은 방향성 근거로 쓰고, 수치 성능이나 구현 세부 주장에는 사용하지 않는 것이 안전하다.

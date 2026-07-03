# Platform Learning Plan

플랫폼은 "기능 목록 암기"가 아니라 "해커톤 데모에 어떻게 쓰이는지" 기준으로 학습합니다.

## Palantir AIP

확인한 공식 문서 기준으로 AIP는 조직의 데이터와 운영 위에 AI workflow, agent, function, app을 얹는 플랫폼입니다. D4D에서는 아래 관점으로 학습합니다.

2026-07-01에는 사용자의 Chrome 로그인 세션에서 D4D Foundry tenant를 read-only로 실제 확인했습니다. 세부 기능 지도는 `04_platforms/palantir_aip/foundry_walkthrough_20260701.md`에 기록합니다.

같은 날 이미 설치된 `AIP Now Ontology` 예제 패키지에서 Workshop 앱, object view, Pipeline Builder 예제를 실제로 실행 확인했습니다. 실행 기록은 `04_platforms/palantir_aip/foundry_examples_walkthrough_20260701.md`에 기록합니다.

추가 deep dive로 `Route Alert` 예제의 ontology object, action type, comment object, metrics pipeline, map/table app 흐름을 추적했습니다. 기록은 `04_platforms/palantir_aip/foundry_alert_workflow_deep_dive_20260701.md`에 둡니다.

### Learn

- Ontology: 데이터셋을 사람/조직/자산/사건 같은 객체와 관계로 모델링하는 방식
- AIP Logic / Workflow: 분석 절차를 재사용 가능한 workflow로 만드는 방식
- AIP Analyst: 자연어로 ontology/dataset을 탐색하고 시각화하는 방식
- AIP Evals: LLM workflow와 prompt를 테스트하고 비교하는 방식
- Security/Governance: 권한, 감사, 출처 추적, 민감정보 통제

### Test Checklist

- [x] 접근 권한과 계정 상태 확인
- [x] 샘플 dataset과 설치 예제 접근 가능 여부 확인
- [x] ontology/object/action 개념을 실제 화면에서 확인
- [ ] 자연어 분석 또는 agent workflow 생성 가능 여부 확인
- [ ] 결과 provenance, lineage, audit 기능 확인
- [ ] export/API/embedding/app 연동 가능성 확인

## StealthMole

공식 제품 페이지 기준으로 Darkweb Tracker는 deep/dark web threat intelligence 플랫폼이며 검색, 필터, 데이터 캔버스, 관계 분석, 지도, API 통합을 강조합니다.

### Learn

- Search: 키워드와 indicator 기반 검색
- Filters: network, personal information, crypto wallet, file 등 검색 지표
- Data Canvas: 데이터 포인트를 추가하고 관계를 시각화
- Darkweb Map: IP/GPS 기반 위치 시각화
- Monitoring: 키워드/조직/위협 관련 지속 감시
- API Integration: 외부 앱/분석 스택과 연결

### Test Checklist

- [ ] 데모 계정/행사 제공 접근 권한 확인
- [ ] 키워드 검색 기능 확인
- [ ] 필터 종류와 입력값 확인
- [ ] 검색 결과에서 entity/indicator 추출 가능 여부 확인
- [ ] Data Canvas에 결과를 추가하고 연결 분석 가능 여부 확인
- [ ] 지도/시간/출처 정보가 데모에 쓸 만큼 충분한지 확인
- [ ] API/export/screenshot 사용 가능 여부 확인

## Evaluation Lens

플랫폼을 테스트할 때마다 다음 질문으로 정리합니다.

- 이 기능은 어떤 군/안보 사용자의 시간을 줄이는가?
- 결과에 근거와 출처가 남는가?
- 오탐/누락이 생겼을 때 사용자가 확인할 수 있는가?
- 데모에서 30초 안에 가치가 드러나는가?
- 민감정보나 약관 문제가 생기지 않는가?

## Platform Learning Artifacts

추가 자료는 아래 문서로 관리합니다.

- `04_platforms/platform_learning_index.md`
- `04_platforms/palantir_aip/learning_brief.md`
- `04_platforms/palantir_aip/foundry_walkthrough_20260701.md`
- `04_platforms/palantir_aip/foundry_examples_walkthrough_20260701.md`
- `04_platforms/palantir_aip/foundry_alert_workflow_deep_dive_20260701.md`
- `04_platforms/palantir_aip/build_examples_index.md`
- `04_platforms/stealthmole/learning_brief.md`
- `04_platforms/stealthmole/youtube_video_index.md`
- `08_ops/runbooks/video_intake_stt_screenshot.md`

## Sources

- https://palantir.com/docs/foundry/aip/overview/
- https://palantir.com/docs/foundry/aip-analyst/overview/
- https://palantir.com/docs/foundry/aip-evals/overview/
- https://www.stealthmole.com/products/darkweb-tracker

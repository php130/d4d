# Platform Learning Index

Last reviewed: 2026-07-01

이 폴더는 D4D 해커톤에서 사용할 가능성이 높은 플랫폼을 미리 학습하기 위한 자료집입니다. 목표는 기능명을 암기하는 것이 아니라, 해커톤 문제를 데이터 입력, 분석 workflow, 데모 UI, 제출물로 바꾸는 데 필요한 사용 패턴을 익히는 것입니다.

## Priority

1. Palantir AIP / Foundry
   - 해커톤에서 데이터, ontology, 분석 workflow, agent, app demo를 구성하는 핵심 플랫폼 후보입니다.
   - 먼저 `Ontology -> data pipeline -> AIP-assisted analysis -> Workshop/COP demo -> Evals/governance` 순서로 학습합니다.

2. StealthMole
   - T2 OSINT & Defense Intelligence, 방산 공급망 credential exposure, threat actor graph 문제에 직접 연결됩니다.
   - 먼저 `search -> filter -> entity/indicator extraction -> Data Canvas/graph -> report/API` 순서로 학습합니다.

3. Video / course materials
   - YouTube는 caption/transcript 우선으로 처리합니다.
   - UI가 중요한 제품 데모 영상은 transcript 요약만으로 부족하므로 key frame screenshot + OCR/메모를 보강합니다.

## Current Files

- `palantir_aip/learning_brief.md`: Palantir AIP/Foundry 학습 브리프
- `palantir_aip/foundry_walkthrough_20260701.md`: 실제 Chrome 세션에서 확인한 Foundry 앱/메뉴/생성 흐름 지도
- `palantir_aip/foundry_examples_walkthrough_20260701.md`: 실제 실행 가능한 Foundry 예제 앱/파이프라인 확인 기록
- `palantir_aip/foundry_alert_workflow_deep_dive_20260701.md`: Route Alert 예제를 기반으로 한 alert ontology/action/pipeline/app deep dive
- `palantir_aip/build_examples_index.md`: Build with AIP 공개 예제 중 해커톤 관련 항목
- `palantir_aip/access_notes.md`: Palantir 사이트 접근/제한 기록
- `stealthmole/learning_brief.md`: StealthMole 플랫폼 학습 브리프
- `stealthmole/youtube_video_index.md`: StealthMole YouTube 영상 인덱스
- `stealthmole/access_notes.md`: StealthMole 사이트/영상 접근 기록
- `../08_ops/runbooks/video_intake_stt_screenshot.md`: 영상 처리 runbook

## How To Use This In The Hackathon

### If the challenge is OSINT / Defense Intelligence

- Start with StealthMole search/report patterns.
- Build a Palantir-style object model: threat actor, alias, wallet, domain, credential leak, incident, organization, source.
- Use AIP/LLM workflow for citation-backed brief generation.
- Demo should show analyst input, retrieved evidence, graph/timeline, risk score, recommended actions.

### If the challenge is Maritime Domain Awareness

- Use public AIS/weather/satellite/event data catalog.
- Build a Palantir-style object model: vessel, port, voyage, AIS event, weather cell, anomaly, report source.
- Use Workshop/COP examples as the demo pattern.
- Keep raw vessel feeds local; present aggregated or sampled data.

### If the challenge is C2 / Sustainment

- Use COP, geospatial, alerting, process workflow, and object actions patterns from Palantir examples.
- Build a simple operational dashboard around objects, status, incidents, and decisions.
- Emphasize provenance, permissions, and human-in-the-loop decisions.

## Source Links

- Palantir docs: https://www.palantir.com/docs
- Build with AIP: https://build.palantir.com/
- Palantir Learn speedrun: https://learn.palantir.com/speedrun-your-first-e2e-workflow
- StealthMole: https://www.stealthmole.com/
- StealthMole YouTube: https://www.youtube.com/@StealthMoleIntelligence/videos

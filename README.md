# D4D | Deploy for Defense Hackathon APAC - Seoul

국방/안보 문제를 다루는 D4D 해커톤을 준비하기 위한 작업 공간입니다. 이 프로젝트는 아직 특정 과제나 솔루션을 확정하기 위한 저장소가 아니라, 사용자가 제공하는 자료, 사이트, 플랫폼, 교육자료를 함께 이해하고 축적하면서 이후 과제 대응을 빠르게 할 수 있게 만드는 준비 공간입니다.

## 프로젝트 방향

행사 페이지 기준 D4D는 국방과 안보 문제를 해결하는 해커톤이며, 공개된 트랙에는 다음 다섯 가지가 있습니다.

1. T1. Autonomy, Unmanned Systems & Counter-UAS
2. T2. OSINT & Defense Intelligence
3. T3. Battle Network, C2 & Sustainment
4. T4. Maritime Domain Awareness
5. T5. Force Readiness, Training & Simulation

아직 세부 과제는 정해지지 않았으므로 특정 트랙이나 솔루션을 미리 고정하지 않습니다. 다만 사용자가 언급한 Palantir AIP, StealthMole, 공개 데이터(OSINT)는 여러 트랙에서 활용될 수 있는 공통 기반으로 보고 먼저 이해도를 쌓습니다.

## 이 프로젝트에 기대하는 역할

사용자는 테크/국방/안보 전문용어와 관련 플랫폼에 익숙하지 않을 수 있으므로, 이 프로젝트는 다음 역할을 수행합니다.

1. 사용자가 제공하는 사이트, 문서, 영상, 자료를 직접 읽고 핵심을 정리합니다.
2. Palantir AIP, StealthMole 같은 플랫폼의 개념과 기능을 실제 사용 관점에서 이해합니다.
3. 접근 가능한 기능은 직접 테스트하고, 안 되는 부분은 원인과 대안을 기록합니다.
4. 낯선 국방/안보/OSINT 용어는 쉬운 말로 풀어서 glossary에 축적합니다.
5. 자료에서 얻은 내용을 향후 과제의 input, output, 데이터, 데모 아이디어로 연결합니다.
6. 아직 확정되지 않은 아이디어는 가설로만 남기고, 사용자가 주는 추가 정보에 맞춰 방향을 조정합니다.

## 운영 원칙

1. 과제를 조급하게 확정하지 않습니다.
2. 자료를 볼 때마다 "무엇을 알게 되었는지", "무엇을 아직 모르는지", "나중에 어디에 쓸 수 있는지"를 분리해 기록합니다.
3. 플랫폼 학습은 기능명 암기가 아니라 실제 해커톤에서 쓸 수 있는 입력/출력/제약 중심으로 정리합니다.
4. OSINT와 보안 관련 자료는 출처, 접근 권한, 민감정보 여부, 사용 조건을 함께 기록합니다.
5. 최종 방향은 사용자가 제공하는 과제 방향, 필요한 input, 원하는 output이 더 구체화된 뒤에 정합니다.

## 디렉토리 구조

```text
D4D/
  00_admin/                 행사 정보, 용어집, 운영 메모
  01_research/              자료 읽기, 플랫폼 학습, OSINT 소스 정리
    source_intake/          사용자가 준 링크/문서/영상별 요약
    platform_notes/         Palantir AIP, StealthMole 등 기능 테스트 기록
    domain_notes/           국방/안보 도메인 개념 노트
    osint_sources/          공개 데이터 출처별 설명과 수집 조건
  02_problem_statements/    해커톤 과제, 문제정의, 가설
    tracks/                 트랙별 아이디어
    hypotheses/             검증할 제품/데이터 가설
  03_data/                  원천/가공/샘플 데이터
    raw/                    원본 데이터. 민감정보와 약관 주의
    processed/              정제/조인/피처 데이터
    samples/                데모용 작은 샘플
  04_platforms/             외부 플랫폼 실습과 연동 테스트
    palantir_aip/           AIP 학습, ontology/action/agent 메모
    stealthmole/            검색, 필터, canvas/API 테스트 기록
    api_tests/              curl/Postman/httpie 등 테스트 로그
  05_analysis/              분석 산출물
    notebooks/              탐색 분석
    knowledge_graph/        엔티티/관계 모델
    threat_models/          위협 모델, 리스크 기준
  06_prototype/             실제 해커톤 데모 코드
    app/                    웹앱/대시보드/프론트엔드
    scripts/                수집/정제/분석 스크립트
    prompts/                LLM 프롬프트와 평가 케이스
  07_deliverables/          제출물
    pitch/                  발표자료, 스토리라인
    demo/                   시연 시나리오, 스크린샷, 영상
    submission/             최종 제출 패키지
  08_ops/                   실행 절차와 안전/윤리/보안 체크
    playbooks/              분석가 워크플로우
    runbooks/               데모 실행법, 장애 대응
    security_compliance/    OSINT 윤리, 약관, 개인정보, 민감정보 처리
```

## 앞으로의 작업 방식

사용자가 자료나 사이트를 주면 다음 순서로 처리합니다.

1. 자료를 직접 열람하고 핵심 내용을 요약합니다.
2. 기능이 있는 플랫폼이면 가능한 범위에서 직접 눌러보고 테스트합니다.
3. 모르는 국방/안보/플랫폼 용어는 glossary에 추가합니다.
4. 해커톤 문제정의와 연결되는 지점을 problem canvas에 기록합니다.
5. 프로토타입으로 만들 만한 입력/출력/API/화면을 구체화합니다.

## GitHub Sync

이 프로젝트는 private GitHub repo로 동기화합니다. 어떤 Codex 세션이든 작업 전후에 아래 명령으로 로컬 상태가 GitHub 최신 버전보다 앞서거나 뒤처졌는지 확인할 수 있습니다.

```bash
cd /Users/mollykim/projects/D4D
./08_ops/scripts/git_sync_status.sh
```

자세한 운영 방식은 `08_ops/runbooks/git_sync_workflow.md`를 참고합니다. `.env`와 실제 API key/token/credential 파일은 private repo에도 커밋하지 않고, 필요한 변수명은 `.env.example`로만 관리합니다.

## Google Sheet Dataset

사용자가 제공한 D4D Google Sheet는 계속 바뀔 수 있는 canonical source로 취급합니다. 매번 시트를 새로 읽을 때는 raw snapshot과 processed dataset version을 함께 남깁니다.

- Latest processed dataset: `03_data/processed/current/`
- Version registry: `03_data/processed/VERSIONS.md`
- Track problem dataset: `03_data/processed/current/track_problem_statements.json`
- Glossary dataset: `03_data/processed/current/glossary_terms.json`
- Human-readable track summary: `02_problem_statements/tracks/d4d_track_problem_dataset.md`
- Refresh runbook: `08_ops/runbooks/google_sheet_dataset_versioning.md`

## Literature Research

논문 리서치는 OpenAlex와 arXiv 기반으로 versioned metadata dataset을 만들고, 사람이 읽을 우선순위 큐를 별도로 관리합니다.

- Methodology: `01_research/literature/literature_research_methodology.md`
- Seed catalog: `03_data/processed/literature/current/literature_seed_catalog.json`
- Human-readable catalog: `01_research/literature/literature_seed_catalog.md`
- First reading queue: `01_research/literature/first_reading_queue.md`
- Paper note template: `01_research/literature/paper_note_template.md`
- Refresh runbook: `08_ops/runbooks/literature_collection_runbook.md`

### T3 Deep Research

T3 주제인 `거부환경 해상 COP 의미 전송 시스템`은 별도 focused research dataset으로 관리합니다.

- Plan: `01_research/literature/t3_deep_research/deep_research_plan.md`
- Current dataset: `03_data/processed/literature_t3/current/t3_deep_research_catalog.json`
- First reading queue: `01_research/literature/t3_deep_research/t3_first_reading_queue.md`
- Concept map: `01_research/literature/t3_deep_research/concept_map.md`
- Architecture options: `01_research/literature/t3_deep_research/architecture_options.md`
- Dataset candidates: `01_research/literature/t3_deep_research/dataset_candidates.md`
- Pitch evidence: `01_research/literature/t3_deep_research/pitch_evidence.md`
- Runbook: `08_ops/runbooks/t3_deep_research_runbook.md`

## Rules and Safety

D4D 해커톤 규칙과 데이터 취급 원칙은 별도 문서로 관리합니다.

- Hackathon rules: `00_admin/hackathon_rules.md`
- OSINT ethics: `08_ops/security_compliance/osint_ethics.md`
- Submission checklist: `08_ops/security_compliance/hackathon_submission_checklist.md`
- Data availability Q&A: `01_research/osint_sources/data_availability_qa.md`
- OSINT source catalog: `01_research/osint_sources/osint_source_catalog.md`
- API key prep checklist: `01_research/osint_sources/api_key_prep_checklist.md`
- Resilient Maritime COP data connection guide: `08_ops/runbooks/resilient_maritime_cop_data_connection_guide.md`

## Platform Learning

해커톤에서 사용할 수 있는 Palantir AIP, StealthMole, 교육 영상/문서 학습 자료는 `04_platforms/` 아래에 축적합니다.

- Platform learning index: `04_platforms/platform_learning_index.md`
- Palantir AIP brief: `04_platforms/palantir_aip/learning_brief.md`
- Palantir Build examples: `04_platforms/palantir_aip/build_examples_index.md`
- StealthMole brief: `04_platforms/stealthmole/learning_brief.md`
- StealthMole YouTube index: `04_platforms/stealthmole/youtube_video_index.md`
- Video processing runbook: `08_ops/runbooks/video_intake_stt_screenshot.md`

## 주요 출처

- D4D Luma 행사 페이지: https://luma.com/2ew4xn7b
- Palantir AIP docs: https://palantir.com/docs/foundry/aip/overview/
- Palantir AIP for Defense: https://www.palantir.com/platforms/aip/defense/
- StealthMole Darkweb Tracker: https://www.stealthmole.com/products/darkweb-tracker

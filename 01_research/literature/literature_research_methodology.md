# Literature Research Methodology

Last updated: 2026-07-01

이 문서는 D4D 트랙별 문제를 이해하기 위한 논문 리서치 방법론입니다. 목표는 학술적으로 완벽한 systematic review가 아니라, 해커톤 전에 빠르게 도메인 감각을 만들고, 데이터·모델·데모 아이디어로 이어지는 근거 기반 자료를 축적하는 것입니다.

## Research Goals

1. 트랙별 문제의 기술 배경과 대표 방법론을 빠르게 파악합니다.
2. 해커톤 데모에 쓸 수 있는 공개 데이터셋, benchmark, synthetic data, simulator를 찾습니다.
3. 논문에서 나온 입력 데이터, 알고리즘, 평가 지표, 시스템 아키텍처를 프로토타입 설계로 연결합니다.
4. Palantir AIP, StealthMole, OSINT source catalog와 연결 가능한 분석 워크플로우를 도출합니다.
5. 기밀정보, 민감정보, 공격적 보안 행위 없이 공개 연구와 공개 데이터 범위에서만 검토합니다.

## Source Strategy

### Primary Scholarly Sources

- OpenAlex Works API: https://api.openalex.org/works
- arXiv API: https://export.arxiv.org/api/query
- DOI landing pages
- Publisher pages when open access is available

### Later Expansion Sources

- Semantic Scholar API
- IEEE Xplore, ACM Digital Library, Springer, MDPI, Elsevier, Nature, Sensors, Remote Sensing, JMSE
- Google Scholar는 수동 확인용으로만 사용합니다. 자동 scraping은 피합니다.
- 국내 논문은 RISS, KCI, DBpia, 국방 관련 학술지에서 수동 검색 후보로 둡니다.

## Topic Map

현재 검색식은 D4D track problem dataset을 기준으로 15개 topic으로 나누었습니다.

| Topic | Track | Purpose |
| --- | --- | --- |
| Multi-UxV control | T1 | 1인 다중 무인기 통제, human-swarm interaction |
| Terrain-aware autonomy | T1 | GPS/통신 거부환경, 지형 인지형 UAV 자율성 |
| Counter-UAS sensor fusion | T1 | RF, EO/IR, radar, vision 기반 드론 탐지·추적·요격 |
| Radio-silent IFF | T1 | 저방출 인증, challenge-response, replay/MITM 방어 |
| Fusion Intel Copilot | T2 | OSINT, 지식그래프, LLM, citation, provenance |
| Cyber Threat Intelligence | T2 | CTI, dark web, credential exposure, APT, entity resolution |
| Air ISR Fusion | T2 | 항적, 위성, 기상, OSINT 융합 |
| Sensor Fusion COP | T3 | Common Operational Picture, C2, sensor fusion |
| Semantic Tactical Network | T3 | 시맨틱 통신, bandwidth constrained tactical network |
| Sustainment Logistics | T3 | 군수, 예측정비, resilient logistics |
| Maritime AIS Anomaly | T4 | AIS anomaly detection, dark vessel, SAR-AIS fusion |
| Maritime Sensor Fusion | T4 | USV, sonar, EO/IR, radar, underwater sensing |
| Wargame AI Tutor | T5 | AI 교관, serious games, AAR, tactical simulation |
| On-device Tactical AI | T5 | offline RAG, edge LLM, on-device AI |
| LLM Reliability | T2/T3/T5 | hallucination, citation, eval, provenance |

## Collection Pipeline

1. 트랙별 문제를 problem ID 단위로 분해합니다.
2. 각 problem ID에 대해 영어 검색식을 만듭니다.
3. OpenAlex와 arXiv에서 논문 메타데이터를 수집합니다.
4. DOI 또는 normalized title로 중복 제거합니다.
5. track ID, problem ID, topic ID를 붙입니다.
6. 제목, 초록, citation count, open access 여부, 연도 기반으로 rough priority score를 계산합니다.
7. 사람이 직접 관련성을 확인해 `first_reading_queue.md`를 만듭니다.
8. 읽은 논문은 `paper_note_template.md` 형식으로 요약합니다.

## Triage Criteria

논문을 읽을 우선순위는 다음 순서로 봅니다.

| Criterion | Question |
| --- | --- |
| Problem fit | D4D 문제 statement와 직접 연결되는가? |
| Data relevance | 공개 데이터셋, benchmark, simulator, API 힌트가 있는가? |
| Method transferability | 24시간 해커톤 데모로 축소 구현 가능한가? |
| Evaluation clarity | 평가 지표가 명확한가? |
| System insight | architecture, workflow, data fusion 구조가 있는가? |
| Evidence quality | survey/review/benchmark/peer-reviewed/open access인가? |
| Safety | 민감정보·공격적 행위 없이 방어/분석/훈련 목적에 맞는가? |

## Output Schema

현재 1차 데이터셋은 다음 필드를 포함합니다.

| Field | Meaning |
| --- | --- |
| `id` | 로컬 안정 ID |
| `source` | OpenAlex, arXiv, or combined |
| `doi` | DOI |
| `title` | 논문 제목 |
| `authors` | 저자 목록 |
| `year` | 출판 연도 |
| `url` | DOI/arXiv/publisher link |
| `pdf_url` | 공개 PDF가 식별된 경우 |
| `is_open_access` | open access 여부 |
| `cited_by_count` | OpenAlex citation count |
| `concepts` | OpenAlex concepts 또는 arXiv category |
| `abstract` | 초록 |
| `topic_id` | D4D research topic |
| `track_ids` | 관련 트랙 |
| `problem_ids` | 관련 problem ID |
| `priority_score` | 자동 rough score |

## Reading Workflow

1. 5분 skim: 제목, 초록, 그림, 데이터셋, conclusion만 봅니다.
2. 15분 extraction: 입력 데이터, 방법, 출력, 평가 지표, 한계를 기록합니다.
3. D4D mapping: 어떤 트랙/문제/데모와 연결되는지 적습니다.
4. Prototype hook: 해커톤에서 만들 수 있는 최소 기능을 한 문장으로 씁니다.
5. Evidence trace: DOI, URL, dataset link, code link를 남깁니다.

## Versioning

- Raw API run log: `03_data/raw/literature/<version>/collection_run_log.json`
- Processed metadata: `03_data/processed/literature/versions/<version>/`
- Latest symlink: `03_data/processed/literature/current`
- Human-readable queue: `01_research/literature/literature_seed_catalog.md`

## Known Limitations

- 자동 검색은 citation이 높은 범용 AI 논문을 과대평가할 수 있습니다.
- OpenAlex metadata의 abstract와 citation count는 완벽하지 않을 수 있습니다.
- arXiv 논문은 peer review 상태가 다릅니다.
- 군사 도메인 논문은 공개 자료가 제한적이어서 civil/maritime/disaster/security 연구를 전이해야 합니다.
- 논문 원문 전체는 저작권상 무단 저장/재배포하지 않습니다. 링크와 메타데이터 중심으로 관리합니다.


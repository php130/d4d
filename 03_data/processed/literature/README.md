# Literature Dataset

OpenAlex와 arXiv에서 수집한 D4D 관련 논문 메타데이터입니다.

## Current Version

- Latest: `current`
- Versioned snapshots: `versions/<version>/`
- Raw run logs: `03_data/raw/literature/<version>/`

## Current Counts

- Version: `20260701_081735`
- Raw records: 265
- Deduped records: 228
- Topics: 15
- Queries: 32

## Main Files

- `current/dataset_manifest.json`: 수집 조건과 output 경로
- `current/literature_seed_catalog.json`: 논문 메타데이터 JSON
- `current/literature_seed_catalog.csv`: 논문 메타데이터 CSV
- `current/literature_seed_catalog.md`: 트랙별 상위 논문 목록

## Human-readable Research Files

- `01_research/literature/literature_research_methodology.md`
- `01_research/literature/literature_seed_catalog.md`
- `01_research/literature/first_reading_queue.md`
- `01_research/literature/paper_note_template.md`

## Caveats

- 이 데이터셋은 논문 원문이 아니라 메타데이터와 초록 중심입니다.
- 자동 검색 결과에는 범용 AI/IoT 논문이 섞일 수 있습니다.
- 실제 reading queue는 사람이 관련성을 확인한 `first_reading_queue.md`를 우선합니다.


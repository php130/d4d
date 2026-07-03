# Processed Dataset

Google Sheet 기반 D4D 자료를 분석/프로토타입에서 바로 쓰기 좋은 형태로 변환한 데이터셋입니다.

## Current Version

`current`는 최신 processed dataset version을 가리키는 심볼릭 링크입니다.

주요 파일:

- `current/dataset_manifest.json`: 데이터셋 출처, 생성 시각, row count, output 경로
- `current/track_problem_statements.json`: 트랙별 배경, 해결과제, 예시 접근 방향 구조화 데이터
- `current/track_problem_statements.csv`: 같은 데이터의 CSV 버전
- `current/glossary_terms.json`: 용어집 구조화 데이터
- `current/glossary_terms.csv`: 같은 데이터의 CSV 버전
- `current/tracks.json`: 트랙별 anchor partner, 확장 주제 등 메타데이터
- `current/track_problem_statements.md`: 사람이 읽기 좋은 트랙별 문제 정리본

## Schema

### track_problem_statements

| Field | Description |
| --- | --- |
| `id` | 트랙 내 순번 기반 ID. 예: `T2-001` |
| `track_id` | `T1` ~ `T5` |
| `track_title_en` | 트랙 영문명 |
| `track_title_ko` | 트랙 국문명 |
| `anchor_partners` | 시트에 기재된 트랙 anchor/partner |
| `expansions` | 공중 ISR, CCA 등 확장 주제 |
| `problem_type` | 범용, 특수상황, 공중 등 원문 유형 |
| `problem_type_tags` | 유형을 배열로 분리한 값 |
| `problem_name` | 원문 문제명 |
| `problem_name_ko` | 문제명 국문 |
| `problem_name_en` | 문제명 영문 |
| `background` | 배경 |
| `challenge` | 해결과제/문제 |
| `example_approach` | 예시 접근 방향 원문 |
| `example_approach_items` | 예시 접근 방향을 항목 배열로 분리한 값 |
| `notes` | 비고 |
| `source` | spreadsheet id, sheet, gid, source row, version |

### glossary_terms

| Field | Description |
| --- | --- |
| `id` | 용어 ID |
| `category` | 용어 구분 |
| `term` | 용어/약어 |
| `english` | 영문 full name |
| `description` | 설명 |
| `related_tracks` | 관련 트랙 배열 |
| `source` | spreadsheet id, sheet, gid, source row, version |

## Versioning Rule

시트가 바뀌면 새 timestamp version을 만들고 `current`를 갱신합니다. 과거 버전은 `versions/<version>/` 아래에 그대로 둡니다.


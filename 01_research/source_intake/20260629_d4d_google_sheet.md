# Source Intake: D4D Google Sheet

## Metadata

- Date reviewed: 2026-06-29
- Source title: D4D_SEOUL_참가자안내(260629/공개)
- URL: https://docs.google.com/spreadsheets/d/1l_ThafA1n5Wue2BnPeJ1FPpiZvThG6X9iIPRuJsxR5o/edit
- Source type: Google Sheets
- Access status: public export available, connector metadata readable
- Local version: `20260629_200733`

## Sheets Inspected

| Sheet | gid | Use |
| --- | --- | --- |
| `A.운영 시간표` | `177708301` | 운영 일정 참고 |
| `B-1. 문제_참가자안내` | `1073579156` | 참가자 안내 |
| `B-2. 트랙별_문제` | `1313109997` | 트랙별 문제 데이터셋 구축 |
| `B-3. 용어집` | `1682873298` | glossary 업데이트 |

## Extracted Dataset

- Track problem statements: 23
- Tracks: 5
- Glossary terms: 88

## Key Takeaway

시트는 해커톤 문제정의의 canonical source로 취급합니다. 변경 가능성이 있으므로 매번 raw CSV snapshot과 processed JSON/CSV version을 함께 남기고, `current` 심볼릭 링크만 최신 버전으로 갱신합니다.

## Follow-up

- T2 문제 4개를 기준으로 팀 역량/데이터 접근성/데모 가능성을 평가합니다.
- StealthMole 및 Palantir AIP 접근 가능 여부에 따라 T2-001, T2-003, T2-004 중 우선순위를 정합니다.


# OSINT Ethics and Safety Notes

OSINT 프로젝트는 공개 정보를 다루더라도 안전, 개인정보, 약관, 운영보안 문제가 생길 수 있습니다. 이 문서는 프로젝트 진행 중 계속 업데이트합니다.

## Principles

- 합법적이고 접근 권한이 있는 자료만 사용합니다.
- 기밀·군사보안·민감정보를 수집하거나 공유하지 않습니다.
- 개인정보와 민감정보는 최소 수집, 최소 보관합니다.
- 출처, 수집 시점, 사용 조건을 기록합니다.
- 다크웹/유출 데이터는 원문 보관을 피하고 필요한 indicator와 요약만 남깁니다.
- 실제 개인이나 조직에 피해를 줄 수 있는 공개/시연 방식은 피합니다.
- 해킹, 침투, 우회, credential 사용, 악성코드 실행은 하지 않습니다.
- 실제 환경에 영향을 주는 활동은 해커톤 범위 밖으로 봅니다.

## Data Handling

- `03_data/raw/`: 원본 데이터. 가능하면 공개 샘플과 링크 위주로 보관합니다.
- `03_data/processed/`: 민감값을 마스킹한 분석용 데이터만 둡니다.
- `03_data/samples/`: 데모에 사용할 작은 샘플을 둡니다.
- API keys, access tokens, credentials는 저장소에 저장하지 않습니다.
- 원본 데이터(raw data)는 외부 공개 및 재배포하지 않습니다.
- 외부 연결 데이터는 해커톤 목적 범위 내에서만 사용합니다.

## Demo Safety

- 실제 개인 이메일, 전화번호, 계정명, credential은 화면에 노출하지 않습니다.
- 실제 민감 사건을 다룰 때는 샘플화/익명화합니다.
- 리스크 점수는 "조사 우선순위"로 표현하고 단정적 혐의 표현은 피합니다.
- GitHub, GitLab, 발표자료, 데모 영상에는 원본 DB와 raw data를 넣지 않습니다.
- 심사용 제출물에는 최소한의 샘플 데이터만 포함합니다.

## D4D Rules References

- `00_admin/hackathon_rules.md`: 해커톤 규칙 원문 정리
- `08_ops/security_compliance/hackathon_submission_checklist.md`: 제출 전 보안 체크리스트

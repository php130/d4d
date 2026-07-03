# data.go.kr API Application Status

Last updated: 2026-07-04

## Key Status

- Account: `[REDACTED_ACCOUNT]`
- General API key: issued on 2026-07-03
- Local storage: project root `.env`
- Environment variables: `DATA_GO_KR_SERVICE_KEY`, `DATA_GO_KR_SERVICE_KEY_PLAIN`, `DATA_GO_KR_KEY_ISSUED_AT`
- Do not copy the key into docs, slides, GitHub, prompts, or shared files.

## Approved Development Accounts

| Public data PK | API | Type | D4D use |
| --- | --- | --- | --- |
| 15129394 | 조달청_나라장터 입찰공고정보서비스 | REST, JSON/XML | 조달·공급망 이벤트, 품목/기관/일정 기반 신호 |
| 15084084 | 기상청_단기예보 조회서비스 | REST | 기상 위험 이벤트, 해상/물류 작전환경 보강 |
| 15058815 | 조달청_나라장터 공공데이터개방표준서비스 | REST, JSON/XML | 입찰·낙찰·계약 표준 데이터, 공급망/기관 관계 분석 |
| 15116876 | 대한무역투자진흥공사_국가 목록 | REST | 국가 메타데이터, 지역/국가 엔티티 정규화 |
| 15134045 | 대한무역투자진흥공사_미국 글로벌 이슈 모니터링 정보 | REST | 글로벌 이슈·규제·공급망 리스크 브리핑 |

## Application Attempts Requiring Verification

| Public data PK | API | Type | Status | Next check |
| --- | --- | --- | --- | --- |
| 15129186 | 해양수산부_선박 AIS 동적정보 | File-data auto-converted JSON/XML | 신청 폼 작성 및 확인 다이얼로그 승인 시도. 최종 목록 확인 전 Chrome 제어 타임아웃 | 공공데이터포털 `활용신청 현황`에서 승인/신청 여부 재확인 |
| 15141997 | 해양수산부_지능형해양수산재난정보체계_AIS정보 | File-data auto-converted JSON/XML | planned | 15129186 상태 확인 후 같은 `redirectDevAcountRequestForm.do` 패턴으로 신청 |
| 15128156 | 해양수산부_해운항만물류정보시스템_선박관제정보 | File-data auto-converted JSON/XML | planned | Port anomaly demo용으로 신청 |

## Not data.go.kr Key Targets

아래 항목은 공공데이터포털 상세 페이지에 있지만 `API 유형: LINK`로 표시됩니다. data.go.kr 일반 인증키 신청 대상이 아니며, 원 제공기관에서 별도 인증키/신청 절차를 진행해야 합니다.

| Public data PK | Data | Linked source | Next step |
| --- | --- | --- | --- |
| 15040463 | 국토교통부_교통소통정보 | https://www.its.go.kr/opendata/opendataList?service=traffic | ITS 국가교통정보센터 OpenAPI 키/신청 확인 |
| 15040465 | 국토교통부_돌발상황정보 | https://www.its.go.kr/opendata/opendataList?service=event | ITS 국가교통정보센터 OpenAPI 키/신청 확인 |
| 15139684 | 행정안전부_공유플랫폼_재난대응기관 | https://www.safetydata.go.kr/disaster-data/view?dataSn=783 | 재난안전데이터 공유플랫폼 회원가입/활용신청 필요 |

## Application Reason Used

> D4D 해커톤용 연구·프로토타입입니다. 공개 데이터를 해상·기상·재난·물류 OSINT와 융합해 거부환경에서도 핵심 이벤트만 COP에 전송·갱신하는 데모를 구축합니다. 원본 데이터는 외부 공개하지 않고 비식별 샘플만 사용합니다.

## Notes

- data.go.kr 안내상 신규 신청 API는 1~2시간 뒤 호출 가능할 수 있습니다.
- 첫 smoke test는 나라장터 입찰공고 1건, 기상청 단기예보 1건, KOTRA 국가 목록 1건 순서로 진행합니다.

## Smoke Test Log

| Date | API | Result | Note |
| --- | --- | --- | --- |
| 2026-07-03 | 기상청_단기예보 조회서비스 | Success | `resultCode=00`, `NORMAL_SERVICE`, sample forecast item returned |
| 2026-07-03 | 조달청_나라장터 입찰공고정보서비스 | Needs follow-up | Immediate call returned `Unauthorized`; retry after propagation and verify endpoint/operation parameters |
| 2026-07-04 | 기상청_단기예보 조회서비스 | Success | `smoke_test_api_sources.py` run `20260704_002947`; `resultCode=00`, `NORMAL_SERVICE` |

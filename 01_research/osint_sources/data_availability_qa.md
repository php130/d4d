# Data Availability Q&A

입수일: 2026-06-29

## Question

트랙별 세부주제 중 "해상 환경 적응형 무인 감시 자산 기반 위협 탐지 및 센서 퓨전 기술"처럼 신호 및 데이터 처리 주제가 있는데, 이를 위한 데이터셋은 주최 측에서 제공되는가? 아니면 참가팀이 직접 데이터를 구해서 시스템을 만들어야 하는가?

## Answer Summary

- 주최 측에서 별도 데이터셋을 기본 제공하지 않습니다.
- 참가팀이 필요한 공개(Open Source) 데이터를 직접 탐색하고 활용해야 합니다.
- 웹, Telegram, 공개 API 등 다양한 오픈소스 접근이 가능할 수 있습니다.
- 확보하기 어려운 데이터를 수집·융합하는 과정 자체도 제품 형태가 될 수 있습니다.
- 행사 전 활용 가능한 오픈소스 데이터, 웹사이트, 레퍼런스 자료를 별도로 공유할 예정이지만 참고용입니다.
- 주최 측도 행사 전까지 유의미한 데이터셋/API 연결을 위해 노력 중입니다.

## Mentioned References

- MarineTraffic: https://marinetraffic.com/
  - AIS 트래킹 정보 확인 가능.
- AI Hub: https://www.aihub.or.kr/
  - 일부 국방 합성 데이터 참고 가능.
- 해상 및 드론 관련 공개 SIGINT/SIGNT 데이터
  - 원문에는 `SIGNT`로 표기되어 있었으나, 일반적으로는 `SIGINT`(Signals Intelligence)를 의미할 가능성이 있습니다. 추후 출처 확인 필요.

## Implications for D4D Project

- 데이터 확보 전략이 솔루션의 핵심 경쟁력이 될 수 있습니다.
- `03_data/raw/`에는 원본을 무분별하게 보관하지 않고, 출처와 접근 조건을 먼저 기록합니다.
- 데모는 공개 데이터, 합성 데이터, 샘플 데이터 중심으로 설계합니다.
- 데이터가 부족한 트랙은 "수집·정규화·융합 파이프라인" 자체를 프로덕트로 볼 수 있습니다.
- 특히 T2, T4는 공개 API, 웹 데이터, AIS, 위성/기상/뉴스/제재 목록, 다크웹 인텔리전스 등 다중 소스 융합이 중요합니다.

## Follow-up Research Queue

- MarineTraffic의 무료 접근 범위, 약관, API 제공 여부 확인
- AI Hub 국방/해상/드론/센서 관련 공개 데이터셋 탐색
- 공개 AIS 대체 소스 탐색
- 공개 위성/기상/해상 이벤트 데이터 소스 탐색
- 해상 및 드론 관련 공개 SIGINT/SIGNT 데이터셋 여부 확인

## Related Catalog

- `01_research/osint_sources/osint_source_catalog.md`: 국내외 OSINT/공공데이터 소스 1차 카탈로그

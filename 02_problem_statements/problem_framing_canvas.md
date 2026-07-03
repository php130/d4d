# Problem Framing Canvas

아이디어가 생길 때마다 이 문서를 업데이트합니다. 좋은 D4D 문제정의는 "데이터를 많이 모은다"가 아니라 "특정 사용자에게 특정 판단을 더 빠르고 정확하게 하게 한다"여야 합니다.

## Candidate 1: OSINT Risk Briefing Copilot

- User: 국방/안보 분석가, 군 정보 담당자, 방산 보안 담당자
- Decision: 특정 조직/지역/사건에 대해 어떤 위협이 우선순위인지 판단
- Inputs: 키워드, 조직명, 지역, 기간, 공개 뉴스, SNS, 제재 목록, 다크웹 노출 신호
- Outputs: 근거 기반 위협 브리핑, 엔티티 그래프, 리스크 스코어, 추천 액션
- Why now: 공개 정보는 많지만 출처 간 연결과 설명 가능한 요약이 어렵다
- Demo shape: 대상 입력 -> 수집/분석 -> 그래프/지도 -> 3분 브리핑 생성

## Candidate 2: Defense Supply Chain Exposure Watch

- User: 방산 기업/군 조달/보안 담당자
- Decision: 특정 공급업체나 부품 공급망이 사이버/제재/지정학 리스크에 노출되었는지 판단
- Inputs: 공급업체명, 도메인, 이메일 도메인, 국가, 제재/뉴스/유출 credential 신호
- Outputs: 공급망 리스크 레포트, 노출 근거, 재점검 우선순위
- Why now: 방산 공급망은 사이버/지정학/제재 리스크가 복합적이다
- Demo shape: 업체 리스트 업로드 -> 외부 신호 매칭 -> 위험순 정렬 -> remediation checklist

## Candidate 3: Maritime Suspicious Activity Triage

- User: 해상 안보 분석가, 항만/해경/군 관계자
- Decision: 특정 선박/항만/해역에서 이상징후가 있는지 판단
- Inputs: AIS, 선박명/IMO, 항만, 제재 목록, 뉴스, 위성/항로 이벤트
- Outputs: 이상 패턴, 관련 조직/선박 관계, 근거 링크, 조사 우선순위
- Why now: MDA 트랙과도 연결되고 OSINT 데이터 조합이 명확하다
- Demo shape: 해역 선택 -> 선박 이벤트 탐색 -> 제재/뉴스 매칭 -> 리스크 지도

## Selection Criteria

| Criterion | Weight | Question |
| --- | ---: | --- |
| Problem Fit | 25 | 실제 국방/안보 의사결정 문제인가? |
| Military Deployability | 30 | 권한, 보안, 네트워크, 현장 제약을 고려했는가? |
| Technical Execution | 25 | 24시간 안에 작동하는 데모를 만들 수 있는가? |
| Creativity | 20 | 단순 챗봇/대시보드 이상인가? |


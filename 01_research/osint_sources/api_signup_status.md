# API Signup Status

Last updated: 2026-07-04

목표 계정: `[REDACTED_ACCOUNT]`

이 문서는 API key 발급을 위해 각 서비스의 회원가입/신청 절차를 어디까지 진행했는지 기록합니다. 비밀번호, OTP, 본인인증, CAPTCHA, 약관 동의처럼 사용자 본인이 처리해야 하는 단계는 여기에서 `Needs user`로 표시합니다.

| Priority | Service | Status | Current blocker | URL |
| --- | --- | --- | --- | --- |
| P0 | 공공데이터포털 | Issued | 로그인 완료. 일반 인증키 발급 후 `.env`에 저장. 개발계정 승인 API 5건 확보. `LINK` 유형 교통/재난 API는 ITS·safetydata 별도 신청 필요 | https://www.data.go.kr/iim/api/selectApiKeyList.do |
| P0 | 기상청 API허브 | Issued | 인증키 저장 완료. 실제 로그인은 이메일 식별자 기준으로 동작. 단기 해상예보 API 활용신청 완료 및 smoke test 통과. 다른 단기/특보 endpoint는 필요 시 추가 신청 | https://apihub.kma.go.kr/mypage.do |
| P0 | AI Hub | Needs user | 일반회원 선택 완료, 약관/개인정보 동의 체크 필요 | https://www.aihub.or.kr/join/stplatAgre.do?currMenu=108&topMenu=108&mberSe=1 |
| P0 | VWorld | Issued | 기존 개발키 확인 후 `.env`에 저장. 주소/geocoding smoke test 통과 | https://www.vworld.kr/mypo/mypo_apiKey_s001.do |
| P1 | 재난안전데이터 공유플랫폼 | In progress | 2026-07-04 재로그인 확인. 행정안전부_긴급재난문자 이용신청은 `승인대기`, 표 수정일 2026-07-04. 추가 데이터 신청은 현재 사이트 알림으로 보류 | https://www.safetydata.go.kr/myPage_7 |
| P1 | 생활안전지도 OpenAPI | Needs user | 인증키 발급 전 필수 약관 동의 필요 | https://www.safemap.go.kr/opna/crtfc/keyAgreeRenew.do |
| P1 | Global Fishing Watch | Issued | 이메일 인증 완료 확인. API user info 저장, `D4D Semantic Maritime COP` token 생성 후 `.env` 저장. 4Wings AIS vessel presence bins smoke test 통과 | https://globalfishingwatch.org/our-apis/tokens |
| P2 | Copernicus Data Space | Issued | OData access token 생성 및 `.env` 저장. Sentinel-1 catalogue smoke test 통과. 토큰은 단기 만료라 재발급 helper 필요 | https://documentation.dataspace.copernicus.eu/APIs/Token.html |
| P2 | NASA Earthdata | Issued | 웹 프로필에서 bearer token 생성 및 `.env` 저장. CMR collection smoke test 통과 | https://urs.earthdata.nasa.gov/users/mollykim/user_tokens |
| P1 | OpenSanctions | Issued | 로그인 성공. Trial API key 자동 생성 및 `.env` 저장. `/match/default` smoke test 통과. Trial key 만료일 2026-08-02, quota 50 req/mo | https://www.opensanctions.org/account/ |
| P1 | alerts.in.ua | In progress | 2026-07-04 사용자가 API 요청 form 제출 완료. 토큰 승인 메일 대기, 스팸함 확인 필요. 7일 내 미수신 시 재요청 또는 `api@alerts.in.ua` 문의 | https://alerts.in.ua/api-request |
| P0 | NASA FIRMS | Issued | MAP_KEY `.env` 저장 완료. Ukraine tiny AOI smoke test 통과 | https://firms.modaps.eosdis.nasa.gov/api/map_key/ |
| P0 | ACLED | Blocked | 제공된 계정으로 OAuth token 요청 시 `invalid_grant` / incorrect credentials. ACLED 비밀번호 또는 이메일 인증 상태 확인 필요 | https://acleddata.com/user/login |
| P1 | Kaggle | Issued | 이메일 로그인 성공. `D4D Ukraine OSINT` API token 생성 후 `.env` 및 `~/.kaggle/access_token` 저장. Bearer API smoke test 통과 | https://www.kaggle.com/settings/api |
| P1 | HDX | Issued | 로그인 성공. `D4D Ukraine OSINT` API token 생성 후 `.env` 저장. CKAN smoke test 통과. token 만료 2026-08-03 | https://data.humdata.org/user/mollykim/api-tokens |
| P1 | StealthMole | Issued | Access key / Secret key `.env` 저장 완료. 공개 문서상 API base URL과 signing 방식이 확인되지 않아 smoke test는 보류 | https://platform.stealthmole.com |
| P1 | MarineTraffic | Needs user | API는 `api_key` 인증이나 Kpler/MarineTraffic 데이터 서비스 문의·데모/상용 접근 필요 | https://www.kpler.com/product/maritime/data-services |
| P3 | UN Comtrade | Needs user | Azure API Management 개발자 포털 로그인 필요; 제품/구독 키 목록은 로그인 뒤 접근 | https://comtradedeveloper.un.org/signin |
| P2 | Space-Track | Needs user | 이메일/조직/관심분야/성명/전화번호/주소/국가 및 User Agreement 동의 필요 | https://www.space-track.org/auth/createAccount |
| P3 | KISA C-TAS | Needs user | 회원가입 및 관리자 승인 필요; 아이디/비밀번호/기업명/회사 개인 이메일/휴대전화/약관 동의 필요 | https://ctas.krcert.or.kr/member/join |

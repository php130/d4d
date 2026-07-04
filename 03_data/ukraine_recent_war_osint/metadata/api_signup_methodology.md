# API Signup Methodology for Ukraine Recent War OSINT Dataset

- Date: 2026-07-04 KST
- Dataset root: `/Users/mollykim/projects/D4D/03_data/ukraine_recent_war_osint`
- Placeholder file: `/Users/mollykim/projects/D4D/03_data/ukraine_recent_war_osint/raw/blocked_or_key_required/api_placeholders.json`

## Purpose

이 문서는 `ukraine_recent_war_osint` 데이터셋의 blocker로 남아 있는 외부 API를 사용하기 위해 사용자가 직접 가입하거나 승인 요청해야 하는 절차를 정리합니다.

키와 비밀번호는 문서에 적지 않고 `/Users/mollykim/projects/D4D/.env`에만 저장합니다.

## Priority Summary

| Priority | Source | User action | Store in `.env` | Why it matters |
|---|---|---|---|---|
| P0 | ACLED | blocked: provided credentials failed OAuth | `ACLED_EMAIL`, `ACLED_ACCESS_TOKEN`, `ACLED_REFRESH_TOKEN` | 가장 깔끔한 conflict event spine |
| P0 | NASA FIRMS | MAP_KEY issued; smoke passed | `NASA_FIRMS_MAP_KEY` | 공격 후 화재/열원 proxy |
| P0 | alerts.in.ua | API token request submitted; wait for approval email | `ALERTS_IN_UA_TOKEN` | 공습경보/경보 지속시간 layer |
| P1 | Kaggle | API token issued; smoke passed | `KAGGLE_USERNAME`, `KAGGLE_API_TOKEN` | missile/UAV dataset 공식 package fetch |
| P1 | ReliefWeb | pre-approved `appname` 요청 | `RELIEFWEB_APPNAME` | humanitarian/official report evidence |
| P2 | HDX | API token issued; CKAN smoke passed | `HDX_API_TOKEN` | humanitarian admin/context datasets |

## Site Handoff Matrix

아래는 실제 접근을 확인한 사이트와 사람이 필요한 지점입니다.

| Source | Signup / request site | Current check | Human-needed blocker | What to send back to Codex |
|---|---|---|---|---|
| ACLED | `https://acleddata.com/user/login` | OAuth token request returned `invalid_grant` for provided credentials | verify password or account email activation | corrected password or OAuth access/refresh tokens |
| NASA FIRMS | `https://firms.modaps.eosdis.nasa.gov/api/map_key/` | MAP_KEY stored; tiny Ukraine AOI smoke passed | none | `NASA_FIRMS_MAP_KEY` already stored |
| alerts.in.ua | `https://alerts.in.ua/api-request`; docs `https://devs.alerts.in.ua/` | user submitted browser form on 2026-07-04 and saw Tally thank-you confirmation page | wait for token email; check spam; if no response within 7 days, assume rejected and retry with clearer non-real-time research use case or contact `api@alerts.in.ua` | `ALERTS_IN_UA_TOKEN` |
| Kaggle | `https://www.kaggle.com/settings/api` | email login succeeded; `D4D Ukraine OSINT` API token issued and stored | official dataset terms may still need browser acceptance before package download | `KAGGLE_API_TOKEN` already stored |
| ReliefWeb | docs `https://apidoc.reliefweb.int/parameters`; appname request form `https://docs.google.com/forms/d/e/1FAIpQLScR5EE_SBhweLLg_2xMCnXNbT6md4zxqIB00OL0yZWyrqX_Nw/viewform?usp=header` | docs reachable; appname form link extracted | submit form and wait for approval email | approved `RELIEFWEB_APPNAME` |
| HDX | `https://data.humdata.org/user/mollykim/api-tokens` | login succeeded; API token issued and CKAN smoke passed | token expires 2026-08-03; regenerate if needed after that date | `HDX_API_TOKEN` already stored |

## Current Technical Findings

| Source | No-human progress completed | Result |
|---|---|---|
| ACLED | Tried OAuth token request with provided password and one known password pattern | blocked: credentials incorrect |
| NASA FIRMS | Stored MAP_KEY and ran tiny AOI CSV smoke test | passed |
| alerts.in.ua | Tried docs/request pages from current environment, then user submitted the request in browser | request submitted; token email pending |
| Kaggle | Logged in by email, created API token, stored token, and ran direct Bearer API smoke test | passed |
| ReliefWeb | Opened API docs and extracted appname Google Form link | appname approval needed before API use after 2025-11-01 |
| HDX | Logged in, created API token, and ran authorized CKAN package search | passed |

## 1. ACLED

### What To Get

ACLED는 key-only 방식보다 myACLED 계정 기반 인증으로 보는 것이 맞습니다. 공식 문서 기준으로:

- 브라우저/툴 기반: cookie-based authentication
- 스크립트 기반: OAuth access token / refresh token
- access token은 24시간, refresh token은 14일 유효

### Current Status

OAuth token issuance was attempted on 2026-07-04 using the provided account credentials. ACLED returned `invalid_grant`, meaning the credentials were not accepted.

Remaining human step:

1. Verify the ACLED password and whether the account email activation is complete.
2. Send the corrected password or generate OAuth tokens manually.
3. Re-run `/Users/mollykim/projects/D4D/06_prototype/scripts/smoke_test_ukraine_osint_sources.py`.

### Recommended Env

```bash
ACLED_EMAIL=
ACLED_PASSWORD=
ACLED_ACCESS_TOKEN=
ACLED_REFRESH_TOKEN=
ACLED_TOKEN_ISSUED_AT=
```

### First Smoke Test

Target query:

```text
GET https://acleddata.com/api/acled/read?_format=json&country=Ukraine&event_date=2025-12-01|2026-07-04&event_date_where=BETWEEN&limit=10
Authorization: Bearer <ACLED_ACCESS_TOKEN>
```

Expected output:

- conflict events with dates, locations, event type, sub-event type, actors, source, notes.

### Dataset Use

Use ACLED as structured evidence for:

- `conflict_event_report`
- `infrastructure_attack_context`
- `frontline_activity_context`
- `civilian_impact_context`

Do not treat ACLED alone as a real-time targeting source.

## 2. NASA FIRMS

### What To Get

NASA FIRMS requires a free `MAP_KEY` for API and map services. The key is requested with an email and sent to that email.

### Current Status

MAP_KEY was provided, stored in `.env`, and smoke tested on 2026-07-04.

Latest report:

```text
/Users/mollykim/projects/D4D/03_data/processed/ukraine_osint_api_smoke_tests/20260704_114329/smoke_report.json
```

### Env

```bash
NASA_FIRMS_MAP_KEY=
```

### First Smoke Test

Ukraine bounding box:

```text
GET https://firms.modaps.eosdis.nasa.gov/api/area/csv/<MAP_KEY>/VIIRS_SNPP_NRT/22,44,40,53/10/2026-07-04
```

Expected output:

- CSV rows with latitude, longitude, brightness, confidence, acquisition date/time, satellite, instrument.

### Dataset Use

Use FIRMS as thermal anomaly evidence for:

- `thermal_anomaly_near_infrastructure`
- `possible_fire_after_attack`
- `port_or_energy_disruption_context`

Do not claim a thermal anomaly is a confirmed missile strike unless corroborated by other sources.

## 3. alerts.in.ua

### What To Get

alerts.in.ua provides air raid alert and other threat alert data for Ukraine. Public client libraries indicate an API token is required, obtained by an API request form or support contact.

### Request Status

The API access request form was submitted by the user on 2026-07-04. The browser showed the Tally thank-you confirmation page.

Remaining human step:

1. Check the request email inbox and spam folder.
2. If approved, send the token to Codex or paste it into `/Users/mollykim/projects/D4D/.env` as `ALERTS_IN_UA_TOKEN`.
3. If no response arrives within 7 days, retry with a clearer non-real-time research purpose or contact `api@alerts.in.ua`.

### Env

```bash
ALERTS_IN_UA_TOKEN=
```

### First Smoke Test

Use the official API docs or Python client once token is issued.

Expected output:

- active or historical alerts by region, started/finished timestamps, alert type.

### Dataset Use

Use as warning pressure evidence for:

- `air_alert_active`
- `alert_duration_high`
- `missile_uav_warning_priority`

For public demo, prefer delayed/historical mode over live operational display.

## 4. Kaggle

### What To Get

Kaggle API supports OAuth login in the CLI and API tokens from account settings. For this dataset, credentials are needed to fetch the official package for `piterfm/massive-missile-attacks-on-ukraine`.

### Current Status

Kaggle login succeeded with the email account on 2026-07-04. A new API token named `D4D Ukraine OSINT` was generated and stored in:

- `.env` as `KAGGLE_API_TOKEN`
- `/Users/mollykim/.kaggle/access_token`

The direct Bearer API smoke test passed. Local PyPI versions of `kaggle`/`kagglehub` are older than the documented token-support versions in this environment, so collectors should use direct HTTP Bearer calls unless the local Kaggle tooling is updated.

Possible remaining browser step:

1. Open the target dataset page if a download fails.
2. Accept dataset terms if Kaggle requires it.

### Env

```bash
KAGGLE_API_TOKEN=
```

### First Smoke Test

```text
GET https://www.kaggle.com/api/v1/datasets/list?search=ukraine+missile&page=1&pageSize=5
Authorization: Bearer <KAGGLE_API_TOKEN>
```

### Dataset Use

Use as official package fetch for:

- `missile_uav_attack_wave`
- `interception_rate_context`
- `daily_attack_pressure`

## 5. ReliefWeb

### What To Get

ReliefWeb API v2 is read-only, but from 2025-11-01 API users need a pre-approved `appname`. It is not a secret key, but it must be approved.

### User Request Steps

1. Open ReliefWeb API docs: `https://apidoc.reliefweb.int/parameters`.
2. Open the appname request form: `https://docs.google.com/forms/d/e/1FAIpQLScR5EE_SBhweLLg_2xMCnXNbT6md4zxqIB00OL0yZWyrqX_Nw/viewform?usp=header`.
3. Request an appname using a format like:

```text
d4d-molly-ukraine-osint-<random>
```

4. Use purpose:
   - non-commercial D4D hackathon research prototype
   - humanitarian/official report metadata for Ukraine scenario context
   - local data processing, citations retained, no full copyrighted article republication
5. Wait for approval email.

### Env

```bash
RELIEFWEB_APPNAME=
```

### First Smoke Test

```text
GET https://api.reliefweb.int/v2/reports?appname=<RELIEFWEB_APPNAME>&query[value]=Ukraine&limit=10
```

Expected output:

- report metadata, titles, dates, source, country, disaster tags, URLs.

### Dataset Use

Use as citation-backed humanitarian context:

- `humanitarian_report_context`
- `infrastructure_impact_report`
- `evacuation_or_displacement_context`

Do not archive full report bodies unless license allows it.

## 6. HDX

### What To Get

HDX has two relevant API surfaces:

- HDX CKAN API: dataset metadata/resource discovery and downloads.
- HDX HAPI: standardized humanitarian indicators from selected providers.

Read-only CKAN discovery often works without a personal token, but an account/API token helps with browser/session friction and some workflows.

### Current Status

HDX login succeeded on 2026-07-04. A token named `D4D Ukraine OSINT` was generated from `https://data.humdata.org/user/mollykim/api-tokens`, stored in `.env`, and used successfully against CKAN package search.

Token expiry recorded from the HDX page:

```text
2026-08-03T02:41:57Z
```

Basic CKAN search also works without a token, but the stored token is useful for account-protected workflows and Tabular Data Endpoints if needed.

### Env

```bash
HDX_API_TOKEN=
```

This may be optional for read-only pulls.

### First Smoke Test

CKAN metadata search:

```text
GET https://data.humdata.org/api/3/action/package_search?q=Ukraine&rows=20
```

If using token:

```text
Authorization: <HDX_API_TOKEN>
```

### Dataset Use

Use HDX for:

- admin boundaries / COD context
- humanitarian needs and response context
- infrastructure and population exposure datasets when available

Keep source license and update date in metadata.

## Operational Checklist

1. User completes signup/request for ACLED, FIRMS, alerts.in.ua, Kaggle, ReliefWeb, HDX.
2. Store issued values only in `.env`.
3. Run one tiny smoke test per source.
4. Save raw samples under `raw/api_snapshots/<run_id>/`.
5. Convert to normalized observations.
6. Convert observations to semantic events.
7. Keep raw API responses out of public demo artifacts unless license permits redistribution.

## Suggested Signup Order

1. NASA FIRMS: fastest, email-only, high scenario value.
2. Kaggle: fastest if account exists, unlocks official missile/UAV package.
3. ACLED: highest analytical value, but OAuth connector work needed.
4. ReliefWeb: request pre-approved appname early because approval may take time.
5. alerts.in.ua: request early because token approval may take time.
6. HDX: lower urgency unless we need humanitarian/admin datasets beyond current package.

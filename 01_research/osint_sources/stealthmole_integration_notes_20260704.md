# StealthMole Integration Notes

- Date: 2026-07-04 KST
- Project: D4D / Resilient Maritime COP over Denied Networks
- Credential storage: `/Users/mollykim/projects/D4D/.env`
- Env keys: `STEALTHMOLE_ACCESS_KEY`, `STEALTHMOLE_SECRET_KEY`, `STEALTHMOLE_KEY_STATUS`

## Current Status

The StealthMole API access key and secret key were stored in `.env` on 2026-07-04.

Smoke test status:

- `not_run_endpoint_unconfirmed`
- Public pages confirm access-key/secret-key licensing and platform/API integration, but the actual REST base URL and request signing pattern are not clearly exposed in public documentation.
- Next step is to obtain StealthMole API documentation from the platform, the confirmation email, support, or an approved integration package.

## Source Findings

Public StealthMole and integration pages indicate the following capability areas:

| Module | Publicly described capability | Useful fields / signals | D4D relevance |
|---|---|---|---|
| Darkweb Tracker | Search deep/dark web content with 52 indicators, link analysis, map view for IP/GPS-bearing data, historical snapshots | keyword hits, source, indicator type, IP/domain/url/hash/wallet/file metadata, first/last seen where available | cyber threat context for ports, logistics, government agencies, telecom operators, and defense-adjacent suppliers |
| Dark Web Monitoring | Incident alert feeds for ransomware, leaked data, and government-focused threats | victim, ransomware gang, detection date, ransomware URL, victim site, victim country, sector, leak title, bad actor, source URL | `CYBER_INCIDENT_CONTEXT`, `RANSOMWARE_VICTIM_ALERT`, `GOVERNMENT_LEAK_ALERT` |
| Credential Lookout | Detect credentials exposed through breached databases or leaks | leaked username, leaked date, leak source; password may exist but should not be stored in D4D outputs | aggregate credential exposure risk only; do not collect or display raw passwords |
| Compromised Data Set | Malware-infected device credential leakage by domain/email/keyword | domain, leaked username, leaked date, leaked data source or bad actor; password may exist but must be suppressed | enterprise/agency exposure context, supply-chain cyber risk, internal domain hygiene |
| Telegram Tracker | Search/filter/extract/analyze Telegram channels, groups, messages, and user/group relations | channel/group/message hits, Telegram URL/type/subtype/name/username/bio, media/history retrieval depending on entitlement | cybercrime chatter, disinformation/threat rumors, port/logistics fraud signals; use only public/authorized data |

## Recommended Use In Our Project

StealthMole should be a cyber-threat enrichment layer, not a primary maritime sensor.

Good demo patterns:

1. Monitor a synthetic port operator domain, telecom domain, logistics vendor, or defense supplier name.
2. Convert results into a compact semantic event:
   - `entity`: hashed/synthetic organization or infrastructure node
   - `event_type`: `DARKWEB_MENTION`, `CREDENTIAL_EXPOSURE_AGGREGATE`, `RANSOMWARE_CONTEXT`, `TELEGRAM_THREAT_MENTION`
   - `severity`: based on source type, recency, sector, and corroboration
   - `evidence_ref`: source/module/count/time, not raw leaked content
3. Send only the semantic event over the degraded network channel.
4. Keep raw results internal and never present raw credentials, private messages, contact data, faces, or doxxing-style details.

## Candidate Semantic Events

| Event type | Trigger | Payload fields for COP | Priority contribution |
|---|---|---|---|
| `CREDENTIAL_EXPOSURE_AGGREGATE` | Credential Lookout or Compromised Data Set returns domain exposure | domain_hash, exposure_count, newest_leak_month, source_family, confidence | raises cyber risk for an operator, port, agency, or supplier |
| `RANSOMWARE_VICTIM_ALERT` | Dark Web Monitoring finds a victim in relevant sector/country | victim_alias, sector, country, detection_date, gang_alias, source_ref | high priority if logistics/energy/telecom/port sector |
| `DATA_LEAK_CONTEXT` | leaked-data/government monitoring hit | title_summary, actor_alias, detection_date, source_ref, affected_sector | medium/high depending on entity criticality |
| `TELEGRAM_THREAT_MENTION` | Telegram Tracker keyword/channel hit | keyword, source_type, timestamp, channel_alias, relation_count | context only unless corroborated |
| `CYBER_IOC_CONTEXT` | Darkweb Tracker hit on domain/IP/hash/CVE/wallet | indicator_type, indicator_hash, first_seen, last_seen, source_count | useful for SOC-style annex and risk score |
| `SUPPLY_CHAIN_CYBER_RISK` | vendor/contractor domain has exposure or ransomware context | supplier_alias, risk_reason, exposure_count, linked_event_refs | enriches sustainment and logistics storyline |

## Safe Data Handling Rules

- Do not store, export, or demo raw passwords.
- Do not redistribute raw dark web, Telegram, or breach records.
- Do not collect PII that is not required for the hackathon demo.
- Use synthetic domains/entities for public demonstrations whenever possible.
- For real organizations, show only aggregate counts and redacted evidence metadata.
- Treat all StealthMole outputs as leads requiring corroboration, not ground truth.

## Implementation Plan

1. Confirm API documentation:
   - base URL
   - authentication/signing method
   - rate limits
   - enabled modules for the issued license
   - permitted storage/export terms
2. Add a minimal connector:
   - read `.env`
   - test authentication
   - run one harmless query against a synthetic or owned test domain
   - write redacted sample metadata only
3. Normalize output:
   - `source`, `module`, `indicator_type`, `query`, `result_count`, `time_range`, `redacted_evidence_ref`
4. Generate semantic events:
   - aggregate, rank, and cite without exposing sensitive values
5. Attach to COP:
   - show as cyber/context panel next to maritime/weather/AIS events

## Public References Checked

- StealthMole home: `https://www.stealthmole.com/`
- Darkweb Tracker: `https://www.stealthmole.com/products/darkweb-tracker`
- Dark Web Monitoring: `https://www.stealthmole.com/products/dark-web-monitoring`
- Credential Lookout: `https://www.stealthmole.com/products/credential-protection/credential-lookout`
- Compromised Data Set: `https://www.stealthmole.com/products/credential-protection/compromised-data-set`
- Telegram Tracker: `https://www.stealthmole.com/products/telegram-tracker`
- Netskope StealthMole plugin guide: `https://docs.netskope.com/en/stealthmole-v1-0-0-plugin-for-risk-exchange`
- Logpresso StealthMole command reference: `https://logpresso.store/en/apps/stealthmole/commands/stealthmole-tt-search`
- Logpresso StealthMole node reference: `https://logpresso.store/en/apps/stealthmole/commands/stealthmole-tt-node`

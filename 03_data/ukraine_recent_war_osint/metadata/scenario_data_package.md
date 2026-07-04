# Ukraine Recent War Scenario Data Package

- Built: 2026-07-04 KST
- Dataset root: `/Users/mollykim/projects/D4D/03_data/ukraine_recent_war_osint`
- Scenario focus: rail/energy infrastructure strike resilience, missile/UAV saturation, critical infrastructure COP, and degraded-network prioritization.

## MVP Tables

| Table | Rows | Role in scenario |
|---|---:|---|
| `processed/missile_uav_daily_summary_recent.csv` | 90 | Daily pressure signal: how many missiles/UAVs were launched, destroyed, or reported as Shahed-type. |
| `processed/missile_uav_attacks_recent.csv` | 311 | Event-level missile/UAV records for wave grouping and warning prioritization. |
| `processed/osm_ukraine_aoi_critical_infrastructure.csv` | 3,500 | Rail, power, hospital, bridge, and port-like infrastructure around selected AOIs. |
| `processed/gdelt_event_export_ukraine_filtered_recent.csv` | 3,353 | News-derived event stream from the latest 24h GDELT export files. |
| `processed/gdelt_doc_ukraine_scenario_articles.csv` | 250 | Article evidence layer for railway, energy, Shahed, port, and shipping queries. |
| `processed/ucdp_candidate_ged_ukraine_filtered.csv` | 280 | Recent candidate conflict-event records for cross-checking. |
| `processed/ucdp_stable_ged_ukraine_2022plus_filtered.csv` | 38,234 | Stable historical event baseline from 2022 onward. |
| `processed/warspotting_latest_losses.csv` | 200 | Latest visually confirmed equipment-loss records where API access allowed. |
| `processed/petro_russian_equipment_losses_recent.csv` | 214 | Recent daily Russian equipment-loss time series. |
| `processed/petro_russian_personnel_losses_recent.csv` | 214 | Recent daily personnel-loss time series. |
| `processed/open_meteo_aoi_daily_weather_recent.csv` | 1,505 | Weather context for selected AOIs, useful for explaining operational constraints. |
| `processed/isw_recent_russia_ukraine_assessment_links.csv` | 7 | Analyst assessment link index, not full article archive. |
| `processed/oryx_equipment_loss_category_summaries.csv` | 4 | Category-level loss summaries from Oryx pages. |

## How To Use For A Concrete Scenario

1. Pick an AOI such as Kyiv, Kharkiv, Odesa, Dnipro, Zaporizhzhia, Lviv, or Kramatorsk.
2. Load infrastructure from `osm_ukraine_aoi_critical_infrastructure.csv`.
3. Load missile/UAV pressure from `missile_uav_daily_summary_recent.csv` and `missile_uav_attacks_recent.csv`.
4. Add open event evidence from `gdelt_event_export_ukraine_filtered_recent.csv`, `gdelt_doc_ukraine_scenario_articles.csv`, and UCDP.
5. Compute a semantic event:
   - `event_type`: `rail_attack_report`, `energy_outage_report`, `uav_wave_pressure`, `infrastructure_risk`, `maritime_port_disruption`
   - `evidence_refs`: GDELT/ UCDP / source URL / OSM id / missile dataset source
   - `affected_entities`: nearby rail, power, hospital, bridge, or port features
   - `network_priority`: higher when infrastructure criticality, recency, source count, and wave pressure are high
6. Send only the semantic event over degraded network modes; queue raw evidence for store-forward sync.

## API Status

| Source | Why needed | Key/account needed |
|---|---|---|
| ACLED | Best structured event spine for Ukraine/Black Sea and infrastructure tags. | Blocked: provided credentials failed OAuth. Need corrected password or account activation check. |
| NASA FIRMS | Fire/thermal anomaly proxy after missile/UAV waves. | Issued and smoke passed: `NASA_FIRMS_MAP_KEY`. |
| alerts.in.ua | Air raid alert layer and warning duration. | Request submitted 2026-07-04; token email pending: `ALERTS_IN_UA_TOKEN`. |
| Kaggle official package | Official package for `piterfm/massive-missile-attacks-on-ukraine`. | API token issued and smoke passed: `KAGGLE_API_TOKEN`. |
| HDX / ReliefWeb | Humanitarian reports and admin/context datasets. | HDX API token issued and smoke passed. ReliefWeb appname still pending. |

## Safety Notes

- This package is for analysis, resilience planning, and demo scenario generation.
- It does not include raw Telegram/media archives, faces, personal profiles, exact home addresses, or live tactical recommendations.
- GDELT and other news-derived records are not ground truth. Treat them as leads requiring cross-checking.
- OSM infrastructure data is public and broad; do not combine it with live targeting logic.

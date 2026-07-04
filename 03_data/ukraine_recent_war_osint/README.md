# Ukraine Recent War OSINT Dataset

- Built at: 2026-07-04T01:49:20.631045+00:00
- Date window: 2025-12-01 to 2026-07-04
- Scenario focus: rail/energy infrastructure pressure, missile/UAV saturation, Black Sea / port context, and COP/C2 prioritization.
- Safety: no live targeting recommendations, no PII collection, no raw social-media media archive.

## Processed Tables

| File | Rows | Bytes |
|---|---:|---:|
| `gdelt_doc_ukraine_scenario_articles.csv` | 250 | 108091 |
| `gdelt_event_export_ukraine_filtered_recent.csv` | 3353 | 1376894 |
| `isw_recent_russia_ukraine_assessment_links.csv` | 7 | 136055 |
| `missile_uav_attacks_recent.csv` | 311 | 69963 |
| `missile_uav_daily_summary_recent.csv` | 90 | 19359 |
| `open_meteo_aoi_daily_weather_recent.csv` | 1505 | 65691 |
| `oryx_equipment_loss_category_summaries.csv` | 4 | 1197 |
| `osm_ukraine_aoi_critical_infrastructure.csv` | 3500 | 410679 |
| `petro_russian_equipment_losses_recent.csv` | 214 | 17982 |
| `petro_russian_personnel_losses_recent.csv` | 214 | 6665 |
| `ucdp_candidate_ged_ukraine_filtered.csv` | 280 | 199583 |
| `ucdp_stable_ged_ukraine_2022plus_filtered.csv` | 38234 | 28884143 |
| `warspotting_latest_losses.csv` | 200 | 26140 |

## Source Families

- Petro Ivaniuk GitHub: Russian equipment/personnel loss time series.
- Massive Missile Attacks derivative GitHub CSV: missile/UAV launch and interception records.
- UCDP GED/candidate GED: academically maintained organized violence event data.
- GDELT DOC/API and GDELT v2 exports: news-derived article/event layer.
- OpenStreetMap Overpass: selected AOI critical infrastructure basemap.
- WarSpotting: latest visually confirmed loss records where accessible.
- Oryx: category-level equipment loss summaries only, with source URL retained.
- ISW: recent assessment link index, not full copyrighted article archive.
- Open-Meteo: AOI weather context for scenario explanation.

## Key-Required / Blocked Sources

See `raw/blocked_or_key_required/api_placeholders.json`.

Signup and API request methodology:

- `metadata/api_signup_methodology.md`

## Suggested Use

Use `processed/missile_uav_daily_summary_recent.csv`, `processed/osm_ukraine_aoi_critical_infrastructure.csv`, and `processed/gdelt_event_export_ukraine_filtered_recent.csv` as the first MVP data spine. NASA FIRMS, Kaggle API token, and HDX CKAN token are now available and smoke-tested; ACLED remains blocked until the account password or activation status is corrected.

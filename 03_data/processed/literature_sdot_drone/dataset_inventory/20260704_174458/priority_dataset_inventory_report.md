# S-DOT Drone Priority Dataset Inventory

- Run ID: `20260704_174458`
- Checked at: `2026-07-04T08:45:04.535547+00:00`
- Sources inspected: 3
- Passed: 3
- Failed: 0
- Scope: metadata, file inventory, and dataset descriptions only; no raw source data downloaded.

## Summary

| Dataset | Status | Size | Files | Role | Next Action |
|---|---|---:|---:|---|---|
| `yunnan_gnss_interference_spoofing` | passed | 8.58 GB | 216 | best_gnss_feature_range_candidate | Use API metadata and selected small zip only after choosing a specific feature table; avoid bulk download. |
| `aerpaw_dataset_12` | passed | 140.48 GB | 4 | best_link_health_feature_range_candidate | Use README/API metadata now. Only ingest GPS/RSS metadata if a small subset can be isolated; do not bulk download 150GB archive. |
| `zenodo_gnss_jamming_spoofing_meaconing_2025` | passed | 4.96 KB | 1 | small_readme_and_taxonomy_reference | Ingest README/taxonomy only unless external raw-resource access is explicitly needed. |

## Details

### yunnan_gnss_interference_spoofing

- Title: GNSS Dataset (with Interference and Spoofing) Part I
- Source: https://data.mendeley.com/datasets/ccdgjcfvn5/1
- DOI/license: 10.17632/ccdgjcfvn5.1 / CC BY 4.0
- S-DOT use: GNSS C/N0, DOP, Doppler, pseudorange, position feature-range calibration; clean/jamming/spoofing receiver-state class reference
- Caveat: Static receiver dataset; not a moving drone trajectory. Do not reuse offensive spoofing/jamming setup details.
- Feature terms found: C/N0, DOP, Doppler, pseudorange, carrier phase, GPS, GNSS, jamming, spoofing

Sample files:

- `0.zip` (40.65 MB)
- `0.zip` (41.03 MB)
- `0.zip` (41.14 MB)
- `0.zip` (40.65 MB)
- `0.zip` (41.79 MB)
- `0.zip` (42.09 MB)
- `0.zip` (41.07 MB)
- `0.zip` (40.02 MB)

### aerpaw_dataset_12

- Title: AERPAW Dataset-12: Rural air-to-ground channel measurements at 3.3 GHz
- Source: https://aerpaw.org/dataset/uav-based-signal-data-collected-at-varying-altitudes-and-sampling-rates-for-wireless-communication-studies/
- DOI/license: doi:10.5061/dryad.2z34tmpvv / https://spdx.org/licenses/CC0-1.0.html
- S-DOT use: UAV RSS/link-health feature-range calibration; GPS/RSS timestamp alignment and bearer-health model reference
- Caveat: Large 150GB+ IQ archive; use metadata and README first, not bulk download.
- Feature terms found: GPS, RSS, SigMF, IQ, trajectory, altitude, sampling rate

Sample files:

- `README.md` (4.36 KB)
- `UAV-Based_Signal_Data_Collected_at_Varying_Altitudes_and_Sampling_Rates_for_Wireless_Communication_Studies.zip` (150.84 GB)
- `README.md` (3.96 KB)
- `UAV-Based_Signal_Data_Collected_at_Varying_Altitudes_and_Sampling_Rates_for_Wireless_Communication_Studies.zip` (150.84 GB)

### zenodo_gnss_jamming_spoofing_meaconing_2025

- Title: GNSS Dataset Under Jamming, Spoofing, and Meaconing Conditions
- Source: https://zenodo.org/records/15911359
- DOI/license: 10.5281/zenodo.15911359 / gpl-3.0-or-later
- S-DOT use: GNSS attack-condition taxonomy; UBX/RINEX/RF-monitoring/navigation-solution schema reference
- Caveat: Record currently exposes a small README through Zenodo; external/raw resources should be checked manually before use.
- Feature terms found: GNSS, jamming, spoofing, meaconing, IQ

Sample files:

- `README.md` (4.96 KB)

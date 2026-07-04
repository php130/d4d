# S-DOT Drone Priority Dataset Inventory

- Run ID: `20260704_174645`
- Checked at: `2026-07-04T08:46:50.110461+00:00`
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
- Download policy: Optional small single-zip inspection only after selecting a concrete feature table. Never bulk-download the full 8.58GB during demo prep.
- Feature terms found: C/N0, DOP, Doppler, pseudorange, carrier phase, GPS, GNSS, jamming, spoofing
- Candidate S-DOT fields: cn0_dbhz_mean, doppler_shift_proxy, pseudorange_residual_proxy, carrier_phase_quality_proxy, hdop, vdop, receiver_position_error_proxy, gnss_condition_label

Structure notes:

- Dataset is split into raw clean-data parts and a processed/attack-condition part.
- Public description identifies normal, jamming-affected, and spoofing-affected receiver scenarios.
- Description references five constellations and multiple signal bands; treat as receiver-feature calibration, not drone trajectory truth.

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
- Download policy: Use Dryad API/methods text and README-level metadata first. Avoid 150GB archive unless a small subset can be isolated.
- Feature terms found: GPS, RSS, SigMF, IQ, trajectory, altitude, sampling rate
- Candidate S-DOT fields: rss_dbm, rss1_dbm, rss2_dbm, snr_bucket, gps_x, gps_y, gps_z, interpolated_mx, interpolated_my, interpolated_mz, altitude_m, sampling_rate_hz

Structure notes:

- UAV follows repeated trajectories at 40m, 70m, and 100m altitude.
- 40m runs include 5MHz, 10MHz, and 20MHz sampling rates.
- GPS coordinates are 1Hz; radio measurements are timestamped separately and aligned by interpolation.
- Data uses SigMF metadata/data files and includes RSS measurements from fixed nodes LW1-LW5.
- Dryad page exposes multiple file blocks; use the current Dryad API record as the authoritative dataset metadata.

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
- Download policy: Safe to use README/taxonomy. Do not assume raw scenario files are locally available from the Zenodo record.
- Feature terms found: GNSS, jamming, spoofing, meaconing, IQ
- Candidate S-DOT fields: attack_condition_label, receiver_mobility_label, mon_rf_quality_proxy, nav_pvt_position_proxy, rinex_observation_ref, scenario_metadata_ref

Structure notes:

- Zenodo record exposes a small README through the record API.
- README describes scenario-level metadata and GNSS monitoring/navigation files such as scenario metadata, RF monitoring, PVT, RINEX, and UBX-style raw receiver data.
- Use as taxonomy/schema reference unless raw-resource access is separately validated.

Sample files:

- `README.md` (4.96 KB)

# S-DOT Drone Dataset Candidate Smoke Test

- Run ID: `20260704_173915`
- Checked at: `2026-07-04T08:39:38.836454+00:00`
- Candidate datasets: 14
- Passed: 13
- Partial: 0
- Failed: 1

## Results

| Dataset | Class | Status | URL Checks | Next Action |
|---|---|---|---:|---|
| `texbat` | candidate_validation | passed | 1/1 | Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined. |
| `oakbat_gps` | candidate_validation | passed | 1/1 | Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined. |
| `fgi_jsdr` | candidate_validation | passed | 2/2 | Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined. |
| `yunnan_gnss_interference_spoofing` | candidate_validation | passed | 1/1 | Best first smoke-test target for v0.7 GNSS feature ranges; inspect file sizes before downloading. |
| `zenodo_gnss_jamming_spoofing_meaconing_2025` | candidate_validation | passed | 2/2 | Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined. |
| `dronerf_mendeley` | reference_only | passed | 1/1 | Keep as reference-only citation/design input for now. |
| `aerpaw_dataset_12` | candidate_validation | passed | 1/1 | Best first smoke-test target for RSS/GPS link-health feature ranges; inspect Dryad file list before downloading. |
| `aerpaw_dataset_28` | reference_only | passed | 1/1 | Keep as reference-only citation/design input for now. |
| `aerpaw_drone_rc_rf` | reference_only | passed | 1/1 | Keep as reference-only citation/design input for now. |
| `deepsense_6g_scenario_23` | candidate_validation | passed | 2/2 | Keep as a validation candidate; ingest only small samples after a concrete feature-calibration task is defined. |
| `ku_leuven_drone_rf` | reference_only | passed | 1/1 | Keep as reference-only citation/design input for now. |
| `maritime_gnss_antarctica` | reference_only | passed | 2/2 | Keep as reference-only citation/design input for now. |
| `uav_lora_avalanche` | reference_only | failed | 0/1 | Retry manually or look for an alternate mirror/API before relying on this source. |
| `uav_a2g_path_loss_mendeley` | reference_only | passed | 1/1 | Keep as reference-only citation/design input for now. |

## Notes

- Samples are capped at 200KB and are page/API metadata only.
- No large RF/IQ/UBX/RINEX datasets were downloaded.
- Public data can calibrate feature ranges, but the end-to-end S-DOT mission timeline remains synthetic.

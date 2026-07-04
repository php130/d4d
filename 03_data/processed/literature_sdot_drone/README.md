# S-DOT Drone Literature Metadata

This folder stores literature metadata for the revised S-DOT drone semantic transmission direction.

## Scope

Topics:

- semantic communications for UAV / edge
- UAV GNSS-denied navigation
- GNSS jamming / spoofing detection and integrity
- Kalman residual / NIS / integrity monitoring
- UAV networks, DDIL, DTN, intermittent links
- resilient UAV communications under jamming
- edge AI / compression / video semantic transmission
- UAV sensor fusion and tracking
- UAV simulation / digital twin
- provenance, trust, C2, decision support

## Current Run

- Version: `20260704_164224`
- Raw records: 1,771
- Deduped records: 1,343
- OpenAlex records: 1,173
- arXiv records: 170

## Snowball Run

- Version: `snowball_20260704_165653`
- Seed papers: 120
- Candidate OpenAlex work IDs: 500
- Successfully fetched: 446
- New records after dedupe against base: 446
- Merged record count: 1,789
- Failure count: 54, mostly stale/deleted OpenAlex IDs returning 404

## arXiv Retry

- Version: `arxiv_retry_20260704_170558`
- Raw arXiv records: 216
- New records after dedupe against base+snowball: 111
- Failures: 0

## Final Combined Corpus

- Version: `final_20260704_170558`
- Total records: 1,900
- OpenAlex records: 1,619
- arXiv records: 281
- Path: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/final_20260704_170558/sdot_drone_literature_records_final.json`

## Priority Source Access Dataset

- Version: `priority_source_access_20260704`
- Sources: 14
- Path: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/priority_source_access_20260704.json`
- Pointer: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/latest_priority_source_access.json`

## GNSS / RF / Link Dataset Candidates

- Version: `gnss_rf_link_dataset_candidates_20260704`
- Candidate datasets: 14
- Synthetic-required categories: 5
- Path: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/gnss_rf_link_dataset_candidates_20260704.json`
- Pointer: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/latest_gnss_rf_link_dataset_candidates.json`
- Human-readable catalog: `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_gnss_rf_link_dataset_catalog_20260704.md`

## Dataset Candidate Smoke Test

- Version: `dataset_smoke_test_20260704_173915`
- Candidate datasets checked: 14
- Passed: 13
- Failed: 1 (`uav_lora_avalanche`, ScienceDirect HTTP 403)
- Scope: metadata/page/API accessibility only; no large RF/IQ/UBX/RINEX datasets downloaded
- Report: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/dataset_smoke_tests/20260704_173915/dataset_smoke_test_report.json`
- Markdown: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/dataset_smoke_tests/20260704_173915/dataset_smoke_test_report.md`
- Pointer: `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/latest_dataset_smoke_test.json`

## Files

Current run directory:

- `/Users/mollykim/projects/D4D/03_data/processed/literature_sdot_drone/20260704_164224`

Key outputs:

- `sdot_drone_literature_records.json`
- `sdot_drone_literature_records.csv`
- `sdot_drone_topic_summary.json`
- `manifest.json`

Pointer:

- `latest.json`
- `latest_snowball.json`
- `latest_arxiv_retry.json`
- `latest_final.json`
- `latest_dataset_smoke_test.json`
- `VERSIONS.md`

## Notes

The collection stores metadata only. It does not download or redistribute full papers.

arXiv rate-limited the first run after early topics. OpenAlex completed successfully, and the slower arXiv retry later completed without failures.

Primary analysis outputs:

- `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_literature_synthesis_20260704.md`
- `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_algorithm_evidence_matrix_20260704.md`
- `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_top_paper_extraction_notes_20260704.md`
- `/Users/mollykim/projects/D4D/01_research/literature/sdot_drone_research/sdot_drone_priority_source_access_and_algorithm_notes_20260704.md`
- `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_public_dataset_simulator_catalog_20260704.md`
- `/Users/mollykim/projects/D4D/03_data/reference/sdot_drone_gnss_rf_link_dataset_catalog_20260704.md`
- `/Users/mollykim/projects/D4D/06_prototype/docs/s_dot_drone_v0_7_algorithm_and_data_requirements_20260704.md`

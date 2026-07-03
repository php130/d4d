# Resilient Maritime COP Mock Dataset

- Dataset ID: `resilient_maritime_cop_mock_v0_1`
- Generated: 2026-07-03T15:22:46.749610+00:00
- Scenario: A cooperative AIS track goes stale, an independent SAR-like detection appears nearby, weather reduces confirmation options, and the network drops into semantic-summary mode.

## Safety

All values are synthetic. Vessel identifiers are masked-style placeholders. The data is meant to demonstrate architecture and routing behavior, not to make real maritime claims.

## Why This Dataset Exists

The live API collection workstream may produce real snapshots later. Until then, this dataset keeps the demo runnable and reproducible.

Each mock source states which real source type it can be replaced by:

- AIS-like tracks -> data.go.kr maritime AIS, Global Fishing Watch, NOAA AIS
- SAR-like detections -> Copernicus Sentinel-1, xView3, Global Fishing Watch SAR detections
- weather hazard -> KMA APIHub, Copernicus Marine, NOAA/NCEP
- OSINT incident -> GDELT and official advisories
- network state -> Cloudflare Radar, Ookla, RIPE Atlas, synthetic netem

## Files

- `mock_dataset.json`: full dataset used by the demo app
- app copy: `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.json`

## Key Demonstration

The same set of events is routed differently under each network mode:

- `full_sync`: all event details can move
- `delta_sync`: compact event deltas move
- `semantic_summary`: only high-priority alert cards survive
- `store_forward`: almost everything queues
- `local_only`: no remote transmission

This shows the T3 point: the project is not just maritime sensing; it is mission-aware communication under constrained links.

# S-DOT Seoul Ground Mission Continuity COP Mock Dataset

- Dataset ID: `s_dot_seoul_ground_mission_continuity_mock_v0_5`
- Generated: 2026-07-04T05:59:39.370299+00:00
- Scenario: 12-1 becomes intermittently connected in a Seoul urban ground scenario while command staff monitor synthetic opposing route branches, public civil context, support resources, and candidate bearers through S-DOT semantic packets.

## Safety

The base map and civil infrastructure context are public/open-source style Seoul context. Unit state, support resources, tactical network values, readiness, and allocation decisions are synthetic. The data is meant to demonstrate S-DOT architecture and routing behavior, not to disclose real force disposition, real readiness, protected-facility coordinates, or operational claims.

## Why This Dataset Exists

The live API collection workstream may produce real snapshots later. Until then, this dataset keeps the demo runnable and reproducible.

Each mock source states which real source type it can be replaced by:

- unit/readiness state -> redacted exercise telemetry or training data only
- civil/public comms assets -> KCA public radio-station data, Spectrum Map, PS-LTE/LTE-M/LTE-R references, or telco-provided emergency inventory
- support resources -> public facility context plus synthetic military support resources
- Seoul map/buildings -> OpenStreetMap building footprints, VWorld/MOLIT public map context
- public medical context -> HIRA/NMC public facility APIs
- aggregate public IT/power context -> MOIS/KPX aggregate public datasets
- weather hazard -> KMA APIHub, Open-Meteo, data.go.kr weather
- OSINT incident -> GDELT, official advisories, public emergency notices
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

This shows the T3 point: the project is not just a COP. It is mission-aware semantic transmission under constrained links.

## S-DOT Additions

- `mission_intent`: structured commander/staff intent and priority weights
- `unit_nodes`: synthetic isolated/intermittent units with confirmed vs predicted state
- `unit_nodes[].branch_scenarios`: probabilistic branch scenarios instead of exact tracking claims
- `pace_bearer_ladder`: Network/Bearer/PACE state that drives payload priority and C2 mode
- `civil_comms_assets`: candidate bearers with legal, power, backhaul, auth, and priority status
- `korea_civil_infra_context`: safe Korea civil infrastructure COP layer, imported only as protected/support context
- `urban_routes`: synthetic support routes over public Seoul map context
- `support_options`: ranked medical, power, and comms support options
- `sdot_messages`: semantic command/status/support packets with raw-vs-semantic bytes
- `rejoin_audit`: expected sync order and prediction-review questions

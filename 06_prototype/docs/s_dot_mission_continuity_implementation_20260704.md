# S-DOT Mission Continuity COP Implementation Note

- Date: 2026-07-04 KST
- Prototype path: `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop`
- Public deployment: `d4d-cop-public`
- Public URL: `https://anti-plug-cheapest-hoped.trycloudflare.com`

## Decision

Real unit/resource placement data should not be used for the hackathon prototype. Public fragments may exist for bases, organizations, infrastructure, weather, maps, and policy, but real force disposition, readiness, support-resource location, tactical network state, and allocation priorities are either non-public, operationally sensitive, or unsuitable for a public demo.

The demo therefore uses:

- public/open data patterns for context and evidence structure
- synthetic unit state
- synthetic support resources
- synthetic civil/public bearer candidates
- synthetic DDIL network modes
- synthetic S-DOT command/status/support messages

## Implemented In V0.2

Dataset generator:

- `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_resilient_maritime_cop_mock_dataset.py`

Generated artifacts:

- `/Users/mollykim/projects/D4D/03_data/samples/resilient_maritime_cop/mock_dataset.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.js`

Dataset additions:

- `mission_intent`
- `unit_nodes`
- `civil_comms_assets`
- `support_options`
- `sdot_messages`
- `rejoin_audit`

UI additions:

- central map overlays for confirmed unit position, predicted unit position, uncertainty radius, bearer candidates, and support options
- mission intent panel
- unit continuity panel
- support routing panel
- S-DOT message queue panel
- glossary entries for S-DOT, mission intent, predicted COP, support option, and civil comms asset

## Implemented In V0.3

User-facing refinements:

- Korean-first command-board labels for hackathon reviewers
- S-DOT name caveat: `S-DOT = Semantic Data On Tactical-network`, a hackathon concept label, not an existing standard
- framing changed from "HQ keeps tracking/commanding" to "intent, minimum COP, resource state, uncertainty, and rejoin audit continue"

Dataset additions:

- dataset id: `s_dot_mission_continuity_mock_v0_3`
- `pace_bearer_ladder`: Network/Bearer/PACE state as an explicit fourth plane
- `unit_nodes[].branch_scenarios`: probabilistic branches instead of exact tracking claims
- `korea_civil_infra_context`: safe Korea civil infrastructure COP inset layer imported from the other demo

UI additions:

- Korea civil infrastructure COP inset on the central map
- PACE/Bearer ladder panel
- branch scenario display under each synthetic unit
- Korean event labels, evidence copy, routing labels, mission panels, and briefing copy

Feedback modules now represented:

- C2 Mode Manager: network/DDIL mode selector plus unit C2 mode
- Confirmed vs Predicted: last confirmed vs predicted marker and uncertainty radius
- Intent Card: mission intent panel
- PACE/Bearer Ladder: explicit network/bearer panel
- Resource Option Ranking: support options panel
- S-DOT Packet Inspector: raw vs semantic transmission panel plus S-DOT queue
- Rejoin Audit: rejoin audit card and expected sync order

## Implemented In V0.4

User direction changed from maritime/coastal exploration to Seoul urban-ground exploration.

Dataset changes:

- dataset id: `s_dot_seoul_ground_mission_continuity_mock_v0_4`
- AOI: `서울 도심 지상 AOI`
- removed maritime tracks/vessels from the active generated dataset
- added `urban_routes` for synthetic support-route display
- renamed the isolated synthetic unit from the old maritime scenario to `Alpha-1`
- retained public Seoul civil infrastructure context as protected/support context

Map changes:

- removed the synthetic coastal SVG map from the active UI
- replaced the main map with Leaflet + OpenStreetMap tiles
- added local Seoul building-footprint overlay copied from the Korea civil infra COP demo
- overlaid synthetic units, branch uncertainty radius, support options, route lines, candidate bearers, public hospitals, communication aggregates, and semantic events on the Seoul map

Safety boundary:

- OpenStreetMap/building/public medical layers are public context.
- Unit, readiness, support, network, route ranking, and resource-allocation data remain synthetic.
- Communications and power/public IT layers stay coarse/aggregate; no base-station, backbone, protected-facility, or real military coordinates are included.

## Implemented In V0.5

User direction changed from a generic Seoul ground map to a command-room scenario board.

Dataset changes:

- dataset id: `s_dot_seoul_ground_mission_continuity_mock_v0_5`
- added `operation_objective`: Korean-first current objective, end state, phase, decision focus, and protected priorities
- added `adversary_assessment`: three synthetic opposing movement candidate axes, with likelihood/confidence and explicit safety note
- added `evt_opposing_axis_watch` and `obs_opposing_axis_a` to show the watch-axis hypothesis as an evidence-backed semantic event
- expanded synthetic unit layer to `12-1`, `12-2`, and `12-3`
- kept all unit locations, readiness, support assignments, route branches, and opposing-axis assumptions synthetic

UI changes:

- added a top objective banner so command staff immediately see the current operation goal
- map command strip now emphasizes operation phase, top watch axis, link state, and routing decision
- opposing candidate axes render as animated dashed routes on the Seoul map
- unit markers render short unit codes (`12-1`, `12-2`, `12-3`) instead of verbose map labels
- unit communication state is shown by marker color and pulse animation instead of text on the map
- support options use compact symbols and remain ranked options, not automatic dispatch orders

Safety boundary:

- The opposing route layer is a scenario hypothesis for UI/S-DOT prioritization only.
- It is not real intelligence, a targeting layer, or tactical guidance.
- The demo still uses public Seoul context plus synthetic force/resource/network layers.

## Current Synthetic Scenario

`12-1` is intermittently connected in a synthetic Seoul urban-ground scenario. Command staff must preserve the operation objective, monitor synthetic opposing route hypotheses, protect public/civil context, rank support options, and send only the most valuable S-DOT packets while the tactical link is degraded.

The system demonstrates:

- which S-DOT messages survive under each network mode
- how much payload is saved versus raw data movement
- what the command room can infer while a unit is isolated
- which support options are ranked for medical, relay, and power needs
- how candidate opposing movement is shown as probability branches rather than confirmed tracking
- how rejoin/sync priority is handled when connectivity returns

## Verification

Passed:

- `python3 06_prototype/scripts/generate_resilient_maritime_cop_mock_dataset.py`
- `python3 -m json.tool 06_prototype/app/resilient_maritime_cop/data/mock_dataset.json`
- `node --check 06_prototype/app/resilient_maritime_cop/assets/app.js`
- `node --check 06_prototype/app/resilient_maritime_cop/assets/glossary.js`
- data consistency check: all `sdot_messages[].event_id` values map to existing `semantic_events[].event_id`
- v0.3 field check: 4 PACE bearers, 3 branch scenarios, 6 hospital context nodes, 3 communications aggregate cells, 4 civil infra semantic events
- v0.4 field check: Seoul AOI, 0 vessels, 0 maritime tracks, 2 synthetic urban units, 2 synthetic support routes, 4 PACE bearers, 3 Alpha-1 branch scenarios, 3200 OSM building footprints available to the app
- v0.5 field check: 1 operation objective, 3 synthetic opposing candidate axes, 3 synthetic unit nodes, 3 synthetic support routes, 12 semantic events, 12 observations
- `local-deployer list`: `d4d-cop-public` running on port `3006`
- public URL static check: `s_dot_seoul_ground_mission_continuity_mock_v0_5` served with objective `서울 도심 임무지속 방호`
- `/healthz`: `ok`

Not completed:

- In-app browser visual verification was blocked by Codex browser security policy for both `127.0.0.1:3006` and the current Cloudflare tunnel. The app should be visually rechecked from a normal user browser before presentation.

## Next Build Slice

1. Add mode-switch interaction tests from a normal browser.
2. Add a S-DOT packet schema validator.
3. Add a CSV/JSON export bundle for possible Palantir Foundry/AIP import.
4. Add a small route-cost simulator for support options.
5. Keep all force/resource layers synthetic unless the organizer explicitly provides approved exercise data.

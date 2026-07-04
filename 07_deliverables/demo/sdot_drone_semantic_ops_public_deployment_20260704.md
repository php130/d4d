# S-DOT Drone Semantic Ops Public Deployment

- Date: 2026-07-04 KST
- Deployment name: `d4d-sdot-drone`
- Local app path: `/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops`
- Local port: `3008`
- Active public URL: https://bench-coverage-saving-membrane.trycloudflare.com

## Product Scope

This is the v0.6 drone-first S-DOT demo.

It reframes the project from a ground-unit COP into:

> A drone semantic transmission and navigation-integrity demo for GNSS/link degradation, suspected jamming, uncertainty-aware prediction, and raw-vs-semantic packet routing.

## What Is Deployed

- Three.js 3D drone simulation
- 5 scenario cases:
  - normal mission
  - link degradation
  - GNSS jamming suspected
  - spoofing-like inconsistency
  - rejoin audit
- 3 synthetic assets:
  - `UAV-S1`
  - `UGV-R1`
  - `RF-S3`
- v0.6 dataset:
  - `s_dot_drone_semantic_ops_mock_v0_6`
- semantic events:
  - `STATUS_SUMMARY`
  - `LINK_DEGRADED`
  - `GNSS_DEGRADED`
  - `JAMMING_SUSPECTED`
  - `SPOOFING_SUSPECTED`
  - `REJOIN_AUDIT_REQUIRED`
- case-specific event filtering:
  - each scenario shows only the semantic events and packets relevant to that case
  - normal mission stays quiet except for baseline status summary
  - GNSS degradation and spoofing-like cases expose separate evidence chains
- packet inspector:
  - raw feed bytes
  - semantic bytes sent
  - send/defer/hold decisions by DDIL mode
- evidence/provenance panel
- predicted vs reported state panel
- Kalman-style estimator comparison:
  - innovation NIS
  - gate threshold
  - measurement sigma
  - 2-sigma position uncertainty
  - reported-position error vs Kalman-estimate error
  - accepted/rejected measurement decision
- algorithm evaluation panel:
  - max residual
  - max NIS
  - NIS watch/critical threshold
  - detection latency
  - false alarm risk
  - confidence
  - operator decision and semantic transmission policy
  - normalized trend chart for residual, NIS, uncertainty, and hypothesis score
- NIS/residual and defensive jamming/spoofing hypothesis score display
- scenario selection jumps to the first degraded/watch/critical point so judges see the relevant phase immediately
- Korean-first UI copy for case summaries, asset labels, evidence cards, and packet tiers
- Palantir/AIP handoff bundle:
  - output path: `/Users/mollykim/projects/D4D/07_deliverables/palantir/sdot_drone_semantic_ops`
  - 12 object CSV tables
  - 225 relationship links
  - 4 action definitions
  - 3 AIP workflow cards
- Foundry/AIP handoff panel in the public UI:
  - object/link/action/workflow-card summary
  - ontology candidate object list
  - action candidate list
  - guardrail note that this is a safe handoff bundle, not an official Palantir import spec

## Important URL Note

`local-deployer` initially printed:

- `https://interim-nursing-preserve-parties.trycloudflare.com`

That URL returned Cloudflare 1033 because the tunnel process was not present in PM2.

The active manually started tunnel is:

- https://bench-coverage-saving-membrane.trycloudflare.com

PM2 process:

- `ld-d4d-sdot-drone`
- `ld-d4d-sdot-drone-tunnel`

## Verification

Passed:

- `node --check assets/app.js`
- `node --check server.js`
- `node --check data/mock_dataset.js`
- `python3 -m json.tool data/mock_dataset.json`
- local health check: `http://127.0.0.1:3008/healthz` -> `ok`
- public HTML check contains `S-DOT Edge Semantic Ops`
- public dataset check:
  - `metadata.dataset_id`: `s_dot_drone_semantic_ops_mock_v0_6`
  - cases: `5`
  - `drone_assets`: `3`
  - events: `6`
  - packets: `6`
  - `algorithm_basis`: `6`
  - `case_evaluations`: `5`
  - `case_evaluation_series`: `5` cases x `13` points
  - `kalman_estimator_traces`: `5` cases x `13` points
  - case event counts:
    - normal mission: `1`
    - link degradation: `1`
    - GNSS jamming suspected: `3`
    - spoofing-like inconsistency: `2`
    - rejoin audit: `1`
- Playwright desktop/mobile visual checks against local server:
  - canvas nonblank
  - no page errors
  - screenshots saved in `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks`
- Playwright public desktop visual check:
  - canvas nonblank
  - no page errors
- Playwright public case-switch check:
  - all 5 cases selectable
  - selected case filters semantic events and packets correctly
  - selected case changes default DDIL mode correctly
  - algorithm evaluation panel renders Korean labels and case-specific values
  - trend chart renders 4 polylines and current-time marker advances
  - GNSS degradation case jumps to first anomaly point
  - Kalman comparison panel renders gate rejection for GNSS degraded first anomaly
  - no page errors
- Playwright public handoff panel check:
  - public page title: `S-DOT 드론 시맨틱 전송 데모`
  - WebGL canvas renders
  - algorithm/Kalman evaluation panel renders
  - Foundry/AIP handoff panel renders
  - object table count: `12`
  - relationship link count: `225`
  - action and workflow-card summary renders
  - non-official import-spec guardrail text renders
- Palantir/AIP handoff validation:
  - export script compiles and runs
  - object files: `12`
  - relationship links: `225`
  - missing link references: `0`

## Visual Check Artifacts

- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_desktop.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_mobile.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_public_desktop.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_case_filtered_public.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_evaluation_public.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_korean_evaluation_public.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_trend_chart_public.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_kalman_public.png`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/visual_checks/sdot_drone_handoff_public.png`

## Safety Boundary

All drone, GNSS, link, jamming-hypothesis, and route data is synthetic.

The demo does not include:

- real drone tasking routes
- real military unit positions
- real EW emitter details
- sensitive infrastructure coordinates
- offensive jamming guidance

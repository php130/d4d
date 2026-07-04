# Drone Production Conversion Public Deployment

- Date: 2026-07-04 KST
- Deployment name: `d4d-drone-production-conversion`
- Local app path: `/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion`
- Local-deployer port: `3009`
- Active public URL: https://fair-extreme-gmbh-humanities.trycloudflare.com
- Public full candidate capacity CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/full_factory_candidate_capacity_backdata.csv
- Public dynamic pipeline shortlist CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/factory_pipeline_candidate_shortlist.csv
- Public capacity CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/factory_capacity_backdata.csv
- Public route/capacity CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/factory_route_capacity_edges.csv
- Public consolidated logistics route CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/logistics_route_edges.csv
- Public raw-material supply CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/material_supply_backdata.csv
- Public material import-route CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/material_import_routes.csv
- Public allied supply-source CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/allied_supply_sources.csv
- Public component survival CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/component_survival_backdata.csv
- Public subcomponent constraints CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/subcomponent_constraints.csv
- Public blockade phase-curve CSV: https://fair-extreme-gmbh-humanities.trycloudflare.com/data/blockade_phase_curve.csv

## What Is Deployed

The deployed app is the v0.8 D4D drone production-conversion demo.

Visible scope:

- Map-first satellite Korea decision canvas with compact header and floating controls.
- 180 map-visible factory candidates across 8 high-level drone part families.
- Full-pool supplier selection across 29,645 capacity-profiled factory candidates; the map layer includes every selected supplier and resource-target factory.
- 32 critical-resource candidate nodes across rare-earth/magnet, battery material, urban-mining/e-waste metals, and composite/light-metal feedstock categories.
- 6 raw-material categories tied to the drone use/BOM model: magnet feedstock, battery/lithium feedstock, copper/PCB/connector feedstock, composite/light-metal feedstock, optical sensor components, and polymers/packaging.
- 12 component-level blockade survival items and 9 subcomponent constraints for chip/magnet/sensor bottleneck analysis.
- 4 import-port nodes and 6 overseas material source nodes for a coarse East Sea/Japan import-corridor demo.
- 6 allied/partner supply-source hypotheses linking Australia, Canada, Taiwan, the United States, and Japan to material/component categories and Japan-side staging nodes.
- Japan-Korea maritime lines use source-specific coastal waypoints in v0.8 so Nagoya/Yokohama/Kobe routes do not draw across Japanese land.
- 3 synthetic assembly hubs: Pyeongtaek, Daejeon, Daegu.
- Default/Scenario view modes: Default keeps the left/right operation cards, while Scenario switches to a bottom carousel and hides the side cards for presentation.
- Three scenario models are exposed in the header. Scenario 2 now expands into a six-step factory-strike recovery story, from `2-1` strike alert through `2-6` frozen-order/in-transit review, and playback advances at the stage level.
- Scenario stage focus now drives the map: factory IDs, route IDs, material IDs, threat paths, and trade/material routes are used to zoom and highlight the relevant supply-change area.
- Factory-to-assembly and resource-to-factory route lines with animated flow dots.
- Maritime import route and port-to-factory material route layers, controlled from the Layers drawer.
- Road-network route distance, duration, route geometry, road-step summary, fuel-per-trip, driver-hour, and estimated trip-cost fields.
- Factory capacity profiles using public employee count, manufacturing/building/land area, industry/product fit, direct NGMS matches where available, and regional industrial electricity proxies otherwise.
- Collapsible map summary chip for target, feasible volume, and shortfall.
- Layers/filters drawer that is closed by default and opens over the map.
- Dataset drawer for source status, BOM bottleneck, active flow ledger, raw-material/import-route summary, allied supply-source summary, blockade survival, and critical-material feeder summary.
- Left/right decision-card detail buttons now open contextual dark glass side sheets instead of the reserved central report modal.
- Detail sheets use compact metrics, route cards, expandable route notes, and map-linked hover/focus highlighting for related factories and routes.
- Map toolbar includes an `전체 공장 / 활성화 공장` scope toggle. Current baseline shows 180 demo candidate factories or 50 active pipeline-linked factories.
- Map toolbar includes a `범례` panel that defines node shapes and edge colors: convergence factories, resource nodes, import ports, threat-affected nodes, maritime/raw-material/resource/part/threat/fallback routes.
- Convergence factories are ring-highlighted, threat-affected factories become partially transparent, and high-risk factories render dotted fallback arrows toward alternate candidate factories.
- Factory node click now opens the left contextual factory sheet, keeps the selected factory and connected routes in focus, enlarges convergence/assembly nodes above normal part factories, and reduces distant node/route glow so the satellite map stays readable.
- Selected-node drawer remains suppressed for the map-first flow; node clicks use contextual dark operation sheets instead of the large white drawer.
- Factory detail drawer includes raw-material inbound legs from import ports where present.
- Safety boundary in the layers drawer that treats all rows as candidate triage records, not verified mobilization or extraction capacity.

## Process Layout

| Process | Role |
| --- | --- |
| `ld-d4d-drone-production-conversion` | Node static server managed by local-deployer/pm2 |
| `ld-d4d-drone-production-conversion-tunnel` | Manually started Cloudflare quick tunnel managed by pm2 |

## Verification

```bash
curl -I -L https://fair-extreme-gmbh-humanities.trycloudflare.com
curl https://fair-extreme-gmbh-humanities.trycloudflare.com/healthz
curl https://fair-extreme-gmbh-humanities.trycloudflare.com/data/drone_production_conversion_dataset.json
```

Verified:

- public HTML returns HTTP 200
- public `/healthz` returns `ok`
- public title is `D4D Drone Production Conversion`
- dataset schema is `d4d.drone_production_conversion.v0.8`
- map-visible factory candidates: `180`
- demo critical-resource candidates: `32`
- rich capacity source rows parsed: `198,235`
- full factory candidate pool rows: `29,645`
- dynamic pipeline shortlist rows: `8,916`
- factory capacity backdata CSV rows: `180`
- factory route/capacity edge CSV rows: `126`
- rare-earth/magnet full-CSV candidate rows: `109`
- battery material full-CSV candidate rows: `1,356`
- urban-mining/e-waste metals full-CSV candidate rows: `1,166`
- composite/light-metal full-CSV candidate rows: `2,520`
- total part-to-assembly route segments: `126`
- total resource-to-factory routes: `26`
- total maritime import route segments: `18`
- total port-to-factory material routes: `71`
- allied/partner supply-source hypotheses: `6`
- Nagoya -> Ulsan public demo sea route: `8` geometry points, `coastal_waypoint_corridor_v0.2`, `528.7 nm`
- Yokohama -> Pohang public demo sea route: `9` geometry points, `coastal_waypoint_corridor_v0.2`, `685.0 nm`
- active routed/estimated road segments including material feeder legs: `223`
- OSRM-routed road segments with road summary: `223`
- consolidated logistics route CSV rows: `241`
- raw-material categories: `6`
- component survival items: `12`
- subcomponent constraints: `9`
- blockade phase curve rows: `18`
- allied supply-source CSV rows: `6`
- component survival CSV rows: `36`
- subcomponent constraints CSV rows: `27`
- blockade phase curve CSV rows: `18`
- drone use/BOM mission profiles: `3`
- import ports: `4`
- overseas material source nodes: `6`
- unique cached OD routes: `111`
- route provider for active dataset: `OSRM public demo server`
- NGMS emissions/energy records parsed: `777`
- direct factory energy matches: `15`
- direct resource energy matches: `1`
- regional energy/electricity context year: `2024`
- `assets/app.js` and `server.js` pass `node --check`
- dataset JSON passes `python3 -m json.tool`
- static JS and public JSON/CSV checks passed for default-closed drawers, material-route layer control, raw-material summary, allied supply-source summary, blockade survival summary, active flow ledger, dataset metadata, and node-click contextual factory sheet
- public JS/CSS/HTML check confirms `opsDetailSheet`, `openOpsSheet`, route-card detail layout, convergence marker sizing, reduced map glow, and context-highlight map classes are deployed
- browser screenshot check was blocked by local enterprise browser policy; public URL data was verified with `curl`

## Important URL Note

`local-deployer` initially printed:

- https://fingers-commissioner-dist-six.trycloudflare.com

That URL returned Cloudflare 1033 because the tunnel process was not present in PM2.

The active manually started tunnel is:

- https://fair-extreme-gmbh-humanities.trycloudflare.com

## Useful Commands

List deployments:

```bash
/Users/mollykim/projects/local-deployer/.venv/bin/deployer list
```

Show app logs:

```bash
pm2 logs ld-d4d-drone-production-conversion --nostream --lines 100
```

Show tunnel logs:

```bash
pm2 logs ld-d4d-drone-production-conversion-tunnel --nostream --lines 100
```

Restart the app:

```bash
pm2 restart ld-d4d-drone-production-conversion
```

Recreate only the tunnel if the quick URL expires:

```bash
pm2 delete ld-d4d-drone-production-conversion-tunnel
pm2 start cloudflared --name ld-d4d-drone-production-conversion-tunnel -- tunnel --url http://localhost:3009
pm2 logs ld-d4d-drone-production-conversion-tunnel --nostream --lines 100
```

## Safety Boundary

All route-risk and threat-corridor data is synthetic. The public factory and resource rows are candidate records inferred from product text and require verification for equipment, permits, material grade, line availability, and wartime legal status.

# Drone Production Conversion Sample Dataset

Generated: 2026-07-04 KST

## Purpose

This dataset supports the D4D demo `전시 드론 생산전환 의사결정 시스템`.

It uses public factory registry data to create a safe candidate-matching dataset for high-level, non-weaponized drone part families. The dataset does not assert that any company can or should be converted to military production.

v0.2 also adds critical-material feeder candidates for rare-earth/magnet inputs, battery material recovery, urban-mining/e-waste metals, and composite/light-metal feedstock. These are candidate verification queues, not confirmed rare-earth extraction capacity.

v0.3 adds road-network route metrics for logistics-cost planning. The active generated dataset was enriched with OSRM route distance/duration/geometry and keeps a fallback road-distance estimate path for environments without a routing provider.

v0.4 adds energy/capacity evidence fields. Candidate factories and resource nodes now include `energy_profile` with direct NGMS emissions/energy matches where available and regional industrial electricity proxies otherwise.

v0.5 adds grid/power-risk proxy zones, manufacturing-speed profiles, frozen-order ledger rows, in-transit shipment rows, and inventory/WIP rows. These are decision-support schemas and synthetic operational placeholders until ERP/MES/TMS and verified utility/customer-side data are connected.

## Files

- `drone_production_conversion_dataset.json`: processed demo dataset used by the app.
- `full_factory_candidate_capacity_backdata.csv`: full matched factory candidate pool with capacity, manufacturing-speed, energy, and grid-risk evidence. This is the algorithm backdata table, not the default map layer.
- `factory_pipeline_candidate_shortlist.csv`: scenario/category shortlist for dynamic pipeline planning before expanding expensive road-route matrices.
- `factory_capacity_backdata.csv`: map/demo sample factory-level capacity, manufacturing-speed, energy, and grid-risk evidence table.
- `factory_route_capacity_edges.csv`: scenario supplier-route/capacity edge table.
- `grid_risk_zones.csv`: coarse regional load-serving risk zones for continuity planning.
- `factory_operational_state.csv`: combined inventory/WIP, frozen-order, and in-transit shipment ledger.

The raw public CSV cache is generated under:

`/Users/mollykim/projects/D4D/03_data/raw/drone_production_conversion/factory_registry_public_snapshot.csv`

That raw folder is ignored by git.

## Source

- Public factory registry CSV: https://www.data.go.kr/data/15105482/fileData.do
- Future API enrichment candidate: https://www.data.go.kr/data/15087611/openapi.do
- Waste/recycling statistics API candidate: https://www.data.go.kr/data/15106003/openapi.do
- Recycling performance/operator status file/API candidate: https://www.data.go.kr/data/15105969/fileData.do
- Critical-mineral recycling policy basis: https://www.korea.kr/news/policyNewsView.do?newsId=148953591
- KEPCO large-load customer information: https://www.data.go.kr/data/15068962/fileData.do
- OpenStreetMap power-tag reference for future coarse geospatial validation: https://wiki.openstreetmap.org/wiki/Key:power

## Generated Fields

- `factory_candidates`: public factory candidates with inferred part-family tags.
- Full candidate pool: 29,616 factory candidates exported to CSV for algorithmic planning.
- Pipeline shortlist: 8,829 scenario/category candidate rows exported to CSV for route-matrix expansion.
- Map candidate layer: 180 factories, composed of the balanced demo sample plus every factory selected by the full-pool scenario plans.
- `resource_candidates`: public factory candidates with inferred critical-material/resource tags.
- `resource_categories`: rare-earth/magnet, battery, urban-mining/e-waste metals, and composite feedstock categories.
- `material_requirements`: high-level mapping from drone BOM families to upstream material risks.
- `bom`: high-level non-sensitive part families.
- `assembly_hubs`: synthetic demo assembly hubs.
- `plans`: baseline and threat-adjusted routing scenarios, including factory-to-hub and resource-to-factory routes.
- route metric fields: `straight_line_km`, `road_distance_km`, `duration_min`, `route_geometry`, `fuel_liters_per_trip`, `driver_hours_per_trip`, `estimated_trip_cost_krw`, `routing_provider`, `routing_status`.
- `logistics_cost_model`: placeholder cost assumptions for fuel and driver-hour estimates.
- `routing_design`: route-provider options and production integration notes.
- `energy_profile`: direct or proxy energy evidence for each factory/resource candidate.
- `energy_capacity_model`: interpretation rules and limitations for using power/energy as capacity evidence.
- `manufacturing_profile`: proxy daily output, surge output, setup days, minimum batch size, yield rate, and bottleneck notes for each factory.
- `grid_risk_zones`: province/city-cluster load-serving risk proxies using KEA electricity context, KEPCO large-customer equipment context, and factory distribution. These are not exact electric-facility dependency maps.
- `grid_disruption_scenarios`: coarse power-degradation scenarios that estimate affected factories, exposed part families, and capacity at risk.
- `grid_risk_profile`: factory-level grid dependency score, outage output multiplier, backup-hour estimate, and verification needs.
- `frozen_orders`: synthetic frozen order ledger rows for rolling-horizon reconfiguration constraints.
- `in_transit_shipments`: synthetic shipment rows with progress, ETA, and threat response options.
- `inventory_wip`: synthetic inventory, work-in-process, QA hold, committed, and available-to-ship rows.
- `apac_extension`: follow-on design direction for APAC allied sustainment C2.

## Important Limitations

- Factory equipment, machine age, live capacity, QA state, wartime legal status, and security readiness are not public in this dataset.
- Coordinates are approximate for demo safety and geocoding stability.
- Threat corridors are synthetic scenario assumptions, not real intelligence.
- Candidate tags are inferred from product text and require human verification.
- Rare-earth, magnet, battery, and e-waste nodes require separate checks for recycling permits, separation/refining process, material grade, and feedstock ownership.
- OSRM road routes are suitable for prototype visualization, not final Korean logistics pricing. Production should use an approved commercial provider or self-hosted road graph with validated road coverage, traffic, toll, and vehicle restrictions.
- High electricity/energy use is a useful production-scale signal, but it does not prove spare capacity, conversion readiness, or efficient output. Treat it as one weighted evidence input alongside equipment, workforce, inventory, certifications, and grid reliability.
- Grid-risk fields are coarse continuity-planning proxies. They must not be read as confirmed substation-to-factory dependencies or as a targetable power-infrastructure map.
- Frozen orders, in-transit shipments, and inventory/WIP rows are synthetic placeholders anchored to the demo plan. Production use requires ERP, MES, TMS, procurement, and warehouse feeds.

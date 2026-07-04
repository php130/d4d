# Drone Optimizer Input v0.8 Readiness Report

Generated: 2026-07-04T16:39:31.792883+00:00
Source dataset: `d4d.drone_production_conversion.v0.8`
Validation status: `pass_with_warnings`

## Artifact Counts

| Artifact | Count |
| --- | ---: |
| `nodes` | 238 |
| `edges` | 259 |
| `commodities` | 40 |
| `demands` | 108 |
| `capacities` | 525 |
| `constraints` | 109 |
| `inventory_wip` | 180 |
| `frozen_orders` | 24 |
| `in_transit_shipments` | 27 |

## Scenario Dry Run

| Scenario | Target 30d | Possible 30d | Bottleneck | Survival likely | Valley |
| --- | ---: | ---: | --- | ---: | --- |
| baseline | 10000 | 6428 | camera_module | 8.0d | D+9-D+73 |
| western_axis_threat | 10000 | 5788 | vtx_module | 7.6d | D+9-D+81 |
| southern_port_disruption | 10000 | 6434 | flight_controller | 7.4d | D+8-D+73 |

## Warnings

- 231 operating-state rows are synthetic placeholders.
- 259 edge capacities currently use generated flow as a proxy.
- 180 factory capacities are public-data proxies, not verified spare capacity.

## Solver Readiness Judgment

- Ready for v0.9 deterministic allocation/min-cost-flow prototype.
- Not yet sufficient for operational MILP without verified live capacity, vehicle fleet, route capacity, ERP/MES inventory, and supplier-contract feeds.
- Use `state.frozen_orders` and `state.in_transit_shipments` as hard constraints in the next solver iteration.
- Treat edge capacities as temporary upper-bound proxies until a vehicle/driver/route-throughput model is connected.

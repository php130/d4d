# Drone Allocation Optimizer v0.9 Report

Generated: 2026-07-04T16:39:43.313433+00:00
Source input: `d4d.drone_optimizer_input.v0.8`
Validation status: `pass_with_warnings`

## Scenario Results

| Scenario | Feasible output | Gap | Cost proxy | Risk | Limiting constraint |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 6,428 | 3,572 | 2,969,000 | 0.120 | Motor / Propulsion |
| western_axis_threat | 5,788 | 4,212 | 5,207,400 | 0.187 | Motor / Propulsion |
| southern_port_disruption | 6,434 | 3,566 | 2,927,600 | 0.166 | Motor / Propulsion |

## Validation Counts

| Item | Count |
| --- | ---: |
| `scenarios` | 3 |
| `selected_flows` | 144 |
| `shortages` | 42 |
| `binding_constraints` | 22 |

## Warnings

- baseline has output gap 3572 units
- western_axis_threat has output gap 4212 units
- southern_port_disruption has output gap 3566 units
- v0.9 is a deterministic allocation prototype, not a full MILP.
- Cost is a trip-count proxy because fleet and vehicle-capacity data are not connected.

## Next Step

Use this result as the bridge to v1.0 rolling-horizon reconfiguration. The next implementation should convert frozen orders and in-transit shipments from report constraints into hard constraints, then emit a user-facing Plan Delta.

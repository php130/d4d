# Drone Reconfiguration v1.0 Report

Generated: 2026-07-04T16:39:43.351775+00:00
Validation status: `pass_with_warnings`

## Plan Delta Summary

| Scenario | Level | Output delta | Cost delta | Risk delta | Added factories | Removed factories | Rerouted flows | Reserve actions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | monitor | 0 | 0 | 0.0000 | 0 | 0 | 0 | 0 |
| western_axis_threat | emergency_replan | -640 | 2,238,400 | 0.0673 | 37 | 33 | 0 | 8 |
| southern_port_disruption | emergency_replan | 6 | -41,400 | 0.0461 | 15 | 14 | 0 | 4 |

## Validation

| Item | Count |
| --- | ---: |
| `scenarios` | 3 |
| `frozen_order_actions` | 28 |
| `in_transit_actions` | 81 |
| `assembly_replacement_actions` | 12 |
| `emergency_replan_count` | 2 |

## Warnings

- western_axis_threat requires emergency replan review
- southern_port_disruption requires emergency replan review
- v1.0 emits decision deltas; it does not enforce a full rolling-horizon MILP yet.

## Next Step

Turn this Plan Delta into a true rolling-horizon loop: ingest event, update state, solve, freeze commitments, emit delta, and rerun after execution feedback.

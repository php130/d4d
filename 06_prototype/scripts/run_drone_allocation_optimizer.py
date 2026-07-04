#!/usr/bin/env python3
"""Run a deterministic allocation prototype over optimizer_input_v0_8.

v0.9 is deliberately modest: it does not claim to be a full MILP. It turns the
normalized v0.8 graph into an explainable allocation result by minimizing
shortage first and then preferring lower-cost/lower-risk routes inside the
current candidate edge pool.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR = ROOT / "06_prototype" / "app" / "drone_production_conversion" / "data"
SAMPLE_DATA_DIR = ROOT / "03_data" / "samples" / "drone_production_conversion"
INPUT_PATH = APP_DATA_DIR / "optimizer_input_v0_8.json"
JSON_NAME = "optimizer_result_v0_9.json"
JS_NAME = "optimizer_result_v0_9.js"
REPORT_NAME = "optimizer_result_report_v0_9.md"

UNIT_TRIP_EQUIVALENT = 1000
KG_TRIP_EQUIVALENT = 1000


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_js(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("window.DRONE_OPTIMIZATION_RESULT_V0_9 = ")
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write(";\n")


def as_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def severity_from_coverage(coverage: float) -> str:
    if coverage >= 0.95:
        return "covered"
    if coverage >= 0.75:
        return "watch"
    if coverage >= 0.4:
        return "short"
    return "critical"


def edge_quantity(edge: dict[str, Any]) -> float:
    return as_float(edge.get("quantity"))


def edge_risk(edge: dict[str, Any]) -> float:
    return as_float((edge.get("cost") or {}).get("risk_score"))


def edge_cost(edge: dict[str, Any]) -> float:
    return as_float((edge.get("cost") or {}).get("estimated_trip_cost_krw"))


def trip_count_proxy(edge: dict[str, Any], quantity: float) -> int:
    unit = edge.get("quantity_unit", "")
    base = KG_TRIP_EQUIVALENT if "kg" in unit else UNIT_TRIP_EQUIVALENT
    return max(1, int(math.ceil(quantity / base))) if quantity > 0 else 0


def route_score(edge: dict[str, Any], nodes_by_id: dict[str, dict[str, Any]]) -> float:
    quantity = max(edge_quantity(edge), 1.0)
    cost_per_unit = edge_cost(edge) / quantity
    risk_penalty = edge_risk(edge) * 5000
    origin = nodes_by_id.get(edge.get("origin_node_id"), {})
    grid_penalty = (
        as_float(origin.get("grid_dependency_score")) * 1000
        if edge.get("edge_type") == "component_factory_to_priority_assembly_factory"
        else 0
    )
    reroute_penalty = 250 if "reroute" in str(edge.get("status", "")).lower() else 0
    return round(cost_per_unit + risk_penalty + grid_penalty + reroute_penalty, 3)


def commodity_label(commodity_id: str, commodities_by_id: dict[str, dict[str, Any]]) -> str:
    item = commodities_by_id.get(commodity_id, {})
    return item.get("label") or commodity_id


def allocate_edges_for_demand(
    scenario_id: str,
    demand: dict[str, Any],
    edges: list[dict[str, Any]],
    nodes_by_id: dict[str, dict[str, Any]],
    commodities_by_id: dict[str, dict[str, Any]],
    flow_layer: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    required = as_float(demand.get("quantity"))
    commodity_id = demand.get("commodity_id")
    candidates = [
        edge
        for edge in edges
        if edge.get("scenario_id") == scenario_id and edge.get("commodity_id") == commodity_id and edge_quantity(edge) > 0
    ]
    candidates.sort(key=lambda edge: (route_score(edge, nodes_by_id), edge_risk(edge), edge_cost(edge), edge.get("edge_id", "")))

    selected: list[dict[str, Any]] = []
    remaining = required
    for rank, edge in enumerate(candidates, start=1):
        if remaining <= 0:
            break
        available = edge_quantity(edge)
        allocated = min(available, remaining)
        if allocated <= 0:
            continue
        trips = trip_count_proxy(edge, allocated)
        per_trip = edge_cost(edge)
        total_cost = round(per_trip * trips)
        selected.append(
            {
                "edge_id": edge.get("edge_id"),
                "flow_layer": flow_layer,
                "edge_type": edge.get("edge_type"),
                "commodity_id": commodity_id,
                "commodity_label": commodity_label(commodity_id, commodities_by_id),
                "origin_node_id": edge.get("origin_node_id"),
                "destination_node_id": edge.get("destination_node_id"),
                "allocated_quantity": round(allocated, 3),
                "quantity_unit": edge.get("quantity_unit"),
                "trip_count_proxy": trips,
                "estimated_cost_krw_proxy": total_cost,
                "risk_score": edge_risk(edge),
                "route_score": route_score(edge, nodes_by_id),
                "selection_rank": rank,
                "status": edge.get("status"),
                "selected_reason": "lowest route score while filling unmet demand",
            }
        )
        remaining -= allocated

    allocated_total = sum(row["allocated_quantity"] for row in selected)
    coverage = allocated_total / required if required else 1.0
    shortage = max(0.0, required - allocated_total)
    shortage_row = {
        "scenario_id": scenario_id,
        "commodity_id": commodity_id,
        "commodity_label": commodity_label(commodity_id, commodities_by_id),
        "required_quantity": round(required, 3),
        "allocated_quantity": round(allocated_total, 3),
        "shortage_quantity": round(shortage, 3),
        "coverage_ratio": round(min(1.0, coverage), 4),
        "quantity_unit": demand.get("quantity_unit"),
        "severity": severity_from_coverage(coverage),
        "driver": "candidate_edge_capacity" if shortage > 0 else "covered_by_current_candidate_edges",
    }
    return selected, shortage_row


def material_shortage_rows(input_data: dict[str, Any], scenario_id: str, commodities_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    capacities_by_commodity = {
        row.get("commodity_id"): as_float(row.get("quantity"))
        for row in input_data["capacities"]
        if row.get("scenario_id") == scenario_id and row.get("capacity_type") == "scenario_material_available"
    }
    rows: list[dict[str, Any]] = []
    for demand in input_data["demands"]:
        if demand.get("scenario_id") != scenario_id or not str(demand.get("commodity_id", "")).startswith("material:"):
            continue
        required = as_float(demand.get("quantity"))
        available = capacities_by_commodity.get(demand.get("commodity_id"), 0.0)
        coverage = available / required if required else 1.0
        shortage = max(0.0, required - available)
        rows.append(
            {
                "scenario_id": scenario_id,
                "commodity_id": demand.get("commodity_id"),
                "commodity_label": commodity_label(demand.get("commodity_id"), commodities_by_id),
                "required_quantity": round(required, 3),
                "allocated_quantity": round(min(required, available), 3),
                "available_quantity": round(available, 3),
                "shortage_quantity": round(shortage, 3),
                "coverage_ratio": round(min(1.0, coverage), 4),
                "quantity_unit": demand.get("quantity_unit"),
                "severity": severity_from_coverage(coverage),
                "driver": "raw_material_availability",
            }
        )
    return rows


def survival_constraints(input_data: dict[str, Any], scenario_id: str, commodities_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for constraint in input_data["constraints"]:
        if constraint.get("scenario_id") != scenario_id:
            continue
        if constraint.get("constraint_type") not in {"component_blockade_survival", "subcomponent_blockade_survival"}:
            continue
        likely = as_float(constraint.get("survival_days_likely"))
        if likely > 14 and not constraint.get("is_bottleneck"):
            continue
        rows.append(
            {
                "constraint_id": constraint.get("constraint_id"),
                "constraint_type": constraint.get("constraint_type"),
                "commodity_id": constraint.get("commodity_id"),
                "commodity_label": commodity_label(constraint.get("commodity_id"), commodities_by_id),
                "survival_days_likely": likely,
                "daily_demand_units": as_float(constraint.get("daily_demand_units")),
                "net_burn_units_per_day": as_float(constraint.get("net_burn_units_per_day")),
                "ramp_gap_days": as_float(constraint.get("ramp_gap_days")),
                "severity": "critical" if likely < 10 else "watch",
            }
        )
    rows.sort(key=lambda item: (item["survival_days_likely"], item["constraint_type"]))
    return rows[:8]


def scenario_result(
    input_data: dict[str, Any],
    scenario: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    commodities_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scenario_id = scenario["scenario_id"]
    part_demands = [
        row
        for row in input_data["demands"]
        if row.get("scenario_id") == scenario_id and str(row.get("commodity_id", "")).startswith("part:")
    ]
    all_flows: list[dict[str, Any]] = []
    shortages: list[dict[str, Any]] = []

    for demand in part_demands:
        selected, shortage = allocate_edges_for_demand(
            scenario_id,
            demand,
            input_data["edges"],
            nodes_by_id,
            commodities_by_id,
            "part_factory_to_final_assembly",
        )
        all_flows.extend(selected)
        shortages.append(shortage)

    material_shortages = material_shortage_rows(input_data, scenario_id, commodities_by_id)
    shortages.extend(material_shortages)

    limiting_parts = [row for row in shortages if str(row["commodity_id"]).startswith("part:")]
    limiting_parts.sort(key=lambda row: (row["coverage_ratio"], -row["shortage_quantity"]))
    limiting_part = limiting_parts[0] if limiting_parts else None

    target = as_float(scenario.get("target_drones_30d"))
    feasible_output = 0.0
    if limiting_part:
        part_commodity = commodities_by_id.get(limiting_part["commodity_id"], {})
        bom_qty = max(as_float(part_commodity.get("bom_quantity_per_drone"), 1.0), 1.0)
        feasible_output = limiting_part["allocated_quantity"] / bom_qty

    total_flow_quantity = sum(row["allocated_quantity"] for row in all_flows)
    total_cost = sum(row["estimated_cost_krw_proxy"] for row in all_flows)
    weighted_risk = (
        sum(row["allocated_quantity"] * row["risk_score"] for row in all_flows) / total_flow_quantity
        if total_flow_quantity
        else 0
    )
    weighted_route_score = (
        sum(row["allocated_quantity"] * row["route_score"] for row in all_flows) / total_flow_quantity
        if total_flow_quantity
        else 0
    )

    survival_rows = survival_constraints(input_data, scenario_id, commodities_by_id)
    material_blockers = [row for row in material_shortages if row["shortage_quantity"] > 0 or row["coverage_ratio"] < 0.95]

    binding_constraints: list[dict[str, Any]] = []
    if limiting_part:
        binding_constraints.append(
            {
                "constraint_type": "limiting_part_family",
                "commodity_id": limiting_part["commodity_id"],
                "commodity_label": limiting_part["commodity_label"],
                "coverage_ratio": limiting_part["coverage_ratio"],
                "shortage_quantity": limiting_part["shortage_quantity"],
                "severity": limiting_part["severity"],
            }
        )
    binding_constraints.extend(survival_rows[:5])
    binding_constraints.extend(material_blockers[:3])
    binding_constraints.append(
        {
            "constraint_type": "state_freeze_and_transit",
            "frozen_orders": len(input_data.get("state", {}).get("frozen_orders", [])),
            "in_transit_shipments": len(input_data.get("state", {}).get("in_transit_shipments", [])),
            "solver_handling": "included as reporting constraints in v0.9; hard recourse constraints in v1.0",
        }
    )

    scenario_delta = {
        "baseline_reference": "baseline",
        "added_factory_count": 0,
        "removed_factory_count": 0,
        "rerouted_flow_count": sum(1 for row in all_flows if "reroute" in str(row.get("status", "")).lower()),
        "output_delta_vs_baseline": None,
    }

    return {
        "scenario_id": scenario_id,
        "solver_method": "deterministic_greedy_min_shortage_then_route_score",
        "method_limitations": [
            "Uses current candidate edge pool only; it does not search all possible factories/routes.",
            "Edge capacity is a generated-flow proxy until vehicle/driver/route-throughput data is connected.",
            "Factory output is public-data proxy capacity, not verified spare production capacity.",
        ],
        "objective_breakdown": {
            "target_drones_30d": round(target),
            "feasible_output_units_30d": round(feasible_output),
            "output_gap_units_30d": round(max(0.0, target - feasible_output)),
            "total_part_shortage_units_30d": round(
                sum(row["shortage_quantity"] for row in shortages if str(row["commodity_id"]).startswith("part:"))
            ),
            "material_shortage_count": len([row for row in material_shortages if row["shortage_quantity"] > 0]),
            "logistics_cost_krw_proxy": round(total_cost),
            "weighted_route_risk": round(weighted_risk, 4),
            "weighted_route_score": round(weighted_route_score, 3),
            "blockade_survival_days_likely": scenario.get("blockade_survival_days_likely"),
            "valley_start_day": scenario.get("valley_start_day"),
            "valley_end_day": scenario.get("valley_end_day"),
            "valley_depth_units_per_day": scenario.get("valley_depth_units_per_day"),
        },
        "selected_flows": all_flows,
        "shortages": shortages,
        "binding_constraints": binding_constraints,
        "plan_delta": scenario_delta,
    }


def attach_plan_deltas(results: list[dict[str, Any]]) -> None:
    baseline = next((row for row in results if row["scenario_id"] == "baseline"), None)
    if not baseline:
        return
    baseline_factories = {row["origin_node_id"] for row in baseline["selected_flows"] if row["origin_node_id"]}
    baseline_output = baseline["objective_breakdown"]["feasible_output_units_30d"]
    for result in results:
        factories = {row["origin_node_id"] for row in result["selected_flows"] if row["origin_node_id"]}
        result["plan_delta"].update(
            {
                "added_factory_count": len(factories - baseline_factories),
                "removed_factory_count": len(baseline_factories - factories),
                "output_delta_vs_baseline": result["objective_breakdown"]["feasible_output_units_30d"] - baseline_output,
                "added_factory_ids": sorted(factories - baseline_factories)[:20],
                "removed_factory_ids": sorted(baseline_factories - factories)[:20],
            }
        )


def validate_result(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for scenario in payload["scenarios"]:
        if not scenario.get("selected_flows"):
            errors.append(f"{scenario['scenario_id']} has no selected flows")
        if not scenario.get("shortages"):
            errors.append(f"{scenario['scenario_id']} has no shortage rows")
        if not scenario.get("binding_constraints"):
            errors.append(f"{scenario['scenario_id']} has no binding constraints")
        if scenario["objective_breakdown"]["feasible_output_units_30d"] <= 0:
            errors.append(f"{scenario['scenario_id']} feasible output is zero")
        if scenario["objective_breakdown"]["output_gap_units_30d"] > 0:
            warnings.append(
                f"{scenario['scenario_id']} has output gap {scenario['objective_breakdown']['output_gap_units_30d']} units"
            )
    warnings.append("v0.9 is a deterministic allocation prototype, not a full MILP.")
    warnings.append("Cost is a trip-count proxy because fleet and vehicle-capacity data are not connected.")
    return {
        "status": "pass" if not errors and not warnings else "pass_with_warnings" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "scenarios": len(payload["scenarios"]),
            "selected_flows": sum(len(row["selected_flows"]) for row in payload["scenarios"]),
            "shortages": sum(len(row["shortages"]) for row in payload["scenarios"]),
            "binding_constraints": sum(len(row["binding_constraints"]) for row in payload["scenarios"]),
        },
    }


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Drone Allocation Optimizer v0.9 Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Source input: `{payload['source_optimizer_input_schema']}`",
        f"Validation status: `{payload['validation']['status']}`",
        "",
        "## Scenario Results",
        "",
        "| Scenario | Feasible output | Gap | Cost proxy | Risk | Limiting constraint |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for scenario in payload["scenarios"]:
        objective = scenario["objective_breakdown"]
        limiting = scenario["binding_constraints"][0] if scenario["binding_constraints"] else {}
        lines.append(
            "| {sid} | {out:,} | {gap:,} | {cost:,} | {risk:.3f} | {limiting} |".format(
                sid=scenario["scenario_id"],
                out=objective["feasible_output_units_30d"],
                gap=objective["output_gap_units_30d"],
                cost=objective["logistics_cost_krw_proxy"],
                risk=objective["weighted_route_risk"],
                limiting=limiting.get("commodity_label") or limiting.get("constraint_type", "-"),
            )
        )

    lines.extend(["", "## Validation Counts", "", "| Item | Count |", "| --- | ---: |"])
    for key, value in payload["validation"]["counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Warnings", ""])
    for warning in payload["validation"]["warnings"]:
        lines.append(f"- {warning}")

    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Use this result as the bridge to v1.0 rolling-horizon reconfiguration. The next implementation should convert frozen orders and in-transit shipments from report constraints into hard constraints, then emit a user-facing Plan Delta.",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(input_data: dict[str, Any]) -> dict[str, Any]:
    nodes_by_id = {row["node_id"]: row for row in input_data["nodes"]}
    commodities_by_id = {row["commodity_id"]: row for row in input_data["commodities"]}
    scenarios = [
        scenario_result(input_data, scenario, nodes_by_id, commodities_by_id)
        for scenario in input_data["scenario_parameters"]
    ]
    attach_plan_deltas(scenarios)
    payload = {
        "schema": "d4d.drone_allocation_optimizer_result.v0.9",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_optimizer_input_schema": input_data.get("schema"),
        "source_dataset_schema": input_data.get("source_dataset_schema"),
        "solver_method": "deterministic_greedy_min_shortage_then_route_score",
        "assumptions": {
            "unit_trip_equivalent": UNIT_TRIP_EQUIVALENT,
            "kg_trip_equivalent": KG_TRIP_EQUIVALENT,
            "primary_objective": "fill demand from available candidate edges; report shortage if candidate capacity is insufficient",
            "secondary_objective": "prefer lower route score, where score includes route cost, route risk, grid dependency, and reroute penalty",
        },
        "scenarios": scenarios,
    }
    payload["validation"] = validate_result(payload)
    return payload


def main() -> None:
    input_data = load_json(INPUT_PATH)
    payload = build_payload(input_data)
    report = build_report(payload)

    for directory in (APP_DATA_DIR, SAMPLE_DATA_DIR):
        write_json(directory / JSON_NAME, payload)
        write_text(directory / REPORT_NAME, report)
    write_js(APP_DATA_DIR / JS_NAME, payload)

    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "validation_status": payload["validation"]["status"],
                "counts": payload["validation"]["counts"],
                "warnings": payload["validation"]["warnings"],
                "outputs": [
                    str((APP_DATA_DIR / JSON_NAME).relative_to(ROOT)),
                    str((APP_DATA_DIR / JS_NAME).relative_to(ROOT)),
                    str((APP_DATA_DIR / REPORT_NAME).relative_to(ROOT)),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if payload["validation"]["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

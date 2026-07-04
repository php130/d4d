#!/usr/bin/env python3
"""Build v1.0 reconfiguration deltas from v0.9 optimizer results.

This is a product-facing bridge: it explains what changes when a threat or
logistics scenario replaces the baseline plan. It does not issue operational
orders; it produces reviewable decision deltas for a human planner.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR = ROOT / "06_prototype" / "app" / "drone_production_conversion" / "data"
SAMPLE_DATA_DIR = ROOT / "03_data" / "samples" / "drone_production_conversion"
INPUT_PATH = APP_DATA_DIR / "optimizer_input_v0_8.json"
OPTIMIZER_PATH = APP_DATA_DIR / "optimizer_result_v0_9.json"
JSON_NAME = "reconfiguration_result_v1_0.json"
JS_NAME = "reconfiguration_result_v1_0.js"
REPORT_NAME = "reconfiguration_result_report_v1_0.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_js(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("window.DRONE_RECONFIGURATION_RESULT_V1_0 = ")
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write(";\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def flow_factory_ids(result: dict[str, Any]) -> set[str]:
    return {row.get("origin_node_id") for row in result.get("selected_flows", []) if row.get("origin_node_id")}


def index_by_scenario(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in result.get("scenarios", [])}


def objective(result: dict[str, Any]) -> dict[str, Any]:
    return result.get("objective_breakdown") or {}


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def company_group_key(value: str | None) -> str:
    text = (value or "").split("/")[0].lower()
    for token in ["주식회사", "(주)", "㈜", "co.ltd", "co ltd", "ltd", "inc", "corp"]:
        text = text.replace(token, "")
    return re.sub(r"[\s\-_,.&·()]", "", text)


def haversine_km(a: dict[str, Any], b: dict[str, Any]) -> float:
    lat1 = math.radians(as_float(a.get("lat")))
    lon1 = math.radians(as_float(a.get("lon")))
    lat2 = math.radians(as_float(b.get("lat")))
    lon2 = math.radians(as_float(b.get("lon")))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(h)))


def point_segment_distance_km(point: dict[str, Any], start: dict[str, Any], end: dict[str, Any]) -> float:
    lat0 = as_float(point.get("lat"))
    lon0 = as_float(point.get("lon"))
    lat1 = as_float(start.get("lat"))
    lon1 = as_float(start.get("lon"))
    lat2 = as_float(end.get("lat"))
    lon2 = as_float(end.get("lon"))
    scale = math.cos(math.radians((lat0 + lat1 + lat2) / 3))
    px, py = lon0 * scale, lat0
    ax, ay = lon1 * scale, lat1
    bx, by = lon2 * scale, lat2
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return haversine_km(point, start)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    nearest = {"lat": ay + t * dy, "lon": (ax + t * dx) / scale if scale else lon0}
    return haversine_km(point, nearest)


def threat_risk_for_node(node: dict[str, Any], scenario: dict[str, Any]) -> tuple[float, str]:
    threat = scenario.get("threat") or {}
    path = threat.get("path") or []
    radius = as_float(threat.get("risk_radius_km"), 0)
    probability = as_float(threat.get("probability"), 0)
    if len(path) < 2 or radius <= 0 or probability <= 0:
        return 0.0, "no active scenario threat path"
    distances = [
        point_segment_distance_km(node, path[index], path[index + 1])
        for index in range(len(path) - 1)
    ]
    nearest = min(distances) if distances else 999
    if nearest >= radius * 1.8:
        return 0.0, f"outside scenario threat corridor by {nearest:.1f} km"
    falloff = max(0.0, 1 - nearest / max(radius, 1))
    risk = min(0.96, probability * (0.35 + 0.65 * falloff))
    return round(risk, 3), f"within {nearest:.1f} km of synthetic scenario corridor"


def risk_level(output_delta: float, risk_delta: float, rerouted_count: int) -> str:
    if output_delta <= -500 or risk_delta >= 0.03 or rerouted_count >= 20:
        return "emergency_replan"
    if output_delta < 0 or risk_delta > 0 or rerouted_count:
        return "replan_review"
    return "monitor"


def frozen_order_actions(input_data: dict[str, Any], removed_factories: set[str], scenario_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for order in input_data.get("state", {}).get("frozen_orders", []):
        factory_id = order.get("factory_id")
        if factory_id not in removed_factories:
            continue
        rows.append(
            {
                "order_id": order.get("id"),
                "factory_id": factory_id,
                "part_category": order.get("part_category"),
                "quantity_units": order.get("frozen_quantity_units"),
                "freeze_until_day": order.get("freeze_until_day"),
                "recommended_action": "protect_commitment_until_freeze_expires_then_reallocate",
                "reason": f"{scenario_id} removes or deprioritizes this factory, but the order is inside a freeze window.",
            }
        )
    return rows


def in_transit_actions(input_data: dict[str, Any], removed_factories: set[str], added_factories: set[str], scenario_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for shipment in input_data.get("state", {}).get("in_transit_shipments", []):
        factory_id = shipment.get("factory_id") or shipment.get("target_factory_id")
        destination_id = shipment.get("destination_factory_id")
        if factory_id in removed_factories or destination_id in removed_factories:
            action = "hold_or_continue_to_safe_receiving_point"
            reason = "source or receiving factory is disabled, at risk, or no longer in the scenario-selected flow set"
        elif added_factories and scenario_id != "baseline":
            action = "continue"
            reason = "shipment is already in transit; avoid churn unless route risk crosses emergency threshold"
        else:
            action = "continue"
            reason = "no reconfiguration conflict detected"
        rows.append(
            {
                "shipment_id": shipment.get("id"),
                "shipment_kind": shipment.get("shipment_kind"),
                "route_id": shipment.get("route_id"),
                "factory_id": factory_id,
                "destination_factory_id": destination_id,
                "part_category": shipment.get("part_category"),
                "quantity_units": shipment.get("quantity_units"),
                "eta_hours": shipment.get("eta_hours"),
                "recommended_action": action,
                "reason": reason,
            }
        )
    return rows


def scenario_by_id(input_data: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    return next((row for row in input_data.get("scenario_parameters", []) if row.get("scenario_id") == scenario_id), {})


def assembly_replacement_actions(
    input_data: dict[str, Any],
    scenario_id: str,
    removed_factories: set[str],
) -> list[dict[str, Any]]:
    scenario = scenario_by_id(input_data, scenario_id)
    nodes = [row for row in input_data.get("nodes", []) if row.get("node_type") == "factory"]
    core_nodes = [
        row
        for row in nodes
        if row.get("category") == "drone_assembly" and row.get("assembly_operating_status") == "core_operating"
    ]
    reserve_nodes = [
        row
        for row in nodes
        if row.get("category") == "drone_assembly" and row.get("assembly_operating_status") == "reserve_standby"
    ]
    if not core_nodes or not reserve_nodes:
        return []

    disabled: list[dict[str, Any]] = []
    for node in core_nodes:
        risk, risk_reason = threat_risk_for_node(node, scenario)
        if node.get("node_id") in removed_factories or (scenario_id != "baseline" and risk >= 0.32):
            disabled.append({**node, "_scenario_risk": risk, "_risk_reason": risk_reason})

    rows: list[dict[str, Any]] = []
    used_targets: set[str] = set()
    for source in sorted(disabled, key=lambda item: (-as_float(item.get("_scenario_risk")), item.get("name", "")))[:8]:
        source_key = company_group_key(source.get("name"))
        ranked: list[tuple[float, dict[str, Any], float, float, str]] = []
        for candidate in reserve_nodes:
            if candidate.get("node_id") in used_targets:
                continue
            candidate_risk, candidate_reason = threat_risk_for_node(candidate, scenario)
            distance = haversine_km(source, candidate)
            same_company_bonus = -58 if source_key and source_key == company_group_key(candidate.get("name")) else 0
            inland_bonus = -18 if scenario_id == "southern_port_disruption" and candidate.get("province") not in {"부산광역시", "울산광역시", "경상남도"} else 0
            score = (
                distance
                + candidate_risk * 190
                - as_float(candidate.get("capacity_units_30d")) / 75
                - as_float(candidate.get("capacity_confidence")) * 30
                - as_float(candidate.get("priority_weight"), 1.0) * 12
                + same_company_bonus
                + inland_bonus
            )
            ranked.append((score, candidate, distance, candidate_risk, candidate_reason))
        ranked.sort(key=lambda item: item[0])
        for rank, (_, target, distance, target_risk, target_reason) in enumerate(ranked[:2], start=1):
            if rank == 1:
                used_targets.add(target.get("node_id"))
            road_distance = round(distance * 1.28, 1)
            rows.append(
                {
                    "action_id": f"reserve_assembly_{scenario_id}_{source.get('node_id')}_{target.get('node_id')}_{rank}",
                    "action_type": "activate_reserve_final_assembly_factory",
                    "part_category": "drone_assembly",
                    "from_factory_id": source.get("node_id"),
                    "from_factory_name": source.get("name"),
                    "from_site_label": source.get("priority_site_label"),
                    "from_province": source.get("province"),
                    "from_city": source.get("city"),
                    "from": {"lat": source.get("lat"), "lon": source.get("lon")},
                    "from_scenario_risk": source.get("_scenario_risk"),
                    "from_risk_reason": source.get("_risk_reason"),
                    "to_factory_id": target.get("node_id"),
                    "to_factory_name": target.get("name"),
                    "to_site_label": target.get("priority_site_label"),
                    "to_province": target.get("province"),
                    "to_city": target.get("city"),
                    "to": {"lat": target.get("lat"), "lon": target.get("lon")},
                    "to_scenario_risk": target_risk,
                    "to_risk_reason": target_reason,
                    "rank": rank,
                    "same_company_group": source_key == company_group_key(target.get("name")),
                    "reserve_capacity_units_30d": round(as_float(target.get("capacity_units_30d"))),
                    "reserve_nominal_daily_output_units": round(as_float(target.get("nominal_daily_output_units"))),
                    "activation_setup_days_estimate": as_float(target.get("setup_days_estimate")),
                    "straight_line_distance_km": round(distance, 1),
                    "road_distance_km_estimate": road_distance,
                    "recommended_action": "activate_reserve_and_reassign_component_receiving_routes",
                    "visualization": {
                        "line_style": "dashed_arrow",
                        "from_factory_id": source.get("node_id"),
                        "to_factory_id": target.get("node_id"),
                    },
                    "reason": (
                        "Core final-assembly factory is inside the synthetic scenario risk corridor; "
                        "reserve standby site is ranked by lower risk, distance, same-company continuity, and proxy capacity."
                    ),
                    "data_status": "reserve_mapping_from_public_address_seed_proxy",
                }
            )
    return rows


def build_reconfiguration(input_data: dict[str, Any], optimizer_result: dict[str, Any]) -> dict[str, Any]:
    scenarios = index_by_scenario(optimizer_result)
    baseline = scenarios.get("baseline")
    if not baseline:
        raise ValueError("baseline scenario is required")

    baseline_obj = objective(baseline)
    baseline_factories = flow_factory_ids(baseline)
    baseline_cost = float(baseline_obj.get("logistics_cost_krw_proxy") or 0)
    baseline_risk = float(baseline_obj.get("weighted_route_risk") or 0)
    baseline_output = float(baseline_obj.get("feasible_output_units_30d") or 0)

    results: list[dict[str, Any]] = []
    for scenario_id, scenario in scenarios.items():
        current_obj = objective(scenario)
        current_factories = flow_factory_ids(scenario)
        added = current_factories - baseline_factories
        removed = baseline_factories - current_factories
        replacement_actions = assembly_replacement_actions(input_data, scenario_id, removed)
        disabled_assembly_ids = {
            row["from_factory_id"] for row in replacement_actions if row.get("from_factory_id")
        }
        replacement_factory_ids = {
            row["to_factory_id"] for row in replacement_actions if row.get("to_factory_id")
        }
        scenario_added = added | replacement_factory_ids
        scenario_removed = removed | disabled_assembly_ids
        output_delta = float(current_obj.get("feasible_output_units_30d") or 0) - baseline_output
        cost_delta = float(current_obj.get("logistics_cost_krw_proxy") or 0) - baseline_cost
        risk_delta = float(current_obj.get("weighted_route_risk") or 0) - baseline_risk
        rerouted_count = int((scenario.get("plan_delta") or {}).get("rerouted_flow_count") or 0)
        level = risk_level(output_delta, risk_delta, rerouted_count + len(replacement_actions))
        frozen_actions = frozen_order_actions(input_data, scenario_removed, scenario_id)
        transit_actions = in_transit_actions(input_data, scenario_removed, scenario_added, scenario_id)
        binding = scenario.get("binding_constraints", [])

        if scenario_id == "baseline":
            trigger = "baseline_monitoring"
            recommended = "maintain_current_plan_and_verify_final_assembly_capacity"
        elif level == "emergency_replan":
            trigger = "threat_or_logistics_state_change"
            recommended = "issue_replan_review: verify added factories, protect frozen orders, and prepare alternate assembly capacity"
        else:
            trigger = "scenario_watch"
            recommended = "monitor_and_prepare_reallocation_package"

        results.append(
            {
                "scenario_id": scenario_id,
                "trigger_type": trigger,
                "reconfiguration_level": level,
                "recommended_action": recommended,
                "delta_metrics": {
                    "feasible_output_delta_units_30d": round(output_delta),
                    "logistics_cost_delta_krw_proxy": round(cost_delta),
                    "weighted_route_risk_delta": round(risk_delta, 4),
                    "added_factory_count": len(scenario_added),
                    "removed_factory_count": len(scenario_removed),
                    "rerouted_flow_count": rerouted_count,
                    "reserve_replacement_action_count": len(replacement_actions),
                    "disabled_core_assembly_factory_count": len(disabled_assembly_ids),
                    "reserve_assembly_factory_count": len(replacement_factory_ids),
                    "frozen_order_conflict_count": len(frozen_actions),
                    "in_transit_review_count": len([row for row in transit_actions if row["recommended_action"] != "continue"]),
                },
                "added_factory_ids": sorted(scenario_added)[:30],
                "removed_factory_ids": sorted(scenario_removed)[:30],
                "disabled_core_assembly_factory_ids": sorted(disabled_assembly_ids),
                "reserve_assembly_factory_ids": sorted(replacement_factory_ids),
                "assembly_replacement_actions": replacement_actions[:30],
                "frozen_order_actions": frozen_actions,
                "in_transit_actions": transit_actions[:30],
                "binding_constraints": binding[:8],
                "human_review_checklist": [
                    "Confirm final assembly conversion capacity and QA benches first.",
                    "If reserve assembly actions exist, verify standby site activation before changing component receiving routes.",
                    "Check whether frozen orders can be protected without increasing route risk.",
                    "Verify added factories before treating them as real mobilization capacity.",
                    "Keep in-transit shipments stable unless route risk exceeds emergency threshold.",
                    "Update ERP/MES/TMS state and rerun v0.9/v1.0 after each material event.",
                ],
            }
        )

    return {
        "schema": "d4d.drone_reconfiguration_result.v1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_optimizer_result_schema": optimizer_result.get("schema"),
        "source_optimizer_input_schema": input_data.get("schema"),
        "method": "baseline_to_scenario_plan_delta_with_frozen_and_in_transit_review",
        "safe_boundary": "Decision-support delta only. No autonomous tasking, no payload data, no tactical orders.",
        "scenarios": results,
    }


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not payload.get("scenarios"):
        errors.append("no reconfiguration scenarios")
    for scenario in payload.get("scenarios", []):
        if "delta_metrics" not in scenario:
            errors.append(f"{scenario.get('scenario_id')} missing delta metrics")
        if scenario.get("reconfiguration_level") == "emergency_replan":
            warnings.append(f"{scenario.get('scenario_id')} requires emergency replan review")
    warnings.append("v1.0 emits decision deltas; it does not enforce a full rolling-horizon MILP yet.")
    return {
        "status": "pass" if not errors and not warnings else "pass_with_warnings" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "scenarios": len(payload.get("scenarios", [])),
            "frozen_order_actions": sum(len(row.get("frozen_order_actions", [])) for row in payload.get("scenarios", [])),
            "in_transit_actions": sum(len(row.get("in_transit_actions", [])) for row in payload.get("scenarios", [])),
            "assembly_replacement_actions": sum(
                len(row.get("assembly_replacement_actions", [])) for row in payload.get("scenarios", [])
            ),
            "emergency_replan_count": sum(1 for row in payload.get("scenarios", []) if row.get("reconfiguration_level") == "emergency_replan"),
        },
    }


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Drone Reconfiguration v1.0 Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Validation status: `{payload['validation']['status']}`",
        "",
        "## Plan Delta Summary",
        "",
        "| Scenario | Level | Output delta | Cost delta | Risk delta | Added factories | Removed factories | Rerouted flows | Reserve actions |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario in payload["scenarios"]:
        metrics = scenario["delta_metrics"]
        lines.append(
            "| {sid} | {level} | {out:,} | {cost:,} | {risk:.4f} | {added} | {removed} | {rerouted} | {reserve} |".format(
                sid=scenario["scenario_id"],
                level=scenario["reconfiguration_level"],
                out=metrics["feasible_output_delta_units_30d"],
                cost=metrics["logistics_cost_delta_krw_proxy"],
                risk=metrics["weighted_route_risk_delta"],
                added=metrics["added_factory_count"],
                removed=metrics["removed_factory_count"],
                rerouted=metrics["rerouted_flow_count"],
                reserve=metrics.get("reserve_replacement_action_count", 0),
            )
        )
    lines.extend(["", "## Validation", "", "| Item | Count |", "| --- | ---: |"])
    for key, value in payload["validation"]["counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Warnings", ""])
    for warning in payload["validation"]["warnings"]:
        lines.append(f"- {warning}")
    lines.extend(["", "## Next Step", "", "Turn this Plan Delta into a true rolling-horizon loop: ingest event, update state, solve, freeze commitments, emit delta, and rerun after execution feedback.", ""])
    return "\n".join(lines)


def main() -> None:
    input_data = load_json(INPUT_PATH)
    optimizer_result = load_json(OPTIMIZER_PATH)
    payload = build_reconfiguration(input_data, optimizer_result)
    payload["validation"] = validate(payload)
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

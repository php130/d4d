#!/usr/bin/env python3
"""Build normalized optimizer input from the D4D drone production dataset.

This script is intentionally separate from the main dataset generator. It turns
the current demo graph into a solver-oriented contract without changing the app
data model that already powers the map.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR = ROOT / "06_prototype" / "app" / "drone_production_conversion" / "data"
SAMPLE_DATA_DIR = ROOT / "03_data" / "samples" / "drone_production_conversion"
DATASET_PATH = APP_DATA_DIR / "drone_production_conversion_dataset.json"
OUTPUT_NAME = "optimizer_input_v0_8.json"
REPORT_NAME = "optimizer_readiness_report_v0_8.md"


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int | None = None) -> int | None:
    number = as_float(value, None)
    if number is None:
        return default
    return int(round(number))


def compact_dict(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def add_node(nodes: dict[str, dict[str, Any]], node: dict[str, Any]) -> None:
    node_id = node["node_id"]
    if node_id not in nodes:
        nodes[node_id] = node


def add_commodity(commodities: dict[str, dict[str, Any]], commodity: dict[str, Any]) -> None:
    commodity_id = commodity["commodity_id"]
    if commodity_id not in commodities:
        commodities[commodity_id] = commodity


def commodity_id(layer: str, raw_id: str) -> str:
    return f"{layer}:{raw_id}"


def route_cost(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        {
            "road_distance_km": as_float(row.get("road_distance_km") or row.get("distance_km")),
            "straight_line_km": as_float(row.get("straight_line_km")),
            "distance_nm": as_float(row.get("distance_nm")),
            "duration_min": as_float(row.get("duration_min")),
            "duration_hours_estimate": as_float(row.get("duration_hours_estimate")),
            "fuel_liters_per_trip": as_float(row.get("fuel_liters_per_trip")),
            "driver_hours_per_trip": as_float(row.get("driver_hours_per_trip")),
            "estimated_trip_cost_krw": as_float(row.get("estimated_trip_cost_krw")),
            "risk_score": as_float(row.get("risk_score") if row.get("risk_score") is not None else row.get("risk")),
        }
    )


def build_nodes(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}

    for item in dataset.get("factory_candidates", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "factory",
                    "name": item.get("company_name") or item.get("display_name"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "province": item.get("province"),
                    "city": item.get("city"),
                    "category": item.get("category"),
                    "capacity_units_30d": as_float(item.get("capacity_units_30d")),
                    "priority_role": item.get("priority_role"),
                    "priority_weight": as_float(item.get("priority_weight")),
                    "priority_site_label": item.get("priority_site_label"),
                    "priority_site_type": item.get("priority_site_type"),
                    "is_priority_assembly_seed": item.get("is_priority_assembly_seed"),
                    "is_core_operating_assembly": item.get("is_core_operating_assembly"),
                    "is_reserve_assembly_seed": item.get("is_reserve_assembly_seed"),
                    "assembly_operating_status": item.get("assembly_operating_status"),
                    "assembly_node_role": item.get("assembly_node_role"),
                    "capacity_confidence": as_float(
                        (item.get("factory_capacity_profile") or {}).get("capacity_confidence")
                    ),
                    "capacity_index": as_float((item.get("factory_capacity_profile") or {}).get("capacity_index")),
                    "capacity_tier": (item.get("factory_capacity_profile") or {}).get("capacity_tier"),
                    "recommended_role": (item.get("factory_capacity_profile") or {}).get("recommended_role"),
                    "nominal_daily_output_units": as_float(
                        (item.get("manufacturing_profile") or {}).get("nominal_daily_output_units")
                    ),
                    "surge_daily_output_units": as_float(
                        (item.get("manufacturing_profile") or {}).get("surge_daily_output_units")
                    ),
                    "setup_days_estimate": as_float((item.get("manufacturing_profile") or {}).get("setup_days_estimate")),
                    "grid_zone_id": (item.get("grid_risk_profile") or {}).get("grid_zone_id"),
                    "grid_dependency_score": as_float(
                        (item.get("grid_risk_profile") or {}).get("grid_dependency_score")
                    ),
                    "evidence_status": "public_candidate_with_proxy_capacity",
                    "verification_required": item.get("data_limitations"),
                }
            ),
        )

    for item in dataset.get("resource_candidates", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "domestic_resource",
                    "name": item.get("company_name") or item.get("display_name"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "province": item.get("province"),
                    "city": item.get("city"),
                    "resource_category": item.get("resource_category"),
                    "capacity_kg_30d": as_float(item.get("capacity_kg_30d")),
                    "confidence": as_float(item.get("confidence")),
                    "evidence_status": "public_resource_candidate_with_proxy_capacity",
                    "verification_required": item.get("data_limitations"),
                }
            ),
        )

    for item in dataset.get("assembly_hubs", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "assembly_hub",
                    "name": item.get("name"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "capacity_drones_30d": as_float(item.get("capacity_drones_30d")),
                    "accepted_categories": item.get("accepted_categories"),
                    "role": item.get("role"),
                }
            ),
        )

    for item in dataset.get("import_ports", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "import_port",
                    "name": item.get("name"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "coast": item.get("coast"),
                }
            ),
        )

    for item in dataset.get("foreign_material_sources", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "foreign_material_source",
                    "name": item.get("name"),
                    "country": item.get("country"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "material_ids": item.get("material_ids"),
                    "preferred_port_id": item.get("preferred_port_id"),
                    "monthly_capacity_kg": as_float(item.get("monthly_capacity_kg")),
                    "evidence_status": "synthetic_demo_import_source",
                }
            ),
        )

    for item in dataset.get("grid_risk_zones", []):
        add_node(
            nodes,
            compact_dict(
                {
                    "node_id": item.get("id"),
                    "node_type": "grid_risk_zone",
                    "name": item.get("name"),
                    "lat": as_float(item.get("lat")),
                    "lon": as_float(item.get("lon")),
                    "province": item.get("province"),
                    "precision_level": item.get("precision_level"),
                    "factory_count": as_int(item.get("factory_count")),
                    "grid_dependency_score": as_float(item.get("grid_dependency_score")),
                    "exposure_tier": item.get("exposure_tier"),
                    "evidence_status": "regional_proxy_not_exact_grid_dependency",
                }
            ),
        )

    return sorted(nodes.values(), key=lambda item: (item.get("node_type", ""), item.get("node_id", "")))


def build_commodities(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    commodities: dict[str, dict[str, Any]] = {}

    add_commodity(
        commodities,
        {
            "commodity_id": "drone:fpv_class_equivalent",
            "commodity_type": "finished_drone_equivalent",
            "label": "FPV-class equivalent drone output",
            "unit": "units",
            "safe_boundary": "Sustainment output count only; no payload or build instructions.",
        },
    )

    for raw_id, item in (dataset.get("part_categories") or {}).items():
        add_commodity(
            commodities,
            compact_dict(
                {
                    "commodity_id": commodity_id("part", raw_id),
                    "raw_id": raw_id,
                    "commodity_type": "part_family",
                    "label": item.get("label"),
                    "unit": "units",
                    "bom_quantity_per_drone": as_float(item.get("bom_quantity")),
                    "criticality": as_float(item.get("criticality")),
                }
            ),
        )

    for raw_id, item in (dataset.get("resource_categories") or {}).items():
        add_commodity(
            commodities,
            compact_dict(
                {
                    "commodity_id": commodity_id("resource", raw_id),
                    "raw_id": raw_id,
                    "commodity_type": "domestic_resource_feedstock",
                    "label": item.get("label"),
                    "unit": "kg",
                    "target_part_categories": item.get("target_part_categories"),
                    "base_capacity_kg_30d": as_float(item.get("base_capacity_kg_30d")),
                }
            ),
        )

    for raw_id, item in (dataset.get("component_catalog") or {}).items():
        add_commodity(
            commodities,
            compact_dict(
                {
                    "commodity_id": commodity_id("component", raw_id),
                    "raw_id": raw_id,
                    "commodity_type": "component",
                    "label": item.get("label"),
                    "unit": item.get("unit"),
                    "part_category": item.get("part_category"),
                    "base_units_per_drone": as_float(item.get("base_units_per_drone")),
                    "attrition_factor": as_float(item.get("attrition_factor")),
                    "localization_difficulty": item.get("localization_difficulty"),
                    "vulnerability": item.get("vulnerability"),
                    "verification_need": item.get("verification_need"),
                }
            ),
        )

    for raw_id, item in (dataset.get("subcomponent_catalog") or {}).items():
        add_commodity(
            commodities,
            compact_dict(
                {
                    "commodity_id": commodity_id("subcomponent", raw_id),
                    "raw_id": raw_id,
                    "commodity_type": "subcomponent",
                    "label": item.get("label"),
                    "unit": item.get("unit"),
                    "subcomponent_type": item.get("type"),
                    "import_dependency": item.get("import_dependency"),
                    "verification_need": item.get("verification_need"),
                }
            ),
        )

    for raw_id, item in (dataset.get("raw_material_catalog") or {}).items():
        add_commodity(
            commodities,
            compact_dict(
                {
                    "commodity_id": commodity_id("material", raw_id),
                    "raw_id": raw_id,
                    "commodity_type": "raw_material",
                    "label": item.get("label"),
                    "unit": item.get("unit"),
                    "feeds_part_categories": item.get("feeds_part_categories"),
                    "linked_resource_category": item.get("linked_resource_category"),
                    "import_dependency": item.get("import_dependency"),
                    "verification_need": item.get("verification_need"),
                }
            ),
        )

    return sorted(commodities.values(), key=lambda item: item["commodity_id"])


def build_edges(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    edges: dict[str, dict[str, Any]] = {}

    def add_edge(edge: dict[str, Any]) -> None:
        edge_id = edge["edge_id"]
        if edge_id not in edges:
            edges[edge_id] = edge

    for plan in dataset.get("plans", []):
        scenario_id = plan.get("id")

        for row in plan.get("selected_suppliers", []):
            if row.get("part_category") != "drone_assembly":
                continue
            add_edge(
                compact_dict(
                    {
                        "edge_id": f"onsite_final_assembly_{scenario_id}_{row.get('factory_id')}",
                        "scenario_id": scenario_id,
                        "edge_type": "priority_final_assembly_factory_onsite_output",
                        "origin_node_id": row.get("factory_id"),
                        "origin_node_type": "factory",
                        "destination_node_id": row.get("destination_factory_id") or row.get("factory_id"),
                        "destination_node_type": row.get("destination_type") or "priority_final_assembly_factory",
                        "destination_name": row.get("destination_name") or row.get("destination_factory_name"),
                        "commodity_id": commodity_id("part", row.get("part_category")),
                        "quantity": as_float(row.get("requested_quantity")),
                        "quantity_unit": "units_30d",
                        "status": row.get("status"),
                        "routing_provider": row.get("routing_provider"),
                        "routing_status": row.get("routing_status"),
                        "route_road_summary": row.get("route_road_summary"),
                        "cost": route_cost(row),
                        "evidence_status": "priority_final_assembly_factory_onsite_assignment",
                    }
                )
            )

        for row in plan.get("route_segments", []):
            add_edge(
                compact_dict(
                    {
                        "edge_id": row.get("id"),
                        "scenario_id": scenario_id,
                        "edge_type": "component_factory_to_priority_assembly_factory",
                        "origin_node_id": row.get("factory_id"),
                        "origin_node_type": "factory",
                        "destination_node_id": row.get("destination_factory_id") or row.get("hub_id"),
                        "destination_node_type": row.get("destination_type") or "priority_final_assembly_factory",
                        "destination_name": row.get("destination_name") or row.get("destination_factory_name") or row.get("hub_name"),
                        "commodity_id": commodity_id("part", row.get("part_category")),
                        "quantity": as_float(row.get("quantity")),
                        "quantity_unit": "units_30d",
                        "status": row.get("status"),
                        "routing_provider": row.get("routing_provider"),
                        "routing_status": row.get("routing_status"),
                        "route_road_summary": row.get("route_road_summary"),
                        "cost": route_cost(row),
                        "evidence_status": "generated_route_with_osrm_or_estimate",
                    }
                )
            )

        for row in plan.get("resource_route_segments", []):
            add_edge(
                compact_dict(
                    {
                        "edge_id": row.get("id"),
                        "scenario_id": scenario_id,
                        "edge_type": "domestic_resource_to_factory",
                        "origin_node_id": row.get("resource_id"),
                        "origin_node_type": "domestic_resource",
                        "destination_node_id": row.get("target_factory_id"),
                        "destination_node_type": "factory",
                        "commodity_id": commodity_id("resource", row.get("resource_category")),
                        "feeds_part_commodity_id": commodity_id("part", row.get("target_part_category")),
                        "quantity": as_float(row.get("quantity_kg_30d")),
                        "quantity_unit": "kg_30d",
                        "status": row.get("status"),
                        "routing_provider": row.get("routing_provider"),
                        "routing_status": row.get("routing_status"),
                        "route_road_summary": row.get("route_road_summary"),
                        "cost": route_cost(row),
                        "evidence_status": "generated_route_with_osrm_or_estimate",
                    }
                )
            )

        for row in plan.get("maritime_import_route_segments", []):
            material_ids = row.get("material_ids") or []
            if not material_ids:
                material_ids = ["unknown_material"]
            for material_id in material_ids:
                add_edge(
                    compact_dict(
                        {
                            "edge_id": f"{row.get('id')}::{material_id}",
                            "source_route_id": row.get("id"),
                            "scenario_id": scenario_id,
                            "edge_type": "maritime_import",
                            "origin_node_id": row.get("source_id"),
                            "origin_node_type": "foreign_material_source",
                            "destination_node_id": row.get("destination_port_id"),
                            "destination_node_type": "import_port",
                            "commodity_id": commodity_id("material", material_id),
                            "quantity": as_float(row.get("import_capacity_kg_30d")),
                            "quantity_unit": "kg_30d",
                            "status": row.get("status"),
                            "routing_provider": "D4D maritime corridor estimate",
                            "routing_status": row.get("routing_status"),
                            "cost": route_cost(row),
                            "evidence_status": "synthetic_maritime_corridor_demo",
                        }
                    )
                )

        for row in plan.get("port_to_factory_material_routes", []):
            add_edge(
                compact_dict(
                    {
                        "edge_id": row.get("id"),
                        "scenario_id": scenario_id,
                        "edge_type": "port_to_factory_material",
                        "origin_node_id": row.get("port_id"),
                        "origin_node_type": "import_port",
                        "destination_node_id": row.get("target_factory_id"),
                        "destination_node_type": "factory",
                        "commodity_id": commodity_id("material", row.get("material_id")),
                        "feeds_part_commodity_id": commodity_id("part", row.get("target_part_category")),
                        "quantity": as_float(row.get("quantity_kg_30d")),
                        "quantity_unit": "kg_30d",
                        "status": row.get("status"),
                        "routing_provider": row.get("routing_provider"),
                        "routing_status": row.get("routing_status"),
                        "route_road_summary": row.get("route_road_summary"),
                        "cost": route_cost(row),
                        "evidence_status": "generated_route_with_osrm_or_estimate",
                    }
                )
            )

    return sorted(edges.values(), key=lambda item: (item.get("scenario_id", ""), item.get("edge_type", ""), item["edge_id"]))


def build_demands(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    demands: list[dict[str, Any]] = []

    for plan in dataset.get("plans", []):
        scenario_id = plan.get("id")
        demands.append(
            {
                "demand_id": f"{scenario_id}:drone_output:30d",
                "scenario_id": scenario_id,
                "commodity_id": "drone:fpv_class_equivalent",
                "quantity": as_float(plan.get("target_drones")),
                "quantity_unit": "units_30d",
                "demand_basis": "scenario_target_drones",
            }
        )

        for row in plan.get("category_summary", []):
            demands.append(
                compact_dict(
                    {
                        "demand_id": f"{scenario_id}:part:{row.get('part_category')}:30d",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("part", row.get("part_category")),
                        "quantity": as_float(row.get("required_units")),
                        "quantity_unit": "units_30d",
                        "allocated_quantity": as_float(row.get("allocated_units")),
                        "coverage_ratio": as_float(row.get("coverage_ratio")),
                        "demand_basis": "part_bom_expansion",
                    }
                )
            )

        for row in plan.get("raw_material_supply_summary", []):
            demands.append(
                compact_dict(
                    {
                        "demand_id": f"{scenario_id}:material:{row.get('material_id')}:30d",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("material", row.get("material_id")),
                        "quantity": as_float(row.get("required_kg_30d")),
                        "quantity_unit": "kg_30d",
                        "coverage_ratio": as_float(row.get("coverage_ratio")),
                        "shortage_quantity": as_float(row.get("shortage_kg_30d")),
                        "demand_basis": "weighted_material_requirement",
                    }
                )
            )

        for row in plan.get("component_survival_summary", []):
            demands.append(
                compact_dict(
                    {
                        "demand_id": f"{scenario_id}:component:{row.get('component_id')}:daily",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("component", row.get("component_id")),
                        "quantity": as_float(row.get("daily_demand_units")),
                        "quantity_unit": f"{row.get('unit', 'units')}_per_day",
                        "demand_basis": "blockade_daily_consumption",
                    }
                )
            )

        for row in plan.get("subcomponent_survival_summary", []):
            demands.append(
                compact_dict(
                    {
                        "demand_id": f"{scenario_id}:subcomponent:{row.get('subcomponent_id')}:daily",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("subcomponent", row.get("subcomponent_id")),
                        "quantity": as_float(row.get("daily_demand_units")),
                        "quantity_unit": f"{row.get('unit', 'units')}_per_day",
                        "demand_basis": "blockade_daily_consumption_deep_constraint",
                    }
                )
            )

    return demands


def build_capacities(dataset: dict[str, Any], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    capacities: list[dict[str, Any]] = []

    for item in dataset.get("factory_candidates", []):
        profile = item.get("factory_capacity_profile") or {}
        manufacturing = item.get("manufacturing_profile") or {}
        capacities.append(
            compact_dict(
                {
                    "capacity_id": f"factory:{item.get('id')}:{item.get('category')}:30d",
                    "capacity_type": "factory_output_proxy",
                    "node_id": item.get("id"),
                    "commodity_id": commodity_id("part", item.get("category")),
                    "quantity": as_float(profile.get("predicted_output_units_30d") or item.get("capacity_units_30d")),
                    "quantity_unit": "units_30d",
                    "nominal_daily_output_units": as_float(manufacturing.get("nominal_daily_output_units")),
                    "surge_daily_output_units": as_float(manufacturing.get("surge_daily_output_units")),
                    "setup_days_estimate": as_float(manufacturing.get("setup_days_estimate")),
                    "min_batch_units": as_float(manufacturing.get("min_batch_units")),
                    "estimated_yield_rate": as_float(manufacturing.get("estimated_yield_rate")),
                    "confidence": as_float(profile.get("capacity_confidence")),
                    "evidence_status": "proxy_capacity_not_verified_mobilization_capacity",
                }
            )
        )

    for item in dataset.get("resource_candidates", []):
        capacities.append(
            compact_dict(
                {
                    "capacity_id": f"resource:{item.get('id')}:{item.get('resource_category')}:30d",
                    "capacity_type": "domestic_resource_supply_proxy",
                    "node_id": item.get("id"),
                    "commodity_id": commodity_id("resource", item.get("resource_category")),
                    "quantity": as_float(item.get("capacity_kg_30d")),
                    "quantity_unit": "kg_30d",
                    "confidence": as_float(item.get("confidence")),
                    "evidence_status": "proxy_resource_capacity_requires_verification",
                }
            )
        )

    for item in dataset.get("assembly_hubs", []):
        capacities.append(
            compact_dict(
                {
                    "capacity_id": f"hub:{item.get('id')}:drone_output:30d",
                    "capacity_type": "assembly_hub_capacity",
                    "node_id": item.get("id"),
                    "commodity_id": "drone:fpv_class_equivalent",
                    "quantity": as_float(item.get("capacity_drones_30d")),
                    "quantity_unit": "units_30d",
                    "evidence_status": "synthetic_demo_hub_capacity",
                }
            )
        )

    for plan in dataset.get("plans", []):
        scenario_id = plan.get("id")

        for row in plan.get("raw_material_supply_summary", []):
            capacities.append(
                compact_dict(
                    {
                        "capacity_id": f"{scenario_id}:material:{row.get('material_id')}:available_30d",
                        "capacity_type": "scenario_material_available",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("material", row.get("material_id")),
                        "quantity": as_float(row.get("total_available_kg_30d")),
                        "quantity_unit": "kg_30d",
                        "domestic_resource_supply_kg": as_float(row.get("domestic_resource_supply_kg")),
                        "import_supply_kg_30d": as_float(row.get("import_supply_kg_30d")),
                        "existing_factory_inventory_kg": as_float(row.get("existing_factory_inventory_kg")),
                        "evidence_status": "synthetic_material_supply_assumption",
                    }
                )
            )

        for row in plan.get("component_survival_summary", []):
            capacities.append(
                compact_dict(
                    {
                        "capacity_id": f"{scenario_id}:component:{row.get('component_id')}:domestic_daily",
                        "capacity_type": "component_daily_domestic_line_capacity",
                        "scenario_id": scenario_id,
                        "commodity_id": commodity_id("component", row.get("component_id")),
                        "quantity": as_float(row.get("domestic_line_capacity_units_per_day")),
                        "quantity_unit": f"{row.get('unit', 'units')}_per_day",
                        "pre_ramp_output_per_day": as_float(row.get("domestic_output_before_ramp_units_per_day")),
                        "ramp_ready_day": as_int(row.get("ramp_ready_day")),
                        "evidence_status": "synthetic_component_ramp_assumption",
                    }
                )
            )

    for edge in edges:
        if edge.get("quantity") is None:
            continue
        capacities.append(
            compact_dict(
                {
                    "capacity_id": f"edge:{edge['edge_id']}",
                    "capacity_type": "edge_flow_upper_bound_proxy",
                    "scenario_id": edge.get("scenario_id"),
                    "edge_id": edge["edge_id"],
                    "commodity_id": edge.get("commodity_id"),
                    "quantity": edge.get("quantity"),
                    "quantity_unit": edge.get("quantity_unit"),
                    "evidence_status": "current_generated_flow_used_as_proxy_capacity_until_vehicle_capacity_is_connected",
                }
            )
        )

    return capacities


def build_state(dataset: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "inventory_wip": dataset.get("inventory_wip", []),
        "frozen_orders": dataset.get("frozen_orders", []),
        "in_transit_shipments": dataset.get("in_transit_shipments", []),
    }


def build_constraints(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []

    for item in dataset.get("bom", []):
        constraints.append(
            compact_dict(
                {
                    "constraint_id": f"bom:drone:{item.get('part_category')}",
                    "constraint_type": "part_bom_per_drone",
                    "lhs_commodity_id": commodity_id("part", item.get("part_category")),
                    "rhs_commodity_id": "drone:fpv_class_equivalent",
                    "coefficient": as_float(item.get("quantity_per_drone")),
                    "criticality": as_float(item.get("criticality")),
                    "safe_demo_note": item.get("safe_demo_note"),
                }
            )
        )

    for component_id, sub_map in (dataset.get("component_subcomponent_bom") or {}).items():
        for subcomponent_id, quantity in (sub_map or {}).items():
            constraints.append(
                compact_dict(
                    {
                        "constraint_id": f"subbom:{component_id}:{subcomponent_id}",
                        "constraint_type": "component_subcomponent_bom",
                        "lhs_commodity_id": commodity_id("subcomponent", subcomponent_id),
                        "rhs_commodity_id": commodity_id("component", component_id),
                        "coefficient": as_float(quantity),
                    }
                )
            )

    for plan in dataset.get("plans", []):
        scenario_id = plan.get("id")
        for row in plan.get("component_survival_summary", []):
            survival = row.get("survival_days") or {}
            constraints.append(
                compact_dict(
                    {
                        "constraint_id": f"{scenario_id}:survival:component:{row.get('component_id')}",
                        "scenario_id": scenario_id,
                        "constraint_type": "component_blockade_survival",
                        "commodity_id": commodity_id("component", row.get("component_id")),
                        "daily_demand_units": as_float(row.get("daily_demand_units")),
                        "effective_inventory_units": as_float(row.get("effective_inventory_units")),
                        "net_burn_units_per_day": as_float(row.get("net_burn_units_per_day")),
                        "survival_days_likely": as_float(survival.get("likely")),
                        "ramp_ready_day": as_int(row.get("ramp_ready_day")),
                        "ramp_gap_days": as_float(row.get("ramp_gap_days")),
                        "is_bottleneck": bool(row.get("is_bottleneck")),
                    }
                )
            )

        for row in plan.get("subcomponent_survival_summary", []):
            survival = row.get("survival_days") or {}
            constraints.append(
                compact_dict(
                    {
                        "constraint_id": f"{scenario_id}:survival:subcomponent:{row.get('subcomponent_id')}",
                        "scenario_id": scenario_id,
                        "constraint_type": "subcomponent_blockade_survival",
                        "commodity_id": commodity_id("subcomponent", row.get("subcomponent_id")),
                        "daily_demand_units": as_float(row.get("daily_demand_units")),
                        "effective_inventory_units": as_float(row.get("effective_inventory_units")),
                        "net_burn_units_per_day": as_float(row.get("net_burn_units_per_day")),
                        "survival_days_likely": as_float(survival.get("likely")),
                        "import_dependency": row.get("import_dependency"),
                    }
                )
            )

    for row in dataset.get("frozen_orders", []):
        constraints.append(
            compact_dict(
                {
                    "constraint_id": f"frozen:{row.get('id')}",
                    "constraint_type": "frozen_order_commitment",
                    "source_plan_id": row.get("source_plan_id"),
                    "factory_id": row.get("factory_id"),
                    "hub_id": row.get("hub_id"),
                    "destination_type": row.get("destination_type"),
                    "destination_factory_id": row.get("destination_factory_id"),
                    "destination_name": row.get("destination_name"),
                    "commodity_id": commodity_id("part", row.get("part_category")),
                    "quantity": as_float(row.get("frozen_quantity_units")),
                    "quantity_unit": "units",
                    "freeze_until_day": as_int(row.get("freeze_until_day")),
                    "cancelability": row.get("cancelability"),
                    "decision_rule": row.get("decision_rule"),
                }
            )
        )

    for row in dataset.get("grid_disruption_scenarios", []):
        constraints.append(
            compact_dict(
                {
                    "constraint_id": f"grid:{row.get('id')}",
                    "constraint_type": "grid_disruption_capacity_multiplier",
                    "scenario_name": row.get("name"),
                    "affected_factory_count": as_int(row.get("affected_factory_count")),
                    "assumed_availability_multiplier": as_float(row.get("assumed_availability_multiplier")),
                    "capacity_units_30d_at_risk": as_float(row.get("capacity_units_30d_at_risk")),
                    "part_family_exposure": row.get("part_family_exposure"),
                }
            )
        )

    return constraints


def build_scenario_parameters(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for plan in dataset.get("plans", []):
        headline = plan.get("blockade_survival_headline") or {}
        survival = headline.get("survival_days") or {}
        valley = headline.get("valley") or {}
        rows.append(
            compact_dict(
                {
                    "scenario_id": plan.get("id"),
                    "name": plan.get("name"),
                    "target_drones_30d": as_float(plan.get("target_drones")),
                    "possible_drones_30d": as_float(plan.get("possible_drones_30d")),
                    "threat": plan.get("threat"),
                    "bottleneck_part_category": plan.get("bottleneck_part_category"),
                    "bottleneck_coverage_ratio": as_float(plan.get("bottleneck_coverage_ratio")),
                    "blockade_survival_days_likely": as_float(survival.get("likely")),
                    "blockade_total_producible_likely": as_float(
                        (headline.get("blockade_total_producible") or {}).get("likely")
                    ),
                    "valley_start_day": as_int(valley.get("start_day")),
                    "valley_end_day": as_int(valley.get("end_day")),
                    "valley_depth_units_per_day": as_float(valley.get("depth_units_per_day")),
                    "component_bottleneck": (headline.get("bottleneck") or {}).get("id"),
                    "subcomponent_bottleneck": (headline.get("subcomponent_bottleneck") or {}).get("id"),
                }
            )
        )
    return rows


def build_cost_parameters(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "logistics_cost_model": dataset.get("logistics_cost_model"),
        "objective_terms": [
            "shortage_penalty",
            "logistics_cost",
            "route_risk_penalty",
            "grid_risk_penalty",
            "ramp_gap_penalty",
            "switching_cost_penalty_future",
        ],
        "recommended_objective_order": [
            "minimize_unmet_mission_output",
            "minimize_deep_component_or_subcomponent_stockout",
            "minimize_ramp_up_valley",
            "minimize_route_and_driver_cost",
            "minimize_grid_and_route_risk",
        ],
    }


def validate_optimizer_input(payload: dict[str, Any]) -> dict[str, Any]:
    node_ids = {row["node_id"] for row in payload["nodes"]}
    commodity_ids = {row["commodity_id"] for row in payload["commodities"]}
    edge_ids = {row["edge_id"] for row in payload["edges"]}
    scenario_ids = {row["scenario_id"] for row in payload["scenario_parameters"]}

    errors: list[str] = []
    warnings: list[str] = []

    for edge in payload["edges"]:
        if edge.get("origin_node_id") not in node_ids:
            errors.append(f"edge {edge['edge_id']} origin node missing: {edge.get('origin_node_id')}")
        if edge.get("destination_node_id") not in node_ids:
            errors.append(f"edge {edge['edge_id']} destination node missing: {edge.get('destination_node_id')}")
        if edge.get("commodity_id") not in commodity_ids:
            errors.append(f"edge {edge['edge_id']} commodity missing: {edge.get('commodity_id')}")

    for demand in payload["demands"]:
        if demand.get("commodity_id") not in commodity_ids:
            errors.append(f"demand {demand['demand_id']} commodity missing: {demand.get('commodity_id')}")
        if demand.get("scenario_id") not in scenario_ids:
            errors.append(f"demand {demand['demand_id']} scenario missing: {demand.get('scenario_id')}")

    for capacity in payload["capacities"]:
        if capacity.get("commodity_id") and capacity.get("commodity_id") not in commodity_ids:
            errors.append(f"capacity {capacity['capacity_id']} commodity missing: {capacity.get('commodity_id')}")
        if capacity.get("edge_id") and capacity.get("edge_id") not in edge_ids:
            errors.append(f"capacity {capacity['capacity_id']} edge missing: {capacity.get('edge_id')}")
        if capacity.get("node_id") and capacity.get("node_id") not in node_ids:
            errors.append(f"capacity {capacity['capacity_id']} node missing: {capacity.get('node_id')}")

    state = payload.get("state", {})
    synthetic_state_rows = sum(
        1
        for rows in state.values()
        for row in rows
        if "synthetic" in str(row.get("data_status", "")).lower()
    )
    if synthetic_state_rows:
        warnings.append(f"{synthetic_state_rows} operating-state rows are synthetic placeholders.")

    edge_proxy_caps = sum(
        1 for row in payload["capacities"] if row.get("capacity_type") == "edge_flow_upper_bound_proxy"
    )
    if edge_proxy_caps:
        warnings.append(f"{edge_proxy_caps} edge capacities currently use generated flow as a proxy.")

    factory_proxy_caps = sum(
        1 for row in payload["capacities"] if row.get("capacity_type") == "factory_output_proxy"
    )
    if factory_proxy_caps:
        warnings.append(f"{factory_proxy_caps} factory capacities are public-data proxies, not verified spare capacity.")

    status = "pass" if not errors and not warnings else "pass_with_warnings" if not errors else "fail"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "nodes": len(payload["nodes"]),
            "edges": len(payload["edges"]),
            "commodities": len(payload["commodities"]),
            "demands": len(payload["demands"]),
            "capacities": len(payload["capacities"]),
            "constraints": len(payload["constraints"]),
            "inventory_wip": len(state.get("inventory_wip", [])),
            "frozen_orders": len(state.get("frozen_orders", [])),
            "in_transit_shipments": len(state.get("in_transit_shipments", [])),
        },
    }


def build_readiness_report(payload: dict[str, Any]) -> str:
    validation = payload["validation"]
    scenarios = payload["scenario_parameters"]
    counts = validation["counts"]
    lines = [
        "# Drone Optimizer Input v0.8 Readiness Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Source dataset: `{payload['source_dataset_schema']}`",
        f"Validation status: `{validation['status']}`",
        "",
        "## Artifact Counts",
        "",
        "| Artifact | Count |",
        "| --- | ---: |",
    ]
    for key in ["nodes", "edges", "commodities", "demands", "capacities", "constraints", "inventory_wip", "frozen_orders", "in_transit_shipments"]:
        lines.append(f"| `{key}` | {counts.get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Scenario Dry Run",
            "",
            "| Scenario | Target 30d | Possible 30d | Bottleneck | Survival likely | Valley |",
            "| --- | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for row in scenarios:
        valley = f"D+{row.get('valley_start_day')}-D+{row.get('valley_end_day')}"
        lines.append(
            "| {scenario_id} | {target:.0f} | {possible:.0f} | {bottleneck} | {survival:.1f}d | {valley} |".format(
                scenario_id=row.get("scenario_id"),
                target=row.get("target_drones_30d") or 0,
                possible=row.get("possible_drones_30d") or 0,
                bottleneck=row.get("component_bottleneck") or row.get("bottleneck_part_category") or "-",
                survival=row.get("blockade_survival_days_likely") or 0,
                valley=valley,
            )
        )

    lines.extend(["", "## Warnings", ""])
    if validation["warnings"]:
        for warning in validation["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Solver Readiness Judgment",
            "",
            "- Ready for v0.9 deterministic allocation/min-cost-flow prototype.",
            "- Not yet sufficient for operational MILP without verified live capacity, vehicle fleet, route capacity, ERP/MES inventory, and supplier-contract feeds.",
            "- Use `state.frozen_orders` and `state.in_transit_shipments` as hard constraints in the next solver iteration.",
            "- Treat edge capacities as temporary upper-bound proxies until a vehicle/driver/route-throughput model is connected.",
            "",
        ]
    )
    return "\n".join(lines)


def build_optimizer_input(dataset: dict[str, Any]) -> dict[str, Any]:
    nodes = build_nodes(dataset)
    commodities = build_commodities(dataset)
    edges = build_edges(dataset)
    payload = {
        "schema": "d4d.drone_optimizer_input.v0.8",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset_schema": dataset.get("schema"),
        "source_dataset_generated_at": dataset.get("generated_at"),
        "safety_boundary": dataset.get("scenario", {}).get("safety_boundary"),
        "notes": [
            "Solver-normalized input only; this artifact does not solve allocation yet.",
            "All public-data capacity values remain evidence-weighted proxies.",
            "Synthetic inventory, WIP, frozen-order, and in-transit rows must be replaced by ERP/MES/TMS feeds for production use.",
        ],
        "nodes": nodes,
        "edges": edges,
        "commodities": commodities,
        "demands": build_demands(dataset),
        "capacities": build_capacities(dataset, edges),
        "state": build_state(dataset),
        "constraints": build_constraints(dataset),
        "scenario_parameters": build_scenario_parameters(dataset),
        "cost_parameters": build_cost_parameters(dataset),
        "source_files": {
            "dataset": str(DATASET_PATH.relative_to(ROOT)),
            "component_survival_csv": str((APP_DATA_DIR / "component_survival_backdata.csv").relative_to(ROOT)),
            "subcomponent_constraints_csv": str((APP_DATA_DIR / "subcomponent_constraints.csv").relative_to(ROOT)),
            "logistics_edges_csv": str((APP_DATA_DIR / "logistics_route_edges.csv").relative_to(ROOT)),
            "factory_operational_state_csv": str((APP_DATA_DIR / "factory_operational_state.csv").relative_to(ROOT)),
        },
    }
    payload["validation"] = validate_optimizer_input(payload)
    return payload


def main() -> None:
    dataset = load_json(DATASET_PATH)
    payload = build_optimizer_input(dataset)
    report = build_readiness_report(payload)

    for directory in (APP_DATA_DIR, SAMPLE_DATA_DIR):
        write_json(directory / OUTPUT_NAME, payload)
        write_text(directory / REPORT_NAME, report)

    summary = {
        "schema": payload["schema"],
        "validation_status": payload["validation"]["status"],
        "counts": payload["validation"]["counts"],
        "warnings": payload["validation"]["warnings"],
        "outputs": [str((APP_DATA_DIR / OUTPUT_NAME).relative_to(ROOT)), str((APP_DATA_DIR / REPORT_NAME).relative_to(ROOT))],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if payload["validation"]["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

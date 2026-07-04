#!/usr/bin/env python3
"""Generate a safe public-data demo dataset for wartime drone production conversion.

The source is the public Korea Industrial Complex Corporation factory registry
file on data.go.kr. The resulting demo dataset is intentionally a candidate
matching dataset, not a verified mobilization or military-production list.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "03_data" / "samples" / "drone_production_conversion"
RAW_DIR = ROOT / "03_data" / "raw" / "drone_production_conversion"
APP_DATA_DIR = ROOT / "06_prototype" / "app" / "drone_production_conversion" / "data"

SOURCE_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000003109845&fileDetailSn=1&insertDataPrcus=N"
)

RAW_CSV = RAW_DIR / "factory_registry_public_snapshot.csv"
ROUTE_CACHE_JSON = RAW_DIR / "road_route_cache_osrm.json"
CAPACITY_DIR = RAW_DIR / "capacity"
NATIONAL_FACTORY_CAPACITY_CSV = CAPACITY_DIR / "national_registered_factories_20200229.csv"
FACTORYON_EMPLOYEE_XLSX = CAPACITY_DIR / "factoryon_employee_20210731.xlsx"
ENERGY_DIR = RAW_DIR / "energy"
GRID_DIR = RAW_DIR / "grid"
LARGE_ENERGY_USERS_XLSX = ENERGY_DIR / "large_energy_users.xlsx"
NGMS_EMISSIONS_CSV = ENERGY_DIR / "ngms_emissions_public.csv"
KEPCO_LARGE_CUSTOMER_CSV = GRID_DIR / "kepco_large_customer_general_info.csv"
DATASET_JSON = DATA_DIR / "drone_production_conversion_dataset.json"
CAPACITY_BACKDATA_CSV = DATA_DIR / "factory_capacity_backdata.csv"
FULL_CANDIDATE_CAPACITY_BACKDATA_CSV = DATA_DIR / "full_factory_candidate_capacity_backdata.csv"
PIPELINE_CANDIDATE_SHORTLIST_CSV = DATA_DIR / "factory_pipeline_candidate_shortlist.csv"
ROUTE_CAPACITY_EDGES_CSV = DATA_DIR / "factory_route_capacity_edges.csv"
LOGISTICS_ROUTE_EDGES_CSV = DATA_DIR / "logistics_route_edges.csv"
MATERIAL_SUPPLY_BACKDATA_CSV = DATA_DIR / "material_supply_backdata.csv"
MATERIAL_IMPORT_ROUTES_CSV = DATA_DIR / "material_import_routes.csv"
COMPONENT_SURVIVAL_CSV = DATA_DIR / "component_survival_backdata.csv"
SUBCOMPONENT_CONSTRAINTS_CSV = DATA_DIR / "subcomponent_constraints.csv"
BLOCKADE_PHASE_CURVE_CSV = DATA_DIR / "blockade_phase_curve.csv"
ALLIED_SUPPLY_SOURCES_CSV = DATA_DIR / "allied_supply_sources.csv"
GRID_RISK_ZONES_CSV = DATA_DIR / "grid_risk_zones.csv"
OPERATIONAL_STATE_CSV = DATA_DIR / "factory_operational_state.csv"
APP_JSON = APP_DATA_DIR / "drone_production_conversion_dataset.json"
APP_JS = APP_DATA_DIR / "drone_production_conversion_dataset.js"
APP_CAPACITY_BACKDATA_CSV = APP_DATA_DIR / "factory_capacity_backdata.csv"
APP_FULL_CANDIDATE_CAPACITY_BACKDATA_CSV = APP_DATA_DIR / "full_factory_candidate_capacity_backdata.csv"
APP_PIPELINE_CANDIDATE_SHORTLIST_CSV = APP_DATA_DIR / "factory_pipeline_candidate_shortlist.csv"
APP_ROUTE_CAPACITY_EDGES_CSV = APP_DATA_DIR / "factory_route_capacity_edges.csv"
APP_LOGISTICS_ROUTE_EDGES_CSV = APP_DATA_DIR / "logistics_route_edges.csv"
APP_MATERIAL_SUPPLY_BACKDATA_CSV = APP_DATA_DIR / "material_supply_backdata.csv"
APP_MATERIAL_IMPORT_ROUTES_CSV = APP_DATA_DIR / "material_import_routes.csv"
APP_COMPONENT_SURVIVAL_CSV = APP_DATA_DIR / "component_survival_backdata.csv"
APP_SUBCOMPONENT_CONSTRAINTS_CSV = APP_DATA_DIR / "subcomponent_constraints.csv"
APP_BLOCKADE_PHASE_CURVE_CSV = APP_DATA_DIR / "blockade_phase_curve.csv"
APP_ALLIED_SUPPLY_SOURCES_CSV = APP_DATA_DIR / "allied_supply_sources.csv"
APP_GRID_RISK_ZONES_CSV = APP_DATA_DIR / "grid_risk_zones.csv"
APP_OPERATIONAL_STATE_CSV = APP_DATA_DIR / "factory_operational_state.csv"
ROUTE_PROVIDER = os.environ.get("D4D_ROUTE_PROVIDER", "osrm").strip().lower()
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving"

LARGE_ENERGY_USERS_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000003650972&fileDetailSn=1&insertDataPrcus=N"
)
NGMS_EMISSIONS_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000003253502&fileDetailSn=1&insertDataPrcus=N"
)
NATIONAL_FACTORY_CAPACITY_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000003557086&fileDetailSn=1&insertDataPrcus=N"
)
FACTORYON_EMPLOYEE_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000002440492&fileDetailSn=1&insertDataPrcus=N"
)
KEPCO_LARGE_CUSTOMER_URL = (
    "https://www.data.go.kr/cmm/cmm/fileDownload.do?"
    "atchFileId=FILE_000000002339213&fileDetailSn=1&insertDataPrcus=N"
)


PART_CATEGORIES = {
    "drone_assembly": {
        "label": "Drone / Final Assembly",
        "short_label": "Assembly",
        "color": "#245b7a",
        "keywords": ["드론", "무인기", "무인항공", "UAV", "uav"],
        "role": "final assembly, integration, flight-test coordination",
        "bom_quantity": 1,
        "criticality": 0.95,
        "base_capacity": 260,
    },
    "flight_stack": {
        "label": "Flight Stack / Electronics",
        "short_label": "Flight Stack",
        "color": "#7a4b9d",
        "keywords": ["PCB", "피씨비", "회로", "인쇄회로", "전자부품", "SMT", "제어기", "통신장비"],
        "role": "PCB, embedded control, communications electronics",
        "bom_quantity": 1,
        "criticality": 0.98,
        "base_capacity": 950,
    },
    "power": {
        "label": "Battery / Power",
        "short_label": "Power",
        "color": "#b55b2c",
        "keywords": ["배터리", "밧데리", "전지", "리튬", "전원공급", "충전기"],
        "role": "battery pack, charger, power management",
        "bom_quantity": 1,
        "criticality": 0.99,
        "base_capacity": 720,
    },
    "propulsion": {
        "label": "Motor / Propulsion",
        "short_label": "Propulsion",
        "color": "#2f7c4f",
        "keywords": ["모터", "BLDC", "프로펠러", "프롭", "감속기", "구동장치"],
        "role": "motors, rotors, drive components",
        "bom_quantity": 4,
        "criticality": 0.9,
        "base_capacity": 2300,
    },
    "sensor_payload": {
        "label": "Sensor / Camera",
        "short_label": "Sensor",
        "color": "#5b6ea8",
        "keywords": ["카메라", "렌즈", "광학", "CCTV", "영상", "센서", "열화상", "적외선"],
        "role": "camera, optics, sensing payload",
        "bom_quantity": 1,
        "criticality": 0.78,
        "base_capacity": 1100,
    },
    "airframe": {
        "label": "Airframe / Materials",
        "short_label": "Airframe",
        "color": "#9a6a22",
        "keywords": ["탄소", "카본", "복합재", "알루미늄", "프레임", "사출", "금형", "플라스틱"],
        "role": "frame, molded/composite parts, brackets",
        "bom_quantity": 1,
        "criticality": 0.72,
        "base_capacity": 1450,
    },
    "harness": {
        "label": "Harness / Connector",
        "short_label": "Harness",
        "color": "#8b3d55",
        "keywords": ["케이블", "하네스", "커넥터", "전선"],
        "role": "wiring harnesses, connectors, cable assemblies",
        "bom_quantity": 1,
        "criticality": 0.66,
        "base_capacity": 1300,
    },
    "qa_packaging": {
        "label": "Test / Packaging",
        "short_label": "QA",
        "color": "#546061",
        "keywords": ["시험", "검사", "계측", "측정", "포장", "케이스", "상자"],
        "role": "testing, packaging, transport cases",
        "bom_quantity": 1,
        "criticality": 0.58,
        "base_capacity": 1800,
    },
}

RESOURCE_CATEGORIES = {
    "rare_earth_magnet_recovery": {
        "label": "Rare-earth / Magnet Feedstock",
        "short_label": "NdFeB / Magnet",
        "color": "#1f8a84",
        "keywords": ["희토", "네오디", "디스프로", "터븀", "란탄", "세륨", "영구자석", "자석", "마그네트", "페라이트"],
        "role": "magnet makers, magnet-applied equipment, and possible NdFeB recovery/sorting candidates",
        "target_part_categories": ["propulsion"],
        "base_capacity_kg_30d": 900,
    },
    "battery_material_recovery": {
        "label": "Battery Material / Cell Recovery",
        "short_label": "Battery Material",
        "color": "#c05a35",
        "keywords": ["폐배터리", "폐전지", "배터리", "밧데리", "축전지", "리튬", "전지", "재활용"],
        "role": "battery/cell material supply and recycling candidates for emergency power-pack continuity",
        "target_part_categories": ["power"],
        "base_capacity_kg_30d": 1300,
    },
    "metal_electronics_recycling": {
        "label": "Urban Mining / E-waste Metals",
        "short_label": "Urban Mining",
        "color": "#5f6f2e",
        "keywords": ["재활용", "리사이클", "폐전자", "전자스크랩", "스크랩", "비철금속", "폐금속", "금속재생", "고철", "동스크랩", "재생"],
        "role": "PCB, connector, copper, and non-ferrous metal recycling candidates",
        "target_part_categories": ["flight_stack", "harness"],
        "base_capacity_kg_30d": 1800,
    },
    "carbon_composite_supply": {
        "label": "Composite / Light-metal Feedstock",
        "short_label": "Composite",
        "color": "#7d6342",
        "keywords": ["탄소섬유", "카본", "복합재", "알루미늄", "알미늄", "플라스틱재생", "재생플라스틱"],
        "role": "airframe feedstock candidates for frames, brackets, and protective housings",
        "target_part_categories": ["airframe"],
        "base_capacity_kg_30d": 1600,
    },
}

MATERIAL_REQUIREMENTS = [
    {
        "material_id": "ndfeb_magnet_feedstock",
        "label": "NdFeB-class magnet feedstock",
        "feeds_part_category": "propulsion",
        "linked_bom_item": "4 motor / propulsion sets per drone",
        "demo_basis": "드론 모터의 영구자석 공급 리스크를 상위 자원 단위로 모델링합니다. 실제 자석 질량과 합금비는 제품별 검증 대상입니다.",
        "verification_need": "폐영구자석, 모터 스크랩, 자석 제조/가공 업체의 회수 가능량과 품질 등급 검증",
    },
    {
        "material_id": "lithium_battery_feedstock",
        "label": "Battery cell and lithium material feedstock",
        "feeds_part_category": "power",
        "linked_bom_item": "1 battery / power pack per drone",
        "demo_basis": "배터리 셀 또는 폐전지 재자원화 후보를 전력 부품군의 선행 공급 노드로 둡니다.",
        "verification_need": "셀 타입, BMS 호환성, 안전인증, 재활용 원료의 재투입 가능 공정 확인",
    },
    {
        "material_id": "copper_electronics_feedstock",
        "label": "Copper, PCB, and connector feedstock",
        "feeds_part_category": "flight_stack",
        "linked_bom_item": "flight-stack PCB and wiring harness families",
        "demo_basis": "전자스크랩/비철금속 후보를 PCB, 케이블, 커넥터 공급 안정성에 연결합니다.",
        "verification_need": "분류·정제 설비, 원소 분석, 납기, 전자부품 재제조 적합성 확인",
    },
    {
        "material_id": "lightweight_airframe_feedstock",
        "label": "Composite, carbon, and light-metal feedstock",
        "feeds_part_category": "airframe",
        "linked_bom_item": "1 airframe / materials family per drone",
        "demo_basis": "카본·복합재·경량금속 후보를 프레임 및 하우징 부품군의 선행 공급 노드로 둡니다.",
        "verification_need": "재료 등급, 성형 가능성, 치수 안정성, 긴급 전환 가능 설비 확인",
    },
]

RAW_MATERIAL_CATALOG = {
    "ndfeb_magnet_feedstock": {
        "label": "NdFeB magnet feedstock",
        "short_label": "NdFeB",
        "color": "#1f8a84",
        "feeds_part_categories": ["propulsion"],
        "linked_resource_category": "rare_earth_magnet_recovery",
        "unit": "kg",
        "domestic_inventory_share_range": (0.12, 0.32),
        "import_dependency": "high",
        "verification_need": "magnet grade, recovery yield, alloy compatibility, and certified supplier availability",
    },
    "lithium_battery_feedstock": {
        "label": "Battery cell and lithium feedstock",
        "short_label": "Battery",
        "color": "#c05a35",
        "feeds_part_categories": ["power"],
        "linked_resource_category": "battery_material_recovery",
        "unit": "kg",
        "domestic_inventory_share_range": (0.18, 0.42),
        "import_dependency": "high",
        "verification_need": "cell format, BMS compatibility, safety certification, and thermal screening",
    },
    "copper_electronics_feedstock": {
        "label": "Copper, PCB, and connector feedstock",
        "short_label": "Copper/PCB",
        "color": "#5f6f2e",
        "feeds_part_categories": ["flight_stack", "harness"],
        "linked_resource_category": "metal_electronics_recycling",
        "unit": "kg",
        "domestic_inventory_share_range": (0.22, 0.52),
        "import_dependency": "medium",
        "verification_need": "copper purity, laminate availability, connector plating, and PCB fabrication grade",
    },
    "lightweight_airframe_feedstock": {
        "label": "Composite, carbon, and light-metal feedstock",
        "short_label": "Composite",
        "color": "#7d6342",
        "feeds_part_categories": ["airframe"],
        "linked_resource_category": "carbon_composite_supply",
        "unit": "kg",
        "domestic_inventory_share_range": (0.24, 0.58),
        "import_dependency": "medium",
        "verification_need": "material grade, molding compatibility, dimensional stability, and rework rate",
    },
    "optical_sensor_components": {
        "label": "Optical sensor, lens, and imaging components",
        "short_label": "Optics",
        "color": "#5b6ea8",
        "feeds_part_categories": ["sensor_payload"],
        "linked_resource_category": None,
        "unit": "kg",
        "domestic_inventory_share_range": (0.16, 0.36),
        "import_dependency": "high",
        "verification_need": "lens/sensor module availability, calibration bench, and firmware interface",
    },
    "industrial_polymers_packaging": {
        "label": "Industrial polymers, cases, and packaging material",
        "short_label": "Polymers",
        "color": "#546061",
        "feeds_part_categories": ["qa_packaging", "drone_assembly"],
        "linked_resource_category": None,
        "unit": "kg",
        "domestic_inventory_share_range": (0.38, 0.72),
        "import_dependency": "low",
        "verification_need": "case/packaging stock, transport shock rating, and assembly handling requirements",
    },
}

DRONE_MISSION_PROFILES = [
    {
        "profile_id": "short_range_recon_quad",
        "label": "Short-range ISR quad",
        "safe_use": "reconnaissance, inspection, and situational awareness",
        "default_mix_share": 0.55,
        "part_units_per_drone": {
            "drone_assembly": 1,
            "flight_stack": 1,
            "power": 1,
            "propulsion": 4,
            "sensor_payload": 1,
            "airframe": 1,
            "harness": 1,
            "qa_packaging": 1,
        },
        "material_kg_per_drone": {
            "ndfeb_magnet_feedstock": 0.28,
            "lithium_battery_feedstock": 1.55,
            "copper_electronics_feedstock": 0.32,
            "lightweight_airframe_feedstock": 1.25,
            "optical_sensor_components": 0.12,
            "industrial_polymers_packaging": 0.42,
        },
    },
    {
        "profile_id": "comms_relay_quad",
        "label": "Communications relay quad",
        "safe_use": "relay, network extension, and emergency communications",
        "default_mix_share": 0.2,
        "part_units_per_drone": {
            "drone_assembly": 1,
            "flight_stack": 1,
            "power": 1,
            "propulsion": 4,
            "sensor_payload": 1,
            "airframe": 1,
            "harness": 1,
            "qa_packaging": 1,
        },
        "material_kg_per_drone": {
            "ndfeb_magnet_feedstock": 0.3,
            "lithium_battery_feedstock": 1.9,
            "copper_electronics_feedstock": 0.48,
            "lightweight_airframe_feedstock": 1.4,
            "optical_sensor_components": 0.08,
            "industrial_polymers_packaging": 0.46,
        },
    },
    {
        "profile_id": "light_logistics_quad",
        "label": "Light logistics quad",
        "safe_use": "small parcel, medical, and maintenance-item delivery",
        "default_mix_share": 0.25,
        "part_units_per_drone": {
            "drone_assembly": 1,
            "flight_stack": 1,
            "power": 1,
            "propulsion": 4,
            "sensor_payload": 1,
            "airframe": 1,
            "harness": 1,
            "qa_packaging": 1,
        },
        "material_kg_per_drone": {
            "ndfeb_magnet_feedstock": 0.38,
            "lithium_battery_feedstock": 2.45,
            "copper_electronics_feedstock": 0.4,
            "lightweight_airframe_feedstock": 2.2,
            "optical_sensor_components": 0.08,
            "industrial_polymers_packaging": 0.65,
        },
    },
]

DEFAULT_DRONE_MISSION_MIX = [
    {"profile_id": profile["profile_id"], "share": profile["default_mix_share"]} for profile in DRONE_MISSION_PROFILES
]

BLOCKADE_DEMAND_MODEL = {
    "model_version": "d4d.blockade_survival.v0.1",
    "demand_basis": "attrition-driven daily replenishment, not monthly production target",
    "required_fpv_class_units_per_day": 3333,
    "sorties_per_day": 3333,
    "recovery_rate": 0.0,
    "new_deployment_units_per_day": 0,
    "effective_output_factor_range": [0.2, 0.4],
    "fiber_variant_share": 0.1,
    "leakage_scenarios": [
        {"id": "full_blockade", "label": "Full blockade", "leakage_pct": 0.0, "airlift_scenario": "ZERO"},
        {"id": "limited_leakage", "label": "Limited residual inflow", "leakage_pct": 0.1, "airlift_scenario": "LIMITED"},
        {"id": "partial_blockade", "label": "Partial blockade", "leakage_pct": 0.3, "airlift_scenario": "LIMITED"},
    ],
    "safe_boundary": (
        "High-level sustainment and inventory-risk model only. No payload, targeting, or build instructions. "
        "Synthetic defaults must be replaced with authorized ERP/MES/procurement feeds before operational use."
    ),
}

COMPONENT_CATALOG = {
    "frame_fpv": {
        "label": "FPV-class frame",
        "part_category": "airframe",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.0,
        "variant": "all",
        "localization_difficulty": "LOW",
        "vulnerability": "green",
        "inventory_days_range": (12, 28),
        "ramp_ready_day_range": (14, 30),
        "line_output_ratio_range": (0.55, 0.9),
        "factory_search_hint": {"ksic": ["C22", "C25"], "keywords": ["프레임", "카본", "탄소", "사출", "금형"]},
        "verification_need": "carbon/composite grade, mold availability, dimensional tolerance, and QA readiness",
    },
    "motor_bldc_fpv": {
        "label": "BLDC motor class",
        "part_category": "propulsion",
        "unit": "ea",
        "base_units_per_drone": 4,
        "attrition_factor": 1.05,
        "variant": "all",
        "localization_difficulty": "MEDIUM_HIGH",
        "vulnerability": "red",
        "inventory_days_range": (8, 22),
        "ramp_ready_day_range": (35, 70),
        "line_output_ratio_range": (0.25, 0.55),
        "factory_search_hint": {"ksic": ["C28"], "keywords": ["BLDC", "모터", "권선", "자석"]},
        "verification_need": "NdFeB magnet stock, winding equipment, balancing, bearings, and test fixtures",
    },
    "propeller_fpv": {
        "label": "Propeller",
        "part_category": "propulsion",
        "unit": "ea",
        "base_units_per_drone": 4,
        "attrition_factor": 1.5,
        "variant": "all",
        "localization_difficulty": "LOW",
        "vulnerability": "yellow",
        "inventory_days_range": (10, 25),
        "ramp_ready_day_range": (10, 24),
        "line_output_ratio_range": (0.55, 0.95),
        "factory_search_hint": {"ksic": ["C22"], "keywords": ["프로펠러", "정밀사출", "엔지니어링 플라스틱"]},
        "verification_need": "material grade, tooling, balance/warp QA, and packaging loss rate",
    },
    "esc_4in1": {
        "label": "ESC board class",
        "part_category": "flight_stack",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.05,
        "variant": "all",
        "localization_difficulty": "MEDIUM",
        "vulnerability": "red",
        "inventory_days_range": (7, 18),
        "ramp_ready_day_range": (28, 56),
        "line_output_ratio_range": (0.22, 0.48),
        "factory_search_hint": {"ksic": ["C26"], "keywords": ["SMT", "PCB", "전력반도체", "FET"]},
        "verification_need": "MCU/FET/capacitor kit availability, firmware QA, and load testing",
    },
    "flight_controller": {
        "label": "Flight controller board",
        "part_category": "flight_stack",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.05,
        "variant": "all",
        "localization_difficulty": "MEDIUM",
        "vulnerability": "red",
        "inventory_days_range": (7, 17),
        "ramp_ready_day_range": (28, 60),
        "line_output_ratio_range": (0.2, 0.45),
        "factory_search_hint": {"ksic": ["C26"], "keywords": ["SMT", "제어기", "IMU", "PCB"]},
        "verification_need": "MCU and IMU stock, firmware porting, calibration bench, and test coverage",
    },
    "battery_cell_21700": {
        "label": "High-discharge battery cell",
        "part_category": "power",
        "unit": "cell",
        "base_units_per_drone": 12,
        "attrition_factor": 1.1,
        "variant": "all",
        "localization_difficulty": "MEDIUM_LOW",
        "vulnerability": "yellow",
        "inventory_days_range": (14, 35),
        "ramp_ready_day_range": (20, 45),
        "line_output_ratio_range": (0.45, 0.8),
        "factory_search_hint": {"ksic": ["C28"], "keywords": ["배터리팩", "21700", "BMS", "스폿용접"]},
        "aging_sensitive": True,
        "verification_need": "cell origin lot, pack assembly line, BMS stock, connector format, and FIFO aging policy",
    },
    "camera_module": {
        "label": "Camera / imaging module",
        "part_category": "sensor_payload",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.05,
        "variant": "all",
        "localization_difficulty": "HIGH",
        "vulnerability": "red",
        "inventory_days_range": (6, 16),
        "ramp_ready_day_range": (45, 90),
        "line_output_ratio_range": (0.08, 0.24),
        "factory_search_hint": {"ksic": ["C26"], "keywords": ["카메라", "CMOS", "렌즈", "영상"]},
        "verification_need": "sensor module stock, lens compatibility, ISP/firmware interface, and calibration bench",
    },
    "vtx_module": {
        "label": "Video transmitter module",
        "part_category": "flight_stack",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.25,
        "variant": "rf_only",
        "localization_difficulty": "HIGH",
        "vulnerability": "red",
        "inventory_days_range": (5, 14),
        "ramp_ready_day_range": (42, 84),
        "line_output_ratio_range": (0.08, 0.22),
        "factory_search_hint": {"ksic": ["C26"], "keywords": ["RF", "통신모듈", "송신기", "SAW"]},
        "verification_need": "RF chipset, SAW filter, thermal design, certification constraints, and alternate BOM",
    },
    "rx_antenna_set": {
        "label": "Receiver and antenna set",
        "part_category": "flight_stack",
        "unit": "ea",
        "base_units_per_drone": 3,
        "attrition_factor": 1.25,
        "variant": "rf_only",
        "localization_difficulty": "MEDIUM_HIGH",
        "vulnerability": "yellow",
        "inventory_days_range": (6, 18),
        "ramp_ready_day_range": (30, 65),
        "line_output_ratio_range": (0.16, 0.36),
        "factory_search_hint": {"ksic": ["C26"], "keywords": ["수신기", "안테나", "RF", "필터"]},
        "verification_need": "receiver chipset, antenna stock, connector format, and field failure/cannibalization rate",
    },
    "fiber_comm_module": {
        "label": "Fiber communication module",
        "part_category": "flight_stack",
        "unit": "ea",
        "base_units_per_drone": 1,
        "attrition_factor": 1.05,
        "variant": "fiber_only",
        "localization_difficulty": "MEDIUM",
        "vulnerability": "green",
        "inventory_days_range": (8, 22),
        "ramp_ready_day_range": (24, 50),
        "line_output_ratio_range": (0.28, 0.58),
        "factory_search_hint": {"ksic": ["C26", "C27"], "keywords": ["광통신", "광모듈", "케이블", "권취"]},
        "verification_need": "fiber module sourcing, spool interface, and payout mechanism validation",
    },
    "fiber_spool_km": {
        "label": "Fiber spool",
        "part_category": "harness",
        "unit": "km",
        "base_units_per_drone": 20,
        "attrition_factor": 1.0,
        "variant": "fiber_only",
        "localization_difficulty": "LOW",
        "vulnerability": "green",
        "inventory_days_range": (10, 30),
        "ramp_ready_day_range": (14, 35),
        "line_output_ratio_range": (0.45, 0.85),
        "factory_search_hint": {"ksic": ["C28"], "keywords": ["광케이블", "광섬유", "보빈", "권취"]},
        "verification_need": "fiber length, spool QA, payout packaging, and transport damage rate",
    },
    "micro_parts_set": {
        "label": "Micro-parts and wiring set",
        "part_category": "harness",
        "unit": "set",
        "base_units_per_drone": 1,
        "attrition_factor": 1.2,
        "variant": "all",
        "localization_difficulty": "LOW",
        "vulnerability": "green",
        "inventory_days_range": (12, 32),
        "ramp_ready_day_range": (10, 25),
        "line_output_ratio_range": (0.55, 0.92),
        "factory_search_hint": {"ksic": ["C25", "C26"], "keywords": ["나사", "XT60", "커넥터", "배선", "하네스"]},
        "verification_need": "connector standard, capacitor stock, cable gauge, and kit completeness",
    },
}

SUBCOMPONENT_CATALOG = {
    "ndfeb_magnet": {
        "label": "NdFeB magnet",
        "type": "magnet",
        "unit": "ea_equivalent",
        "import_dependency": "critical",
        "inventory_days_range": (7, 20),
        "verification_need": "finished magnet count, grade, coating, and domestic raw rare-earth dependency",
    },
    "bearing_set": {
        "label": "Bearing set",
        "type": "mechanical",
        "unit": "ea",
        "import_dependency": "medium",
        "inventory_days_range": (10, 28),
        "verification_need": "bearing spec, QA, and lubricant/steel stock",
    },
    "mcu_kit": {
        "label": "MCU kit",
        "type": "chip",
        "unit": "ea",
        "import_dependency": "critical",
        "inventory_days_range": (5, 14),
        "verification_need": "alternate MCU qualification, firmware porting, dry-pack/FIFO stock policy",
    },
    "imu_sensor": {
        "label": "IMU sensor",
        "type": "sensor",
        "unit": "ea",
        "import_dependency": "critical",
        "inventory_days_range": (5, 13),
        "verification_need": "gyro/accelerometer availability, calibration compatibility, and alternate source",
    },
    "fet_set": {
        "label": "FET set",
        "type": "power_semiconductor",
        "unit": "set",
        "import_dependency": "high",
        "inventory_days_range": (8, 22),
        "verification_need": "low-voltage FET stock, package compatibility, and heat/current margin",
    },
    "camera_cmos": {
        "label": "CMOS imaging sensor",
        "type": "sensor",
        "unit": "ea",
        "import_dependency": "critical",
        "inventory_days_range": (5, 12),
        "verification_need": "sensor module supply, lens/ISP integration, and alternate camera BOM",
    },
    "rf_chip_saw": {
        "label": "RF chip and SAW filter kit",
        "type": "rf_chip",
        "unit": "kit",
        "import_dependency": "critical",
        "inventory_days_range": (4, 12),
        "verification_need": "RF chipset, SAW filter, certification, and fiber variant substitution option",
    },
    "bms_ic": {
        "label": "BMS IC",
        "type": "chip",
        "unit": "ea",
        "import_dependency": "high",
        "inventory_days_range": (8, 24),
        "verification_need": "BMS IC stock, firmware, pack safety certification, and connector standard",
    },
    "fiber_module_chip": {
        "label": "Fiber module electronics",
        "type": "optoelectronics",
        "unit": "kit",
        "import_dependency": "medium",
        "inventory_days_range": (9, 24),
        "verification_need": "opto module stock, connector package, and spool interface",
    },
}

COMPONENT_SUBCOMPONENT_BOM = {
    "motor_bldc_fpv": {"ndfeb_magnet": 4, "bearing_set": 1},
    "esc_4in1": {"mcu_kit": 1, "fet_set": 1},
    "flight_controller": {"mcu_kit": 1, "imu_sensor": 1},
    "battery_cell_21700": {},
    "camera_module": {"camera_cmos": 1},
    "vtx_module": {"rf_chip_saw": 1},
    "rx_antenna_set": {"rf_chip_saw": 1},
    "fiber_comm_module": {"fiber_module_chip": 1},
}

IMPORT_PORTS = [
    {"id": "port_donghae", "name": "Donghae Port", "lat": 37.49, "lon": 129.14, "coast": "east"},
    {"id": "port_pohang", "name": "Pohang Port", "lat": 36.03, "lon": 129.40, "coast": "east"},
    {"id": "port_ulsan", "name": "Ulsan Port", "lat": 35.50, "lon": 129.38, "coast": "southeast"},
    {"id": "port_busan", "name": "Busan Port", "lat": 35.10, "lon": 129.04, "coast": "southeast"},
]

FOREIGN_MATERIAL_SOURCES = [
    {
        "id": "src_jp_maizuru_magnets",
        "name": "Japan west-coast magnet buffer",
        "country": "Japan",
        "port_name": "Maizuru",
        "lat": 35.47,
        "lon": 135.38,
        "material_ids": ["ndfeb_magnet_feedstock"],
        "preferred_port_id": "port_donghae",
        "monthly_capacity_kg": 4200,
    },
    {
        "id": "src_jp_niigata_battery",
        "name": "Japan Sea battery-material buffer",
        "country": "Japan",
        "port_name": "Niigata",
        "lat": 37.93,
        "lon": 139.05,
        "material_ids": ["lithium_battery_feedstock"],
        "preferred_port_id": "port_donghae",
        "monthly_capacity_kg": 12500,
    },
    {
        "id": "src_jp_kitakyushu_electronics",
        "name": "Kyushu electronics and copper buffer",
        "country": "Japan",
        "port_name": "Kitakyushu",
        "lat": 33.88,
        "lon": 130.88,
        "material_ids": ["copper_electronics_feedstock"],
        "preferred_port_id": "port_busan",
        "monthly_capacity_kg": 7600,
    },
    {
        "id": "src_jp_nagoya_composite",
        "name": "Chubu composite and light-metal buffer",
        "country": "Japan",
        "port_name": "Nagoya",
        "lat": 35.09,
        "lon": 136.88,
        "material_ids": ["lightweight_airframe_feedstock"],
        "preferred_port_id": "port_ulsan",
        "monthly_capacity_kg": 14800,
    },
    {
        "id": "src_jp_yokohama_optics",
        "name": "Kanto optics and imaging buffer",
        "country": "Japan",
        "port_name": "Yokohama",
        "lat": 35.45,
        "lon": 139.64,
        "material_ids": ["optical_sensor_components"],
        "preferred_port_id": "port_pohang",
        "monthly_capacity_kg": 1350,
    },
    {
        "id": "src_jp_kobe_polymers",
        "name": "Kansai industrial polymer buffer",
        "country": "Japan",
        "port_name": "Kobe",
        "lat": 34.68,
        "lon": 135.19,
        "material_ids": ["industrial_polymers_packaging"],
        "preferred_port_id": "port_busan",
        "monthly_capacity_kg": 9000,
    },
]

ALLIED_SUPPLY_SOURCES = [
    {
        "id": "ally_aus_lithium_nickel",
        "country": "Australia",
        "partner_framework": "MSP / Korea-Australia critical minerals cooperation",
        "source_port_name": "Fremantle / Kwinana",
        "source_lat": -32.05,
        "source_lon": 115.74,
        "staging_port_name": "Kobe / Niigata battery-material staging",
        "staging_source_ids": ["src_jp_niigata_battery", "src_jp_kobe_polymers"],
        "material_ids": ["lithium_battery_feedstock"],
        "component_ids": ["battery_cell_21700"],
        "subcomponent_ids": [],
        "supply_role": "lithium, nickel, cobalt, manganese, and graphite feedstock for battery cell continuity",
        "confidence": "medium",
        "evidence_urls": [
            "https://www.ga.gov.au/scientific-topics/minerals/critical-minerals",
            "https://www.austrade.gov.au/content/dam/austrade-assets/global/wip/austrade/documents/Opportunities-in-Korea-for-Australian-critical-minerals.pdf",
        ],
        "verification_need": "contracted grade, conversion chemistry, customs lead time, and Japan staging capacity",
    },
    {
        "id": "ally_aus_rare_earths",
        "country": "Australia",
        "partner_framework": "MSP Nolans rare-earth project / Korea-Australia cooperation",
        "source_port_name": "Darwin / Adelaide",
        "source_lat": -12.47,
        "source_lon": 130.84,
        "staging_port_name": "Maizuru magnet-material staging",
        "staging_source_ids": ["src_jp_maizuru_magnets"],
        "material_ids": ["ndfeb_magnet_feedstock"],
        "component_ids": ["motor_bldc_fpv"],
        "subcomponent_ids": ["ndfeb_magnet"],
        "supply_role": "Nd-Pr rare-earth feedstock for permanent magnets and motor continuity",
        "confidence": "medium",
        "evidence_urls": [
            "https://www.mofa.go.kr/eng/brd/m_5676/view.do?page=1&seq=322736",
            "https://www.ga.gov.au/scientific-topics/minerals/critical-minerals",
        ],
        "verification_need": "oxide-to-magnet conversion route, separator capacity, and magnet alloy specification",
    },
    {
        "id": "ally_can_battery_minerals",
        "country": "Canada",
        "partner_framework": "MSP / G7 critical minerals cooperation",
        "source_port_name": "Vancouver",
        "source_lat": 49.29,
        "source_lon": -123.12,
        "staging_port_name": "Niigata battery-material staging",
        "staging_source_ids": ["src_jp_niigata_battery"],
        "material_ids": ["lithium_battery_feedstock", "copper_electronics_feedstock"],
        "component_ids": ["battery_cell_21700", "esc_4in1"],
        "subcomponent_ids": ["fet_set"],
        "supply_role": "nickel, cobalt, graphite, copper, and lithium-bearing inputs for battery/electronics resilience",
        "confidence": "low-medium",
        "evidence_urls": [
            "https://www.canada.ca/en/campaign/critical-minerals-in-canada/canadas-critical-minerals-strategy/canadian-critical-minerals-strategy-annual-report-2024.html",
            "https://www.mofa.go.kr/eng/brd/m_5676/view.do?seq=322611",
        ],
        "verification_need": "shipper, refining stage, Korea-compatible grade, and Japan transshipment feasibility",
    },
    {
        "id": "ally_twn_semiconductor_kits",
        "country": "Taiwan",
        "partner_framework": "like-minded semiconductor and non-red drone supply chain cooperation",
        "source_port_name": "Kaohsiung",
        "source_lat": 22.61,
        "source_lon": 120.28,
        "staging_port_name": "Yokohama / Kobe electronics staging",
        "staging_source_ids": ["src_jp_yokohama_optics", "src_jp_kobe_polymers"],
        "material_ids": ["optical_sensor_components", "copper_electronics_feedstock"],
        "component_ids": ["flight_controller", "esc_4in1", "camera_module", "vtx_module", "rx_antenna_set"],
        "subcomponent_ids": ["mcu_kit", "imu_sensor", "camera_cmos", "rf_chip_saw"],
        "supply_role": "semiconductor, sensor, RF, camera, and control-board kits for non-red electronics continuity",
        "confidence": "medium",
        "evidence_urls": [
            "https://www.moea.gov.tw/Mns/english/content/Content.aspx?menu_id=43675",
        ],
        "verification_need": "export controls, wafer/package availability, board-level assembly partner, and Japan staging SLA",
    },
    {
        "id": "ally_usa_semiconductor_critical_minerals",
        "country": "United States",
        "partner_framework": "KORUS / Japan partnership / MSP critical supply chain cooperation",
        "source_port_name": "Los Angeles / Long Beach",
        "source_lat": 33.74,
        "source_lon": -118.27,
        "staging_port_name": "Yokohama electronics and optics staging",
        "staging_source_ids": ["src_jp_yokohama_optics"],
        "material_ids": ["optical_sensor_components", "ndfeb_magnet_feedstock", "lithium_battery_feedstock"],
        "component_ids": ["flight_controller", "camera_module", "vtx_module"],
        "subcomponent_ids": ["mcu_kit", "imu_sensor", "camera_cmos", "rf_chip_saw"],
        "supply_role": "semiconductor, advanced packaging, battery, permanent magnet, and critical material partnership support",
        "confidence": "low-medium",
        "evidence_urls": [
            "https://ustr.gov/about-us/policy-offices/press-office/blogs-and-op-eds/2022/april/building-resilient-and-secure-supply-chains-through-trade",
            "https://www.mofa.go.kr/eng/brd/m_5676/view.do?seq=322611",
        ],
        "verification_need": "supplier allocation, export-control review, packaging format, and Japan relay node selection",
    },
    {
        "id": "ally_jpn_midstream_staging",
        "country": "Japan",
        "partner_framework": "Japan-Korea critical minerals high-level dialogue",
        "source_port_name": "Maizuru / Niigata / Kitakyushu / Nagoya / Yokohama / Kobe",
        "source_lat": 35.45,
        "source_lon": 136.15,
        "staging_port_name": "Japan midstream staging ports",
        "staging_source_ids": [source["id"] for source in FOREIGN_MATERIAL_SOURCES],
        "material_ids": sorted({material for source in FOREIGN_MATERIAL_SOURCES for material in source["material_ids"]}),
        "component_ids": [
            "motor_bldc_fpv",
            "battery_cell_21700",
            "flight_controller",
            "camera_module",
            "airframe_carbon",
        ],
        "subcomponent_ids": ["ndfeb_magnet", "mcu_kit", "camera_cmos", "rf_chip_saw"],
        "supply_role": "Japan-side midstream staging, copper refining cooperation, optics/electronics buffers, and coastal transshipment",
        "confidence": "medium",
        "evidence_urls": [
            "https://www.meti.go.jp/english/press/2025/1217_004.html",
        ],
        "verification_need": "actual supplier contracts, port handling slot, domestic trucking-to-port leg, and quality certificate",
    },
]

SEA_CORRIDOR_WAYPOINTS = {
    "src_jp_maizuru_magnets": [
        {"lat": 35.72, "lon": 134.78},
        {"lat": 36.34, "lon": 132.35},
        {"lat": 37.08, "lon": 130.55},
    ],
    "src_jp_niigata_battery": [
        {"lat": 38.22, "lon": 137.25},
        {"lat": 38.05, "lon": 134.30},
        {"lat": 37.66, "lon": 131.65},
    ],
    "src_jp_kitakyushu_electronics": [
        {"lat": 34.06, "lon": 130.63},
        {"lat": 34.42, "lon": 130.05},
        {"lat": 34.82, "lon": 129.55},
    ],
    "src_jp_nagoya_composite": [
        {"lat": 34.62, "lon": 136.92},
        {"lat": 33.52, "lon": 136.55},
        {"lat": 32.88, "lon": 134.42},
        {"lat": 33.15, "lon": 132.15},
        {"lat": 34.18, "lon": 130.35},
        {"lat": 34.85, "lon": 129.70},
    ],
    "src_jp_yokohama_optics": [
        {"lat": 35.05, "lon": 139.72},
        {"lat": 34.35, "lon": 139.10},
        {"lat": 33.15, "lon": 137.20},
        {"lat": 32.88, "lon": 134.42},
        {"lat": 33.15, "lon": 132.15},
        {"lat": 34.18, "lon": 130.30},
        {"lat": 35.20, "lon": 130.08},
    ],
    "src_jp_kobe_polymers": [
        {"lat": 34.45, "lon": 134.72},
        {"lat": 34.15, "lon": 132.70},
        {"lat": 33.95, "lon": 131.02},
        {"lat": 34.35, "lon": 130.22},
        {"lat": 34.82, "lon": 129.45},
    ],
}

MARITIME_CORRIDOR_MODEL = {
    "profile_version": "d4d.material_maritime_supply.v0.2",
    "safe_boundary": "Route corridors are coarse public-demo logistics lanes, not operational vessel tasking or protected convoy guidance.",
    "assumption": "Japan-Korea import routes use coarse coastal waypoints to avoid drawing demo links across land.",
    "unit": "kg per 30 days",
    "geometry_method": "public demo port-to-port sea corridor waypoints; replace with AIS/shipping-lane or approved maritime-routing data before real planning",
}

LOGISTICS_COST_MODEL = {
    "distance_basis": "road_distance_km when routed; heuristic road estimate otherwise",
    "default_vehicle": "3.5-5t cargo truck equivalent",
    "fuel_efficiency_km_per_liter": 6.5,
    "driver_count_per_trip": 1,
    "labor_cost_krw_per_hour_placeholder": 28000,
    "fuel_cost_krw_per_liter_placeholder": 1700,
    "cost_formula": (
        "per_trip_cost = road_distance_km / fuel_efficiency_km_per_liter * fuel_cost "
        "+ duration_min / 60 * driver_count * labor_cost"
    ),
    "mvp_note": (
        "Use this as a comparable planning score until an approved routing provider "
        "and vehicle-capacity model are connected."
    ),
}

ENERGY_CAPACITY_MODEL = {
    "direct_sources": [
        "NGMS 명세서배출량정보공개: 업체명, 대상년도, 지정구분, 부문, 계획업종, 온실가스배출량, 에너지사용량",
        "한국에너지공단 에너지다소비사업자 에너지 사용 현황: 지역/부문별 에너지·전력 집계",
    ],
    "interpretation": (
        "Large reported energy or electricity use is a useful production-scale proxy, "
        "but it is not the same as spare capacity or immediate conversion readiness."
    ),
    "capacity_evidence_fields": [
        "reported_energy_use_toe",
        "reported_ghg_emissions_tco2e",
        "regional_industrial_electricity_mwh",
        "estimated_power_intensity_score",
        "capacity_evidence_score",
    ],
    "limitations": [
        "Company-level NGMS records cover large emitting/managed entities only.",
        "KEPCO/KEA public electricity data is generally aggregated by region and sector, not every factory.",
        "High energy use can mean high output, but can also mean inefficient processes or low spare capacity.",
        "Final mobilization decisions still require live line availability, workforce, equipment, inventory, and grid reliability checks.",
    ],
}

FACTORY_CAPACITY_MODEL = {
    "profile_version": "d4d.factory_capacity_profile.v0.1",
    "interpretation": (
        "Production volume is an evidence-weighted public-data estimate for route planning. "
        "It is not verified mobilization capacity or guaranteed spare line capacity."
    ),
    "primary_sources": [
        "한국산업단지공단 전국등록공장현황_20200229: employees, area, industry, product, factory management number",
        "NGMS/KEA energy context: direct large-emitter energy records where matched; otherwise regional industrial proxy",
    ],
    "score_formula": (
        "capacity_index = 0.25 production_fit + 0.18 physical_scale + 0.17 workforce "
        "+ 0.14 transaction_history + 0.10 financial_scale + 0.08 certification_quality "
        "+ 0.04 technology_signal + 0.04 logistics_access"
    ),
    "mvp_available_terms": [
        "production_fit",
        "physical_scale",
        "workforce_scale",
        "energy_operating_scale",
        "logistics_access",
    ],
    "deferred_terms": [
        "transaction_history",
        "financial_scale",
        "certification_quality",
        "technology_signal",
    ],
    "limitations": [
        "Open data can estimate likely operating scale but cannot prove spare capacity.",
        "Exact equipment inventory, shift availability, inventory, QA status, and emergency power require verification.",
        "Older rich factory registry rows may differ from the latest lightweight registry snapshot.",
    ],
}

POWER_GRID_RISK_MODEL = {
    "profile_version": "d4d.power_grid_risk_proxy.v0.1",
    "interpretation": (
        "Public data can support regional load-serving risk and factory outage sensitivity, "
        "but it should not be treated as a verified substation-to-factory dependency map."
    ),
    "primary_sources": [
        "한국전력공사_전력고객주요정보_대용량고객일반정보: 대용량 고객, 변전소/배전설비, 용량, 점검기준 등 공개 메타데이터",
        "한국에너지공단 에너지다소비사업자 에너지 사용 현황: 지역/산업 전력사용량",
        "OpenStreetMap power tags: optional public power infrastructure context for future coarse validation",
    ],
    "safe_modeling_boundary": [
        "Use province/city-cluster load-serving zones rather than exact electric-facility dependency chains.",
        "Expose impact as production-continuity risk, not as an attack target list.",
        "Treat all dependencies as proxy estimates until KEPCO/customer-side supply contracts and facility diagrams are verified.",
    ],
    "fields": [
        "grid_risk_zones[]",
        "factory_candidates[].grid_risk_profile",
        "grid_disruption_scenarios[]",
    ],
}

OPERATIONS_STATE_MODEL = {
    "profile_version": "d4d.operations_state_proxy.v0.1",
    "interpretation": (
        "Frozen orders, in-transit shipments, and WIP/inventory are synthetic operational ledgers "
        "anchored to the current demo plan. Replace with ERP/MES/TMS feeds for production use."
    ),
    "fields": [
        "frozen_orders[]",
        "in_transit_shipments[]",
        "inventory_wip[]",
        "factory_candidates[].manufacturing_profile",
    ],
}


PROVINCE_CENTROIDS = {
    "서울특별시": (37.5665, 126.9780),
    "부산광역시": (35.1796, 129.0756),
    "대구광역시": (35.8714, 128.6014),
    "인천광역시": (37.4563, 126.7052),
    "광주광역시": (35.1595, 126.8526),
    "대전광역시": (36.3504, 127.3845),
    "울산광역시": (35.5384, 129.3114),
    "세종특별자치시": (36.4800, 127.2890),
    "경기도": (37.4138, 127.5183),
    "강원특별자치도": (37.8228, 128.1555),
    "강원도": (37.8228, 128.1555),
    "충청북도": (36.6357, 127.4913),
    "충청남도": (36.6588, 126.6728),
    "전라북도": (35.7175, 127.1530),
    "전북특별자치도": (35.7175, 127.1530),
    "전라남도": (34.8679, 126.9910),
    "경상북도": (36.4919, 128.8889),
    "경상남도": (35.4606, 128.2132),
    "제주특별자치도": (33.4996, 126.5312),
}

CITY_OFFSETS = {
    "화성시": (0.10, -0.20),
    "수원시": (0.12, -0.18),
    "성남시": (0.20, -0.05),
    "용인시": (0.05, -0.02),
    "안산시": (0.03, -0.31),
    "시흥시": (0.09, -0.34),
    "평택시": (-0.33, -0.24),
    "파주시": (0.39, -0.32),
    "김포시": (0.27, -0.47),
    "부천시": (0.16, -0.42),
    "천안시": (0.16, 0.00),
    "아산시": (0.10, -0.18),
    "청주시": (0.00, -0.02),
    "구미시": (0.25, -0.50),
    "창원시": (-0.23, 0.48),
    "김해시": (-0.45, 0.65),
    "성동구": (-0.00, 0.08),
    "금천구": (-0.10, -0.05),
    "구로구": (-0.08, -0.07),
}

ASSEMBLY_HUBS = [
    {
        "id": "hub_daejeon",
        "name": "Daejeon Rapid Integration Cell",
        "lat": 36.3504,
        "lon": 127.3845,
        "capacity_drones_30d": 4200,
        "accepted_categories": list(PART_CATEGORIES.keys()),
        "role": "central command-linked integration and QA hub",
    },
    {
        "id": "hub_pyeongtaek",
        "name": "Pyeongtaek West-Coast Assembly Hub",
        "lat": 36.9944,
        "lon": 127.0889,
        "capacity_drones_30d": 3500,
        "accepted_categories": list(PART_CATEGORIES.keys()),
        "role": "west-coast logistics and rapid handoff hub",
    },
    {
        "id": "hub_daegu",
        "name": "Daegu Inland Reserve Assembly Hub",
        "lat": 35.8714,
        "lon": 128.6014,
        "capacity_drones_30d": 2800,
        "accepted_categories": list(PART_CATEGORIES.keys()),
        "role": "inland reserve integration hub for rerouted supply",
    },
]

SCENARIOS = [
    {
        "id": "baseline",
        "name": "Baseline Production Plan",
        "short_name": "Baseline",
        "description": "No predicted factory strike. Route by capacity, distance, and category confidence.",
        "target_drones": 10000,
        "threat": None,
        "risk_weight": 0.15,
        "grid_risk_weight": 0.1,
    },
    {
        "id": "western_axis_threat",
        "name": "Western Axis Factory Strike Forecast",
        "short_name": "Threat Reroute",
        "description": "Synthetic hostile movement corridor raises risk for Incheon/Gyeonggi west-coast suppliers; supply flows reroute inland.",
        "target_drones": 10000,
        "risk_weight": 0.7,
        "grid_risk_weight": 0.18,
        "threat": {
            "label": "Synthetic west-coast threat corridor",
            "probability": 0.68,
            "risk_radius_km": 62,
            "path": [
                {"lat": 38.08, "lon": 124.80},
                {"lat": 37.72, "lon": 125.65},
                {"lat": 37.35, "lon": 126.30},
                {"lat": 36.98, "lon": 126.86},
            ],
            "assumption": "Demo-only probabilistic route forecast, not real intelligence.",
        },
    },
    {
        "id": "southern_port_disruption",
        "name": "Southern Port Logistics Disruption",
        "short_name": "Port Stress",
        "description": "Synthetic disruption around Busan/Ulsan/Changwon lowers route preference and pushes assembly inland.",
        "target_drones": 10000,
        "risk_weight": 0.55,
        "grid_risk_weight": 0.16,
        "threat": {
            "label": "Synthetic southern logistics disruption",
            "probability": 0.52,
            "risk_radius_km": 55,
            "path": [
                {"lat": 35.60, "lon": 129.45},
                {"lat": 35.25, "lon": 129.10},
                {"lat": 35.02, "lon": 128.70},
            ],
            "assumption": "Demo-only logistics denial forecast, not real intelligence.",
        },
    },
]

PRIORITY_DRONE_ASSEMBLY_BASES = [
    {
        "slug": "bonai_sangju",
        "company_name": "본AI",
        "site_label": "상주 생산공장",
        "address": "경상북도 상주시 아리랑고개3길 85-26",
        "site_type": "공장 / 제조업 사업장",
        "priority_weight": 2.35,
        "capacity_units_30d": 1450,
        "confidence": 0.94,
    },
    {
        "slug": "uvify_uiwang",
        "company_name": "유비파이 / UVify",
        "site_label": "의왕 연구소 / 생산기지",
        "address": "경기도 의왕시 오봉산단3로 32, 데카빌딩",
        "site_type": "연구소 / 생산기지",
        "priority_weight": 2.2,
        "capacity_units_30d": 1200,
        "confidence": 0.92,
    },
    {
        "slug": "pablo_air_songdo",
        "company_name": "파블로항공 / PABLO AIR",
        "site_label": "송도 제조센터",
        "address": "인천광역시 연수구 송도미래로 30, A동 2004-7호",
        "site_type": "Manufacturing Center",
        "priority_weight": 2.25,
        "capacity_units_30d": 1350,
        "confidence": 0.93,
    },
    {
        "slug": "pablo_air_gimpo",
        "company_name": "파블로항공 / PABLO AIR",
        "site_label": "김포 제조센터",
        "address": "경기도 김포시 양촌읍 황금1로80번길 55",
        "site_type": "Manufacturing Center",
        "priority_weight": 2.25,
        "capacity_units_30d": 1320,
        "confidence": 0.93,
    },
    {
        "slug": "pablo_air_changwon_uichang",
        "company_name": "파블로항공 / PABLO AIR",
        "site_label": "창원 의창 제조기반",
        "address": "경상남도 창원시 의창구 죽전로 85",
        "site_type": "Manufacturing Center",
        "priority_weight": 2.15,
        "capacity_units_30d": 1160,
        "confidence": 0.9,
    },
    {
        "slug": "pablo_air_changwon_seongsan",
        "company_name": "파블로항공 / PABLO AIR",
        "site_label": "창원 성산 제조기반",
        "address": "경상남도 창원시 성산구 곰절길 28번길 2",
        "site_type": "Manufacturing Center",
        "priority_weight": 2.15,
        "capacity_units_30d": 1160,
        "confidence": 0.9,
    },
    {
        "slug": "alux_dobong",
        "company_name": "에이럭스 / ALUX",
        "site_label": "도봉 공식 사업장 / 제조 인프라 확인 필요",
        "address": "서울특별시 도봉구 마들로13길 61, 씨드큐브 창동 C동 오피스 1602호",
        "site_type": "공식 사업장 / 제조 인프라 가정",
        "priority_weight": 1.75,
        "capacity_units_30d": 860,
        "confidence": 0.78,
    },
    {
        "slug": "korean_air_tech_center",
        "company_name": "대한항공 항공우주사업본부",
        "site_label": "대한항공 테크센터",
        "address": "부산광역시 강서구 테크센터로 55",
        "site_type": "항공우주 생산기지 / 테크센터",
        "priority_weight": 2.4,
        "capacity_units_30d": 2100,
        "confidence": 0.95,
    },
    {
        "slug": "kai_sacheon_main",
        "company_name": "KAI / 한국항공우주산업",
        "site_label": "사천 본사 / 항공우주 제조 거점",
        "address": "경상남도 사천시 사남면 공단1로 78",
        "site_type": "본사 및 주요 사업장",
        "priority_weight": 2.45,
        "capacity_units_30d": 2250,
        "confidence": 0.95,
    },
    {
        "slug": "kai_sacheon_jongpo",
        "company_name": "KAI / 한국항공우주산업",
        "site_label": "사천 종포 사업장",
        "address": "경상남도 사천시 용현면 종포산단로 194",
        "site_type": "주요 사업장",
        "priority_weight": 2.25,
        "capacity_units_30d": 1780,
        "confidence": 0.9,
    },
    {
        "slug": "kai_sancheong",
        "company_name": "KAI / 한국항공우주산업",
        "site_label": "산청 사업장",
        "address": "경상남도 산청군 금서면 친환경로 2436",
        "site_type": "주요 사업장",
        "priority_weight": 2.05,
        "capacity_units_30d": 1320,
        "confidence": 0.86,
    },
    {
        "slug": "kai_goseong",
        "company_name": "KAI / 한국항공우주산업",
        "site_label": "고성 사업장",
        "address": "경상남도 고성군 고성읍 사동길 185",
        "site_type": "주요 사업장",
        "priority_weight": 2.05,
        "capacity_units_30d": 1320,
        "confidence": 0.86,
    },
    {
        "slug": "preneu_ansan",
        "company_name": "프리뉴 / PRENEU",
        "site_label": "안산 Manufacturing Center",
        "address": "경기도 안산시 단원구 산단로 325 스마트스퀘어 1400",
        "site_type": "Manufacturing Center",
        "priority_weight": 2.2,
        "capacity_units_30d": 1280,
        "confidence": 0.92,
    },
    {
        "slug": "pnu_drone_busan_factory1",
        "company_name": "피앤유드론 / PNU Drone",
        "site_label": "부산 제1공장",
        "address": "부산광역시 강서구 과학산단1로60번길 31, 부산테크노파크 지사단지 1동 204호",
        "site_type": "제1공장",
        "priority_weight": 2.1,
        "capacity_units_30d": 980,
        "confidence": 0.9,
    },
    {
        "slug": "pnu_drone_yangsan_factory2",
        "company_name": "피앤유드론 / PNU Drone",
        "site_label": "양산 제2공장 / 비행시험센터",
        "address": "경상남도 양산시 물금읍 메기로 319",
        "site_type": "제2공장 / 연구전담부서 / 비행시험센터",
        "priority_weight": 2.0,
        "capacity_units_30d": 920,
        "confidence": 0.88,
    },
    {
        "slug": "pnu_drone_busan_hq",
        "company_name": "피앤유드론 / PNU Drone",
        "site_label": "부산대 본사 / 생산기지 가정",
        "address": "부산광역시 금정구 부산대학로 63번길 2, 부산대학교 효원산학협동관 516호",
        "site_type": "본사 / 생산기지 가정",
        "priority_weight": 1.55,
        "capacity_units_30d": 520,
        "confidence": 0.7,
    },
    {
        "slug": "uconsystem_daejeon",
        "company_name": "유콘시스템 / UCONSYSTEM",
        "site_label": "대전 본사 / 생산기지 가정",
        "address": "대전광역시 유성구 테크노2로 40-9",
        "site_type": "본사 / 생산기지 가정",
        "priority_weight": 2.2,
        "capacity_units_30d": 1350,
        "confidence": 0.9,
    },
    {
        "slug": "dmi_yongin",
        "company_name": "두산모빌리티이노베이션 / DMI",
        "site_label": "두산기술원",
        "address": "경기도 용인시 수지구 수지로112번길 10",
        "site_type": "기술원 / 사업장",
        "priority_weight": 1.95,
        "capacity_units_30d": 980,
        "confidence": 0.84,
    },
    {
        "slug": "dmi_hwaseong",
        "company_name": "두산모빌리티이노베이션 / DMI",
        "site_label": "화성 사업장",
        "address": "경기도 화성시 향남읍 제약단지로 75",
        "site_type": "사업장",
        "priority_weight": 1.9,
        "capacity_units_30d": 920,
        "confidence": 0.82,
    },
    {
        "slug": "soomvi_songdo",
        "company_name": "숨비 / SOOMVI",
        "site_label": "인천 본사 / 연구소",
        "address": "인천광역시 연수구 송도과학로16번길 13-25",
        "site_type": "연구소 / 생산기지 가정",
        "priority_weight": 1.95,
        "capacity_units_30d": 900,
        "confidence": 0.84,
    },
    {
        "slug": "soomvi_seoul_lab",
        "company_name": "숨비 / SOOMVI",
        "site_label": "서울연구소",
        "address": "서울특별시 서초구 사평대로53길 30, 402호",
        "site_type": "연구소 / 생산기지 가정",
        "priority_weight": 1.55,
        "capacity_units_30d": 560,
        "confidence": 0.72,
    },
    {
        "slug": "ninano_gimcheon",
        "company_name": "니나노컴퍼니 / NINANO COMPANY",
        "site_label": "김천 본사",
        "address": "경상북도 김천시 혁신로 315-11",
        "site_type": "본사 / 생산기지 가정",
        "priority_weight": 1.75,
        "capacity_units_30d": 760,
        "confidence": 0.78,
    },
    {
        "slug": "ninano_gumi",
        "company_name": "니나노컴퍼니 / NINANO COMPANY",
        "site_label": "구미 지사",
        "address": "경상북도 구미시 구미대로 350-27, 모바일융합기술센터 408호",
        "site_type": "지사 / 생산기지 가정",
        "priority_weight": 1.65,
        "capacity_units_30d": 650,
        "confidence": 0.74,
    },
    {
        "slug": "assetta_incheon_factory",
        "company_name": "아쎄따 / ASSETTA",
        "site_label": "인천 연구소/공장",
        "address": "인천광역시 서구 가재울로 109, 주안DH비즈타워 1차 902호",
        "site_type": "연구소/공장",
        "priority_weight": 2.05,
        "capacity_units_30d": 980,
        "confidence": 0.9,
    },
    {
        "slug": "assetta_goyang",
        "company_name": "아쎄따 / ASSETTA",
        "site_label": "고양 본사",
        "address": "경기도 고양시 덕양구 화랑로 57-27, 고양드론앵커센터 301호",
        "site_type": "본사",
        "priority_weight": 1.65,
        "capacity_units_30d": 620,
        "confidence": 0.74,
    },
    {
        "slug": "assetta_daejeon_lab",
        "company_name": "아쎄따 / ASSETTA",
        "site_label": "대전 드론연구센터",
        "address": "대전광역시 유성구 테크노2로 199, 미건테크노월드 4층 421호",
        "site_type": "드론연구센터",
        "priority_weight": 1.6,
        "capacity_units_30d": 580,
        "confidence": 0.72,
    },
    {
        "slug": "assetta_yeoncheon_training",
        "company_name": "아쎄따 / ASSETTA",
        "site_label": "연천 드론전문교육원 / 전환 후보",
        "address": "경기도 연천군 전곡읍 양원로46번길 20",
        "site_type": "드론전문교육원 / 생산전환 후보",
        "priority_weight": 1.35,
        "capacity_units_30d": 360,
        "confidence": 0.62,
    },
    {
        "slug": "assetta_namwon_branch",
        "company_name": "아쎄따 / ASSETTA",
        "site_label": "남원 지사 / 생산기지 가정",
        "address": "전북특별자치도 남원시 시묘길 43-12, 남원시바이오산업연구원 C314호",
        "site_type": "지사 / 생산기지 가정",
        "priority_weight": 1.35,
        "capacity_units_30d": 360,
        "confidence": 0.62,
    },
    {
        "slug": "astrox_incheon",
        "company_name": "아스트로엑스 / AstroX",
        "site_label": "인천 로봇타워 R&D·제조거점",
        "address": "인천광역시 서구 로봇랜드로 155-11, 로봇타워 19층",
        "site_type": "본사 / R&D·제조거점 가정",
        "priority_weight": 1.8,
        "capacity_units_30d": 780,
        "confidence": 0.8,
    },
]

CORE_OPERATING_DRONE_ASSEMBLY_SLUGS = [
    "bonai_sangju",
    "uvify_uiwang",
    "pablo_air_songdo",
    "alux_dobong",
    "korean_air_tech_center",
    "preneu_ansan",
    "pnu_drone_busan_factory1",
    "uconsystem_daejeon",
    "dmi_yongin",
    "soomvi_songdo",
    "assetta_incheon_factory",
    "astrox_incheon",
]

RESERVE_STANDBY_DRONE_ASSEMBLY_SLUGS = [
    "pablo_air_gimpo",
    "pablo_air_changwon_uichang",
    "pablo_air_changwon_seongsan",
    "pnu_drone_yangsan_factory2",
    "dmi_hwaseong",
    "soomvi_seoul_lab",
    "ninano_gimcheon",
    "ninano_gumi",
    "assetta_goyang",
    "assetta_daejeon_lab",
]

CORE_OPERATING_DRONE_ASSEMBLY_SET = set(CORE_OPERATING_DRONE_ASSEMBLY_SLUGS)
RESERVE_STANDBY_DRONE_ASSEMBLY_SET = set(RESERVE_STANDBY_DRONE_ASSEMBLY_SLUGS)
DRONE_ASSEMBLY_SEED_SLUGS = CORE_OPERATING_DRONE_ASSEMBLY_SLUGS + RESERVE_STANDBY_DRONE_ASSEMBLY_SLUGS
DRONE_ASSEMBLY_SEED_SET = set(DRONE_ASSEMBLY_SEED_SLUGS)
CORE_OPERATING_ASSEMBLY_RECORD_CACHE: dict[int, list["FactoryRecord"]] = {}
RESERVE_STANDBY_ASSEMBLY_RECORD_CACHE: dict[int, list["FactoryRecord"]] = {}


@dataclass
class FactoryRecord:
    id: str
    company_name: str
    factory_manage_no: str
    complex_name: str
    product_text: str
    raw_materials_text: str
    industry_code: str
    industry_name: str
    factory_size_label: str
    address: str
    province: str
    city: str
    lat: float
    lon: float
    category: str
    confidence: float
    confidence_reasons: list[str]
    employee_total: float | None
    land_area_m2: float | None
    manufacturing_area_m2: float | None
    auxiliary_area_m2: float | None
    building_area_m2: float | None
    capacity_units_30d: int
    capacity_profile: dict
    energy_profile: dict
    source_row: int
    data_limitations: list[str]
    priority_role: str = ""
    priority_weight: float = 1.0
    priority_source: str = ""
    priority_site_label: str = ""
    priority_site_type: str = ""
    assembly_operating_status: str = ""
    assembly_node_role: str = ""
    is_priority_assembly_seed: bool = False


@dataclass
class ResourceRecord:
    id: str
    company_name: str
    complex_name: str
    product_text: str
    address: str
    province: str
    city: str
    lat: float
    lon: float
    resource_category: str
    confidence: float
    confidence_reasons: list[str]
    capacity_kg_30d: int
    target_part_categories: list[str]
    energy_profile: dict
    source_row: int
    data_limitations: list[str]


def stable_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:12], 16)


def stable_float(value: str, low: float, high: float) -> float:
    fraction = stable_hash(value) / float(16**12 - 1)
    return low + (high - low) * fraction


def download_source() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_CSV.exists() and RAW_CSV.stat().st_size > 1024:
        return
    with urllib.request.urlopen(SOURCE_URL, timeout=40) as response:
        RAW_CSV.write_bytes(response.read())


def download_energy_sources() -> None:
    ENERGY_DIR.mkdir(parents=True, exist_ok=True)
    if not LARGE_ENERGY_USERS_XLSX.exists() or LARGE_ENERGY_USERS_XLSX.stat().st_size < 1024:
        with urllib.request.urlopen(LARGE_ENERGY_USERS_URL, timeout=40) as response:
            LARGE_ENERGY_USERS_XLSX.write_bytes(response.read())
    if not NGMS_EMISSIONS_CSV.exists() or NGMS_EMISSIONS_CSV.stat().st_size < 1024:
        with urllib.request.urlopen(NGMS_EMISSIONS_URL, timeout=40) as response:
            NGMS_EMISSIONS_CSV.write_bytes(response.read())


def download_grid_sources() -> None:
    GRID_DIR.mkdir(parents=True, exist_ok=True)
    if not KEPCO_LARGE_CUSTOMER_CSV.exists() or KEPCO_LARGE_CUSTOMER_CSV.stat().st_size < 1024:
        with urllib.request.urlopen(KEPCO_LARGE_CUSTOMER_URL, timeout=120) as response:
            KEPCO_LARGE_CUSTOMER_CSV.write_bytes(response.read())


def download_capacity_sources() -> None:
    CAPACITY_DIR.mkdir(parents=True, exist_ok=True)
    if not NATIONAL_FACTORY_CAPACITY_CSV.exists() or NATIONAL_FACTORY_CAPACITY_CSV.stat().st_size < 1024:
        with urllib.request.urlopen(NATIONAL_FACTORY_CAPACITY_URL, timeout=120) as response:
            NATIONAL_FACTORY_CAPACITY_CSV.write_bytes(response.read())
    if not FACTORYON_EMPLOYEE_XLSX.exists() or FACTORYON_EMPLOYEE_XLSX.stat().st_size < 1024:
        with urllib.request.urlopen(FACTORYON_EMPLOYEE_URL, timeout=120) as response:
            FACTORYON_EMPLOYEE_XLSX.write_bytes(response.read())


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def number_or_none(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if not text or text == "해당없음":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_company_name(value: str) -> str:
    text = (value or "").lower()
    text = re.sub(r"\([^)]*\)", "", text)
    for token in [
        "주식회사",
        "(주)",
        "㈜",
        "유한회사",
        "재단법인",
        "사단법인",
        "농업회사법인",
        "회사법인",
        "co.ltd",
        "co ltd",
        "ltd",
        "inc",
        "corp",
    ]:
        text = text.replace(token, "")
    return re.sub(r"[\s\-_,.&·]", "", text)


def province_short_name(province: str) -> str:
    mapping = {
        "서울특별시": "서울",
        "부산광역시": "부산",
        "대구광역시": "대구",
        "인천광역시": "인천",
        "광주광역시": "광주",
        "대전광역시": "대전",
        "울산광역시": "울산",
        "세종특별자치시": "세종",
        "경기도": "경기",
        "강원특별자치도": "강원",
        "강원도": "강원",
        "충청북도": "충북",
        "충청남도": "충남",
        "전라북도": "전북",
        "전북특별자치도": "전북",
        "전라남도": "전남",
        "경상북도": "경북",
        "경상남도": "경남",
        "제주특별자치도": "제주",
    }
    return mapping.get(province, province[:2])


def normalize_province_name(value: str) -> str:
    text = clean(value)
    mapping = {
        "강원도": "강원특별자치도",
        "전라북도": "전북특별자치도",
    }
    return mapping.get(text, text)


def parse_location(address: str, key: str) -> tuple[str, str, float, float]:
    tokens = address.split()
    province = tokens[0] if tokens else "미상"
    city = tokens[1] if len(tokens) > 1 else ""
    lat, lon = PROVINCE_CENTROIDS.get(province, (36.3, 127.8))
    if city in CITY_OFFSETS:
        dlat, dlon = CITY_OFFSETS[city]
        lat += dlat
        lon += dlon
    lat += stable_float(key + ":lat", -0.12, 0.12)
    lon += stable_float(key + ":lon", -0.16, 0.16)
    return province, city, round(lat, 5), round(lon, 5)


def xlsx_col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - 64
    return index - 1


def read_xlsx_sheet_rows(path: Path, sheet_filename: str) -> list[list[str]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    with ZipFile(path) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            shared_root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("a:si", ns):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", ns)))
        sheet_root = ET.fromstring(workbook.read(f"xl/worksheets/{sheet_filename}.xml"))
        for row in sheet_root.findall(".//a:sheetData/a:row", ns):
            values: list[str] = []
            for cell in row.findall("a:c", ns):
                index = xlsx_col_index(cell.attrib.get("r", "A1"))
                while len(values) <= index:
                    values.append("")
                value_node = cell.find("a:v", ns)
                value = ""
                if value_node is not None:
                    value = value_node.text or ""
                    if cell.attrib.get("t") == "s":
                        value = shared_strings[int(value)]
                values[index] = value
            rows.append(values)
    return rows


def read_regional_energy_context() -> dict:
    if not LARGE_ENERGY_USERS_XLSX.exists():
        return {"year": None, "industrial_electricity_mwh_by_province": {}, "industrial_energy_toe_by_province": {}}

    electricity_rows = read_xlsx_sheet_rows(LARGE_ENERGY_USERS_XLSX, "sheet11")
    energy_rows = read_xlsx_sheet_rows(LARGE_ENERGY_USERS_XLSX, "sheet12")

    def latest_industrial(rows: list[list[str]]) -> tuple[int | None, dict[str, float]]:
        if not rows:
            return None, {}
        header = rows[0]
        latest_year: int | None = None
        latest_row: list[str] | None = None
        for row in rows[1:]:
            if len(row) < 3 or row[1] != "산업":
                continue
            year_value = int(float(row[0]))
            if latest_year is None or year_value > latest_year:
                latest_year = year_value
                latest_row = row
        if latest_row is None:
            return None, {}
        values: dict[str, float] = {}
        for index, label in enumerate(header[2:], start=2):
            province = re.sub(r"\(.*?\)", "", label)
            amount = number_or_none(latest_row[index] if index < len(latest_row) else None)
            if province and amount is not None and province != "총합계":
                values[province] = amount
        return latest_year, values

    electricity_year, electricity = latest_industrial(electricity_rows)
    energy_year, energy = latest_industrial(energy_rows)
    return {
        "year": electricity_year or energy_year,
        "industrial_electricity_mwh_by_province": electricity,
        "industrial_energy_toe_by_province": energy,
    }


def read_ngms_emissions() -> dict[str, dict]:
    if not NGMS_EMISSIONS_CSV.exists():
        return {}
    records: dict[str, dict] = {}
    with NGMS_EMISSIONS_CSV.open("r", encoding="cp949", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            normalized = normalize_company_name(row.get("업체명", ""))
            if not normalized:
                continue
            energy_use = number_or_none(row.get("에너지사용량"))
            emissions = number_or_none(row.get("온실가스배출량"))
            current = records.get(normalized)
            candidate = {
                "reported_company_name": clean(row.get("업체명")),
                "reported_year": int(float(row.get("대상년도") or 0)) if row.get("대상년도") else None,
                "designation_type": clean(row.get("지정구분")),
                "sector": clean(row.get("부문")),
                "industry": clean(row.get("계획업종")),
                "reported_ghg_emissions_tco2e": emissions,
                "reported_energy_use_toe": energy_use,
                "verification_body": clean(row.get("검증수행기관")),
                "source": "NGMS 명세서배출량정보공개",
            }
            if current is None or (candidate["reported_year"] or 0) > (current.get("reported_year") or 0):
                records[normalized] = candidate
    return records


def build_energy_context() -> dict:
    regional = read_regional_energy_context()
    ngms_records = read_ngms_emissions()
    emissions_values = [
        record["reported_ghg_emissions_tco2e"]
        for record in ngms_records.values()
        if record.get("reported_ghg_emissions_tco2e") is not None
    ]
    energy_values = [
        record["reported_energy_use_toe"]
        for record in ngms_records.values()
        if record.get("reported_energy_use_toe") is not None
    ]
    return {
        "regional": regional,
        "ngms_records": ngms_records,
        "stats": {
            "ngms_record_count": len(ngms_records),
            "ngms_max_emissions_tco2e": max(emissions_values) if emissions_values else None,
            "ngms_max_energy_use_toe": max(energy_values) if energy_values else None,
            "regional_electricity_year": regional.get("year"),
        },
    }


def top_counts(counter: dict[str, int], limit: int = 5) -> list[dict]:
    return [
        {"label": label, "count": count}
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
        if label
    ]


def read_kepco_large_customer_context() -> dict:
    if not KEPCO_LARGE_CUSTOMER_CSV.exists():
        return {
            "record_count": 0,
            "by_province": {},
            "source": "한국전력공사_전력고객주요정보_대용량고객일반정보",
        }
    by_province: dict[str, dict] = {}
    record_count = 0
    with KEPCO_LARGE_CUSTOMER_CSV.open("r", encoding="cp949", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            record_count += 1
            province = normalize_province_name(row.get("시도", ""))
            if not province:
                continue
            item = by_province.setdefault(
                province,
                {
                    "large_customer_rows": 0,
                    "substation_class_counts": {},
                    "supply_class_counts": {},
                    "equipment_basis_counts": {},
                    "inspection_basis_counts": {},
                    "capacity_text_examples": [],
                },
            )
            item["large_customer_rows"] += 1
            for field, target in [
                ("변전소 분류", "substation_class_counts"),
                ("공급분류", "supply_class_counts"),
                ("장비기준", "equipment_basis_counts"),
                ("점검기준", "inspection_basis_counts"),
            ]:
                value = clean(row.get(field))
                if value:
                    item[target][value] = item[target].get(value, 0) + 1
            capacity_text = clean(row.get("용량"))
            if capacity_text and len(item["capacity_text_examples"]) < 3:
                item["capacity_text_examples"].append(capacity_text)

    for item in by_province.values():
        item["top_substation_classes"] = top_counts(item.pop("substation_class_counts"))
        item["top_supply_classes"] = top_counts(item.pop("supply_class_counts"))
        item["top_equipment_basis"] = top_counts(item.pop("equipment_basis_counts"))
        item["top_inspection_basis"] = top_counts(item.pop("inspection_basis_counts"))
    return {
        "record_count": record_count,
        "by_province": by_province,
        "source": "한국전력공사_전력고객주요정보_대용량고객일반정보",
        "limitations": [
            "Rows support regional power-demand and equipment-context screening.",
            "Rows do not prove a specific factory's customer-side feeder or outage dependency.",
            "Use aggregated province/city-cluster signals for continuity planning.",
        ],
    }


def category_match(company_name: str, product_text: str) -> tuple[str | None, float, list[str]]:
    product_lower = product_text.lower()
    company_lower = company_name.lower()
    best: tuple[str | None, float, list[str]] = (None, 0.0, [])
    for category, spec in PART_CATEGORIES.items():
        product_hits = [kw for kw in spec["keywords"] if kw.lower() in product_lower]
        company_hits = [kw for kw in spec["keywords"] if kw.lower() in company_lower]
        if not product_hits and not company_hits:
            continue

        score = 0.34
        reasons: list[str] = []
        if product_hits:
            score += min(0.46, 0.2 + 0.08 * len(product_hits))
            reasons.append("product keyword: " + ", ".join(product_hits[:3]))
        if company_hits:
            score += 0.08 if product_hits else 0.03
            reasons.append("company keyword: " + ", ".join(company_hits[:2]))
        if category == "drone_assembly" and product_hits:
            score += 0.14
        if product_text and len(product_text) > 8:
            score += 0.04
        if category == "power" and "bms" in company_lower and not product_hits:
            score -= 0.22
            reasons.append("BMS only in company name; possible non-battery false positive")
        if category == "propulsion" and "모터스" in company_name and not product_hits:
            score -= 0.25
            reasons.append("motors only in company name; likely unrelated")
        if "인쇄" in product_text and category in {"power", "flight_stack"}:
            score -= 0.18
            reasons.append("printing product text lowers electronics confidence")

        score = max(0.12, min(0.96, score))
        if score > best[1]:
            best = (category, score, reasons)
    return best


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def log_score(value: float | None, reference: float) -> float:
    if value is None or value <= 0:
        return 0.0
    return clamp(math.log1p(value) / math.log1p(reference))


def factory_size_score(label: str) -> float:
    normalized = clean(label)
    if "대기업" in normalized:
        return 0.96
    if "중견" in normalized:
        return 0.9
    if "중기업" in normalized:
        return 0.78
    if "소기업" in normalized:
        return 0.46
    return 0.0


def production_fit_score(category: str, confidence: float, product_text: str, industry_name: str, raw_materials: str) -> float:
    spec = PART_CATEGORIES[category]
    combined = f"{product_text} {industry_name} {raw_materials}".lower()
    keyword_hits = sum(1 for keyword in spec["keywords"] if keyword.lower() in combined)
    industry_bonus = 0.0
    if any(token in industry_name for token in ["제조", "전자", "전기", "기계", "금속", "플라스틱", "광학", "통신"]):
        industry_bonus += 0.08
    if any(token in industry_name for token in ["도매", "소매", "부동산", "임대", "교육", "서비스"]):
        industry_bonus -= 0.12
    raw_material_bonus = 0.04 if raw_materials else 0.0
    return round(clamp(0.58 * confidence + min(0.24, keyword_hits * 0.06) + industry_bonus + raw_material_bonus), 3)


def data_completeness_score(values: Iterable[object]) -> float:
    items = list(values)
    if not items:
        return 0.0
    present = 0
    for value in items:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (int, float)) and value <= 0:
            continue
        present += 1
    return round(present / len(items), 3)


def capacity_tier(capacity_index: float, confidence: float) -> str:
    if capacity_index >= 0.78 and confidence >= 0.7:
        return "A"
    if capacity_index >= 0.62 and confidence >= 0.55:
        return "B"
    if capacity_index >= 0.45:
        return "C"
    if confidence < 0.45:
        return "VERIFY_ONLY"
    return "D"


def recommended_role_for(tier: str) -> str:
    return {
        "A": "primary",
        "B": "surge",
        "C": "backup",
        "D": "verification_queue",
        "VERIFY_ONLY": "verification_queue",
    }.get(tier, "verification_queue")


def build_factory_capacity_profile(
    *,
    category: str,
    confidence: float,
    company_name: str,
    product_text: str,
    raw_materials_text: str,
    industry_code: str,
    industry_name: str,
    factory_size_label: str,
    employee_total: float | None,
    land_area_m2: float | None,
    manufacturing_area_m2: float | None,
    auxiliary_area_m2: float | None,
    building_area_m2: float | None,
    energy_profile: dict,
    route_access_score: float = 0.62,
) -> dict:
    manufacturing_score = log_score(manufacturing_area_m2, 18000)
    building_score = log_score(building_area_m2, 26000)
    land_score = log_score(land_area_m2, 90000)
    size_label_score = factory_size_score(factory_size_label)
    physical_candidates = [manufacturing_score, building_score, land_score, size_label_score]
    physical_score = round(max(physical_candidates) * 0.72 + sum(physical_candidates) / len(physical_candidates) * 0.28, 3)

    workforce_score = round(log_score(employee_total, 420), 3)
    production_fit = production_fit_score(category, confidence, product_text, industry_name, raw_materials_text)
    energy_score = float(energy_profile.get("capacity_evidence_score") or 0.0)
    completeness = data_completeness_score(
        [
            product_text,
            industry_name,
            industry_code,
            raw_materials_text,
            employee_total,
            manufacturing_area_m2,
            building_area_m2,
            land_area_m2,
            factory_size_label,
        ]
    )

    # Deferred terms remain explicit zero/low evidence until procurement, finance, certification, and IP data are joined.
    transaction_history = 0.0
    financial_scale = 0.0
    certification_quality = 0.0
    technology_signal = 0.0

    capacity_index = round(
        clamp(
            0.25 * production_fit
            + 0.18 * physical_score
            + 0.17 * workforce_score
            + 0.14 * transaction_history
            + 0.10 * financial_scale
            + 0.08 * certification_quality
            + 0.04 * technology_signal
            + 0.04 * route_access_score
            + 0.12 * energy_score
            + 0.10 * completeness
        ),
        3,
    )
    capacity_confidence = round(
        clamp(
            0.38 * confidence
            + 0.18 * completeness
            + 0.16 * (1 if employee_total and employee_total > 0 else 0)
            + 0.16 * (1 if (manufacturing_area_m2 or building_area_m2 or land_area_m2) else 0)
            + 0.06 * (1 if industry_code or industry_name else 0)
            + 0.06 * (0.85 if energy_profile.get("match_type") == "ngms_company_direct" else 0.35)
        ),
        3,
    )
    scale_signal = clamp(0.42 * physical_score + 0.36 * workforce_score + 0.14 * energy_score + 0.08 * completeness)
    deterministic_jitter = stable_float(company_name + product_text + category, 0.92, 1.08)
    predicted_output = PART_CATEGORIES[category]["base_capacity"] * (0.54 + 1.95 * scale_signal) * (0.62 + 0.48 * production_fit)
    predicted_output_units_30d = int(round((predicted_output * deterministic_jitter) / 25) * 25)

    missing_evidence = []
    if not employee_total or employee_total <= 0:
        missing_evidence.append("public employee/workforce count")
    if not manufacturing_area_m2 and not building_area_m2 and not land_area_m2:
        missing_evidence.append("public land/building/manufacturing area")
    if not industry_name and not industry_code:
        missing_evidence.append("industry code/name")
    missing_evidence.extend(
        [
            "equipment inventory",
            "spare line capacity",
            "shift availability",
            "component QA certification",
            "material inventory",
        ]
    )

    tier = capacity_tier(capacity_index, capacity_confidence)
    return {
        "profile_version": FACTORY_CAPACITY_MODEL["profile_version"],
        "capacity_tier": tier,
        "capacity_index": capacity_index,
        "capacity_confidence": capacity_confidence,
        "recommended_role": recommended_role_for(tier),
        "predicted_output_units_30d": max(25, predicted_output_units_30d),
        "estimate_basis": "public factory area + workforce + product/industry fit + energy operating-scale proxy",
        "evidence": {
            "production_fit": {
                "score": production_fit,
                "source": "product, industry, raw-material keyword match",
                "product_text": product_text,
                "industry_name": industry_name,
                "industry_code": industry_code,
                "raw_materials_text": raw_materials_text,
            },
            "physical_scale": {
                "score": physical_score,
                "land_area_m2": land_area_m2,
                "manufacturing_area_m2": manufacturing_area_m2,
                "auxiliary_area_m2": auxiliary_area_m2,
                "building_area_m2": building_area_m2,
                "factory_size_label": factory_size_label,
                "source": "한국산업단지공단 전국등록공장현황_20200229",
            },
            "workforce_scale": {
                "score": workforce_score,
                "employee_total": employee_total,
                "source": "한국산업단지공단 전국등록공장현황_20200229",
            },
            "energy_operating_scale": {
                "score": round(energy_score, 3),
                "match_type": energy_profile.get("match_type"),
                "source": energy_profile.get("source"),
            },
            "logistics_access": {
                "score": route_access_score,
                "source": "route planning placeholder; actual score should use road matrix and hub distance",
            },
            "transaction_history": {"score": transaction_history, "source": "deferred: 나라장터 계약/납품 실적"},
            "financial_scale": {"score": financial_scale, "source": "deferred: 기업 재무정보"},
            "certification_quality": {"score": certification_quality, "source": "deferred: KTL/KC/product certification"},
            "technology_signal": {"score": technology_signal, "source": "deferred: patent/design/IP record"},
        },
        "data_completeness_score": completeness,
        "missing_evidence": missing_evidence,
        "verification_questions": [
            "현재 생산라인 중 전환 가능한 설비와 공정은 무엇인가?",
            "30일 기준 추가 교대 투입 시 산출 가능량은 얼마인가?",
            "주요 원자재·부품 재고와 선행 공급처는 확보되어 있는가?",
            "드론 부품 납품에 필요한 검사·품질 기준을 충족할 수 있는가?",
            "정전·연료 제한 시 비상 전력과 물류 지속성이 있는가?",
        ],
        "limitations": FACTORY_CAPACITY_MODEL["limitations"],
    }


def resource_match(company_name: str, product_text: str) -> tuple[str | None, float, list[str]]:
    product_lower = product_text.lower()
    company_lower = company_name.lower()
    combined_lower = f"{company_lower} {product_lower}"
    best: tuple[str | None, float, list[str]] = (None, 0.0, [])
    for category, spec in RESOURCE_CATEGORIES.items():
        product_hits = [kw for kw in spec["keywords"] if kw.lower() in product_lower]
        company_hits = [kw for kw in spec["keywords"] if kw.lower() in company_lower]
        if not product_hits and not company_hits:
            continue

        score = 0.24
        reasons: list[str] = []
        if product_hits:
            score += min(0.46, 0.16 + 0.07 * len(product_hits))
            reasons.append("resource product keyword: " + ", ".join(product_hits[:4]))
        if company_hits:
            score += 0.07 if product_hits else 0.03
            reasons.append("resource company keyword: " + ", ".join(company_hits[:3]))

        if category == "rare_earth_magnet_recovery":
            high_value_terms = ["희토", "네오디", "디스프로", "터븀", "영구자석", "마그네트"]
            if any(term in combined_lower for term in high_value_terms):
                score += 0.18
            if any(term in combined_lower for term in ["학습", "교구", "판촉", "파스", "목걸이", "보드판"]):
                score -= 0.22
                reasons.append("generic magnet consumer/education text lowers recovery confidence")

        if category == "battery_material_recovery":
            if any(term in combined_lower for term in ["폐배터리", "폐전지", "재활용", "재생"]):
                score += 0.18
            if any(term in combined_lower for term in ["축전지", "리튬", "배터리", "전지"]):
                score += 0.08

        if category == "metal_electronics_recycling":
            if any(term in combined_lower for term in ["폐전자", "전자스크랩", "스크랩", "비철금속", "금속재생", "고철"]):
                score += 0.2
            if "신재생에너지" in combined_lower:
                score -= 0.18
                reasons.append("renewable-energy text is not necessarily material recycling")

        if category == "carbon_composite_supply":
            if any(term in combined_lower for term in ["탄소섬유", "카본", "복합재"]):
                score += 0.16
            if any(term in combined_lower for term in ["재생플라스틱", "플라스틱재생", "알루미늄", "알미늄"]):
                score += 0.08

        if product_text and len(product_text) > 8:
            score += 0.03
        score = max(0.1, min(0.94, score))
        if score > best[1]:
            best = (category, score, reasons)
    return best


def resource_capacity_for(category: str, confidence: float, company_name: str, product_text: str) -> int:
    spec = RESOURCE_CATEGORIES[category]
    multiplier = stable_float(company_name + product_text + category, 0.5, 1.75)
    capacity = spec["base_capacity_kg_30d"] * multiplier * (0.5 + confidence)
    return int(round(capacity / 25) * 25)


def energy_profile_for(
    company_name: str,
    province: str,
    category: str,
    confidence: float,
    base_capacity: int,
    energy_context: dict,
) -> dict:
    normalized = normalize_company_name(company_name)
    ngms = energy_context["ngms_records"].get(normalized)
    regional = energy_context["regional"]
    province_key = province_short_name(province)
    regional_power = regional["industrial_electricity_mwh_by_province"].get(province_key)
    regional_energy = regional["industrial_energy_toe_by_province"].get(province_key)
    regional_power_values = [
        value for value in regional["industrial_electricity_mwh_by_province"].values() if value is not None
    ]
    max_regional_power = max(regional_power_values) if regional_power_values else 1
    regional_power_score = min(1.0, (regional_power or 0) / max_regional_power)

    category_weight = {
        "power": 0.86,
        "flight_stack": 0.7,
        "propulsion": 0.75,
        "sensor_payload": 0.62,
        "airframe": 0.82,
        "harness": 0.58,
        "qa_packaging": 0.46,
        "drone_assembly": 0.68,
        "rare_earth_magnet_recovery": 0.8,
        "battery_material_recovery": 0.88,
        "metal_electronics_recycling": 0.72,
        "carbon_composite_supply": 0.8,
    }.get(category, 0.62)

    capacity_score = min(1.0, math.log(max(1, base_capacity), 10) / 4.3)
    direct_energy_score = 0.0
    direct_match = False
    if ngms:
        direct_match = True
        max_energy = energy_context["stats"].get("ngms_max_energy_use_toe") or 1
        max_emissions = energy_context["stats"].get("ngms_max_emissions_tco2e") or 1
        energy_component = min(1.0, (ngms.get("reported_energy_use_toe") or 0) / max_energy)
        emissions_component = min(1.0, (ngms.get("reported_ghg_emissions_tco2e") or 0) / max_emissions)
        direct_energy_score = max(energy_component, emissions_component)

    estimated_power_intensity_score = round(
        min(1.0, 0.28 * regional_power_score + 0.36 * category_weight + 0.24 * capacity_score + 0.12 * confidence),
        3,
    )
    capacity_evidence_score = round(
        min(
            1.0,
            0.58 * estimated_power_intensity_score
            + (0.24 * direct_energy_score if direct_match else 0)
            + 0.18 * confidence,
        ),
        3,
    )
    profile = {
        "match_type": "ngms_company_direct" if direct_match else "regional_industrial_proxy",
        "matched_company_name": ngms.get("reported_company_name") if ngms else None,
        "reported_year": ngms.get("reported_year") if ngms else regional.get("year"),
        "reported_energy_use_toe": ngms.get("reported_energy_use_toe") if ngms else None,
        "reported_ghg_emissions_tco2e": ngms.get("reported_ghg_emissions_tco2e") if ngms else None,
        "designation_type": ngms.get("designation_type") if ngms else None,
        "reported_sector": ngms.get("sector") if ngms else None,
        "reported_industry": ngms.get("industry") if ngms else None,
        "verification_body": ngms.get("verification_body") if ngms else None,
        "regional_industrial_electricity_mwh": round(regional_power, 1) if regional_power is not None else None,
        "regional_industrial_energy_toe": round(regional_energy, 1) if regional_energy is not None else None,
        "estimated_power_intensity_score": estimated_power_intensity_score,
        "capacity_evidence_score": capacity_evidence_score,
        "source": (
            "NGMS company-level emissions/energy + KEA regional industrial electricity context"
            if direct_match
            else "KEA regional industrial electricity context + category/capacity proxy"
        ),
        "limitations": ENERGY_CAPACITY_MODEL["limitations"],
    }
    return profile


def priority_assembly_seed_records(energy_context: dict) -> list[FactoryRecord]:
    records: list[FactoryRecord] = []
    category = "drone_assembly"
    seeds_by_slug = {seed["slug"]: seed for seed in PRIORITY_DRONE_ASSEMBLY_BASES}
    ordered_seeds = [seeds_by_slug[slug] for slug in DRONE_ASSEMBLY_SEED_SLUGS if slug in seeds_by_slug]
    for index, seed in enumerate(ordered_seeds, start=1):
        slug = seed["slug"]
        is_core_operating = slug in CORE_OPERATING_DRONE_ASSEMBLY_SET
        is_reserve_standby = slug in RESERVE_STANDBY_DRONE_ASSEMBLY_SET
        assembly_status = "core_operating" if is_core_operating else "reserve_standby"
        assembly_role = (
            "peacetime_final_assembly_factory"
            if is_core_operating
            else "reserve_final_assembly_conversion_candidate"
        )
        company_name = clean(seed["company_name"])
        address = clean(seed["address"])
        site_label = clean(seed["site_label"])
        site_type = clean(seed["site_type"])
        confidence = float(seed.get("confidence", 0.82))
        capacity_units = int(seed.get("capacity_units_30d", 800))
        record_key = f"priority_drone_assembly|{seed['slug']}|{company_name}|{address}"
        province, city, lat, lon = parse_location(address, record_key)
        product_text = f"{site_label} 드론 완성품 조립, 무인기 통합, UAV 생산기지"
        raw_materials_text = "배터리, 모터, 전자부품, 하네스, 복합재, 포장재"
        industry_code = "31322"
        industry_name = "무인기 및 항공우주 부품 조립 후보"
        energy_profile = energy_profile_for(
            company_name,
            province,
            category,
            confidence,
            capacity_units,
            energy_context,
        )
        capacity_profile = build_factory_capacity_profile(
            category=category,
            confidence=confidence,
            company_name=company_name,
            product_text=product_text,
            raw_materials_text=raw_materials_text,
            industry_code=industry_code,
            industry_name=industry_name,
            factory_size_label=site_type,
            employee_total=None,
            land_area_m2=None,
            manufacturing_area_m2=None,
            auxiliary_area_m2=None,
            building_area_m2=None,
            energy_profile=energy_profile,
            route_access_score=0.72 if is_core_operating else 0.62,
        )
        if is_core_operating:
            capacity_profile["capacity_tier"] = "A" if seed.get("priority_weight", 1) >= 2.2 else "B"
            capacity_profile["recommended_role"] = "primary" if capacity_profile["capacity_tier"] == "A" else "surge"
            capacity_profile["capacity_index"] = round(max(float(capacity_profile.get("capacity_index", 0)), 0.78), 3)
            capacity_profile["capacity_confidence"] = round(
                max(float(capacity_profile.get("capacity_confidence", 0)), confidence - 0.08),
                3,
            )
        else:
            capacity_profile["capacity_tier"] = "B" if seed.get("priority_weight", 1) >= 1.9 else "C"
            capacity_profile["recommended_role"] = "standby_reserve"
            capacity_profile["capacity_index"] = round(max(float(capacity_profile.get("capacity_index", 0)), 0.62), 3)
            capacity_profile["capacity_confidence"] = round(
                max(float(capacity_profile.get("capacity_confidence", 0)), confidence - 0.14),
                3,
            )
        capacity_profile["predicted_output_units_30d"] = capacity_units
        capacity_profile["estimate_basis"] = (
            "attached domestic drone production-base address seed + public capacity proxy; field verification required"
        )
        capacity_profile["assembly_operating_status"] = assembly_status
        capacity_profile["reserve_activation_profile"] = {
            "status": assembly_status,
            "role": assembly_role,
            "baseline_counted_as_output": is_core_operating,
            "activation_trigger": (
                "already counted in peacetime final-assembly plan"
                if is_core_operating
                else "activate only after a core final-assembly factory is disabled, capacity-constrained, or manually selected"
            ),
            "activation_setup_days_estimate": round(
                stable_float(slug + ":reserve_activation_days", 1.8, 5.4)
                if is_reserve_standby
                else stable_float(slug + ":core_activation_days", 0.4, 1.6),
                1,
            ),
            "verification_need": [
                "current line availability",
                "assembly workforce and QA bench readiness",
                "component receiving dock and local logistics capacity",
                "legal and contractual mobilization status",
            ],
        }
        capacity_profile.setdefault("evidence", {})["priority_assembly_seed"] = {
            "score": round(float(seed.get("priority_weight", 1.0)), 3),
            "site_label": site_label,
            "site_type": site_type,
            "assembly_operating_status": assembly_status,
            "source": "user-provided domestic_drone_production_base_addresses.md",
        }
        missing = capacity_profile.setdefault("missing_evidence", [])
        for item in ["live line availability", "current assembly workforce", "factory-level ERP/MES output"]:
            if item not in missing:
                missing.append(item)

        records.append(
            FactoryRecord(
                id="fac_priority_" + hashlib.sha1(record_key.encode("utf-8")).hexdigest()[:10],
                company_name=company_name,
                factory_manage_no=f"priority_drone_assembly_{seed['slug']}",
                complex_name=site_label,
                product_text=product_text,
                raw_materials_text=raw_materials_text,
                industry_code=industry_code,
                industry_name=industry_name,
                factory_size_label=site_type,
                address=address,
                province=province,
                city=city,
                lat=lat,
                lon=lon,
                category=category,
                confidence=round(confidence, 2),
                confidence_reasons=[
                    "attached domestic drone manufacturer production-base address",
                    f"priority final assembly seed: {site_label}",
                    "public address or official site/research/manufacturing base assumption",
                ],
                employee_total=None,
                land_area_m2=None,
                manufacturing_area_m2=None,
                auxiliary_area_m2=None,
                building_area_m2=None,
                capacity_units_30d=capacity_units,
                capacity_profile=capacity_profile,
                energy_profile=energy_profile,
                source_row=-index,
                data_limitations=[
                    "Priority seed from attached domestic drone production-base address list.",
                    "Exact current line capacity, equipment, workforce, and wartime legal status require verification.",
                    "Sites marked as research/headquarters are production-base assumptions where factory address is not public.",
                    (
                        "Core operating final-assembly node is counted in the baseline plan."
                        if is_core_operating
                        else "Reserve standby final-assembly node is mapped for fallback only and is not counted in baseline output."
                    ),
                ],
                priority_role="drone_final_assembly_primary" if is_core_operating else "drone_final_assembly_reserve",
                priority_weight=float(seed.get("priority_weight", 1.0)),
                priority_source="attached_domestic_drone_production_base_addresses_20260704",
                priority_site_label=site_label,
                priority_site_type=site_type,
                assembly_operating_status=assembly_status,
                assembly_node_role=assembly_role,
                is_priority_assembly_seed=True,
            )
        )
    return records


def read_candidates(energy_context: dict) -> list[FactoryRecord]:
    records: list[FactoryRecord] = []
    source_csv = NATIONAL_FACTORY_CAPACITY_CSV if NATIONAL_FACTORY_CAPACITY_CSV.exists() else RAW_CSV
    with source_csv.open("r", encoding="cp949", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_number, row in enumerate(reader, start=2):
            company_name = clean(row.get("회사명"))
            product_text = clean(row.get("생산품"))
            address = clean(row.get("공장주소"))
            complex_name = clean(row.get("단지명"))
            if not company_name or not product_text or not address:
                continue
            factory_manage_no = clean(row.get("공장관리번호"))
            raw_materials_text = clean(row.get("원자재"))
            industry_code = clean(row.get("대표업종"))
            industry_name = clean(row.get("업종명"))
            factory_size_label = clean(row.get("공장규모"))
            employee_total = number_or_none(row.get("종업원합계"))
            land_area_m2 = number_or_none(row.get("용지면적"))
            manufacturing_area_m2 = number_or_none(row.get("제조시설면적"))
            auxiliary_area_m2 = number_or_none(row.get("부대시설면적"))
            building_area_m2 = number_or_none(row.get("건축면적"))
            category, confidence, reasons = category_match(company_name, product_text)
            if not category or confidence < 0.42:
                continue
            record_key = f"{factory_manage_no}|{company_name}|{address}|{product_text}|{row_number}"
            province, city, lat, lon = parse_location(address, record_key)
            preliminary_capacity = int(PART_CATEGORIES[category]["base_capacity"] * (0.72 + confidence))
            energy_profile = energy_profile_for(
                company_name,
                province,
                category,
                confidence,
                preliminary_capacity,
                energy_context,
            )
            capacity_profile = build_factory_capacity_profile(
                category=category,
                confidence=confidence,
                company_name=company_name,
                product_text=product_text,
                raw_materials_text=raw_materials_text,
                industry_code=industry_code,
                industry_name=industry_name,
                factory_size_label=factory_size_label,
                employee_total=employee_total,
                land_area_m2=land_area_m2,
                manufacturing_area_m2=manufacturing_area_m2,
                auxiliary_area_m2=auxiliary_area_m2,
                building_area_m2=building_area_m2,
                energy_profile=energy_profile,
            )
            record = FactoryRecord(
                id="fac_" + hashlib.sha1(record_key.encode("utf-8")).hexdigest()[:10],
                company_name=company_name,
                factory_manage_no=factory_manage_no,
                complex_name=complex_name,
                product_text=product_text,
                raw_materials_text=raw_materials_text,
                industry_code=industry_code,
                industry_name=industry_name,
                factory_size_label=factory_size_label,
                address=address,
                province=province,
                city=city,
                lat=lat,
                lon=lon,
                category=category,
                confidence=round(confidence, 2),
                confidence_reasons=reasons,
                employee_total=employee_total,
                land_area_m2=land_area_m2,
                manufacturing_area_m2=manufacturing_area_m2,
                auxiliary_area_m2=auxiliary_area_m2,
                building_area_m2=building_area_m2,
                capacity_units_30d=capacity_profile["predicted_output_units_30d"],
                capacity_profile=capacity_profile,
                energy_profile=energy_profile,
                source_row=row_number,
                data_limitations=[
                    "Candidate inferred from public factory registration product text and capacity proxy fields.",
                    "Equipment inventory, line availability, QA status, and wartime legal status are not verified.",
                    "Coordinates are approximate for demo safety and geocoding stability.",
                ],
            )
            records.append(record)
    existing_keys = {
        (normalize_company_name(record.company_name), re.sub(r"\s+", "", record.address or ""))
        for record in records
    }
    for seed_record in priority_assembly_seed_records(energy_context):
        key = (normalize_company_name(seed_record.company_name), re.sub(r"\s+", "", seed_record.address or ""))
        if key not in existing_keys:
            records.append(seed_record)
            existing_keys.add(key)
    return records


def read_resource_candidates(energy_context: dict) -> list[ResourceRecord]:
    records: list[ResourceRecord] = []
    with RAW_CSV.open("r", encoding="cp949", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_number, row in enumerate(reader, start=2):
            company_name = clean(row.get("회사명"))
            product_text = clean(row.get("생산품"))
            address = clean(row.get("공장주소"))
            complex_name = clean(row.get("단지명"))
            if not company_name or not product_text or not address:
                continue
            category, confidence, reasons = resource_match(company_name, product_text)
            if not category or confidence < 0.42:
                continue
            record_key = f"resource|{company_name}|{address}|{product_text}|{row_number}"
            province, city, lat, lon = parse_location(address, record_key)
            spec = RESOURCE_CATEGORIES[category]
            capacity_kg_30d = resource_capacity_for(category, confidence, company_name, product_text)
            records.append(
                ResourceRecord(
                    id="res_" + hashlib.sha1(record_key.encode("utf-8")).hexdigest()[:10],
                    company_name=company_name,
                    complex_name=complex_name,
                    product_text=product_text,
                    address=address,
                    province=province,
                    city=city,
                    lat=lat,
                    lon=lon,
                    resource_category=category,
                    confidence=round(confidence, 2),
                    confidence_reasons=reasons,
                    capacity_kg_30d=capacity_kg_30d,
                    target_part_categories=list(spec["target_part_categories"]),
                    energy_profile=energy_profile_for(
                        company_name,
                        province,
                        category,
                        confidence,
                        capacity_kg_30d,
                        energy_context,
                    ),
                    source_row=row_number,
                    data_limitations=[
                        "Candidate inferred from public factory registration product text.",
                        "Actual recycling permit, hydrometallurgy/separation line, feedstock ownership, and material grade are not verified.",
                        "Coordinates are approximate for demo safety and geocoding stability.",
                    ],
                )
            )
    return records


def balanced_sample(records: list[FactoryRecord], per_category: int = 12) -> list[FactoryRecord]:
    selected: list[FactoryRecord] = []
    seen_ids: set[str] = set()
    for category in PART_CATEGORIES:
        group = [record for record in records if record.category == category]
        group.sort(
            key=lambda item: (
                -item.capacity_profile.get("capacity_index", 0),
                -item.confidence,
                -item.capacity_units_30d,
                stable_hash(item.id),
            )
        )
        province_counts: dict[str, int] = {}
        for record in group:
            if len([item for item in selected if item.category == category]) >= per_category:
                break
            if province_counts.get(record.province, 0) >= 3:
                continue
            selected.append(record)
            seen_ids.add(record.id)
            province_counts[record.province] = province_counts.get(record.province, 0) + 1

        if len([item for item in selected if item.category == category]) < per_category:
            for record in group:
                if record.id in seen_ids:
                    continue
                selected.append(record)
                seen_ids.add(record.id)
                if len([item for item in selected if item.category == category]) >= per_category:
                    break
    selected.sort(key=lambda item: (item.category, item.province, item.company_name))
    return selected


def balanced_resource_sample(records: list[ResourceRecord], per_category: int = 8) -> list[ResourceRecord]:
    selected: list[ResourceRecord] = []
    seen_ids: set[str] = set()
    for category in RESOURCE_CATEGORIES:
        group = [record for record in records if record.resource_category == category]
        group.sort(
            key=lambda item: (
                -item.confidence,
                -item.capacity_kg_30d,
                stable_hash(item.id),
            )
        )
        province_counts: dict[str, int] = {}
        for record in group:
            if len([item for item in selected if item.resource_category == category]) >= per_category:
                break
            if province_counts.get(record.province, 0) >= 3:
                continue
            selected.append(record)
            seen_ids.add(record.id)
            province_counts[record.province] = province_counts.get(record.province, 0) + 1

        if len([item for item in selected if item.resource_category == category]) < per_category:
            for record in group:
                if record.id in seen_ids:
                    continue
                selected.append(record)
                seen_ids.add(record.id)
                if len([item for item in selected if item.resource_category == category]) >= per_category:
                    break
    selected.sort(key=lambda item: (item.resource_category, item.province, item.company_name))
    return selected


def selected_factory_ids_from_plans(plans: list[dict]) -> set[str]:
    selected_ids: set[str] = set()
    for plan in plans:
        selected_ids.update(plan.get("selected_factory_ids", []))
        for route in plan.get("resource_route_segments", []):
            if route.get("target_factory_id"):
                selected_ids.add(route["target_factory_id"])
    return selected_ids


def merge_map_factory_records(
    base_records: list[FactoryRecord],
    all_records: list[FactoryRecord],
    required_ids: set[str],
    per_category_floor: int = 12,
    max_records: int = 180,
) -> list[FactoryRecord]:
    by_id = {record.id: record for record in all_records}
    merged: list[FactoryRecord] = []
    seen: set[str] = set()

    def add(record: FactoryRecord | None) -> None:
        if not record or record.id in seen:
            return
        if len(merged) >= max_records and record.id not in required_ids:
            return
        merged.append(record)
        seen.add(record.id)

    # Keep every factory actively used by a plan visible on the map.
    required_records = [by_id[factory_id] for factory_id in required_ids if factory_id in by_id]
    required_records.sort(
        key=lambda item: (
            item.category,
            -item.capacity_profile.get("capacity_index", 0),
            item.province,
            item.company_name,
        )
    )
    for record in required_records:
        add(record)

    # Preserve the balanced map sample so the user can still scan alternatives by family/region.
    for record in base_records:
        add(record)

    # Top up sparse categories after plan-required factories are added.
    for category in PART_CATEGORIES:
        category_count = sum(1 for record in merged if record.category == category)
        if category_count >= per_category_floor:
            continue
        candidates = [record for record in all_records if record.category == category and record.id not in seen]
        candidates.sort(
            key=lambda item: (
                -item.capacity_profile.get("capacity_index", 0),
                -item.capacity_units_30d,
                item.province,
                item.company_name,
            )
        )
        for record in candidates:
            if category_count >= per_category_floor or len(merged) >= max_records:
                break
            add(record)
            category_count += 1

    merged.sort(key=lambda item: (item.category, item.province, item.company_name))
    return merged


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def load_route_cache() -> dict:
    if not ROUTE_CACHE_JSON.exists():
        return {}
    try:
        return json.loads(ROUTE_CACHE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_route_cache(cache: dict) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ROUTE_CACHE_JSON.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def route_cache_key(start: dict, end: dict) -> str:
    return f"{float(start['lat']):.5f},{float(start['lon']):.5f}>{float(end['lat']):.5f},{float(end['lon']):.5f}"


def heuristic_road_factor(straight_km: float) -> float:
    if straight_km < 8:
        return 1.48
    if straight_km < 35:
        return 1.34
    if straight_km < 100:
        return 1.24
    return 1.17


def estimate_route_metrics(start: dict, end: dict, straight_km: float) -> dict:
    road_distance_km = round(straight_km * heuristic_road_factor(straight_km), 1)
    average_speed_kph = 62 if road_distance_km < 80 else 72
    duration_min = round((road_distance_km / average_speed_kph) * 60, 1)
    return {
        "straight_line_km": round(straight_km, 1),
        "road_distance_km": road_distance_km,
        "duration_min": duration_min,
        "route_geometry": [
            {"lat": start["lat"], "lon": start["lon"]},
            {"lat": end["lat"], "lon": end["lon"]},
        ],
        "routing_provider": "heuristic_detour_factor",
        "routing_status": "estimated",
        "routing_note": "Fallback road-distance estimate. Replace with approved routing API or self-hosted road graph.",
    }


def fetch_osrm_route(start: dict, end: dict) -> dict | None:
    coordinates = f"{start['lon']},{start['lat']};{end['lon']},{end['lat']}"
    url = (
        f"{OSRM_ROUTE_URL}/{coordinates}"
        "?overview=simplified&geometries=geojson&alternatives=false&steps=true"
    )
    try:
        with urllib.request.urlopen(url, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    routes = payload.get("routes") or []
    if not routes:
        return None
    route = routes[0]
    geometry = [
        {"lat": round(float(lat), 5), "lon": round(float(lon), 5)}
        for lon, lat in (route.get("geometry", {}).get("coordinates") or [])
    ]
    route_steps = summarize_osrm_steps(route.get("legs") or [])
    return {
        "road_distance_km": round(float(route.get("distance", 0)) / 1000, 1),
        "duration_min": round(float(route.get("duration", 0)) / 60, 1),
        "route_geometry": geometry,
        "route_steps": route_steps,
        "route_road_summary": road_summary_text(route_steps),
        "routing_provider": "OSRM public demo server",
        "routing_status": "routed",
        "routing_note": "Prototype route from OpenStreetMap road graph. Production should use approved provider or self-hosted OSRM.",
    }


def summarize_osrm_steps(legs: list[dict]) -> list[dict]:
    summary: dict[str, dict] = {}
    order: list[str] = []
    for leg in legs:
        for step in leg.get("steps") or []:
            distance_km = float(step.get("distance") or 0) / 1000
            if distance_km < 0.4:
                continue
            duration_min = float(step.get("duration") or 0) / 60
            road_name = step.get("name") or ""
            ref = step.get("ref") or ""
            destinations = step.get("destinations") or ""
            label_parts = [part for part in [ref, road_name] if part]
            label = " / ".join(label_parts) or destinations or "unnamed road"
            if label not in summary:
                summary[label] = {
                    "road": label,
                    "distance_km": 0.0,
                    "duration_min": 0.0,
                    "step_count": 0,
                }
                order.append(label)
            summary[label]["distance_km"] += distance_km
            summary[label]["duration_min"] += duration_min
            summary[label]["step_count"] += 1
    rows = sorted(summary.values(), key=lambda row: row["distance_km"], reverse=True)[:8]
    if not rows:
        return []
    rows_by_order = sorted(rows, key=lambda row: order.index(row["road"]) if row["road"] in order else len(order))
    return [
        {
            "road": row["road"],
            "distance_km": round(row["distance_km"], 1),
            "duration_min": round(row["duration_min"], 1),
            "step_count": row["step_count"],
        }
        for row in rows_by_order
    ]


def road_summary_text(route_steps: list[dict]) -> str:
    if not route_steps:
        return "road step summary unavailable"
    return " → ".join(
        f"{step['road']} {step['distance_km']}km" for step in route_steps[:5]
    )


def logistics_cost_fields(road_distance_km: float, duration_min: float) -> dict:
    fuel_liters = road_distance_km / LOGISTICS_COST_MODEL["fuel_efficiency_km_per_liter"]
    fuel_cost = fuel_liters * LOGISTICS_COST_MODEL["fuel_cost_krw_per_liter_placeholder"]
    labor_cost = (
        duration_min
        / 60
        * LOGISTICS_COST_MODEL["driver_count_per_trip"]
        * LOGISTICS_COST_MODEL["labor_cost_krw_per_hour_placeholder"]
    )
    return {
        "fuel_liters_per_trip": round(fuel_liters, 1),
        "driver_hours_per_trip": round(duration_min / 60, 2),
        "estimated_trip_cost_krw": int(round((fuel_cost + labor_cost) / 100) * 100),
    }


def route_metrics(start: dict, end: dict, straight_km: float, cache: dict) -> dict:
    key = route_cache_key(start, end)
    cached = cache.get(key)
    cached_is_usable = cached and (
        ROUTE_PROVIDER != "osrm"
        or (cached.get("routing_status") == "routed" and cached.get("route_geometry"))
    )
    if cached_is_usable:
        metrics = dict(cached)
        metrics["straight_line_km"] = round(straight_km, 1)
    elif ROUTE_PROVIDER == "osrm":
        fetched = fetch_osrm_route(start, end)
        if fetched:
            metrics = {
                "straight_line_km": round(straight_km, 1),
                **fetched,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            cache[key] = {field: value for field, value in metrics.items() if field != "straight_line_km"}
            time.sleep(0.08)
        else:
            metrics = estimate_route_metrics(start, end, straight_km)
    else:
        metrics = estimate_route_metrics(start, end, straight_km)

    metrics.update(logistics_cost_fields(metrics["road_distance_km"], metrics["duration_min"]))
    return metrics


def point_to_segment_km(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    mean_lat = math.radians((point[0] + start[0] + end[0]) / 3)
    px, py = point[1] * math.cos(mean_lat), point[0]
    ax, ay = start[1] * math.cos(mean_lat), start[0]
    bx, by = end[1] * math.cos(mean_lat), end[0]
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return haversine_km(point, start)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    proj = (ay + t * dy, (ax + t * dx) / math.cos(mean_lat))
    return haversine_km(point, proj)


def threat_risk(record: FactoryRecord, scenario: dict) -> tuple[float, str]:
    threat = scenario.get("threat")
    if not threat:
        return 0.12, "normal public-data uncertainty"
    path = [(point["lat"], point["lon"]) for point in threat["path"]]
    distances = [
        point_to_segment_km((record.lat, record.lon), path[index], path[index + 1])
        for index in range(len(path) - 1)
    ]
    nearest = min(distances)
    radius = threat["risk_radius_km"]
    probability = threat["probability"]
    if nearest >= radius * 2.1:
        return 0.16, f"{nearest:.0f} km from predicted corridor"
    corridor_factor = max(0.0, 1 - nearest / (radius * 2.1))
    risk = 0.16 + probability * 0.72 * corridor_factor
    return round(min(0.94, risk), 2), f"{nearest:.0f} km from predicted corridor"


def choose_hub(record: FactoryRecord, scenario: dict, risk: float) -> dict:
    threat = scenario.get("threat")
    ranked = []
    for hub in ASSEMBLY_HUBS:
        distance = haversine_km((record.lat, record.lon), (hub["lat"], hub["lon"]))
        score = distance
        if threat and risk > 0.55 and hub["id"] == "hub_pyeongtaek":
            score += 180
        if threat and risk > 0.55 and hub["id"] == "hub_daegu":
            score -= 80
        if scenario["id"] == "southern_port_disruption" and hub["id"] == "hub_daegu":
            score -= 70
        ranked.append((score, hub))
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1]


def route_destination_label(record: FactoryRecord) -> str:
    if record.priority_site_label:
        return f"{record.company_name} · {record.priority_site_label}"
    return record.company_name


def choose_assembly_destination(
    source: FactoryRecord,
    assembly_destinations: list[dict],
    scenario: dict,
    source_risk: float,
) -> dict:
    if not assembly_destinations:
        return {
            "record": source,
            "risk": source_risk,
            "status": "onsite",
        }
    ranked = []
    for destination in assembly_destinations:
        record = destination["record"]
        distance = haversine_km((source.lat, source.lon), (record.lat, record.lon))
        destination_risk = float(destination.get("risk") or 0.12)
        score = (
            distance
            + destination_risk * 180
            - float(record.priority_weight or 1.0) * 28
            - math.log(max(1, int(destination.get("planned_quantity") or record.capacity_units_30d))) * 4
            + stable_float(source.id + record.id + scenario["id"], 0, 16)
        )
        if scenario["id"] == "southern_port_disruption" and record.province in {"경상남도", "부산광역시", "울산광역시"}:
            score += 70
        if source_risk > 0.5 and destination_risk < source_risk:
            score -= 35
        ranked.append((score, destination))
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1]


def choose_reference_assembly_factory(
    record: FactoryRecord,
    scenario: dict,
    source_risk: float,
    records: list[FactoryRecord],
) -> tuple[FactoryRecord, float]:
    candidates = core_operating_assembly_records(records)
    if not candidates:
        return record, 0.0
    ranked = []
    for candidate in candidates:
        destination_risk, _ = threat_risk(candidate, scenario)
        distance = haversine_km((record.lat, record.lon), (candidate.lat, candidate.lon))
        score = (
            distance
            + destination_risk * 180
            - float(candidate.priority_weight or 1.0) * 28
            + stable_float(record.id + candidate.id + scenario["id"] + ":assembly_ref", 0, 12)
        )
        if scenario["id"] == "southern_port_disruption" and candidate.province in {"경상남도", "부산광역시", "울산광역시"}:
            score += 70
        if source_risk > 0.5 and destination_risk < source_risk:
            score -= 35
        ranked.append((score, candidate, distance))
    ranked.sort(key=lambda item: item[0])
    _, candidate, distance = ranked[0]
    return candidate, distance


def slug_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:8]}"


def priority_seed_slug(record: FactoryRecord) -> str:
    return str(record.factory_manage_no or "").replace("priority_drone_assembly_", "", 1)


def is_core_operating_assembly_record(record: FactoryRecord) -> bool:
    return (
        record.category == "drone_assembly"
        and record.is_priority_assembly_seed
        and priority_seed_slug(record) in CORE_OPERATING_DRONE_ASSEMBLY_SET
    )


def is_reserve_standby_assembly_record(record: FactoryRecord) -> bool:
    return (
        record.category == "drone_assembly"
        and record.is_priority_assembly_seed
        and priority_seed_slug(record) in RESERVE_STANDBY_DRONE_ASSEMBLY_SET
    )


def core_operating_assembly_records(records: list[FactoryRecord]) -> list[FactoryRecord]:
    cache_key = id(records)
    if cache_key not in CORE_OPERATING_ASSEMBLY_RECORD_CACHE:
        records_by_slug = {priority_seed_slug(item): item for item in records if is_core_operating_assembly_record(item)}
        CORE_OPERATING_ASSEMBLY_RECORD_CACHE[cache_key] = [
            records_by_slug[slug] for slug in CORE_OPERATING_DRONE_ASSEMBLY_SLUGS if slug in records_by_slug
        ]
    return CORE_OPERATING_ASSEMBLY_RECORD_CACHE[cache_key]


def reserve_standby_assembly_records(records: list[FactoryRecord]) -> list[FactoryRecord]:
    cache_key = id(records)
    if cache_key not in RESERVE_STANDBY_ASSEMBLY_RECORD_CACHE:
        records_by_slug = {priority_seed_slug(item): item for item in records if is_reserve_standby_assembly_record(item)}
        RESERVE_STANDBY_ASSEMBLY_RECORD_CACHE[cache_key] = [
            records_by_slug[slug] for slug in RESERVE_STANDBY_DRONE_ASSEMBLY_SLUGS if slug in records_by_slug
        ]
    return RESERVE_STANDBY_ASSEMBLY_RECORD_CACHE[cache_key]


def exposure_tier(score: float) -> str:
    if score >= 0.72:
        return "high"
    if score >= 0.52:
        return "elevated"
    if score >= 0.34:
        return "moderate"
    return "low"


def manufacturing_profile_for(record: FactoryRecord) -> dict:
    profile = record.capacity_profile
    capacity = max(25, int(record.capacity_units_30d or profile.get("predicted_output_units_30d") or 25))
    capacity_index = float(profile.get("capacity_index") or 0.45)
    confidence = float(profile.get("capacity_confidence") or record.confidence or 0.4)
    category_setup_days = {
        "drone_assembly": 5.5,
        "flight_stack": 7.0,
        "power": 6.5,
        "propulsion": 5.0,
        "sensor_payload": 6.0,
        "airframe": 4.5,
        "harness": 3.0,
        "qa_packaging": 2.5,
    }.get(record.category, 5.0)
    complexity = PART_CATEGORIES[record.category]["criticality"]
    setup_days = max(1.0, category_setup_days * (1.15 - 0.38 * confidence))
    nominal_daily = capacity / 30
    surge_multiplier = 1.08 + 0.24 * capacity_index
    yield_rate = clamp(0.82 + 0.11 * confidence + stable_float(record.id + ":yield", -0.015, 0.015), 0.78, 0.97)
    min_batch = max(10, int(round((nominal_daily * stable_float(record.id + ":batch", 1.6, 3.8)) / 10) * 10))
    bottlenecks = []
    if record.category in {"flight_stack", "sensor_payload"}:
        bottlenecks.extend(["SMT/inspection slot", "component QA"])
    if record.category == "power":
        bottlenecks.extend(["cell safety verification", "BMS compatibility"])
    if record.category == "propulsion":
        bottlenecks.extend(["magnet/feedstock continuity", "balancing/test bench"])
    if record.category == "airframe":
        bottlenecks.extend(["mold/tooling availability", "material grade verification"])
    if record.category == "drone_assembly":
        bottlenecks.extend(["integration labor", "final QA throughput"])
    if not bottlenecks:
        bottlenecks.extend(["line changeover", "QA sampling"])
    return {
        "profile_version": "d4d.manufacturing_speed_proxy.v0.1",
        "nominal_daily_output_units": int(round(nominal_daily)),
        "surge_daily_output_units": int(round(nominal_daily * surge_multiplier)),
        "setup_days_estimate": round(setup_days, 1),
        "first_article_days_estimate": round(setup_days + 1.5 + complexity * 1.8, 1),
        "min_batch_units": min_batch,
        "estimated_yield_rate": round(yield_rate, 3),
        "line_changeover_cost_index": round(clamp(0.28 + 0.48 * complexity + 0.12 * (1 - confidence)), 3),
        "speed_basis": "capacity profile + part-family complexity + deterministic placeholder variance",
        "primary_bottlenecks": bottlenecks,
        "data_status": "proxy_until_mes_or_factory_verification",
    }


def build_grid_risk_zones(records: list[FactoryRecord], energy_context: dict, kepco_context: dict) -> list[dict]:
    regional = energy_context.get("regional", {})
    electricity = regional.get("industrial_electricity_mwh_by_province", {})
    energy = regional.get("industrial_energy_toe_by_province", {})
    kepco_by_province = kepco_context.get("by_province", {})
    max_kepco_rows = max([item.get("large_customer_rows", 0) for item in kepco_by_province.values()] or [1])
    max_factory_count = max(1, max((sum(1 for item in records if item.province == province) for province in {r.province for r in records}), default=1))
    max_electricity = max([value for value in electricity.values() if value is not None] or [1])
    zones: list[dict] = []
    for province in sorted({record.province for record in records}):
        province_records = [record for record in records if record.province == province]
        if not province_records:
            continue
        lat, lon = PROVINCE_CENTROIDS.get(province, (36.3, 127.8))
        province_key = province_short_name(province)
        electricity_mwh = electricity.get(province_key)
        energy_toe = energy.get(province_key)
        kepco_region = kepco_by_province.get(normalize_province_name(province), {})
        factory_count_score = len(province_records) / max_factory_count
        electricity_score = (electricity_mwh or 0) / max_electricity
        kepco_customer_score = (kepco_region.get("large_customer_rows") or 0) / max_kepco_rows
        criticality_score = sum(PART_CATEGORIES[item.category]["criticality"] for item in province_records) / len(province_records)
        dependency_score = round(
            clamp(0.34 * factory_count_score + 0.30 * electricity_score + 0.18 * kepco_customer_score + 0.18 * criticality_score),
            3,
        )
        categories: dict[str, int] = {}
        for record in province_records:
            categories[record.category] = categories.get(record.category, 0) + 1
        top_categories = [
            {"part_category": category, "part_label": PART_CATEGORIES[category]["short_label"], "count": count}
            for category, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))[:4]
        ]
        zones.append(
            {
                "id": slug_id("grid_zone", province),
                "name": f"{province} industrial load-serving risk zone",
                "province": province,
                "lat": round(lat, 2),
                "lon": round(lon, 2),
                "precision_level": "province_centroid_proxy",
                "facility_class": "aggregated_load_serving_area_proxy",
                "industrial_electricity_mwh": round(electricity_mwh, 1) if electricity_mwh is not None else None,
                "industrial_energy_toe": round(energy_toe, 1) if energy_toe is not None else None,
                "kepco_large_customer_rows": kepco_region.get("large_customer_rows", 0),
                "kepco_top_substation_classes": kepco_region.get("top_substation_classes", []),
                "kepco_top_supply_classes": kepco_region.get("top_supply_classes", []),
                "kepco_top_equipment_basis": kepco_region.get("top_equipment_basis", []),
                "factory_count": len(province_records),
                "affected_factory_ids": [record.id for record in province_records],
                "top_part_categories": top_categories,
                "factory_concentration_score": round(factory_count_score, 3),
                "regional_electricity_score": round(electricity_score, 3),
                "kepco_large_customer_score": round(kepco_customer_score, 3),
                "criticality_score": round(criticality_score, 3),
                "grid_dependency_score": dependency_score,
                "exposure_tier": exposure_tier(dependency_score),
                "outage_radius_km_proxy": 65 if len(province_records) >= 6 else 45,
                "source": "KEA regional industrial electricity + KEPCO large-customer equipment context + candidate factory distribution",
                "limitations": POWER_GRID_RISK_MODEL["safe_modeling_boundary"],
            }
        )
    zones.sort(key=lambda item: (-item["grid_dependency_score"], item["province"]))
    return zones


def grid_profile_for_factory(record: FactoryRecord, zones_by_province: dict[str, dict]) -> dict:
    zone = zones_by_province.get(record.province)
    zone_score = float(zone.get("grid_dependency_score") if zone else 0.35)
    category_weight = {
        "power": 0.92,
        "flight_stack": 0.86,
        "propulsion": 0.82,
        "sensor_payload": 0.78,
        "drone_assembly": 0.76,
        "airframe": 0.68,
        "harness": 0.62,
        "qa_packaging": 0.54,
    }.get(record.category, 0.66)
    energy_score = float(record.energy_profile.get("capacity_evidence_score") or 0.45)
    dependency = round(clamp(0.45 * zone_score + 0.30 * energy_score + 0.25 * category_weight), 3)
    backup_hours = round(stable_float(record.id + ":backup", 4, 30) * (1.12 - 0.45 * dependency), 1)
    outage_multiplier = round(clamp(1 - dependency * 0.62, 0.28, 0.92), 3)
    return {
        "profile_version": POWER_GRID_RISK_MODEL["profile_version"],
        "primary_grid_zone_id": zone.get("id") if zone else None,
        "primary_grid_zone_name": zone.get("name") if zone else None,
        "dependency_model": "regional_load_zone_proxy",
        "grid_dependency_score": dependency,
        "outage_output_multiplier": outage_multiplier,
        "estimated_backup_hours": backup_hours,
        "manual_override_required": dependency >= 0.68,
        "verification_need": [
            "contracted power and peak demand",
            "customer-side feeder/substation relationship",
            "backup generator capacity and fuel stock",
            "critical process restart time after outage",
        ],
        "limitations": POWER_GRID_RISK_MODEL["safe_modeling_boundary"],
    }


def build_grid_disruption_scenarios(records: list[FactoryRecord], zones: list[dict]) -> list[dict]:
    scenarios: list[dict] = []
    for index, zone in enumerate(zones[:4], start=1):
        affected = [record for record in records if record.id in set(zone.get("affected_factory_ids", []))]
        affected.sort(key=lambda item: (-item.capacity_units_30d, item.category, item.company_name))
        capacity_at_risk = sum(record.capacity_units_30d for record in affected)
        part_counts: dict[str, int] = {}
        for record in affected:
            part_counts[record.category] = part_counts.get(record.category, 0) + 1
        scenarios.append(
            {
                "id": f"grid_degradation_{index}_{zone['id']}",
                "name": f"{zone['province']} load-serving degradation",
                "event_type": "grid_zone_degraded",
                "safe_boundary": "Coarse continuity-planning scenario; not an electric-facility targeting model.",
                "affected_grid_zone_id": zone["id"],
                "affected_grid_zone_name": zone["name"],
                "assumed_availability_multiplier": round(clamp(1 - 0.54 * zone["grid_dependency_score"], 0.38, 0.88), 3),
                "affected_factory_count": len(affected),
                "affected_factory_ids": [record.id for record in affected],
                "capacity_units_30d_at_risk": int(capacity_at_risk),
                "part_family_exposure": [
                    {
                        "part_category": category,
                        "part_label": PART_CATEGORIES[category]["short_label"],
                        "factory_count": count,
                    }
                    for category, count in sorted(part_counts.items(), key=lambda item: (-item[1], item[0]))
                ],
                "recommended_reconfiguration": [
                    "reduce new allocations to affected factories until power status is verified",
                    "prioritize factories with backup power and lower grid dependency score",
                    "hold in-transit shipments only when receiving factory outage probability crosses threshold",
                ],
            }
        )
    return scenarios


def build_inventory_wip(records: list[FactoryRecord], baseline_plan: dict) -> list[dict]:
    committed_by_factory: dict[str, int] = {}
    for supplier in baseline_plan.get("selected_suppliers", []):
        committed_by_factory[supplier["factory_id"]] = committed_by_factory.get(supplier["factory_id"], 0) + int(
            supplier.get("requested_quantity") or 0
        )
    rows: list[dict] = []
    for record in records:
        manufacturing = manufacturing_profile_for(record)
        capacity = int(record.capacity_units_30d)
        daily = max(1, int(manufacturing["nominal_daily_output_units"]))
        finished = int(round(capacity * stable_float(record.id + ":fg", 0.035, 0.12) / 5) * 5)
        wip = int(round(capacity * stable_float(record.id + ":wip", 0.045, 0.16) / 5) * 5)
        qa_hold = int(round(capacity * stable_float(record.id + ":qa", 0.008, 0.04) / 5) * 5)
        committed = committed_by_factory.get(record.id, 0)
        available = max(0, finished + int(wip * 0.42) - qa_hold - int(committed * 0.08))
        raw_days = stable_float(record.id + ":rawdays", 5, 24)
        rows.append(
            {
                "id": f"inv_{record.id}_{record.category}",
                "node_type": "factory",
                "factory_id": record.id,
                "factory_name": record.company_name,
                "part_category": record.category,
                "part_label": PART_CATEGORIES[record.category]["short_label"],
                "finished_goods_units": max(0, finished),
                "wip_units": max(0, wip),
                "qa_hold_units": max(0, qa_hold),
                "committed_units": committed,
                "available_to_ship_units": max(0, available),
                "raw_material_days_on_hand": round(raw_days, 1),
                "max_daily_output_units": daily,
                "days_to_clear_wip": round(wip / daily, 1) if daily else None,
                "inventory_confidence": round(clamp(0.24 + 0.44 * record.capacity_profile.get("capacity_confidence", 0.4)), 3),
                "data_status": "synthetic_placeholder_for_erp_mes_join",
                "source": "derived from demo plan and public capacity proxy; replace with ERP/MES inventory feed",
            }
        )
    return rows


def build_frozen_orders(baseline_plan: dict) -> list[dict]:
    rows: list[dict] = []
    suppliers = sorted(
        baseline_plan.get("selected_suppliers", []),
        key=lambda item: (-int(item.get("requested_quantity") or 0), item.get("factory_id", "")),
    )
    for index, supplier in enumerate(suppliers[:24], start=1):
        frozen_qty = int(round(int(supplier.get("requested_quantity") or 0) * stable_float(supplier["factory_id"] + ":freeze", 0.18, 0.52)))
        if frozen_qty <= 0:
            continue
        rows.append(
            {
                "id": f"ord_frozen_{index:03d}",
                "source_plan_id": baseline_plan.get("id"),
                "factory_id": supplier["factory_id"],
                "hub_id": supplier["hub_id"],
                "destination_type": supplier.get("destination_type"),
                "destination_factory_id": supplier.get("destination_factory_id"),
                "destination_name": supplier.get("destination_name") or supplier.get("hub_name"),
                "part_category": supplier["part_category"],
                "part_label": supplier["part_label"],
                "frozen_quantity_units": frozen_qty,
                "freeze_until_day": int(round(stable_float(supplier["factory_id"] + ":freeze_day", 2, 8))),
                "order_status": "released_to_factory",
                "cancelability": "locked_with_manual_override",
                "reroute_allowed_after_day": int(round(stable_float(supplier["factory_id"] + ":reroute_day", 3, 10))),
                "decision_rule": "do not reallocate inside freeze window unless receiving final assembly factory or route risk exceeds emergency threshold",
                "data_status": "synthetic_placeholder_for_erp_procurement_join",
            }
        )
    return rows


def point_along_route(route: dict, ratio: float) -> dict:
    points = route.get("route_geometry") or [route.get("from"), route.get("to")]
    points = [point for point in points if point]
    if len(points) < 2:
        return route.get("from") or {"lat": None, "lon": None}
    start = points[0]
    end = points[-1]
    return {
        "lat": round(float(start["lat"]) + (float(end["lat"]) - float(start["lat"])) * ratio, 5),
        "lon": round(float(start["lon"]) + (float(end["lon"]) - float(start["lon"])) * ratio, 5),
    }


def build_in_transit_shipments(baseline_plan: dict) -> list[dict]:
    rows: list[dict] = []
    production_routes = sorted(
        baseline_plan.get("route_segments", []),
        key=lambda item: (-int(item.get("quantity") or 0), item.get("id", "")),
    )[:18]
    resource_routes = sorted(
        baseline_plan.get("resource_route_segments", []),
        key=lambda item: (-int(item.get("quantity_kg_30d") or 0), item.get("id", "")),
    )[:10]
    index = 1
    for route in production_routes:
        progress = stable_float(route["id"] + ":progress", 0.12, 0.88)
        quantity = int(round(int(route.get("quantity") or 0) * stable_float(route["id"] + ":shipqty", 0.06, 0.18)))
        rows.append(
            {
                "id": f"ship_prod_{index:03d}",
                "shipment_kind": "component_factory_to_final_assembly_factory",
                "route_id": route["id"],
                "factory_id": route["factory_id"],
                "hub_id": route["hub_id"],
                "destination_type": route.get("destination_type"),
                "destination_factory_id": route.get("destination_factory_id"),
                "destination_name": route.get("destination_name") or route.get("hub_name"),
                "part_category": route["part_category"],
                "part_label": route["part_label"],
                "quantity_units": max(1, quantity),
                "progress_ratio": round(progress, 3),
                "current_position": point_along_route(route, progress),
                "eta_hours": round((1 - progress) * float(route.get("duration_min") or 0) / 60, 2),
                "status": "in_transit",
                "threat_response_options": ["continue", "hold_at_safe_yard", "reroute_to_alternate_final_assembly_factory"],
                "data_status": "synthetic_placeholder_for_tms_join",
            }
        )
        index += 1
    for route in resource_routes:
        progress = stable_float(route["id"] + ":progress", 0.1, 0.82)
        quantity = int(round(int(route.get("quantity_kg_30d") or 0) * stable_float(route["id"] + ":shipqty", 0.05, 0.2)))
        rows.append(
            {
                "id": f"ship_res_{index:03d}",
                "shipment_kind": "resource_to_factory",
                "route_id": route["id"],
                "resource_id": route["resource_id"],
                "target_factory_id": route["target_factory_id"],
                "resource_category": route["resource_category"],
                "resource_label": route["resource_label"],
                "target_part_category": route["target_part_category"],
                "quantity_kg": max(1, quantity),
                "progress_ratio": round(progress, 3),
                "current_position": point_along_route(route, progress),
                "eta_hours": round((1 - progress) * float(route.get("duration_min") or 0) / 60, 2),
                "status": "in_transit",
                "threat_response_options": ["continue", "hold_at_safe_yard", "return_to_resource_node"],
                "data_status": "synthetic_placeholder_for_tms_join",
            }
        )
        index += 1
    return rows


def mission_mix_material_kg_per_drone(mission_mix: list[dict] | None = None) -> dict[str, float]:
    profiles = {profile["profile_id"]: profile for profile in DRONE_MISSION_PROFILES}
    mix = mission_mix or DEFAULT_DRONE_MISSION_MIX
    total_share = sum(float(item.get("share") or 0) for item in mix) or 1
    per_drone = {material_id: 0.0 for material_id in RAW_MATERIAL_CATALOG}
    for item in mix:
        profile = profiles.get(item.get("profile_id"))
        if not profile:
            continue
        share = float(item.get("share") or 0) / total_share
        for material_id, kg in profile.get("material_kg_per_drone", {}).items():
            per_drone[material_id] = per_drone.get(material_id, 0.0) + share * float(kg)
    return {material_id: round(kg, 4) for material_id, kg in per_drone.items()}


def part_material_kg_per_unit(material_id: str, part_category: str) -> float:
    kg_per_drone = mission_mix_material_kg_per_drone().get(material_id, 0.0)
    feeds = RAW_MATERIAL_CATALOG[material_id]["feeds_part_categories"]
    if part_category not in feeds:
        return 0.0
    bom_total = sum(PART_CATEGORIES[category]["bom_quantity"] for category in feeds)
    return kg_per_drone / max(1, bom_total)


def material_requirements_for_target(target_drones: int, mission_mix: list[dict] | None = None) -> list[dict]:
    per_drone = mission_mix_material_kg_per_drone(mission_mix)
    rows = []
    for material_id, spec in RAW_MATERIAL_CATALOG.items():
        kg_per_drone = per_drone.get(material_id, 0.0)
        rows.append(
            {
                "material_id": material_id,
                "material_label": spec["label"],
                "unit": spec["unit"],
                "kg_per_drone_weighted": kg_per_drone,
                "required_kg_30d": int(round(target_drones * kg_per_drone)),
                "feeds_part_categories": list(spec["feeds_part_categories"]),
                "import_dependency": spec["import_dependency"],
                "verification_need": spec["verification_need"],
            }
        )
    return rows


def source_by_id() -> dict[str, dict]:
    return {source["id"]: source for source in FOREIGN_MATERIAL_SOURCES}


def port_by_id() -> dict[str, dict]:
    return {port["id"]: port for port in IMPORT_PORTS}


def route_geometry_distance_km(points: list[dict]) -> float:
    if len(points) < 2:
        return 0.0
    return sum(
        haversine_km((start["lat"], start["lon"]), (end["lat"], end["lon"]))
        for start, end in zip(points, points[1:])
    )


def maritime_route_geometry(source: dict, end: dict, route_id: str) -> list[dict]:
    start = {"lat": source["lat"], "lon": source["lon"]}
    waypoints = SEA_CORRIDOR_WAYPOINTS.get(source["id"])
    if waypoints:
        return [
            start,
            *[{"lat": point["lat"], "lon": point["lon"]} for point in waypoints],
            {"lat": end["lat"], "lon": end["lon"]},
        ]
    midpoint = {
        "lat": round((source["lat"] + end["lat"]) / 2 + stable_float(route_id + ":lat", -0.55, 0.55), 5),
        "lon": round((source["lon"] + end["lon"]) / 2 + stable_float(route_id + ":lon", -0.35, 0.35), 5),
    }
    return [
        start,
        midpoint,
        {"lat": end["lat"], "lon": end["lon"]},
    ]


def maritime_route_for_source(source: dict, scenario: dict) -> dict:
    ports = port_by_id()
    preferred_port = ports[source["preferred_port_id"]]
    route_id = f"sea_{scenario['id']}_{source['id']}_{preferred_port['id']}"
    geometry = maritime_route_geometry(source, preferred_port, route_id)
    distance_km = route_geometry_distance_km(geometry)
    distance_nm = distance_km / 1.852
    base_risk = stable_float(route_id + ":risk", 0.12, 0.26)
    port_penalty = 0.0
    if scenario["id"] == "southern_port_disruption" and preferred_port["id"] in {"port_busan", "port_ulsan"}:
        port_penalty = 0.28
    if scenario["id"] == "western_axis_threat" and preferred_port["id"] == "port_donghae":
        port_penalty = -0.04
    route_risk = round(clamp(base_risk + port_penalty, 0.05, 0.82), 3)
    capacity_multiplier = clamp(1 - route_risk * 0.46, 0.42, 0.95)
    total_capacity = int(round(sum(source["monthly_capacity_kg"] for _ in [0]) * capacity_multiplier))
    return {
        "id": route_id,
        "scenario_id": scenario["id"],
        "route_type": "maritime_import",
        "source_id": source["id"],
        "source_name": source["name"],
        "source_country": source["country"],
        "origin_port_name": source["port_name"],
        "destination_port_id": preferred_port["id"],
        "destination_port_name": preferred_port["name"],
        "material_ids": list(source["material_ids"]),
        "distance_nm": round(distance_nm, 1),
        "duration_hours_estimate": round(distance_nm / 15.5, 1),
        "risk_score": route_risk,
        "import_capacity_kg_30d": total_capacity,
        "status": "east_sea_preferred" if preferred_port["coast"] == "east" else "southern_port_link",
        "routing_status": "maritime_corridor_estimate",
        "route_geometry_source": (
            "coastal_waypoint_corridor_v0.2" if source["id"] in SEA_CORRIDOR_WAYPOINTS else "estimated_midpoint"
        ),
        "route_geometry": geometry,
        "from": {"lat": source["lat"], "lon": source["lon"]},
        "to": {"lat": preferred_port["lat"], "lon": preferred_port["lon"]},
        "source": MARITIME_CORRIDOR_MODEL["safe_boundary"],
    }


def selected_factories_for_material(plan: dict, material_id: str) -> list[dict]:
    feeds = set(RAW_MATERIAL_CATALOG[material_id]["feeds_part_categories"])
    rows = [supplier for supplier in plan.get("selected_suppliers", []) if supplier.get("part_category") in feeds]
    rows.sort(key=lambda item: (-int(item.get("requested_quantity") or 0), item.get("factory_id", "")))
    return rows


def material_factory_inventory_kg(plan: dict, material_id: str) -> int:
    kg_per_drone = mission_mix_material_kg_per_drone().get(material_id, 0)
    required = plan["target_drones"] * kg_per_drone
    low, high = RAW_MATERIAL_CATALOG[material_id]["domestic_inventory_share_range"]
    share = stable_float(plan["id"] + material_id + ":inventory", low, high)
    return int(round(required * share))


def domestic_resource_supply_kg(plan: dict, material_id: str) -> int:
    resource_category = RAW_MATERIAL_CATALOG[material_id].get("linked_resource_category")
    if not resource_category:
        return 0
    return int(
        sum(
            item.get("allocated_kg_30d") or 0
            for item in plan.get("resource_supply_summary", [])
            if item.get("resource_category") == resource_category
        )
    )


def build_material_supply_for_plan(
    plan: dict,
    records: list[FactoryRecord],
    scenario: dict,
    route_cache: dict,
) -> None:
    factories_by_id = {record.id: record for record in records}
    material_requirements = material_requirements_for_target(plan["target_drones"])
    maritime_routes = [maritime_route_for_source(source, scenario) for source in FOREIGN_MATERIAL_SOURCES]
    import_capacity_by_material: dict[str, int] = {material_id: 0 for material_id in RAW_MATERIAL_CATALOG}
    for route in maritime_routes:
        per_material_capacity = int(route["import_capacity_kg_30d"] / max(1, len(route["material_ids"])))
        for material_id in route["material_ids"]:
            import_capacity_by_material[material_id] = import_capacity_by_material.get(material_id, 0) + per_material_capacity

    port_routes: list[dict] = []
    summary: list[dict] = []
    material_feasible_values: list[int] = []
    ports = port_by_id()
    maritime_by_material = {
        material_id: [route for route in maritime_routes if material_id in route["material_ids"]]
        for material_id in RAW_MATERIAL_CATALOG
    }
    for requirement in material_requirements:
        material_id = requirement["material_id"]
        required_kg = int(requirement["required_kg_30d"])
        inventory_kg = material_factory_inventory_kg(plan, material_id)
        domestic_kg = domestic_resource_supply_kg(plan, material_id)
        import_kg = import_capacity_by_material.get(material_id, 0)
        total_available = inventory_kg + domestic_kg + import_kg
        kg_per_drone = float(requirement["kg_per_drone_weighted"] or 0)
        feasible_drones = int(total_available / kg_per_drone) if kg_per_drone > 0 else plan["target_drones"]
        material_feasible_values.append(feasible_drones)
        shortage = max(0, required_kg - total_available)
        coverage = total_available / required_kg if required_kg else 1

        target_suppliers = selected_factories_for_material(plan, material_id)[:4]
        route_import_available = import_kg
        for rank, supplier in enumerate(target_suppliers, start=1):
            factory = factories_by_id.get(supplier["factory_id"])
            if not factory or route_import_available <= 0:
                continue
            sea_route = maritime_by_material.get(material_id, [None])[0]
            if not sea_route:
                continue
            port = ports[sea_route["destination_port_id"]]
            supplier_need = int((supplier.get("requested_quantity") or 0) * part_material_kg_per_unit(material_id, supplier["part_category"]))
            quantity = max(1, min(route_import_available, supplier_need or int(import_kg / max(1, len(target_suppliers)))))
            distance = haversine_km((port["lat"], port["lon"]), (factory.lat, factory.lon))
            route_metric_fields = route_metrics(
                {"lat": port["lat"], "lon": port["lon"]},
                {"lat": factory.lat, "lon": factory.lon},
                distance,
                route_cache,
            )
            port_routes.append(
                {
                    "id": f"matroad_{plan['id']}_{material_id}_{port['id']}_{factory.id}_{rank}",
                    "scenario_id": plan["id"],
                    "route_type": "port_to_factory_material",
                    "material_id": material_id,
                    "material_label": RAW_MATERIAL_CATALOG[material_id]["short_label"],
                    "source_maritime_route_id": sea_route["id"],
                    "port_id": port["id"],
                    "port_name": port["name"],
                    "target_factory_id": factory.id,
                    "target_factory_name": factory.company_name,
                    "target_part_category": supplier["part_category"],
                    "quantity_kg_30d": int(quantity),
                    "distance_km": route_metric_fields["road_distance_km"],
                    **route_metric_fields,
                    "status": "import-to-factory",
                    "from": {"lat": port["lat"], "lon": port["lon"]},
                    "to": {"lat": factory.lat, "lon": factory.lon},
                }
            )
            route_import_available -= quantity

        summary.append(
            {
                **requirement,
                "existing_factory_inventory_kg": inventory_kg,
                "domestic_resource_supply_kg": domestic_kg,
                "import_supply_kg_30d": import_kg,
                "total_available_kg_30d": int(total_available),
                "shortage_kg_30d": int(shortage),
                "coverage_ratio": round(min(1.0, coverage), 3),
                "material_feasible_drones_30d": feasible_drones,
                "primary_import_route_ids": [route["id"] for route in maritime_by_material.get(material_id, [])],
                "target_factory_count": len(target_suppliers),
            }
        )

    plan["drone_mission_mix"] = DEFAULT_DRONE_MISSION_MIX
    plan["raw_material_supply_summary"] = summary
    plan["maritime_import_route_segments"] = maritime_routes
    plan["port_to_factory_material_routes"] = port_routes
    plan["factory_capacity_possible_drones_30d"] = plan["possible_drones_30d"]
    plan["raw_material_constrained_possible_drones_30d"] = min(material_feasible_values) if material_feasible_values else plan["target_drones"]
    plan["possible_drones_30d"] = int(min(plan["factory_capacity_possible_drones_30d"], plan["raw_material_constrained_possible_drones_30d"]))
    if plan["possible_drones_30d"] < plan["factory_capacity_possible_drones_30d"]:
        bottleneck = min(summary, key=lambda item: item["material_feasible_drones_30d"])
        plan["bottleneck_part_label"] = f"{bottleneck['material_label']} material"
        plan["bottleneck_part_category"] = bottleneck["material_id"]
        plan["bottleneck_coverage_ratio"] = bottleneck["coverage_ratio"]


def component_variant_share(spec: dict) -> float:
    variant = spec.get("variant", "all")
    fiber_share = float(BLOCKADE_DEMAND_MODEL["fiber_variant_share"])
    if variant == "fiber_only":
        return fiber_share
    if variant == "rf_only":
        return max(0.0, 1 - fiber_share)
    return 1.0


def category_allocated_units(plan: dict, category: str) -> int:
    for row in plan.get("category_summary", []):
        if row.get("part_category") == category:
            return int(row.get("allocated_units") or 0)
    return int(PART_CATEGORIES.get(category, {}).get("base_capacity", 0))


def component_daily_demand(spec: dict, demand_model: dict = BLOCKADE_DEMAND_MODEL) -> float:
    required_daily = float(demand_model["required_fpv_class_units_per_day"])
    return required_daily * component_variant_share(spec) * float(spec["base_units_per_drone"]) * float(spec["attrition_factor"])


def component_line_capacity_daily(plan: dict, component_id: str, spec: dict) -> float:
    category_30d_units = category_allocated_units(plan, spec["part_category"])
    category_daily = category_30d_units / 30
    ratio = stable_float(f"{plan['id']}:{component_id}:line", *spec["line_output_ratio_range"])
    return round(max(0.0, category_daily * ratio), 1)


def inventory_days_for(entity_id: str, spec: dict, scenario_id: str) -> dict:
    low, high = spec["inventory_days_range"]
    likely = stable_float(f"{scenario_id}:{entity_id}:inventory_days", low, high)
    return {
        "p10": round(max(0.5, likely * 0.64), 1),
        "likely": round(likely, 1),
        "p90": round(likely * 1.42, 1),
    }


def ramp_ready_day_for(component_id: str, spec: dict, scenario_id: str) -> int:
    low, high = spec["ramp_ready_day_range"]
    return int(round(stable_float(f"{scenario_id}:{component_id}:ramp", low, high)))


def build_subcomponent_constraints(component_rows: list[dict], scenario_id: str) -> list[dict]:
    demand_by_subcomponent: dict[str, float] = {key: 0.0 for key in SUBCOMPONENT_CATALOG}
    linked_components: dict[str, set[str]] = {key: set() for key in SUBCOMPONENT_CATALOG}
    for row in component_rows:
        for sub_id, qty in COMPONENT_SUBCOMPONENT_BOM.get(row["component_id"], {}).items():
            demand_by_subcomponent[sub_id] += float(row["daily_demand_units"]) * float(qty)
            linked_components[sub_id].add(row["component_id"])

    rows = []
    for sub_id, spec in SUBCOMPONENT_CATALOG.items():
        daily_demand = demand_by_subcomponent.get(sub_id, 0.0)
        days = inventory_days_for(sub_id, spec, scenario_id)
        inventory_likely = daily_demand * days["likely"]
        leakage = daily_demand * BLOCKADE_DEMAND_MODEL["leakage_scenarios"][0]["leakage_pct"]
        net_burn = max(0.0, daily_demand - leakage)
        likely_survival = inventory_likely / net_burn if net_burn else 999
        rows.append(
            {
                "subcomponent_id": sub_id,
                "label": spec["label"],
                "type": spec["type"],
                "unit": spec["unit"],
                "import_dependency": spec["import_dependency"],
                "daily_demand_units": round(daily_demand, 1),
                "effective_inventory_units": int(round(inventory_likely)),
                "net_burn_units_per_day": round(net_burn, 1),
                "survival_days": {
                    "p10": days["p10"],
                    "likely": round(likely_survival, 1),
                    "p90": days["p90"],
                },
                "linked_component_ids": sorted(linked_components.get(sub_id, set())),
                "verification_need": spec["verification_need"],
            }
        )
    rows.sort(key=lambda item: item["survival_days"]["likely"])
    return rows


def build_component_survival_for_plan(plan: dict, scenario: dict) -> None:
    component_rows: list[dict] = []
    for component_id, spec in COMPONENT_CATALOG.items():
        daily_demand = component_daily_demand(spec)
        line_daily = component_line_capacity_daily(plan, component_id, spec)
        ramp_ready_day = ramp_ready_day_for(component_id, spec, plan["id"])
        days = inventory_days_for(component_id, spec, plan["id"])
        inventory_likely = daily_demand * days["likely"]
        domestic_before_ramp = line_daily * 0.18
        leakage_daily = daily_demand * BLOCKADE_DEMAND_MODEL["leakage_scenarios"][0]["leakage_pct"]
        domestic_effective = domestic_before_ramp + leakage_daily
        net_burn = max(0.0, daily_demand - domestic_effective)
        net_burn_low = max(0.0, daily_demand * 0.88 - domestic_effective * 1.08)
        net_burn_high = max(0.0, daily_demand * 1.15 - domestic_effective * 0.82)
        survival_likely = inventory_likely / net_burn if net_burn else 999
        survival_p10 = (daily_demand * days["p10"]) / net_burn_high if net_burn_high else 999
        survival_p90 = (daily_demand * days["p90"]) / net_burn_low if net_burn_low else 999
        ramp_gap = max(0, round(ramp_ready_day - survival_likely, 1))
        component_rows.append(
            {
                "component_id": component_id,
                "component_label": spec["label"],
                "part_category": spec["part_category"],
                "part_label": PART_CATEGORIES[spec["part_category"]]["short_label"],
                "unit": spec["unit"],
                "variant": spec["variant"],
                "base_units_per_drone": spec["base_units_per_drone"],
                "attrition_factor": spec["attrition_factor"],
                "effective_units_per_drone": round(
                    component_variant_share(spec) * float(spec["base_units_per_drone"]) * float(spec["attrition_factor"]),
                    3,
                ),
                "daily_demand_units": round(daily_demand, 1),
                "domestic_line_capacity_units_per_day": round(line_daily, 1),
                "domestic_output_before_ramp_units_per_day": round(domestic_before_ramp, 1),
                "effective_inventory_units": int(round(inventory_likely)),
                "net_burn_units_per_day": round(net_burn, 1),
                "survival_days": {
                    "p10": round(survival_p10, 1),
                    "likely": round(survival_likely, 1),
                    "p90": round(survival_p90, 1),
                },
                "ramp_ready_day": ramp_ready_day,
                "ramp_gap_days": ramp_gap,
                "localization_difficulty": spec["localization_difficulty"],
                "vulnerability": spec["vulnerability"],
                "subcomponent_constraints": sorted(COMPONENT_SUBCOMPONENT_BOM.get(component_id, {}).keys()),
                "factory_search_hint": spec["factory_search_hint"],
                "verification_need": spec["verification_need"],
            }
        )

    component_rows.sort(key=lambda item: item["survival_days"]["likely"])
    for rank, row in enumerate(component_rows, start=1):
        row["bottleneck_rank"] = rank
        row["is_bottleneck"] = rank == 1

    subcomponent_rows = build_subcomponent_constraints(component_rows, plan["id"])
    bottleneck = component_rows[0] if component_rows else None
    sub_bottleneck = subcomponent_rows[0] if subcomponent_rows else None
    total_producible_likely = int(
        min(
            (row["effective_inventory_units"] / max(0.0001, row["effective_units_per_drone"]))
            for row in component_rows
            if row["effective_units_per_drone"] > 0
        )
    )
    total_producible_p10 = int(total_producible_likely * 0.68)
    total_producible_p90 = int(total_producible_likely * 1.55)
    a_end = int(round(bottleneck["survival_days"]["likely"])) if bottleneck else 0
    valley_end = int(max(row["ramp_ready_day"] for row in component_rows[:5])) if component_rows else 0
    required_daily = int(round(BLOCKADE_DEMAND_MODEL["required_fpv_class_units_per_day"]))
    after_ramp_daily = int(
        min(
            required_daily,
            min(
                row["domestic_line_capacity_units_per_day"] / max(0.0001, row["effective_units_per_drone"])
                for row in component_rows
                if row["effective_units_per_drone"] > 0
            ),
        )
    )
    valley_daily = max(0, int(after_ramp_daily * 0.22))
    phase_curve = [
        {"day": 1, "units": required_daily, "phase": "A_STOCK_DRAW"},
        {"day": max(1, a_end), "units": required_daily, "phase": "A_STOCK_DRAW"},
        {"day": max(1, a_end + 1), "units": valley_daily, "phase": "VALLEY"},
        {"day": max(a_end + 1, valley_end), "units": valley_daily, "phase": "VALLEY"},
        {"day": max(a_end + 2, valley_end + 1), "units": after_ramp_daily, "phase": "B_RAMPED_DOMESTIC"},
        {"day": 90, "units": after_ramp_daily, "phase": "B_RAMPED_DOMESTIC"},
    ]
    plan["component_survival_summary"] = component_rows
    plan["subcomponent_survival_summary"] = subcomponent_rows
    plan["blockade_phase_curve"] = phase_curve
    plan["blockade_survival_headline"] = {
        "mode": "FULL_BLOCKADE",
        "required_units_per_day": required_daily,
        "blockade_total_producible": {
            "p10": total_producible_p10,
            "likely": total_producible_likely,
            "p90": total_producible_p90,
        },
        "survival_days": bottleneck["survival_days"] if bottleneck else {"p10": 0, "likely": 0, "p90": 0},
        "valley": {
            "start_day": max(1, a_end + 1),
            "end_day": max(a_end + 1, valley_end),
            "depth_units_per_day": max(0, required_daily - valley_daily),
        },
        "bottleneck": {
            "id": bottleneck["component_id"] if bottleneck else None,
            "label": bottleneck["component_label"] if bottleneck else None,
            "type": "COMPONENT",
        },
        "subcomponent_bottleneck": {
            "id": sub_bottleneck["subcomponent_id"] if sub_bottleneck else None,
            "label": sub_bottleneck["label"] if sub_bottleneck else None,
            "type": sub_bottleneck["type"] if sub_bottleneck else None,
        },
        "fiber_variant_share": BLOCKADE_DEMAND_MODEL["fiber_variant_share"],
        "airlift_scenario": BLOCKADE_DEMAND_MODEL["leakage_scenarios"][0]["airlift_scenario"],
        "leakage_pct": BLOCKADE_DEMAND_MODEL["leakage_scenarios"][0]["leakage_pct"],
        "model_limitations": [
            "Synthetic inventory/ramp defaults; replace with ERP/MES/procurement feeds.",
            "Component-level demand is FPV-class demo profile only; medium/large systems are future profile extensions.",
            "No payload, targeting, or build instruction data is included.",
        ],
    }


def build_resource_routes(
    resources: list[ResourceRecord],
    factories: list[FactoryRecord],
    scenario: dict,
    route_cache: dict,
) -> tuple[list[dict], list[dict]]:
    routes: list[dict] = []
    summary: list[dict] = []
    for category, spec in RESOURCE_CATEGORIES.items():
        candidates = [record for record in resources if record.resource_category == category]
        target_factories = [
            record for record in factories if record.category in set(spec["target_part_categories"])
        ]
        ranked = []
        for resource in candidates:
            risk, risk_reason = threat_risk(resource, scenario)
            adjusted_capacity = int(resource.capacity_kg_30d * (1 - risk * scenario["risk_weight"] * 0.45))
            energy_evidence = resource.energy_profile.get("capacity_evidence_score", 0.45)
            score = (
                resource.confidence * 100
                + math.log(max(1, adjusted_capacity)) * 5
                + energy_evidence * 18
                - risk * 55
                - stable_float(resource.id + scenario["id"], 0, 5)
            )
            ranked.append((score, resource, risk, risk_reason, adjusted_capacity))
        ranked.sort(reverse=True, key=lambda item: item[0])

        allocation = 0
        selected_count = 0
        for _, resource, risk, risk_reason, adjusted_capacity in ranked[:4]:
            if not target_factories or adjusted_capacity <= 0:
                continue
            target = min(
                target_factories,
                key=lambda factory: (
                    haversine_km((resource.lat, resource.lon), (factory.lat, factory.lon))
                    - factory.confidence * 18
                    + stable_float(resource.id + factory.id, 0, 8)
                ),
            )
            distance = haversine_km((resource.lat, resource.lon), (target.lat, target.lon))
            route_metric_fields = route_metrics(
                {"lat": resource.lat, "lon": resource.lon},
                {"lat": target.lat, "lon": target.lon},
                distance,
                route_cache,
            )
            status = "resource-primary"
            if scenario.get("threat") and risk > 0.36:
                status = "resource-reroute"
            quantity = min(adjusted_capacity, int(spec["base_capacity_kg_30d"] * 2.6) - allocation)
            if quantity <= 0:
                continue
            routes.append(
                {
                    "id": f"resource_route_{scenario['id']}_{resource.id}_{target.id}",
                    "resource_id": resource.id,
                    "resource_name": resource.company_name,
                    "resource_category": category,
                    "resource_label": spec["short_label"],
                    "target_factory_id": target.id,
                    "target_factory_name": target.company_name,
                    "target_part_category": target.category,
                    "target_part_label": PART_CATEGORIES[target.category]["short_label"],
                    "quantity_kg_30d": int(quantity),
                    "risk": risk,
                    "risk_reason": risk_reason,
                    "status": status,
                    "distance_km": route_metric_fields["road_distance_km"],
                    **route_metric_fields,
                    "from": {"lat": resource.lat, "lon": resource.lon},
                    "to": {"lat": target.lat, "lon": target.lon},
                }
            )
            allocation += quantity
            selected_count += 1

        summary.append(
            {
                "resource_category": category,
                "resource_label": spec["label"],
                "target_part_categories": list(spec["target_part_categories"]),
                "allocated_kg_30d": int(allocation),
                "candidate_count": len(candidates),
                "selected_route_count": selected_count,
                "top_resource_names": [item[1].company_name for item in ranked[:3]],
            }
        )
    return routes, summary


def build_plan(
    records: list[FactoryRecord],
    scenario: dict,
    route_cache: dict,
    resources: list[ResourceRecord] | None = None,
    grid_profiles_by_factory: dict[str, dict] | None = None,
) -> dict:
    target = scenario["target_drones"]
    suppliers = []
    routes = []
    category_summary = []
    selected_ids = set()

    def rank_category(category: str) -> list[tuple]:
        candidates = [record for record in records if record.category == category]
        ranked = []
        for record in candidates:
            risk, risk_reason = threat_risk(record, scenario)
            adjusted_capacity = int(record.capacity_units_30d * (1 - risk * scenario["risk_weight"] * 0.55))
            energy_evidence = record.energy_profile.get("capacity_evidence_score", 0.45)
            capacity_index = record.capacity_profile.get("capacity_index", 0.45)
            capacity_confidence = record.capacity_profile.get("capacity_confidence", 0.45)
            grid_profile = (grid_profiles_by_factory or {}).get(record.id, {})
            grid_dependency_score = float(grid_profile.get("grid_dependency_score") or 0.35)
            priority_bonus = 0.0
            if category == "drone_assembly" and record.is_priority_assembly_seed:
                priority_bonus = 44 * max(1.0, float(record.priority_weight or 1.0))
            effective_score = (
                record.confidence * 100
                + capacity_index * 52
                + capacity_confidence * 26
                + math.log(max(1, adjusted_capacity)) * 6
                + energy_evidence * 10
                + priority_bonus
                - risk * 65
                - grid_dependency_score * 24 * float(scenario.get("grid_risk_weight", 0.1))
                - stable_float(record.id + scenario["id"], 0, 4)
            )
            ranked.append((effective_score, record, risk, risk_reason, adjusted_capacity, grid_profile))
        ranked.sort(reverse=True, key=lambda item: item[0])
        return ranked

    assembly_spec = PART_CATEGORIES["drone_assembly"]
    assembly_required = target * int(assembly_spec["bom_quantity"])
    assembly_allocation = 0
    assembly_suppliers = []
    assembly_destinations: list[dict] = []
    ranked_assembly_by_slug = {
        priority_seed_slug(item[1]): item for item in rank_category("drone_assembly") if is_core_operating_assembly_record(item[1])
    }
    selected_assembly_rows = [
        ranked_assembly_by_slug[slug] for slug in CORE_OPERATING_DRONE_ASSEMBLY_SLUGS if slug in ranked_assembly_by_slug
    ]
    if not selected_assembly_rows:
        selected_assembly_rows = rank_category("drone_assembly")[:12]
    base_quantity = assembly_required // max(1, len(selected_assembly_rows))
    remainder = assembly_required % max(1, len(selected_assembly_rows))
    for index, (_, record, risk, risk_reason, adjusted_capacity, grid_profile) in enumerate(selected_assembly_rows):
        selected_ids.add(record.id)
        quantity = base_quantity + (1 if index < remainder else 0)
        if quantity <= 0:
            continue
        onsite_route_fields = {
            "route_distance_km": 0,
            "distance_km": 0,
            "road_distance_km": 0,
            "straight_line_km": 0,
            "duration_min": 0,
            "route_geometry": [
                {"lat": record.lat, "lon": record.lon},
                {"lat": record.lat, "lon": record.lon},
            ],
            "routing_provider": "onsite_final_assembly_assignment",
            "routing_status": "onsite",
            "routing_note": "Final assembly is assigned directly to this priority drone manufacturer site; no synthetic assembly hub leg.",
            "fuel_liters_per_trip": 0,
            "driver_hours_per_trip": 0,
            "estimated_trip_cost_krw": 0,
        }
        supplier = {
            "factory_id": record.id,
            "part_category": "drone_assembly",
            "part_label": assembly_spec["label"],
            "requested_quantity": int(quantity),
            "capacity_units_30d": record.capacity_units_30d,
            "adjusted_capacity_units_30d": int(adjusted_capacity),
            "capacity_index": record.capacity_profile.get("capacity_index"),
            "capacity_confidence": record.capacity_profile.get("capacity_confidence"),
            "capacity_tier": record.capacity_profile.get("capacity_tier"),
            "grid_dependency_score": grid_profile.get("grid_dependency_score"),
            "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
            "outage_output_multiplier": grid_profile.get("outage_output_multiplier"),
            "hub_id": record.id,
            "hub_name": route_destination_label(record),
            "destination_type": "priority_final_assembly_factory",
            "destination_factory_id": record.id,
            "destination_factory_name": record.company_name,
            "destination_site_label": record.priority_site_label,
            "destination_name": route_destination_label(record),
            "risk": risk,
            "risk_reason": risk_reason,
            "priority_role": record.priority_role,
            "priority_weight": record.priority_weight,
            "priority_site_label": record.priority_site_label,
            "is_priority_assembly_seed": record.is_priority_assembly_seed,
            "assembly_operating_status": record.assembly_operating_status,
            "assembly_node_role": record.assembly_node_role,
            "selection_basis": "core_domestic_drone_manufacturer_operating_factory",
            "selection_note": "Included as a peacetime operating domestic drone manufacturer facility; baseline inclusion is not capacity-ranked.",
            **onsite_route_fields,
            "status": "final-assembly",
        }
        suppliers.append(supplier)
        assembly_suppliers.append(supplier)
        assembly_destinations.append(
            {
                "record": record,
                "risk": risk,
                "risk_reason": risk_reason,
                "grid_profile": grid_profile,
                "planned_quantity": int(quantity),
                "status": "final-assembly",
            }
        )
        assembly_allocation += quantity

    category_summary.append(
        {
            "part_category": "drone_assembly",
            "part_label": assembly_spec["label"],
            "bom_quantity_per_drone": assembly_spec["bom_quantity"],
            "required_units": int(assembly_required),
            "allocated_units": int(assembly_allocation),
            "coverage_ratio": round(assembly_allocation / assembly_required if assembly_required else 0, 3),
            "supplier_count": len(assembly_suppliers),
            "top_supplier_names": [
                route_destination_label(next(record for record in records if record.id == item["factory_id"]))
                for item in assembly_suppliers[:3]
            ],
        }
    )

    for category, spec in PART_CATEGORIES.items():
        if category == "drone_assembly":
            continue
        required = target * int(spec["bom_quantity"])
        ranked = rank_category(category)

        allocation = 0
        category_suppliers = []
        for _, record, risk, risk_reason, adjusted_capacity, grid_profile in ranked[:6]:
            if allocation >= required:
                break
            selected_ids.add(record.id)
            quantity = min(adjusted_capacity, max(0, required - allocation))
            if quantity <= 0:
                continue
            destination = choose_assembly_destination(record, assembly_destinations, scenario, risk)
            destination_record = destination["record"]
            destination_risk = float(destination.get("risk") or 0.12)
            distance = haversine_km((record.lat, record.lon), (destination_record.lat, destination_record.lon))
            route_metric_fields = route_metrics(
                {"lat": record.lat, "lon": record.lon},
                {"lat": destination_record.lat, "lon": destination_record.lon},
                distance,
                route_cache,
            )
            route_status = "primary"
            if scenario.get("threat") and (risk > 0.32 or destination_risk > 0.42):
                route_status = "rerouted"
            supplier = {
                "factory_id": record.id,
                "part_category": category,
                "part_label": spec["label"],
                "requested_quantity": int(quantity),
                "capacity_units_30d": record.capacity_units_30d,
                "adjusted_capacity_units_30d": int(adjusted_capacity),
                "capacity_index": record.capacity_profile.get("capacity_index"),
                "capacity_confidence": record.capacity_profile.get("capacity_confidence"),
                "capacity_tier": record.capacity_profile.get("capacity_tier"),
                "grid_dependency_score": grid_profile.get("grid_dependency_score"),
                "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
                "outage_output_multiplier": grid_profile.get("outage_output_multiplier"),
                "hub_id": destination_record.id,
                "hub_name": route_destination_label(destination_record),
                "destination_type": "priority_final_assembly_factory",
                "destination_factory_id": destination_record.id,
                "destination_factory_name": destination_record.company_name,
                "destination_site_label": destination_record.priority_site_label,
                "destination_name": route_destination_label(destination_record),
                "risk": risk,
                "risk_reason": risk_reason,
                "route_distance_km": route_metric_fields["road_distance_km"],
                "priority_role": record.priority_role,
                "priority_weight": record.priority_weight,
                "priority_site_label": record.priority_site_label,
                "is_priority_assembly_seed": record.is_priority_assembly_seed,
                **route_metric_fields,
                "status": route_status,
            }
            suppliers.append(supplier)
            category_suppliers.append(supplier)
            routes.append(
                {
                    "id": f"route_{scenario['id']}_{record.id}_{destination_record.id}",
                    "factory_id": record.id,
                    "factory_name": record.company_name,
                    "hub_id": destination_record.id,
                    "hub_name": route_destination_label(destination_record),
                    "destination_type": "priority_final_assembly_factory",
                    "destination_factory_id": destination_record.id,
                    "destination_factory_name": destination_record.company_name,
                    "destination_site_label": destination_record.priority_site_label,
                    "destination_name": route_destination_label(destination_record),
                    "part_category": category,
                    "part_label": spec["short_label"],
                    "quantity": int(quantity),
                    "risk": risk,
                    "grid_dependency_score": grid_profile.get("grid_dependency_score"),
                    "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
                    "priority_role": record.priority_role,
                    "priority_weight": record.priority_weight,
                    "priority_site_label": record.priority_site_label,
                    "is_priority_assembly_seed": record.is_priority_assembly_seed,
                    "status": supplier["status"],
                    "distance_km": route_metric_fields["road_distance_km"],
                    **route_metric_fields,
                    "from": {"lat": record.lat, "lon": record.lon},
                    "to": {"lat": destination_record.lat, "lon": destination_record.lon},
                }
            )
            allocation += quantity

        category_summary.append(
            {
                "part_category": category,
                "part_label": spec["label"],
                "bom_quantity_per_drone": spec["bom_quantity"],
                "required_units": int(required),
                "allocated_units": int(allocation),
                "coverage_ratio": round(allocation / required if required else 0, 3),
                "supplier_count": len(category_suppliers),
                "top_supplier_names": [
                    next(record.company_name for record in records if record.id == item["factory_id"])
                    for item in category_suppliers[:3]
                ],
            }
        )

    bottleneck = min(category_summary, key=lambda item: item["coverage_ratio"])
    possible_drones_by_part = [
        item["allocated_units"] / PART_CATEGORIES[item["part_category"]]["bom_quantity"]
        for item in category_summary
    ]
    possible_drones = int(min(possible_drones_by_part))
    high_risk_count = sum(1 for item in suppliers if item["risk"] >= 0.55)
    rerouted_count = sum(1 for item in suppliers if item["status"] == "rerouted")
    resource_routes, resource_summary = build_resource_routes(resources or [], records, scenario, route_cache)
    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "short_name": scenario["short_name"],
        "description": scenario["description"],
        "target_drones": target,
        "possible_drones_30d": possible_drones,
        "bottleneck_part_category": bottleneck["part_category"],
        "bottleneck_part_label": bottleneck["part_label"],
        "bottleneck_coverage_ratio": bottleneck["coverage_ratio"],
        "high_risk_supplier_count": high_risk_count,
        "rerouted_supplier_count": rerouted_count,
        "threat": scenario.get("threat"),
        "category_summary": category_summary,
        "selected_final_assembly_factories": [
            {
                "factory_id": item["factory_id"],
                "company_name": next(record.company_name for record in records if record.id == item["factory_id"]),
                "site_label": item.get("priority_site_label"),
                "destination_name": item.get("destination_name"),
                "planned_quantity": item.get("requested_quantity"),
                "capacity_units_30d": item.get("capacity_units_30d"),
                "risk": item.get("risk"),
                "priority_weight": item.get("priority_weight"),
                "assembly_operating_status": item.get("assembly_operating_status"),
                "assembly_node_role": item.get("assembly_node_role"),
                "status": item.get("status"),
            }
            for item in assembly_suppliers
        ],
        "resource_supply_summary": resource_summary,
        "selected_suppliers": suppliers,
        "route_segments": routes,
        "resource_route_segments": resource_routes,
        "selected_factory_ids": sorted(selected_ids),
        "recommendation": (
            "Maintain current distributed plan and verify battery/flight-stack capacity first."
            if scenario["id"] == "baseline"
            else "Reduce west/south exposed suppliers, move final integration inland, and verify alternate power and flight-stack suppliers."
        ),
    }


def factory_to_dict(record: FactoryRecord, grid_profiles_by_factory: dict[str, dict] | None = None) -> dict:
    return {
        "id": record.id,
        "company_name": record.company_name,
        "display_name": record.company_name,
        "factory_manage_no": record.factory_manage_no,
        "complex_name": record.complex_name,
        "product_text": record.product_text,
        "raw_materials_text": record.raw_materials_text,
        "industry_code": record.industry_code,
        "industry_name": record.industry_name,
        "factory_size_label": record.factory_size_label,
        "address_public": record.address,
        "province": record.province,
        "city": record.city,
        "lat": record.lat,
        "lon": record.lon,
        "category": record.category,
        "category_label": PART_CATEGORIES[record.category]["label"],
        "confidence": record.confidence,
        "confidence_reasons": record.confidence_reasons,
        "priority_role": record.priority_role,
        "priority_weight": record.priority_weight,
        "priority_source": record.priority_source,
        "priority_site_label": record.priority_site_label,
        "priority_site_type": record.priority_site_type,
        "assembly_operating_status": record.assembly_operating_status,
        "assembly_node_role": record.assembly_node_role,
        "is_core_operating_assembly": is_core_operating_assembly_record(record),
        "is_reserve_assembly_seed": is_reserve_standby_assembly_record(record),
        "is_priority_assembly_seed": record.is_priority_assembly_seed,
        "factory_scale": {
            "employee_total": record.employee_total,
            "land_area_m2": record.land_area_m2,
            "manufacturing_area_m2": record.manufacturing_area_m2,
            "auxiliary_area_m2": record.auxiliary_area_m2,
            "building_area_m2": record.building_area_m2,
            "factory_size_label": record.factory_size_label,
        },
        "capacity_units_30d": record.capacity_units_30d,
        "factory_capacity_profile": record.capacity_profile,
        "manufacturing_profile": manufacturing_profile_for(record),
        "grid_risk_profile": (grid_profiles_by_factory or {}).get(record.id),
        "energy_profile": record.energy_profile,
        "source": record.priority_source if record.is_priority_assembly_seed else "data.go.kr 한국산업단지공단 전국등록공장현황_20200229 CSV",
        "source_row": record.source_row,
        "data_limitations": record.data_limitations,
    }


def resource_to_dict(record: ResourceRecord) -> dict:
    category = RESOURCE_CATEGORIES[record.resource_category]
    return {
        "id": record.id,
        "company_name": record.company_name,
        "display_name": record.company_name,
        "complex_name": record.complex_name,
        "product_text": record.product_text,
        "address_public": record.address,
        "province": record.province,
        "city": record.city,
        "lat": record.lat,
        "lon": record.lon,
        "resource_category": record.resource_category,
        "resource_label": category["label"],
        "target_part_categories": record.target_part_categories,
        "confidence": record.confidence,
        "confidence_reasons": record.confidence_reasons,
        "capacity_kg_30d": record.capacity_kg_30d,
        "energy_profile": record.energy_profile,
        "source": "data.go.kr 한국산업단지공단 전국등록공장현황 CSV",
        "source_row": record.source_row,
        "data_limitations": record.data_limitations,
    }


def build_dataset() -> dict:
    download_source()
    download_capacity_sources()
    download_energy_sources()
    download_grid_sources()
    route_cache = load_route_cache()
    energy_context = build_energy_context()
    kepco_grid_context = read_kepco_large_customer_context()
    all_records = read_candidates(energy_context)
    all_resource_records = read_resource_candidates(energy_context)
    map_seed_records = balanced_sample(all_records, per_category=12)
    selected_resources = balanced_resource_sample(all_resource_records, per_category=8)
    scoring_grid_zones = build_grid_risk_zones(all_records, energy_context, kepco_grid_context)
    scoring_zones_by_province = {zone["province"]: zone for zone in scoring_grid_zones}
    scoring_grid_profiles_by_factory = {
        record.id: grid_profile_for_factory(record, scoring_zones_by_province) for record in all_records
    }
    plans = [
        build_plan(all_records, scenario, route_cache, selected_resources, scoring_grid_profiles_by_factory)
        for scenario in SCENARIOS
    ]
    for plan, scenario in zip(plans, SCENARIOS):
        build_material_supply_for_plan(plan, all_records, scenario, route_cache)
        build_component_survival_for_plan(plan, scenario)
    required_map_factory_ids = selected_factory_ids_from_plans(plans)
    required_map_factory_ids.update(record.id for record in all_records if record.is_priority_assembly_seed)
    selected_records = merge_map_factory_records(map_seed_records, all_records, required_map_factory_ids)
    grid_risk_zones = build_grid_risk_zones(selected_records, energy_context, kepco_grid_context)
    zones_by_province = {zone["province"]: zone for zone in grid_risk_zones}
    grid_profiles_by_factory = {
        record.id: grid_profile_for_factory(record, scoring_zones_by_province) for record in selected_records
    }
    baseline_plan = next((plan for plan in plans if plan["id"] == "baseline"), plans[0])
    grid_disruption_scenarios = build_grid_disruption_scenarios(selected_records, grid_risk_zones)
    frozen_orders = build_frozen_orders(baseline_plan)
    in_transit_shipments = build_in_transit_shipments(baseline_plan)
    inventory_wip = build_inventory_wip(selected_records, baseline_plan)
    if ROUTE_PROVIDER == "osrm":
        save_route_cache(route_cache)
    counts_by_category = {
        category: sum(1 for record in all_records if record.category == category)
        for category in PART_CATEGORIES
    }
    resource_counts_by_category = {
        category: sum(1 for record in all_resource_records if record.resource_category == category)
        for category in RESOURCE_CATEGORIES
    }
    counts_by_province: dict[str, int] = {}
    for record in selected_records:
        counts_by_province[record.province] = counts_by_province.get(record.province, 0) + 1
    resource_counts_by_province: dict[str, int] = {}
    for record in selected_resources:
        resource_counts_by_province[record.province] = resource_counts_by_province.get(record.province, 0) + 1
    direct_energy_matches = sum(
        1 for record in selected_records if record.energy_profile.get("match_type") == "ngms_company_direct"
    )
    direct_resource_energy_matches = sum(
        1 for record in selected_resources if record.energy_profile.get("match_type") == "ngms_company_direct"
    )
    priority_seed_records = [record for record in all_records if record.is_priority_assembly_seed]
    core_operating_priority_seed_count = sum(1 for record in priority_seed_records if is_core_operating_assembly_record(record))
    reserve_standby_priority_seed_count = sum(1 for record in priority_seed_records if is_reserve_standby_assembly_record(record))
    selected_priority_seed_count = sum(1 for record in selected_records if record.is_priority_assembly_seed)
    dataset = {
        "schema": "d4d.drone_production_conversion.v0.8",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario": {
            "name": "Drone Production Continuity & Factory Conversion Planner",
            "aoi": "Republic of Korea public factory registry demo",
            "safety_boundary": (
                "Candidate matching only. No weapon payloads, no build instructions, "
                "and no verified mobilization claim."
            ),
        },
        "source_catalog": [
            {
                "name": "한국산업단지공단_전국등록공장현황_등록공장현황자료_20241231",
                "url": "https://www.data.go.kr/data/15105482/fileData.do",
                "use": "public factory base list: company, product, address, industrial complex",
                "limitation": "does not include equipment inventory, line availability, or QA readiness",
            },
            {
                "name": "한국산업단지공단_전국등록공장현황_20200229",
                "url": "https://www.data.go.kr/data/15106170/fileData.do",
                "use": "factory capacity backdata: employee count, land/building/manufacturing area, industry code/name, raw materials, factory management number",
                "limitation": "older rich snapshot; use for capacity proxy and entity-resolution seed, not live factory status",
            },
            {
                "name": "한국산업단지공단_팩토리온_종업원관리_20210731",
                "url": "https://www.data.go.kr/data/15088930/fileData.do",
                "use": "future cross-check for factory management number and employee counts",
                "limitation": "not yet joined in v0.5; prepared as secondary validation source",
            },
            {
                "name": "한국산업단지공단_공장등록생산정보조회서비스",
                "url": "https://www.data.go.kr/data/15087611/openapi.do",
                "use": "future enrichment for employees, registration date, industry codes, product text",
                "limitation": "API approval/call behavior must be verified per account",
            },
            {
                "name": "한국환경공단_자원순환정보시스템_폐기물통계정보",
                "url": "https://www.data.go.kr/data/15106003/openapi.do",
                "use": "future enrichment for waste generation, recycling performance, and waste-company statistics",
                "limitation": "statistics are not a verified facility-level rare-earth extraction capacity list",
            },
            {
                "name": "한국환경공단_폐기물 재활용실적 및 업체현황",
                "url": "https://www.data.go.kr/data/15105969/fileData.do",
                "use": "future calibration for recycling operators and annual recycling performance by waste type",
                "limitation": "public table is aggregated; facility-specific item handling must be validated elsewhere",
            },
            {
                "name": "대한민국 정책브리핑_핵심광물 재자원화 정책",
                "url": "https://www.korea.kr/news/policyNewsView.do?newsId=148953591",
                "use": "policy basis for rare-earth permanent-magnet recycling, critical-mineral DB, and 2030 recycling target",
                "limitation": "policy goal is not a current operating-capacity dataset",
            },
            {
                "name": "한국에너지공단_에너지다소비사업자 에너지 사용 현황(통합)",
                "url": "https://www.data.go.kr/data/15127341/fileData.do",
                "use": "regional/sector energy and electricity context for large energy users",
                "limitation": "public downloadable table is aggregate context, not a full factory-level live capacity feed",
            },
            {
                "name": "기후에너지환경부 온실가스종합정보센터_명세서배출량정보공개",
                "url": "https://www.data.go.kr/data/15148894/fileData.do",
                "use": "company-level reported greenhouse-gas emissions and energy use for managed/allocated entities",
                "limitation": "covers large managed emitters; company-level match may not identify the exact factory line",
            },
            {
                "name": "한국전력공사_업종별 전력사용량",
                "url": "https://www.data.go.kr/data/15101310/fileData.do",
                "use": "future enrichment for regional/industry electricity trends and average electricity price",
                "limitation": "generally aggregate by region/industry; individual customer/factory power use is not public",
            },
            {
                "name": "한국전력공사_전력고객주요정보_대용량고객일반정보",
                "url": "https://www.data.go.kr/data/15068962/fileData.do",
                "use": "regional aggregation of large-load customer, transformer/distribution facility, capacity, inspection, and supply-class fields for grid-risk proxy scoring",
                "limitation": "use for resilience screening only; do not expose or infer exact attack-relevant electric-facility dependencies without authorization",
            },
            {
                "name": "OpenStreetMap power infrastructure tags",
                "url": "https://wiki.openstreetmap.org/wiki/Key:power",
                "use": "optional public geospatial context for coarse grid-zone validation and map QA",
                "limitation": "community-mapped data can be incomplete, stale, or operationally sensitive; use only as coarse context",
            },
            {
                "name": "D4D synthetic APAC material import corridor assumptions",
                "url": "internal://d4d/material-maritime-supply-v0.2",
                "use": "demo material BOM, Japan-East Sea import corridor, import-port, and port-to-factory route planning schema",
                "limitation": "coarse planning assumptions only; replace with customs/import, port call, shipping, inventory, and supplier contract data",
            },
            {
                "name": "D4D synthetic blockade component-survival assumptions",
                "url": "internal://d4d/blockade-survival-v0.1",
                "use": "component/subcomponent inventory survival-days, ramp-gap, and full-blockade phase-curve demo schema",
                "limitation": "synthetic defaults only; replace with authorized inventory, ERP/MES, procurement, customs, and supplier lead-time feeds",
            },
            {
                "name": "User-provided domestic drone production-base address seed list",
                "url": "attachment://domestic_drone_production_base_addresses.md",
                "use": "priority final-assembly seed factories for domestic drone manufacturers and aerospace UAV production bases",
                "limitation": "some rows are research/headquarters/manufacturing-base assumptions where a public factory address is not available",
            },
        ],
        "part_categories": PART_CATEGORIES,
        "resource_categories": RESOURCE_CATEGORIES,
        "component_catalog": COMPONENT_CATALOG,
        "subcomponent_catalog": SUBCOMPONENT_CATALOG,
        "component_subcomponent_bom": COMPONENT_SUBCOMPONENT_BOM,
        "blockade_demand_model": BLOCKADE_DEMAND_MODEL,
        "raw_material_catalog": RAW_MATERIAL_CATALOG,
        "drone_mission_profiles": DRONE_MISSION_PROFILES,
        "default_drone_mission_mix": DEFAULT_DRONE_MISSION_MIX,
        "import_ports": IMPORT_PORTS,
        "foreign_material_sources": FOREIGN_MATERIAL_SOURCES,
        "allied_supply_sources": ALLIED_SUPPLY_SOURCES,
        "maritime_corridor_model": MARITIME_CORRIDOR_MODEL,
        "priority_drone_assembly_bases": [
            {
                "factory_id": record.id,
                "company_name": record.company_name,
                "site_label": record.priority_site_label,
                "site_type": record.priority_site_type,
                "address_public": record.address,
                "province": record.province,
                "city": record.city,
                "priority_weight": record.priority_weight,
                "capacity_units_30d": record.capacity_units_30d,
                "confidence": record.confidence,
                "assembly_operating_status": record.assembly_operating_status,
                "assembly_node_role": record.assembly_node_role,
                "is_core_operating_assembly": is_core_operating_assembly_record(record),
                "is_reserve_assembly_seed": is_reserve_standby_assembly_record(record),
                "source": record.priority_source,
            }
            for record in priority_seed_records
        ],
        "material_requirements": MATERIAL_REQUIREMENTS,
        "logistics_cost_model": LOGISTICS_COST_MODEL,
        "energy_capacity_model": ENERGY_CAPACITY_MODEL,
        "factory_capacity_model": FACTORY_CAPACITY_MODEL,
        "power_grid_risk_model": POWER_GRID_RISK_MODEL,
        "kepco_large_customer_context": {
            "source": kepco_grid_context.get("source"),
            "record_count": kepco_grid_context.get("record_count"),
            "limitations": kepco_grid_context.get("limitations"),
        },
        "operations_state_model": OPERATIONS_STATE_MODEL,
        "routing_design": {
            "active_provider": ROUTE_PROVIDER if ROUTE_PROVIDER in {"osrm", "estimate"} else "estimate",
            "default_mode": "osrm",
            "fallback_mode": "estimate",
            "optional_estimate_mode": "Run with D4D_ROUTE_PROVIDER=estimate only for offline draft data; map production routes should be regenerated with OSRM or an approved road-routing API before demo use.",
            "final_assembly_destination_policy": (
                "Synthetic demo assembly hubs are removed from active planning. Component routes now terminate at "
                "the fixed core operating domestic drone manufacturer facilities, not a capacity-ranked top-N subset. "
                "Reserve standby drone manufacturer sites are retained as fallback nodes for reconfiguration but are "
                "not counted in baseline output. Scenario route choice still considers risk and distance."
            ),
            "production_options": [
                "Self-host OSRM/Valhalla/GraphHopper on Korea OSM or government road graph for offline/closed-network planning.",
                "Use Kakao Mobility, NAVER Cloud Directions, or Tmap for commercial Korean road distance, traffic, toll, and ETA when API keys and terms allow.",
                "Persist a route matrix table keyed by origin node, destination node, vehicle profile, scenario, and provider version.",
            ],
        },
        "bom": [
            {
                "part_category": category,
                "part_label": spec["label"],
                "quantity_per_drone": spec["bom_quantity"],
                "criticality": spec["criticality"],
                "safe_demo_note": "High-level non-weaponized part family only.",
            }
            for category, spec in PART_CATEGORIES.items()
        ],
        "assembly_hubs": [],
        "legacy_assembly_hubs_removed": {
            "removed": True,
            "previous_count": len(ASSEMBLY_HUBS),
            "reason": "Demo-only logistics/assembly hubs replaced by priority drone manufacturer final-assembly factory destinations.",
        },
        "factory_candidates": [factory_to_dict(record, grid_profiles_by_factory) for record in selected_records],
        "resource_candidates": [resource_to_dict(record) for record in selected_resources],
        "grid_risk_zones": grid_risk_zones,
        "grid_disruption_scenarios": grid_disruption_scenarios,
        "frozen_orders": frozen_orders,
        "in_transit_shipments": in_transit_shipments,
        "inventory_wip": inventory_wip,
        "plans": plans,
        "stats": {
            "raw_factory_rows": sum(1 for _ in RAW_CSV.open("r", encoding="cp949")) - 1,
            "capacity_source_rows": sum(1 for _ in NATIONAL_FACTORY_CAPACITY_CSV.open("r", encoding="cp949")) - 1
            if NATIONAL_FACTORY_CAPACITY_CSV.exists()
            else None,
            "candidate_counts_by_category_full_csv": counts_by_category,
            "resource_candidate_counts_by_category_full_csv": resource_counts_by_category,
            "full_factory_candidate_pool_count": len(all_records),
            "pipeline_shortlist_per_category_per_scenario": 400,
            "pipeline_shortlist_candidate_count": sum(min(400, count) for count in counts_by_category.values())
            * len(SCENARIOS),
            "pipeline_shortlist_route_policy": "shortlist first; road-route matrix should be expanded only for shortlisted candidates",
            "demo_factory_count": len(selected_records),
            "demo_resource_count": len(selected_resources),
            "priority_drone_assembly_seed_count": len(priority_seed_records),
            "core_operating_drone_assembly_seed_count": core_operating_priority_seed_count,
            "reserve_standby_drone_assembly_seed_count": reserve_standby_priority_seed_count,
            "selected_priority_drone_assembly_seed_count": selected_priority_seed_count,
            "demo_factory_counts_by_province": counts_by_province,
            "demo_resource_counts_by_province": resource_counts_by_province,
            "ngms_emissions_public_records": energy_context["stats"]["ngms_record_count"],
            "direct_factory_energy_matches": direct_energy_matches,
            "direct_resource_energy_matches": direct_resource_energy_matches,
            "regional_energy_context_year": energy_context["stats"]["regional_electricity_year"],
            "kepco_large_customer_public_rows": kepco_grid_context.get("record_count"),
            "grid_risk_zone_count": len(grid_risk_zones),
            "grid_disruption_scenario_count": len(grid_disruption_scenarios),
            "frozen_order_count": len(frozen_orders),
            "in_transit_shipment_count": len(in_transit_shipments),
            "inventory_wip_row_count": len(inventory_wip),
            "raw_material_count": len(RAW_MATERIAL_CATALOG),
            "component_count": len(COMPONENT_CATALOG),
            "subcomponent_count": len(SUBCOMPONENT_CATALOG),
            "blockade_phase_curve_point_count": sum(len(plan.get("blockade_phase_curve", [])) for plan in plans),
            "drone_mission_profile_count": len(DRONE_MISSION_PROFILES),
            "import_port_count": len(IMPORT_PORTS),
            "foreign_material_source_count": len(FOREIGN_MATERIAL_SOURCES),
            "allied_supply_source_count": len(ALLIED_SUPPLY_SOURCES),
            "maritime_import_route_count": sum(len(plan.get("maritime_import_route_segments", [])) for plan in plans),
            "port_to_factory_material_route_count": sum(len(plan.get("port_to_factory_material_routes", [])) for plan in plans),
        },
        "apac_extension": {
            "title": "APAC gray-zone denied-environment allied sustainment C2",
            "priority": "follow-on design, not MVP",
            "design_direction": [
                "Treat APAC logistics nodes as coalition-maintained resource pools with source confidence.",
                "Fuse equipment maintenance demand, local sourcing, depot capacity, route risk, and communications state.",
                "Run min-cost flow / resilient routing to allocate parts and maintenance kits under denied logistics corridors.",
                "Show local procurement and distribution monitoring as aggregate resource classes rather than sensitive facility-level data.",
            ],
        },
    }
    pipeline_context = {
        "all_records": all_records,
        "zones_by_province": scoring_zones_by_province,
        "scenarios": SCENARIOS,
    }
    return dataset, pipeline_context


def write_outputs(dataset: dict, pipeline_context: dict | None = None) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in [DATASET_JSON, APP_JSON]:
        path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    APP_JS.write_text(
        "window.DRONE_PRODUCTION_CONVERSION_DATASET = "
        + json.dumps(dataset, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    write_capacity_backdata_csv(dataset, CAPACITY_BACKDATA_CSV)
    write_capacity_backdata_csv(dataset, APP_CAPACITY_BACKDATA_CSV)
    if pipeline_context:
        all_records = pipeline_context.get("all_records", [])
        zones_by_province = pipeline_context.get("zones_by_province", {})
        scenarios = pipeline_context.get("scenarios", SCENARIOS)
        write_full_candidate_capacity_backdata_csv(
            all_records,
            zones_by_province,
            FULL_CANDIDATE_CAPACITY_BACKDATA_CSV,
        )
        write_full_candidate_capacity_backdata_csv(
            all_records,
            zones_by_province,
            APP_FULL_CANDIDATE_CAPACITY_BACKDATA_CSV,
        )
        pipeline_shortlist = build_pipeline_candidate_shortlist_rows(all_records, scenarios, zones_by_province)
        write_pipeline_candidate_shortlist_rows_csv(pipeline_shortlist, PIPELINE_CANDIDATE_SHORTLIST_CSV)
        write_pipeline_candidate_shortlist_rows_csv(pipeline_shortlist, APP_PIPELINE_CANDIDATE_SHORTLIST_CSV)
    write_route_capacity_edges_csv(dataset, ROUTE_CAPACITY_EDGES_CSV)
    write_route_capacity_edges_csv(dataset, APP_ROUTE_CAPACITY_EDGES_CSV)
    write_logistics_route_edges_csv(dataset, LOGISTICS_ROUTE_EDGES_CSV)
    write_logistics_route_edges_csv(dataset, APP_LOGISTICS_ROUTE_EDGES_CSV)
    write_material_supply_backdata_csv(dataset, MATERIAL_SUPPLY_BACKDATA_CSV)
    write_material_supply_backdata_csv(dataset, APP_MATERIAL_SUPPLY_BACKDATA_CSV)
    write_material_import_routes_csv(dataset, MATERIAL_IMPORT_ROUTES_CSV)
    write_material_import_routes_csv(dataset, APP_MATERIAL_IMPORT_ROUTES_CSV)
    write_allied_supply_sources_csv(dataset, ALLIED_SUPPLY_SOURCES_CSV)
    write_allied_supply_sources_csv(dataset, APP_ALLIED_SUPPLY_SOURCES_CSV)
    write_component_survival_csv(dataset, COMPONENT_SURVIVAL_CSV)
    write_component_survival_csv(dataset, APP_COMPONENT_SURVIVAL_CSV)
    write_subcomponent_constraints_csv(dataset, SUBCOMPONENT_CONSTRAINTS_CSV)
    write_subcomponent_constraints_csv(dataset, APP_SUBCOMPONENT_CONSTRAINTS_CSV)
    write_blockade_phase_curve_csv(dataset, BLOCKADE_PHASE_CURVE_CSV)
    write_blockade_phase_curve_csv(dataset, APP_BLOCKADE_PHASE_CURVE_CSV)
    write_grid_risk_zones_csv(dataset, GRID_RISK_ZONES_CSV)
    write_grid_risk_zones_csv(dataset, APP_GRID_RISK_ZONES_CSV)
    write_operational_state_csv(dataset, OPERATIONAL_STATE_CSV)
    write_operational_state_csv(dataset, APP_OPERATIONAL_STATE_CSV)


def write_capacity_backdata_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "factory_id",
        "company_name",
        "province",
        "city",
        "address_public",
        "part_category",
        "part_label",
        "is_priority_assembly_seed",
        "is_core_operating_assembly",
        "is_reserve_assembly_seed",
        "assembly_operating_status",
        "assembly_node_role",
        "priority_weight",
        "priority_role",
        "priority_site_label",
        "priority_site_type",
        "factory_manage_no",
        "industry_code",
        "industry_name",
        "product_text",
        "raw_materials_text",
        "factory_size_label",
        "employee_total",
        "land_area_m2",
        "manufacturing_area_m2",
        "auxiliary_area_m2",
        "building_area_m2",
        "capacity_tier",
        "recommended_role",
        "capacity_index",
        "capacity_confidence",
        "predicted_output_units_30d",
        "nominal_daily_output_units",
        "surge_daily_output_units",
        "setup_days_estimate",
        "min_batch_units",
        "estimated_yield_rate",
        "grid_zone_id",
        "grid_dependency_score",
        "outage_output_multiplier",
        "estimated_backup_hours",
        "production_fit_score",
        "physical_scale_score",
        "workforce_score",
        "energy_operating_scale_score",
        "logistics_access_score",
        "data_completeness_score",
        "energy_match_type",
        "energy_capacity_evidence_score",
        "missing_evidence",
        "source",
        "source_row",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for factory in dataset.get("factory_candidates", []):
            profile = factory.get("factory_capacity_profile", {})
            evidence = profile.get("evidence", {})
            physical = evidence.get("physical_scale", {})
            workforce = evidence.get("workforce_scale", {})
            energy = evidence.get("energy_operating_scale", {})
            logistics = evidence.get("logistics_access", {})
            production = evidence.get("production_fit", {})
            manufacturing = factory.get("manufacturing_profile", {})
            grid_profile = factory.get("grid_risk_profile", {})
            scale = factory.get("factory_scale", {})
            writer.writerow(
                {
                    "factory_id": factory.get("id"),
                    "company_name": factory.get("company_name"),
                    "province": factory.get("province"),
                    "city": factory.get("city"),
                    "address_public": factory.get("address_public"),
                    "part_category": factory.get("category"),
                    "part_label": factory.get("category_label"),
                    "is_priority_assembly_seed": factory.get("is_priority_assembly_seed"),
                    "is_core_operating_assembly": factory.get("is_core_operating_assembly"),
                    "is_reserve_assembly_seed": factory.get("is_reserve_assembly_seed"),
                    "assembly_operating_status": factory.get("assembly_operating_status"),
                    "assembly_node_role": factory.get("assembly_node_role"),
                    "priority_weight": factory.get("priority_weight"),
                    "priority_role": factory.get("priority_role"),
                    "priority_site_label": factory.get("priority_site_label"),
                    "priority_site_type": factory.get("priority_site_type"),
                    "factory_manage_no": factory.get("factory_manage_no"),
                    "industry_code": factory.get("industry_code"),
                    "industry_name": factory.get("industry_name"),
                    "product_text": factory.get("product_text"),
                    "raw_materials_text": factory.get("raw_materials_text"),
                    "factory_size_label": factory.get("factory_size_label"),
                    "employee_total": scale.get("employee_total"),
                    "land_area_m2": scale.get("land_area_m2"),
                    "manufacturing_area_m2": scale.get("manufacturing_area_m2"),
                    "auxiliary_area_m2": scale.get("auxiliary_area_m2"),
                    "building_area_m2": scale.get("building_area_m2"),
                    "capacity_tier": profile.get("capacity_tier"),
                    "recommended_role": profile.get("recommended_role"),
                    "capacity_index": profile.get("capacity_index"),
                    "capacity_confidence": profile.get("capacity_confidence"),
                    "predicted_output_units_30d": profile.get("predicted_output_units_30d"),
                    "nominal_daily_output_units": manufacturing.get("nominal_daily_output_units"),
                    "surge_daily_output_units": manufacturing.get("surge_daily_output_units"),
                    "setup_days_estimate": manufacturing.get("setup_days_estimate"),
                    "min_batch_units": manufacturing.get("min_batch_units"),
                    "estimated_yield_rate": manufacturing.get("estimated_yield_rate"),
                    "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
                    "grid_dependency_score": grid_profile.get("grid_dependency_score"),
                    "outage_output_multiplier": grid_profile.get("outage_output_multiplier"),
                    "estimated_backup_hours": grid_profile.get("estimated_backup_hours"),
                    "production_fit_score": production.get("score"),
                    "physical_scale_score": physical.get("score"),
                    "workforce_score": workforce.get("score"),
                    "energy_operating_scale_score": energy.get("score"),
                    "logistics_access_score": logistics.get("score"),
                    "data_completeness_score": profile.get("data_completeness_score"),
                    "energy_match_type": factory.get("energy_profile", {}).get("match_type"),
                    "energy_capacity_evidence_score": factory.get("energy_profile", {}).get("capacity_evidence_score"),
                    "missing_evidence": " | ".join(profile.get("missing_evidence", [])),
                    "source": factory.get("source"),
                    "source_row": factory.get("source_row"),
                }
            )


def factory_record_capacity_row(record: FactoryRecord, zones_by_province: dict[str, dict] | None = None) -> dict:
    profile = record.capacity_profile
    evidence = profile.get("evidence", {})
    physical = evidence.get("physical_scale", {})
    workforce = evidence.get("workforce_scale", {})
    energy = evidence.get("energy_operating_scale", {})
    logistics = evidence.get("logistics_access", {})
    production = evidence.get("production_fit", {})
    manufacturing = manufacturing_profile_for(record)
    grid_profile = grid_profile_for_factory(record, zones_by_province or {})
    return {
        "factory_id": record.id,
        "company_name": record.company_name,
        "province": record.province,
        "city": record.city,
        "address_public": record.address,
        "part_category": record.category,
        "part_label": PART_CATEGORIES[record.category]["label"],
        "is_priority_assembly_seed": record.is_priority_assembly_seed,
        "is_core_operating_assembly": is_core_operating_assembly_record(record),
        "is_reserve_assembly_seed": is_reserve_standby_assembly_record(record),
        "assembly_operating_status": record.assembly_operating_status,
        "assembly_node_role": record.assembly_node_role,
        "priority_weight": record.priority_weight,
        "priority_role": record.priority_role,
        "priority_site_label": record.priority_site_label,
        "priority_site_type": record.priority_site_type,
        "factory_manage_no": record.factory_manage_no,
        "industry_code": record.industry_code,
        "industry_name": record.industry_name,
        "product_text": record.product_text,
        "raw_materials_text": record.raw_materials_text,
        "factory_size_label": record.factory_size_label,
        "employee_total": record.employee_total,
        "land_area_m2": record.land_area_m2,
        "manufacturing_area_m2": record.manufacturing_area_m2,
        "auxiliary_area_m2": record.auxiliary_area_m2,
        "building_area_m2": record.building_area_m2,
        "capacity_tier": profile.get("capacity_tier"),
        "recommended_role": profile.get("recommended_role"),
        "capacity_index": profile.get("capacity_index"),
        "capacity_confidence": profile.get("capacity_confidence"),
        "predicted_output_units_30d": profile.get("predicted_output_units_30d"),
        "nominal_daily_output_units": manufacturing.get("nominal_daily_output_units"),
        "surge_daily_output_units": manufacturing.get("surge_daily_output_units"),
        "setup_days_estimate": manufacturing.get("setup_days_estimate"),
        "min_batch_units": manufacturing.get("min_batch_units"),
        "estimated_yield_rate": manufacturing.get("estimated_yield_rate"),
        "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
        "grid_dependency_score": grid_profile.get("grid_dependency_score"),
        "outage_output_multiplier": grid_profile.get("outage_output_multiplier"),
        "estimated_backup_hours": grid_profile.get("estimated_backup_hours"),
        "production_fit_score": production.get("score"),
        "physical_scale_score": physical.get("score"),
        "workforce_score": workforce.get("score"),
        "energy_operating_scale_score": energy.get("score"),
        "logistics_access_score": logistics.get("score"),
        "data_completeness_score": profile.get("data_completeness_score"),
        "energy_match_type": record.energy_profile.get("match_type"),
        "energy_capacity_evidence_score": record.energy_profile.get("capacity_evidence_score"),
        "missing_evidence": " | ".join(profile.get("missing_evidence", [])),
        "source": record.priority_source if record.is_priority_assembly_seed else "data.go.kr 한국산업단지공단 전국등록공장현황_20200229 CSV",
        "source_row": record.source_row,
    }


def write_full_candidate_capacity_backdata_csv(
    records: list[FactoryRecord],
    zones_by_province: dict[str, dict],
    path: Path,
) -> None:
    fieldnames = [
        "factory_id",
        "company_name",
        "province",
        "city",
        "address_public",
        "part_category",
        "part_label",
        "is_priority_assembly_seed",
        "is_core_operating_assembly",
        "is_reserve_assembly_seed",
        "assembly_operating_status",
        "assembly_node_role",
        "priority_weight",
        "priority_role",
        "priority_site_label",
        "priority_site_type",
        "factory_manage_no",
        "industry_code",
        "industry_name",
        "product_text",
        "raw_materials_text",
        "factory_size_label",
        "employee_total",
        "land_area_m2",
        "manufacturing_area_m2",
        "auxiliary_area_m2",
        "building_area_m2",
        "capacity_tier",
        "recommended_role",
        "capacity_index",
        "capacity_confidence",
        "predicted_output_units_30d",
        "nominal_daily_output_units",
        "surge_daily_output_units",
        "setup_days_estimate",
        "min_batch_units",
        "estimated_yield_rate",
        "grid_zone_id",
        "grid_dependency_score",
        "outage_output_multiplier",
        "estimated_backup_hours",
        "production_fit_score",
        "physical_scale_score",
        "workforce_score",
        "energy_operating_scale_score",
        "logistics_access_score",
        "data_completeness_score",
        "energy_match_type",
        "energy_capacity_evidence_score",
        "missing_evidence",
        "source",
        "source_row",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(factory_record_capacity_row(record, zones_by_province))


def pipeline_shortlist_rows(
    records: list[FactoryRecord],
    scenario: dict,
    zones_by_province: dict[str, dict],
    per_category: int = 400,
) -> list[dict]:
    rows: list[dict] = []
    province_cap = max(24, per_category // 8)
    for category, spec in PART_CATEGORIES.items():
        category_records = [record for record in records if record.category == category]
        ranked = []
        for record in category_records:
            risk, risk_reason = threat_risk(record, scenario)
            profile = record.capacity_profile
            capacity_index = float(profile.get("capacity_index") or 0)
            capacity_confidence = float(profile.get("capacity_confidence") or 0)
            grid_profile = grid_profile_for_factory(record, zones_by_province)
            outage_multiplier = float(grid_profile.get("outage_output_multiplier") or 1)
            adjusted_capacity = int(record.capacity_units_30d * (1 - risk * scenario["risk_weight"] * 0.55) * outage_multiplier)
            assembly_factory, assembly_distance = choose_reference_assembly_factory(record, scenario, risk, records)
            score = (
                capacity_index * 62
                + capacity_confidence * 30
                + record.confidence * 48
                + math.log(max(1, adjusted_capacity)) * 7
                - risk * 58
                - min(28, assembly_distance / 18)
                - float(grid_profile.get("grid_dependency_score") or 0) * 8
                + stable_float(record.id + scenario["id"] + ":shortlist", -1.5, 1.5)
            )
            ranked.append((score, record, risk, risk_reason, adjusted_capacity, assembly_factory, assembly_distance, grid_profile))
        ranked.sort(reverse=True, key=lambda item: item[0])

        selected = []
        province_counts: dict[str, int] = {}
        for item in ranked:
            _, record, *_ = item
            if len(selected) >= per_category:
                break
            if province_counts.get(record.province, 0) >= province_cap:
                continue
            selected.append(item)
            province_counts[record.province] = province_counts.get(record.province, 0) + 1
        if len(selected) < per_category:
            selected_ids = {item[1].id for item in selected}
            for item in ranked:
                if len(selected) >= per_category:
                    break
                if item[1].id in selected_ids:
                    continue
                selected.append(item)
                selected_ids.add(item[1].id)

        for rank, (
            score,
            record,
            risk,
            risk_reason,
            adjusted_capacity,
            assembly_factory,
            assembly_distance,
            grid_profile,
        ) in enumerate(
            selected, start=1
        ):
            profile = record.capacity_profile
            rows.append(
                {
                    "scenario_id": scenario["id"],
                    "scenario_name": scenario["name"],
                    "part_category": category,
                    "part_label": spec["label"],
                    "shortlist_rank": rank,
                    "scenario_score": round(score, 3),
                    "factory_id": record.id,
                    "company_name": record.company_name,
                    "province": record.province,
                    "city": record.city,
                    "capacity_tier": profile.get("capacity_tier"),
                    "capacity_index": profile.get("capacity_index"),
                    "capacity_confidence": profile.get("capacity_confidence"),
                    "predicted_output_units_30d": record.capacity_units_30d,
                    "adjusted_capacity_units_30d": adjusted_capacity,
                    "risk": risk,
                    "risk_reason": risk_reason,
                    "grid_zone_id": grid_profile.get("primary_grid_zone_id"),
                    "grid_dependency_score": grid_profile.get("grid_dependency_score"),
                    "outage_output_multiplier": grid_profile.get("outage_output_multiplier"),
                    "nearest_assembly_factory_id": assembly_factory.id,
                    "nearest_assembly_factory_name": route_destination_label(assembly_factory),
                    "nearest_assembly_factory_site_label": assembly_factory.priority_site_label,
                    "straight_line_to_assembly_factory_km": round(assembly_distance, 1),
                    "route_matrix_status": "pending_shortlist_route",
                    "selection_reason": "top capacity/risk/logistics candidate before expensive road-route matrix expansion",
                }
            )
    return rows


def write_pipeline_candidate_shortlist_csv(
    records: list[FactoryRecord],
    scenarios: list[dict],
    zones_by_province: dict[str, dict],
    path: Path,
) -> None:
    write_pipeline_candidate_shortlist_rows_csv(
        build_pipeline_candidate_shortlist_rows(records, scenarios, zones_by_province),
        path,
    )


def build_pipeline_candidate_shortlist_rows(
    records: list[FactoryRecord],
    scenarios: list[dict],
    zones_by_province: dict[str, dict],
) -> list[dict]:
    rows: list[dict] = []
    for scenario in scenarios:
        rows.extend(pipeline_shortlist_rows(records, scenario, zones_by_province))
    return rows


def write_pipeline_candidate_shortlist_rows_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "scenario_name",
        "part_category",
        "part_label",
        "shortlist_rank",
        "scenario_score",
        "factory_id",
        "company_name",
        "province",
        "city",
        "capacity_tier",
        "capacity_index",
        "capacity_confidence",
        "predicted_output_units_30d",
        "adjusted_capacity_units_30d",
        "risk",
        "risk_reason",
        "grid_zone_id",
        "grid_dependency_score",
        "outage_output_multiplier",
        "nearest_assembly_factory_id",
        "nearest_assembly_factory_name",
        "nearest_assembly_factory_site_label",
        "straight_line_to_assembly_factory_km",
        "route_matrix_status",
        "selection_reason",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_route_capacity_edges_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "scenario_name",
        "factory_id",
        "part_category",
        "part_label",
        "requested_quantity",
        "capacity_units_30d",
        "adjusted_capacity_units_30d",
        "capacity_tier",
        "capacity_index",
        "capacity_confidence",
        "grid_zone_id",
        "grid_dependency_score",
        "outage_output_multiplier",
        "hub_id",
        "hub_name",
        "destination_type",
        "destination_factory_id",
        "destination_name",
        "destination_site_label",
        "route_distance_km",
        "duration_min",
        "fuel_liters_per_trip",
        "driver_hours_per_trip",
        "estimated_trip_cost_krw",
        "routing_provider",
        "routing_status",
        "route_geometry_source",
        "route_geometry_points",
        "route_road_summary",
        "routing_note",
        "risk",
        "risk_reason",
        "status",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for supplier in plan.get("selected_suppliers", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "scenario_name": plan.get("name"),
                        "factory_id": supplier.get("factory_id"),
                        "part_category": supplier.get("part_category"),
                        "part_label": supplier.get("part_label"),
                        "requested_quantity": supplier.get("requested_quantity"),
                        "capacity_units_30d": supplier.get("capacity_units_30d"),
                        "adjusted_capacity_units_30d": supplier.get("adjusted_capacity_units_30d"),
                        "capacity_tier": supplier.get("capacity_tier"),
                        "capacity_index": supplier.get("capacity_index"),
                        "capacity_confidence": supplier.get("capacity_confidence"),
                        "grid_zone_id": supplier.get("grid_zone_id"),
                        "grid_dependency_score": supplier.get("grid_dependency_score"),
                        "outage_output_multiplier": supplier.get("outage_output_multiplier"),
                        "hub_id": supplier.get("hub_id"),
                        "hub_name": supplier.get("hub_name"),
                        "destination_type": supplier.get("destination_type"),
                        "destination_factory_id": supplier.get("destination_factory_id"),
                        "destination_name": supplier.get("destination_name"),
                        "destination_site_label": supplier.get("destination_site_label"),
                        "route_distance_km": supplier.get("route_distance_km"),
                        "duration_min": supplier.get("duration_min"),
                        "fuel_liters_per_trip": supplier.get("fuel_liters_per_trip"),
                        "driver_hours_per_trip": supplier.get("driver_hours_per_trip"),
                        "estimated_trip_cost_krw": supplier.get("estimated_trip_cost_krw"),
                        "routing_provider": supplier.get("routing_provider"),
                        "routing_status": supplier.get("routing_status"),
                        "route_geometry_points": len(supplier.get("route_geometry") or []),
                        "route_road_summary": supplier.get("route_road_summary"),
                        "routing_note": supplier.get("routing_note"),
                        "risk": supplier.get("risk"),
                        "risk_reason": supplier.get("risk_reason"),
                        "status": supplier.get("status"),
                    }
                )


def write_material_supply_backdata_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "scenario_name",
        "material_id",
        "material_label",
        "kg_per_drone_weighted",
        "required_kg_30d",
        "existing_factory_inventory_kg",
        "domestic_resource_supply_kg",
        "import_supply_kg_30d",
        "total_available_kg_30d",
        "shortage_kg_30d",
        "coverage_ratio",
        "material_feasible_drones_30d",
        "import_dependency",
        "feeds_part_categories",
        "primary_import_route_ids",
        "target_factory_count",
        "verification_need",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for row in plan.get("raw_material_supply_summary", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "scenario_name": plan.get("name"),
                        "material_id": row.get("material_id"),
                        "material_label": row.get("material_label"),
                        "kg_per_drone_weighted": row.get("kg_per_drone_weighted"),
                        "required_kg_30d": row.get("required_kg_30d"),
                        "existing_factory_inventory_kg": row.get("existing_factory_inventory_kg"),
                        "domestic_resource_supply_kg": row.get("domestic_resource_supply_kg"),
                        "import_supply_kg_30d": row.get("import_supply_kg_30d"),
                        "total_available_kg_30d": row.get("total_available_kg_30d"),
                        "shortage_kg_30d": row.get("shortage_kg_30d"),
                        "coverage_ratio": row.get("coverage_ratio"),
                        "material_feasible_drones_30d": row.get("material_feasible_drones_30d"),
                        "import_dependency": row.get("import_dependency"),
                        "feeds_part_categories": " | ".join(row.get("feeds_part_categories", [])),
                        "primary_import_route_ids": " | ".join(row.get("primary_import_route_ids", [])),
                        "target_factory_count": row.get("target_factory_count"),
                        "verification_need": row.get("verification_need"),
                    }
                )


def write_material_import_routes_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "route_id",
        "route_type",
        "material_id",
        "material_label",
        "source_name",
        "origin_port_name",
        "destination_port_name",
        "port_name",
        "target_factory_id",
        "target_factory_name",
        "target_part_category",
        "quantity_kg_30d",
        "import_capacity_kg_30d",
        "distance_nm",
        "distance_km",
        "duration_hours_estimate",
        "duration_min",
        "risk_score",
        "fuel_liters_per_trip",
        "driver_hours_per_trip",
        "estimated_trip_cost_krw",
        "routing_provider",
        "status",
        "routing_status",
        "route_geometry_source",
        "route_geometry_points",
        "route_road_summary",
        "routing_note",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for route in plan.get("maritime_import_route_segments", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "route_id": route.get("id"),
                        "route_type": route.get("route_type"),
                        "material_id": " | ".join(route.get("material_ids", [])),
                        "source_name": route.get("source_name"),
                        "origin_port_name": route.get("origin_port_name"),
                        "destination_port_name": route.get("destination_port_name"),
                        "import_capacity_kg_30d": route.get("import_capacity_kg_30d"),
                        "distance_nm": route.get("distance_nm"),
                        "duration_hours_estimate": route.get("duration_hours_estimate"),
                        "risk_score": route.get("risk_score"),
                        "status": route.get("status"),
                        "routing_status": route.get("routing_status"),
                        "route_geometry_source": route.get("route_geometry_source"),
                        "route_geometry_points": len(route.get("route_geometry") or []),
                        "routing_note": route.get("source"),
                    }
                )
            for route in plan.get("port_to_factory_material_routes", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "route_id": route.get("id"),
                        "route_type": route.get("route_type"),
                        "material_id": route.get("material_id"),
                        "material_label": route.get("material_label"),
                        "port_name": route.get("port_name"),
                        "target_factory_id": route.get("target_factory_id"),
                        "target_factory_name": route.get("target_factory_name"),
                        "target_part_category": route.get("target_part_category"),
                        "quantity_kg_30d": route.get("quantity_kg_30d"),
                        "distance_km": route.get("road_distance_km") or route.get("distance_km"),
                        "duration_min": route.get("duration_min"),
                        "fuel_liters_per_trip": route.get("fuel_liters_per_trip"),
                        "driver_hours_per_trip": route.get("driver_hours_per_trip"),
                        "estimated_trip_cost_krw": route.get("estimated_trip_cost_krw"),
                        "routing_provider": route.get("routing_provider"),
                        "status": route.get("status"),
                        "routing_status": route.get("routing_status"),
                        "route_geometry_source": route.get("route_geometry_source"),
                        "route_geometry_points": len(route.get("route_geometry") or []),
                        "route_road_summary": route.get("route_road_summary"),
                        "routing_note": route.get("routing_note"),
                    }
                )


def write_allied_supply_sources_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "source_id",
        "country",
        "partner_framework",
        "source_port_name",
        "source_lat",
        "source_lon",
        "staging_port_name",
        "staging_source_ids",
        "supply_role",
        "material_ids",
        "component_ids",
        "subcomponent_ids",
        "confidence",
        "evidence_urls",
        "verification_need",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for source in dataset.get("allied_supply_sources", []):
            writer.writerow(
                {
                    "source_id": source.get("id"),
                    "country": source.get("country"),
                    "partner_framework": source.get("partner_framework"),
                    "source_port_name": source.get("source_port_name"),
                    "source_lat": source.get("source_lat"),
                    "source_lon": source.get("source_lon"),
                    "staging_port_name": source.get("staging_port_name"),
                    "staging_source_ids": " | ".join(source.get("staging_source_ids", [])),
                    "supply_role": source.get("supply_role"),
                    "material_ids": " | ".join(source.get("material_ids", [])),
                    "component_ids": " | ".join(source.get("component_ids", [])),
                    "subcomponent_ids": " | ".join(source.get("subcomponent_ids", [])),
                    "confidence": source.get("confidence"),
                    "evidence_urls": " | ".join(source.get("evidence_urls", [])),
                    "verification_need": source.get("verification_need"),
                }
            )


def write_logistics_route_edges_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "route_id",
        "route_type",
        "origin_node_type",
        "origin_name",
        "destination_node_type",
        "destination_name",
        "flow_category",
        "flow_label",
        "quantity",
        "quantity_unit",
        "routing_provider",
        "routing_status",
        "straight_line_km",
        "road_distance_km",
        "distance_nm",
        "duration_min",
        "duration_hours_estimate",
        "fuel_liters_per_trip",
        "driver_hours_per_trip",
        "estimated_trip_cost_krw",
        "risk_score",
        "route_geometry_points",
        "route_road_summary",
        "routing_note",
        "status",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for route in plan.get("maritime_import_route_segments", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "route_id": route.get("id"),
                        "route_type": route.get("route_type"),
                        "origin_node_type": "foreign_material_source",
                        "origin_name": route.get("origin_port_name"),
                        "destination_node_type": "import_port",
                        "destination_name": route.get("destination_port_name"),
                        "flow_category": " | ".join(route.get("material_ids", [])),
                        "flow_label": " | ".join(route.get("material_ids", [])),
                        "quantity": route.get("import_capacity_kg_30d"),
                        "quantity_unit": "kg_30d",
                        "routing_provider": "D4D maritime corridor estimate",
                        "routing_status": route.get("routing_status"),
                        "distance_nm": route.get("distance_nm"),
                        "duration_hours_estimate": route.get("duration_hours_estimate"),
                        "risk_score": route.get("risk_score"),
                        "route_geometry_points": len(route.get("route_geometry") or []),
                        "routing_note": route.get("source"),
                        "status": route.get("status"),
                    }
                )
            for route in plan.get("port_to_factory_material_routes", []):
                writer.writerow(
                    logistics_route_csv_row(
                        plan,
                        route,
                        route_type="port_to_factory_material",
                        origin_type="import_port",
                        origin_name=route.get("port_name"),
                        destination_type="factory",
                        destination_name=route.get("target_factory_name"),
                        flow_category=route.get("material_id"),
                        flow_label=route.get("material_label"),
                        quantity=route.get("quantity_kg_30d"),
                        quantity_unit="kg_30d",
                    )
                )
            for route in plan.get("resource_route_segments", []):
                writer.writerow(
                    logistics_route_csv_row(
                        plan,
                        route,
                        route_type="domestic_resource_to_factory",
                        origin_type="resource_node",
                        origin_name=route.get("resource_name"),
                        destination_type="factory",
                        destination_name=route.get("target_factory_name"),
                        flow_category=route.get("resource_category"),
                        flow_label=route.get("resource_label"),
                        quantity=route.get("quantity_kg_30d"),
                        quantity_unit="kg_30d",
                    )
                )
            for route in plan.get("route_segments", []):
                writer.writerow(
                    logistics_route_csv_row(
                        plan,
                        route,
                        route_type="component_factory_to_priority_assembly_factory",
                        origin_type="factory",
                        origin_name=route.get("factory_name"),
                        destination_type=route.get("destination_type") or "priority_final_assembly_factory",
                        destination_name=route.get("destination_name") or route.get("destination_factory_name") or route.get("hub_name"),
                        flow_category=route.get("part_category"),
                        flow_label=route.get("part_label"),
                        quantity=route.get("quantity"),
                        quantity_unit="units_30d",
                    )
                )


def logistics_route_csv_row(
    plan: dict,
    route: dict,
    *,
    route_type: str,
    origin_type: str,
    origin_name: str | None,
    destination_type: str,
    destination_name: str | None,
    flow_category: str | None,
    flow_label: str | None,
    quantity: float | int | None,
    quantity_unit: str,
) -> dict:
    return {
        "scenario_id": plan.get("id"),
        "route_id": route.get("id"),
        "route_type": route_type,
        "origin_node_type": origin_type,
        "origin_name": origin_name,
        "destination_node_type": destination_type,
        "destination_name": destination_name,
        "flow_category": flow_category,
        "flow_label": flow_label,
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "routing_provider": route.get("routing_provider"),
        "routing_status": route.get("routing_status"),
        "straight_line_km": route.get("straight_line_km"),
        "road_distance_km": route.get("road_distance_km") or route.get("distance_km"),
        "duration_min": route.get("duration_min"),
        "fuel_liters_per_trip": route.get("fuel_liters_per_trip"),
        "driver_hours_per_trip": route.get("driver_hours_per_trip"),
        "estimated_trip_cost_krw": route.get("estimated_trip_cost_krw"),
        "risk_score": route.get("risk"),
        "route_geometry_points": len(route.get("route_geometry") or []),
        "route_road_summary": route.get("route_road_summary"),
        "routing_note": route.get("routing_note"),
        "status": route.get("status"),
    }


def write_component_survival_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "component_id",
        "component_label",
        "part_category",
        "variant",
        "unit",
        "effective_units_per_drone",
        "daily_demand_units",
        "domestic_line_capacity_units_per_day",
        "domestic_output_before_ramp_units_per_day",
        "effective_inventory_units",
        "net_burn_units_per_day",
        "survival_days_p10",
        "survival_days_likely",
        "survival_days_p90",
        "ramp_ready_day",
        "ramp_gap_days",
        "localization_difficulty",
        "vulnerability",
        "bottleneck_rank",
        "is_bottleneck",
        "subcomponent_constraints",
        "verification_need",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for row in plan.get("component_survival_summary", []):
                survival = row.get("survival_days", {})
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "component_id": row.get("component_id"),
                        "component_label": row.get("component_label"),
                        "part_category": row.get("part_category"),
                        "variant": row.get("variant"),
                        "unit": row.get("unit"),
                        "effective_units_per_drone": row.get("effective_units_per_drone"),
                        "daily_demand_units": row.get("daily_demand_units"),
                        "domestic_line_capacity_units_per_day": row.get("domestic_line_capacity_units_per_day"),
                        "domestic_output_before_ramp_units_per_day": row.get("domestic_output_before_ramp_units_per_day"),
                        "effective_inventory_units": row.get("effective_inventory_units"),
                        "net_burn_units_per_day": row.get("net_burn_units_per_day"),
                        "survival_days_p10": survival.get("p10"),
                        "survival_days_likely": survival.get("likely"),
                        "survival_days_p90": survival.get("p90"),
                        "ramp_ready_day": row.get("ramp_ready_day"),
                        "ramp_gap_days": row.get("ramp_gap_days"),
                        "localization_difficulty": row.get("localization_difficulty"),
                        "vulnerability": row.get("vulnerability"),
                        "bottleneck_rank": row.get("bottleneck_rank"),
                        "is_bottleneck": row.get("is_bottleneck"),
                        "subcomponent_constraints": " | ".join(row.get("subcomponent_constraints", [])),
                        "verification_need": row.get("verification_need"),
                    }
                )


def write_subcomponent_constraints_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "subcomponent_id",
        "label",
        "type",
        "unit",
        "import_dependency",
        "daily_demand_units",
        "effective_inventory_units",
        "net_burn_units_per_day",
        "survival_days_p10",
        "survival_days_likely",
        "survival_days_p90",
        "linked_component_ids",
        "verification_need",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            for row in plan.get("subcomponent_survival_summary", []):
                survival = row.get("survival_days", {})
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "subcomponent_id": row.get("subcomponent_id"),
                        "label": row.get("label"),
                        "type": row.get("type"),
                        "unit": row.get("unit"),
                        "import_dependency": row.get("import_dependency"),
                        "daily_demand_units": row.get("daily_demand_units"),
                        "effective_inventory_units": row.get("effective_inventory_units"),
                        "net_burn_units_per_day": row.get("net_burn_units_per_day"),
                        "survival_days_p10": survival.get("p10"),
                        "survival_days_likely": survival.get("likely"),
                        "survival_days_p90": survival.get("p90"),
                        "linked_component_ids": " | ".join(row.get("linked_component_ids", [])),
                        "verification_need": row.get("verification_need"),
                    }
                )


def write_blockade_phase_curve_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "scenario_id",
        "day",
        "units",
        "phase",
        "headline_bottleneck_id",
        "headline_bottleneck_label",
        "subcomponent_bottleneck_id",
        "survival_days_likely",
        "valley_start_day",
        "valley_end_day",
        "valley_depth_units_per_day",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for plan in dataset.get("plans", []):
            headline = plan.get("blockade_survival_headline", {})
            bottleneck = headline.get("bottleneck", {})
            sub_bottleneck = headline.get("subcomponent_bottleneck", {})
            survival = headline.get("survival_days", {})
            valley = headline.get("valley", {})
            for row in plan.get("blockade_phase_curve", []):
                writer.writerow(
                    {
                        "scenario_id": plan.get("id"),
                        "day": row.get("day"),
                        "units": row.get("units"),
                        "phase": row.get("phase"),
                        "headline_bottleneck_id": bottleneck.get("id"),
                        "headline_bottleneck_label": bottleneck.get("label"),
                        "subcomponent_bottleneck_id": sub_bottleneck.get("id"),
                        "survival_days_likely": survival.get("likely"),
                        "valley_start_day": valley.get("start_day"),
                        "valley_end_day": valley.get("end_day"),
                        "valley_depth_units_per_day": valley.get("depth_units_per_day"),
                    }
                )


def write_grid_risk_zones_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "grid_zone_id",
        "name",
        "province",
        "precision_level",
        "facility_class",
        "factory_count",
        "industrial_electricity_mwh",
        "industrial_energy_toe",
        "kepco_large_customer_rows",
        "kepco_top_substation_classes",
        "grid_dependency_score",
        "exposure_tier",
        "top_part_categories",
        "source",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for zone in dataset.get("grid_risk_zones", []):
            writer.writerow(
                {
                    "grid_zone_id": zone.get("id"),
                    "name": zone.get("name"),
                    "province": zone.get("province"),
                    "precision_level": zone.get("precision_level"),
                    "facility_class": zone.get("facility_class"),
                    "factory_count": zone.get("factory_count"),
                    "industrial_electricity_mwh": zone.get("industrial_electricity_mwh"),
                    "industrial_energy_toe": zone.get("industrial_energy_toe"),
                    "kepco_large_customer_rows": zone.get("kepco_large_customer_rows"),
                    "kepco_top_substation_classes": " | ".join(
                        f"{item.get('label')}:{item.get('count')}"
                        for item in zone.get("kepco_top_substation_classes", [])
                    ),
                    "grid_dependency_score": zone.get("grid_dependency_score"),
                    "exposure_tier": zone.get("exposure_tier"),
                    "top_part_categories": " | ".join(
                        f"{item.get('part_label')}:{item.get('count')}" for item in zone.get("top_part_categories", [])
                    ),
                    "source": zone.get("source"),
                }
            )


def write_operational_state_csv(dataset: dict, path: Path) -> None:
    fieldnames = [
        "row_type",
        "id",
        "factory_id",
        "factory_name",
        "part_category",
        "part_label",
        "finished_goods_units",
        "wip_units",
        "qa_hold_units",
        "committed_units",
        "available_to_ship_units",
        "raw_material_days_on_hand",
        "max_daily_output_units",
        "frozen_quantity_units",
        "freeze_until_day",
        "shipment_kind",
        "route_id",
        "quantity_units",
        "quantity_kg",
        "progress_ratio",
        "eta_hours",
        "data_status",
    ]
    factory_names = {factory["id"]: factory["company_name"] for factory in dataset.get("factory_candidates", [])}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in dataset.get("inventory_wip", []):
            writer.writerow(
                {
                    "row_type": "inventory_wip",
                    "id": row.get("id"),
                    "factory_id": row.get("factory_id"),
                    "factory_name": row.get("factory_name"),
                    "part_category": row.get("part_category"),
                    "part_label": row.get("part_label"),
                    "finished_goods_units": row.get("finished_goods_units"),
                    "wip_units": row.get("wip_units"),
                    "qa_hold_units": row.get("qa_hold_units"),
                    "committed_units": row.get("committed_units"),
                    "available_to_ship_units": row.get("available_to_ship_units"),
                    "raw_material_days_on_hand": row.get("raw_material_days_on_hand"),
                    "max_daily_output_units": row.get("max_daily_output_units"),
                    "data_status": row.get("data_status"),
                }
            )
        for row in dataset.get("frozen_orders", []):
            writer.writerow(
                {
                    "row_type": "frozen_order",
                    "id": row.get("id"),
                    "factory_id": row.get("factory_id"),
                    "factory_name": factory_names.get(row.get("factory_id")),
                    "part_category": row.get("part_category"),
                    "part_label": row.get("part_label"),
                    "frozen_quantity_units": row.get("frozen_quantity_units"),
                    "freeze_until_day": row.get("freeze_until_day"),
                    "data_status": row.get("data_status"),
                }
            )
        for row in dataset.get("in_transit_shipments", []):
            writer.writerow(
                {
                    "row_type": "in_transit_shipment",
                    "id": row.get("id"),
                    "factory_id": row.get("factory_id") or row.get("target_factory_id"),
                    "factory_name": factory_names.get(row.get("factory_id") or row.get("target_factory_id")),
                    "part_category": row.get("part_category") or row.get("target_part_category") or row.get("resource_category"),
                    "part_label": row.get("part_label") or row.get("resource_label"),
                    "shipment_kind": row.get("shipment_kind"),
                    "route_id": row.get("route_id"),
                    "quantity_units": row.get("quantity_units"),
                    "quantity_kg": row.get("quantity_kg"),
                    "progress_ratio": row.get("progress_ratio"),
                    "eta_hours": row.get("eta_hours"),
                    "data_status": row.get("data_status"),
                }
            )


def main() -> int:
    dataset, pipeline_context = build_dataset()
    write_outputs(dataset, pipeline_context)
    print(f"Generated {DATASET_JSON}")
    print(f"Generated {APP_JSON}")
    print(f"Generated {APP_JS}")
    print(f"Demo factories: {dataset['stats']['demo_factory_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

window.KOREA_CIVIL_INFRA_DATASET = {
  "schema": "korea_civil_infra_cop.v0.1",
  "generated_at": "2026-07-04T05:06:53.388772+00:00",
  "scenario": {
    "name": "Seoul Civil Infrastructure Protection COP",
    "purpose": "civilian protection, medical support, public-service continuity, and defensive staff awareness",
    "safety_boundary": "No exact sensitive telecom rooms, backbone routes, substations, or protected-facility coordinates are included.",
    "aoi": {
      "name": "Seoul Metropolitan AOI",
      "bounds": {
        "lat_min": 37.43,
        "lat_max": 37.69,
        "lon_min": 126.78,
        "lon_max": 127.16
      },
      "center": {
        "lat": 37.5665,
        "lon": 126.978
      }
    }
  },
  "source_catalog": [
    {
      "source": "HIRA hospital / pharmacy APIs",
      "status": "candidate_public_api",
      "public_url": "https://www.data.go.kr/data/15051059/fileData.do",
      "layer": "medical",
      "precision_allowed": "public exact for hospitals; no patient or PII data"
    },
    {
      "source": "NMC emergency medical APIs",
      "status": "candidate_public_api",
      "public_url": "https://www.data.go.kr/",
      "layer": "medical",
      "precision_allowed": "public exact for emergency facilities"
    },
    {
      "source": "MOLIT GIS building integrated information",
      "status": "candidate_public_api_or_shp",
      "public_url": "https://www.data.go.kr/data/15123970/openapi.do",
      "layer": "building",
      "precision_allowed": "building footprints can be public; demo uses aggregate exposure cells"
    },
    {
      "source": "VWorld map/geocoding/data API",
      "status": "key_available",
      "public_url": "https://www.vworld.kr/",
      "layer": "map",
      "precision_allowed": "base map and public geocoding"
    },
    {
      "source": "KCA mountain-area mobile radio station API",
      "status": "candidate_public_api",
      "public_url": "https://www.data.go.kr/data/15067860/openapi.do",
      "layer": "communications",
      "precision_allowed": "limited public wireless data; exact telecom backbone and rooms omitted"
    },
    {
      "source": "MOIS public-sector IT operating facilities",
      "status": "candidate_public_file_or_api",
      "public_url": "https://www.data.go.kr/data/15080581/fileData.do",
      "layer": "public_it",
      "precision_allowed": "city/county/district level only for demo"
    },
    {
      "source": "KPX generation facility / power market APIs",
      "status": "candidate_public_api",
      "public_url": "https://www.data.go.kr/data/15099767/openapi.do",
      "layer": "power",
      "precision_allowed": "regional/generator metadata; avoid sensitive substation/transmission detail"
    },
    {
      "source": "MOIS national core infrastructure statistics",
      "status": "candidate_public_api",
      "public_url": "https://www.data.go.kr/data/15107185/openapi.do",
      "layer": "critical_infra",
      "precision_allowed": "aggregate statistics only"
    }
  ],
  "layers": {
    "medical_facilities": [
      {
        "id": "med_nmc",
        "name": "National Medical Center",
        "kind": "public_hospital",
        "lat": 37.5672,
        "lon": 127.0057,
        "district": "Jung-gu",
        "role": "regional emergency care and public medical coordination",
        "capacity_tier": "high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "NMC emergency medical API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_snuh",
        "name": "Seoul National University Hospital",
        "kind": "tertiary_hospital",
        "lat": 37.5798,
        "lon": 126.999,
        "district": "Jongno-gu",
        "role": "tertiary emergency and trauma-capable medical support",
        "capacity_tier": "very_high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_severance",
        "name": "Severance Hospital",
        "kind": "tertiary_hospital",
        "lat": 37.5623,
        "lon": 126.9407,
        "district": "Seodaemun-gu",
        "role": "tertiary emergency care and west-Seoul medical anchor",
        "capacity_tier": "very_high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_st_mary",
        "name": "Seoul St. Mary's Hospital",
        "kind": "tertiary_hospital",
        "lat": 37.5019,
        "lon": 127.0058,
        "district": "Seocho-gu",
        "role": "south-central tertiary emergency care",
        "capacity_tier": "very_high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_asan",
        "name": "Asan Medical Center",
        "kind": "tertiary_hospital",
        "lat": 37.5263,
        "lon": 127.1086,
        "district": "Songpa-gu",
        "role": "east-Seoul tertiary emergency and high-capacity care",
        "capacity_tier": "very_high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_samsung",
        "name": "Samsung Medical Center",
        "kind": "tertiary_hospital",
        "lat": 37.4885,
        "lon": 127.0852,
        "district": "Gangnam-gu",
        "role": "south-east tertiary emergency care",
        "capacity_tier": "very_high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_korea_anam",
        "name": "Korea University Anam Hospital",
        "kind": "tertiary_hospital",
        "lat": 37.5871,
        "lon": 127.0267,
        "district": "Seongbuk-gu",
        "role": "north-east tertiary medical support",
        "capacity_tier": "high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_hanyang",
        "name": "Hanyang University Seoul Hospital",
        "kind": "general_hospital",
        "lat": 37.5598,
        "lon": 127.0446,
        "district": "Seongdong-gu",
        "role": "central-east emergency medical support",
        "capacity_tier": "high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_boramae",
        "name": "Seoul Metropolitan Boramae Medical Center",
        "kind": "public_hospital",
        "lat": 37.4931,
        "lon": 126.9245,
        "district": "Dongjak-gu",
        "role": "public emergency care and south-west support",
        "capacity_tier": "high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "NMC emergency medical API",
          "VWorld geocode"
        ]
      },
      {
        "id": "med_seoul_medical",
        "name": "Seoul Medical Center",
        "kind": "public_hospital",
        "lat": 37.612,
        "lon": 127.0983,
        "district": "Jungnang-gu",
        "role": "public medical anchor for north-east Seoul",
        "capacity_tier": "high",
        "source_mode": "public_exact",
        "source_candidates": [
          "HIRA hospital API",
          "NMC emergency medical API",
          "VWorld geocode"
        ]
      }
    ],
    "building_exposure_cells": [
      {
        "id": "bld_jongno_jung",
        "label": "Jongno/Jung CBD",
        "lat": 37.57,
        "lon": 126.985,
        "radius_km": 2.4,
        "density": 0.91,
        "civilian_exposure": "very_high",
        "mobility_constraint": "high"
      },
      {
        "id": "bld_yongsan",
        "label": "Yongsan transit/river corridor",
        "lat": 37.532,
        "lon": 126.98,
        "radius_km": 2.8,
        "density": 0.74,
        "civilian_exposure": "high",
        "mobility_constraint": "medium"
      },
      {
        "id": "bld_gangnam",
        "label": "Gangnam/Seocho dense business belt",
        "lat": 37.504,
        "lon": 127.033,
        "radius_km": 3.0,
        "density": 0.95,
        "civilian_exposure": "very_high",
        "mobility_constraint": "high"
      },
      {
        "id": "bld_songpa",
        "label": "Songpa east medical/logistics belt",
        "lat": 37.514,
        "lon": 127.104,
        "radius_km": 2.9,
        "density": 0.79,
        "civilian_exposure": "high",
        "mobility_constraint": "medium"
      },
      {
        "id": "bld_mapo_yeouido",
        "label": "Mapo/Yeouido river crossing belt",
        "lat": 37.54,
        "lon": 126.93,
        "radius_km": 3.2,
        "density": 0.82,
        "civilian_exposure": "high",
        "mobility_constraint": "high"
      },
      {
        "id": "bld_guro_geumcheon",
        "label": "Guro/Geumcheon industrial district",
        "lat": 37.485,
        "lon": 126.895,
        "radius_km": 3.4,
        "density": 0.69,
        "civilian_exposure": "medium",
        "mobility_constraint": "medium"
      },
      {
        "id": "bld_seongbuk_dobong",
        "label": "North-east residential belt",
        "lat": 37.635,
        "lon": 127.045,
        "radius_km": 3.6,
        "density": 0.66,
        "civilian_exposure": "medium",
        "mobility_constraint": "medium"
      },
      {
        "id": "bld_gimpo_gangseo",
        "label": "Gangseo/Gimpo airport access belt",
        "lat": 37.56,
        "lon": 126.815,
        "radius_km": 4.0,
        "density": 0.6,
        "civilian_exposure": "medium",
        "mobility_constraint": "medium"
      }
    ],
    "communications_context_cells": [
      {
        "id": "comm_north_ridge",
        "label": "North ridge wireless coverage aggregate",
        "lat": 37.65,
        "lon": 126.99,
        "radius_km": 6.0,
        "coverage_score": 0.73,
        "stress": "medium",
        "source_mode": "coarse_or_synthetic",
        "public_source_candidate": "KCA mountain-area mobile radio station API",
        "note": "Exact base-station locations are intentionally omitted."
      },
      {
        "id": "comm_han_river",
        "label": "Han River crossing communications aggregate",
        "lat": 37.535,
        "lon": 126.97,
        "radius_km": 8.0,
        "coverage_score": 0.82,
        "stress": "high",
        "source_mode": "coarse_or_synthetic",
        "public_source_candidate": "radio station statistics + synthetic coverage model",
        "note": "Represents expected civilian communications load around crossings."
      },
      {
        "id": "comm_southeast",
        "label": "South-east hospital corridor communications aggregate",
        "lat": 37.505,
        "lon": 127.095,
        "radius_km": 5.5,
        "coverage_score": 0.78,
        "stress": "medium",
        "source_mode": "coarse_or_synthetic",
        "public_source_candidate": "public radio statistics + service continuity assumption",
        "note": "No telecom room or backbone route is displayed."
      }
    ],
    "power_it_aggregates": [
      {
        "id": "it_public_ops_seoul",
        "label": "Public-sector IT operating facilities aggregate",
        "kind": "public_it_facility_aggregate",
        "lat": 37.566,
        "lon": 126.978,
        "district_level_only": true,
        "count_bucket": "500m2_plus facilities present",
        "source_mode": "district_aggregate",
        "source_candidate": "MOIS public-sector IT operating facilities list",
        "safe_use": "support continuity planning and restoration prioritization, not facility targeting"
      },
      {
        "id": "power_seoul_region",
        "label": "Seoul regional power dependency context",
        "kind": "power_dependency_aggregate",
        "lat": 37.52,
        "lon": 127.02,
        "district_level_only": true,
        "count_bucket": "regional context",
        "source_mode": "regional_aggregate",
        "source_candidate": "KPX power market generation facility info + public renewable datasets",
        "safe_use": "show dependency and restoration context without substation/backbone coordinates"
      },
      {
        "id": "critical_core_stats",
        "label": "National core infrastructure statistics",
        "kind": "national_core_infra_stat",
        "lat": 37.6,
        "lon": 126.91,
        "district_level_only": true,
        "count_bucket": "national aggregate only",
        "source_mode": "aggregate_only",
        "source_candidate": "MOIS national core infrastructure statistics",
        "safe_use": "display category awareness, not exact protected-facility locations"
      }
    ]
  },
  "semantic_events": [
    {
      "id": "evt_medical_access_north",
      "event_type": "MEDICAL_SUPPORT_CAPACITY",
      "severity": "high",
      "priority": 0.91,
      "lat": 37.579,
      "lon": 126.999,
      "summary": "Central and north-east hospitals provide overlapping emergency-care capacity near the AOI.",
      "why_it_matters": "Civilian casualty evacuation and hospital access routes should stay protected and unobstructed.",
      "recommended_action": "Maintain protected medical corridors, monitor congestion, and coordinate with civil authorities.",
      "evidence_refs": [
        "med_snuh",
        "med_nmc",
        "med_korea_anam",
        "bld_jongno_jung"
      ],
      "transmit_tier": "alert_card",
      "bytes_semantic": 780
    },
    {
      "id": "evt_building_density_cbd",
      "event_type": "CIVILIAN_EXPOSURE_DENSITY",
      "severity": "high",
      "priority": 0.87,
      "lat": 37.57,
      "lon": 126.985,
      "summary": "CBD building density and civilian exposure are high around the central AOI.",
      "why_it_matters": "Operations near dense civilian areas require stricter deconfliction and emergency-service access.",
      "recommended_action": "Use aggregate exposure to guide protection, evacuation support, and movement deconfliction.",
      "evidence_refs": [
        "bld_jongno_jung",
        "bld_yongsan"
      ],
      "transmit_tier": "exposure_summary",
      "bytes_semantic": 640
    },
    {
      "id": "evt_comms_stress_han",
      "event_type": "COMMUNICATION_COVERAGE_STRESS",
      "severity": "medium",
      "priority": 0.79,
      "lat": 37.535,
      "lon": 126.97,
      "summary": "Communications demand may concentrate around Han River crossing corridors.",
      "why_it_matters": "Civil warning, responder coordination, and restoration teams may need priority connectivity support.",
      "recommended_action": "Prioritize resilient civilian communications and do not disclose exact telecom facility locations.",
      "evidence_refs": [
        "comm_han_river",
        "bld_mapo_yeouido",
        "bld_yongsan"
      ],
      "transmit_tier": "context_summary",
      "bytes_semantic": 710
    },
    {
      "id": "evt_power_it_context",
      "event_type": "PUBLIC_IT_POWER_CONTEXT",
      "severity": "medium",
      "priority": 0.74,
      "lat": 37.552,
      "lon": 127.002,
      "summary": "Public IT facilities and regional power dependency should be treated as continuity context, not target data.",
      "why_it_matters": "Staff should understand service continuity dependencies while avoiding disclosure of sensitive nodes.",
      "recommended_action": "Show district aggregate, protect restoration access, and keep exact sensitive facility data out of the COP.",
      "evidence_refs": [
        "it_public_ops_seoul",
        "power_seoul_region",
        "critical_core_stats"
      ],
      "transmit_tier": "aggregate_context",
      "bytes_semantic": 690
    }
  ],
  "network_modes": {
    "full_context": {
      "label": "Full context",
      "bandwidth_kbps": 4000,
      "description": "All public points and aggregate overlays are visible."
    },
    "semantic_summary": {
      "label": "Semantic summary",
      "bandwidth_kbps": 96,
      "description": "Only priority events and aggregate counts are transmitted."
    },
    "civil_authority_handoff": {
      "label": "Civil authority handoff",
      "bandwidth_kbps": 512,
      "description": "Medical, public warning, and restoration context is emphasized."
    }
  },
  "safety_rules": [
    "Use real public hospital data as protected civilian assets only.",
    "Represent telecom, public IT, power, and national core infrastructure as aggregate or synthetic layers.",
    "Do not infer targets, vulnerabilities, attack paths, or exact protected-facility locations.",
    "Use this COP for deconfliction, protection, restoration, evacuation support, and continuity planning."
  ]
};

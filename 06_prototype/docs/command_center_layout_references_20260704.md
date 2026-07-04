# Command Center Layout References

- Date: 2026-07-04 KST
- Target artifact: `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop`

## Reference Patterns

### SeaVision

Source: https://info.seavision.volpe.dot.gov/

Useful pattern:

- primary surface is a real-time maritime map;
- AIS and SAT-SAR are map layers, not separate pages;
- rules and anomaly alerts sit around the map;
- map, search/filter, vessel lists, alerts, and sharing/community features support the same COP.

Design implication:

- The D4D demo should make the map the visual center and show semantic alerts as overlays or immediate side-panel selections.

### Global Fishing Watch Map

Source: https://globalfishingwatch.org/map and https://globalfishingwatch.org/user-guide/

Useful pattern:

- open map first;
- layer controls and vessel/activity analysis are secondary to the ocean view;
- maritime activity is understood spatially through density, vessel presence, and event overlays.

Design implication:

- The D4D demo should avoid feeling like a generic analytics page. Vessel tracks, SAR-like detections, and event markers should be visually dominant.

### ArcGIS Dashboards

Source: https://www.esri.com/en-us/arcgis/products/arcgis-dashboards/overview and https://doc.arcgis.com/en/dashboards/latest/get-started/what-is-a-dashboard.htm

Useful pattern:

- single-screen operational view;
- geographic information plus supporting visualizations;
- dashboards should help users monitor events, make decisions, and see trends at a glance;
- rows/columns support predictable placement of map, indicators, lists, and details.

Design implication:

- Use a command-board grid: central map, left queue, right evidence, top indicators, bottom briefing.

### TAK / ATAK

Sources:

- https://www.civtak.org/atak-about/
- https://wftak.wildfire.gov/pages/what-is-wftak

Useful pattern:

- common operating picture for distributed teams;
- map-centric geospatial situational awareness;
- communication and sharing are core, not afterthoughts.

Design implication:

- Network/degraded-link state should be visible beside the map, because the D4D concept is not only maritime awareness but COP survivability over constrained networks.

## Layout Decision

The revised demo should use this structure:

```text
Top command bar:
  operation name, clock, message survival, byte savings

Main board:
  left rail:
    network mode selector
    priority event queue

  center:
    large COP map
    map HUD: AOI, selected event, link mode, transmission decision

  right rail:
    evidence bundle
    raw-vs-semantic transmission result
    data/API readiness

Bottom band:
  grounded briefing
  glossary helper
```

This makes the demo feel closer to a command center situation board while preserving the existing semantic-event and evidence-bundle logic.

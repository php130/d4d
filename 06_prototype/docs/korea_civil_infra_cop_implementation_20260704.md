# Korea Civil Infrastructure COP Implementation

Date: 2026-07-04

## Purpose

This prototype implements a safe Korea civil infrastructure COP for D4D staff-system demos.

The intended use is civilian protection, medical support, public-service continuity, evacuation/deconfliction support, and defensive staff awareness.

## Current Build

- Dataset root: `/Users/mollykim/projects/D4D/03_data/korea_civil_infra_cop`
- Demo app: `/Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop`
- Dataset generator: `/Users/mollykim/projects/D4D/06_prototype/scripts/generate_korea_civil_infra_cop_dataset.py`
- Building footprint collector: `/Users/mollykim/projects/D4D/06_prototype/scripts/collect_korea_building_footprints_osm.py`
- Map base: Leaflet + OpenStreetMap public raster tiles

Generated layers:

| Layer | Count | Precision |
|---|---:|---|
| Medical facilities | 10 | public exact, treated as protected civilian assets |
| Building footprints | 3,200 | public exact OSM building polygons, no PII |
| Building exposure cells | 8 | aggregate / synthetic fallback |
| Communications context cells | 3 | coarse / synthetic |
| Power and public IT aggregates | 3 | aggregate only |
| Semantic events | 4 | compressed COP event summaries |

Building footprint class counts from the current OSM collection:

| Class | Count |
|---|---:|
| commercial | 1,401 |
| other_building | 955 |
| residential / apartments-like | 665 |
| public_or_civic | 175 |
| industrial | 4 |

## Safety Boundary

The prototype intentionally avoids exact coordinates for sensitive facilities:

- telecom rooms
- wired backbone routes
- base-station dependency nodes beyond public/coarse context
- substations and transmission nodes
- nationally protected facility locations
- military facilities

These categories are represented only as aggregate, regional, district-level, or synthetic context.

## Data Source Candidates

Source metadata is stored in:

`/Users/mollykim/projects/D4D/03_data/korea_civil_infra_cop/metadata/source_catalog.json`

Key candidates:

- HIRA hospital/pharmacy public data
- NMC emergency medical APIs
- MOLIT GIS building integrated information
- VWorld map/geocoding APIs
- KCA public wireless/radio station datasets
- MOIS public-sector IT operating facility data
- KPX power market/generation facility APIs
- MOIS national core infrastructure statistics

## Run

```bash
cd /Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop
PORT=8771 npm start
```

Then open:

```text
http://localhost:8771
```

## Verification

Commands used:

```bash
python3 /Users/mollykim/projects/D4D/06_prototype/scripts/generate_korea_civil_infra_cop_dataset.py
python3 -m py_compile /Users/mollykim/projects/D4D/06_prototype/scripts/generate_korea_civil_infra_cop_dataset.py
python3 -m json.tool /Users/mollykim/projects/D4D/03_data/korea_civil_infra_cop/korea_civil_infra_cop_dataset.json >/dev/null
node --check /Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop/assets/app.js
node --check /Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop/server.js
```

## Next API Attachment Pattern

1. Ingest public exact hospital data as protected civilian assets.
2. Ingest public building footprints directly for civilian exposure; keep resident, owner, unit-level, contact, and access-control data out of scope.
3. Convert communications and power data to coarse coverage/dependency context before display.
4. Store exact sensitive source data outside public deliverables, or avoid collecting it when not required.
5. Emit semantic events with evidence references, priority, recommended action, and transmit tier.

## Map Base Note

The public demo uses OpenStreetMap tiles so the external link does not expose private VWorld API keys in browser source.

If VWorld is preferred for Korea-specific styling, add a small server-side tile/geocode proxy first, then keep the key in `.env` on the server side instead of shipping it to the browser.

The building layer currently uses OpenStreetMap Overpass building footprints for the public demo. Official Korean building data should be added through a server-side collector using MOLIT GIS building integrated information or VWorld WFS, with API keys kept out of browser-delivered JavaScript.

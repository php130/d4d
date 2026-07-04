# Korea Civil Infrastructure COP Dataset

- Generated: 2026-07-04T05:06:53.388772+00:00
- Scenario: Seoul Civil Infrastructure Protection COP
- Purpose: civilian protection, medical support, public-service continuity, and defensive staff awareness.

## Safety Boundary

This dataset does not include exact coordinates for sensitive telecom rooms, backbone routes, substations, military facilities, or nationally protected facilities.

Sensitive infrastructure is represented as:

- district or regional aggregate
- synthetic coverage/context cell
- public statistics only

## Layers

| Layer | Count | Precision |
|---|---:|---|
| Medical facilities | 10 | public exact, protected civilian assets |
| Building exposure cells | 8 | aggregate / synthetic |
| Communications context cells | 3 | coarse / synthetic |
| Power and public IT aggregates | 3 | aggregate only |
| Semantic events | 4 | safe event summaries |

## Source Candidates

See `metadata/source_catalog.json` for public source URLs and precision rules.

## Demo App

Local app path:

```text
/Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop
```

## Use Rule

Use this package for deconfliction, protection, medical support, public communications continuity, and restoration prioritization. Do not use it to infer attack paths, target lists, or vulnerabilities.

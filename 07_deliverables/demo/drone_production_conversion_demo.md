# Drone Production Conversion Demo

## Open

```bash
cd /Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion
PORT=8782 npm start
```

Then open:

```text
http://localhost:8782
```

## Demo Story

1. Start on the full-screen satellite map and frame it as a production/resource decision canvas.
2. Open the compact summary chip to show target drones, feasible volume, and shortfall.
3. Open `Layers` only when needed, then show candidate factories and critical-resource nodes from public data.
4. Point to animated flows from resources to part factories, then from factories to assembly hubs.
5. Point out that route distances are road-network distances, not straight-line measurements.
6. Click a factory or resource node to open the selected-node drawer with public evidence, confidence, assignment, capacity tier, 30-day production estimate, energy/capa evidence, and verification checklist.
7. Open `Dataset` to show BOM bottleneck, active flow ledger, public-source status, and critical-material feeder summary.
8. Close on the operating logic: production continuity depends on upstream materials, factory capacity evidence, road logistics cost, and verification readiness.

## One-Line Pitch

전시 드론 수요가 폭증했을 때 공개 공장등록 데이터로 부품군별 후보 공장과 희토류·폐배터리 등 선행 자원 후보를 찾고, 위협 예측에 따라 수급·조립 경로를 즉시 재구성하는 지속지원 C2 데모입니다.

# Public Deployment Note

- Date: 2026-07-04 KST
- Deployment name: `d4d-cop-public`
- Local app path: `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop`
- Local port: `3006`
- Public URL: https://anti-plug-cheapest-hoped.trycloudflare.com

## What Is Deployed

The deployed demo is the static S-DOT Mission Continuity COP prototype with a small Node.js static server. It still lives under the original `resilient_maritime_cop` app directory, but the user-facing product framing is now `S-DOT 시맨틱 전송 | Semantic Data On Tactical-network`.

Current visible scope:

- Korean-first S-DOT mission-continuity COP dashboard
- command-center situation board layout with central Seoul ground map
- top operation objective banner: `서울 도심 임무지속 방호`
- Leaflet + OpenStreetMap base map
- Seoul building-footprint overlay from the Korea civil infra COP workstream
- 12 semantic events
- 5 degraded-network transmission modes
- 3 synthetic unit nodes with `12-1`, `12-2`, `12-3` map symbols
- 3 synthetic opposing movement candidate axes rendered as probability branches
- probabilistic branch scenarios for isolated/intermittent units
- 2 synthetic civil/public bearer candidates
- Korea civil infrastructure COP context layers on the main map
- 3 synthetic urban support routes
- 4-step PACE/Bearer ladder
- 3 synthetic support options
- 5 S-DOT command/status/support packets
- mission intent, unit state, support routing, network/PACE, and rejoin-audit panels
- data/API readiness strip
- evidence bundle panel
- raw-vs-semantic transmission comparison
- grounded briefing panel

The current build ships with packaged mock data. Live-ready APIs and pending APIs are shown explicitly in the UI so external viewers can distinguish real integration readiness from synthetic demo backbone data. Unit disposition, readiness, military support resources, tactical network state, and resource-allocation decisions are intentionally synthetic and must not be replaced with real force posture data.

## Process Layout

| Process | Role |
| --- | --- |
| `ld-d4d-cop-public` | Node static server managed by local-deployer/pm2 |
| `ld-d4d-cop-public-tunnel` | Cloudflare quick tunnel managed by pm2 |

## Verification

HTTP check:

```bash
curl -I https://anti-plug-cheapest-hoped.trycloudflare.com
curl https://anti-plug-cheapest-hoped.trycloudflare.com/healthz
```

Current shell/static verification:

- deployment `d4d-cop-public` is running on port `3006`
- `/healthz` returns `ok`
- title source contains `S-DOT 임무지속 COP 데모`
- HTML contains the objective banner, mission grid container, and S-DOT panel targets
- dataset id: `s_dot_seoul_ground_mission_continuity_mock_v0_5`
- operation objective: `서울 도심 임무지속 방호`
- event buttons expected from data: `12`
- network mode buttons expected from data: `5`
- PACE/Bearer options: `4`
- Alpha-1 branch scenarios: `3`
- Korea civil infra context: 6 hospitals, 3 communications aggregates, 4 semantic events
- OpenStreetMap building footprints served locally: `3200`
- maritime vessels/tracks in active dataset: `0/0`
- synthetic opposing candidate axes: `3`
- synthetic unit nodes: `3`
- synthetic support options: `3`
- S-DOT message packets: `5`
- `mock_dataset.json` is valid JSON
- `assets/app.js` and `assets/glossary.js` pass `node --check`

Browser note:

- Direct in-app browser verification of both `127.0.0.1:3006` and the current Cloudflare tunnel was blocked by Codex browser security policy on 2026-07-04. No workaround browser surface was used after that policy block.

## Useful Commands

List deployments:

```bash
cd /Users/mollykim/projects/local-deployer
uv run deployer list
```

Show app logs:

```bash
cd /Users/mollykim/projects/local-deployer
uv run deployer logs d4d-cop-public --lines 80
```

Show tunnel logs:

```bash
pm2 logs ld-d4d-cop-public-tunnel --nostream --lines 100
```

Stop the public demo:

```bash
cd /Users/mollykim/projects/local-deployer
uv run deployer stop d4d-cop-public
pm2 delete ld-d4d-cop-public-tunnel
```

## Note

Cloudflare account-less quick tunnel URLs are ephemeral and have no uptime guarantee. If the URL becomes unreachable, keep the local-deployer app process and recreate only the tunnel process:

```bash
pm2 delete ld-d4d-cop-public-tunnel
pm2 start cloudflared --name ld-d4d-cop-public-tunnel -- tunnel --url http://localhost:3006
pm2 logs ld-d4d-cop-public-tunnel --nostream --lines 100
```

# Korea Civil Infrastructure COP Public Deployment

- Date: 2026-07-04 KST
- Deployment name: `d4d-korea-civil-infra-cop`
- Local app path: `/Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop`
- Local-deployer port: `3007`
- Public URL: https://margin-david-integrated-meant.trycloudflare.com

## What Is Deployed

The deployed app is the safe Korea Civil Infrastructure COP prototype.

Visible scope:

- actual map basemap using Leaflet + OpenStreetMap public raster tiles
- public medical facilities as protected civilian support nodes
- 3,200 public OSM building footprints, including 665 residential/apartments-like buildings
- aggregate building exposure cells as fallback only
- coarse/synthetic communications context cells
- aggregate-only power, public IT, and national core infrastructure context
- semantic COP events for civil protection, restoration, and deconfliction
- explicit safety boundary that omits sensitive exact coordinates

## Process Layout

| Process | Role |
| --- | --- |
| `ld-d4d-korea-civil-infra-cop` | Node static server managed by local-deployer/pm2 |
| `ld-d4d-korea-civil-infra-cop-tunnel` | Cloudflare quick tunnel managed by pm2 |

## Verification

```bash
curl -I -L https://margin-david-integrated-meant.trycloudflare.com
curl https://margin-david-integrated-meant.trycloudflare.com/healthz
curl https://margin-david-integrated-meant.trycloudflare.com/ | rg -o '<title>[^<]+'
```

Verified:

- local `/healthz` returns `ok`
- public URL returns HTTP 200
- public `/healthz` returns `ok`
- public HTML title is `Korea Civil Infrastructure COP`
- local browser loads real map tiles, 3,200 building SVG polygons, and COP markers without console errors
- local-deployer list shows the deployment as `running`

## Useful Commands

List deployments:

```bash
/Users/mollykim/projects/local-deployer/.venv/bin/deployer list
```

Show app logs:

```bash
/Users/mollykim/projects/local-deployer/.venv/bin/deployer logs d4d-korea-civil-infra-cop --lines 80
```

Show tunnel logs:

```bash
pm2 logs ld-d4d-korea-civil-infra-cop-tunnel --nostream --lines 100
```

Stop the public demo:

```bash
/Users/mollykim/projects/local-deployer/.venv/bin/deployer stop d4d-korea-civil-infra-cop
pm2 delete ld-d4d-korea-civil-infra-cop-tunnel
```

## Note

Cloudflare account-less quick tunnel URLs are ephemeral and have no uptime guarantee. If this URL becomes unreachable, keep the local-deployer app process and recreate only the tunnel:

```bash
pm2 delete ld-d4d-korea-civil-infra-cop-tunnel
pm2 start cloudflared --name ld-d4d-korea-civil-infra-cop-tunnel -- tunnel --url http://localhost:3007
pm2 logs ld-d4d-korea-civil-infra-cop-tunnel --nostream --lines 100
```

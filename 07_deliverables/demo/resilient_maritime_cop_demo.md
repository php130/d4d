# S-DOT 임무지속 COP 데모

Local app:

- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/index.html`

The app can be opened directly in a browser because it includes a local dataset JS fallback. The current prototype reuses the original Resilient Maritime COP app path, but the product framing is now `S-DOT 시맨틱 전송 | Semantic Data On Tactical-network` for a Seoul urban-ground mission-continuity scenario.

The UI is Korean-first for the D4D Seoul hackathon. English technical terms are retained only where they help reviewers connect the demo to the track language.

Optional local server command:

```bash
cd /Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop
python3 -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

The app uses:

- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.json`
- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/data/mock_dataset.js`

Data boundary:

- Public/open data is used only as context or evidence-type scaffolding.
- Unit locations, readiness, support resources, tactical network state, and resource allocation are synthetic scenario data.
- Do not replace these layers with real military unit disposition, readiness, or operational resource placement data.

Verified behavior:

- 5 network modes render.
- 12 semantic events render.
- top operation objective banner renders.
- 3 synthetic opposing candidate axes render as probability branches.
- 3 synthetic unit nodes render as compact `12-x` map symbols.
- probabilistic branch scenarios render under unit cards.
- Seoul actual/public map renders through Leaflet + OpenStreetMap.
- Seoul building footprints and civil infrastructure context render on the main map.
- Maritime vessels/tracks are removed from the active generated dataset.
- PACE/Bearer ladder renders as the fourth plane.
- 3 synthetic support options render.
- 3 synthetic support routes render.
- 5 S-DOT message packets render.
- switching `Local Only` changes packet decisions toward `LOCAL`.
- evidence drawer shows source observations for the selected event.
- JSON and JavaScript syntax checks pass.

Browser note:

- Direct in-app browser verification of `127.0.0.1` and the current Cloudflare tunnel was blocked by the Codex browser security policy on 2026-07-04. Local server health and static asset checks were verified from the shell instead.

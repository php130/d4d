# Resilient Maritime COP Demo

Local app:

- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/index.html`

The app can be opened directly in a browser because it includes a local dataset JS fallback.

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

Verified behavior:

- 5 network modes render.
- 7 semantic events render.
- switching `Local Only` changes all packet decisions to `LOCAL`.
- evidence drawer shows source observations for the selected event.
- no browser console errors after favicon fix.

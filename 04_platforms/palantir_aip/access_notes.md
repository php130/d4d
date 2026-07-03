# Palantir Access Notes

Last checked: 2026-06-29

## Checked URLs

| URL | Result | Notes |
| --- | --- | --- |
| https://www.palantir.com/docs | Accessible | Official docs portal is accessible. |
| https://www.palantir.com/docs/foundry/aip/overview/ | Accessible | AIP overview page is accessible. |
| https://www.palantir.com/docs/foundry/aip-analyst/overview/ | Accessible | AIP Analyst overview page is accessible. |
| https://www.palantir.com/docs/foundry/aip-evals/overview/ | Accessible | AIP Evals overview page is accessible. |
| https://www.palantir.com/docs/foundry/security/overview/ | Accessible | Security and governance docs are accessible. |
| https://build.palantir.com/ | Public SPA | HTML and JS bundle accessible. Needs JS rendering for full UI. Public bundle contains example metadata. |
| https://learn.palantir.com/speedrun-your-first-e2e-workflow | 403 | CloudFront 403 during public fetch. Likely requires login, enrollment, or permitted access path. |

## Browser Rendering Status

Attempted to connect to the in-app browser for JS rendering, but the browser bridge returned: `browser-client is not trusted`.

Fallback used:

- Public HTML fetch
- Build site JS bundle inspection
- Official docs pages

Next step if exact tutorial UI is needed:

- Open `build.palantir.com` manually in a browser session with JavaScript enabled.
- If `learn.palantir.com` is required, sign in or use the hackathon-provided enrollment link, then re-run the browser inspection.


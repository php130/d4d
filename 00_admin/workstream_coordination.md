# D4D Workstream Coordination

- Created: 2026-07-04 KST
- Purpose: avoid conflicts between the API collection session and prototype/report implementation.

## Active Workstreams

### 1. `D4D_리서치` session

Primary responsibility:

- API account/key issuance
- external data source smoke tests
- live connector planning
- API collection tracker updates

Likely touched paths:

- `/Users/mollykim/projects/D4D/.env`
- `/Users/mollykim/projects/D4D/.env.example`
- `/Users/mollykim/projects/D4D/01_research/osint_sources/api_collection_tracker.md`
- `/Users/mollykim/projects/D4D/02_problem_statements/hypotheses/resilient_maritime_cop_data_api_plan.md`
- `/Users/mollykim/projects/D4D/08_ops/runbooks/resilient_maritime_cop_data_connection_guide.md`
- `/Users/mollykim/projects/D4D/01_research/research_log.md`

Important boundary:

- Do not expose values from `.env`.
- Do not overwrite API tracker status while another session is issuing keys.
- Treat live API connector status as owned by `D4D_리서치` unless explicitly asked to take over.

### 2. Current prototype/report workstream

Primary responsibility:

- technical design for the Resilient Maritime COP demo
- mock dataset with source/evidence rationale
- local demo app
- non-technical HTML explainer report

Owned paths:

- `/Users/mollykim/projects/D4D/06_prototype/docs/resilient_maritime_cop_technical_design.md`
- `/Users/mollykim/projects/D4D/03_data/samples/resilient_maritime_cop/`
- `/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop/`
- `/Users/mollykim/projects/D4D/07_deliverables/report/resilient_maritime_cop_explainer.html`
- `/Users/mollykim/projects/D4D/07_deliverables/demo/`

## Integration Rule

The prototype must run without live API keys. Live APIs can later replace the mock adapters if the `D4D_리서치` session succeeds.

The shared contract is:

```text
raw snapshot -> normalized record -> semantic event -> priority packet -> COP update
```

If API data arrives later, only the `raw snapshot` and `normalized record` layer should change. The demo UI, semantic event schema, routing policy, and report should remain stable.


# Literature Collection Runbook

D4D 관련 논문 메타데이터를 새로 수집할 때 사용합니다.

## Refresh

```bash
cd /Users/mollykim/projects/D4D
./06_prototype/scripts/collect_literature_seed.py \
  --project-root /Users/mollykim/projects/D4D \
  --per-query 8 \
  --sleep 0.25
```

## Outputs

- Raw run log: `03_data/raw/literature/<version>/collection_run_log.json`
- Processed JSON: `03_data/processed/literature/versions/<version>/literature_seed_catalog.json`
- Processed CSV: `03_data/processed/literature/versions/<version>/literature_seed_catalog.csv`
- Human-readable catalog: `01_research/literature/literature_seed_catalog.md`
- Latest symlink: `03_data/processed/literature/current`

## After Refresh

1. Check counts in `dataset_manifest.json`.
2. Inspect top results by track.
3. Move truly relevant papers into `01_research/literature/first_reading_queue.md`.
4. For each read paper, create a note using `paper_note_template.md`.
5. Add any dataset/code links from papers into `01_research/osint_sources/osint_source_catalog.md`.

## Good Follow-up Queries

- `OSINT analyst copilot source citation provenance`
- `source credibility open source intelligence analysis`
- `dark web threat intelligence credential exposure dataset`
- `AIS anomaly detection dark vessel SAR fusion`
- `common operational picture ontology command and control`
- `semantic communication tactical networks bandwidth constrained`
- `offline RAG edge LLM on device`
- `military wargaming LLM after action review`


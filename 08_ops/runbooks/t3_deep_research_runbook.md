# T3 Deep Research Runbook

Use this to refresh focused literature research for the T3 semantic COP project.

## Run

```bash
cd /Users/mollykim/projects/D4D
./06_prototype/scripts/collect_t3_deep_research.py \
  --project-root /Users/mollykim/projects/D4D \
  --per-query 10 \
  --snowball-per-seed 4 \
  --max-snowball-fetches 180 \
  --sleep 0.12
```

## Outputs

- Raw log: `03_data/raw/literature_t3/<version>/collection_run_log.json`
- Processed dataset: `03_data/processed/literature_t3/versions/<version>/`
- Current pointer: `03_data/processed/literature_t3/current`
- Human-readable catalog: `01_research/literature/t3_deep_research/t3_deep_research_catalog.md`

## After Running

1. Inspect top 60 records.
2. Remove generic-but-high-score papers from the reading queue.
3. Update `t3_first_reading_queue.md`.
4. Add dataset/code links discovered from papers to `dataset_candidates.md`.
5. Add defensible pitch claims to `pitch_evidence.md`.


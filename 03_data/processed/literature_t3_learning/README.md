# T3 Literature Learning Dataset

This folder stores structured learning outputs generated from the T3 priority reading queue.

## Versions

- `20260703_225103`: priority papers 01-10
- `20260703_225652`: priority papers 11-20
- `20260703_231026`: priority papers 21-40
- `current`: symlink to the most recent batch run, currently `20260703_231026`

For the full 40-paper learning set, use all three version folders and the Markdown notes in:

`/Users/mollykim/projects/D4D/01_research/literature/t3_deep_research/paper_notes`

## Contents

Each version folder contains:

- per-paper structured JSON summaries
- `learning_manifest.json`

Raw PDFs and extracted text are stored under:

`/Users/mollykim/projects/D4D/03_data/raw/literature_t3_learning`

## Evidence Strength

Some papers were processed from full or partial extracted PDF text. Others used abstract/metadata fallback because the PDF URL was missing or blocked. Do not use `abstract_only` notes for detailed performance claims unless the full paper is later verified.

# Google Sheet Dataset Versioning Runbook

소스 Google Sheet는 계속 바뀔 수 있으므로, 매번 raw snapshot과 processed dataset을 함께 남깁니다.

## Source

- Spreadsheet: `D4D_SEOUL_참가자안내(260629/공개)`
- URL: https://docs.google.com/spreadsheets/d/1l_ThafA1n5Wue2BnPeJ1FPpiZvThG6X9iIPRuJsxR5o/edit
- Track problem tab: `B-2. 트랙별_문제`, gid `1313109997`
- Glossary tab: `B-3. 용어집`, gid `1682873298`

## Refresh Steps

```bash
cd /Users/mollykim/projects/D4D
version=$(date +%Y%m%d_%H%M%S)
./06_prototype/scripts/build_d4d_sheet_dataset.py \
  --project-root /Users/mollykim/projects/D4D \
  --version "$version" \
  --download
```

## Outputs

Raw snapshot:

- `03_data/raw/google_sheets/<version>/B-2_track_problems.csv`
- `03_data/raw/google_sheets/<version>/B-3_glossary.csv`

Processed snapshot:

- `03_data/processed/versions/<version>/dataset_manifest.json`
- `03_data/processed/versions/<version>/track_problem_statements.json`
- `03_data/processed/versions/<version>/track_problem_statements.csv`
- `03_data/processed/versions/<version>/glossary_terms.json`
- `03_data/processed/versions/<version>/glossary_terms.csv`
- `03_data/processed/versions/<version>/tracks.json`

Project docs updated by the script:

- `00_admin/glossary.md`
- `02_problem_statements/tracks/d4d_track_problem_dataset.md`
- `03_data/processed/VERSIONS.md`
- `03_data/processed/current`

## Verification

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path("/Users/mollykim/projects/D4D/03_data/processed/current")
manifest = json.loads((root / "dataset_manifest.json").read_text())
print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
PY
```

## Notes

- `current`는 최신 버전으로 이동하지만, `versions/` 아래의 이전 버전은 삭제하지 않습니다.
- source row가 각 record에 남기 때문에 시트 변경사항을 추적하기 쉽습니다.
- API key, private token, 민감 데이터는 raw snapshot에 넣지 않습니다.


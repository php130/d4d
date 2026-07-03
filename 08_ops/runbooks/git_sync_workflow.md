# Git Sync Workflow

This project is stored in a private GitHub repository. Use Git history as the shared source of truth across Codex sessions.

## Safety Rule

Do not commit local secrets or raw private data.

Tracked:
- project notes
- research summaries
- mock and synthetic sample data
- prototype code
- reports and deliverables
- `.env.example`

Ignored:
- `.env`
- `.env.*`
- API keys, tokens, credential files
- `03_data/raw/**`
- `03_data/samples/private/**`

## Check Whether This Session Is Newer Than GitHub

Run:

```bash
cd /Users/mollykim/projects/D4D
./08_ops/scripts/git_sync_status.sh
```

Read the output as:

- `ahead > 0`: local commits exist that are not pushed yet.
- `behind > 0`: GitHub has commits that local repo has not pulled yet.
- `changed files > 0`: local files changed but are not committed yet.
- `clean: yes`: local working tree matches the latest local commit.

## Normal Update Flow

```bash
cd /Users/mollykim/projects/D4D
git fetch origin
git status -sb
git add <intended-files>
git commit -m "short description"
git push
./08_ops/scripts/git_sync_status.sh
```

After `git push`, the status script should show `ahead: 0` and `clean: yes`.

## Compare Last Local Commit With GitHub

```bash
git rev-parse HEAD
git rev-parse origin/main
git log --oneline --decorate -5
```

If `HEAD` and `origin/main` are the same commit, this folder is pushed to the latest GitHub version.

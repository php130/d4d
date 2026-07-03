#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repository"
  exit 1
fi

branch="$(git branch --show-current)"
remote_branch="origin/${branch}"

git fetch origin >/dev/null 2>&1 || true

if git rev-parse --verify "${remote_branch}" >/dev/null 2>&1; then
  read -r behind ahead < <(git rev-list --left-right --count "${remote_branch}...HEAD")
else
  behind="n/a"
  ahead="n/a"
fi

changed="$(git status --porcelain | wc -l | tr -d ' ')"
head_short="$(git rev-parse --short HEAD 2>/dev/null || echo "none")"
remote_short="$(git rev-parse --short "${remote_branch}" 2>/dev/null || echo "none")"

echo "repo: $(basename "$(pwd)")"
echo "branch: ${branch}"
echo "HEAD: ${head_short}"
echo "remote ${remote_branch}: ${remote_short}"
echo "behind: ${behind}"
echo "ahead: ${ahead}"
echo "changed files: ${changed}"

if [[ "${changed}" == "0" ]]; then
  echo "clean: yes"
else
  echo "clean: no"
fi

#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <new_project_name>" >&2
  exit 1
fi

PROJECT_NAME="$1"
KEYWORD="pyproject"

# Переименование директории
if [ -d "src/$KEYWORD" ]; then
  mv "src/$KEYWORD" "src/$PROJECT_NAME"
fi

find . \
  \( \
    -path './.venv' \
    -o -path './.git' \
    -o -path './.vscode' \
    -o -path './.ruff_cache' \
    -o -path './.mypy_cache' \
    -o -path './.idea' \
  \) -prune \
  -o -type f \
  ! -name 'uv.lock' \
  ! -name 'rename.sh' \
  -print0 \
| xargs -0 perl -pi -e "
    next if m{github\\.com/draincoder/$KEYWORD};
    s/\\b$KEYWORD\\b(?!\\.toml)/$PROJECT_NAME/g;
  "

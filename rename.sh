#!/usr/bin/env bash
set -euo pipefail

KEYWORD="pyproject"
PROJECT_NAME="${1:-}"

if [ -z "$PROJECT_NAME" ]; then
  PROJECT_NAME="$(basename "$PWD")"
fi

if ! [[ "$PROJECT_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]]; then
  echo "Project name must match ^[A-Za-z0-9][A-Za-z0-9_.-]*$: $PROJECT_NAME" >&2
  exit 1
fi

PYTHON_NAME="$(
  printf '%s' "$PROJECT_NAME" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/_/g; s/^_+//; s/_+$//; s/_+/_/g'
)"

if [ -z "$PYTHON_NAME" ]; then
  echo "Project name cannot be normalized to a Python package name: $PROJECT_NAME" >&2
  exit 1
fi

if [[ "$PYTHON_NAME" =~ ^[0-9] ]]; then
  PYTHON_NAME="_$PYTHON_NAME"
fi

replace_in_file() {
  local file="$1"
  local from="$2"
  local to="$3"

  if [ -f "$file" ]; then
    perl -0pi -e "s{\\Q$from\\E}{$to}g" "$file"
  fi
}

remove_project_urls() {
  local file="pyproject.toml"

  if [ -f "$file" ]; then
    perl -0pi -e 's/\n\[project\.urls\]\n(?:[^\n]*\n)*?(?=\n\[)/\n/s' "$file"
  fi
}

remove_rename_recipe() {
  local file="justfile"

  if [ -f "$file" ]; then
    perl -0pi -e 's/\n# Rename project\n\@rename name=.*\n(?:    [^\n]*\n)+//g' "$file"
  fi
}

update_readme() {
  local file="README.md"

  if [ -f "$file" ]; then
    perl -0pi -e "s/^# PyProject$/# $PROJECT_NAME/m" "$file"
    perl -0pi -e "s/^Minimal template for a quick start of a Python project\\.$/Minimal infrastructure settings for $PROJECT_NAME./m" "$file"
    perl -0pi -e '/^just rename\b/d' "$file"
  fi
}

if [ -d "src/$KEYWORD" ] && [ "$PYTHON_NAME" != "$KEYWORD" ]; then
  mv "src/$KEYWORD" "src/$PYTHON_NAME"
fi

replace_in_file "pyproject.toml" 'name = "pyproject"' "name = \"$PROJECT_NAME\""
remove_project_urls

for file in \
  README.md \
  justfile \
  config/template.env \
  docker/docker-compose.yaml \
  src/"$PYTHON_NAME"/main.py \
  src/"$PYTHON_NAME"/config.py \
  tests/unit/test_config.py \
  tests/unit/test_logger.py
do
  replace_in_file "$file" "$KEYWORD" "$PYTHON_NAME"
done

replace_in_file ".github/workflows/test.yaml" "--cov=$KEYWORD" "--cov=$PYTHON_NAME"

replace_in_file "docker/docker-compose.yaml" "$PYTHON_NAME:" "$PROJECT_NAME:"
replace_in_file "docker/docker-compose.yaml" "container_name: $PYTHON_NAME" "container_name: $PROJECT_NAME"
replace_in_file "docker/docker-compose.yaml" "hostname: $PYTHON_NAME" "hostname: $PROJECT_NAME"
replace_in_file "config/template.env" "/etc/$PYTHON_NAME/" "/etc/$PROJECT_NAME/"
replace_in_file "docker/docker-compose.yaml" "/etc/$PYTHON_NAME/" "/etc/$PROJECT_NAME/"

update_readme
remove_rename_recipe

git add -- \
  .github/workflows/test.yaml \
  README.md \
  config/template.env \
  docker/docker-compose.yaml \
  justfile \
  pyproject.toml \
  "src/$KEYWORD" \
  "src/$PYTHON_NAME" \
  tests/unit/test_config.py \
  tests/unit/test_logger.py

git rm --force --quiet --ignore-unmatch rename.sh

echo "Renamed project to $PROJECT_NAME"
echo "Python package: $PYTHON_NAME"

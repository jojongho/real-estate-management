#!/usr/bin/env bash
set -euo pipefail

# Export each project directory as an independent git repository.
# Optionally add remote origin and push.
#
# Usage:
#   ./tools/split_projects_to_repos.sh --target ~/dev/split-repos
#   ./tools/split_projects_to_repos.sh --target ~/dev/split-repos --remote-base https://github.com/<owner>
#   ./tools/split_projects_to_repos.sh --target ~/dev/split-repos --remote-base git@github.com:<owner> --push

TARGET_DIR=""
REMOTE_BASE=""
DO_PUSH="false"
DEFAULT_BRANCH="main"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --remote-base)
      REMOTE_BASE="$2"
      shift 2
      ;;
    --push)
      DO_PUSH="true"
      shift
      ;;
    --branch)
      DEFAULT_BRANCH="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  echo "--target is required"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$TARGET_DIR"

PROJECTS=(
  "property-management-core"
  "building-ledger-automation"
  "apartment-notice-normalization"
  "legacy-archive"
)

for project in "${PROJECTS[@]}"; do
  src="$ROOT_DIR/projects/$project"
  dst="$TARGET_DIR/$project"

  if [[ ! -d "$src" ]]; then
    echo "Skip: $src not found"
    continue
  fi

  echo "\n=== Exporting $project ==="
  rm -rf "$dst"
  mkdir -p "$dst"

  rsync -av \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude 'venv/' \
    --exclude 'node_modules' \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude 'data/cache/*.sqlite3' \
    "$src/" "$dst/"

  (
    cd "$dst"
    git init -b "$DEFAULT_BRANCH" >/dev/null
    git add .
    git commit -m "chore: bootstrap split repository from monorepo" >/dev/null

    repo_name="$project"
    if [[ -n "$REMOTE_BASE" ]]; then
      remote_url=""
      if [[ "$REMOTE_BASE" == git@* ]]; then
        remote_url="$REMOTE_BASE/$repo_name.git"
      else
        remote_url="$REMOTE_BASE/$repo_name.git"
      fi
      git remote add origin "$remote_url"
      echo "Added remote origin: $remote_url"

      if [[ "$DO_PUSH" == "true" ]]; then
        git push -u origin "$DEFAULT_BRANCH"
      fi
    fi
  )

done

echo "\nDone. Exported repos at: $TARGET_DIR"

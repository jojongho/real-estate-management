#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <target-directory>"
  echo "Example: $0 ~/dev/building-ledger-automation"
  exit 1
fi

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$1"

mkdir -p "$TARGET_DIR"

rsync -av \
  --exclude '.venv' \
  --exclude '.env' \
  --exclude 'data/cache/*.sqlite3' \
  --exclude '__pycache__' \
  "$SRC_DIR/" "$TARGET_DIR/"

cd "$TARGET_DIR"
if [ ! -d .git ]; then
  git init
fi

echo "Standalone project exported to: $TARGET_DIR"
echo "Next steps:"
echo "  cd $TARGET_DIR"
echo "  cp .env.example .env"
echo "  make run"

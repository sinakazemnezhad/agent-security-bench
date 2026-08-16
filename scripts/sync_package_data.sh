#!/usr/bin/env bash
# Sync repo-root data into the wheel package tree.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/src/agent_security_bench/data"
mkdir -p "$DEST"
rsync -a --delete "$ROOT/tasks/" "$DEST/tasks/"
rsync -a --delete "$ROOT/security/" "$DEST/security/"
rsync -a --delete "$ROOT/schema/" "$DEST/schema/"
rsync -a --delete "$ROOT/examples/" "$DEST/examples/"
echo "synced -> $DEST"

#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

source .venv/bin/activate

python -m src \
    --file "$SCRIPT_DIR/clubs.tsv" \
    --count 20 \
    --delay 2 \
    --no-discord \
    -a close \
    --no-interactive \
    --env-file "$SCRIPT_DIR/.env" \
    >> "$SCRIPT_DIR/cron.log" 2>&1

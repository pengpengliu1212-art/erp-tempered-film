#!/usr/bin/env bash
# Stop ERP 钢化膜 server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/server.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo "[stop-erp] No server.pid found. Server not running?"
    exit 0
fi

PID="$(cat "$PID_FILE")"
if [[ "$PID" -gt 0 ]] && kill -0 "$PID" 2>/dev/null; then
    echo "[stop-erp] Stopping PID $PID..."
    kill "$PID" 2>/dev/null || true
    sleep 1
fi
rm -f "$PID_FILE"
echo "[stop-erp] Stopped"

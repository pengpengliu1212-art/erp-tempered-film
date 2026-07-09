#!/usr/bin/env bash
# ========================================
# ERP 钢化膜 startup script (macOS / Linux)
# Per lobsterai-team dashboard pattern: idempotent + graceful shutdown
# ========================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
PORT="${ERP_PORT:-8000}"
HOST="${ERP_HOST:-127.0.0.1}"
LOG_FILE="$PROJECT_ROOT/server.log"
PID_FILE="$PROJECT_ROOT/server.pid"

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    OLD_PID="$(cat "$PID_FILE")"
    if [[ "$OLD_PID" -gt 0 ]] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[start-erp] Already running with PID $OLD_PID"
        echo "  URL: http://$HOST:$PORT/"
        echo "  Stop: ./stop-erp.sh"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# Pick Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[start-erp] Python not found in PATH" >&2
    exit 1
fi

echo "[start-erp] Starting ERP 钢化膜 server..."
echo "  Project: $PROJECT_ROOT"
echo "  URL: http://$HOST:$PORT/"

# Launch in background, write pid
cd "$PROJECT_ROOT"
nohup "$PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --log-level info > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

# Verify
sleep 2
if kill -0 "$PID" 2>/dev/null; then
    echo "  Started: PID $PID"
    echo ""
    echo "  打开浏览器: http://$HOST:$PORT/"
    echo "  Swagger UI: http://$HOST:$PORT/docs"
    echo ""
    echo "  Log: $LOG_FILE"
    echo "  Stop: ./stop-erp.sh"
else
    echo "  FAILED to start. Check log:"
    cat "$LOG_FILE" | tail -20
    exit 1
fi

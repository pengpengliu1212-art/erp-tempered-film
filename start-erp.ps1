# ========================================
# ERP 钢化膜 startup script (Windows PowerShell)
# Per lobsterai-team dashboard pattern: idempotent + graceful shutdown
# Usage: .\start-erp.ps1
# ========================================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$PORT = if ($env:ERP_PORT) { [int]$env:ERP_PORT } else { 8000 }
$BIND_HOST = if ($env:ERP_HOST) { $env:ERP_HOST } else { "127.0.0.1" }
$LOG_FILE = Join-Path $PROJECT_ROOT "server.log"
$ERR_FILE = Join-Path $PROJECT_ROOT "server.err"
$PID_FILE = Join-Path $PROJECT_ROOT "server.pid"

# Check if already running
if (Test-Path $PID_FILE) {
    $oldPid = [int](Get-Content $PID_FILE -Raw -ErrorAction SilentlyContinue)
    if ($oldPid -gt 0) {
        $proc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "[start-erp] Already running with PID $oldPid"
            Write-Host "  URL: http://$($BIND_HOST):$PORT/"
            Write-Host "  Stop: .\stop-erp.ps1"
            exit 0
        }
    }
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
}

# Pick Python
$python = $null
foreach ($c in @("python3", "python", "py")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) {
    Write-Error "[start-erp] Python not found in PATH"
    exit 1
}

Write-Host "[start-erp] Starting ERP 钢化膜 server..."
Write-Host "  Project: $PROJECT_ROOT"
Write-Host "  Python: $python"
Write-Host "  URL: http://$($BIND_HOST):$PORT/"

# Launch uvicorn in background
$args = @(
    "-m", "uvicorn",
    "app.main:app",
    "--host", $BIND_HOST,
    "--port", "$PORT",
    "--log-level", "info"
)
$proc = Start-Process -FilePath $python -ArgumentList $args `
    -WorkingDirectory $PROJECT_ROOT `
    -RedirectStandardOutput $LOG_FILE `
    -RedirectStandardError $ERR_FILE `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 2

# Write pid
$proc.Id | Out-File $PID_FILE -Encoding ascii

# Verify
$running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "  Started: PID $($proc.Id)"
    Write-Host ""
    Write-Host "  Open browser: http://$($BIND_HOST):$PORT/"
    Write-Host "  Swagger UI: http://$($BIND_HOST):$PORT/docs"
    Write-Host ""
    Write-Host "  Log: $LOG_FILE"
    Write-Host "  Stop: .\stop-erp.ps1"
} else {
    Write-Host "  FAILED to start. Check log:"
    if (Test-Path $ERR_FILE) { Get-Content $ERR_FILE -Tail 20 }
    exit 1
}

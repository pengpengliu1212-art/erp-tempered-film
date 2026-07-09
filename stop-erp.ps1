# Stop ERP 钢化膜 server
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$PID_FILE = Join-Path $PROJECT_ROOT "server.pid"

if (-not (Test-Path $PID_FILE)) {
    Write-Host "[stop-erp] No server.pid found. Server not running?"
    exit 0
}

$pid = [int](Get-Content $PID_FILE -Raw -ErrorAction SilentlyContinue)
if ($pid -le 0) {
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    Write-Host "[stop-erp] Stale pid file removed"
    exit 0
}

$proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[stop-erp] Stopping PID $pid..."
    Stop-Process -Id $pid -Force
    Start-Sleep -Seconds 1
}
Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
Write-Host "[stop-erp] Stopped"

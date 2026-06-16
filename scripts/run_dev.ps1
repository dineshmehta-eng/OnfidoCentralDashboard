<#
.SYNOPSIS
    Launch the Onfido Dashboard in local mock mode with hot-reload.
.DESCRIPTION
    Sets MOCK_DB=true so no SQL Server is needed, then starts Uvicorn
    with --reload for live code changes. Opens the dashboard in the
    default browser after a short startup delay.
.NOTES
    Run from the project root (same folder as .env).
#>
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$env:MOCK_DB = "true"
$projectRoot = (Get-Item $PSScriptRoot).Parent.FullName

Write-Host "Starting Onfido Dashboard in MOCK mode..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:8000/"
Write-Host "API docs (Swagger UI) at: http://localhost:8000/docs"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

# Start uvicorn in the background so we can wait and open the browser
$job = Start-Job -ScriptBlock {
    param($projectRoot)
    Set-Location $projectRoot
    & python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $projectRoot

# Wait for server to be ready
$ready = $false
$attempts = 0
while (-not $ready -and $attempts -lt 20) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
        if ($r.success -eq $true) {
            $ready = $true
        }
    } catch {}
    $attempts++
}

if ($ready) {
    Write-Host "Server is ready. Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost:8000/"
} else {
    Write-Host "Server did not start within 20 seconds. Check logs below:" -ForegroundColor Red
}

# Stream job output to console in real time
while ($job.State -eq "Running") {
    $output = Receive-Job -Job $job
    if ($output) {
        $output | ForEach-Object { Write-Host $_ }
    }
    Start-Sleep -Seconds 0.5
}

# Print any remaining output
$output = Receive-Job -Job $job
if ($output) {
    $output | ForEach-Object { Write-Host $_ }
}

Remove-Job -Job $job -Force
Write-Host "Server stopped." -ForegroundColor Yellow

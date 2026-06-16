<#
.SYNOPSIS
    Installs the Onfido Dashboard API as a Windows service using NSSM.
.DESCRIPTION
    Assumes NSSM is already on the system PATH.
    Adjust $ProjectRoot, $PythonPath, and $ServiceName as needed.
.NOTES
    Run as Administrator.
#>
$ErrorActionPreference = "Stop"

$ServiceName = "OnfidoDashboardAPI"
$DisplayName = "Onfido SQL Dashboard API"
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$PythonPath = "python"

$AppRun = "$PythonPath"
$AppArgs = "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

Write-Host "Checking NSSM availability..."
$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssm) {
    Write-Error "nssm.exe not found in PATH. Download from https://nssm.cc and add to PATH."
    exit 1
}

Write-Host "Stopping existing service if present..."
nssm stop $ServiceName 2>$null
Start-Sleep -Seconds 2

Write-Host "Removing existing service if present..."
nssm remove $ServiceName confirm 2>$null

Write-Host "Installing service..."
nssm install $ServiceName $AppRun
nssm set $ServiceName AppDirectory $ProjectRoot
nssm set $ServiceName AppParameters $AppArgs
nssm set $ServiceName DisplayName $DisplayName
nssm set $ServiceName Start SERVICE_AUTO_START
nssm set $ServiceName ObjectName LocalSystem
nssm set $ServiceName AppStdout "$ProjectRoot\logs\service_stdout.log"
nssm set $ServiceName AppStderr "$ProjectRoot\logs\service_stderr.log"
nssm set $ServiceName AppRotateFiles 1
nssm set $ServiceName AppRotateOnline 0
nssm set $ServiceName AppRotateBytes 10485760

Write-Host "Starting service..."
nssm start $ServiceName

Write-Host "Done. Verify at http://localhost:8000/api/health"

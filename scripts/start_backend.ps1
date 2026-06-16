$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$env:PYTHONUNBUFFERED = "1"
$ErrorActionPreference = "Continue"
& $Python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 `
    >> (Join-Path $LogDir "backend_autostart.out.log") `
    2>> (Join-Path $LogDir "backend_autostart.err.log")

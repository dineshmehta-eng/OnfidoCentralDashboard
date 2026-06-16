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
& $Python etl\onfido_multi_gsheet_to_sqlserver_hourly.py `
    >> (Join-Path $LogDir "etl_hourly.out.log") `
    2>> (Join-Path $LogDir "etl_hourly.err.log")

exit $LASTEXITCODE

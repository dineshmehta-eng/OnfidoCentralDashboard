$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "start_backend.ps1"
$TaskName = "OnfidoCentralDashboardBackend"
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$StartScript`"" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Settings $Settings `
    -Description "Starts the Onfido Central Dashboard FastAPI backend on Windows logon." `
    -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName
Write-Host "Registered and started task: $TaskName"
Write-Host "Backend URL: http://127.0.0.1:8000/?v=20260614_all_pages_fix_final"

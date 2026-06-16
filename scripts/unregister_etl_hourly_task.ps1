$ErrorActionPreference = "SilentlyContinue"

$TaskName = "OnfidoCentralDashboardETLHourly"
Stop-ScheduledTask -TaskName $TaskName
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Removed task: $TaskName"

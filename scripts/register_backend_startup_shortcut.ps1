$ErrorActionPreference = "Stop"

$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "Onfido Central Dashboard Backend.lnk"
$StartScript = Join-Path $PSScriptRoot "start_backend.ps1"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`""
$Shortcut.WorkingDirectory = Split-Path -Parent $PSScriptRoot
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Starts the Onfido Central Dashboard backend."
$Shortcut.Save()

Write-Host "Created startup shortcut: $ShortcutPath"

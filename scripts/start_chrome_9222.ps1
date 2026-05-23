param(
  [int]$Port = 9222,
  [string]$ProfileDir = "$Env:USERPROFILE\.hermes\chrome-cdp-profile",
  [switch]$KillExisting = $true
)

$ErrorActionPreference = 'Stop'

function Find-ChromePath {
  $candidates = @(
    "$Env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${Env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$Env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  ) | Where-Object { $_ -and (Test-Path $_) }

  if ($candidates.Count -gt 0) { return $candidates[0] }
  throw "chrome.exe not found in common install paths"
}

if ($KillExisting) {
  Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 2
}

New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
$chrome = Find-ChromePath

$args = @(
  "--remote-debugging-port=$Port",
  "--user-data-dir=$ProfileDir",
  "--remote-allow-origins=*",
  "--no-first-run",
  "--no-default-browser-check",
  "https://tcm2.dayuan1997.com/"
)

Start-Process -FilePath $chrome -ArgumentList $args | Out-Null
Start-Sleep -Seconds 4

try {
  $json = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/json" -UseBasicParsing -TimeoutSec 5
  Write-Host "Chrome CDP is ready on port $Port"
  Write-Host "Profile: $ProfileDir"
  Write-Host "Targets bytes: $($json.Content.Length)"
} catch {
  Write-Error "Chrome started but CDP check failed on port $Port: $($_.Exception.Message)"
  exit 1
}

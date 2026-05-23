param(
  [int]$Port = 9222
)

$ErrorActionPreference = 'Continue'

Write-Host "=== 9222 listeners ==="
try {
  $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
  if (-not $listeners) {
    Write-Host "No listener on port $Port"
  } else {
    foreach ($l in $listeners) {
      $p = Get-CimInstance Win32_Process -Filter "ProcessId = $($l.OwningProcess)"
      [PSCustomObject]@{
        Port = $Port
        PID = $l.OwningProcess
        Name = $p.Name
        CommandLine = $p.CommandLine
      } | Format-List
    }
  }
} catch {
  Write-Host "Unable to query listeners: $($_.Exception.Message)"
}

Write-Host "\n=== related processes ==="
$kw = 'tcm2|battle-record|run-monitor|openclaw|qclaw|hermes|9222|chrome|python|node'
$procs = Get-CimInstance Win32_Process | Where-Object {
  ($_.Name -match 'chrome|python|node') -or ($_.CommandLine -match $kw)
}

if (-not $procs) {
  Write-Host "No related processes found"
} else {
  $procs |
    Select-Object ProcessId, ParentProcessId, Name, CommandLine |
    Sort-Object Name, ProcessId |
    Format-List
}

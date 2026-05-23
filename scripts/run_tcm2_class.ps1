param(
  [Parameter(Mandatory = $false)][string]$ClassName,
  [string]$ClassId,
  [int]$Total = 0,
  [string]$OutFile = "",
  [switch]$SkipConflictCheck,
  [switch]$SkipChromeStart
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $PSScriptRoot 'tcm2_portable_extract.py'

$map = @{
  'QV848' = @{ class_id = '60018'; total = 26 }
  'JJ014' = @{ class_id = '60024'; total = 21 }
  'VD241' = @{ class_id = '60056'; total = 26 }
  'RB881' = @{ class_id = '120003'; total = 20 }
  'RL526' = @{ class_id = '180020'; total = 25 }
}

if (-not $ClassName -and -not $ClassId) {
  throw 'Provide -ClassName or -ClassId'
}

if ($ClassName -and $map.ContainsKey($ClassName)) {
  if (-not $ClassId) { $ClassId = $map[$ClassName].class_id }
  if (-not $Total) { $Total = $map[$ClassName].total }
}

if (-not $ClassName) {
  $ClassName = "CLASS_$ClassId"
}

if (-not $SkipConflictCheck) {
  & (Join-Path $PSScriptRoot 'check_tcm2_conflict.ps1')
}

if (-not $SkipChromeStart) {
  & (Join-Path $PSScriptRoot 'start_chrome_9222.ps1')
}

$python = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
$args = @($py, '--class-id', $ClassId, '--class-name', $ClassName)
if ($Total -gt 0) { $args += @('--total', "$Total") }

if ($OutFile) {
  & $python @args | Tee-Object -FilePath $OutFile
} else {
  & $python @args
}

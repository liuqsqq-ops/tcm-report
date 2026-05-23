param(
  [string]$OutputDir = (Join-Path (Get-Location) 'reports'),
  [switch]$SkipConflictCheck,
  [switch]$SkipChromeStart
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$classes = @(
  @{ name = 'QV848'; id = '60018'; total = 26 },
  @{ name = 'JJ014'; id = '60024'; total = 21 },
  @{ name = 'VD241'; id = '60056'; total = 26 },
  @{ name = 'RB881'; id = '120003'; total = 20 },
  @{ name = 'RL526'; id = '180020'; total = 25 }
)

$runner = Join-Path $PSScriptRoot 'run_tcm2_class.ps1'
$first = $true

foreach ($c in $classes) {
  $out = Join-Path $OutputDir ($c.name + '.md')
  Write-Host "=== $($c.name) -> $out ==="
  $args = @(
    '-ExecutionPolicy', 'Bypass',
    '-File', $runner,
    '-ClassName', $c.name,
    '-ClassId', $c.id,
    '-Total', "$($c.total)",
    '-OutFile', $out
  )
  if ($SkipChromeStart -or -not $first) { $args += '-SkipChromeStart' }
  if ($SkipConflictCheck -or -not $first) { $args += '-SkipConflictCheck' }
  powershell @args
  $first = $false
}

Write-Host "Done. Reports saved to $OutputDir"

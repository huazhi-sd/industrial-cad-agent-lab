param(
  [Parameter(Mandatory = $true)]
  [string] $InputModel,

  [ValidateSet("inspect", "sensor", "solve", "all")]
  [string] $Mode = "sensor",

  [string] $ComsolRoot = "",

  [string] $DatasetTag = "dset4",

  [string] $DtDeg = "45",

  [string] $OutputDir = "",

  [string] $RunId = "",

  [switch] $DryRun
)

$ErrorActionPreference = "Stop"

$CaseRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $CaseRoot "..\..\..")
$Tool = Join-Path $RepoRoot "tools\comsol-baseline\comsol_baseline_tool.ps1"

if (-not (Test-Path -LiteralPath $Tool)) {
  throw "Missing COMSOL baseline tool: $Tool"
}

if (-not $OutputDir) {
  $OutputDir = Join-Path $CaseRoot "runs"
}

$argsForTool = @(
  "-InputModel", $InputModel,
  "-Mode", $Mode,
  "-DatasetTag", $DatasetTag,
  "-DtDeg", $DtDeg,
  "-OutputDir", $OutputDir
)

if ($ComsolRoot) {
  $argsForTool += @("-ComsolRoot", $ComsolRoot)
}

if ($RunId) {
  $argsForTool += @("-RunId", $RunId)
}

if ($DryRun) {
  $argsForTool += "-DryRun"
}

& powershell -NoProfile -ExecutionPolicy Bypass -File $Tool @argsForTool

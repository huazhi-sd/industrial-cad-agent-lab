param(
  [Parameter(Mandatory = $true)]
  [string] $InputModel,

  [ValidateSet("inspect", "sensor", "sensor-config", "solve", "solve-config", "all")]
  [string] $Mode = "sensor-config",

  [string] $ComsolRoot = "",

  [string] $DatasetTag = "dset4",

  [string] $DtDeg = "45",

  [string] $ConfigFile = "",

  [string] $OutputDir = "",

  [string] $RunId = "",

  [switch] $Report,

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

if (-not $ConfigFile) {
  $ConfigFile = Join-Path $CaseRoot "configs\magnetostatic_sensor_eval.properties"
}

$argsForTool = @(
  "-InputModel", $InputModel,
  "-Mode", $Mode,
  "-DatasetTag", $DatasetTag,
  "-DtDeg", $DtDeg,
  "-ConfigFile", $ConfigFile,
  "-OutputDir", $OutputDir
)

if ($ComsolRoot) {
  $argsForTool += @("-ComsolRoot", $ComsolRoot)
}

if ($RunId) {
  $argsForTool += @("-RunId", $RunId)
}

if ($Report) {
  $argsForTool += "-Report"
}

if ($DryRun) {
  $argsForTool += "-DryRun"
}

& powershell -NoProfile -ExecutionPolicy Bypass -File $Tool @argsForTool

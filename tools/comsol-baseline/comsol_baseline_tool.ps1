param(
  [Parameter(Mandatory = $true)]
  [string] $InputModel,

  [ValidateSet("inspect", "sensor", "sensor-config", "solve", "solve-config", "all")]
  [string] $Mode = "inspect",

  [string] $ComsolRoot = "",

  [string] $DatasetTag = "dset4",

  [string] $DtDeg = "45",

  [string] $ConfigFile = "",

  [string] $OutputDir = "",

  [string] $RunId = "",

  [switch] $DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-ComsolRoot {
  param([string] $Root)

  if ($Root) {
    return $Root
  }

  if ($env:COMSOL_ROOT) {
    return $env:COMSOL_ROOT
  }

  $candidates = @(
    "C:\Program Files\COMSOL\COMSOL63\Multiphysics",
    "D:\COMSOL\COMSOL63\Multiphysics"
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath (Join-Path $candidate "bin\win64\comsolbatch.exe")) {
      return $candidate
    }
  }

  if ($DryRun) {
    return "<COMSOL_ROOT>"
  }

  throw "COMSOL root was not provided and could not be auto-detected. Pass -ComsolRoot or set COMSOL_ROOT."
}

function Get-ModeSpec {
  param([string] $RunMode)

  switch ($RunMode) {
    "inspect" {
      return @{
        className = "ComsolBaselineInspector"
        javaArgs = @($InputModel, "-")
        csvBegin = ""
        csvEnd = ""
        csvName = ""
      }
    }
    "sensor" {
      return @{
        className = "ComsolBaselineSensorEval"
        javaArgs = @($InputModel, $DatasetTag)
        csvBegin = "SENSOR_EVAL_CSV_BEGIN"
        csvEnd = "SENSOR_EVAL_CSV_END"
        csvName = "sensor_eval.csv"
      }
    }
    "sensor-config" {
      $configArgs = Get-ConfiguredSensorArgs $ConfigFile
      return @{
        className = "ComsolConfiguredSensorEval"
        javaArgs = @($InputModel) + $configArgs
        csvBegin = "CONFIG_SENSOR_EVAL_CSV_BEGIN"
        csvEnd = "CONFIG_SENSOR_EVAL_CSV_END"
        csvName = "configured_sensor_eval.csv"
      }
    }
    "solve" {
      $safeDt = ($DtDeg -replace '[^0-9A-Za-z_.-]', '_')
      return @{
        className = "ComsolBaselineSingleSolve"
        javaArgs = @($InputModel, $DtDeg)
        csvBegin = "SINGLE_SOLVE_CSV_BEGIN"
        csvEnd = "SINGLE_SOLVE_CSV_END"
        csvName = "single_solve_dt_$safeDt.csv"
      }
    }
    "solve-config" {
      $solveArgs = Get-ConfiguredSolveArgs $ConfigFile $DtDeg
      $safeValue = ($solveArgs[3] -replace '[^0-9A-Za-z_.-]', '_')
      return @{
        className = "ComsolConfiguredSingleSolve"
        javaArgs = @($InputModel) + $solveArgs
        csvBegin = "CONFIG_SINGLE_SOLVE_CSV_BEGIN"
        csvEnd = "CONFIG_SINGLE_SOLVE_CSV_END"
        csvName = "configured_single_solve_$safeValue.csv"
      }
    }
  }
}

function Read-SimpleProperties {
  param([string] $Path)

  $props = @{}
  foreach ($line in Get-Content -LiteralPath $Path) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) {
      continue
    }
    $idx = $trimmed.IndexOf("=")
    if ($idx -lt 1) {
      continue
    }
    $key = $trimmed.Substring(0, $idx).Trim()
    $value = $trimmed.Substring($idx + 1).Trim()
    $props[$key] = $value
  }
  return $props
}

function Get-ConfiguredSensorArgs {
  param([string] $Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Config file does not exist: $Path"
  }

  $props = Read-SimpleProperties $Path
  $configDir = Split-Path -Parent $Path
  $sensorFile = $props["sensor_file"]
  if (-not $sensorFile) {
    $sensorFile = "sensor_points.csv"
  }
  if (-not [System.IO.Path]::IsPathRooted($sensorFile)) {
    $sensorFile = Join-Path $configDir $sensorFile
  }
  if (-not (Test-Path -LiteralPath $sensorFile)) {
    throw "Sensor file does not exist: $sensorFile"
  }

  $sensorRows = New-Object System.Collections.Generic.List[string]
  foreach ($line in Get-Content -LiteralPath $sensorFile) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) {
      continue
    }
    if ($trimmed.ToLowerInvariant().StartsWith("name,")) {
      continue
    }
    $cells = $trimmed.Split(",")
    if ($cells.Length -lt 4) {
      throw "Invalid sensor row: $trimmed"
    }
    $sensorRows.Add(("{0}|{1}|{2}|{3}" -f $cells[0].Trim(), $cells[1].Trim(), $cells[2].Trim(), $cells[3].Trim()))
  }
  if ($sensorRows.Count -eq 0) {
    throw "Sensor file has no sensor points: $sensorFile"
  }

  $dataset = if ($props["dataset"]) { $props["dataset"] } else { "dset4" }
  $exprs = if ($props["exprs"]) { $props["exprs"] } else { "mf.Bx,mf.By,mf.Bz,mf.normB" }
  $units = if ($props["units"]) { $props["units"] } else { "G,G,G,G" }
  $solutionIndices = if ($props["solution_indices"]) { $props["solution_indices"] } else { "1,10,19" }
  $phaseStart = if ($props["phase_start"]) { $props["phase_start"] } else { "0" }
  $phaseStep = if ($props["phase_step"]) { $props["phase_step"] } else { "10" }
  $phaseColumn = if ($props["phase_column"]) { $props["phase_column"] } else { "dt_deg" }
  $csvHeader = if ($props["csv_header"]) { $props["csv_header"] } else { "" }
  $sensorsInline = [string]::Join(";", $sensorRows)

  return @(
    $dataset,
    $exprs,
    $units,
    $solutionIndices,
    $phaseStart,
    $phaseStep,
    $phaseColumn,
    $csvHeader,
    $sensorsInline
  )
}

function Get-ConfiguredSolveArgs {
  param(
    [string] $Path,
    [string] $ParamOverride
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Config file does not exist: $Path"
  }

  $props = Read-SimpleProperties $Path
  $configDir = Split-Path -Parent $Path
  $sensorFile = $props["sensor_file"]
  if (-not $sensorFile) {
    $sensorFile = "sensor_points.csv"
  }
  if (-not [System.IO.Path]::IsPathRooted($sensorFile)) {
    $sensorFile = Join-Path $configDir $sensorFile
  }
  if (-not (Test-Path -LiteralPath $sensorFile)) {
    throw "Sensor file does not exist: $sensorFile"
  }

  $sensorRows = New-Object System.Collections.Generic.List[string]
  foreach ($line in Get-Content -LiteralPath $sensorFile) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) {
      continue
    }
    if ($trimmed.ToLowerInvariant().StartsWith("name,")) {
      continue
    }
    $cells = $trimmed.Split(",")
    if ($cells.Length -lt 4) {
      throw "Invalid sensor row: $trimmed"
    }
    $sensorRows.Add(("{0}|{1}|{2}|{3}" -f $cells[0].Trim(), $cells[1].Trim(), $cells[2].Trim(), $cells[3].Trim()))
  }
  if ($sensorRows.Count -eq 0) {
    throw "Sensor file has no sensor points: $sensorFile"
  }

  $studyTag = if ($props["study_tag"]) { $props["study_tag"] } else { "std1" }
  $paramFeatureTag = if ($props["param_feature_tag"]) { $props["param_feature_tag"] } else { "param" }
  $paramName = if ($props["solve_param_name"]) { $props["solve_param_name"] } else { "dt" }
  $paramValue = if ($props["solve_param_value"]) { $props["solve_param_value"] } else { "45" }
  if ($ParamOverride) {
    $paramValue = $ParamOverride
  }
  $paramUnit = if ($props["solve_param_unit"]) { $props["solve_param_unit"] } else { "" }
  if (-not $paramUnit) {
    $paramUnit = "__EMPTY__"
  }
  $resultDataset = "dset4"
  if ($props["dataset"]) {
    $resultDataset = $props["dataset"]
  }
  if ($props["solve_dataset"]) {
    $resultDataset = $props["solve_dataset"]
  }
  $exprs = if ($props["exprs"]) { $props["exprs"] } else { "mf.Bx,mf.By,mf.Bz,mf.normB" }
  $units = if ($props["units"]) { $props["units"] } else { "G,G,G,G" }
  $phaseColumn = if ($props["phase_column"]) { $props["phase_column"] } else { "dt_deg" }
  $csvHeader = if ($props["csv_header"]) { $props["csv_header"] } else { "sensor,$phaseColumn" }
  $sensorsInline = [string]::Join(";", $sensorRows)
  $modelName = if ($props["solve_model_name"]) { $props["solve_model_name"] } else { "ConfiguredSingleSolve" }

  return @(
    $studyTag,
    $paramFeatureTag,
    $paramName,
    $paramValue,
    $paramUnit,
    $resultDataset,
    $exprs,
    $units,
    $phaseColumn,
    $csvHeader,
    $sensorsInline,
    $modelName
  )
}

function Export-MarkedBlock {
  param(
    [string] $InputFile,
    [string] $BeginMarker,
    [string] $EndMarker,
    [string] $OutputFile
  )

  if (-not $BeginMarker -or -not $EndMarker) {
    return $false
  }

  $inside = $false
  $lines = New-Object System.Collections.Generic.List[string]
  foreach ($line in Get-Content -LiteralPath $InputFile) {
    if ($line -eq $BeginMarker) {
      $inside = $true
      continue
    }
    if ($line -eq $EndMarker) {
      $inside = $false
      break
    }
    if ($inside) {
      $lines.Add($line)
    }
  }

  if ($lines.Count -eq 0) {
    return $false
  }

  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllLines($OutputFile, $lines, $utf8NoBom)
  return $true
}

function Invoke-ComsolMode {
  param(
    [string] $RunMode,
    [string] $ComsolRootResolved,
    [string] $RunDir,
    [string] $ScriptDir
  )

  $spec = Get-ModeSpec $RunMode
  $className = $spec.className
  $sourceJava = Join-Path $ScriptDir "$className.java"

  if (-not (Test-Path -LiteralPath $sourceJava)) {
    throw "Missing Java baseline script: $sourceJava"
  }

  $modeDir = Join-Path $RunDir $RunMode
  $buildDir = Join-Path $modeDir "build"
  New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

  $workJava = Join-Path $buildDir "$className.java"
  $classFile = Join-Path $buildDir "$className.class"
  $classStatusFile = Join-Path $buildDir "$className.class.status"
  $stdoutFile = Join-Path $modeDir "$RunMode.stdout.txt"
  $batchLog = Join-Path $modeDir "$RunMode.batch.log"
  $compileLog = Join-Path $modeDir "$RunMode.compile.stdout.txt"
  $csvFile = ""

  Copy-Item -LiteralPath $sourceJava -Destination $workJava -Force
  Remove-Item -LiteralPath $classFile, $classStatusFile, $stdoutFile, $batchLog, $compileLog -ErrorAction SilentlyContinue

  $compileExe = Join-Path $ComsolRootResolved "bin\win64\comsolcompile.exe"
  $batchExe = Join-Path $ComsolRootResolved "bin\win64\comsolbatch.exe"

  if ($DryRun) {
    return [ordered]@{
      mode = $RunMode
      status = "dry-run"
      class = $className
      build_dir = $buildDir
      stdout = $stdoutFile
      batch_log = $batchLog
      csv = $csvFile
    }
  }

  Push-Location $buildDir
  try {
    & $compileExe $workJava *> $compileLog
    $compileExit = $LASTEXITCODE
  } finally {
    Pop-Location
  }

  if ($compileExit -ne 0 -or -not (Test-Path -LiteralPath $classFile)) {
    throw "COMSOL compile failed for $className. See $compileLog"
  }

  Push-Location $buildDir
  try {
    & $batchExe -batchlog $batchLog -inputfile $classFile @($spec.javaArgs) *> $stdoutFile
    $batchExit = $LASTEXITCODE
  } finally {
    Pop-Location
  }

  if ($batchExit -ne 0) {
    throw "COMSOL batch failed for mode '$RunMode' with exit code $batchExit. See $stdoutFile and $batchLog"
  }

  if (Test-Path -LiteralPath $classStatusFile) {
    $classStatus = (Get-Content -LiteralPath $classStatusFile -Raw).Trim()
    if ($classStatus -match "Error") {
      throw "COMSOL Java class reported Error for mode '$RunMode'. See $batchLog"
    }
  }

  $csvExtracted = $false
  if ($spec.csvName) {
    $csvFile = Join-Path $modeDir $spec.csvName
    $csvExtracted = Export-MarkedBlock `
      -InputFile $stdoutFile `
      -BeginMarker $spec.csvBegin `
      -EndMarker $spec.csvEnd `
      -OutputFile $csvFile
    if (-not $csvExtracted) {
      throw "Expected CSV block was not found for mode '$RunMode'. See $stdoutFile"
    }
  }

  $status = "unknown"
  $statusLine = Select-String -LiteralPath $stdoutFile -Pattern "status=success|status=failed" | Select-Object -Last 1
  if ($statusLine) {
    if ($statusLine.Line -match "success") {
      $status = "success"
    } elseif ($statusLine.Line -match "failed") {
      $status = "failed"
    }
  } elseif ($RunMode -eq "inspect") {
    $status = "success"
  }

  return [ordered]@{
    mode = $RunMode
    status = $status
    class = $className
    stdout = $stdoutFile
    batch_log = $batchLog
    compile_log = $compileLog
    csv = $csvFile
    csv_extracted = $csvExtracted
  }
}

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptDir = Join-Path $ToolRoot "scripts"

if (-not $ConfigFile) {
  $ConfigFile = Join-Path $ToolRoot "configs\magnetostatic_sensor_eval.properties"
}

if (-not [System.IO.Path]::IsPathRooted($ConfigFile)) {
  $ConfigFile = Join-Path (Get-Location) $ConfigFile
}

if (-not $DryRun -and -not (Test-Path -LiteralPath $InputModel)) {
  throw "Input model does not exist: $InputModel"
}

if (($Mode -eq "sensor-config" -or $Mode -eq "solve-config" -or $Mode -eq "all") -and -not (Test-Path -LiteralPath $ConfigFile)) {
  throw "Config file does not exist: $ConfigFile"
}

$ComsolRootResolved = Resolve-ComsolRoot $ComsolRoot
$compilePath = Join-Path $ComsolRootResolved "bin\win64\comsolcompile.exe"
$batchPath = Join-Path $ComsolRootResolved "bin\win64\comsolbatch.exe"

if (-not $DryRun) {
  if (-not (Test-Path -LiteralPath $compilePath)) {
    throw "Missing comsolcompile.exe: $compilePath"
  }
  if (-not (Test-Path -LiteralPath $batchPath)) {
    throw "Missing comsolbatch.exe: $batchPath"
  }
}

if (-not $OutputDir) {
  $OutputDir = Join-Path $ToolRoot "runs"
}
if (-not $RunId) {
  $RunId = Get-Date -Format "yyyyMMddTHHmmss"
}

$RunDir = Join-Path $OutputDir $RunId
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$modes = @($Mode)
if ($Mode -eq "all") {
  $modes = @("inspect", "sensor-config", "solve-config")
}

$results = New-Object System.Collections.Generic.List[object]
foreach ($runMode in $modes) {
  $results.Add((Invoke-ComsolMode `
    -RunMode $runMode `
    -ComsolRootResolved $ComsolRootResolved `
    -RunDir $RunDir `
    -ScriptDir $ScriptDir))
}

$manifest = [ordered]@{
  command = "comsol_baseline_tool"
  status = "success"
  mode = $Mode
  run_id = $RunId
  run_dir = $RunDir
  input_model = $InputModel
  comsol_root = $ComsolRootResolved
  dataset_tag = $DatasetTag
  dt_deg = $DtDeg
  config_file = $ConfigFile
  dry_run = [bool]$DryRun
  results = $results
}

$manifestFile = Join-Path $RunDir "manifest.json"
$json = $manifest | ConvertTo-Json -Depth 8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($manifestFile, $json, $utf8NoBom)

Write-Host "COMSOL baseline tool complete."
Write-Host "RunDir:   $RunDir"
Write-Host "Manifest: $manifestFile"
foreach ($item in $results) {
  Write-Host ("- {0}: {1}" -f $item.mode, $item.status)
  if ($item.csv) {
    Write-Host ("  CSV: {0}" -f $item.csv)
  }
}

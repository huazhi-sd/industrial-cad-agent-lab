param(
  [Parameter(Mandatory = $true)]
  [string] $InputModel,

  [ValidateSet("inspect", "sensor", "solve45")]
  [string] $Mode = "inspect",

  [string] $ComsolRoot = "D:\COMSOL\COMSOL63\Multiphysics",

  [string] $DatasetTag = "dset4",

  [string] $DtDeg = "45",

  [string] $OutputDir = ""
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptDir = Join-Path $ToolRoot "scripts"

if (-not $OutputDir) {
  $OutputDir = Join-Path $ToolRoot "runs"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

switch ($Mode) {
  "inspect" {
    $ClassName = "ComsolBaselineInspector"
    $JavaArgs = @($InputModel, "-")
  }
  "sensor" {
    $ClassName = "ComsolBaselineSensorEval"
    $JavaArgs = @($InputModel, $DatasetTag)
  }
  "solve45" {
    $ClassName = "ComsolBaselineSingleSolve"
    $JavaArgs = @($InputModel, $DtDeg)
  }
}

$JavaFile = Join-Path $ScriptDir "$ClassName.java"
$ClassFile = Join-Path $ScriptDir "$ClassName.class"
$BatchLog = Join-Path $OutputDir "$Mode.batch.log"
$StdoutFile = Join-Path $OutputDir "$Mode.stdout.txt"

Remove-Item -LiteralPath $BatchLog, $StdoutFile -ErrorAction SilentlyContinue

Push-Location $ScriptDir
try {
  & (Join-Path $ComsolRoot "bin\win64\comsolcompile.exe") $JavaFile
  $compileExit = $LASTEXITCODE
} finally {
  Pop-Location
}

if ($compileExit -ne 0 -or -not (Test-Path -LiteralPath $ClassFile)) {
  throw "COMSOL compile failed. Check the newest COMSOL compile log."
}

Push-Location $ScriptDir
try {
  & (Join-Path $ComsolRoot "bin\win64\comsolbatch.exe") `
    -batchlog $BatchLog `
    -inputfile $ClassFile `
    @JavaArgs *> $StdoutFile

  if ($LASTEXITCODE -ne 0) {
    throw "COMSOL batch failed with exit code $LASTEXITCODE"
  }
} finally {
  Pop-Location
}

Write-Host "COMSOL baseline mode '$Mode' complete."
Write-Host "Stdout:   $StdoutFile"
Write-Host "BatchLog: $BatchLog"

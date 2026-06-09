# COMSOL Baseline Automation

This folder contains a small COMSOL Java API baseline for agent-driven simulation workflows.

It verifies three minimum capabilities:

1. Load an existing `.mph` model and inspect model structure.
2. Read existing solution data from a dataset without rerunning a study.
3. Modify a study parameter and run one controlled solve.
4. Run configurable sensor evaluation from a small properties file and sensor-point CSV.

The baseline was tested on COMSOL Multiphysics 6.3 with a magnetostatic model. No model file is included in this public repository.

## Files

- `comsol_baseline_tool.ps1`
  Recommended wrapper. It creates an isolated run folder, compiles Java in a temporary build directory, captures stdout and batch logs, extracts CSV blocks, and writes a `manifest.json`.

- `scripts/ComsolBaselineInspector.java`  
  Loads a model and prints parameters, components, geometry features, materials, physics, mesh, studies, datasets, numerical features, and exports.

- `scripts/ComsolBaselineSensorEval.java`  
  Evaluates `mf.Bx`, `mf.By`, `mf.Bz`, and `mf.normB` at four sensor points from an existing dataset.

- `scripts/ComsolConfiguredSensorEval.java`
  Reads dataset tag, expressions, units, solution indices, phase mapping, and sensor coordinates from config files, then exports sensor CSV data from an existing solution.

- `scripts/ComsolBaselineSingleSolve.java`  
  Uses `ModelUtil.loadCopy`, changes the study parameter sweep to a single `dt` value, runs `std1`, and evaluates the same four sensor points.

- `configs/`
  Default public sample config for the configurable magnetostatic sensor extraction workflow.

- `run_comsol_baseline.ps1`  
  Legacy minimal runner. Keep this only as a compact reference.

- `sample-output/`  
  Small CSV outputs from the baseline run.

## Usage

Run from Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode inspect
```

Read existing solution data:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode sensor `
  -DatasetTag dset4
```

Read existing solution data from config files:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode sensor-config `
  -ConfigFile .\configs\magnetostatic_sensor_eval.properties
```

Run a controlled single-parameter solve:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode solve `
  -DtDeg 45
```

Run all three baseline checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode all `
  -DatasetTag dset4 `
  -DtDeg 45
```

If COMSOL is installed somewhere else, pass `-ComsolRoot` or set `COMSOL_ROOT`.

The wrapper writes outputs under `runs/<run-id>/` by default:

- `manifest.json` records the command, input model, COMSOL root, mode list, status, and output paths.
- `<mode>/<mode>.stdout.txt` captures Java stdout.
- `<mode>/<mode>.batch.log` captures COMSOL batch logs.
- `sensor/sensor_eval.csv` is extracted from `SENSOR_EVAL_CSV_BEGIN` / `SENSOR_EVAL_CSV_END`.
- `sensor-config/configured_sensor_eval.csv` is extracted from `CONFIG_SENSOR_EVAL_CSV_BEGIN` / `CONFIG_SENSOR_EVAL_CSV_END`.
- `solve/single_solve_dt_<value>.csv` is extracted from `SINGLE_SOLVE_CSV_BEGIN` / `SINGLE_SOLVE_CSV_END`.

Use `-DryRun` to verify paths and planned outputs without launching COMSOL:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\comsol_baseline_tool.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode all `
  -DryRun
```

## Baseline Notes

- `comsolcompile.exe` may return exit code 0 even when compilation fails, so the runner also checks that the `.class` file exists.
- COMSOL Java security preferences may block direct file writes from a Java class. This baseline writes results to process stdout and lets PowerShell capture them.
- COMSOL Java security preferences may also block direct config-file reads from Java. The configurable sensor workflow reads `.properties` and sensor CSV files in PowerShell, then passes the resolved config values into Java as command-line arguments.
- `comsolbatch.exe` may return exit code 0 even when the Java class fails. The wrapper checks the generated `.class.status` file and fails fast when COMSOL reports `Error`.
- Java classes are compiled inside each run folder instead of beside the source files, so the repository stays clean.
- Windows PowerShell 5.1 can misread UTF-8 scripts containing non-ASCII paths if the file is not saved with UTF-8 BOM. The local scripts used during testing were saved with BOM for that reason.
- The public runner is parameterized and does not include private model paths.

## Tested Workflow

The internal test model used a parametric sweep:

- Parameter: `dt`
- Sweep: `range(0,10,180)`
- Controlled solve: `dt = 45`
- Expressions: `mf.Bx`, `mf.By`, `mf.Bz`, `mf.normB`
- Unit: `G`

The `sensor` mode reproduced the existing final CSV values exactly for sampled `Bx` values at `dt = 0, 90, 180`.

The `solve45` mode completed successfully and produced the sample CSV in `sample-output/single_solve_dt45.csv`.

# COMSOL Baseline Automation

This folder contains a small COMSOL Java API baseline for agent-driven simulation workflows.

It verifies three minimum capabilities:

1. Load an existing `.mph` model and inspect model structure.
2. Read existing solution data from a dataset without rerunning a study.
3. Modify a study parameter and run one controlled solve.

The baseline was tested on COMSOL Multiphysics 6.3 with a magnetostatic model. No model file is included in this public repository.

## Files

- `scripts/ComsolBaselineInspector.java`  
  Loads a model and prints parameters, components, geometry features, materials, physics, mesh, studies, datasets, numerical features, and exports.

- `scripts/ComsolBaselineSensorEval.java`  
  Evaluates `mf.Bx`, `mf.By`, `mf.Bz`, and `mf.normB` at four sensor points from an existing dataset.

- `scripts/ComsolBaselineSingleSolve.java`  
  Uses `ModelUtil.loadCopy`, changes the study parameter sweep to a single `dt` value, runs `std1`, and evaluates the same four sensor points.

- `run_comsol_baseline.ps1`  
  Compiles and runs one of the three Java baselines through `comsolcompile.exe` and `comsolbatch.exe`.

- `sample-output/`  
  Small CSV outputs from the baseline run.

## Usage

Run from Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_comsol_baseline.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode inspect
```

Read existing solution data:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_comsol_baseline.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode sensor `
  -DatasetTag dset4
```

Run a controlled single-parameter solve:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_comsol_baseline.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode solve45 `
  -DtDeg 45
```

If COMSOL is installed somewhere else, pass `-ComsolRoot`.

## Baseline Notes

- `comsolcompile.exe` may return exit code 0 even when compilation fails, so the runner also checks that the `.class` file exists.
- COMSOL Java security preferences may block direct file writes from a Java class. This baseline writes results to process stdout and lets PowerShell capture them.
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

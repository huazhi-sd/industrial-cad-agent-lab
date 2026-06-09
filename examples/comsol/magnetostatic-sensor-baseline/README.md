# Magnetostatic Sensor Automation Baseline

This is a public, sanitized COMSOL automation case for agent-driven simulation workflows.

The original private `.mph` model is not included. The case demonstrates the automation pattern only:

1. Inspect an existing COMSOL model through the Java API.
2. Read magnetic field values from an existing solution dataset.
3. Run a controlled single-parameter solve on a copied model.
4. Extract sensor-level CSV data for engineering review.

The workflow is implemented by the reusable wrapper in `tools/comsol-baseline`.

## Engineering Context

The baseline represents a low-frequency / quasi-static magnetics workflow:

- Physics interface: magnetic field / induction-current style model.
- Study type: stationary study with a phase-angle parameter.
- Key parameter: `dt`, interpreted as an electrical phase angle in degrees.
- Result expressions:
  - `mf.Bx`
  - `mf.By`
  - `mf.Bz`
  - `mf.normB`
- Output unit: gauss (`G`)
- Review points: four fixed sensor points named `A`, `B`, `C`, and `N`.

This kind of case is useful when a structure engineer needs to compare magnetic-field readings at sensor positions across phase angles, without manually clicking through COMSOL result nodes.

## Public Files

| File | Purpose |
| --- | --- |
| `run_case.ps1` | Thin wrapper around `tools/comsol-baseline/comsol_baseline_tool.ps1`. |
| `configs/magnetostatic_sensor_eval.properties` | Dataset, expressions, units, solution indices, and CSV header. |
| `configs/magnetostatic_sensor_points.csv` | Public sample sensor names and coordinates. |
| `sample-output/sensor_eval_sample.csv` | Existing-solution sensor extraction sample. |
| `sample-output/single_solve_dt45.csv` | Controlled single-solve sample at `dt = 45`. |

## How To Run

From this folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_case.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode sensor-config
```

The default mode is `sensor-config`, which uses `configs/magnetostatic_sensor_eval.properties`.
Edit the properties file and `configs/magnetostatic_sensor_points.csv` to change dataset tag, result expressions, phase indices, or sensor coordinates.

The PowerShell wrapper reads these config files and passes resolved values into Java as command-line arguments. This avoids COMSOL Java security restrictions that can block direct file reads from inside the Java class.
For `solve-config`, `-DtDeg` overrides `solve_param_value` in the properties file.

Run one controlled solve:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_case.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode solve-config `
  -DtDeg 45
```

Run all baseline steps:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_case.ps1 `
  -InputModel "D:\path\to\your_model.mph" `
  -Mode all `
  -DatasetTag dset4 `
  -DtDeg 45
```

If COMSOL is installed outside the common paths, pass `-ComsolRoot` or set `COMSOL_ROOT`.

## Sample Results

Existing solution extraction:

| Sensor | Phase (`dt`) | `Bx` (G) | `By` (G) | `Bz` (G) | `normB` (G) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 0 | 0.0092 | -3.0336 | -1.4571 | 3.3654 |
| A | 90 | 102.8408 | 1.7202 | 2.5191 | 102.8861 |
| A | 180 | -0.0092 | 3.0336 | 1.4571 | 3.3654 |
| B | 0 | 88.9918 | 4.1154 | 3.4060 | 89.1520 |
| B | 90 | -50.8695 | 6.0319 | 2.0790 | 51.2681 |
| B | 180 | -88.9918 | -4.1154 | -3.4060 | 89.1520 |

Controlled single solve:

| Sensor | Phase (`dt`) | `Bx` (G) | `By` (G) | `Bz` (G) | `normB` (G) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 45 | 72.6625 | -0.9208 | 0.7560 | 72.6722 |
| B | 45 | 26.8287 | 7.1824 | 3.8806 | 28.0433 |
| C | 45 | -99.1116 | 1.5619 | -1.1063 | 99.1301 |
| N | 45 | -0.4711 | -4.0912 | -2.0198 | 4.5868 |

## What This Case Proves

- COMSOL can be driven from a repeatable command-line wrapper instead of manual GUI operations.
- Existing model results can be inspected and exported without rerunning the full study.
- A copied model can be modified and solved for a controlled parameter value.
- The output is small, reviewable, and suitable for downstream agent workflows.

## Known Limits

- The model file is private and intentionally excluded.
- The `sensor-config` and `solve-config` paths move sensor coordinates, expressions, study tag, parameter tag, parameter name, and dataset tag into public config files.
- The older `sensor` and `solve` modes are still hard-coded baseline checks.
- This is a baseline automation case, not a general COMSOL MCP server yet.

## Next Improvements

1. Add chart generation for `Bx`, `By`, `Bz`, and `normB` across phase angle.
2. Add an inspection summary that flags missing study, dataset, physics, and result tags before running a solve.
3. Wrap the same workflow behind a small MCP tool once the command-line contract is stable.

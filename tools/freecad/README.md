# FreeCAD STEP Inspection Wrapper

This folder contains small FreeCAD-based utilities for industrial CAD agent workflows.

The first wrapper is `inspect_step.py`. It reads a STEP/STP file with FreeCAD, then reports:

- overall bounding box
- solid count
- per-solid bounding boxes
- volume, area, face count, edge count, vertex count
- basic validity flags
- whether the input path contains non-ASCII characters
- optional validation checks for expected solid count, expected bbox, and geometry validity

Run it with FreeCAD's bundled Python:

```powershell
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  "<repo>\tools\freecad\inspect_step.py" `
  "<workspace>\matx-case\matx_tray_board_gpu_final_3part.step" `
  --json "<workspace>\matx_inspection.json" `
  --md "<workspace>\matx_inspection.md"
```

Use it as a validation gate:

```powershell
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  "<repo>\tools\freecad\inspect_step.py" `
  "<repo>\examples\pc-cooling\matx-motherboard-gpu-datum\motherboard_tray_board_gpu_v1.step" `
  --expect-solids 3 `
  --expect-bbox 342.5 154.45 253.84 `
  --bbox-tol 1.0 `
  --fail-on-invalid
```

The command exits with code `0` when all requested validation checks pass and `2` when any check fails.

Why bundled Python instead of `FreeCADCmd.exe`: on this Windows workstation, `FreeCADCmd.exe` did not reliably execute scripts from a path containing non-ASCII characters. FreeCAD's bundled `python.exe` imported `FreeCAD` and `Part` cleanly and produced stable output.

This is intentionally a local prototype. If the workflow proves stable, it can be used as the basis for a future `freecad-mcp` contribution such as `import_step` or `list_solids_with_bbox`.

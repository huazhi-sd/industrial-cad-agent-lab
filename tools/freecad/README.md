# FreeCAD STEP Inspection Wrapper

This folder contains small FreeCAD-based utilities for industrial CAD agent workflows.

The first wrapper is `inspect_step.py`. It reads a STEP/STP file with FreeCAD, then reports:

- overall bounding box
- solid count
- per-solid bounding boxes
- volume, area, face count, edge count, vertex count
- basic validity flags
- whether the input path contains non-ASCII characters

Run it with FreeCAD's bundled Python:

```powershell
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  "D:\cdxwork\26-0507-出图\onshape-cn-hardware-skills\tools\freecad\inspect_step.py" `
  "D:\cdxwork\26-0507-出图\matx-case\matx_tray_board_gpu_final_3part.step" `
  --json "D:\cdxwork\mcp-lab\matx_inspection.json" `
  --md "D:\cdxwork\mcp-lab\matx_inspection.md"
```

Why bundled Python instead of `FreeCADCmd.exe`: on this Windows workstation, `FreeCADCmd.exe` did not reliably execute scripts from a path containing non-ASCII characters. FreeCAD's bundled `python.exe` imported `FreeCAD` and `Part` cleanly and produced stable output.

This is intentionally a local prototype. If the workflow proves stable, it can be used as the basis for a future `freecad-mcp` contribution such as `import_step` or `list_solids_with_bbox`.

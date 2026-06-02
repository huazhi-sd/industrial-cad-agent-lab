---
name: industrial-cad-validator
description: Validate industrial CAD STEP/STP files and assemblies with rules-based checks. Use when a user needs STEP inspection, part/solid count verification, bounding-box checks, geometry validity checks, feature-plane or direction checks, assembly regression gates, or a validation report for industrial CAD work.
---

# Industrial CAD Validator

Use this skill to turn industrial CAD review requirements into repeatable validation gates.

## Workflow

1. Inspect the STEP with `scripts/inspect_step.py`.
2. Prefer a project `.rules.json` file for repeatable checks.
3. Keep checks focused on engineer-meaningful facts:
   - expected solid count;
   - overall and per-solid bounding boxes;
   - geometry validity;
   - relative bbox edge relationships;
   - feature direction or plane proxies.
4. Treat a failed rule as a design-review signal, not as a script problem until the rule is checked.
5. Do not use mirror or scale-like CAD operations to satisfy a rule unless the user explicitly approves.

## Script

Run with FreeCAD's bundled Python:

```powershell
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  ".\skills\industrial-cad-validator\scripts\inspect_step.py" `
  ".\examples\pc-cooling\matx-motherboard-gpu-datum\motherboard_tray_board_gpu_v1.step" `
  --rules ".\examples\pc-cooling\matx-motherboard-gpu-datum\motherboard_tray_board_gpu_v1.rules.json" `
  --json "$env:TEMP\cad_validation.json" `
  --md "$env:TEMP\cad_validation.md"
```

Exit code:

- `0`: all requested validation checks passed.
- `2`: one or more validation checks failed.

## Rules

Read `references/rules_schema.md` before writing a new project rules file.

Supported rule types:

- `solid_count`
- `bbox_dimensions`
- `bbox_dimension_range`
- `bbox_edge_relation`
- `validity`

## Reporting

Report:

- input STEP path;
- FreeCAD version if available;
- solid count;
- overall bbox;
- rule status and failed checks;
- whether the failure is likely a CAD issue, a wrong assumption, or a rule bug.

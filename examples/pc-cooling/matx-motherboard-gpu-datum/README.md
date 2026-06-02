# mATX motherboard tray + board + 3-slot GPU datum

This is a public AI + CAD collaboration example. It does not try to copy a specific commercial motherboard or GPU. Its purpose is to define a usable three-part datum assembly for compact mATX case layout work:

1. motherboard tray
2. mATX motherboard datum
3. 3-slot GPU datum

The current STEP is intentionally kept as 3 top-level solids. Helper details such as standoffs, connectors, PCIe goldfinger cues, backplate cues, and bracket pockets are integrated into those three meaningful parts instead of being exported as many small loose solids.

## Current output

| File | Purpose |
| --- | --- |
| `motherboard_tray_board_gpu_v1.step` | Current three-part assembly STEP |
| `motherboard_tray_v1.py` | Motherboard tray source |
| `motherboard_datum_v1.py` | mATX motherboard datum source |
| `gpu_3slot_datum_v1.py` | 3-slot GPU datum source |
| `motherboard_tray_board_gpu_v1.py` | Assembly source |
| `motherboard_tray_board_gpu_v1.rules.json` | FreeCAD STEP inspection rules |
| `validate_handedness.py` | Orientation and handedness checks |
| `validate_motherboard_tray_board_gpu_v1.py` | Assembly, GPU bracket, and goldfinger checks |
| `VIEW_CONVENTIONS.md` | Coordinate and view contract |
| `MOTHERBOARD_LAYOUT_DATUMS.md` | Motherboard layout datum notes |
| `GPU_3SLOT_DATUM_V1.md` | 3-slot GPU datum notes |
| `motherboard_tray_board_gpu_v1_front_20260602T045059Z.png` | Current front review image |
| `motherboard_tray_board_gpu_v1_side_20260602T045059Z.png` | Current side review image |
| `motherboard_tray_board_gpu_v1_iso_20260602T045059Z.png` | Current isometric review image |

The older `matx_tray_board_gpu_final_3part.*` files are retained as a process checkpoint from 2026-06-01. New work should prefer the `*_v1` files.

## Geometry contract

- Units: mm.
- Raw CAD `front` = motherboard component side.
- Rear I/O is left / low X.
- 24-pin ATX is right / high X.
- PCIe x16 and GPU are in the lower area / low Z.
- GPU extends to the right / high X.
- Tray is behind the motherboard on positive Y.
- Motherboard front surface is at negative Y.
- No mirror or scale-like CAD operation is allowed without explicit user approval.

## 3-slot GPU bracket lesson

The GPU bracket was corrected through several failed attempts. The useful rule is:

```text
The three PCIe slot screw pockets must be visible in the motherboard front view,
but their actual retaining-flange plane is away from the motherboard, near the
far end of the I/O bracket.
```

In this model:

- PCI slot pitch: `20.32 mm`
- Three-slot bracket span: `63.23 mm`
- Bracket height datum: `120.11 mm`
- Screw pocket count: `3`
- Screw pocket diameter datum: `6.2 mm`
- Screw clearance diameter datum: `3.6 mm`
- Screw pocket plane offset from motherboard front surface: about `117.51 mm`
- PCIe x16 goldfinger datum: `89.9 x 12.06 mm`

These bracket pockets drive the future case rear PCIe fixing geometry.

## Regenerate

From this directory:

```powershell
python .\validate_handedness.py
python .\validate_motherboard_tray_board_gpu_v1.py
python C:\Users\cokewithice\.codex\skills\cad\scripts\step --force .\motherboard_tray_board_gpu_v1.py
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  ..\..\..\tools\freecad\inspect_step.py `
  .\motherboard_tray_board_gpu_v1.step `
  --rules .\motherboard_tray_board_gpu_v1.rules.json
```

Render a review image:

```powershell
python C:\Users\cokewithice\.codex\skills\cad\scripts\snapshot `
  --input .\motherboard_tray_board_gpu_v1.step `
  --output .\front_view.png `
  --camera front `
  --size-profile diagnostic
```

## Why this example matters

This small assembly exposed real AI CAD workflow issues:

- "Front" must be defined as a project contract, not guessed from camera labels.
- User corrections should become executable validators as soon as they reveal a recurring failure mode.
- STEP part structure matters. For layout work, meaningful top-level parts are more useful than many helper solids.
- A visible feature can still be on the wrong physical plane. The GPU screw pockets are the best example here.
- CAD agents need both visual checks and numeric checks.

The procedural rule from this case:

```text
When a user corrects a principle, turn it into a written and executable gate
before continuing geometry work.
```

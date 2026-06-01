# mATX case view conventions

This project uses engineering view names, not CAD snapshot preset names.

## Coordinate datum

- X = rear I/O side to front side of motherboard. In raw motherboard front
  view, low X appears on the left and high X appears on the right.
- Y = motherboard tray normal. Negative Y is the component/front side;
  positive Y is the tray/back side.
- Z = bottom PCIe side to top CPU power side.
- Origin = lower rear corner of the motherboard PCB envelope.

## Motherboard Front View

For motherboard/tray/GPU datum assemblies, `front` means the motherboard
component side. In a raw CAD standard front view, the user must see the
motherboard features, not the tray back side.

Later full-case work may use `case front` for the human-facing case front panel.
Do not shorten `case front` to `front` while editing motherboard datum files.

## Component-side main view

The semantic component-side main view must show:

- Rear I/O on the left upper edge.
- Dual EPS 8-pin connectors near the upper-left area.
- 24-pin ATX connector on the right edge.
- DIMM slots to the right of the CPU socket.
- PCIe x16 slot in the lower-left area, extending toward the right.

Do not use manually flipped PNGs as engineering truth. The opened STEP must be
correct by itself. A snapshot may be used only as a direct view of the exported
STEP; do not horizontally flip it to make the view look correct.

Before generating side or section views, first inspect the raw CAD standard
front view against the checklist above.

## Handedness gate

Before regenerating motherboard, tray, GPU, or case assembly STEP files, run:

```powershell
python matx-case/validate_handedness.py
```

Do not continue to assembly generation if this check fails.

This gate exists because the project has already produced multiple mirrored
motherboard drafts. The check locks the semantic layout:

- rear I/O = left side in raw opened STEP front view / low X
- PCIe x16 and GPU = low Z / lower side
- EPS CPU power = high Z / upper side
- 24-pin ATX power = right side in raw opened STEP front view / high X
- 8-hole mATX support pattern = B, C, F, R, H, J, L, M

## Forbidden Without Explicit User Approval

Do not use CAD mirror operations to fix handedness unless the user explicitly
approves that exact operation first.

Forbidden examples include:

- `shape.mirror(...)`
- mirrored clone/feature operations
- using a global negative scale as a mirror substitute
- mirroring a component assembly after it has already been authored

Reason: mirror operations are dangerous in this project because they can hide
wrong handedness, invert left/right mechanical intent, and break mating datums.
Fix handedness by rebuilding coordinates, rotating around documented datums, or
editing part-local placement rules instead.

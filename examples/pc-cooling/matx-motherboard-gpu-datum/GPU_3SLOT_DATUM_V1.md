# GPU 3-Slot Datum V1

This layer adds a simplified 3-slot GPU to the mATX tray + board datum.

## External References Used

- PCI Express CEM Rev. 5.1, Figure 1-4: triple-slot cards use three `20.32 mm`
  slot intervals.
- PCI Express CEM Rev. 5.1, Figure 11-15: detailed three-slot I/O bracket
  design includes `120.11 mm`, `112.75 mm`, `63.23 mm`, `5x Ø4.42 mm`, and
  `20 GA` low carbon steel notes.
- Public discussion citing CEM connector opening: `89.9 mm x 12.06 mm`.

## Scope

- 335 mm long GPU envelope.
- 70 mm three-slot cooler envelope.
- 145 mm height away from motherboard.
- Three-slot I/O bracket datum.
- Simplified vent windows and fixture holes.
- Three visible rear screw-lock pockets on the folded video-I/O retaining
  flange. These pockets are intended to be visible in the motherboard front
  view, because they drive the case rear PCI-slot fixing geometry.
- PCIe x16 goldfinger mating datum.
- Raised backplate datum above the goldfinger plane.

## Not Yet Final

- Exact stamped bracket outline is simplified.
- Individual PCIe contacts are not modeled.
- Screw tab geometry is simplified.
- Screw pockets are layout datums, not a fully stamped production bracket.
- Thermal fins/fans are not modeled.

## Validation

Run:

```powershell
python validate_motherboard_tray_board_gpu_v1.py
```

Expected gates:

- no mirror/scale-like CAD operations;
- assembly has exactly 3 top-level parts;
- GPU length envelope is at least `335 mm`;
- GPU slot-width envelope is at least `70 mm`;
- GPU height-away-from-board envelope is at least `145 mm`;
- bracket uses `120.11 mm` height and `63.23 mm` three-slot span;
- rear bracket has `3x` front-view screw-lock pockets on `20.32 mm` slot pitch;
- goldfinger datum is aligned to the motherboard PCIe x16 slot.

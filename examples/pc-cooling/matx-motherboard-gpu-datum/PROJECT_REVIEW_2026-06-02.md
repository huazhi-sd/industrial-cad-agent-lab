# mATX datum project review - 2026-06-02

## Current useful output

- `motherboard_tray_board_gpu_v1.step`
- Scope: motherboard tray + mATX motherboard datum + 3-slot GPU datum.
- Top-level solids: exactly 3.
- FreeCAD import: valid.
- GPU datum: one solid.
- Raw CAD front view: motherboard component side.

## What was added today

### 1. Layered source files

The model was split into clearer source layers:

- `motherboard_tray_v1.py`
- `motherboard_datum_v1.py`
- `gpu_3slot_datum_v1.py`
- `motherboard_tray_board_gpu_v1.py`

This is better than a monolithic script because each layer has its own datum logic and validation target.

### 2. 3-slot GPU bracket datum

The GPU is still a simplified layout datum, but it now includes the features that affect case design:

- 335 mm GPU length envelope.
- 145 mm height-away-from-board envelope.
- 70 mm class three-slot cooler envelope.
- PCIe x16 goldfinger mating datum.
- Video-I/O bracket datum.
- Three PCIe slot screw pockets.

### 3. Front-view-visible screw pockets on the correct plane

The most important correction:

```text
The three screw pockets should be visible in motherboard front view,
but the retaining-flange plane is away from the motherboard.
```

The wrong intermediate versions placed the holes on the side-view plane or too close to the motherboard. That looked partly plausible in screenshots but was physically wrong for case rear-panel design.

Current validation checks:

- `3x` screw pockets.
- `20.32 mm` PCI slot pitch.
- `6.2 mm` screw pocket diameter datum.
- `3.6 mm` screw clearance diameter datum.
- screw pocket plane offset from motherboard front: about `117.51 mm`.

## What this teaches for AI CAD

### Visual correctness is not enough

A feature can be visible from the expected camera view and still be on the wrong physical plane.

This happened with the GPU retaining screw pockets:

- First mistake: modeled as side-view bracket holes.
- Second mistake: visible in front view, but placed too close to the motherboard.
- Corrected version: visible in front view and located on the far retaining-flange plane.

The lesson:

```text
For every mating feature, validate both visibility and physical plane.
```

### User corrections must become gates

Once the user identified the screw pocket plane issue, the validator was updated immediately. This is the right workflow. The next time this class of error appears, a script should catch it before a final answer.

### Assembly cleanliness matters

The final handoff should remain three meaningful parts:

1. tray
2. motherboard datum
3. GPU datum

Internal helper features may be built in source code, but the exported STEP should not expose dozens of tiny top-level solids.

## Validator gates added

`validate_motherboard_tray_board_gpu_v1.py` now checks:

- no mirror or scale-like operation;
- bracket height datum remains `120.11 mm`;
- three-slot span remains `63.23 mm`;
- screw pocket diameter remains `6.2 mm`;
- screw clearance diameter remains `3.6 mm`;
- goldfinger length remains `89.9 mm`;
- goldfinger visible depth remains `12.06 mm`;
- goldfinger aligns to motherboard PCIe x16 datum;
- screw pocket plane is at the far bracket end, away from motherboard;
- GPU envelope remains large enough;
- assembly has exactly 3 top-level parts.

## Known simplifications

- The bracket is not a full stamped production PCIe bracket.
- Screw pockets are layout datums for case rear-panel design.
- The GPU cooler is an envelope, not a detailed graphics card.
- PCIe contacts are not individually modeled.
- The motherboard is a chassis-layout datum, not a specific commercial B850M board.

## Next suggested step

Use this assembly as the starting point for the case rear panel:

1. rear I/O shield opening;
2. PCIe slot cutouts;
3. PCIe retaining screw strip;
4. GPU clearance volume;
5. first-pass mATX tray-to-rear-panel structure.


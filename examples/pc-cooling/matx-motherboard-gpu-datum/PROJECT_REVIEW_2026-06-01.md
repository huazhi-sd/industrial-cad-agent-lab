# mATX case datum project review - 2026-06-01

## Current useful output

- File: `matx_tray_board_gpu_final_3part.step`
- Scope: motherboard tray + motherboard datum + 3-slot GPU.
- Top-level parts: exactly 3.
- Raw CAD front view: motherboard component side.
- Current accepted state: first visually usable version, not final case layout.

## 1. How much came from the new skill and MCP work

### Directly used

- `cad` skill was the main production tool.
  - Generated STEP from build123d source.
  - Inspected STEP topology and part counts.
  - Rendered raw `front` and `side` verification PNGs.
  - Helped enforce STEP-first workflow instead of browser/UI clicking.
- `cad-viewer` was used as the review handoff path.
  - The user inspected `matx_tray_board_gpu_final_3part.step` in the browser.
  - This made part-tree clutter and visual direction errors visible.

### Indirectly used

- AgentCAD influenced the workflow idea:
  - produce structured run results;
  - compare versions;
  - report part count, bounding boxes, validity;
  - keep generated artifacts reviewable.
- Onshape MCP / Onshape API research influenced the target direction:
  - future work should use structured CAD operations, import/export, part lists, names, and metadata;
  - browser UI automation should not be the main route.

### Not directly used in this final mATX assembly

- AgentCAD MCP was not the actual generator for this model.
- Onshape MCP/API was not used to create or edit this STEP.
- FreeCAD MCP was not used.

The real production path for this deliverable was:

```text
build123d source -> cad skill STEP generation -> inspect/snapshot -> CAD Viewer/manual review -> source correction
```

## 2. Possible contributions to early AI CAD projects

### cad / text-to-cad skill

- Windows snapshot issue:
  - report or fix `--single-process` causing Chrome Headless Shell / WebGL crashes on Windows.
- Orientation review workflow:
  - add a documented "raw CAD view contract" pattern.
  - recommend saving front/back/side snapshots without manual flipping.
- Assembly cleanliness:
  - add examples or docs for exporting low-clutter STEP assemblies with only meaningful top-level parts.
- Regression gates:
  - add examples for user-defined geometry validators, such as handedness checks and part-count checks.

### AgentCAD

- Windows daemon problem:
  - report/fix `os.getuid()` usage on Windows.
  - ensure MCP run also avoids daemon spawning or supports `--no-daemon`.
- MCP error reporting:
  - return full traceback/exception text instead of `No output`.
- Industrial workflow examples:
  - provide small mechanical layout examples with constraints, snapshots, diffs, and user review loops.

### Onshape MCP / Onshape client direction

- mm-first defaults.
- Import STEP, list elements, list parts, rename parts, export STEP.
- Render named standard views from API where possible.
- Return structured feature/part-operation results.
- Avoid relying on screenshot clicking as the main CAD operation path.

## 3. Why the view-direction problem repeated

The repeated failure was not only a "view" problem. It was a process-control failure.

### What went wrong

- There were several meanings of "front":
  - CAD camera `front`;
  - motherboard component side;
  - motherboard tray side;
  - future case user-facing front.
- I did not freeze the user's definition early enough:
  - for this project, motherboard `front` must mean motherboard component side.
- I changed other accepted geometry while fixing one issue:
  - a previous acceptable I/O armor was replaced by a worse one.
- I relied too much on visual judgement after each change.
  - The raw STEP view and source coordinate rules were not locked together.
- I lacked a regression checklist.
  - After fixing one item, I did not automatically check the user-emphasized constraints again.
- I treated the user's correction as local feedback, not as a global rule.
  - "先统一正面" should have become a project gate immediately.

### How to reduce repeats next time

Before touching geometry after a major user correction, create or update a contract file:

```text
1. Accepted facts - do not change without explicit reason.
2. Variable facts - allowed to edit.
3. View contract - what front/left/right/top mean.
4. Hard gates - scripts or manual checks that must pass before exporting.
5. Review images - the exact raw views that prove the gates.
```

For every later edit, use this rule:

```text
Fix only the requested item.
Do not alter accepted items unless explicitly required.
Run regression checks before saying "done".
```

For this project, the active hard gates are now:

- raw CAD `front` = motherboard component side;
- rear I/O = left / low X;
- 24-pin = right / high X;
- PCIe and GPU = lower area, GPU extends right;
- tray is behind board on positive Y;
- final STEP has exactly 3 top-level parts;
- no mirror or scale-like operations without explicit user approval.

## 4. Process changes for the next CAD task

### Work in accepted layers

- Layer 1: orientation and coordinate contract.
- Layer 2: mounting holes and standoff spacing.
- Layer 3: board keepouts and connector envelopes.
- Layer 4: mating features such as PCIe goldfinger.
- Layer 5: cosmetic cues.

Do not work on Layer 5 while Layer 1-4 are unstable.

### Use "lock notes"

When the user says a version is acceptable in one area, record it:

```text
LOCKED: I/O armor concept from earlier board image is acceptable.
UNLOCKED: I/O armor height may need adjustment.
```

This prevents replacing a good design while solving a small issue.

### Use failure memory

If the same kind of error happens twice, add an automatic or written gate before continuing.
If it happens three times, stop generating geometry and repair the workflow first.

In this project, the gate should have been added after the second handedness error, not after the fourth.

## 5. Current known remaining issues

- I/O armor height/shape is improved but still needs user visual approval.
- CPU EPS position is only a plausible datum, not checked against a specific real B850M board.
- GPU goldfinger is present and aligned as a mating datum, but still simplified.
- Motherboard mounting-hole standard and visible-board-hole styling are separated imperfectly.
- The model is a datum/fit assembly, not a manufacturable motherboard or chassis yet.


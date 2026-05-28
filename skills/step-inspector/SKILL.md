# Step Inspector

Generate engineer-verifiable 2D reference views from imported STEP files.

This skill exists because CAD agents can easily confuse mathematical projection
directions with the view orientation expected by a human CAD user. For circuit
breaker and meter layouts, always anchor view direction to the product meaning:

- Front: the user-facing side with the handle and covers.
- Back: the DIN rail / rail clip side.
- Left view: the same screen result the engineer gets by clicking `Left` on the
  Onshape view cube after the model has been front-aligned.

## Current Proven Workflow

Use this skill when the user asks for a side-view layout, hidden-shell view, or
internal space relationship from a STEP model.

1. Use the `*_front_aligned.step` file, not an early raw import.
2. Render both candidates if direction is uncertain.
3. Do not call the view correct until the user confirms it matches their CAD
   `Left` view.
4. After the correct view is confirmed, reuse the same projection and hiding
   parameters for overlays and layout sketches.

## G1-1P Meter Project Calibration

For the 2026-05-28 G1-1P meter layout project, the corrected left view is:

```powershell
python .\skills\step-inspector\scripts\render_left_view.py `
  --step <private-project>\g1-1p-528_front_aligned.step `
  --output <private-project>\corrected_left_view_g1_hide_other_shell_candidate.png `
  --title "G1-1P corrected LEFT view - hide other shell candidate" `
  --hide 20 `
  --label-solids `
  --view-from xmax `
  --mirror-y `
  --tolerance 1.0
```

This produced the first user-confirmed correct image:

```text
<private-project>\corrected_left_view_g1_hide_other_shell_candidate.png
```

Important: earlier images without `--mirror-y`, or images hiding part `29` for
this same view task, were right-view or wrong-hidden-shell outputs for the
user's purpose. Do not use them as layout basis.

## Why The Earlier Attempts Failed

The local renderer projected geometry to the Y-Z plane correctly, but the screen
orientation did not match Onshape's human-facing `Left` view. The result looked
geometrically plausible but was left-right reversed for the user's design
discussion.

The lesson is:

- A correct projection plane is not enough.
- The screen orientation must match the engineer's CAD view cube.
- For this project, `--view-from xmax --mirror-y` is the confirmed left-view
  calibration for `g1-1p-528_front_aligned.step`.

## Usage Notes

The script is a lightweight inspection renderer. It tessellates solids and draws
triangles sorted by X depth. It is not a full CAD renderer, but it is good enough
for:

- side-view space relationship checks;
- hidden-shell inspection;
- marking copper busbar corridors;
- checking gear group / connector / shell relative positions;
- creating discussion images before formal modeling.

Do not use color order or STEP entity order as semantic identity by itself.
Part indices may help reproduce a view after a user-confirmed calibration, but
semantic names such as left shell, right shell, copper busbar, gear group, and
18-pin connector must be confirmed by geometry and engineer feedback.

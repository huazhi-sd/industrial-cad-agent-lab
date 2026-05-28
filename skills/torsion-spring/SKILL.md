---
name: torsion-spring
description: Generate or repair close-coiled torsion spring CAD models for Onshape from wire diameter, coil outside diameter, turn count, leg lengths, and leg directions; use when creating a clean STEP torsion spring or replacing a faulty imported spring.
---

# Torsion Spring

Use this skill when a user needs a clean torsion spring model for Onshape, especially when an imported STEP spring has topology errors.

## Required Inputs

- `wire_d`: wire diameter.
- `coil_od`: coil outside diameter.
- `turns`: effective coil turns.
- `leg_a_len`: first leg length.
- `leg_b_len`: second leg length.
- Leg direction or included angle, if known.
- `close_coiled`: default `true`.

## Modeling Rules

1. Build one continuous centerline: leg A -> helix -> leg B.
2. Sweep one circular section along the full centerline in one operation.
3. Do not model the coil and legs as separate bodies and boolean them later.
4. Do not allow a leg to reverse direction with a local 180 degree bend.
5. For close-coiled springs, use:

```text
coil_center_radius = (coil_od - wire_d) / 2
pitch = wire_d
```

6. The coil outside diameter must remain `coil_od` after sweep.
7. If fitting an original imported spring, prioritize in this order:
   1. continuous centerline,
   2. correct leg directions,
   3. close-coiled turns,
   4. correct wire diameter and outside diameter,
   5. endpoint position near the original assembly.

## Recommended Workflow

1. Ask for missing spring parameters only when they cannot be inferred safely.
2. Run `scripts/generate_torsion_spring.py` to create a STEP file.
3. Import into Onshape with `allowFaultyParts=false`.
4. If replacing an existing assembly instance, preserve the old instance transform before deleting it.
5. Compare against the original with transparent overlay or multi-view screenshots.

## Script

Basic example:

```powershell
python .\scripts\generate_torsion_spring.py `
  --wire-d 0.25 `
  --coil-od 2.45 `
  --turns 3 `
  --leg-a-len 12 `
  --leg-b-len 10 `
  --output torsion_spring.step
```

Optional direction fitting:

```powershell
python .\scripts\generate_torsion_spring.py `
  --wire-d 0.25 `
  --coil-od 2.45 `
  --turns 3 `
  --leg-a-len 12 `
  --leg-b-len 10 `
  --leg-a-dir 0,-1,0 `
  --leg-b-dir 0,1,0 `
  --output fitted_torsion_spring.step
```

Read `references/onshape_import_replace.md` before uploading/replacing parts through the Onshape API.

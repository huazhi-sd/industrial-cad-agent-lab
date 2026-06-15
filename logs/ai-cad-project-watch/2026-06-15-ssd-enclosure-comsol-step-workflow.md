# SSD Enclosure COMSOL STEP Workflow - 2026-06-15

## Scope

Today focused on connecting a CAD-generated M.2 2280 SSD enclosure to a COMSOL
electrostatic workflow.

The main question was not whether COMSOL can import STEP. It can. The useful
question was which import workflow gives an agent a clean path toward material
assignment, boundary conditions, and later simulation checks.

## What Worked

- Generated a refined product STEP for a transparent PC M.2 enclosure.
- Removed accidental top-cover circular features from the CAD model.
- Reworked the top-cover tongue and Type-C relief to reduce obvious assembly
  interference.
- Built a simulation-prep manifest experiment for CAD-to-COMSOL semantic
  mapping.
- Verified that COMSOL can directly import the product STEP.
- Verified the corrected workflow:
  - import product STEP first;
  - keep it as Form Assembly;
  - create the air domain inside COMSOL afterward.

The corrected direct STEP workflow produced:

```text
SSD_DIRECT_STEP_STATUS=geometry_success
geom_is_assembly=true
geom_has_cad_rep=true
geom_features=[imp1, air_after_import, fin]
geom_domains=40
geom_boundaries=449
```

This is much cleaner than the earlier attempt that included the air domain in
the same STEP file.

## Important Correction

The earlier "88 domains" result was caused by the wrong workflow:

1. The air domain was exported together with the product geometry into one STEP.
2. COMSOL finalized that mixed geometry in a way that heavily partitioned the
   model.

That was not a reason to avoid direct STEP import.

The better industrial workflow is:

```text
Product STEP -> COMSOL import as assembly -> COMSOL air box -> physics setup
```

This is also closer to how a human COMSOL user would work.

## Current Blocker

The next hard step is robust automated material and boundary-condition
assignment for imported STEP geometry.

Open questions:

- How should an agent reliably map `imp1.SOLID(n)` objects to semantic product
  roles?
- Can COMSOL-generated import selections be used directly?
- Is it better to record a COMSOL method after one manual material-assignment
  pass and convert that into a reusable wrapper?
- Should the CAD generator emit a manifest with expected material, role,
  voltage, and bbox for every semantic solid?

## Artifacts Added

Public example:

- `examples/comsol/ssd-enclosure-esd-step-workflow/`

Key files:

- `transparent_pc_m2_2280_ssd_enclosure_assembly.step`
- `source/transparent_pc_m2_2280_ssd_enclosure_assembly.py`
- `source/ssd_enclosure_esd_sim_simplified.py`
- `source/match_comsol_step_manifest.py`
- `comsol/ComsolStepImportInspector.java`
- `comsol/SsdEnclosureDirectStepAssemblyDraft.java`

## Next Step

Use COMSOL Desktop or Java API inspection to discover the most reliable way to
assign materials to imported product solids.

The most practical next experiment is:

1. Open the generated `.mph` draft.
2. Assign one or two materials manually in COMSOL.
3. Record or export the corresponding Java method.
4. Turn that method into a small reusable agent wrapper.

# SSD Enclosure ESD STEP-to-COMSOL Workflow

Date: 2026-06-15

This example records a small workflow trial for moving a CAD-generated M.2
2280 SSD enclosure into COMSOL for a first-pass electrostatic study.

It is not a certification-grade breakdown model. The goal is to test how a CAD
agent can hand geometry to COMSOL in a way that still resembles a human
simulation workflow.

## Files

- `transparent_pc_m2_2280_ssd_enclosure_assembly.step`
  - Product-only CAD assembly STEP.
  - Intended for direct import into COMSOL.
- `source/transparent_pc_m2_2280_ssd_enclosure_assembly.py`
  - build123d source for the enclosure assembly.
- `source/ssd_enclosure_esd_sim_simplified.py`
  - Experimental CAD-side semantic-domain export.
  - Useful for manifest and mapping tests, but not the preferred COMSOL setup
    path.
- `source/match_comsol_step_manifest.py`
  - Matches COMSOL-imported object bounding boxes back to a CAD-side manifest.
- `ssd_enclosure_esd_manifest.json`
  - CAD-side semantic manifest for the simulation-prep export.
- `ssd_enclosure_esd_comsol_mapping.json`
  - Example bbox mapping result.
- `comsol/ComsolStepImportInspector.java`
  - COMSOL Java utility that imports a STEP file and prints geometry/object
    diagnostics.
- `comsol/SsdEnclosureDirectStepAssemblyDraft.java`
  - Preferred draft: import the product STEP first, then create the air domain
    inside COMSOL.

## Corrected Workflow

The useful result from this trial is the workflow correction:

1. Export the product geometry as a product-only STEP.
2. Import that STEP into COMSOL.
3. Keep the product geometry as an assembly:

   ```java
   model.component("comp1").geom("geom1").feature("fin").set("action", "assembly");
   model.component("comp1").geom("geom1").feature("fin").set("imprint", false);
   ```

4. Create the outer air domain after STEP import, inside COMSOL.
5. Assign materials and electrostatic boundary conditions after import.

This matches the normal human workflow better than exporting the air domain and
the product into one monolithic STEP.

## Result

The direct STEP import + COMSOL-created air domain route produced:

```text
SSD_DIRECT_STEP_STATUS=geometry_success
geom_is_assembly=true
geom_has_cad_rep=true
geom_features=[imp1, air_after_import, fin]
geom_domains=40
geom_boundaries=449
```

The 40 domains correspond to:

- 39 product solids from the product STEP
- 1 air domain created after import in COMSOL

## Important Lesson

A previous attempt exported the air domain together with all product solids into
one STEP, then let COMSOL finalize it as a union. That created a heavily sliced
geometry with many more domains than expected.

That was not a COMSOL failure. It was a workflow mistake.

For product-enclosure electrostatics, a better agent workflow is:

```text
CAD product STEP -> COMSOL import as assembly -> COMSOL air domain -> physics setup
```

## Remaining Open Problem

The next hard step is reliable automated material and boundary-condition
assignment for imported STEP objects.

COMSOL exposes imported objects as names such as:

```text
imp1.SOLID(1)
imp1.SOLID(2)
...
```

However, these object names are not yet semantic enough for robust agent
simulation setup. The current practical options are:

- use an exported CAD manifest plus bounding-box matching;
- use COMSOL GUI method recording after a human assigns materials once;
- investigate generated import selections and object/domain mappings in the
  COMSOL Java API.

The most promising next step is to record or export a small COMSOL method after
manual material assignment, then translate that into a reusable agent-side
wrapper.

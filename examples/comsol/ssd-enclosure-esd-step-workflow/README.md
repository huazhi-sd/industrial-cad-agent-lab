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
- `source/run_comsol_step_import_baseline.py`
  - Imports the product STEP into COMSOL, creates the air domain, and records
    geometry diagnostics.
- `source/match_union_domains_by_measure.py`
  - Uses COMSOL final-geometry measurements to match Form Union domains back to
    CAD semantic groups.
- `source/apply_comsol_domain_mapping.py`
  - Creates domain selections and first-pass material assignments.
- `source/probe_comsol_boundary_mapping.py`
  - Converts domain selections into boundary selections for electrode setup.
- `source/apply_comsol_esd_boundary_conditions.py`
  - Applies first-pass voltage and ground boundary conditions with overlap
    checks.
- `source/run_comsol_esd_stationary_solve.py`
  - Runs mesh generation and a stationary Electrostatics study.
- `source/extract_comsol_esd_results.py`
  - Extracts first-pass voltage and electric-field statistics from a solved
    `.mph` model.
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
3. Create the outer air domain after STEP import, inside COMSOL.
4. Use two different geometry finalization modes for two different jobs:

   - `assembly` + `imprint=false` is useful for object/domain inspection.
   - `union` is required for a connected electrostatic field solve.

Inspection mode:

   ```java
   model.component("comp1").geom("geom1").feature("fin").set("action", "assembly");
   model.component("comp1").geom("geom1").feature("fin").set("imprint", false);
   ```

Solve mode:

   ```java
   model.component("comp1").geom("geom1").feature("fin").set("action", "union");
   ```

5. Match COMSOL domains back to CAD semantic groups.
6. Assign materials and electrostatic boundary conditions after import.
7. Mesh, solve, and extract first-pass field statistics.

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

## Re-Test With Local COMSOL 6.3

Date: 2026-06-17

The workflow was re-tested on Windows with COMSOL installed at:

```text
D:\comsol\COMSOL63\Multiphysics\bin\win64
```

Reusable script:

```powershell
D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\run_comsol_step_import_baseline.py
```

Observed result:

```text
status=success
comsol_version=6.3
features=[imp1, air_after_import, fin]
geom_is_assembly=true
geom_has_cad_rep=true
object_count=40
geom_domains=40
geom_boundaries=449
geom_bbox=[-67.5, 67.5, -32.0, 32.0, -8.0, 26.0]
physics_created=[es]
```

This confirms that the product-only STEP can be imported into COMSOL, kept as
an assembly for inspection, combined with a COMSOL-created air domain, and
given an initial Electrostatics physics node. Later solve tests showed that
this assembly mode is not sufficient for a connected electrostatic solve; the
solved workflow below uses Form Union.

## Domain Mapping And First-Pass Materials

Date: 2026-06-17

Reusable scripts:

```powershell
python .\source\match_baseline_json_manifest.py `
  --manifest .\ssd_enclosure_esd_manifest.json `
  --baseline .\comsol\baseline-runs\ssd_enclosure_step_import_baseline_20260617_170638.json `
  --output .\comsol\baseline-runs\ssd_enclosure_baseline_domain_mapping_20260617_170638.json

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\apply_comsol_domain_mapping.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_step_import_baseline_20260617_170638.mph `
  --mapping .\comsol\baseline-runs\ssd_enclosure_baseline_domain_mapping_20260617_170638.json `
  --out .\comsol\baseline-runs
```

Mapping result:

```text
baseline_object_count=40
manifest_product_solid_count=39
all_matched=True
```

First-pass domain groups:

| CAD semantic domain | Material | Domain guesses |
| --- | --- | --- |
| bottom_shell_transparent_pc | polycarbonate | 1 |
| top_shell_transparent_pc | polycarbonate | 2 |
| main_pcb_fr4_and_components | FR4_simplified | 3-17 |
| usb_c_shell_metal_ground | stainless_steel_or_shell_metal | 18 |
| main_pcb_high_potential_copper | copper | 19-30 |
| main_pcb_ground_copper | copper | 31-33 |
| m2_2280_ssd_fr4_and_components | FR4_simplified | 34 |
| ssd_exposed_copper_regions | copper | 35-38 |
| m2_tail_screw | steel | 39 |
| air_domain_esd_clearance_box | air | 40 |

The script creates named COMSOL selections for these groups and assigns
first-pass material nodes:

- Polycarbonate: relative permittivity `2.9`
- FR4: relative permittivity `4.3`
- Air: relative permittivity `1`
- Copper/steel/stainless: placeholder conductor materials

Important caveat: conductor material assignment is not the final electrostatic
boundary setup. Final ESD simulation should apply voltage/ground conditions to
the relevant conductor surfaces after boundary IDs are verified.

## Important Lesson

A previous attempt treated the `assembly` import result as the final simulation
geometry. That was useful for object recognition, but it produced a disconnected
electrostatic model and the stationary solve became singular.

The working simulation route uses:

```text
CAD product STEP -> COMSOL import -> COMSOL air domain -> Form Union -> domain measurement/mapping -> physics setup
```

With Form Union, COMSOL splits the air volume around product solids. Therefore
the final domain count is expected to be larger than the number of CAD solids.
This is not a COMSOL failure; it is the geometry becoming solvable for a field
problem.

## First Closed-Loop ESD Solve

Date: 2026-06-17

After simplifying overlapping conductor geometry and moving the USB-C shield to
a simulation-safe external block, the workflow reached a first complete loop:

```text
CAD STEP -> COMSOL Form Union -> measured domain mapping -> materials -> boundary conditions -> mesh -> stationary solve -> result extraction
```

Observed solve run:

```text
baseline_timestamp=20260617_184109
domain_count=53
boundary_count=570
all_product_matched=True
mesh_size=8
solve_status=success
result_timestamp=20260617_184842
V_min=-0.013 V
V_max=1000.000 V
E_norm_max=3.57e6 V/m
```

Reusable command sequence:

```powershell
D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\run_comsol_step_import_baseline.py `
  --finalization-action union `
  --out .\comsol\baseline-runs

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\match_union_domains_by_measure.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_step_import_baseline_20260617_184109.mph `
  --manifest .\ssd_enclosure_esd_manifest.json `
  --output .\comsol\baseline-runs\ssd_enclosure_measured_domain_mapping_union_20260617_184109.json `
  --tolerance 0.1

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\apply_comsol_domain_mapping.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_step_import_baseline_20260617_184109.mph `
  --mapping .\comsol\baseline-runs\ssd_enclosure_measured_domain_mapping_union_20260617_184109.json `
  --out .\comsol\baseline-runs

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\probe_comsol_boundary_mapping.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_material_selections_20260617_184221.mph `
  --material-report .\comsol\baseline-runs\ssd_enclosure_material_selections_20260617_184221.json `
  --out .\comsol\baseline-runs

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\apply_comsol_esd_boundary_conditions.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_material_selections_20260617_184221.mph `
  --boundary-probe .\comsol\baseline-runs\ssd_enclosure_boundary_probe_20260617_184300.json `
  --out .\comsol\baseline-runs

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\run_comsol_esd_stationary_solve.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_esd_boundary_conditions_20260617_184341.mph `
  --out .\comsol\baseline-runs `
  --mesh-size 8

D:\cdxwork\mcp-lab\COMSOL_Multiphysics_MCP\.venv\Scripts\python.exe `
  .\source\extract_comsol_esd_results.py `
  --mph .\comsol\baseline-runs\ssd_enclosure_esd_stationary_solved_20260617_184421.mph `
  --out .\comsol\baseline-runs
```

Important caveats:

- This is not a qualified breakdown model.
- The maximum electric field is mesh- and sharp-edge-dependent.
- The current USB-C shield is a simulation simplification, not final product
  geometry.
- A real ESD/breakdown workflow still needs better conductor definitions,
  dielectric strength criteria, and visual verification of boundary selections.

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

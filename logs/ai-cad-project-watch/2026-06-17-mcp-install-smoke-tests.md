# MCP Install Smoke Tests - 2026-06-17

## Purpose

Smoke-test several CAD/simulation MCP-style projects on a Windows workstation and record which parts are usable for industrial CAD agent workflows, especially the M.2 SSD enclosure experiment.

This log intentionally avoids API keys and proprietary model details.

## Local Environment

- OS: Windows
- Python: 3.12.10
- `uv`: 0.11.15
- Node/npm: available
- FreeCAD: `D:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe`
- COMSOL: available at `D:\comsol\COMSOL63\Multiphysics\bin\win64\comsol.exe`
- Autodesk Inventor/Fusion 360: not installed on this workstation

## Results

### 1. `kouya-group/fcgen-mcp`

Status: usable locally through its CLI/package entry point.

What worked:

- Installed dependencies with `uv`.
- Ran `uv run --extra mcp fcgen --help`.
- Generated a simple enclosure STEP from the built-in `enclosure` template.
- Generated a simple bolt STEP from the built-in `bolt` template.
- Inspected generated STEP files with FreeCAD.

Generated local artifacts:

- `D:\cdxwork\mcp-lab\fcgen-mcp\trials\ssd_enclosure_fcgen_out\model.step`
- `D:\cdxwork\mcp-lab\fcgen-mcp\trials\m2_ssd_screw_fcgen_out\model.step`

Observed geometry:

- Enclosure: 2 solids, bounding box about `105 x 35 x 15 mm`
- Screw/bolt: 1 solid, bounding box about `4 x 4 x 3.8 mm`

Relevance to SSD enclosure:

- Good reference for a constrained template architecture: template + JSON Schema + semantic validation + STEP output.
- The current enclosure template is too generic for our SSD enclosure: no Type-C opening, no continuous enclosure lip, no snap/fit wall, no PCB/SSD internals.
- Good candidate architecture for future "standard industrial part / enclosure template" work.

Limitations observed:

- The template parameter meaning should be documented more explicitly. For example, input body height and resulting total height are not one-to-one.
- The bolt template exported geometry, but its report did not expose useful bbox/volume metrics.

### 2. `wjc9011/COMSOL_Multiphysics_MCP`

Status: MCP tool layer imports and registers successfully. After correcting the Windows COMSOL path, a real COMSOL 6.3 session can be started through `mph`.

What worked:

- Installed dependencies with `uv`.
- Imported `src.server` successfully.
- Registered tools/resources manually.
- Confirmed 79 tools and 1 resource are available.
- Queried documentation/knowledge tools:
  - `docs_list`
  - `physics_get_guide(electrostatics)`
  - `physics_get_guide(heat_transfer)`
  - `modeling_best_practices(geometry)`
  - `pdf_search_status`
- Confirmed failure mode is clean when no COMSOL session exists.
- Started a local COMSOL session with `mph.Client(cores=2, version="6.3")`.
- Confirmed session status: COMSOL `6.3`, standalone mode, 2 cores.
- Created a smoke-test empty model named `codex_smoke_model`.

Relevance to SSD enclosure:

- Directly relevant for electrostatic discharge / breakdown workflows and heat-transfer studies.
- The tool families we care about are present:
  - geometry import
  - electrostatics physics
  - heat transfer physics
  - meshing
  - studies
  - results export
  - documentation search

Limitations observed:

- COMSOL startup needs the actual Windows COMSOL bin path in the process environment, for example `D:\comsol\COMSOL63\Multiphysics\bin\win64`.
- Full STEP import, material assignment, meshing, electrostatics setup, and solve were not tested in this smoke run.
- The local PDF knowledge base dependencies are present, but the vector store was not built yet.
- One guide response referenced `physics_add_electrostatic`, while the registered tool name appears to be `physics_add_electrostatics`; this naming mismatch is worth checking later.

### 3. `NeonGlay/inventor-mcp`

Status: tool layer imports and lists tools; real Inventor connection fails because Inventor is not installed.

What worked:

- Installed dependencies with `uv`.
- Imported the MCP server module.
- Confirmed 36 tools are available.
- `status` reports that Inventor is not connected.

What failed:

- `connect(visible=False)` failed with a Windows COM class error because Inventor is not installed/registered.

Relevance:

- Very useful as an architectural reference.
- Strong ideas to reuse:
  - transactions
  - topology helpers
  - face/edge listing
  - operation-level feedback
  - export tools
  - sheet-metal tools

### 4. `ghbalf/freecad-ai`

Status: cloned and inspected only; not installed into FreeCAD.

Why it matters:

- This is closer to a FreeCAD AI workbench than a thin headless MCP bridge.
- It contains reusable skills and validation logic.
- The `enclosure` skill is especially relevant to our SSD enclosure work because it explicitly discusses electronics enclosures, lids, screw posts, snap-fit concepts, and validation.

Reason not installed yet:

- Installing it would modify the user-level FreeCAD environment.
- Current FreeCAD MCP/RPC state is not fully stable, so installation should be a separate controlled test.

### 5. `mikan-atomoki/text-to-model`

Status: Fusion 360 is not installed, but local mock introspection works.

What worked:

- Used the bundled `adsk_mock.py` to register tools without Fusion 360.
- Confirmed 65 tools are exposed.

Notable tools:

- `export_step`
- `export_stl`
- `create_jis_bolt`
- `create_jis_nut`
- `create_jis_screw`
- `create_jis_washer`
- `create_threaded_hole`
- `create_counterbore_hole`
- `create_countersink_hole`
- `create_bearing_hole`
- `import_svg`
- `import_dxf`

Relevance:

- Very relevant to the "standard part selection" direction.
- It proves that another project is already exposing standard fastener and standard hole operations as CAD-agent tools.
- Real geometry execution requires Fusion 360.

### 6. `hedless/onshape-mcp`

Status: tool layer can be listed locally; no remote Onshape mutation was performed.

What worked:

- Imported the local server with dummy credentials for safe tool-list inspection.
- Confirmed 47 tools are available.

Relevant tools:

- assembly creation
- assembly instance insertion
- mates
- bounding boxes
- Part Studio / Assembly export
- assembly interference check
- assembly positions
- instance positioning
- face coordinate systems
- body details

Relevance:

- This is closer to the API-driven CAD direction we originally wanted from Onshape.
- The assembly-position and interference tools are directly relevant to our repeated enclosure and PC-case alignment problems.

Limitations:

- Real operations require valid Onshape API credentials and should be tested on a throwaway document first.
- Several tools use inches, which is risky for our millimeter-first workflow unless wrapped.

### 7. Existing `neka-nat/freecad-mcp` State

Status: installed previously, but RPC connection was not alive during this run.

What happened:

- The Codex MCP tool surfaced, but `list_documents` failed with connection refused on `localhost:9875`.
- A headless FreeCADCmd launch hit a GUI-workbench issue in the installed FreeCAD MCP workbench.
- A GUI FreeCAD launch did not bring the RPC port up during this smoke test.

Relevance:

- Still valuable because previous tests proved basic `execute_code`, STEP export, object listing, and view capture can work when the RPC server is alive.
- Current blocker is environment/RPC lifecycle, not the idea itself.

## Practical Ranking For Our Current Work

1. `COMSOL_Multiphysics_MCP`: highest relevance to electrostatic and thermal simulation; local COMSOL 6.3 startup is now confirmed.
2. `onshape-mcp`: strongest candidate for cloud CAD assembly/interference workflows, but needs millimeter wrappers and safe test documents.
3. `fcgen-mcp`: best architecture reference for constrained template-driven generation.
4. `text-to-model`: best reference for standard fasteners and CAD standard-part tools.
5. `freecad-ai`: best reference for skill packaging and validation in a FreeCAD UI workflow.
6. `inventor-mcp`: strong architecture reference, but unusable here without Inventor.
7. `neka-nat/freecad-mcp`: still useful, but local RPC launch needs cleanup.

## SSD Enclosure Takeaways

- No single MCP currently solves the full workflow.
- The most promising combined route is:
  1. generate/model with build123d/FreeCAD-style code,
  2. inspect part count, bbox, wall continuity, connector opening, and fit gaps,
  3. export STEP,
  4. import into COMSOL for electrostatic or thermal study,
  5. use structured failures to drive geometry revision.
- The missing tool layer is not just "CAD generation"; it is repeatable assembly/fit validation:
  - expected part count,
  - bbox ranges,
  - no unexpected gaps at enclosure lips,
  - connector cutout shape/position checks,
  - screw/boss alignment,
  - material assignment readiness for simulation.

## Next Actions

- Continue the SSD enclosure COMSOL workflow with real STEP import, domain mapping, materials, boundary conditions, mesh, solve, and result extraction.
- Add a local SSD-enclosure validation script that checks part count, rough bbox, screw-hole alignment, cover/base overlap, and Type-C cutout sanity.
- Keep `fcgen-mcp` and `text-to-model` as references for future standard-part and template-based tools.
- Test `onshape-mcp` only on a disposable Onshape document, and wrap inch-based assembly tools into millimeter-first helpers before serious use.

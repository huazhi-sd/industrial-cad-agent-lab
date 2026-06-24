# AI CAD Project Watch - 2026-06-24

## Context

New-week scan for practical AI + industrial CAD/CAE work. Focus areas:

- CAD MCP servers and CAD agent tooling.
- COMSOL / FreeCAD / build123d automation.
- STEP-first workflows and standard-part libraries.
- Verification loops that can reduce agent CAD mistakes.

## High-Priority Updates

### build123d-mcp moved fast after our Windows/Codex issue

Project: <https://github.com/pzfreo/build123d-mcp>

Our issue is now closed:

- <https://github.com/pzfreo/build123d-mcp/issues/143>

Current package check:

- PyPI latest observed version: `0.3.57`
- The old failing test was on `0.3.28`.
- The README now explicitly mentions the Windows/sandboxed-host failure mode and recommends `--in-process` / `BUILD123D_IN_PROCESS=1` when every `execute()` fails with worker startup timeout.

Why it matters:

- This is a direct example that our test reports are useful to upstream projects.
- The tool has grown from "execute + render" into a stronger CAD inspection layer:
  - `measure`
  - `clearance`
  - `cross_sections`
  - `find_holes`
  - `find_bosses`
  - `shape_compare`
  - `align_check`
  - `import_cad_file`
  - `render_view`
  - drafting helpers
  - `bd_warehouse` fastener resource

Suggested next action:

- Retest `build123d-mcp 0.3.57` in Codex with `--in-process`.
- Use it specifically on our SSD enclosure or PC-case assembly for:
  - part count sanity,
  - bbox sanity,
  - clearance checks,
  - hole/boss recognition,
  - fastener/standard-part workflow exploration.

### step.parts is now directly relevant to our standard-parts direction

Project: <https://github.com/earthtojake/step.parts>

Observed signal:

- The catalog now advertises `16,000+` open-source STEP parts.
- It includes a public API under `https://api.step.parts/v1`.
- The catalog includes fasteners, washers, pins, spacers, standoffs, threaded parts, electronics modules, connectors, heatsinks, and fans.
- It also ships a `skills/step-parts` Codex skill, which is already aligned with our "standard part selection" direction.

Why it matters:

- This reduces the need to manually model common screws, standoffs, connectors, fans, and heatsinks.
- It can become a data source for a future `standard-part-selection-mcp`.
- The contribution workflow is clear: add catalog metadata + canonical STEP + validation checks through PRs.

Suggested next action:

- Use `step.parts` before we manually model any purchasable part.
- Build a small local test:
  - query `#6-32`, `M2`, `M2.5`, standoff, Type-C connector, 2280 screw;
  - download candidate STEP;
  - inspect bbox and orientation;
  - document whether the part is usable in real assemblies.

## Existing Projects Checked

| Project | Status | Signal |
| --- | --- | --- |
| [pzfreo/build123d-mcp](https://github.com/pzfreo/build123d-mcp) | Very active | Latest observed package version `0.3.57`; our Windows/Codex issue closed; now includes `--in-process` guidance and richer inspection tools. |
| [earthtojake/step.parts](https://github.com/earthtojake/step.parts) | High value | 16,000+ open-source STEP parts; public API; directly supports standard-part selection. |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | Active | Our STEP import/export feature request remains open; another open issue on Jun 22 reports UI wait-cursor blinking while RPC server is running. |
| [ghbalf/freecad-ai](https://github.com/ghbalf/freecad-ai) | Active alpha | FreeCAD-native AI assistant workbench; recently visible in search as updated/published yesterday; good reference for "CAD assistant as product". |
| [wjc9011/COMSOL_Multiphysics_MCP](https://github.com/wjc9011/COMSOL_Multiphysics_MCP) | Relevant | Still the main public COMSOL MCP reference; covers model management, geometry, physics, mesh, study, results, and PDF knowledge-base integration. |
| [ReshefElisha/jarvis-onshape-mcp](https://github.com/ReshefElisha/jarvis-onshape-mcp) | Reference only | Still a strong Onshape agent reference, especially structured mutation results and visual feedback. |
| [altendky/onshape-mcp](https://github.com/altendky/onshape-mcp) | Newly notable | Search results show it as a recently published Onshape MCP helper focused on assistant-driven API calls. |
| [hedless/onshape-mcp](https://github.com/hedless/onshape-mcp) | Reference only | Broad Onshape REST API MCP, with document discovery and project navigation direction. |
| [am-will/onshape-cli](https://github.com/am-will/onshape-cli) | Watch | CLI rather than MCP; useful as an Onshape API contract/reference for agents. |
| [sandraschi/freecad-mcp](https://github.com/sandraschi/freecad-mcp) | Watch | FreeCAD MCP + web dashboard direction, including file conversion and fluid-simulation UI ideas. |
| [spkane/freecad-addon-robust-mcp-server](https://github.com/spkane/freecad-addon-robust-mcp-server) | Watch | Large FreeCAD MCP tool surface with GUI/headless support; may be worth a later smoke test. |

## Notes On Direction

### Onshape is no longer the main route

Onshape MCP projects are still useful as API/agent references, but our current practical path is more STEP-first:

1. Generate or edit geometry locally.
2. Export STEP.
3. Inspect / validate with FreeCAD, build123d, or custom tools.
4. Import into COMSOL for simulation where needed.
5. Use catalog STEP parts instead of hand-modeling common standard parts.

Onshape remains a possible cloud CAD backend, not the center of the lab.

### Standard-part selection is becoming more realistic

The combination of:

- `step.parts`,
- `bd_warehouse`,
- build123d-mcp `bd_warehouse` resources,
- local STEP inspection,
- and FreeCAD/COMSOL validation

makes a small "standard-part selection agent layer" more realistic than it looked one week ago.

Near-term MVP:

1. User gives design need, e.g. "M.2 2280 board screw and standoff".
2. Agent searches catalog/library candidates.
3. Agent returns candidate part numbers/specs, STEP source, bbox, fit notes, and uncertainty.
4. Agent only generates placeholder geometry when no catalog part is available.

### Verification loops are still the most valuable gap

The recurring mistakes in our projects are not only modeling mistakes. They are missing verification gates:

- wrong handedness,
- wrong datum/front definition,
- wrong part count,
- wrong mating gap,
- wrong connector or screw feature plane,
- shell/wall interference,
- assembly component explosion.

The most useful reusable tool for us is likely not a huge benchmark. It is a small rule-based verifier:

- expected part count,
- bbox ranges,
- named datum directions,
- key feature plane/side checks,
- clearance or interference checks,
- simple report in Markdown/JSON.

## Recommended Actions This Week

1. Retest `build123d-mcp 0.3.57` with `--in-process`.
2. Use `step.parts` on one real standard-part task, preferably SSD enclosure screw/standoff or PC-case screw.
3. Keep COMSOL work focused on STEP import, material/domain assignment, and electrostatic baseline automation.
4. Do not spend time on Onshape UI automation unless a specific Onshape-only feature is needed.
5. Convert our repeated assembly checks into a small reusable verifier rather than relying on visual review only.

## Sources

- <https://github.com/pzfreo/build123d-mcp>
- <https://github.com/pzfreo/build123d-mcp/issues/143>
- <https://github.com/earthtojake/step.parts>
- <https://github.com/neka-nat/freecad-mcp>
- <https://github.com/ghbalf/freecad-ai>
- <https://github.com/wjc9011/COMSOL_Multiphysics_MCP>
- <https://github.com/ReshefElisha/jarvis-onshape-mcp>
- <https://github.com/altendky/onshape-mcp>
- <https://github.com/hedless/onshape-mcp>
- <https://github.com/am-will/onshape-cli>
- <https://github.com/sandraschi/freecad-mcp>
- <https://github.com/spkane/freecad-addon-robust-mcp-server>

# AI CAD Project Watch - 2026-06-17

## Context

Daily scan after the PCB adapter side task was closed. The focus is still practical industrial CAD and simulation workflows: CAD agent tooling, FreeCAD/Inventor/COMSOL automation, standard-part selection, and verification loops.

## Existing Projects Checked

| Project | Status | Signal |
| --- | --- | --- |
| [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | Active | Latest observed release activity around `0.3.2`; still the strongest public "text-to-CAD skill" style project. |
| [pzfreo/build123d-mcp](https://github.com/pzfreo/build123d-mcp) | Active but small | Latest observed push on 2026-06-14. Our Windows/Codex worker issue is closed; useful as a local build123d MCP testbed. |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | Active | Our STEP import/export wrapper feature request remains open. Still useful as a FreeCAD automation bridge. |
| [w1ne/kernelCAD-web](https://github.com/w1ne/kernelCAD-web) | Active | Local clone shows many agent-facing skills, validators, kinematic tools, and MCP tools. Still important as a "CAD kernel + agent tooling" reference. |
| [wjc9011/COMSOL_Multiphysics_MCP](https://github.com/wjc9011/COMSOL_Multiphysics_MCP) | Active | Most relevant public COMSOL MCP candidate. Recent push observed on 2026-06-16. |

## Newly Notable Projects

### [ghbalf/freecad-ai](https://github.com/ghbalf/freecad-ai)

An AI assistant workbench inside FreeCAD. More application-like than `freecad-mcp`: chat UI, Plan/Act modes, structured FreeCAD operations, skills, hooks, tool reranking, file attachments, vision routing, session resume, many LLM providers, and error self-correction.

Why it matters:

- It is closer to a "human CAD user + AI assistant" product than a thin MCP bridge.
- The skill optimizer and user extension tools match our long-term direction: reusable industrial CAD skills rather than one-off scripts.
- It may be a strong reference for how to package our own workflows.

Suggested next action:

- Install or inspect it locally only after current COMSOL baseline work is stable.
- Compare its tool model with `neka-nat/freecad-mcp`: UI workbench vs headless MCP bridge.

### [kouya-group/fcgen-mcp](https://github.com/kouya-group/fcgen-mcp)

A FreeCAD MCP server built around verified parametric templates instead of unconstrained generated scripts.

Why it matters:

- This directly supports our current idea: standards-based, constrained generation for industrial parts.
- Its "template + JSON Schema + semantic validation" pattern is likely safer for standard parts than pure code generation.
- This may be the best architectural reference for `standard-part-selection-mcp`.

Suggested next action:

- Study its template format.
- Prototype one template family in our lab: screw/standoff/PCB fastener selection.

### [NeonGlay/inventor-mcp](https://github.com/NeonGlay/inventor-mcp)

An Autodesk Inventor MCP using the Inventor COM API. It exposes high-level millimeter-based tools, parametric sketches/features, topology helpers, feature-operation reporting, transactions, and an `execute_python` escape hatch.

Why it matters:

- The architecture maps well to industrial desktop CAD: COM API, transactions, topology deltas, and parametric discipline.
- The "feature operation returns volume/topology delta" idea is exactly the kind of self-verification loop we need.
- Even if we do not use Inventor, this is a reference for Creo/COMSOL-style API wrapper design.

Suggested next action:

- Read its tool list and reporting format.
- Borrow the idea of operation-level structured feedback for our COMSOL and CAD validation wrappers.

### [Greenmint-labs/greenloom_CAD_MCP](https://github.com/Greenmint-labs/greenloom_CAD_MCP)

AutoCAD LT / DXF-oriented MCP with both AutoCAD IPC and headless `ezdxf` backends.

Why it matters:

- Less relevant to 3D product design, but useful for drawing/DXF automation.
- The dual-backend idea may apply to us: real CAD backend when installed, lightweight headless backend for simple review/export.

### [mikan-atomoki/text-to-model](https://github.com/mikan-atomoki/text-to-model)

Fusion 360 MCP-style project with standard-parts direction, including JIS-related examples.

Why it matters:

- It confirms that "standard parts through CAD agent tooling" is not an isolated idea.
- It is worth reviewing before we design our own standard-part-selection layer.

## COMSOL Direction

The COMSOL public ecosystem is still thin compared with CAD generation, but there are multiple emerging MCP wrappers:

- [wjc9011/COMSOL_Multiphysics_MCP](https://github.com/wjc9011/COMSOL_Multiphysics_MCP)
- [Suzy-Sa/COMSOL-Multiphysics-MCP](https://github.com/Suzy-Sa/COMSOL-Multiphysics-MCP)
- [Zhangyoupeng1996/Codex_MCP_Comsol](https://github.com/Zhangyoupeng1996/Codex_MCP_Comsol)
- [MPh-py/MPh](https://github.com/MPh-py/MPh), a mature Python wrapper around COMSOL Java API, still worth keeping in the toolbox.

Near-term COMSOL work should continue to focus on:

- repeatable Java API baseline scripts,
- direct STEP import inspection,
- material/domain mapping,
- electrostatic sanity checks,
- and reportable outputs that are useful for job hunting and portfolio evidence.

## Takeaways

1. The most useful new reference today is `freecad-ai`: it shows how a CAD assistant can become a product, not just a script runner.
2. The most relevant architecture for our standard-parts idea is `fcgen-mcp`: template-driven generation with schema and semantic validation.
3. The most relevant architecture for industrial CAD API wrappers is `inventor-mcp`: structured tools, transactions, topology helpers, and operation deltas.
4. COMSOL automation remains valuable for career positioning, but our own immediate advantage is building small repeatable workflows rather than waiting for a mature public COMSOL agent ecosystem.

## Proposed Next Step

Continue the COMSOL simulation workflow, then reserve a short separate session for `fcgen-mcp` study because it is directly connected to the `standard-part-selection-mcp` idea.

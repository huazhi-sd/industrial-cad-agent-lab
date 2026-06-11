# AI CAD Project Watch - 2026-06-11

## Scope

Daily scan for agent-assisted industrial CAD, CAD MCP servers, code-first CAD workflows, COMSOL automation, and standard-part/STEP inspection tooling.

## High-Signal Updates

### pzfreo/build123d-mcp

- Repo: https://github.com/pzfreo/build123d-mcp
- Latest release: `v0.3.46`, published 2026-06-10.
- Relevant change: added `--in-process` fallback for MCP hosts that block subprocess creation.
- Local result: verified on Windows Codex. `execute()`, STEP export, PNG/SVG rendering, `health_check`, and a minimal `with BuildPart()` example now work.
- Why it matters: this removes the main blocker we hit with Codex + Windows and makes build123d-mcp usable as a real interactive CAD loop.

### w1ne/kernelCAD-web

- Repo: https://github.com/w1ne/kernelCAD-web
- Latest release: `v0.12.0`, published 2026-06-09.
- Key release themes:
  - Agent animation toolset.
  - Print-readiness DFM suite.
  - STEP inspection with solid tree, exact bbox/volume, and cylindrical-hole detection.
  - Interop exports: DXF, 3MF, GLB, plus robotics formats.
  - Generation-loop tightening with typed feedback and closed-loop repair.
  - New `spring()` primitive and smoother sweep support.
- Why it matters: the STEP inspection and DFM checks overlap strongly with our own direction: part count checks, bbox checks, feature-plane checks, and compatibility validation.
- Suggested action: keep watching; test the newest release only if we want to compare its inspection output with our FreeCAD/build123d wrappers.

### ghbalf/freecad-ai

- Repo: https://github.com/ghbalf/freecad-ai
- Latest release: `v0.16.3-alpha`, published 2026-06-07.
- Project type: FreeCAD AI workbench, not just an MCP bridge.
- Notable features from README: chat UI, Plan/Act modes, structured FreeCAD tool calling, skills, hooks, file attachments, viewport screenshots, AGENTS.md support, multiple LLM providers.
- Latest fix focus: headless sandbox false positives around empty sketches and GUI view-framing calls.
- Why it matters: this is close to the "AI inside CAD GUI" route we discussed, but with stronger FreeCAD-native UX than a plain MCP server.
- Suggested action: medium priority. Install only after current FreeCAD MCP wrapper work is stable.

### sandraschi/freecad-mcp

- Repo: https://github.com/sandraschi/freecad-mcp
- Project type: FastMCP server + webapp for FreeCAD, OpenFOAM, FluidX3D, slicing, and model search.
- Claimed scope: 46 tools, FreeCAD geometry, STEP/STL conversion, IFC/BIM, FEM via CalculiX, fluid simulation via OpenFOAM/FluidX3D, 3D printing, marketplace search.
- Why it matters: this is the most ambitious FreeCAD+simulation MCP candidate found today. The CFD/FluidX3D angle is relevant to our future liquid-cooling cabinet direction.
- Risk: very broad scope, very low stars, likely rough. Treat as exploratory, not a dependable production base.
- Suggested action: low-to-medium priority smoke test later: start server, run STEP inspection/conversion, then inspect any CFD pipeline assumptions.

### KoStard/forgecad-public-kit

- Repo: https://github.com/KoStard/forgecad-public-kit
- Project type: public companion kit for ForgeCAD.
- Relevant capabilities:
  - Code-first `.forge.js` CAD.
  - CLI validation, rendering, collision inspection, STEP/STL export, parameter sweeps.
  - Public agent skills installable for Codex with `forgecad skill install --target codex`.
  - Workflow loop: agent edits code -> `forgecad run` -> `forgecad inspect` -> iterate.
- Why it matters: this is very aligned with our "agent CAD requires evidence, inspection, and iteration" direction.
- Caveat: hosted app/core source are external; public kit is the entry point, not the full platform.
- Suggested action: high priority if we want a new demo after COMSOL baseline. Test skill install + one example model + STEP export.

## COMSOL / Simulation Watch

### wjc9011/COMSOL_Multiphysics_MCP

- Repo: https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- Stars: about 400.
- Last code push checked: 2026-05-14.
- Status: still the most visible COMSOL MCP project, but no fresh code movement today.
- Suggested action: continue our own COMSOL baseline wrapper; use this repo mainly for comparison.

### MPh-py/MPh

- Repo: https://github.com/MPh-py/MPh
- Project type: Pythonic scripting wrapper around COMSOL through JPype/Java bridge.
- Recent relevant commit: linked COMSOL API docs from `.java` attribute docstrings.
- Why it matters: not MCP, but may be a stronger backend layer for Python-first COMSOL automation than writing raw Java every time.
- Suggested action: evaluate after we finish baseline Java wrapper docs. Main question: licensing/runtime compatibility on this workstation.

### 777gegewu/comsol-mcp

- Repo: https://github.com/777gegewu/comsol-mcp
- Project type: unofficial COMSOL MCP learning project using Java Shell to control an already-open COMSOL Desktop GUI.
- Last code push checked: 2026-05-13.
- Why it matters: closer to GUI-attached COMSOL automation than our current batch Java wrapper.
- Suggested action: watch only for now. Our batch wrapper is cleaner and easier to document.

### HZ-KMNO/comsol-project-guardrails

- Repo: https://github.com/HZ-KMNO/comsol-project-guardrails
- Project type: vendor-neutral guardrails/skills for COMSOL automation.
- Last code push checked: 2026-06-05.
- Why it matters: conceptually overlaps with our own "simulation baseline wrapper + manifest + cleanup + report" direction.
- Suggested action: inspect later for prompt/guardrail structure, not runtime tooling.

## Other Noted Projects

### cyberchitta/cad-khana

- Repo: https://github.com/cyberchitta/cad-khana
- Project type: diagnostics-first Build123d wrapper and Claude Code skill for LLM-driven CAD iteration.
- Status: no very recent update, but direction remains relevant.
- Suggested action: keep as reference for diagnostics-first design, especially if we build our own validator layer.

### mikan-atomoki/text-to-model

- Repo: https://github.com/mikan-atomoki/text-to-model
- Project type: Fusion 360 MCP add-in with many CAD tools.
- Status: not recently active.
- Suggested action: observe only. Not our current stack.

## Recommended Next Actions

1. Update the build123d-mcp issue with the short confirmation that `v0.3.46 --in-process` works in Windows Codex.
2. Continue COMSOL baseline wrapper work; it is now our strongest "traditional engineering + AI automation" track.
3. Next new demo candidate: ForgeCAD public kit, because it has Codex-targeted skills, validation, rendering, STEP export, and inspection commands.
4. Later exploratory candidate: ghbalf/freecad-ai, because it represents the "AI workbench inside CAD" route.
5. Keep sandraschi/freecad-mcp in the watchlist for CFD/OpenFOAM/FluidX3D ideas, but do not rely on it yet.

## Sources

- https://github.com/pzfreo/build123d-mcp
- https://github.com/pzfreo/build123d-mcp/releases/tag/v0.3.46
- https://github.com/w1ne/kernelCAD-web
- https://github.com/w1ne/kernelCAD-web/releases/tag/v0.12.0
- https://github.com/ghbalf/freecad-ai
- https://github.com/ghbalf/freecad-ai/releases/tag/v0.16.3-alpha
- https://github.com/sandraschi/freecad-mcp
- https://github.com/KoStard/forgecad-public-kit
- https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- https://github.com/MPh-py/MPh
- https://github.com/777gegewu/comsol-mcp
- https://github.com/HZ-KMNO/comsol-project-guardrails
- https://github.com/cyberchitta/cad-khana
- https://github.com/mikan-atomoki/text-to-model

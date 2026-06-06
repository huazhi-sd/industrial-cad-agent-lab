# AI CAD Project Watch - 2026-06-06

## Scope

Three-day follow-up scan for agent + CAD / CAE projects after the 2026-06-03 watch log.

Focus areas:

- CAD skills and STEP-first agent workflows;
- FreeCAD / build123d / OpenCASCADE automation;
- COMSOL and simulation automation;
- standard part selection / engineering-grade CAD model sourcing;
- new CAE bridges that may matter for thermal/CFD/meshing later.

## High-Signal Updates

### earthtojake/text-to-cad / CAD Skills

- Repo: https://github.com/earthtojake/text-to-cad
- GitHub page now shows about 5.7k stars and 670 forks.
- Latest visible release: `0.2.1`, dated 2026-06-04.
- README positioning is now broader than "text-to-CAD": CAD Skills is described as a library of agent skills for CAD, robotics, and hardware design.
- Listed skills include CAD, CAD Viewer, step.parts, URDF, SRDF, SDF, SendCutSend, G-code, and Bambu Labs.

Assessment:

- This is no longer just a toy CAD generator. It is becoming an agent skill suite around engineering artifacts.
- The `step.parts` skill directly overlaps with our standard part direction, but only as a sourcing skill.
- Our opportunity remains downstream of sourcing:
  - engineering-grade model quality checks;
  - STEP vs mesh usability grading;
  - standard part selection rationale;
  - fallback clean STEP generation.

Action:

- Keep watching releases.
- Do not write another long generic comment on issue #41.
- If replying, keep it short and contributor-oriented.

### pzfreo/build123d-mcp

- Repo: https://github.com/pzfreo/build123d-mcp
- GitHub page shows 6 stars, 2 forks, 200 commits.
- Latest visible release: `v0.3.34`, dated 2026-06-04.
- README explicitly notes startup with `uvx build123d-mcp --upgrade`, so clients do not remain pinned to an older cached version.

Assessment:

- Fast-moving despite low star count.
- The project has turned into one of the most active MCP-native build123d experiments.
- Our earlier Windows/Codex test reports are still relevant because the project is release-heavy and likely to benefit from stable Windows feedback.

Action:

- Retest only when there is a reason, not every day.
- If retesting, use `--upgrade` or explicit version pinning so the tested version is unambiguous.

### neka-nat/freecad-mcp

- Repo: https://github.com/neka-nat/freecad-mcp
- GitHub page shows about 1.1k stars and 172 forks.
- Open issues/pull requests remain active.

Assessment:

- Still the most practical FreeCAD automation bridge we have tested.
- No new high-signal maintainer response observed for our STEP import/export + metrics feature request during this scan.
- It remains useful as a real local FreeCAD bridge, but our immediate value is likely a wrapper/tool layer rather than waiting for upstream.

Action:

- Continue using our local inspection wrapper direction.
- Keep issue #66 as a public signal of industrial STEP workflow needs.

### ghbalf/freecad-ai

- Repo: https://github.com/ghbalf/freecad-ai
- Latest visible release: `v0.16.0-alpha - datum geometry + transform/duplicate suite`, dated 2026-06-03.

Assessment:

- This update is especially relevant to our repeated orientation/handedness problems.
- Datum geometry and transform tooling are exactly where CAD agents need stronger guardrails.

Action:

- Medium-priority test candidate.
- If tested, design a simple orientation/handedness benchmark rather than a freeform modeling prompt.

### wjc9011/COMSOL_Multiphysics_MCP

- Repo: https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- GitHub page still shows a small commit history but a broad tool surface.
- README lists `80+` tools, including session, model, parameter, geometry, and other COMSOL operations.
- Example model directories include thermal and micromixer-related models.

Assessment:

- This remains the most direct COMSOL MCP candidate.
- The project is useful to study even if we do not rely on it immediately, because our local COMSOL automation can also use Java API or MPh.

Action:

- Resume from the existing magnetostatic project before trying thermal/CFD.
- Compare this MCP against direct COMSOL Java scripts and MPh after the local baseline is restored.

### MPh-py/MPh

- Repo: https://github.com/MPh-py/MPh
- MPh wraps the COMSOL Java API through JPype and covers common scripting tasks: loading models, modifying parameters, importing data, running simulations, evaluating results, and exporting outputs.

Assessment:

- More mature than most COMSOL MCP wrappers.
- It should be treated as a stable fallback path for Python-driven COMSOL automation.

Action:

- Keep as a serious candidate for our COMSOL learning line.
- Prefer MPh for controlled scripts if MCP behavior is unstable.

## New / Newly Important Candidate

### gnshb/salome-mcp

- Repo: https://github.com/gnshb/salome-mcp
- Positioning: Model Context Protocol bridge for SALOME.
- Components:
  - SALOME GUI plugin;
  - SALOME-side bridge for GEOM/SMESH operations;
  - MCP server for agent clients.
- Tool coverage includes:
  - geometry creation and transforms;
  - boolean operations;
  - surface/volume group creation;
  - geometry import/export;
  - mesh import/export;
  - mesh creation and statistics;
  - raw SALOME Python execution.

Assessment:

- This is very relevant to the future thermal/CFD direction.
- SALOME is closer to CAE preprocessing and meshing than FreeCAD.
- It may become important if we move from CAD shape generation into CFD/FEA preprocessing.

Action:

- Add to the watch list.
- Do not test immediately unless COMSOL/thermal work specifically needs meshing/CFD preprocessing.

## Standard Part / Engineering Model Quality Direction

Recent observation from the vendor-provided PCB OBJ case:

- A visually previewable OBJ can be useless for engineering CAD.
- The sample OBJ was not watertight, had many open edges, and included a zero-thickness PCB surface.
- This supports our standard part/model sourcing thesis:

```text
The useful tool is not just "find a 3D model".
The useful tool is "grade whether this model is engineering-usable, and produce a clean fallback when it is not".
```

External trend signal:

- CadShift discussed SolidWorks 2026 AI features such as AI fastener recognition and design inspection.
- This suggests large CAD vendors are moving toward model-aware standard hardware and inspection, but mostly inside proprietary CAD systems.

Opportunity:

- An open agent-facing engineering standard part selection and validation bridge remains valuable.
- Our niche should be:
  - part requirement parsing;
  - source lookup;
  - engineering usability grading;
  - clean STEP fallback generation;
  - validation report.

## Priority Recommendation

For the next few days:

1. Resume COMSOL automation from the old magnetostatic project.
2. Keep the standard part/model quality direction alive, using the PCB OBJ failure as a concrete case.
3. Watch `salome-mcp`, but do not start a new SALOME thread yet.
4. Avoid spending too much time on generic new CAD demos unless they directly improve employment, COMSOL, or standard part workflows.

## Sources

- https://github.com/earthtojake/text-to-cad
- https://github.com/pzfreo/build123d-mcp
- https://github.com/neka-nat/freecad-mcp
- https://github.com/ghbalf/freecad-ai
- https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- https://github.com/MPh-py/MPh
- https://github.com/gnshb/salome-mcp
- https://cadshift.com/blog/ai-cad-tools-vs-workflow-automation/

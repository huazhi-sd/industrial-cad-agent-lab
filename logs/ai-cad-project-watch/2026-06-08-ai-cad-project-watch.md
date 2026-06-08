# AI CAD Project Watch - 2026-06-08

## Scope

Follow-up scan for agent + CAD / CAE projects after the COMSOL baseline work.

Focus areas:

- CAD agent skills and MCP-native CAD tools;
- FreeCAD / build123d / OpenCASCADE automation;
- COMSOL and simulation automation;
- standard part sourcing and selection;
- CAD benchmark projects that may help us define validation gates.

## High-Signal Updates

### earthtojake/text-to-cad / CAD Skills

- Repo: https://github.com/earthtojake/text-to-cad
- GitHub API snapshot:
  - stars: 5,785
  - forks: 689
  - latest release: `0.2.2`
  - release date: 2026-06-07
  - latest main commit: `Publish 0.2.2 from develop to main`
- Relevant issue:
  - `#41 Can it be integrated with freeacd?`
  - State: open
  - Last maintainer reply remains: "Could you elaborate on what kind of support you'd want to be added for FreeCAD?"

Assessment:

- CAD Skills is still the fastest-moving public skill-suite direction.
- The ecosystem now includes `step.parts`, which overlaps with our standard-part direction as a sourcing layer.
- Our best contribution should stay downstream:
  - model quality checks;
  - standard-part selection rationale;
  - manufacturability-aware validation;
  - agent-friendly failure reports.

Action:

- Do not send another long generic reply.
- If replying to issue #41, keep it short and human:
  - Windows + Codex + FreeCAD/STEP workflow;
  - useful first scope: import/export/inspect/render bridge;
  - offer to test a small concrete PR.

### pzfreo/build123d-mcp

- Repo: https://github.com/pzfreo/build123d-mcp
- GitHub API snapshot:
  - stars: 8
  - forks: 2
  - latest release: `v0.3.38`
  - release date: 2026-06-07
  - latest commit: `Add per-version Python trove classifiers (3.10-3.12) (#178)` on 2026-06-08
- Relevant issue:
  - `#143 Windows + Codex MCP host: execute fails...`
  - State: open
  - No maintainer reply after our diagnostic follow-up.

Assessment:

- Still very active despite small public visibility.
- The project continues to refine packaging/version compatibility.
- It is worth retesting only when a release explicitly touches Windows worker execution, MCP stdio, or process startup.

Action:

- No immediate retest today.
- Keep our Windows/Codex issue precise and reproducible.

### jdilla1277/agentcad

- Site: https://agentcad.dev/
- Repo: https://github.com/jdilla1277/agentcad
- GitHub API snapshot:
  - stars: 3
  - forks: 0
  - latest release: `v0.2.4`
  - release date: 2026-06-02
  - latest commit message: `Refresh runtime docs for build123d default (#3)`

Assessment:

- Public site positioning is strong: "CAD tool for AI agents", with CLI, MCP, versioned outputs, metrics, render, inspect, diff.
- We already proved it can run useful small CAD loops locally, but we hit Windows daemon issues and reported them.
- It is still more immediately useful as a workflow pattern than as our main production CAD backend.

Action:

- Keep using AgentCAD concepts:
  - versioned runs;
  - metrics after every run;
  - render/inspect/diff loops.
- Do not depend on it as the only backend until Windows daemon behavior is cleaner.

### w1ne/kernelCAD-web

- Repo: https://github.com/w1ne/kernelCAD-web
- GitHub API snapshot:
  - stars: 5
  - forks: 0
  - latest release: `v0.11.1`
  - latest commit: `feat(studio): quarter/octant cutaway section tool (#409)` on 2026-06-08
- Our issue:
  - `#362 Windows CLI wasm path becomes D:\D:\...`
  - State: open
  - No maintainer reply yet.

Assessment:

- The new cutaway-section work is relevant to industrial CAD review because section/cutaway views are exactly how engineers inspect hidden layout relationships.
- This is not our highest-priority backend, but it is worth watching as a browser-native CAD viewer/editor experiment.

Action:

- Retest later only if Windows CLI/wasm path handling changes.
- Watch cutaway/section tooling because it overlaps with our repeated "hide shell / left view / internal layout" work.

### neka-nat/freecad-mcp

- Repo: https://github.com/neka-nat/freecad-mcp
- GitHub API snapshot:
  - stars: 1,075
  - forks: 171
  - latest commit remains 2026-05-29: `Merge pull request #63 ... add-reload-document-tool`
- Our issue:
  - `#66 Feature request: STEP import/export and solid metrics tools for industrial CAD workflows`
  - State: open
  - No maintainer reply yet.

Assessment:

- No new upstream movement since the last scan.
- Still useful as a local FreeCAD bridge.
- Our wrapper/tool-layer direction remains the right path.

Action:

- Continue local wrappers instead of waiting for upstream.
- If we contribute, keep the scope small: typed STEP import/export, object listing, bbox/solid metrics, view export.

### COMSOL automation projects

Projects checked:

- https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- https://github.com/Ching-Chiang/comsol-mcp
- https://github.com/MPh-py/MPh

GitHub API snapshot:

- `wjc9011/COMSOL_Multiphysics_MCP`
  - stars: 380
  - latest commit: 2026-05-14
- `Ching-Chiang/comsol-mcp`
  - stars: 8
  - latest commit: 2026-05-14
- `MPh-py/MPh`
  - stars: 532
  - latest commit: 2026-05-23
  - latest notable commit: links to COMSOL API docs from `.java` docstrings

Assessment:

- No fresh upstream movement today.
- Our local COMSOL baseline is now more concrete than most public demos for our actual use case:
  - inspect model structure;
  - evaluate existing results;
  - run controlled single-parameter solve.

Action:

- Next local step should be a small COMSOL wrapper interface, not another broad search.
- Keep watching `MPh` because it is a mature Python bridge and may reduce Java boilerplate later.

### step.parts

- Site: https://www.step.parts/
- Observed catalog size: 12,734 STEP parts.
- Examples include electronics boards, motors, fans, thermal pads, heat pipes, standoffs, ISO dowel pins, ISO 4762 screws, clearance-hole cylinders, and extrusion profiles.

Assessment:

- This is directly relevant to our standard-part direction.
- It is a sourcing/catalog layer, not a full engineering selection layer.
- Our opportunity remains:
  - choose the right standard part for a design constraint;
  - explain the standard and selection rationale;
  - verify the downloaded/generated STEP is usable as CAD, not just visually plausible.

Action:

- Use `step.parts` as one source in the future standard-part selection MCP.
- Add model quality grading and fallback clean STEP generation.

### CADCLAW / MARB

- Site: https://marb.cadclaw.io/
- Repo: https://github.com/sunnyday-technologies/CADCLAW
- GitHub API snapshot:
  - stars: 9
  - latest commit: 2026-06-07
- MARB positions itself as a mechanical assembly readiness benchmark:
  - checks whether parts are placed, aligned, collision-free, and not floating;
  - grades exported STEP independent of authoring tool;
  - maps benchmark levels to readiness concepts.

Assessment:

- This is highly relevant to our repeated failures around orientation, handedness, standoff spacing, GPU placement, and interface alignment.
- It validates our instinct that "part count, bbox, feature direction/plane, and compatibility checks" are more valuable than a huge generic benchmark.

Action:

- Do not build a full benchmark now.
- Borrow the concept:
  - L0 component validity;
  - L1 assembly alignment/no collision/no floating;
  - small black-box STEP validators for our own workflows.

### CAD benchmark landscape

Projects/sites noted:

- https://cadarena.dev/
- https://marb.cadclaw.io/
- https://dong7313.github.io/muse-benchmark/
- BenchCAD / CADBench / Text2CAD-Bench papers remain active in May-June 2026.

Assessment:

- The benchmark field is moving quickly.
- Most public benchmarks still focus on geometry generation, reconstruction, or prompt-to-CAD output quality.
- Our niche should remain industrial workflow validation rather than competing with large academic benchmarks.

Action:

- Keep benchmark work as a method source, not a primary project.
- Fold useful validation gates into `industrial-cad-validator` and future standard-part selection tooling.

## Issue Thread Status

| Repo | Issue | State | Last observed action |
| --- | --- | --- | --- |
| `earthtojake/text-to-cad` | `#41` | open | Maintainer asked what FreeCAD support should mean |
| `pzfreo/build123d-mcp` | `#143` | open | Our diagnostic follow-up is still latest |
| `neka-nat/freecad-mcp` | `#66` | open | No comments yet |
| `w1ne/kernelCAD-web` | `#362` | open | No comments yet |

## Recommended Next Moves

1. Build a small COMSOL wrapper around our three local baselines.
2. Start the standard-part selection project with a narrow fastener/standoff use case.
3. Add assembly validation concepts from CADCLAW/MARB into our validator notes.
4. Reply to `text-to-cad` issue #41 only if we can propose one concrete FreeCAD bridge scope.

## Sources

- https://github.com/earthtojake/text-to-cad
- https://github.com/pzfreo/build123d-mcp
- https://github.com/jdilla1277/agentcad
- https://agentcad.dev/
- https://github.com/neka-nat/freecad-mcp
- https://github.com/w1ne/kernelCAD-web
- https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- https://github.com/Ching-Chiang/comsol-mcp
- https://github.com/MPh-py/MPh
- https://www.step.parts/
- https://marb.cadclaw.io/
- https://cadarena.dev/

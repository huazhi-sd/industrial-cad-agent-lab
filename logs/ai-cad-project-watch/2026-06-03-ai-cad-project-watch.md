# AI CAD Project Watch - 2026-06-03

## Scope

Daily scan for agent + CAD / CAE projects relevant to:

- industrial CAD agent workflows;
- STEP import/export/inspection;
- FreeCAD / build123d / OpenCASCADE automation;
- COMSOL automation;
- engineering standard part selection.

## High-signal Updates

### earthtojake/text-to-cad

- Repo: https://github.com/earthtojake/text-to-cad
- Stars at scan time: 5,537
- Latest notable update: main branch has `Publish 0.2.1 from develop to main`.
- Active PR: `#53 [codex] Add viewer default workspace dir`
- Relevant issue: `#41 Can it be integrated with freeacd?`

Maintainer reply on issue #41:

> Could you elaborate on what kind of support you'd want to be added for FreeCAD?

Assessment:

- This is a useful opening, but the previous reply from our side was too generic and overly agent-like.
- Do not rush another long answer.
- Next response should be short, human, and contributor-oriented:
  - willing to help test;
  - Windows + Codex + FreeCAD/STEP workflow;
  - first useful scope: import/export/inspect/render bridge;
  - ask what small task would be preferred.

### pzfreo/build123d-mcp

- Repo: https://github.com/pzfreo/build123d-mcp
- Stars at scan time: 6
- Latest branch signal: bumped to `0.3.33.dev0` after release.
- Active PR: `#155 docs: add Claude Code skill for engineering drawings workflow`
- Relevant issue: `#143 Windows + Codex MCP host: execute fails...`

Assessment:

- This remains worth monitoring because it is close to our toolchain.
- Current issue thread still only has our diagnostic follow-up; no maintainer reply observed in this scan.
- The project is moving quickly despite low star count.
- Short-term value: keep Windows/Codex test reports precise and reproducible.

### neka-nat/freecad-mcp

- Repo: https://github.com/neka-nat/freecad-mcp
- Stars at scan time: 1,054
- Latest commit signal: merged `#63 add-reload-document-tool` on 2026-05-29.
- Relevant issue: `#66 Feature request: STEP import/export and solid metrics tools for industrial CAD workflows`

Assessment:

- No new maintainer reply observed on issue #66 today.
- Still one of the most practical bridges for FreeCAD automation.
- Our own `industrial-cad-validator` and FreeCAD inspection wrapper direction remains aligned with the missing typed STEP tools.

### ghbalf/freecad-ai

- Repo: https://github.com/ghbalf/freecad-ai
- Stars at scan time: 269
- Latest notable update: `v0.16.0-alpha - datum geometry + transform/duplicate suite (#18)`.

Assessment:

- This is relevant to CAD assistant behavior inside FreeCAD.
- Datum geometry and transform tools are directly related to our repeated orientation/handedness problems.
- Worth testing later, but not before FreeCAD MCP and our validator workflow are stable.

### w1ne/kernelCAD-web

- Repo: https://github.com/w1ne/kernelCAD-web
- Stars at scan time: 5
- Latest activity: rapid PR series around tendon-driven coil springs, collision-aware MuJoCo, and wrap routing.
- Active PRs observed:
  - `#373 P11 - collision-aware MuJoCo`
  - `#372 P11 Slice 3 - route Luxo springs over wrap rails`
  - `#371 P11 Slice 2 - tendon wrap-geom routing API`

Assessment:

- Still experimental, but technically interesting.
- Less aligned with industrial CAD selection/validation than FreeCAD/build123d/COMSOL.
- Keep as low-priority observation unless a concrete reproduction task appears.

### wjc9011/COMSOL_Multiphysics_MCP

- Repo: https://github.com/wjc9011/COMSOL_Multiphysics_MCP
- Stars at scan time: 337
- Latest commit observed: 2026-05-14, `Use dynamic star history chart`.

Assessment:

- No recent code activity today, but project is still important for our COMSOL agent line.
- Next action should be local trial against existing COMSOL 6.3 installation and the old magnetostatic project.

### MPh-py/MPh

- Repo: https://github.com/MPh-py/MPh
- Stars at scan time: 525
- Latest commit signal: documentation links to COMSOL API docs from `.java` attributes.

Assessment:

- More mature than the COMSOL MCP project as a Python-to-COMSOL automation base.
- Good fallback if the MCP wrapper is unstable.

### gumyr/build123d

- Repo: https://github.com/gumyr/build123d
- Stars at scan time: 2,390
- Notable active PR: `#1327 Add implicit fields: marching cubes + signed-distance fields (build123d.implicit)`
- Other active fixes: drafting dimension line crash and `Axis` construction improvements.

Assessment:

- Important upstream for build123d-based CAD skills.
- Implicit/SDF support could matter later for organic ducts, ergonomic shapes, or complex cooling geometry, but it is not immediate priority.

## New / Adjacent Projects To Keep On Radar

### HKUDS/CLI-Anything

- Repo: https://github.com/HKUDS/CLI-Anything
- Stars at scan time: 41,897
- Not CAD-specific, but very active in general agent-native CLI orchestration.

Assessment:

- Too broad for our immediate CAD work.
- Watch for reusable CLI harness ideas, not a direct CAD dependency.

### jupytercad/JupyterCAD

- Repo: https://github.com/jupytercad/JupyterCAD
- Stars at scan time: 226

Assessment:

- Interesting browser/Jupyter CAD direction.
- Current issues mention export and tree grouping limitations.
- Low priority for now.

## Project Direction Notes

The strongest month-level directions remain:

1. Run and document new agent + CAD / CAE demos.
2. Prototype an engineering standard part selection MCP.
3. Resume COMSOL automation from the existing magnetostatic project before attempting thermal-fluid simulation.

For the standard part direction, the likely valuable niche is not a new parts library. Mature libraries already exist. The useful gap is:

```text
engineering requirement
-> standard part recommendation
-> catalog/source lookup
-> STEP download or fallback generation
-> geometric validation
-> selection report
```

## Immediate Next Actions

- Fill 5-10 rows in the standard part Excel template with real PC case fasteners.
- Do not send another long reply to `text-to-cad` issue #41 yet.
- Prepare a short, human reply only if continuing that thread.
- Start the COMSOL line from the existing local magnetostatic project, not from thermal-fluid simulation.

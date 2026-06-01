# hardware-cad-agent-lab

Chinese manufacturing CAD skills and experiments for hardware CAD agents.

This repository starts from real structure-design work and small public CAD experiments. It is not tied to one CAD platform: current workflows use STEP, build123d/CadQuery-style scripts, CAD Viewer, AgentCAD, FreeCAD/Onshape MCP experiments, and GitHub-based process notes.

## Why this repo exists

General CAD agents can call APIs, but they often lack manufacturing judgement. This repo captures repeatable structure-design workflows as small skills, scripts, examples, and review notes:

- Generate mechanical parts from engineering parameters.
- Repair or replace imported STEP parts with cleaner geometry.
- Keep geometry decisions explainable for engineers, reviewers, and suppliers.
- Avoid storing API keys or company-sensitive model files in code.

## Current skills

| Skill | Path | Status |
| --- | --- | --- |
| Torsion spring generation | `skills/torsion-spring` | Draft, usable locally |
| STEP left-view inspection | `skills/step-inspector` | Draft, validated on G1 meter layout |
| Onshape REST API client | `skills/onshape-client` | Draft, kept as one optional CAD backend |

## Quick start

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Generate a close-coiled torsion spring STEP:

```powershell
python .\skills\torsion-spring\scripts\generate_torsion_spring.py `
  --wire-d 0.25 `
  --coil-od 2.45 `
  --turns 3 `
  --leg-a-len 12 `
  --leg-b-len 10 `
  --output .\examples\torsion_spring\torsion_spring.step
```

The script uses `pitch = wire_d` by default, so neighboring turns are tangent/close-coiled unless you intentionally set another pitch.

Render a calibrated hidden-shell left view from a STEP file:

```powershell
python .\skills\step-inspector\scripts\render_left_view.py `
  --step <private-project>\g1-1p-528_front_aligned.step `
  --output <private-project>\corrected_left_view.png `
  --hide 20 `
  --label-solids `
  --view-from xmax `
  --mirror-y `
  --tolerance 1.0
```

For detailed local setup, see `docs/environment-setup.zh-CN.md`.

Parse an Onshape document URL and prepare API operations:

```powershell
python .\skills\onshape-client\scripts\onshape_client.py parse-url `
  "https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>"
```

After setting `ONSHAPE_ACCESS_KEY` and `ONSHAPE_SECRET_KEY`, the same script can list elements, list parts, import a CAD file, and export a Part Studio STEP.

For the current AI + industrial 3D learning roadmap, see
`docs/ai-industrial-3d-learning-2026-05-29.zh-CN.md`.

## Repository rules

- Do not commit Onshape API keys, secrets, customer files, or private supplier drawings.
- Put reusable knowledge into `skills/*/SKILL.md`.
- Put deterministic CAD generation code into `skills/*/scripts`.
- Put detailed API workflows into `skills/*/references`.
- Keep examples small and sanitized.

## Roadmap

- Torsion spring fitting against an imported original STEP.
- STEP inspection views that match an engineer's CAD view cube.
- Onshape upload, import/export, element/part listing, and assembly replacement helper.
- Plastic shell supplier simplification skill.
- Rivet and screw inference skill for small appliance/electrical products.
- PC hardware layout datums, including motherboard/GPU/case examples.
- FreeCAD and AgentCAD MCP comparison workflows.

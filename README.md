# industrial-cad-agent-lab

Industrial CAD skills and experiments for CAD agents.

This repository starts from real structure-design work and small public CAD experiments. It is not tied to one CAD platform: current workflows use STEP, build123d/CadQuery-style scripts, CAD Viewer, AgentCAD, FreeCAD MCP experiments, kernelCAD experiments, and GitHub-based process notes.

## Why this repo exists

General CAD agents can call APIs, but they often lack manufacturing judgement. This repo captures repeatable structure-design workflows as small skills, scripts, examples, and review notes:

- Generate mechanical parts from engineering parameters.
- Repair or replace imported STEP parts with cleaner geometry.
- Keep geometry decisions explainable for engineers, reviewers, and suppliers.
- Avoid storing API keys or company-sensitive model files in code.

## Current skills

| Skill | Path | Status |
| --- | --- | --- |
| Industrial CAD validation | `skills/industrial-cad-validator` | Draft, backed by FreeCAD STEP rules |
| Datum research before CAD | `skills/datum-research-before-cad` | Draft, workflow skill |
| Torsion spring generation | `skills/torsion-spring` | Draft, usable locally |
| STEP left-view inspection | `skills/step-inspector` | Draft, validated on G1 meter layout |

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

For detailed local setup, see `docs/environment-setup.md`.

For the current AI + industrial CAD workflow roadmap, see
`docs/ai-cad-workflow-roadmap.md`.

## Repository rules

- Do not commit Onshape API keys, secrets, customer files, or private supplier drawings.
- Public repository content is English by default.
- Chinese/raw working notes stay in a local private archive and are not committed.
- Put reusable knowledge into `skills/*/SKILL.md`.
- Put deterministic CAD generation code into `skills/*/scripts`.
- Put detailed API workflows into `skills/*/references`.
- Keep examples small and sanitized.

## Roadmap

- Torsion spring fitting against an imported original STEP.
- STEP inspection views that match an engineer's CAD view cube.
- CAD backend import/export, part listing, and assembly replacement helpers.
- Plastic shell supplier simplification skill.
- Rivet and screw inference skill for small appliance/electrical products.
- PC component layout datums, including motherboard/GPU/case examples.
- PC cooling datum research, starting with a public 120mm case fan example.
- FreeCAD and AgentCAD MCP comparison workflows.

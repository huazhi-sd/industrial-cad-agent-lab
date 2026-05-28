# onshape-industrial-hardware-skills

Chinese manufacturing CAD skills for Onshape and AI coding agents.

This repository starts from real intelligent circuit breaker structure work. The first skill is a torsion spring generator that turns engineering parameters into a clean STEP model suitable for Onshape import.

## Why this repo exists

General CAD agents can call APIs, but they often lack manufacturing judgement. This repo captures repeatable structure-design workflows as small skills and scripts:

- Generate mechanical parts from engineering parameters.
- Repair or replace imported STEP parts with cleaner geometry.
- Keep geometry decisions explainable for engineers and suppliers.
- Avoid storing API keys or company-sensitive model files in code.

## Current skills

| Skill | Path | Status |
| --- | --- | --- |
| Torsion spring generation | `skills/torsion-spring` | Draft, usable locally |

## Quick start

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

## Repository rules

- Do not commit Onshape API keys, secrets, customer files, or private supplier drawings.
- Put reusable knowledge into `skills/*/SKILL.md`.
- Put deterministic CAD generation code into `skills/*/scripts`.
- Put detailed API workflows into `skills/*/references`.
- Keep examples small and sanitized.

## Roadmap

- Torsion spring fitting against an imported original STEP.
- Onshape upload and assembly replacement helper.
- Plastic shell supplier simplification skill.
- Rivet and screw inference skill for small appliance/electrical products.

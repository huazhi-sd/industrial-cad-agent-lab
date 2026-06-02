---
name: datum-research-before-cad
description: Research standards, mechanical interfaces, coordinate conventions, and non-guessable dimensions before CAD generation. Use before modeling industrial hardware, PC components, sheet-metal parts, plastic shells, brackets, enclosures, connectors, or assemblies where standards, handedness, view direction, mounting datums, keepouts, or feature planes matter.
---

# Datum Research Before CAD

Use this skill before modeling when wrong assumptions would cause CAD rework.

## Workflow

1. Identify the product class and standard family.
2. Search for primary or high-quality sources:
   - official standards or mechanical specifications;
   - vendor mechanical drawings;
   - datasheets;
   - reputable reference implementations;
   - open CAD models only as secondary evidence.
3. Extract only dimensions that affect the first CAD datum.
4. Define the project coordinate contract before modeling:
   - front/back/left/right meanings;
   - origin and datum planes;
   - part naming;
   - handedness;
   - which side is user-facing or assembly-facing.
5. Separate facts into:
   - locked facts;
   - assumptions;
   - unknowns requiring user confirmation;
   - simplifications allowed for datum modeling.
6. Draft validator rules before generating CAD.

## Output

Create a concise `datum-research.md` or equivalent note using `references/datum_research_template.md`.

The note must include:

- source links;
- extracted dimensions;
- coordinate and view contract;
- do-not-guess dimensions;
- simplification boundaries;
- proposed `.rules.json` checks.

## Stop Conditions

Stop and ask the user before modeling if:

- the standard cannot be identified;
- two credible sources disagree on a critical datum;
- the handedness/front direction is ambiguous;
- the model would require mirror or scale-like CAD operations;
- a critical dimension is unavailable and cannot be safely simplified.

## Typical Targets

- PC case components: mATX/ITX motherboard, GPU, PSU, SSD, cooler, fan, PCIe bracket.
- Industrial electrical hardware: plastic shell, busbar, terminal cover, rivet, DIN-rail features.
- Injection-molded parts: draft direction, wall thickness, ribs, posts, clips, assembly splits.
- Sheet-metal and CNC datum parts: mounting holes, bends, keepouts, fastener planes.


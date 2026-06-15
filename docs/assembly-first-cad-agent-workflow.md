# Assembly-First CAD Agent Workflow

This note captures a small but important lesson from building a public M.2
2280 SSD enclosure example with a CAD agent.

The first model looked acceptable from a camera view, but it failed basic
industrial assembly reasoning:

- The assembly tree contained many accidental sub-parts instead of the intended
  main parts.
- The SSD mounting feature used a full circular hole instead of an open-ended
  M.2 tail notch.
- PCB mounting holes and bottom-shell bosses were not coaxial.
- The SSD tail fixation was under-defined until a separate screw part was added.
- Some shell features visually looked closed but had hidden solid interference.

The failure mode was not a lack of geometry generation. The failure was starting
from appearance instead of assembly intent.

## Core Idea

For multi-part industrial CAD, an agent should write the assembly logic before
it writes the geometry.

The minimum pre-modeling brief should include:

1. **Root datum part**
   - Which part defines the assembly coordinate system?
   - Which faces, axes, holes, slots, and interfaces are the primary datums?

2. **Assembly order**
   - Which part is fixed first?
   - Which parts are inserted, seated, pressed, screwed, clipped, or covered?
   - Which motions are required before the final static placement?

3. **Mating constraints**
   - Which holes must be coaxial?
   - Which faces must sit flush or with a defined clearance?
   - Which interfaces must be exposed after assembly?
   - Which contacts are intentional, and which intersections are forbidden?

4. **Validation matrix**
   - Expected top-level part count.
   - Bounding boxes and envelope limits.
   - Required coaxial features.
   - Forbidden interference pairs.
   - Required clearance pairs.
   - Required contact or clamping pairs.

## Example: M.2 SSD Enclosure

For a simple external M.2 2280 enclosure, the intended assembly was:

1. Fix the bottom shell as the root datum.
2. Install the PCB into the bottom shell.
   - PCB mounting holes must align with bottom-shell bosses.
   - The USB-C receptacle must align with the front opening.
   - PCB edges need clearance from the inner shell walls.
3. Insert the M.2 SSD into the M.2 connector.
   - The gold fingers align with the connector centerline.
   - The SSD is inserted at an angle in the real product, then pressed down.
   - In the static CAD model, the final placement must still respect that
     assembly intent.
4. Secure the SSD tail with a screw.
   - The screw axis must align with the SSD tail notch and PCB standoff.
   - The screw head clamps the SSD tail area.
   - The screw must not collide with the top shell.
5. Install the top shell.
   - The top shell lips must fit inside the bottom shell with clearance.
   - The top shell must not hit the SSD, screw head, connector, or tall PCB
     components.

## Tooling Implication

Existing CAD skills and MCP servers can generate geometry, export STEP, render
views, and inspect topology. They do not automatically know which contacts are
functional and which intersections are failures.

That judgment needs to be represented as explicit rules.

Useful agent checks include:

- `expected_part_count`
- `bbox_within_limits`
- `no_interference(part_a, part_b)`
- `min_clearance(part_a, part_b, value_mm)`
- `coaxial(axis_a, axis_b, tolerance_mm)`
- `required_contact_or_clamp(part_a, part_b)`

The important distinction is that "zero interference" is not always correct.
Screws, clips, gaskets, springs, and press-fit features often require intentional
contact or preload. A CAD agent needs a rule matrix, not just a global collision
test.

## Recommended Agent Behavior

Before creating a multi-part assembly, the agent should produce a short
assembly-first brief:

```text
Root datum:
Assembly order:
Top-level parts:
Mating constraints:
Forbidden interference:
Required clearance:
Required contact / clamping:
Validation checks:
```

Only after this brief is stable should the agent generate geometry.

This workflow is small, but it prevents a common failure in AI CAD work:
producing a model that looks plausible but cannot be assembled, inspected, or
explained like an industrial product.

# 120mm Case Fan Datum Research

## Task

- Product or assembly: 120mm PC case fan datum
- Modeling goal: create a public datum for PC case fan cutouts, mounting holes, and clearance planning
- Public/private status: public example

## Sources

| Source | Type | URL | Why it matters |
| --- | --- | --- | --- |
| ARCTIC 120mm fan mounting hole drawing | vendor mechanical drawing | https://support.arctic.de/products/p12-pwm-pst-co/techdocs/120mm_fan-Mounting_hole_pattern.pdf | Primary source for 120mm fan mounting pattern and hole diameter |
| ARCTIC P12 PWM PST spec sheet | vendor specification | https://www.arctic.de/media/42/84/78/1693306001/Spec_Sheet_P12_PWM_PST_EN.pdf | Confirms common 120 x 120 x 25 mm fan body envelope |
| Noctua NF-A12x25 downloads page | vendor CAD/download page | https://www.noctua.at/en/products/nf-a12x25-pwm/downloads | Confirms that vendor CAD models are suitable for mounting and external dimensions, while internal features may be simplified |

## Standard Family

- Standard or mechanical interface: de facto 120mm square PC fan mounting interface
- Related variants: 120mm x 25mm fan, 120mm slim fan, radiator fan, case fan
- Known exclusions:
  - blade geometry;
  - motor hub internal design;
  - rubber corner pad details;
  - cable connector geometry;
  - manufacturer-specific cosmetic frame details.

## Extracted Datums

| Item | Value | Unit | Source | Confidence |
| --- | ---: | --- | --- | --- |
| Fan body width | 120.0 | mm | ARCTIC P12 spec sheet | high |
| Fan body height | 120.0 | mm | ARCTIC P12 spec sheet | high |
| Typical fan thickness | 25.0 | mm | ARCTIC P12 spec sheet | high |
| Mounting hole diameter | 4.3 | mm | ARCTIC mounting drawing | high |
| Drawing unit | mm | ARCTIC mounting drawing | high |
| Mounting pattern outer reference | 116.0 | mm | ARCTIC mounting drawing | medium |
| Mounting pattern secondary reference | 108.0 | mm | ARCTIC mounting drawing | medium |

## Coordinate Contract

- Origin: fan center, on the front face plane.
- X direction: left to right across the fan square.
- Y direction: fan thickness direction, positive toward the rear/exhaust side.
- Z direction: bottom to top across the fan square.
- Front: intake-facing side for case layout review unless the project defines airflow direction differently.
- Back: exhaust-facing side.
- Left/right/top/bottom: screen directions in the raw front view.
- Mounting plane: front square frame plane by default.
- Airflow arrow: optional datum, not required for the first geometry.

## Locked Facts

- The first datum model should use a 120 x 120 x 25 mm bounding box.
- Four mounting holes must be symmetric around the fan center.
- Mounting holes are through-features normal to the thickness direction.
- The hole diameter datum is 4.3 mm for the ARCTIC-derived mounting pattern.

## Assumptions

- The first public datum may use a simplified square frame and circular opening.
- Mounting holes may be represented by cylindrical cutouts.
- Internal blades and hub may be simplified because case-layout work mostly needs envelope, mounting, and airflow opening.
- If using a 105 mm center-to-center hole pitch as a project convention, confirm it against the selected vendor drawing before creating case tooling geometry.

## Unknowns

- Whether the target case should use round holes, slotted holes, or rubber-isolator clearance.
- Whether the fan should be modeled as intake or exhaust in the final assembly.
- Whether radiator compatibility requires wider slots or alternate screw clearance.

## Do-Not-Guess Dimensions

- Mounting hole pitch for manufacturing drawings.
- Screw clearance and thread-forming assumptions.
- Radiator slot pattern.
- Rubber pad compression geometry.

## Allowed Simplifications

- Use a square block for the frame envelope.
- Use a simple circular central airflow opening.
- Use four through-holes for mounting.
- Omit blade geometry in the first datum.
- Omit cable, connector, stickers, and rubber pads.

## Proposed CAD Parts

| Part name | Purpose | Required features |
| --- | --- | --- |
| `fan_120mm_datum` | fan envelope and mounting datum | 120 x 120 x 25 mm body, central airflow opening, four mounting holes |
| `fan_120mm_case_cutout` | optional case-panel cutout helper | fan opening, screw clearance pattern |

## Proposed Validation Rules

- solid count: 1 for a single fan datum body
- overall bbox: 120 x 25 x 120 mm if X/Z are square frame axes and Y is thickness
- hole count: 4, if future validator supports cylindrical feature detection
- symmetry: mounting holes symmetric around origin, if future validator supports feature centers
- orientation: thickness must be on Y axis

## Decision Before Modeling

- Ready to model: yes, for a simplified public datum
- Reason: body envelope and hole diameter have vendor sources; hole pitch should be confirmed before manufacturing-grade case panel tooling


# Standard Parts Expanded Test - 2026-06-24

## Context

Expanded the `tools/standard-parts` prototype beyond the first M2 screw/boss
trial. The goal was to check whether `step.parts` can support practical
engineering standard-part selection for:

- metric small screws,
- imperial PC-case screws,
- nuts and washers,
- standoffs,
- USB-C connectors,
- 120 mm fan interface references.

## Tool Improvements

Updated:

- `tools/standard-parts/standard_part_select.py`

Changes:

1. Added pagination across multiple API pages.
   - This is required because `screw` returns more than one page.
   - Without this, valid parts may be missed.

2. Added metric token normalization.
   - `M2p5` and `M2.5` are treated as equivalent for filtering.

3. Added numeric equality for structured filters.
   - This makes `attributes.lengthMm=3` match numeric `3`.

4. Added `--contains`.
   - Useful for model strings such as USB-C connector names:
     `--contains attributes.model=USB_C`.

## Selection Results

| Case | Filter strategy | Matched | Best result |
| --- | --- | ---: | --- |
| M2.5 screw | `attributes.thread=M2.5` | 29 | Many M2.5 bolts/screws; family must be specified for head style. |
| M3 socket head cap screw, 6 mm | `family=socket-head-cap-screw`, `thread=M3`, `lengthMm=6` | 1 | `iso4762_socket_head_cap_screw_m3x6` |
| PC-case #6-32 x 1/4 socket head screw | `family=asme-socket-head-cap-screw`, `thread=#6-32`, `lengthIn=0.25` | 1 | `asme_socket_head_cap_screw_n6_32_l0p25in_simple` |
| M3 hex nut | `family=hex-nut`, `thread=M3` | 1 | `iso4032_hex_nut_m3` |
| M3 flat washer | `family=flat-washer`, `thread=M3` | 6 | `din125_flat_washer_m3`, plus other washer standards |
| M3 12 mm hex standoff | `family=hex-standoff`, `thread=M3`, `lengthMm=12` | 1 | `hex_standoff_m3_12mm_male_female` |
| USB-C connector | `family=connector-usb`, `model contains USB_C` | 7 | Includes `usb_c_receptacle_gct_usb4085` |
| 120 mm fan mount pattern | `fanSizeMm=120`, `kind=fan_mount_pattern_reference` | 1 | `fan_mount_pattern_reference_120mm` |

## Download / Checksum Trial

Downloaded representative STEP files to a local non-repo trial directory:

```text
D:\cdxwork\26-0507-出图\standard-parts-expanded-trial-20260624
```

Downloaded records:

| id | Checksum |
| --- | --- |
| `iso4762_socket_head_cap_screw_m3x6` | verified |
| `asme_socket_head_cap_screw_n6_32_l0p25in_simple` | verified |
| `iso4032_hex_nut_m3` | verified |
| `din125_flat_washer_m3` | verified |
| `usb_c_receptacle_gct_usb4085` | verified |
| `fan_mount_pattern_reference_120mm` | verified |

The STEP files are not committed. They can be reproduced by id through the
selection script.

## Lessons

1. `step.parts` is strong enough to support a real standard-part selection
   workflow.

2. Plain text search is not enough.
   - `M2 screw` can collide with `M20`.
   - USB-C queries can include USB-A unless model/category filters are applied.

3. Family is important.
   - `thread=M3` alone returns bolts, set screws, countersunk screws, and more.
   - `family=socket-head-cap-screw` or `family=hex-nut` makes the result much
     more deterministic.

4. Some part classes are "reference geometry" rather than real purchasable
   components.
   - `fan_mount_pattern_reference_120mm` is useful for PC-case layout.
   - It is not a complete fan model.

5. This is a good candidate for an MCP wrapper.
   - Inputs should be engineering intent, not raw API filters.
   - Output should include candidate id, standard, key dimensions, STEP URL,
     checksum, and fit/uncertainty notes.

## Next Step

Use selected M2/M3 fasteners and boss/standoff parts inside a real assembly
verification task:

- SSD enclosure screw/boss alignment, or
- PC-case motherboard tray screw/standoff compatibility.

The next layer should combine:

- standard-part selection,
- STEP import,
- bbox/topology inspection,
- axis/clearance validation.

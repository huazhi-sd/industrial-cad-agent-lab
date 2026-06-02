# mATX motherboard layout datums

This file records the fixed layout assumptions for the mATX case project so
the CAD model does not drift into guessed or mirrored motherboard geometry.

## Primary references

- `references/microATX_spec_1_2.pdf`
- `references/microATX_spec_1_2_page_10_hi.png`
- `references/asus_tuf_b850m_manual_page_14.png`

## Coordinate convention

- X: rear I/O side to front side of board.
- Y: board thickness/component height, positive toward components.
- Z: lower PCIe side to upper CPU power side.
- Origin: lower rear corner of the motherboard PCB envelope.
- Board envelope: 243.84 mm x 243.84 mm.

## Semantic main-view checklist

The component-side main view must show:

- Rear I/O stack on the left edge.
- Dual EPS 8-pin CPU power near the upper-left area.
- CPU socket in the upper-middle area.
- DIMM slots to the right of the CPU, close to the right-side power area.
- 24-pin ATX connector on the right edge.
- PCIe x16 first slot below the CPU, extending left-to-right.

## Current placeholder datums

These are approximate visual datums based on the ASUS B850M layout page, not a
reverse-engineered copy of that board.

- CPU socket lower-left: X 83.0, Z 119.0, size 52.0 mm.
- DIMM slots: X 154.0, 164.0, 174.0, 184.0; Z 94.0; length 112.0 mm.
- Dual EPS 8-pin: X 34.0 and 56.0; Z 227.0.
- 24-pin ATX connector: X 228.0; Z 118.0; length 52.0 mm.
- PCIe x16 first slot: X 35.0; center Z 81.58; length 92.0 mm.

## Mounting holes policy

For case design, the tray/standoff datum has priority over decorative
motherboard modeling. Use the 8-hole mATX case datum board when checking
standoff positions:

- B: X 10.16, Z 30.48
- C: X 10.16, Z 83.72
- F: X 22.86, Z 233.68
- R: X 165.10, Z 30.48
- H: X 165.10, Z 83.72
- J: X 165.10, Z 233.68
- L: X 233.68, Z 83.72
- M: X 233.68, Z 233.68

Keep simplified rear I/O, PCIe x16 first slot, and power connector envelopes in
the chassis datum file, because they are fit-critical. Do not place uncertain
CPU, DIMM, SSD, or decorative motherboard details in a file whose purpose is
validating chassis hole positions. If those visual parts are needed later, put
them in a separate motherboard appearance placeholder.

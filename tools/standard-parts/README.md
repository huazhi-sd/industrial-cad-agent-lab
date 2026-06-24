# Standard Parts Selection

Prototype tool for selecting traceable engineering standard parts from
`step.parts`.

The goal is to add an engineering filter layer above plain keyword search. For
example, a naive query for `M2 screw` may return `M20` screws early because text
search alone is not enough. This tool searches the catalog, then filters
structured fields such as `attributes.thread`, `attributes.lengthMm`, `family`,
`category`, and `standard`.

## Example

Find an ISO 4762 M2 x 3 screw:

```powershell
python .\tools\standard-parts\standard_part_select.py screw `
  --category fastener `
  --tag screw `
  --filter attributes.thread=M2 `
  --filter attributes.lengthMm=3 `
  --limit 3
```

Download the STEP file:

```powershell
python .\tools\standard-parts\standard_part_select.py screw `
  --category fastener `
  --tag screw `
  --filter attributes.thread=M2 `
  --filter attributes.lengthMm=3 `
  --limit 1 `
  --download `
  --out-dir .\standard-parts-downloads
```

Find M2 molded PCB bosses:

```powershell
python .\tools\standard-parts\standard_part_select.py standoff `
  --filter attributes.screwInsert=M2 `
  --filter attributes.heightMm=4 `
  --limit 5
```

Find a USB-C connector by model substring:

```powershell
python .\tools\standard-parts\standard_part_select.py "usb c connector" `
  --family connector-usb `
  --contains attributes.model=USB_C `
  --limit 8
```

## Current Scope

- Uses the public `https://api.step.parts/v1/parts` endpoint.
- Outputs JSON for agent use.
- Fetches multiple result pages by default, so broad categories such as `screw`
  are not limited to the first API page.
- Can download STEP files and verify SHA-256 when the API provides a checksum.
- Has one early assembly-fit example in
  `examples/comsol/ssd-enclosure-esd-step-workflow`, where an M2x3 screw is
  accepted and an M2 h=4 mm PCB boss is rejected by stack-height checks.

## Future MCP Direction

This script can become the core of a future `standard-part-selection-mcp`:

1. Search standard-part sources.
2. Filter by engineering attributes.
3. Download or reference STEP files.
4. Inspect bbox/topology.
5. Check fit against named assembly features.
6. Return ranked candidates with uncertainty and provenance.

The SSD enclosure fastener trial is the first seed for step 5. It shows that a
catalog match is not enough: the M2x3 screw is usable, while the catalog M2
4 mm boss is too tall for the 1.1 mm PCB-to-SSD gap and must be rejected.

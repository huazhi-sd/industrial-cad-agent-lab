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

## Current Scope

- Uses the public `https://api.step.parts/v1/parts` endpoint.
- Outputs JSON for agent use.
- Can download STEP files and verify SHA-256 when the API provides a checksum.
- Does not yet perform fit validation against an assembly.

## Future MCP Direction

This script can become the core of a future `standard-part-selection-mcp`:

1. Search standard-part sources.
2. Filter by engineering attributes.
3. Download or reference STEP files.
4. Inspect bbox/topology.
5. Check fit against named assembly features.
6. Return ranked candidates with uncertainty and provenance.

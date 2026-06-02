# Rules Schema

Rules files are JSON objects with a `checks` array.

```json
{
  "version": 1,
  "description": "Short project description.",
  "checks": []
}
```

## Targets

Use `shape` for the whole STEP file:

```json
"target": "shape"
```

Use a zero-based solid index for one solid:

```json
"target": { "solid": 2 }
```

Solid index is based on FreeCAD `shape.Solids` order. Confirm the order with an inspection report before relying on it.

## Rule Types

### solid_count

```json
{
  "name": "assembly_has_three_solids",
  "type": "solid_count",
  "expected": 3
}
```

### bbox_dimensions

Check exact bbox dimensions within tolerance.

```json
{
  "name": "overall_bbox",
  "type": "bbox_dimensions",
  "target": "shape",
  "expected": { "x": 342.5, "y": 154.45, "z": 253.84 },
  "tolerance": 1.0
}
```

### bbox_dimension_range

Check one bbox dimension against min and/or max.

```json
{
  "name": "gpu_envelope_x",
  "type": "bbox_dimension_range",
  "target": { "solid": 2 },
  "axis": "x",
  "min": 335.0,
  "tolerance": 0.5
}
```

### bbox_edge_relation

Compare bbox edges between two targets.

```json
{
  "name": "tray_is_behind_motherboard",
  "type": "bbox_edge_relation",
  "a": { "solid": 0 },
  "a_edge": "y_max",
  "op": ">",
  "b": { "solid": 1 },
  "b_edge": "y_max",
  "tolerance": 0.1
}
```

Supported edges: `x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max`.

Supported operators: `==`, `!=`, `>`, `>=`, `<`, `<=`.

### validity

```json
{
  "name": "all_geometry_valid",
  "type": "validity",
  "target": "all_solids"
}
```

## Rule Design Guidance

- Start with broad gates: solid count, overall bbox, validity.
- Add per-solid bbox only after confirming solid order.
- Use edge relations for orientation, side, and plane checks.
- Keep tolerances realistic. Datum models should not use overly tight tolerances.
- Write rules that catch recurring agent failures, not cosmetic differences.


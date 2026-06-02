# FreeCAD MCP Trial - 2026-06-01

## Summary

`neka-nat/freecad-mcp` was tested on Windows through the Codex MCP host for industrial STEP workflows.

## What worked

- FreeCAD RPC server startup and connection.
- Document creation and object listing.
- `execute_code` for simple geometry.
- STEP export through FreeCAD Python.
- Standard-view image retrieval through MCP.
- Reading a multi-solid STEP through `Part.Shape().read`.

## Limitations

- STEP import/export still requires custom FreeCAD Python snippets.
- Full import workflows can lose assembly hierarchy or time out on larger files.
- A typed wrapper would be more reliable for agents than repeated generated boilerplate.

## Suggested contribution direction

Add stable MCP tools for:

- `import_step`
- `export_step`
- `list_solids_with_bbox`
- `save_view_png`

This would make FreeCAD MCP more useful for real industrial CAD-agent workflows.


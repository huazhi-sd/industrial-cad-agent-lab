# build123d-mcp + step.parts Smoke Test - 2026-06-24

## Context

Follow-up after the weekly AI CAD project watch. Goal:

1. Check whether `build123d-mcp` is usable through the Codex MCP host.
2. Test `step.parts` as a real standard-part source for the SSD enclosure / PCB fastener workflow.

## build123d-mcp Result

Current MCP host version:

```text
build123d-mcp: 0.3.46
build123d: 0.10.0
build123d-drafting-helpers: 0.4.2
bd_warehouse: 0.2.0
augura: 0.1.3
```

Important note:

- The latest observed PyPI version is `0.3.57`.
- The Codex-connected MCP server is therefore not the latest build.
- This means "latest package is installed/available" and "Codex MCP host is connected to latest package" must be checked separately.

### What Worked

`execute()` works.

Minimal script:

```python
print("hello from build123d-mcp")
x = 2
print(x)
```

Result:

```text
hello from build123d-mcp
2
```

Simple CAD generation works.

Generated part:

- 40 x 20 x 3 mm plate
- two 4 mm diameter holes

Measured result:

```text
volume: 2325 mm3
bbox: 40 x 20 x 3 mm
faces: 8
edges: 18
vertices: 12
```

STEP export works when using the MCP server's allowed root:

```text
D:\cdxwork\build123d-mcp-lab\build123d_mcp_smoke_plate_20260624.step
```

STEP re-import works:

```text
volume: 2324.6018 mm3
bbox: 40 x 20 x 3 mm
faces: 8
edges: 18
vertices: 12
```

`bd_warehouse` import works:

```python
from bd_warehouse.fastener import SocketHeadCapScrew
screw = SocketHeadCapScrew(size="M2-0.4", length=3, simple=True)
show(screw, "bdw_socket_head_cap_screw_M2x3")
```

Result:

```text
volume: 28.66 mm3
bbox: 3.98 x 3.98 x 5 mm
faces: 13
```

The 5 mm total height is expected because it includes the screw head.

### Issues Observed

`health_check()` timed out after 300 seconds.

Interpretation:

- The tool is too heavy as a quick startup check in this environment.
- The timeout does not mean core modeling is broken, because `execute`, STEP export, and STEP import all worked afterwards.

Absolute export/import paths are restricted.

Failed path:

```text
D:\cdxwork\26-0507-出图\...
```

Working path:

```text
D:\cdxwork\build123d-mcp-lab\...
```

Interpretation:

- The MCP server has its own allowed read/write roots.
- Our workflow should either configure that root intentionally or export to the MCP lab and copy artifacts afterwards.

`search_library("M2 screw")` returned:

```text
No part library configured.
Start the server with --library PATH or set BUILD123D_PART_LIBRARY.
```

Interpretation:

- The currently connected server is usable for modeling, but not started with a local custom part library.

## step.parts Result

Skill source:

- `C:\Users\cokewithice\.codex\skills\step-parts`

API source:

- <https://api.step.parts>
- <https://www.step.parts>

Downloaded and checksum-verified parts:

| id | Name | Local path | Checksum |
| --- | --- | --- | --- |
| `iso4762_socket_head_cap_screw_m2x3` | ISO 4762 hexagon socket head cap screw, M2 x 3 | `D:\cdxwork\26-0507-出图\standard-parts-trial-20260624\iso4762_socket_head_cap_screw_m2x3.step` | verified |
| `pcb_standoff_boss_m2_h04` | PCB standoff boss M2 h04 | `D:\cdxwork\26-0507-出图\standard-parts-trial-20260624\pcb_standoff_boss_m2_h04.step` | verified |
| `heat_set_insert_boss_m2_h04` | heat set insert boss M2 h04 | `D:\cdxwork\26-0507-出图\standard-parts-trial-20260624\heat_set_insert_boss_m2_h04.step` | verified |

Imported into build123d-mcp after copying to the allowed MCP lab path:

| Part | bbox | volume | faces |
| --- | --- | ---: | ---: |
| ISO 4762 M2 x 3 screw | 3.8 x 3.8 x 5.0 mm | 28.3811 mm3 | 15 |
| PCB standoff boss M2 h04 | 6.0 x 6.0 x 4.0 mm | 100.531 mm3 | 4 |
| heat set insert boss M2 h04 | 6.0 x 6.0 x 4.0 mm | 100.531 mm3 | 4 |

CAD Viewer links:

- [ISO 4762 M2 x 3 screw](http://127.0.0.1:4178/?dir=D%3A%2Fcdxwork%2F26-0507-%E5%87%BA%E5%9B%BE%2Fstandard-parts-trial-20260624&file=iso4762_socket_head_cap_screw_m2x3.step)
- [PCB standoff boss M2 h04](http://127.0.0.1:4178/?dir=D%3A%2Fcdxwork%2F26-0507-%E5%87%BA%E5%9B%BE%2Fstandard-parts-trial-20260624&file=pcb_standoff_boss_m2_h04.step)
- [Heat set insert boss M2 h04](http://127.0.0.1:4178/?dir=D%3A%2Fcdxwork%2F26-0507-%E5%87%BA%E5%9B%BE%2Fstandard-parts-trial-20260624&file=heat_set_insert_boss_m2_h04.step)

## Search Behavior Lesson

Naive search:

```text
M2 screw
```

returned many poor early matches such as M20 screws.

Better method:

1. Query broad fastener/screw records.
2. Filter by structured attributes:
   - `attributes.thread == "M2"`
   - `attributes.lengthMm == 3`
   - expected family / standard.

This confirms the value of a future standard-part-selection layer:

- step.parts is a strong part source,
- but engineering selection should not rely on plain keyword ranking alone.

## Near-Term Design Use

For the SSD enclosure, two different part classes are useful:

1. Screw:
   - `ISO 4762 M2 x 3`
   - suitable as a traceable catalog STEP or as a `bd_warehouse` parameterized fastener.

2. Plastic boss / insert boss:
   - `pcb_standoff_boss_m2_h04`
   - `heat_set_insert_boss_m2_h04`
   - useful as reference geometry for molded PC/ABS/PC enclosure screw posts.

## Recommended Next Steps

1. Upgrade or rewire Codex MCP to use `build123d-mcp 0.3.57`, then rerun this same test.
2. Build a tiny `standard_part_select.py` prototype:
   - input: natural language need,
   - search: step.parts API,
   - filter: structured attributes,
   - output: ranked candidates + STEP URL + bbox.
3. Use the selected M2 screw and M2 boss in the next SSD enclosure assembly iteration.
4. Add a verifier rule for the SSD enclosure:
   - screw axis aligns with boss axis,
   - screw does not pierce board or lid incorrectly,
   - boss height matches board standoff requirement.

## Sources

- <https://github.com/pzfreo/build123d-mcp>
- <https://github.com/pzfreo/build123d-mcp/issues/143>
- <https://github.com/earthtojake/step.parts>
- <https://api.step.parts/v1/parts/iso4762_socket_head_cap_screw_m2x3>
- <https://api.step.parts/v1/parts/pcb_standoff_boss_m2_h04>
- <https://api.step.parts/v1/parts/heat_set_insert_boss_m2_h04>

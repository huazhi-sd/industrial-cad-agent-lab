# mATX motherboard tray + board + 3-slot GPU datum

这是一个公开的 AI + CAD 协作样例，目标不是复刻某一块真实主板或显卡，而是建立一个可用于小型 mATX 机箱布局的三件基准装配：

1. motherboard tray / 主板支架
2. mATX motherboard datum / 主板基准件
3. 3-slot GPU datum / 三槽显卡基准件

当前 STEP 保持为 3 个顶层实体，避免把螺丝柱、接口、金手指、背板等辅助特征散成大量小零件。

## Current output

| File | Purpose |
| --- | --- |
| `motherboard_tray_board_gpu_v1.step` | 当前三件装配 STEP |
| `motherboard_tray_v1.py` | 主板支架源文件 |
| `motherboard_datum_v1.py` | mATX 主板基准件源文件 |
| `gpu_3slot_datum_v1.py` | 三槽显卡基准件源文件 |
| `motherboard_tray_board_gpu_v1.py` | 三件装配源文件 |
| `validate_handedness.py` | 方向/手性检查 |
| `validate_motherboard_tray_board_gpu_v1.py` | 装配、显卡、挡板、金手指检查 |
| `VIEW_CONVENTIONS.md` | 坐标和视图契约 |
| `MOTHERBOARD_LAYOUT_DATUMS.md` | 主板布局基准 |
| `GPU_3SLOT_DATUM_V1.md` | 三槽显卡基准说明 |
| `motherboard_tray_board_gpu_v1_front_20260602T045059Z.png` | 当前主视图 |
| `motherboard_tray_board_gpu_v1_side_20260602T045059Z.png` | 当前侧视图 |
| `motherboard_tray_board_gpu_v1_iso_20260602T045059Z.png` | 当前等轴图 |

旧版 `matx_tray_board_gpu_final_3part.*` 是 2026-06-01 的早期单文件成果，保留作过程对照；新工作应优先看 `*_v1` 文件。

## Geometry contract

- Units: mm.
- Raw CAD `front` = motherboard component side / 主板元件面。
- Rear I/O is left / low X.
- 24-pin ATX is right / high X.
- PCIe x16 and GPU are in the lower area / low Z.
- GPU extends to the right / high X.
- Tray is behind the motherboard on positive Y.
- Motherboard front surface is at negative Y.
- No mirror or scale-like CAD operation is allowed without explicit user approval.

## 3-slot GPU bracket lesson

The GPU bracket was corrected through several failed attempts. The useful rule is:

```text
The three PCIe slot screw pockets must be visible in the motherboard front view,
but their actual retaining-flange plane is away from the motherboard, near the
far end of the I/O bracket.
```

In this model:

- PCI slot pitch: `20.32 mm`
- Three-slot bracket span: `63.23 mm`
- Bracket height datum: `120.11 mm`
- Screw pocket count: `3`
- Screw pocket diameter datum: `6.2 mm`
- Screw clearance diameter datum: `3.6 mm`
- Screw pocket plane offset from motherboard front surface: about `117.51 mm`
- PCIe x16 goldfinger datum: `89.9 x 12.06 mm`

This matters because the three screw pockets drive the future case rear PCIe fixing geometry.

## Regenerate

From this directory:

```powershell
python .\validate_handedness.py
python .\validate_motherboard_tray_board_gpu_v1.py
python C:\Users\cokewithice\.codex\skills\cad\scripts\step --force .\motherboard_tray_board_gpu_v1.py
```

Render review images:

```powershell
python C:\Users\cokewithice\.codex\skills\cad\scripts\snapshot `
  --input .\motherboard_tray_board_gpu_v1.step `
  --output .\front_view.png `
  --camera front `
  --size-profile diagnostic
```

## Why this example matters

This small assembly exposed real AI CAD workflow issues:

- "Front" must be defined as a project contract, not guessed from camera labels.
- User corrections should become executable validators as soon as they reveal a recurring failure mode.
- STEP part structure matters. For layout work, meaningful top-level parts are more useful than many helper solids.
- A visible feature can still be on the wrong physical plane. The GPU screw pockets are the best example here.
- CAD agents need both visual checks and numeric checks.

The procedural rule from this case:

```text
When a user corrects a principle, turn it into a written and executable gate
before continuing geometry work.
```


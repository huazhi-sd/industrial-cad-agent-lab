# mATX motherboard tray + motherboard + GPU datum example

这是一个公开的 AI + CAD 协作样例，来源于一次小型 mATX 机箱项目的现场试做。

目标不是复刻某一块真实主板，而是建立一个可用于机箱布局的三件套基准：

1. 主板支架 / motherboard tray
2. mATX 主板基准件 / motherboard datum
3. 三槽显卡基准件 / 3-slot GPU datum

最终 STEP 保持为 3 个顶层零件，避免把螺丝柱、接口、金手指、装甲等细节散成几十个小零件。

## Files

| File | Purpose |
| --- | --- |
| `matx_tray_board_gpu_final_3part.step` | 当前可查看的最终三件套 STEP |
| `matx_tray_board_gpu_final_3part.py` | build123d 源码 |
| `validate_handedness.py` | 方向/手性/零件数校验 |
| `VIEW_CONVENTIONS.md` | 本项目的视图与坐标约定 |
| `PROJECT_REVIEW_2026-06-01.md` | 过程复盘、踩坑、可贡献点 |
| `front_view.png` | 原始 CAD front 视图检查图 |
| `side_view.png` | 侧向间距检查图 |

## Current geometry contract

- Raw CAD `front` = 主板元件面。
- Rear I/O 在左侧，低 X。
- 24-pin ATX 电源在右侧，高 X。
- PCIe x16 和 GPU 在下侧，GPU 向右延伸。
- 主板支架在主板背后，即正 Y 方向。
- 主板与支架由 6.5 mm 螺丝柱隔开。
- 最终 STEP 只允许 3 个顶层零件。
- 未经明确允许，不使用镜像或负比例缩放来修正手性。

## Regenerate STEP

From this directory:

```powershell
python .\validate_handedness.py
python C:\Users\cokewithice\.codex\skills\cad\scripts\step `
  .\matx_tray_board_gpu_final_3part.py `
  --output .\matx_tray_board_gpu_final_3part.step
```

Render review images:

```powershell
python C:\Users\cokewithice\.codex\skills\cad\scripts\snapshot `
  --input .\matx_tray_board_gpu_final_3part.step `
  --output .\front_view.png `
  --camera front `
  --size-profile diagnostic `
  --appearance workbench
```

## Why this example matters

This small example exposed several real problems in AI-assisted CAD:

- The agent repeatedly confused CAD `front`, motherboard component side, tray back side, and future case front.
- A previously acceptable I/O armor concept was accidentally replaced while fixing another issue.
- Handedness checks were added too late; they should become gates as soon as the user identifies a repeated direction error.
- STEP assemblies need clean part structure, not dozens of tiny helper solids.
- A user-emphasized rule should become a project contract immediately, not remain a chat memory.

The most important lesson is procedural:

```text
When a user corrects a principle, turn it into a written and executable gate
before continuing geometry work.
```

## Remaining simplifications

- The motherboard is a chassis-layout datum, not a real B850M board.
- CPU socket, DIMM, EPS, 24-pin, PCIe, and I/O armor are simplified envelopes.
- GPU goldfinger and bracket are simplified but kept as mating datums.
- This is not a manufacturable chassis yet; it is a validated layout seed.


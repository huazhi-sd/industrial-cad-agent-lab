# build123d-mcp 0.3.31 复测记录 - 2026-06-02

项目：<https://github.com/pzfreo/build123d-mcp>

本地环境：

- OS: Windows 11
- Python: 3.12.10
- Codex MCP host
- MCP 配置目录：`D:\cdxwork\build123d-mcp-lab`
- MCP launcher：`build123d_mcp_no_worker_launcher.py`
- 当前版本：`build123d-mcp 0.3.31`

## 结论

`build123d-mcp 0.3.31` 在当前 Codex MCP 环境下已经可以稳定完成我们短期最关心的流程：

- `execute`
- `measure`
- `render_view`
- `export`
- `import_cad_file`
- `health_check`
- `clearance`
- `align_check`
- `shape_compare`
- `cross_sections`

这比前几天的状态明显进步。当时 `execute()` 在 Codex MCP 下会卡死或超时；现在最小建模、真实 STEP 导入、测量、导出、渲染、干涉/间隙验证都跑通。

## 升级记录

本地 venv 从：

```text
build123d-mcp 0.3.28
build123d-drafting-helpers 0.1.12
```

升级到：

```text
build123d-mcp 0.3.31
build123d-drafting-helpers 0.2.0
```

命令：

```powershell
D:\cdxwork\build123d-mcp-lab\.venv\Scripts\python.exe -m pip install --upgrade build123d-mcp
```

## health_check

新版 `health_check` 通过：

```json
{
  "render_png": {"ok": true},
  "render_svg": {"ok": true},
  "export_step": {"ok": true},
  "export_stl": {"ok": true},
  "ok": true
}
```

之前 `0.3.28` 下曾出现 `health_check` 120 秒超时。升级后同项测试约 0.13 秒完成。

## 最小建模闭环

执行：

```python
from build123d import *
plate = Box(40, 20, 3)
show(plate, 'plate_latest_40x20x3')
```

结果：

```text
Registered 'plate_latest_40x20x3': volume=2400 mm³, faces=6
```

测量结果：

```json
{
  "volume": 2400.0,
  "bbox": {
    "xsize": 40.0,
    "ysize": 20.0,
    "zsize": 3.0
  },
  "topology": {
    "faces": 6,
    "edges": 12,
    "vertices": 8
  }
}
```

导出成功：

```text
D:\cdxwork\build123d-mcp-lab\plate_latest_40x20x3.step
D:\cdxwork\build123d-mcp-lab\plate_latest_40x20x3.stl
```

## 真实 STEP 导入测试

导入文件：

```text
D:\cdxwork\26-0507-出图\matx-case\motherboard_tray_board_gpu_v1.step
```

导入名称：

```text
matx_latest_import
```

导入结果：

```json
{
  "volume": 3373795.083,
  "faces": 154,
  "edges": 439,
  "vertices": 292,
  "bbox": {
    "xsize": 342.5,
    "ysize": 154.45,
    "zsize": 253.84
  }
}
```

这和我们之前通过 FreeCAD / 本地脚本得到的 mATX 组件 bbox 基本一致。

## 真实 STEP 测量价值

`measure("matx_latest_import")` 不只返回 bbox，还返回：

- 体积；
- 表面积；
- 拓扑数量；
- 质心；
- 惯性张量；
- face inventory。

其中 face inventory 对我们很有价值，因为它能列出圆柱面：

```json
{
  "type": "Cylinder",
  "diameter": 6.2,
  "axis": [0.0, -1.0, 0.0]
}
```

这可以用于我们想做的验证：

```text
指定特征是否在正确方向/平面
```

例如机箱项目里：

- 主板螺丝孔是否沿正确方向；
- 显卡挡板固定孔是否在远离主板的平面；
- 孔径是否为预期规格；
- bbox 是否符合预期。

## 渲染测试

对真实 STEP 渲染 front view：

```text
D:\cdxwork\build123d-mcp-lab\matx_latest_import_front.png
```

渲染成功，走的是 `3d pipeline`。

注意：render 能辅助人眼确认，但仍然不能替代 `measure / align_check / clearance`。

## 干涉/间隙/对齐测试

测试几何：

```python
box_a = Box(40, 20, 10).translate((0, 0, 0))
box_b = Box(20, 20, 10).translate((15, 0, 0))
box_c = Box(40, 20, 10).translate((0, 0, 0))
show(box_a, 'box_a')
show(box_b, 'box_b_overlap')
show(box_c, 'box_c_same')
```

### clearance

```json
{
  "clearance": 0.0,
  "status": "interpenetrating",
  "containment": "neither",
  "intersection_volume": 3000.0,
  "a_volume_outside_b": 5000.0,
  "b_volume_outside_a": 1000.0
}
```

### align_check

```json
{
  "delta": -15.0,
  "axis": "X",
  "mode": "clearance",
  "interpretation": "box_a and box_b_overlap overlap by 15 mm on X axis."
}
```

### shape_compare

两个相同盒子对比结果：

```json
{
  "delta": {
    "volume": 0.0,
    "faces": 0,
    "edges": 0,
    "vertices": 0,
    "bbox": [0.0, 0.0, 0.0],
    "center_offset": 0.0
  }
}
```

### cross_sections

对 `box_a` 沿 Z 方向取 5 个截面：

```json
[
  {"position": -4.9, "area": 800.0},
  {"position": -2.45, "area": 800.0},
  {"position": 0.0, "area": 800.0},
  {"position": 2.45, "area": 800.0},
  {"position": 4.9, "area": 800.0}
]
```

这些工具和我们的“工业 CAD agent 验证器”思路高度重合。

## 当前限制

### 1. 仍在用本地 no-worker launcher

当前可用状态基于：

```text
D:\cdxwork\build123d-mcp-lab\build123d_mcp_no_worker_launcher.py
```

也就是说，我们还没有回到官方默认 worker session 模式。

短期没问题，但如果要向作者反馈或贡献，需要明确说明：

- Windows + Codex MCP 下，我们目前使用 no-worker launcher；
- 官方默认 worker 是否已经完全修复，还需要单独复测。

### 2. Python `execute` 有安全沙箱

例如 `getattr(...)` 会被拦截：

```text
SecurityError: Call to 'getattr' is not allowed.
```

这不是坏事，说明它适合 agent 安全执行；但也意味着我们不能靠反射式 Python 代码乱扫模型。

更推荐的方式：

- 用 `measure`;
- 用 `session_state`;
- 用 `resolve`;
- 用 `clearance`;
- 用 `align_check`;
- 用后续我们自己的 wrapper 做结构化检测。

### 3. 导入 STEP 后不直接暴露为 Python `objects` 变量

通过 MCP 工具导入的对象可以被 `measure / render_view / export` 使用，但不适合在 `execute` 里直接写：

```python
objects['matx_latest_import']
```

这会失败：

```text
name 'objects' is not defined
```

所以“导入 STEP 后做 Python 内部复杂遍历”这条路还需要进一步研究。

## 对我们后续项目的意义

`build123d-mcp 0.3.31` 已经可以作为我们短期 CAD agent workflow 的核心工具之一。

它适合承担：

- 快速生成简单参数化模型；
- 导出 STEP/STL；
- 对已有 STEP 做 bbox / topology / face inventory 检查；
- 生成标准视图 PNG；
- 做两个零件之间的 clearance / interference / align check；
- 作为我们后续“验证器模式”的原型工具。

它暂时不适合作为唯一工具：

- 复杂装配源文件仍建议保留 build123d/Python 脚本；
- STEP 复杂层级/零件名解析仍需要 FreeCAD 或自写 wrapper 辅助；
- 工业项目仍需要人工视图约定和用户确认，不能只靠自动渲染。

## 下一步建议

1. 继续保留 `build123d-mcp` 为重点工具。
2. 短期把它接入我们的 mATX 项目验证流程：
   - expected part count;
   - bbox sanity;
   - hole diameter / axis;
   - clearance / align check。
3. 单独复测官方默认 worker launcher：
   - 如果默认 worker 已经在 Windows + Codex 下可用，就可以移除 no-worker 本地改造；
   - 如果仍不可用，就把 no-worker workaround 作为 issue / PR 方向。


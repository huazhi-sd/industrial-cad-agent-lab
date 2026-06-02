# neka-nat/freecad-mcp Windows + Codex 试验记录（2026-06-01）

## 结论

`neka-nat/freecad-mcp` 的 FreeCAD 插件 + RPC server 在本机可以跑通。

已验证能力：

- FreeCAD 插件安装成功。
- RPC 端口 `localhost:9875` 可连通。
- 可通过 RPC 创建 FreeCAD 文档。
- 可执行 FreeCAD Python 代码。
- 可生成简单实体、布尔切孔、导出 STEP。
- 可获取对象拓扑/尺寸信息。
- 可从 FreeCAD 当前视图生成 PNG 截图。

## 关键区别

之前 Codex 中的 `mcp__freecad` 不是 `neka-nat/freecad-mcp`，而是旧的 FreeCAD bridge。

两者端口不同：

- 旧 bridge：`localhost:23456`
- `neka-nat/freecad-mcp`：默认 `localhost:9875`

因此旧工具的 `check_freecad_connection` 会出现误报：显示 FreeCAD 已连接，但实际 `23456` 端口未开放。

## 当前配置

Codex 配置已切换为：

```toml
[mcp_servers.freecad]
command = 'uvx'
args = ['freecad-mcp', '--host', 'localhost']
cwd = 'D:\cdxwork\mcp-lab'
startup_timeout_sec = 120
```

备份：

```text
C:\Users\cokewithice\.codex\config.toml.bak-freecad-nekanat-20260601-try
```

注意：Codex 需要重启后，`mcp__freecad` 工具列表才会切换到 `neka-nat/freecad-mcp`。

## FreeCAD 侧安装

FreeCAD 路径：

```text
D:\Program Files\FreeCAD 1.1\bin\freecad.exe
```

FreeCAD 1.1 用户目录：

```text
C:\Users\cokewithice\AppData\Roaming\FreeCAD\v1-1\
```

插件安装位置：

```text
C:\Users\cokewithice\AppData\Roaming\FreeCAD\v1-1\Mod\FreeCADMCP
```

已设置自动启动 RPC：

```json
{
  "remote_enabled": false,
  "allowed_ips": "127.0.0.1",
  "auto_start_rpc": true
}
```

## 实测输出

测试文件：

```text
D:\cdxwork\mcp-lab\freecad_neka_nat_trial_plate.step
D:\cdxwork\mcp-lab\freecad_neka_nat_trial_plate_iso.png
```

测试模型：

- 40 x 20 x 3 mm 板件。
- 两个 M3 clearance 近似孔，孔径 3.4 mm。
- STEP 导出成功。
- FreeCAD 截图成功。

## 观察

这个项目更接近“真实 FreeCAD 自动化桥梁”：它让 agent 能在 FreeCAD GUI 环境里执行 FreeCAD Python、读对象、截图、保存结果。

与 `build123d-mcp` 相比：

- `build123d-mcp` 更适合纯代码参数化建模和结构化几何验证。
- `freecad-mcp` 更适合利用 FreeCAD 生态、已有模型、GUI 截图、FreeCAD 原生命令。

与 `text-to-cad` 相比：

- `text-to-cad` 更像 CAD skill/workflow。
- `freecad-mcp` 更像 CAD 软件控制层。

## 当前限制

- 本轮 Codex 尚未重启，因此当前暴露的 `mcp__freecad` 工具仍是旧 bridge。
- 重启 Codex 后需要再次验证新工具 schema。
- FreeCAD 插件需要 FreeCAD GUI 启动，纯 headless 稳定性还未验证。
- 后续要测试复杂装配、STEP 导入、对象命名、标准视图截图、工程图输出。

## 2026-06-02 复测

Codex 重启后，`mcp__freecad` 已切换为 `neka-nat/freecad-mcp` 的工具 schema。

新工具包括：

- `create_document`
- `list_documents`
- `create_object`
- `edit_object`
- `get_object`
- `get_objects`
- `delete_object`
- `execute_code`
- `get_view`
- `insert_part_from_library`
- `get_parts_list`

复测结论：

- `list_documents` 成功。
- `create_document` 成功。
- `execute_code` 成功创建 40 x 20 x 3 mm 双孔板。
- STEP 导出成功：

```text
D:\cdxwork\mcp-lab\freecad_mcp_trial_0602_plate.step
```

几何数据：

- bbox：40.0 x 20.0 x 3.0 mm
- volume：2345.5248 mm^3
- faces：8
- edges：18

`get_objects` 可以返回对象结构、bbox、体积、面积、面数、边数和颜色信息。

`get_view` 可以返回指定标准视图截图。

## STEP 导入测试

测试对象：

```text
D:\cdxwork\26-0507-出图\matx-case\matx_tray_board_gpu_final_3part.step
```

### 成功路线

使用 `Part.Shape().read(step_path)` 可以稳定导入已有 STEP。

结果：

- object_count：1
- bbox：340.0 x 154.1 x 253.84 mm
- volume：3840807.731 mm^3
- faces：160
- edges：373
- solids：3

输出 FreeCAD 文件：

```text
D:\cdxwork\mcp-lab\freecad_mcp_import_matx_shape_read_0602.FCStd
```

局限：

- 这种方式把 STEP 读成一个 `Part::Feature`。
- 可以保留多个 solid，但会丢失原始零件层级/对象命名。

### 失败/阻塞路线

`ImportGui.insert(step_path, doc_name)` 在 MCP `execute_code` 中失败：

```text
NameError: Unknown document 'codex_freecad_import_matx_0602'
```

改用 `doc.Name` 后仍失败。

`Import.open(step_path)` 在同步 MCP 调用中超过 120 秒超时。

推测：

- `Import.open` 更接近完整 STEP 装配导入，可能保留更多结构。
- 但对较复杂 STEP 而言，同步 MCP 调用容易卡住。
- 后续要测试 `execute_code_async` 或 FreeCAD GUI 侧导入后由 MCP 读取对象。

`saveImage()` 也出现 120 秒超时，可能与前一次重导入/GUI 线程状态有关。

## 对我们的意义

`neka-nat/freecad-mcp` 在本机已经具备基本可用性：

- 适合执行 FreeCAD Python。
- 适合从已有 STEP 提取几何数据。
- 适合把简单模型导出成 STEP。
- 适合返回对象结构和标准视图截图。

目前不建议把它作为唯一主建模路径。

更合理的定位：

- `build123d-mcp`：参数化建模、快速几何验证。
- `FreeCAD MCP`：读取/检查 STEP、FreeCAD 原生操作、后续工程图/GUI 生态。
- CAD skill / text-to-cad：沉淀可复用 workflow 和公开案例。

需要继续研究的问题：

- 如何稳定导入 STEP 装配并保留零件层级。
- 如何避免 GUI 线程同步超时。
- 如何把 FreeCAD 标准视图截图保存为本地文件，而不是只作为 MCP image 返回。
- 是否可以对 FreeCAD MCP 增加 `import_step`、`export_step`、`save_view_png` 等更工业化的封装工具。

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

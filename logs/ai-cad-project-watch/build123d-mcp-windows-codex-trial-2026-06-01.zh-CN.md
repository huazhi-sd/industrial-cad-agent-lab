# build123d-mcp Windows + Codex trial - 2026-06-01

## 目的

试用 [pzfreo/build123d-mcp](https://github.com/pzfreo/build123d-mcp)，判断它是否适合作为当前 AI + CAD 工作流中的 build123d 参数化建模后端。

## 环境

- OS: Windows
- Python: 3.12.10
- build123d-mcp: 0.3.28
- Codex MCP 配置目录：`C:\Users\cokewithice\.codex\config.toml`
- 本地试验目录：`D:\cdxwork\build123d-mcp-lab`

## 已尝试配置

### 1. uv tool run 直接启动

```toml
[mcp_servers.build123d_mcp]
command = '...\uv.exe'
args = ['tool', 'run', '--python', '3.12', 'build123d-mcp', '--exec-timeout', '30']
cwd = 'D:\cdxwork\build123d-mcp-lab'
```

结果：

- `version` 正常返回 `0.3.28`
- `reset` 初始正常
- `execute` 失败：`Worker process failed to start within timeout`

### 2. 本地 launcher + uv run

新增：

```python
from build123d_mcp.server import main

if __name__ == "__main__":
    main()
```

配置：

```toml
args = ['run', '--with', 'build123d-mcp', '--python', '3.12', 'python', 'build123d_mcp_launcher.py', '--exec-timeout', '30']
```

结果：

- `version` 正常
- `reset` 正常
- `execute` 仍失败：`Worker process failed to start within timeout`

### 3. 固定 venv + 本地 launcher

安装：

```powershell
python -m venv D:\cdxwork\build123d-mcp-lab\.venv
D:\cdxwork\build123d-mcp-lab\.venv\Scripts\python.exe -m pip install build123d-mcp
```

配置：

```toml
[mcp_servers.build123d_mcp]
command = 'D:\cdxwork\build123d-mcp-lab\.venv\Scripts\python.exe'
args = ['build123d_mcp_launcher.py', '--exec-timeout', '30']
cwd = 'D:\cdxwork\build123d-mcp-lab'
startup_timeout_sec = 180

[mcp_servers.build123d_mcp.env]
PYTHONIOENCODING = 'utf-8'
PYTHONUTF8 = '1'
```

结果：

- `version` 正常
- `reset` 正常
- `execute("print('hello')")` 仍失败
- 失败后 `session_state` 也失败，说明 worker 状态已坏

## 对照测试

在 PowerShell 中直接调用 `WorkerSession`，同样的 fixed venv 可以成功：

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
D:\cdxwork\build123d-mcp-lab\.venv\Scripts\python.exe debug_worker_execute.py
```

结果：

```text
version: 0.3.28
execute-start
hello
2
state: {
  "current_shape": null,
  "objects": {},
  "snapshots": [],
  "variables": {
    "x": {
      "type": "int",
      "value": 2
    }
  },
  "geometry_refs": {}
}
```

几何生成也可以在 PowerShell 中成功：

```text
Registered 'datum_plate_m3': volume=2346 mm³, faces=8
bbox: 40×20×3 mm
Exported to D:\cdxwork\build123d-mcp-lab\datum_plate_m3.step
```

## 初步判断

问题不在 build123d 本身，也不在 `Session.execute()` 本体。

更可能的问题是：

- Codex 作为 MCP 宿主启动 `build123d-mcp` 后；
- `build123d-mcp` 内部再通过 Windows `multiprocessing.spawn` 启动 worker 子进程；
- worker 子进程未能在 `_WORKER_READY_TIMEOUT` 内发回 ready 信号；
- 因此任何依赖 worker 的工具都会失败。

这个问题与 Windows multiprocessing、MCP stdio 宿主环境、console entrypoint / launcher 启动形态有关。

## 对当前项目的影响

`build123d-mcp` 的工具设计非常适合当前路线：

- `execute`
- `measure`
- `render_view`
- `clearance`
- `interference`
- `shape_compare`
- `import_cad_file`
- `export`
- `script`
- 2D drawing lint / inspect

但在当前 Codex Windows 环境中，还不能稳定作为 MCP 直接使用。

短期可行方案：

1. 继续用普通 build123d Python 脚本生成 STEP。
2. 用 PowerShell / Python 直接调用 `WorkerSession` 做局部验证。
3. 暂时不把 `build123d-mcp` 作为生产主路径。
4. 整理复现信息，向作者反馈。

## 后续建议

向 `build123d-mcp` 作者反馈：

- Windows + Codex MCP host
- `version/reset` works
- `execute` fails with `Worker process failed to start within timeout`
- same `WorkerSession.execute()` succeeds from normal PowerShell
- tested uv tool run, launcher, fixed venv
- likely issue around `multiprocessing.spawn` from MCP stdio host


# 环境搭建：Onshape 工业结构 Agent

本文档记录运行本仓库脚本所需的本地环境。原则是：凡是后续项目会反复用到的库，都应安装并写入仓库文档；临时试验命令不应只留在聊天记录里。

## 1. Python 环境

推荐使用 Python 3.11 或更新版本。可以使用系统 Python、虚拟环境，或 Codex/IDE 自带的 Python 运行环境。

检查版本：

```powershell
python --version
```

如果 Windows 提示 `Python was not found`，说明当前 `python` 命令可能指向 Microsoft Store 占位符，而不是实际解释器。解决方式：

- 安装 Python 后把真实 Python 加入 `PATH`；
- 或在命令中使用你当前工程环境的 Python 可执行文件；
- 或把常用解释器路径设置成一个本地变量，例如：

```powershell
$PYTHON="path\to\python.exe"
& $PYTHON --version
```

后续命令中的 `python` 都可以替换成 `& $PYTHON`。

## 2. 安装依赖

在仓库根目录运行：

```powershell
python -m pip install -r requirements.txt
```

如果使用 `$PYTHON`：

```powershell
& $PYTHON -m pip install -r requirements.txt
```

当前依赖：

- `requests`：调用 Onshape REST API，尤其是上传 STEP、查询翻译任务、读取文档/装配结构。
- `cadquery`：本地参数化建模，生成 STEP，例如扭簧、铆钉、简化结构件。

`cadquery` 会带来 Open CASCADE/OCP 相关能力，安装可能比普通 Python 包更慢。若 pip 安装失败，可单独使用已带 CadQuery 的工程环境，或后续改用 conda 环境。

## 3. 验证依赖

```powershell
python -c "import requests, cadquery; print('ok')"
```

如果使用 `$PYTHON`：

```powershell
& $PYTHON -c "import requests, cadquery; print('ok')"
```

如果只做 Onshape API 上传，不做本地建模，至少需要：

```powershell
python -c "import requests; print(requests.__version__)"
```

## 4. Onshape API 凭据

不要把 API key/secret 写进代码或提交到 GitHub。使用环境变量：

```powershell
$env:ONSHAPE_ACCESS_KEY="replace_with_access_key"
$env:ONSHAPE_SECRET_KEY="replace_with_secret_key"
```

长期使用时，可以放到本机私有 `.env` 或系统环境变量中，但 `.env` 已被 `.gitignore` 排除。

## 5. 大 STEP 上传经验

Onshape 上传 STEP 应优先使用 `multipart/form-data`，不要把 STEP 文件作为裸 body 直接 POST。裸 body 对大文件更容易触发 `413 Request Entity Too Large` 或服务端拒绝。

当前验证有效的上传路径：

```text
POST /api/v6/blobelements/d/{documentId}/w/{workspaceId}
```

表单字段：

```text
storeInDocument=true
allowFaultyParts=false
flattenAssemblies=false
formatName=STEP
file=<STEP file>
```

上传返回中会包含 `translationId`，然后查询：

```text
GET /api/v10/translations/{translationId}
```

直到 `requestState = DONE`，再读取 `resultElementIds`。

大文件上传失败时，按以下顺序排查：

1. 确认使用的是 `requests` multipart 上传。
2. 确认 `Content-Type` 参与 HMAC 签名时与实际 multipart boundary 完全一致。
3. 如果出现代理或连接中止，尝试浏览器手动上传，或检查本机代理/安全软件。
4. 上传成功后等待 Onshape translation 完成，再读取生成的 element/assembly。

## 6. 项目习惯

- 能沉淀为通用能力的环境补充，要写入 `requirements.txt` 或文档。
- 能沉淀为流程经验的失败，要写入 `docs/` 或对应 skill 的 `references/`。
- 不上传公司原始文件、API 密钥、本地绝对路径或临时大文件。

## 7. 2026-05-29 本机环境记录

今天把后续 AI + CAD 工作会反复使用的基础环境补齐：

| 工具 | 版本/用途 | 状态 |
| --- | --- | --- |
| Python | 3.12.10，用于 Onshape API、CadQuery/OCP、脚本化几何处理 | 已安装 |
| pip | 26.1.1 | 已安装 |
| requests | 2.34.2，用于 REST API | 已安装 |
| cadquery | 2.7.0，用于生成/读取 STEP 和参数化建模 | 已安装 |
| matplotlib | 3.10.9，用于视图渲染 | 已安装 |
| Node.js | 24.16.0，用于 MCP、前端预览、JavaScript 工具 | 已安装 |
| npm | 11.13.0 | 已安装 |
| uv | 0.11.15，用于 Python 项目和 MCP server 运行 | 已安装 |
| Git | 2.54.0 | 已安装 |

当前 Codex 进程可能不会立即读取新的 Windows PATH。若命令行仍提示 `python` 找不到，可先重新打开 PowerShell；如果仍指向 Microsoft Store 占位符，应关闭 Windows 的 Python App execution aliases。

已验证的正式 Python 路径：

```powershell
$PYTHON="$env:LocalAppData\Programs\Python\Python312\python.exe"
& $PYTHON -c "import requests, cadquery, matplotlib; print('ok')"
```

Node 和 uv 由 `winget` 安装到用户目录。重新打开 shell 后应可直接运行：

```powershell
node --version
npm --version
uv --version
```

## 8. 2026-05-29 安装 CAD Skills

已从 `earthtojake/text-to-cad` 安装 3 个核心 skill 到本机 Codex：

| Skill | 本机位置 | 用途 |
| --- | --- | --- |
| `cad` | `%USERPROFILE%\.codex\skills\cad` | STEP-first 参数化 CAD 生成、检查、验证 |
| `cad-viewer` | `%USERPROFILE%\.codex\skills\cad-viewer` | 启动本地 CAD Viewer，查看 STEP/STP/GLB/STL/DXF 等文件 |
| `step-parts` | `%USERPROFILE%\.codex\skills\step-parts` | 从 step.parts 搜索并下载常见标准件/采购件 STEP |

安装命令：

```powershell
$SCRIPT="$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py"
& "$env:LocalAppData\Programs\Python\Python312\python.exe" $SCRIPT `
  --repo earthtojake/text-to-cad `
  --path skills/cad skills/cad-viewer skills/step-parts
```

暂未安装：

- `urdf`、`sdf`、`srdf`：偏机器人描述和仿真格式，当前工业结构项目暂不需要；
- `gcode`、`bambu-labs`：偏 3D 打印；
- `sendcutsend`：偏钣金/在线加工交付，后续需要时再装。

安装后需要重启 Codex，新的 skill 才会进入会话可用列表。未重启前，文件已经在本机，但当前对话不一定能自动触发这些 skill。

资料：

- https://github.com/earthtojake/text-to-cad
- https://www.cadskills.xyz

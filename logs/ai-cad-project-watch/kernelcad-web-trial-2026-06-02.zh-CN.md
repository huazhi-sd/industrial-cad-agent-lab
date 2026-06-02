# kernelCAD-web 试用记录 - 2026-06-02

项目：<https://github.com/w1ne/kernelCAD-web>

本地试用目录：

- 源码：`D:\cdxwork\kernelCAD-web`
- 临时输出：`D:\cdxwork\kernelcad-lab`

## 结论

`kernelCAD-web` 值得继续跟进。它不是传统 CAD UI，而是更接近我们想要的“Agent-first CAD workflow layer”：

- `.kcad.ts` 源码作为设计源文件；
- CLI / MCP 作为 agent 入口；
- evaluate / validate / export / render 形成可复现证据链；
- 支持 STEP/STL/DXF/3MF/GLB 等导出；
- README 明确强调 deterministic validation、feature history、review evidence。

今天已经跑通：

- `kernelcad --help`
- `kernelcad evaluate`
- `kernelcad export step`
- `kernelcad render`

但 Windows 上发现一个明确可复现的问题：CLI bundle 的 `__filename` / `__dirname` 构造方式会导致 wasm 路径被拼成 `D:\D:\...`。

## 环境

- OS: Windows 11
- Node: `v24.16.0`
- npm package: `kernelcad@0.11.1`
- Playwright: `1.58.0`
- kernelCAD 本地源码：`w1ne/kernelCAD-web`

## 安装观察

`npm install` 可以成功，但比较慢：

- 耗时约 7 分钟；
- 安装 713 个 packages；
- 依赖包含 GitHub 版 `replicad-opencascadejs`；
- npm audit 报 17 个漏洞：9 moderate、7 high、1 critical。

这不影响今天的功能试用，但后续如果要把它作为长期工具，需要关注依赖体积和安全提示。

## Windows wasm 路径问题

构建 CLI 后，直接运行：

```powershell
node dist\cli\index.js evaluate examples\bracket-with-hole.kcad.ts
```

失败：

```text
ERROR [cli.script-exception] <unknown>: Aborted(Error: ENOENT: no such file or directory, open 'D:\D:\cdxwork\kernelCAD-web\dist\cli\replicad_single.wasm')
```

实际 wasm 文件存在：

```text
D:\cdxwork\kernelCAD-web\dist\cli\replicad_single.wasm
```

定位原因：

`scripts/build-cli.mjs` 的 banner 使用：

```js
const __filename=new URL(import.meta.url).pathname;
const __dirname=new URL('.',import.meta.url).pathname;
```

在 Windows 上这会得到 URL pathname 风格路径，后续被 Emscripten / Node 路径逻辑拼坏。

本地临时修复：

```js
import{fileURLToPath as __bfu}from'node:url';
const __filename=__bfu(import.meta.url);
const __dirname=__bfu(new URL('.',import.meta.url));
```

修复后重新构建 CLI，`evaluate` 和 `export step` 均成功。

## 几何试用结果

示例文件：

```text
D:\cdxwork\kernelCAD-web\examples\bracket-with-hole.kcad.ts
```

源码内容很简洁：

```typescript
const w = 60;
const h = 40;
const t = 5;

const base = box(w, h, t);
const hole = cylinder(t + 2, 4).translate(w / 2, h / 2, -1);
return base.subtract(hole).fillet(1);
```

运行：

```powershell
node dist\cli\index.js evaluate examples\bracket-with-hole.kcad.ts
```

结果：

```text
Features: 4
OK
```

STEP 导出：

```powershell
node dist\cli\index.js export step examples\bracket-with-hole.kcad.ts -o D:\cdxwork\kernelcad-lab\bracket-with-hole-kernelcad.step
```

结果：

```text
Wrote 74458 bytes to D:\cdxwork\kernelcad-lab\bracket-with-hole-kernelcad.step
```

## 渲染试用结果

render 需要先启动 web Studio：

```powershell
npm run dev -- --host 127.0.0.1
```

然后运行：

```powershell
node dist\cli\index.js render examples\bracket-with-hole.kcad.ts -o D:\cdxwork\kernelcad-lab\bracket_kernelcad.png --separate --width 900 --height 700 --base-url http://127.0.0.1:5173
```

生成：

- `D:\cdxwork\kernelcad-lab\bracket_kernelcad.front.png`
- `D:\cdxwork\kernelcad-lab\bracket_kernelcad.right.png`
- `D:\cdxwork\kernelcad-lab\bracket_kernelcad.top.png`
- `D:\cdxwork\kernelcad-lab\bracket_kernelcad.iso.png`

视觉检查：

- iso 图显示为一个带中心圆孔的倒角矩形板；
- 无空白渲染；
- 无明显浮动物体；
- 圆角和孔特征清晰可见。

## Playwright 环境摩擦

第一次 render 失败，因为 Playwright 找不到：

```text
C:\Users\cokewithice\AppData\Local\ms-playwright\chromium_headless_shell-1208\chrome-headless-shell-win64\chrome-headless-shell.exe
```

`npx playwright install chromium` 在本地网络下 10 分钟超时。

临时解决：

- 使用本机已有的 `D:\chrome-download\chrome-headless-shell-win64.zip`
- 解压到：

```text
C:\Users\cokewithice\AppData\Local\ms-playwright\chromium_headless_shell-1208
```

之后 render 成功。

这说明 kernelCAD 的可视化链路本身可用，但 Playwright 浏览器安装仍是 Windows + 国内网络环境下的高频摩擦点。

## MCP 观察

`kernelcad mcp --help` 可用：

```text
Run the kernelCAD MCP server (stdio transport).

Options:
  --cloud
  --api-base-url <url>
  --token <token>
```

`kernelcad install --codex --dry-run` 输出：

```text
Would run: codex mcp add kernelcad -- npx -y kernelcad mcp
```

判断：

- 它已经考虑了 Codex 接入；
- 但默认走 `npx -y kernelcad mcp`，也就是 npm 发布包；
- 如果发布包也存在 Windows wasm 路径问题，直接接入 Codex MCP 可能会失败；
- 建议等路径修复进入发布包，或暂时用本地修复版 CLI 作为 MCP command。

## 对我们的价值

kernelCAD 和我们目前形成的方向高度重合：

```text
source-first CAD + deterministic validation + STEP export + rendered evidence
```

它比单纯的 build123d 脚本多了几个值得学习的点：

- `.kcad.ts` 作为专门的 CAD agent 源文件格式；
- skill tree 很完整，覆盖 authoring、assemblies、patterns、sheet metal、MCP、from-reference；
- render inspect / mask / depth / normals 这类证据链设计，和我们想做的“特征方向/平面验证”很接近；
- MCP / CLI / web review cockpit 三层架构很清晰。

## 暂不建议立刻做的事

- 暂不把 `kernelcad` MCP 写进 Codex 主配置；
- 暂不把它用于公司断路器项目；
- 暂不大规模迁移我们当前 build123d / FreeCAD 流程。

原因：

- Windows CLI 有可复现路径 bug；
- Playwright 安装仍有摩擦；
- 它的 `.kcad.ts` 生态需要单独学习；
- 我们已有的 mATX datum 项目目前用 Python/build123d 更直接。

## 建议下一步

1. 给 `w1ne/kernelCAD-web` 提一个 Windows issue：
   - 标题可围绕 `CLI wasm path becomes D:\D:\... on Windows`
   - 附上最小复现和 `fileURLToPath` 修复建议。
2. 继续观察 kernelCAD 的 MCP / render inspect：
   - 重点看是否能输出 mask、depth、normals；
   - 这可能能帮助我们做“特征在正确方向/平面”的验证器。
3. 后续可以尝试用 `.kcad.ts` 复刻一个小型散热片或主板支架 datum：
   - 不追求复杂；
   - 重点比较它和 build123d 的可维护性、验证能力、MCP 能力。


# AI + 工业 3D 学习路线 2026-05-29

## 今日定位

本仓库的主线不是“替某个公司项目画完图”，而是学习并沉淀 AI + 工业 3D 的前沿工作方式。公司真实项目只作为练兵场，用来暴露问题、验证流程、沉淀 skill。

## 五条技术路线

### 1. Agent CAD skill 库

代表项目：`earthtojake/text-to-cad`。

它的价值不是某一个零件生成得多好，而是把 CAD、STEP、机器人描述、加工交付等任务拆成多个 agent skill。对我们最有参考意义的是仓库结构：

- 每个能力独立成 `skills/<name>/SKILL.md`；
- 可执行脚本放在 skill 下；
- 输出以 STEP/STL/3MF/GLB 等工程文件为主；
- 让 agent 先遵循明确流程，再调用脚本。

我们的对应动作：

- 保持 `torsion-spring`、`step-inspector` 这种小 skill；
- 每完成一个真实项目动作，就问能否抽象成 skill；
- 避免把所有能力混成一个巨大脚本。

资料：

- https://github.com/earthtojake/text-to-cad
- https://www.cadskills.xyz

### 2. Onshape MCP / API Agent

代表项目：`ReshefElisha/jarvis-onshape-mcp`，以及多个新的 `onshape-mcp` 仓库。

它最接近我们的目标：让 agent 通过 Onshape API 和 FeatureScript 驱动真实 CAD，而不是只靠浏览器截图点按钮。值得学习的关键点：

- 每次修改都返回结构化结果，例如是否成功、生成了什么 feature、有什么警告；
- 用标准视图 PNG 和局部裁剪帮助 agent 看模型；
- 在建模前先做视觉拆解，生成 feature tree，再让用户确认；
- 通过 FeatureScript 处理普通 API 工具不够表达的复杂特征。

我们的对应动作：

- 建一个轻量 `onshape-client` skill，先做上传、导入、导出、列 element、列 part；
- 后续再做零件重命名、标准视图渲染、装配替换；
- 不再把浏览器 UI 自动化当主线。

资料：

- https://github.com/ReshefElisha/jarvis-onshape-mcp
- https://cad.onshape.com/FsDoc/index.html
- https://www.onshape.com/en/blog/cloud-native-cad-rest-api

### 3. STEP / B-Rep 几何识别

这是我们昨天真正验证成功的一条路线。`step-inspector` 通过本地 CadQuery/OCP 读取 STEP，输出工程师认可的左视图、隐藏壳体后的视图、实体编号和投影关系。

它解决的问题是：agent 不能只靠“看屏幕”，必须能直接读几何。

下一步应扩展：

- 实体清单：编号、包围盒、体积、颜色、质心；
- 视图校准：记录用户确认过的前/后/左/右方向；
- 截面和投影：用于铜排、PCB、插针、齿轮组空间判断；
- 候选特征识别：孔、柱、薄片铜排、齿轮、端子框、插针阵列。

资料：

- https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html
- https://cadquery.readthedocs.io/

### 4. AI 原生 CAD / 新几何内核

代表项目：`ecto/vcad`、`Adam-CAD/CADAM`、`KoStard/forgecad-public-kit`。

这类项目说明一个趋势：未来 CAD 不一定只是在传统软件上外挂 AI，也可能出现“为 AI 调用而设计”的 CAD 内核、文件格式、MCP 工具和网页建模环境。

当前判断：

- 适合关注和学习，不适合作为公司项目主工具；
- 对我们最有价值的是接口设计：inspect、export、create document、feature-level 操作；
- Rust/WASM 内核路线值得长期关注，但短期仍以 Onshape + STEP/B-Rep 为主。

资料：

- https://github.com/ecto/vcad
- https://vcad.io
- https://github.com/Adam-CAD/CADAM
- https://github.com/KoStard/forgecad-public-kit

### 5. 研究 benchmark 与视觉 GUI 自动化

研究方向包括 CAD 生成 benchmark、FeatureScript 数据集、GUI agent、工程图 OCR、截图识别。它们的共同价值是建立“如何评价 agent 是否真的懂 CAD”的方法。

对我们而言，截图自动化只能做辅助：

- 判断是否登录；
- 点击固定按钮；
- 保存标准视图截图；
- 读取错误提示。

几何判断必须回到 API 和 B-Rep。昨天反复错左右视图，已经证明纯截图和坐标猜测不可靠。

我们的对应动作：

- 建 `screen-checker` 时只让它负责 UI 状态确认；
- 不让截图模型承担几何语义理解；
- 把每次失败归档成规则，减少同类错误。

资料：

- https://sikulix.github.io/docs/
- https://www.microsoft.com/en-us/research/publication/omniparser-for-pure-vision-based-gui-agent/

## 今日环境补充

已安装并验证：

- Python 3.12.10：正式本机 Python；
- `requests 2.34.2`：Onshape API；
- `cadquery 2.7.0`：本地 STEP/参数化建模；
- `matplotlib 3.10.9`：视图渲染；
- Node.js LTS 24.16.0 / npm 11.13.0：MCP、前端预览和 JavaScript 工具；
- `uv 0.11.15`：现代 Python 项目和 MCP server 常用运行器；
- Git 2.54.0：仓库管理。

注意：

- 当前 Codex 进程还没刷新 Windows PATH，所以今天命令中可能仍需使用完整路径；
- 重新打开 PowerShell 后，`python`、`node`、`npm`、`uv` 应该可以直接使用；
- 如果 `python` 仍指向 Microsoft Store 占位符，需要关闭 Windows 的 Python App execution aliases。

## 今天建议按这个顺序推进

1. 先讲清 5 条路线的基本概念和各自边界；
2. 用本仓库跑通正式 Python 环境；
3. 研究 `text-to-cad` 的 skill 目录设计；
4. 研究 `jarvis-onshape-mcp` 的 Onshape API/MCP 设计；
5. 给我们自己的仓库补一个最小 `onshape-client` skill 草案；
6. 再回到 G1 电表项目，把真实问题转成可复用工具需求。

## 一句话判断

短期最应该押注的是：`Onshape API + STEP/B-Rep 本地识别 + 小 skill 仓库`。

长期可以跟踪：`AI 原生 CAD 内核 + MCP + 仿真闭环`。

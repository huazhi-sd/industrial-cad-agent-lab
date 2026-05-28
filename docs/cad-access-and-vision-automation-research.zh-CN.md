# CAD 特征获取与视觉自动化调研

## 背景

当前项目遇到的第一个核心问题不是建模本身，而是 agent 难以稳定、直观地获取用户希望看到的 CAD 特征和画面。

这类问题不能只靠“截图后猜测”。前人常见路线可以分成四类：

1. CAD 平台 API：直接读取文档、零件、装配、视图、导出文件。
2. CAD 几何内核：读取 STEP/B-Rep，分析面、边、体、孔、壳、包围盒、截面。
3. CAD 内置脚本：用 FeatureScript、Creo Toolkit、宏等方式在 CAD 内部建立可重复工具。
4. 视觉 UI 自动化：用截图、OCR、模板匹配、目标检测辅助点击和状态确认。

本项目应该采用混合路线：API 和几何内核作为主线，视觉自动化作为补充，不把截图点击当成唯一入口。

## 路线 1：Onshape REST API

Onshape 的 REST API 可以把 CAD 数据当作稳定的数据源来访问。官方说明中明确提到，它可以用 Python、JavaScript、Go、Rust、Java 等任何能发送 HTTP 请求的语言访问；API 可用于获取零件元数据、导出几何、读取装配结构、监听文档变化和写回属性。

适合我们做：

- 上传、替换、导出 STEP。
- 获取 documentId、workspaceId、elementId、partId。
- 获取 Part Studio / Assembly 的结构信息。
- 获取质量属性、体积、材料、缩略图或标准视图。
- 用稳定 ID 管理项目，而不是依赖本地文件路径或浏览器界面。

局限：

- STEP 导入后的模型通常没有原始参数特征树。
- API 能告诉我们“有哪些实体、几何属性是什么”，但不会天然知道“这是左壳、这是铜排、这是插针”。
- 语义命名仍需要用户工程知识参与，或者由我们建立规则库。

结论：

这是本项目的主入口。浏览器 UI 不稳定时，API 仍然应能继续工作。

资料：

- Onshape REST API blog: https://www.onshape.com/en/blog/cloud-native-cad-rest-api

## 路线 2：FeatureScript / CAD 内置脚本

Onshape 的 FeatureScript 是内置在 Onshape 中的参数化建模语言。官方文档说明，Onshape 的标准特征如 Extrude、Fillet、Helix 等本身就是 FeatureScript 函数；用户也可以创建 custom feature，并使用 Onshape Standard Library。

适合我们做：

- 把“扭簧生成器”“壳料厚度检查”“柱子/卡扣生成器”做成可复用 custom feature。
- 在 Onshape 内部生成可编辑几何，而不是只上传死 STEP。
- 让技能从 Markdown + Python 脚本，升级为 Onshape 内可直接使用的建模工具。

局限：

- 对导入的复杂 STEP 做自动语义识别，不是 FeatureScript 最强项。
- FeatureScript 更适合生成和修改参数化几何，不适合代替完整的视觉操作程序。

结论：

中期重点。短期先用 Python/OCP 验证算法，再把稳定算法迁移为 FeatureScript。

资料：

- FeatureScript docs: https://cad.onshape.com/FsDoc/index.html
- Onshape Custom Features: https://www.onshape.com/en/features/custom-features

## 路线 3：STEP / B-Rep 几何识别

对 STEP 这类交换文件，前人的主流方法不是截图，而是读取 B-Rep 的拓扑结构。Open CASCADE 的 STEP processor 文档说明，STEP 文件包含产品信息、几何、拓扑和装配结构。

工业和研究中常用的识别方法包括：

- 遍历实体、面、边、曲面类型。
- 识别圆柱面、平面、孔、凸台、凹槽、倒角、圆角。
- 计算包围盒、体积、中心、投影轮廓、截面。
- 建立 face adjacency graph 或 attributed adjacency graph。

Analysis Situs 的特征识别框架尤其值得参考：它把 B-Rep 转成 AAG，即带属性的面邻接图。图节点代表面，边代表面之间的邻接关系，并标记凹/凸二面角。这样“特征”就可以被看成图中的子图。

适合我们做：

- 从 STEP 中稳定获取每个实体的外形、空间位置、尺寸。
- 自动识别候选孔、柱、卡扣、端子槽、插针孔、铜排空间。
- 做标准左视图、剖面图、隐藏某类实体后的投影图。
- 在不依赖 Onshape 浏览器的情况下分析内部空间关系。

局限：

- 语义识别要靠规则逐步积累，不能一开始就全自动理解复杂壳料。
- 导入 STEP 后的实体命名可能很差，需要我们建立“用户命名表”。
- 复杂塑胶件的特征相互交叠，单纯规则可能不够，需要人机协作确认。

结论：

这是本项目最关键的技术主线。我们应优先做一个 `step-inspector`：读取 STEP，输出实体清单、包围盒、颜色、标准视图、截面、候选功能特征。

资料：

- Open CASCADE STEP processor: https://dev.opencascade.org/doc/occt-7.0.0/overview/html/occt_user_guides__step.html
- Analysis Situs feature recognition: https://www.analysissitus.org/features/features_feature-recognition-framework.html
- Analysis Situs AAG: https://analysissitus.org/features/features_aag.html

## 路线 4：FreeCAD / OpenCascade 脚本化中转

FreeCAD 基于 Open CASCADE，并有完整 Python 脚本环境。对于传统结构工程师，它的价值不是取代 Creo 或 Onshape，而是作为可脚本化 CAD 中转站。

适合我们做：

- 批量打开 STEP。
- 导出视图、截面、DXF、STL。
- 用 Python 读取对象树和几何属性。
- 在本地离线执行 CAD 数据清洗。

局限：

- 大型 STEP 可能很慢。
- FreeCAD 对复杂导入模型的交互体验不一定好。
- 仍然需要我们封装脚本，不能依赖手工操作。

结论：

可以作为本地工具链备选。优先级低于直接使用 OCP/CadQuery，但对调试和可视化有帮助。

资料：

- FreeCAD scripting basics: https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FreeCAD_Scripting_Basics.md
- FreeCAD source documentation: https://freecad.github.io/SourceDoc/index.html

## 路线 5：截图识别和 GUI 自动化

截图自动化不是新东西。SikuliX 很早就用截图和 OpenCV 模板匹配来做 GUI 自动化；现代 GUI agent 则进一步使用 OCR、目标检测、图标识别和视觉语言模型。

SikuliX 的路线：

- 保存按钮、菜单、图标等 PNG 模板。
- 运行时截图。
- 用 OpenCV `matchTemplate()` 找模板位置。
- 再执行点击、等待、键盘输入。

Microsoft OmniParser 的路线：

- 把 GUI 截图解析成结构化元素。
- 检测可交互区域。
- 为图标和区域生成语义描述。
- 让大模型根据结构化屏幕元素生成操作。

适合我们做：

- 判断 Onshape/Creo 当前界面状态。
- 确认是否登录、是否进入文档、是否出现错误提示。
- 快速点击固定工具栏按钮或视图立方体。
- 当 API 做不到时，辅助完成 UI 操作。

局限：

- CAD 画布是 WebGL/桌面图形，普通 DOM 自动化基本读不到零件语义。
- 纯截图点击容易受分辨率、缩放、主题、窗口位置、语言影响。
- 训练深度学习模型前，需要大量稳定标注数据。
- 对真正的几何关系判断，截图不如 B-Rep 可靠。

结论：

这是重要补充路线，但不应作为主线。我们可以先做“确定性截图工具”，积累数据，再考虑深度学习。

资料：

- SikuliX docs: https://sikulix.github.io/docs/
- Microsoft OmniParser: https://www.microsoft.com/en-us/research/publication/omniparser-for-pure-vision-based-gui-agent/
- OmniParser arXiv: https://arxiv.org/abs/2408.00203

## 对本项目的建议架构

短期先做三个小工具：

1. `onshape-client`
   - 上传/替换 STEP。
   - 拉取元素、零件、partId、标准视图。
   - 导出 API 原始 JSON，保证过程可追溯。

2. `step-inspector`
   - 用 OCP/CadQuery 读取 STEP。
   - 输出实体包围盒、颜色、体积、投影视图、截面。
   - 支持“隐藏某实体后出标准左视图”。

3. `screen-checker`
   - 只负责截图、OCR、模板识别、状态确认。
   - 不承担几何理解。

中期把稳定能力升级为：

- 零件语义命名表。
- 壳料/铜排/插针/齿轮组规则库。
- 塑胶件工艺规则检查：壁厚、脱模方向、倒扣、多层结构风险。
- Onshape FeatureScript 自定义特征。

长期可以发展成：

- AI CAD agent MCP。
- 面向智能断路器/电表结构设计的专用 skill 仓库。
- 基于截图和 B-Rep 双输入的 CAD 操作与结构理解系统。

## 当前结论

我们遇到的问题是有价值的，不是单个操作失败。

正确方向不是让 agent 更努力地“看屏幕”，而是建立一套分层系统：

- API 负责稳定访问 CAD 数据。
- B-Rep 负责真实几何理解。
- 用户工程知识负责语义命名和设计判断。
- 截图识别负责 UI 状态确认和必要操作。

这正是本 GitHub 项目应该解决的第一个核心问题。

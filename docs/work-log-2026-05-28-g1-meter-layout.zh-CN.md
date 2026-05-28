# 工作日志：G1-1P 到 2P 电表布局 2026-05-28

## 今天解决的问题

今天的核心问题不是“马上画出新电表”，而是让 agent 能稳定获得工程师真正想看的 CAD 画面。

最终确认了一套可复用流程：

1. 使用已经按产品正面校正的 `front_aligned` STEP。
2. 用本地 STEP/B-Rep 读取实体。
3. 生成与 Onshape 视图立方体一致的左视图。
4. 隐藏指定外壳，观察内部空间关系。
5. 在确认视图方向正确后，再做铜排、18pin、齿轮组、隔离壳等布局推演。

这套流程被沉淀为新 skill：`skills/step-inspector`。

## 走过的弯路

### 1. 把数学投影误当成工程师左视图

最开始只把 STEP 投影到 Y-Z 平面，但没有让屏幕方向匹配 Onshape 右上角视图立方体的 `Left`。结果连续输出了右视图。

结论：

- 正确投影平面不等于正确屏幕方向；
- 视图必须以用户在 CAD 里点击 `Left` 后看到的画面为准；
- 对本项目，确认参数为 `view-from=xmax` 和 `mirror-y=true`。

### 2. 用颜色/实体顺序猜零件身份

早期尝试用 Onshape part 顺序、STEP 实体顺序和颜色去判断左右壳。这条路不可靠。

结论：

- 颜色和实体顺序只能帮助复现图，不应作为语义身份依据；
- 零件名、左右壳、铜排、18pin、齿轮组等工程语义必须由几何位置和工程师反馈共同确认。

### 3. 在 G1 原图中凭空猜铜排

G1 原 1P 左侧没有新电表的零线铜排。铜排位置不能从 G1 图里直接猜。

结论：

- 新电表左铜排位置必须从 S2-2P 左视图继承；
- 先在 S2-2P 中找上下接线框；
- 再找嵌在接线框里的铜排起点和终点；
- 最后把端点相对壳料的位置关系迁移到 G1 功能区。

### 4. 把接线框区域画得过大

一开始用很大的橙色框表达接线区域，容易误导为铜排本体。用户指出实际铜排在左视图中只是靠断路器后侧的一条约 `1.8 mm` 薄片。

结论：

- 后续铜排应画成贴后侧的窄薄片；
- 接线框可以作为参考，但不能用大框替代铜排本体。

## 获得的成果

### 1. 新增 Step Inspector skill

新增文件：

```text
skills/step-inspector/SKILL.md
skills/step-inspector/scripts/render_left_view.py
```

能力：

- 读取 STEP；
- tessellate 实体；
- 输出 Y-Z 侧视图；
- 支持隐藏指定实体；
- 支持 `--view-from` 和 `--mirror-y` 校准工程视图方向；
- 支持给实体编号，方便人机共同确认。

### 2. 确认 G1-1P 左视图隐藏左壳基准图

确认规则：

```text
view-from = xmax
mirror-y = true
hidden shell index = 20
```

这成为后续 G1-1P 电表功能区讨论的基准。

### 3. 确认 S2-2P 去掉左壳左视图

用户确认 S2-2P 的目标图为：

```text
corrected_left_view_s2_hide_10.png
```

该图用于寻找左铜排和接线框参考。

### 4. 理解“强弱电交叉，因此新增左中壳”

今天达成的工程判断：

- 电表左铜排是强电路径；
- 18pin、齿轮组定位板、电机/控制板属于弱电/控制系统；
- 铜排需要参考 S2-2P 接线框位置，并尽量直、短、少折弯；
- 18pin 位于左下，齿轮组位于中右；
- 弱电连接从 18pin 到齿轮/电机控制区域时，会与强电铜排所在空间发生交叉；
- 因此新增左中壳不是多余塑胶件，而是强弱电分层、隔离、定位和装配顺序的结构基础。

### 5. 建立 G1-1P-528 命名提案

新增文件：

```text
docs/g1-1p-528-part-naming-proposal-0528.zh-CN.md
```

内容包括：

- Onshape 推荐格式；
- 31 个零件的第一版英文名；
- 中文理解；
- 置信度；
- 依据和待用户校正项。

## 文件格式结论

Onshape 更偏好 Parasolid B-rep：

```text
.x_t / .x_b
```

STEP 仍适合供应商和跨 CAD 交换：

```text
.stp / .step
```

建议后续：

- 给 Onshape/agent 分析：优先尝试 Parasolid，如果 Creo 导出稳定；
- 给供应商/模具厂：继续保留 STEP；
- 内部源文件：保留 Creo `.prt/.asm`；
- GitHub：只提交脚本、流程、skill、脱敏说明，不提交真实公司 CAD 文件。

## 今天形成的公开仓库内容

新增/更新：

```text
docs/cad-access-and-vision-automation-research.zh-CN.md
docs/g1-1p-left-view-calibration-0528.zh-CN.md
docs/g1-1p-528-part-naming-proposal-0528.zh-CN.md
docs/work-log-2026-05-28-g1-meter-layout.zh-CN.md
skills/step-inspector/SKILL.md
skills/step-inspector/scripts/render_left_view.py
requirements.txt
```

## 下一步

1. 用户批改零件命名提案。
2. 生成 `partId -> final_name` CSV。
3. 尝试用 Onshape API 批量更新零件名。
4. 继续基于确认左视图设计功能区铜排、左中壳、隔离壁。
5. 把稳定流程抽象成更强的 `step-inspector`：自动输出候选壳体、端子区、连接器区、齿轮区。


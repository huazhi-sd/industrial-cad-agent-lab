# G1-1P 左视图校准记录 0528

## 结论

在私有 `G1-1P-528` 项目中，用户确认真正需要查看的图片是：

```text
<private-project>\corrected_left_view_g1_hide_other_shell_candidate.png
```

这张图用于后续 2P 电表功能区布局讨论，尤其是：

- 左壳隐藏后的内部空间关系；
- 齿轮组位置；
- 18pin 插针位置；
- 零线铜排/锰铜采样段的直线走向；
- 新增左中壳如何隔离强电区和弱电区。

## 正确命令

```powershell
python .\skills\step-inspector\scripts\render_left_view.py `
  --step <private-project>\g1-1p-528_front_aligned.step `
  --output <private-project>\corrected_left_view_g1_hide_other_shell_candidate.png `
  --title "G1-1P corrected LEFT view - hide other shell candidate" `
  --hide 20 `
  --label-solids `
  --view-from xmax `
  --mirror-y `
  --tolerance 1.0
```

## 关键校准点

用户在 Onshape 中的操作逻辑是：

1. 模型已经按断路器使用方向摆正；
2. 有扳手和三个盖子的面是正面；
3. 有轨道卡的一面是背面；
4. 点击右上角视图立方体的 `左`，得到用户口中的左视图。

本地脚本必须复现这个屏幕方向，而不能只说“数学上沿 X 投影就是左视图”。

## 错误路径

以下路径已经证明会误导布局：

- 只做 Y-Z 投影但不镜像屏幕方向；
- 依赖本地坐标猜左/右；
- 依赖 STEP 实体顺序、颜色顺序判断左右壳；
- 输出右视图后称为左视图；
- 在视图方向未确认前叠加铜排草图。

## 对后续工作的要求

后续所有基于这套 STEP 的布局图，必须先确认使用同一校准：

```text
view-from = xmax
mirror-y = true
hidden shell index = 20
```

在进入铜排布局、左中壳隔离壁、强弱电区域划分之前，必须优先使用这张确认图作为底图。

如果后续更换 STEP 文件或重新上传 Onshape，必须重新做一次左右视图校准，不能沿用本次 part index。

## 2026-05-28 铜排位置修正

铜排位置不能从 G1 原 1P 图里直接猜，因为原 1P 左侧没有电表用零线铜排。

正确来源是：

1. 在 `S2-2P` 的确认左视图中找到上下接线框；
2. 找到嵌在接线框里的铜排起点和终点；
3. 将铜排端点相对壳料/接线框的位置关系迁移到 G1 功能区。

用户确认：在左视图中，实际铜排起点和终点不是接线框中心，而是在上下接线框区域的最左侧，也就是断路器后侧，表现为约 `1.8 mm` 的薄片。

因此后续图中铜排应按“贴后侧的薄铜片”表达，而不是画在橙色接线框区域中间。

当前修正版标注图：

```text
<private-project>\g1_left_view_s2_busbar_rear_thin_strip_annotation_0528.png
```

这张图仍是布局讨论图，不是最终铜排设计。它只表达：强电铜排参考 S2 接线框并贴后侧薄片布置；弱电 18pin 到齿轮组的连接路径会与强电铜排所在平面产生交叉/隔离需求。

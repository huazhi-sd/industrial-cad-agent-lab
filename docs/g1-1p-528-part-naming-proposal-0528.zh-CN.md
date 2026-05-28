# G1-1P-528 零件命名第一版

## 文件格式建议

Onshape 官方文档明确说明：`Parasolid B-rep (.x_t / .x_b)` 是 Onshape 偏好的导入格式。`STEP (.stp / .step)` 也受支持，但 STEP 主要保留几何、装配结构和颜色，不会保留原始特征树。

因此后续建议：

- 如果 Creo 能稳定导出 Parasolid：优先给 Onshape 用 `.x_t` 或 `.x_b`。
- 如果要和供应商、模具厂、其他 CAD 通用交换：继续用 `.stp/.step`。
- 如果要保留 Creo 原始参数特征：同时归档 `.prt/.asm`，但不要指望 Onshape 像 Creo 一样完整编辑原始特征。
- 如果是给 agent 做分析：保留一份 front-aligned 的 `.step` 或 `.x_t`，并配套零件命名表。

## 命名规则

英文名建议用小写蛇形命名，方便脚本、CSV 和 API 使用。

建议格式：

```text
zone_function_detail
```

示例：

```text
housing_left_shell
mechanism_large_output_gear
connector_18pin_row_a
terminal_upper_cover
```

## 本次视图校准前提

本表基于：

```text
<private-project>\g1-1p-528_front_aligned.step
<private-project>\corrected_left_view_g1_hide_other_shell_candidate.png
```

已确认：

- `index 20` 是隐藏后得到正确左视图的左壳候选；
- 左视图校准参数为 `view-from=xmax` 与 `mirror-y=true`；
- 齿轮组应以可见齿轮本体为主要识别依据；
- 新电表铜排位置来自 S2-2P 左视图，不从 G1 原图中猜。

## 命名提案表

| index | partId | 建议英文名 | 中文理解 | 置信度 | 依据/备注 |
| --- | --- | --- | --- | --- | --- |
| 0 | JFD | mechanism_small_shaft_or_pin_01 | 小轴/销钉 01 | low | 细长小件，位置在机构上部，需人工确认 |
| 1 | JFH | mechanism_motor_or_actuator_block | 电机/执行器块候选 | medium | 齿轮组附近的灰色块状件 |
| 2 | JFL | mechanism_motor_mount_bracket | 电机/机构支架候选 | medium | 蓝色支架状件，靠近齿轮机构 |
| 3 | JFP | mechanism_worm_or_drive_support | 蜗杆/传动支撑候选 | low | 齿轮组附近，形态需实物确认 |
| 4 | JFT | mechanism_small_spur_gear | 小直齿轮 | high | 左视图中可见橙色小齿轮 |
| 5 | JFX | mechanism_large_spur_gear | 大直齿轮 | high | 左视图中可见大齿轮 |
| 6 | JFb | mechanism_cam_or_output_disc | 凸轮/输出盘候选 | medium | 齿轮组输出附近圆形件 |
| 7 | JFf | mechanism_handle_link_or_latch | 扳手联动/锁扣候选 | medium | 靠近扳手和齿轮输出区 |
| 8 | JFj | mechanism_actuator_body | 执行器主体候选 | medium | 位于电机/齿轮支撑附近 |
| 9 | JFn | mechanism_upper_metal_plate | 上部金属/支撑片候选 | low | 灰色小件，需确认作用 |
| 10 | JFr | handle_green_toggle | 分合闸扳手 | high | 用户已确认绿色扳手不变，位置与形态匹配 |
| 11 | JFv | terminal_upper_small_contact | 上端子小接触件候选 | low | 端子区小件，需结合 S2/实物确认 |
| 12 | JFz | terminal_upper_pin_or_insert | 上端子插片候选 | low | 上部端子附近小件 |
| 13 | JF3 | terminal_lower_small_contact | 下端子小接触件候选 | low | 下部端子附近小件 |
| 14 | JF7 | spring_torsion_original | 原扭簧 | medium | 细长弹簧/钢丝类特征，需与此前扭簧问题核对 |
| 15 | JF/ | connector_can_5pin_or_side_pcb_part | 旧 CAN/侧边接口候选 | medium | 原 5PIN CAN 区域相关可能性高 |
| 16 | KFDB | terminal_upper_cover_or_block | 上端子盖/端子块候选 | medium | 上部接线区域件 |
| 17 | KFHB | terminal_upper_long_cover | 上部端子长盖/罩 | medium | 横跨宽度的上部端子区域件 |
| 18 | KFLB | terminal_lower_long_cover | 下部端子长盖/罩 | medium | 横跨宽度的下部端子区域件 |
| 19 | KFPB | pcb_or_mechanism_partition_plate | PCB/机构隔板候选 | medium | 薄板状件，可能遮挡齿轮/弱电结构 |
| 20 | KFTB | housing_left_shell | 左壳 | high | 隐藏后得到用户确认的正确左视图 |
| 21 | KFXB | housing_inner_or_middle_shell | 中壳/内壳候选 | medium | 大壳体之一，需确认是否为中壳或内支架 |
| 22 | KFbB | connector_side_pin_strip | 侧边连接针条候选 | low | 细长连接件 |
| 23 | KFfB | din_rail_rear_clip_or_back_feature | 后部轨道卡/背部特征候选 | medium | 靠后侧长条结构，可能与导轨卡相关 |
| 24 | KFjB | connector_18pin_part_a | 18pin 连接器部件 A | medium | 18pin 区域附近条状件 |
| 25 | KFnB | connector_18pin_part_b | 18pin 连接器部件 B | medium | 18pin 区域附近条状件 |
| 26 | KFrB | connector_18pin_row_a | 18pin 插针排 A | high | 18pin 区域附近，和用户确认区域吻合 |
| 27 | KFvB | connector_18pin_housing | 18pin 连接器座 | high | 左下 18pin 区域主体候选 |
| 28 | KFzB | connector_18pin_row_b | 18pin 插针排 B | high | 18pin 区域附近，和用户确认区域吻合 |
| 29 | KF3B | housing_right_shell_or_cover | 右壳/右侧大壳体候选 | medium | 大壳体之一，隐藏 20 后仍可见 |
| 30 | KF7B | mechanism_intermediate_gear_or_cam | 中间齿轮/凸轮候选 | medium | 齿轮组附近小机构件 |

## 需要用户重点校正的项目

第一批建议优先校正这些：

- `20 housing_left_shell` 是否确认为左壳；
- `29 housing_right_shell_or_cover` 是否为右壳；
- `21 housing_inner_or_middle_shell` 到底是中壳、内壳还是其他大件；
- `4/5/30` 齿轮组命名是否符合你们内部叫法；
- `24-28` 是否确认为 18pin 相关部件；
- `15/16/17/18` 是否属于端子盖、CAN 接口、上下盖或其他。

## 后续批量改名流程

1. 用户在本表中直接改建议英文名；
2. agent 生成 `partId -> final_name` CSV；
3. 用 Onshape API 批量更新 Part metadata；
4. 再导出一份截图和 JSON，确认 Onshape 中名称已更新。

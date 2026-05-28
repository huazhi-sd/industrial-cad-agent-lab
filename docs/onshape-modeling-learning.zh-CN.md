# Onshape/AI 建模学习路线

## 目标

让用户通过自然语言、标注图和工程判断指挥 Agent 完成建模，而不是频繁手动操作 Onshape。Agent 需要逐步掌握：

- Onshape 文档/文件夹/导入导出管理；
- Part Studio 建模策略；
- Assembly 装配和参考模型组织；
- FeatureScript 自定义特征；
- Onshape API 自动化；
- CadQuery/OCP 本地参数化建模；
- 导入 STEP 后的整理、脱敏、重命名和参考建模流程。

## 学习资料优先级

### 1. Onshape 官方学习中心

用途：学习 Onshape 的标准建模习惯，而不是把 Creo/SolidWorks 的习惯硬搬过来。

链接：

```text
https://learn.onshape.com/
```

重点：

- Onshape Fundamentals；
- Part Studios；
- Assemblies；
- Drawings；
- Document management。

### 2. Onshape 导入 CAD 官方文档

用途：理解 STEP、Parasolid、装配导入、扁平导入、故障零件、引用断裂等问题。

链接：

```text
https://cad.onshape.com/help/Content/translation.htm
https://cad.onshape.com/help/Content/using_importedCAD.htm
https://cad.onshape.com/help/Content/Document/importing_files.htm
```

当前经验：

- Onshape 导入装配 STEP 会自动拆出大量子装配 tab；
- 项目参考外形优先使用 `flattenAssemblies=true` 的扁平导入；
- 正式编辑模型前，先区分“参考模型”和“可编辑设计模型”。

### 3. FeatureScript

用途：把重复建模动作封装为 Onshape 内部自定义特征。

链接：

```text
https://cad.onshape.com/FsDoc/index.html
https://cad.onshape.com/FsDoc/intro.html
```

适合本项目的方向：

- 自动生成壳体定位柱；
- 自动生成卡扣/筋位基础特征；
- 自动生成螺钉柱/铆钉孔；
- 自动生成连接器开孔阵列；
- 自动生成 18pin 孔阵列参考特征。

### 4. Onshape API

用途：减少手动操作，完成上传、导入、导出、查询 element、整理文档等任务。

当前已验证：

```text
POST /api/v6/blobelements/d/{documentId}/w/{workspaceId}
GET  /api/v10/translations/{translationId}
GET  /api/v10/documents/d/{documentId}/w/{workspaceId}/elements
```

经验：

- 大 STEP 上传使用 `multipart/form-data`；
- 上传返回 `translationId`；
- 等待 `requestState=DONE` 后读取 `resultElementIds`；
- 文件夹内创建文档时要带 `parentId`，否则会跑到个人根目录。

### 5. CadQuery / OCP

用途：用 Python 生成可控的参数化 STEP 草模，适合 Agent 自动建模。

链接：

```text
https://cadquery.github.io/
https://cadquery.readthedocs.io/
```

适合本项目的方向：

- 扭簧；
- 铆钉；
- 铜排占位；
- PCB/显示屏/连接器占位；
- 2P 壳料粗略空间块；
- 结构方案 A/B 的快速草模。

## 项目执行方式

### 用户负责

- 产品意图；
- 哪些结构必须保留；
- 哪些区域可以改；
- 装配逻辑和工程风险；
- 对草图/模型进行判断。

### Agent 负责

- 整理需求；
- 查资料；
- 建立 Onshape 文档；
- 上传/导入/整理参考模型；
- 生成草图、草模和对比方案；
- 把经验写入仓库；
- 遇到失败时记录原因和修正方案。

## 当前 G1-2P 项目建模策略

1. 不直接在混乱旧文档里继续做。
2. 在公司文件夹中使用 `00_G1-2P-meter-0528-reference` 作为参考入口。
3. `g1-1p-528` 用作现有产品参考。
4. `s2-2p-0612` 用作 2P 外形参考。
5. 先做空间/壳料草图，再做可编辑草模。
6. 先表达功能区/分断区、左壳/中壳/右壳/左中壳方案，不急于细节特征。
7. 等用户讲清齿轮组、铜排、PCB、显示屏、翻盖方式后，再收敛壳料结构。

## 长期目标

把“用户指挥 + Agent 建模”发展成一套稳定流程：

1. 用户给 STEP/截图/口述。
2. Agent 生成项目 brief。
3. Agent 建立干净 Onshape 文档。
4. Agent 整理参考模型和命名。
5. Agent 生成草图和草模。
6. 用户评审。
7. Agent 迭代模型。
8. 经验沉淀为 skill、脚本和文档。

核心原则：用户不为了适应 Agent 增加大量表格工作；Agent 通过学习和文档化来适应用户的工程表达方式。

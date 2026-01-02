# 实施计划与任务列表

本文档根据 `设计文档-配置文件.md` 的要求，制定了详细的系统修改计划。

---

## 需求总览

| # | 需求描述 | 优先级 | 复杂度 |
|---|---------|-------|--------|
| 0 | 为项目编写 README | 中 | 低 |
| 1 | 数据库配置通过配置文件实现，取消管理面板和比对历史两个页面 | 高 | 中 |
| 2 | Minimap2 的比对结果说明标题还是 BLAST（修复显示错误） | 中 | 低 |
| 3 | BLAST 结果 sseqid 不对，目前的结果都是 0（修复解析错误） | 高 | 中 |
| 4 | 将 BLAST 的比对模式作为可选择的列表 | 中 | 低 |

---

## 任务 0: 项目文档完善

### 目标
为项目创建完整的 README 文档，帮助用户理解和部署系统。

### 任务列表
- [ ] 创建 `README.md`
  - [ ] 项目简介与功能特性
  - [ ] 系统架构说明（FastAPI + Vue 3 + Celery + Redis）
  - [ ] 安装与部署指南（Docker Compose）
  - [ ] 配置说明（重点说明 `databases.yaml` 配置方式）
  - [ ] 使用说明与 API 文档

---

## 任务 1: 数据库配置重构与页面清理

### 目标
将数据库管理从 UI 界面操作转变为基于配置文件的方式，简化系统架构，删除不必要的页面。

### 现状分析
- **后端**: `app/database_config.py` 已支持 YAML 配置（`/data/databases.yaml`）
- **后端路由**: `app/routers/databases.py` 提供上传、删除、索引等 API
- **前端页面**:
  - `Admin.vue` - 管理面板页面（需删除）
  - `History.vue` - 比对历史页面（需删除）
- **前端路由**: `router/index.ts` 包含 `/admin` 和 `/history` 路由
- **前端导航**: `App.vue` 导航栏包含 "管理面板" 和 "比对历史" 入口

### 任务列表

#### 后端重构
- [ ] 设计并记录 `databases.yaml` 配置文件格式
  ```yaml
  # 示例格式
  example.fa:
    species: "Human"
    genome_version: "GRCh38"
    sequence_type: "genome"
    description: "人类参考基因组"
  ```
- [ ] 修改 `app/routers/databases.py`
  - [ ] 保留 `GET /api/databases` (读取配置，列出数据库)
  - [ ] 保留 `POST /{db_id}/index` (创建索引)
  - [ ] 移除 `DELETE /{db_id}` (删除数据库)
  - [ ] 移除 `PUT /{db_id}` (更新元数据)
  - [ ] 移除 `POST /reference` (上传参考文件)
  - [ ] 保留 `POST /upload` (用于上传查询序列文件)

#### 前端清理
- [ ] 删除页面组件
  - [ ] 删除 `frontend/src/pages/Admin.vue`
  - [ ] 删除 `frontend/src/pages/History.vue`
  - [ ] 删除 `frontend/src/components/ReferenceManager.vue`
- [ ] 修改 `frontend/src/router/index.ts`
  - [ ] 移除 `Admin` 和 `History` 的导入
  - [ ] 移除 `/admin` 和 `/history` 路由定义
- [ ] 修改 `frontend/src/App.vue`
  - [ ] 从 `navItems` 数组中移除 "管理面板" 和 "比对历史" 条目
- [ ] 修改 `frontend/src/api/index.ts`
  - [ ] 移除 `deleteDatabase`、`updateDatabase`、`uploadReference` 等不再需要的 API 函数

---

## 任务 2: 修复 Minimap2 结果标题显示错误

### 目标
修复前端结果表格中，Minimap2 结果的列说明标题错误显示为 "BLAST" 的问题。

### 现状分析
- **文件**: `frontend/src/components/ResultTable.vue`
- **问题**: 第 193 行的标题固定为 "表格列说明（参照 BLAST -outfmt 6）"，未根据 `tool` 属性动态变化

### 任务列表
- [ ] 修改 `frontend/src/components/ResultTable.vue`
  - [ ] 将第 193 行的标题改为根据 `props.tool` 动态显示
    - 若 `tool === 'blast'`: "BLAST 比对结果列说明"
    - 若 `tool === 'minimap2'`: "Minimap2 比对结果列说明"

---

## 任务 3: 修复 BLAST 结果 sseqid 解析错误

### 目标
修复 BLAST 比对结果中 `sseqid`（目标序列 ID）显示为 0 的问题。

### 现状分析
- **文件**: `app/tools/blast.py`
- **解析逻辑** (第 77-80 行):
  ```python
  hits.append({
      "qseqid": query_title,
      "sseqid": description.get("accession", ""),
      ...
  })
  ```
- **问题**: BLAST JSON 输出格式中，如果 FASTA 序列头没有标准 accession 格式，`accession` 字段可能不存在或为空/0。应优先使用 `id` 或从 `title` 中提取序列 ID。

### 任务列表
- [ ] 调试验证
  - [ ] 检查一个实际的 BLAST JSON 输出文件，确认 `description` 对象的结构
  - [ ] 确认 `accession`、`id`、`title` 字段的实际值
- [ ] 修改 `app/tools/blast.py` 中的 `parse_result` 方法
  - [ ] 优先使用 `description.get("id")` 作为 `sseqid`
  - [ ] 若 `id` 不存在，则使用 `description.get("accession")`
  - [ ] 若都不存在，则从 `description.get("title", "")` 中提取第一个空格前的字符串作为序列 ID
  - [ ] 示例修复代码:
    ```python
    sseqid = description.get("id") or description.get("accession") or ""
    if not sseqid:
        title = description.get("title", "")
        sseqid = title.split()[0] if title else ""
    ```

---

## 任务 4: BLAST 比对模式选择功能

### 目标
允许用户在提交 BLAST 任务时选择具体的比对模式（task 参数），并显示各模式的适用说明。

### 现状分析
- **后端**: `app/tools/blast.py` 第 42 行已支持 `task` 参数，默认为 `blastn`
- **前端**: `Home.vue` 第 78-79 行目前仅在短序列时自动设置 `task: 'blastn-short'`
- **缺失**: 没有提供用户可见的选择界面和模式说明

### 可选模式说明
| 模式 | 适用场景 |
|-----|---------|
| `blastn` | 通用核酸序列比对（默认） |
| `blastn-short` | 短序列比对 (< 50bp)，如引物、探针 |
| `megablast` | 高相似度长序列比对，速度快 |
| `dc-megablast` | 不连续 megablast，适用于远缘同源序列 |

### 任务列表
- [ ] 修改 `frontend/src/pages/Home.vue`
  - [ ] 添加 "比对模式" 下拉选择框（仅在 `selectedTool === 'blast'` 时显示）
  - [ ] 选项：`blastn` (默认), `blastn-short`, `megablast`, `dc-megablast`
  - [ ] 添加模式说明文本或 tooltip
  - [ ] 修改 `submitJob` 函数，将选中的模式通过 `options.task` 传递给后端
  - [ ] 移除或调整现有的 `useShortQuery` 自动检测逻辑（可保留为辅助提示）

---

## 验证计划

### 功能测试
1. **配置文件验证**: 手动编辑 `databases.yaml`，确认前端能正确读取并显示数据库列表
2. **页面清理验证**: 确认 `/admin` 和 `/history` 路由不可访问，导航栏无相关入口
3. **Minimap2 标题验证**: 执行 Minimap2 比对，确认结果页面标题正确显示
4. **BLAST sseqid 验证**: 执行 BLAST 比对，确认 `sseqid` 列正确显示序列 ID
5. **BLAST 模式验证**: 选择不同的 BLAST 模式（如 `megablast`），确认后端日志显示正确的 `-task` 参数

### 回归测试
- 确保基本的 BLAST/Minimap2 比对流程正常工作
- 确保多数据库选择功能正常
- 确保结果下载功能正常

---

## 实施顺序建议

1. **任务 3** (BLAST sseqid 修复) - 高优先级 Bug
2. **任务 2** (Minimap2 标题修复) - 简单快速修复
3. **任务 4** (BLAST 模式选择) - 功能增强
4. **任务 1** (数据库配置重构) - 需要较多改动
5. **任务 0** (README 文档) - 最后完成


# 项目进展总结报告 (2026-01-02)

## 1. 项目概况
**Align-Fasta** 是一个基于 Web 的序列比对服务平台，旨在为生物信息学研究人员提供便捷的 BLAST 和 Minimap2 在线比对功能。系统采用前后端分离架构（Vue 3 + FastAPI），支持大规模参考基因组管理、多数据库并行比对及可视化的结果分析。

## 2. 近期核心更新 (2026.01.02)

本次迭代主要集中在**数据库元数据管理**与**多数据库并行比对**功能的增强。

### 2.1 数据库元数据增强
- **功能描述**：为参考数据库增加了更丰富的元数据支持，不再仅限于简单的文件名。
- **新增字段**：
  - `species`: 物种名称 (如 *Oryza sativa*)
  - `genome_version`: 基因组版本 (如 *IRGSP-1.0*)
  - `sequence_type`: 序列类型 (cds, protein, genome, transcript)
  - `description`: 详细描述文本
- **实现细节**：
  - 新增 `app/database_config.py` 模块，采用 YAML 文件持久化存储元数据，无需依赖复杂的关系型数据库。
  - 前端 `ReferenceManager.vue` 新增内联编辑功能，支持用户直观地管理数据库信息。

### 2.2 多数据库并行比对支持
- **功能描述**：打破了单次只能比对一个数据库的限制，支持用户同时对多个参考基因组进行检索。
- **UI 改进**：
  - `Home.vue` 重构了数据库选择器，支持多选，并根据“物种”元数据自动分组展示，提升了在大量数据库场景下的可用性。
  - 结果列表 (`ResultTable.vue`) 新增“数据库来源”列，清晰标识每一条比对结果来自哪个参考文件。
- **后端逻辑**：
  - `jobs.py` 和 `tasks.py` 升级为支持接收数据库列表 (`db_ids`)。
  - 多个数据库的比对任务并行执行（或顺序执行，视 Celery 配置而定），结果自动合并并按得分（Bitscore/MapQ）统一排序。

### 2.3 其他改进
- **TSV 导出优化**：下载的比对结果表格中包含了 `database` 字段，方便后续分析。
- **状态可视化**：首页新增了“已选数据库”计数器和选中状态的高亮显示。

## 3. 当前系统架构

### 后端 (Python/FastAPI)
- **核心模块**：
  - `main.py`: 应用入口与路由配置。
  - `routers/databases.py`: 数据库文件管理、索引构建及元数据更新。
  - `routers/jobs.py`: 任务提交与状态查询，现支持多库列表解析。
  - `tasks.py`: Celery 异步任务定义，封装了 BLAST 和 Minimap2 的调用逻辑及结果合并。
  - `database_config.py`: **[NEW]** 基于 YAML 的元数据读写模块。
- **工具封装**：
  - `tools/blast.py` & `tools/minimap2.py`: 命令行工具的 Python 包装器，负责执行和结果解析。

### 前端 (Vue 3/TypeScript)
- **页面结构**：
  - `Home.vue`: 任务提交入口，支持文本粘贴/文件上传，多数据库选择。
  - `Result.vue`: 结果详情页，包含轮询状态检查和结果展示。
  - `Admin.vue`: 数据库管理后台，上传/删除/索引/元数据编辑。
- **状态管理**：
  - `stores/alignment.ts`: 统一管理数据库列表、工具列表及任务状态。

## 4. 关键文件清单

| 路径 | 说明 | 修改状态 (本次) |
| :--- | :--- | :--- |
| `app/models/schemas.py` | Pydantic 数据模型定义 | **Updated** (新增元数据字段) |
| `app/database_config.py` | YAML 配置管理模块 | **New** |
| `app/routers/databases.py` | 数据库 API 接口 | **Updated** (支持 PUT 更新) |
| `app/routers/jobs.py` | 任务提交 API 接口 | **Updated** (支持 db_ids) |
| `app/tasks.py` | 异步任务逻辑 | **Updated** (多库合并) |
| `frontend/src/types/index.ts` | TypeScript 类型定义 | **Updated** |
| `frontend/src/pages/Home.vue` | 首页组件 | **Updated** (多选UI) |
| `frontend/src/components/ReferenceManager.vue` | 数据库管理组件 | **Updated** (元数据编辑) |
| `frontend/src/components/ResultTable.vue` | 结果表格组件 | **Updated** (来源列) |

## 5. 下一步建议 (Next Steps)
1.  **自动化测试**：随着逻辑变复杂，建议补充后端 pytest 单元测试，特别是针对多库合并逻辑。
2.  **结果筛选**：在结果页面增加按“数据库”或“物种”筛选的功能，并在可视化图表中区分来源。
3.  **性能优化**：对于极大量的数据库并行比对，考虑引入更细粒度的任务分发或使用专门的分布式计算框架。

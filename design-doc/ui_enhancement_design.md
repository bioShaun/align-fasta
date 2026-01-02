# 前端优化设计文档

## 优化目标

1. **页面分离** - 提交页和结果页分离，提交后自动跳转到新页面显示结果
2. **完整比对表格** - 显示所有比对字段，并在页面底部添加列说明
3. **中文界面** - 所有界面文字改为中文显示

---

## 一、页面分离方案

### 现状
- 单页应用，提交和结果在同一页面
- 使用 `currentView` 切换 search/admin 视图

### 方案
引入 Vue Router，创建独立页面：

| 路由 | 组件 | 说明 |
|------|------|------|
| `/` | `HomePage.vue` | 序列提交页 |
| `/result/:jobId` | `ResultPage.vue` | 结果展示页 |
| `/admin` | `AdminPage.vue` | 数据库管理页 |
| `/history` | `HistoryPage.vue` | 历史记录页（可选） |

### 工作流程
1. 用户在 `/` 提交序列
2. 提交成功后，调用 `router.push('/result/' + jobId)`
3. 结果页自动轮询任务状态
4. 任务完成后显示完整比对结果

### 需修改文件
- [ ] 安装 `vue-router`
- [ ] 创建 `src/router/index.ts`
- [ ] 创建 `src/pages/HomePage.vue`
- [ ] 创建 `src/pages/ResultPage.vue`
- [ ] 创建 `src/pages/AdminPage.vue`
- [ ] 修改 `src/main.ts` 引入 Router
- [ ] 修改 `src/App.vue` 使用 `<router-view>`

---

## 二、完整比对表格

### BLAST 表格列（完整）

| 列名 | 字段 | 说明 |
|------|------|------|
| 查询序列 | query_name | 输入序列的名称 |
| 登录号 | accession | 数据库序列登录号 |
| 描述 | title | 序列描述信息 |
| E值 | evalue | 期望值，越小越显著 |
| 比对得分 | bit_score | 比对质量得分 |
| 一致性 | identity | 匹配碱基数量 |
| 比对长度 | align_len | 比对区域总长度 |
| 一致性百分比 | (计算值) | identity / align_len × 100% |
| 查询范围 | query_from - query_to | 查询序列上的匹配位置 |
| 目标范围 | hit_from - hit_to | 目标序列上的匹配位置 |

### Minimap2 表格列（完整）

| 列名 | 字段 | 说明 |
|------|------|------|
| 查询序列 | query_name | 输入序列名称 |
| 目标序列 | target_name | 参考序列名称 |
| 查询长度 | query_len | 查询序列总长度 |
| 目标长度 | target_len | 目标序列总长度 |
| 查询范围 | query_start - query_end | 查询序列匹配区间 |
| 目标范围 | target_start - target_end | 目标序列匹配区间 |
| 链方向 | strand | 正链(+)或负链(-) |
| 匹配碱基 | matches | 匹配的碱基数 |
| 比对长度 | block_len | 比对区块长度 |
| 映射质量 | mapq | 映射可信度(0-60) |

### 列说明组件
在表格底部添加 `<ColumnLegend>` 组件，展示各列含义。

---

## 三、中文界面

### 翻译范围

**导航栏**
- AlignFasta → 序列比对服务
- Search → 序列比对
- Databases → 数据库管理
- History → 历史记录
- Admin Panel → 管理面板

**提交页**
- Sequence Alignment Service → 序列比对服务
- Configuration → 比对配置
- Alignment Tool → 比对工具
- Target Database → 目标数据库
- Query Sequence → 查询序列
- Paste Sequence → 粘贴序列
- Upload File → 上传文件
- Short Query Optimization → 短序列优化
- Run Alignment → 开始比对

**结果页**
- Results for Job → 作业结果
- Completed with X hits → 找到 X 个匹配
- No alignment hits found → 未找到匹配结果
- Processing alignment results → 正在处理比对结果

---

## 任务列表

### 阶段一：页面路由
- [x] 1.1 安装 vue-router 依赖
- [x] 1.2 创建路由配置文件
- [x] 1.3 重构 App.vue 为路由容器
- [x] 1.4 创建 HomePage.vue（从 App.vue 提取）
- [x] 1.5 创建 ResultPage.vue
- [x] 1.6 创建 AdminPage.vue
- [x] 1.7 实现提交后自动跳转

### 阶段二：完整表格
- [x] 2.1 更新 AlignmentHit 类型定义
- [x] 2.2 增加 BLAST 表格列
- [x] 2.3 增加 Minimap2 表格列
- [x] 2.4 添加一致性百分比计算
- [x] 2.5 创建 ColumnLegend 组件
- [x] 2.6 在结果页底部显示列说明

### 阶段三：中文化
- [x] 3.1 创建 i18n 配置（或直接硬编码）
- [x] 3.2 翻译导航栏
- [x] 3.3 翻译提交页
- [x] 3.4 翻译结果页
- [x] 3.5 翻译管理页
- [x] 3.6 翻译表格列名和说明

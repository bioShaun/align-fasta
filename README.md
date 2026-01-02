# AlignFasta - Advanced Sequence Alignment Service

AlignFasta 是一个高性能的生物序列比对 Web 服务，集成并封装了经典的 **BLAST+** 和现代的 **Minimap2** 比对工具。它提供了一个现代化的 Web 界面，支持异步比对任务处理、多数据库并行搜索以及结果可视化分析。

## 主要功能

- **双引擎支持**: 集成 BLAST+ (核酸比对) 和 Minimap2 (长读段/基因组比对)。
- **多模式比对**: 支持 BLAST 的多种任务模式 (`blastn`, `blastn-short`, `megablast`, `dc-megablast`)。
- **现代化 UI**: 基于 Vue 3 和 Tailwind CSS 构建的响应式界面，具有极佳的用户体验。
- **异步处理**: 使用 Celery + Redis 进行任务排队，支持大数据量序列比对而不阻塞用户操作。
- **可视化报告**: 提供清晰的比对结果表格，支持结果按分值排序及 TSV 格式下载。
- **配置驱动**: 数据库管理通过 `databases.yaml` 配置文件驱动，简单可靠。

## 系统架构

- **Frontend**: Vue 3 + Vite + TypeScript + Pinia + Tailwind CSS
- **Backend**: FastAPI (Python 3.9+)
- **Task Queue**: Celery
- **Broker/Backend**: Redis
- **Alignment Engines**: NCBI BLAST+, Minimap2

## 快速启动 (Docker)

确保您的系统中已安装 Docker 和 Docker Compose。

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd align-fasta
   ```

2. **准备参考序列**
   将您的参考序列 FASTA 文件放置在 `data/references/` 目录下。

3. **配置数据库**
   在 `data/` 目录下创建 `databases.yaml`，示例格式如下：
   ```yaml
   example.fa:
     species: "Human"
     genome_version: "GRCh38"
     sequence_type: "genome"
     description: "人类参考基因组第38版"
   ```

4. **启动服务**
   ```bash
   docker-compose up -d
   ```

5. **访问应用**
   在浏览器中访问 `http://localhost:5173`。

## 手动安装开发环境

### 后端
```bash
cd app
pip install -r requirements.txt
# 启动 FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 启动 Celery Worker
celery -A tasks worker --loglevel=info
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 配置文件说明 (`databases.yaml`)

数据库配置文件位于 `/data/databases.yaml`，每个条目的键必须与 `data/references/` 目录下的 FASTA 文件名完全一致。

- `species`: 物种名称 (字符串)
- `genome_version`: 基因组版本 (字符串)
- `sequence_type`: 序列类型 (如 genome, transcript, cds 等)
- `description`: 详细说明文本

## 许可证

MIT License

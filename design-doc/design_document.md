# Sequence Alignment Service Design Proposal

## 1. Goal
Build a web-based service similar to [SequenceServer](https://sequenceserver.com/) that allows users to perform sequence alignments using multiple tools, specifically **BLAST+** and **Minimap2**, with an extensible architecture for adding more tools later.

## 2. System Architecture

The system will use a **Client-Server** architecture with an asynchronous job queue for handling computationally intensive alignment tasks.

```mermaid
graph TD
    Client[Web Client (Vue 3)] -->|HTTP API| Backend[Backend API (FastAPI)]
    Backend -->|Enqueue Job| Redis[Redis Message Broker]
    Backend -->|Read/Write| DB[(Database - SQLite/Postgres)]
    Backend -->|File Access| FS[File System (FASTA/Indices)]
    
    Worker[Celery Worker] -->|Poll| Redis
    Worker -->|Execute| Tools[Bioinfo Tools]
    Tools -->|BLAST+| BLAST_Bin[blastn/blastp/...]
    Tools -->|Minimap2| MM2_Bin[minimap2]
    
    Worker -->|Update Status| DB
    Worker -->|Save Results| FS
```

### 2.1 Key Components

1.  **Frontend (UI):**
    -   **Technology**: Vue 3 + Vite + Tailwind CSS.
    -   **Features**:
        -   **Dashboard**: View available reference databases with status indicators.
        -   **Search Interface**: Input query sequences (text or file upload), select target databases, select algorithm (BLAST vs Minimap2), and configure parameters (e-value, presets).
        -   **Job Monitor**: Real-time job status updates via polling or WebSocket.
        -   **Results View**: Interactive display of alignment hits.
            -   *BLAST*: Standard HTML report (tabular + graphical summary).
            -   *Minimap2*: PAF format parser, visualized as a table or a simple dotplot/synteny view.
        -   **Admin Panel**: Upload FASTA files, manage databases (format/index).

2.  **Backend (API):**
    -   **Technology**: Python 3.10+ with FastAPI.
    -   **Responsibilities**:
        -   Manage reference databases (metadata + file paths).
        -   Handle file uploads with validation.
        -   Submit alignment jobs to the queue.
        -   Serve job status and results.
        -   WebSocket support for real-time updates (optional).

3.  **Task Queue:**
    -   **Technology**: Celery + Redis.
    -   **Role**: Decouples the request from the execution. Bio-alignment jobs can take seconds to hours.
    -   **Workflows**:
        -   `create_database`: Runs `makeblastdb` or `minimap2 -d` to index files.
        -   `run_alignment`: Wrapper around subprocess calls to `blastn`, `minimap2`, etc.

4.  **Storage:**
    -   **Database**: SQLite (for simplicity/portability) or PostgreSQL (for production). Stores job history, database metadata.
    -   **File System**: Stores raw FASTA files, index files (`.nin`, `.nhr`, `.mmi`), and result output files (XML/JSON/PAF).

## 3. Detailed Features

### 3.1 Tool Integration Strategy

The system will define a generic `AlignmentTool` interface (abstract base class) for extensibility.

```python
# Conceptual interface
class AlignmentTool(ABC):
    @abstractmethod
    def index(self, fasta_path: str, output_path: str) -> bool: ...
    
    @abstractmethod
    def search(self, query_path: str, db_path: str, options: dict) -> str: ...
    
    @abstractmethod
    def parse_result(self, result_path: str) -> list[Hit]: ...
```

*   **BLAST Integration**:
    *   **Indexing**: `makeblastdb -in ref.fa -dbtype <nucl|prot> -out <db_name>`
    *   **Search**: `blastn -query query.fa -db <db_name> -outfmt 15 -out result.json`
    *   **Parsing**: Use built-in JSON support in BLAST+ (outfmt 15) for easier parsing.

*   **Minimap2 Integration**:
    *   **Indexing**: `minimap2 -d ref.mmi ref.fa` (Optional, can align directly against fasta, but indexing is faster).
    *   **Search**: `minimap2 -c ref.mmi query.fa > output.paf` (PAF is preferred for this use case).
    *   **Output**: PAF (Pairwise mApping Format) is preferred for long reads as it's lighter than SAM.

### 3.2 Data Management
*   **Database Library**: A directory where user places or uploads FASTA files.
*   **Auto-discovery**: The backend scans a specific directory on startup or on-demand to find FASTA files and check if indices exist. If not, it suggests creating them.
*   **File Validation**: Validate uploaded files are valid FASTA format before processing.

## 4. API Design

### 4.1 Core Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/api/databases` | List available reference databases |
| POST | `/api/databases` | Upload new FASTA and create database |
| DELETE | `/api/databases/{id}` | Delete a database |
| GET | `/api/tools` | List available alignment tools |
| POST | `/api/jobs` | Submit a new alignment job |
| GET | `/api/jobs/{id}` | Get job status and result |
| GET | `/api/jobs` | List past jobs (with pagination) |
| DELETE | `/api/jobs/{id}` | Delete a job and its results |

### 4.2 WebSocket (Optional)
*   `WS /api/jobs/{id}/stream`: Real-time job status updates.

## 5. Implementation Steps

### Phase 1: Prototype (MVP)
1.  **Backend Setup**: FastAPI project with basic structure (routers, models, config).
2.  **Database Management API**: Endpoints to list, upload, and manage FASTA databases.
3.  **BLAST Integration**: Implement `blastn` wrapper with synchronous execution for testing.
4.  **Basic Frontend**: Vue 3 project with simple form to submit queries and view raw results.

### Phase 2: Asynchronous Jobs & Production Readiness
1.  **Add Celery/Redis**: Move tool execution to background workers.
2.  **Job Management**: Implement job status tracking, result persistence, and history.
3.  **Integrate Minimap2**: Add `minimap2` wrapper and basic PAF parsing.
4.  **Frontend Job Monitor**: Add job status polling and result display.

### Phase 3: Advanced UI & Visualization
1.  **Results Parsing**: Convert raw outputs (JSON/PAF) into structured Vue 3 components.
2.  **Visualizations**:
    -   BLAST: Hit table with sorting/filtering, query coverage graphic.
    -   Minimap2: Dotplot visualization (using ECharts or D3.js).
3.  **Admin Panel**: Database management UI, index creation, file cleanup.

### Phase 4: Polish & Deployment
1.  **Error Handling**: Comprehensive error messages and user feedback.
2.  **Documentation**: API docs (auto-generated by FastAPI), user guide.
3.  **Docker Optimization**: Multi-stage builds, health checks, production config.
4.  **Testing**: Unit tests for backend, E2E tests for critical flows.

## 6. Technology Stack

| Component | Choice | Reason |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | Standard for bioinformatics; excellent libraries (Biopython). |
| **Web Framework** | **FastAPI** | Fast, async, auto-docs (OpenAPI/Swagger). |
| **Frontend** | **Vue 3 + Vite** | Composition API, fast HMR, good ecosystem. |
| **UI Framework** | **Tailwind CSS** | Utility-first, rapid prototyping. |
| **State Management** | **Pinia** | Official Vue 3 state management. |
| **Task Queue** | **Celery** | Robust job management, retries, monitoring. |
| **Broker** | **Redis** | Standard broker for Celery, also caching. |
| **Database** | **SQLite → PostgreSQL** | SQLite for dev, PostgreSQL for production. |
| **Containerization** | **Docker Compose** | Easy orchestration of all services. |

## 7. Directory Structure

```text
align-fasta/
├── app/                       # Backend (FastAPI)
│   ├── main.py                # API entry point
│   ├── config.py              # Configuration management
│   ├── routers/               # API routes
│   │   ├── databases.py       # Database management endpoints
│   │   ├── jobs.py            # Job submission and status
│   │   └── tools.py           # Tool listing
│   ├── models/                # Data models
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── tasks.py               # Celery tasks
│   ├── tools/                 # Tool wrappers
│   │   ├── base.py            # Abstract base class
│   │   ├── blast.py           # BLAST specific logic
│   │   └── minimap2.py        # Minimap2 specific logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Vue 3 app
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── views/             # Page views
│   │   ├── stores/            # Pinia stores
│   │   ├── api/               # API client
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── references/            # User uploaded FASTA and indices
│   └── results/               # Job outputs
├── design-doc/                # Design documentation
├── docker-compose.yml         # Orchestration
└── README.md
```

## 8. Access Control & Deployment

*   **Authentication**: None initially (Open access, similar to SequenceServer default). Can add basic auth or OAuth later if needed.
*   **Deployment**: Docker Compose for development and small-scale production.
*   **Scaling**: For larger deployments, consider Kubernetes with horizontal pod autoscaling for workers.

## 9. Future Considerations

*   **Additional Tools**: DIAMOND, MMseqs2, HMMER for protein alignments.
*   **Batch Jobs**: Support multiple query sequences in one job.
*   **Result Export**: Download results in various formats (CSV, TSV, FASTA).
*   **Job Scheduling**: Priority queues, resource limits per user.

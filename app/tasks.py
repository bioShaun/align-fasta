import os
import logging
from celery import Celery
from tools.blast import BlastTool
from tools.minimap2 import Minimap2Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "align_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Tool instances
tools = {
    "blast": BlastTool(),
    "minimap2": Minimap2Tool()
}

@celery_app.task(name="tasks.run_blast", bind=True)
def run_blast(self, query_path: str, db_paths: list, options: dict = None):
    """支持多数据库的 BLAST 比对"""
    options = options or {}
    logger.info(f"Starting BLAST job: query={query_path}, dbs={db_paths}")
    
    try:
        tool = tools["blast"]
        all_hits = []
        
        for db_path in db_paths:
            result_path = tool.search(query_path, db_path, options)
            hits = tool.parse_result(result_path)
            # 添加来源数据库标记
            db_name = os.path.basename(db_path)
            for hit in hits:
                hit['database'] = db_name
            all_hits.extend(hits)
        
        # 按分数排序
        all_hits.sort(key=lambda x: x.get('bitscore', 0), reverse=True)
        
        return {
            "status": "completed",
            "tool": "blast",
            "hits_count": len(all_hits),
            "hits": all_hits[:100],  # 限制返回数量避免数据过大
            "databases": [os.path.basename(p) for p in db_paths]
        }
    except Exception as e:
        logger.error(f"BLAST job failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(name="tasks.run_minimap2", bind=True)
def run_minimap2(self, query_path: str, db_paths: list, options: dict = None):
    """支持多数据库的 Minimap2 比对"""
    options = options or {}
    logger.info(f"Starting Minimap2 job: query={query_path}, dbs={db_paths}")
    
    try:
        tool = tools["minimap2"]
        all_hits = []
        
        for db_path in db_paths:
            result_path = tool.search(query_path, db_path, options)
            hits = tool.parse_result(result_path)
            # 添加来源数据库标记
            db_name = os.path.basename(db_path)
            for hit in hits:
                hit['database'] = db_name
            all_hits.extend(hits)
        
        # 按 mapping quality 排序
        all_hits.sort(key=lambda x: x.get('mapq', 0), reverse=True)
        
        return {
            "status": "completed",
            "tool": "minimap2",
            "hits_count": len(all_hits),
            "hits": all_hits[:100],
            "databases": [os.path.basename(p) for p in db_paths]
        }
    except Exception as e:
        logger.error(f"Minimap2 job failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(name="tasks.index_database")
def index_database(fasta_path: str, tool_name: str, output_path: str):
    logger.info(f"Indexing database: {fasta_path} using {tool_name}")
    if tool_name not in tools:
        return {"status": "error", "message": f"Tool {tool_name} not supported"}
    
    success = tools[tool_name].index(fasta_path, output_path)
    return {"status": "completed" if success else "failed", "path": output_path}

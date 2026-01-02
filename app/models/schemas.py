from pydantic import BaseModel
from typing import List, Optional, Any

class ToolInfo(BaseModel):
    name: str
    description: str

class DatabaseInfo(BaseModel):
    id: str
    name: str
    path: str
    indexed: bool
    tools: List[str]
    # 元数据字段
    species: Optional[str] = None          # 物种名称
    genome_version: Optional[str] = None   # 基因组版本
    sequence_type: Optional[str] = None    # cds/protein/genome/transcript
    description: Optional[str] = None      # 描述信息

class DatabaseUpdate(BaseModel):
    """用于更新数据库元数据"""
    species: Optional[str] = None
    genome_version: Optional[str] = None
    sequence_type: Optional[str] = None
    description: Optional[str] = None

class IndexRequest(BaseModel):
    tool: str  # 'blast' or 'minimap2'

class JobSubmit(BaseModel):
    query_filename: Optional[str] = None
    query_sequence: Optional[str] = None
    db_ids: List[str]  # 支持多数据库
    tool: str
    options: Optional[dict] = {}

class JobStatus(BaseModel):
    job_id: str
    state: str
    status: Optional[str] = None
    result: Optional[Any] = None

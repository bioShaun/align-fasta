from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import DatabaseInfo, IndexRequest
from database_config import get_db_metadata
from tasks import index_database
import os
import shutil
from typing import List

router = APIRouter(prefix="/api/databases", tags=["databases"])

# Default to Docker paths, with local fallbacks
REF_DIR = os.getenv("REF_DIR", "/data/references")
if not os.path.exists(REF_DIR):
    REF_DIR = "data/references"

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
if not os.path.exists(UPLOAD_DIR):
    UPLOAD_DIR = "data/uploads"

@router.get("/", response_model=List[DatabaseInfo])
def list_databases():
    dbs = []
    if not os.path.exists(REF_DIR):
        return []
        
    for f in os.listdir(REF_DIR):
        if f.endswith((".fa", ".fasta")):
            # Check for indices
            has_blast = os.path.exists(os.path.join(REF_DIR, f + ".nin"))
            has_mm2 = os.path.exists(os.path.join(REF_DIR, f + ".mmi"))
            
            tools = []
            if has_blast: tools.append("blast")
            if has_mm2: tools.append("minimap2")
            
            # 获取元数据
            metadata = get_db_metadata(f)
            
            dbs.append(DatabaseInfo(
                id=f,
                name=f,
                path=os.path.join(REF_DIR, f),
                indexed=len(tools) > 0,
                tools=tools,
                species=metadata.get("species"),
                genome_version=metadata.get("genome_version"),
                sequence_type=metadata.get("sequence_type"),
                description=metadata.get("description"),
            ))
    return dbs

@router.post("/{db_id}/index")
def create_index(db_id: str, request: IndexRequest):
    db_path = os.path.join(REF_DIR, db_id)
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database not found")
    
    output_path = db_path
    if request.tool == "minimap2":
        output_path = db_path + ".mmi"
    
    task = index_database.delay(db_path, request.tool, output_path)
    return {"job_id": task.id, "state": "PENDING"}

@router.post("/upload")
async def upload_for_alignment(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "size": os.path.getsize(file_path)}


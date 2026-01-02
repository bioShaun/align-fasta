from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import DatabaseInfo, IndexRequest, DatabaseUpdate
from database_config import get_db_metadata, update_db_metadata, delete_db_metadata
from tasks import index_database
import os
import shutil
import glob
from typing import List

router = APIRouter(prefix="/api/databases", tags=["databases"])

REF_DIR = "/data/references"
UPLOAD_DIR = "/data/uploads"

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

@router.put("/{db_id}")
def update_database(db_id: str, update: DatabaseUpdate):
    """更新数据库元数据"""
    db_path = os.path.join(REF_DIR, db_id)
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database not found")
    
    update_db_metadata(db_id, update.dict(exclude_none=True))
    return {"message": f"Database {db_id} updated"}

@router.delete("/{db_id}")
def delete_database(db_id: str):
    db_path = os.path.join(REF_DIR, db_id)
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database not found")
    
    # Remove the FASTA file
    os.remove(db_path)
    
    # Remove associated indices
    # BLAST indices: .nin, .nhr, .nsq, .pin, .phr, .psq etc.
    # Minimap2 index: .mmi
    pattern = os.path.join(REF_DIR, f"{db_id}.*")
    for f in glob.glob(pattern):
        try:
            os.remove(f)
        except OSError:
            pass
    
    # 删除数据库元数据配置
    delete_db_metadata(db_id)
            
    return {"message": f"Database {db_id} deleted"}

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

@router.post("/reference")
async def upload_reference(file: UploadFile = File(...)):
    if not os.path.exists(REF_DIR):
        os.makedirs(REF_DIR)
        
    file_path = os.path.join(REF_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "path": file_path}


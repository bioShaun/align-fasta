from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import JobSubmit, JobStatus
from tasks import celery_app, run_blast, run_minimap2
import os

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

UPLOAD_DIR = "/data/uploads"
REF_DIR = "/data/references"

@router.post("/", response_model=JobStatus)
def submit_job(job: JobSubmit):
    if job.query_sequence:
        # Save sequence to a temporary file
        import uuid
        filename = f"paste_{uuid.uuid4().hex[:8]}.fasta"
        query_path = os.path.join(UPLOAD_DIR, filename)
        with open(query_path, "w") as f:
            f.write(job.query_sequence)
    elif job.query_filename:
        query_path = os.path.join(UPLOAD_DIR, job.query_filename)
        if not os.path.exists(query_path):
            raise HTTPException(status_code=404, detail="Query file not found")
    else:
        raise HTTPException(status_code=400, detail="Either query_filename or query_sequence must be provided")
    
    # 验证并获取所有数据库路径
    db_paths = []
    for db_id in job.db_ids:
        db_path = os.path.join(REF_DIR, db_id)
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail=f"Database {db_id} not found")
        db_paths.append(db_path)
    
    if job.tool == "blast":
        task = run_blast.delay(query_path, db_paths, job.options)
    elif job.tool == "minimap2":
        task = run_minimap2.delay(query_path, db_paths, job.options)
    else:
        raise HTTPException(status_code=400, detail="Unsupported tool")
    
    return JobStatus(job_id=task.id, state="PENDING")

@router.get("/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    task = celery_app.AsyncResult(job_id)
    
    result = None
    if task.state == 'SUCCESS':
        result = task.result
        
    return JobStatus(
        job_id=job_id,
        state=task.state,
        status=str(task.info) if task.state == 'FAILURE' else None,
        result=result
    )

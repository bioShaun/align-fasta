from fastapi import APIRouter
from models.schemas import ToolInfo
from typing import List

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.get("/", response_model=List[ToolInfo])
def list_tools():
    return [
        ToolInfo(name="blast", description="Nucleotide-Nucleotide BLAST (blastn)"),
        ToolInfo(name="minimap2", description="Fast pairwise alignment for long sequences")
    ]

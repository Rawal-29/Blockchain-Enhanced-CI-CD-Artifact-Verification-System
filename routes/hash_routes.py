from fastapi import APIRouter, HTTPException
from models.artifact import Artifact
import hashlib, os

router = APIRouter()

@router.post("/")
def compute_hash(data: Artifact):
    if not os.path.exists(data.artifact_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(data.artifact_path, "rb") as f:
        data.hash = hashlib.sha256(f.read()).hexdigest()
    return {"artifact_hash": data.hash}

from fastapi import APIRouter
from core.blockchain import store_artifact_hash
from models.artifact import HashData

router = APIRouter()

@router.post("/api/register/artifact")
def register_artifact(data: HashData):
    try:
        tx_hash = store_artifact_hash(data.hash)
        return {"status": "success", "transaction_hash": tx_hash}
    except Exception as e:
        return {"status": "error", "message": str(e)}
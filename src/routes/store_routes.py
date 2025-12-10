from fastapi import APIRouter
from core.blockchain import store_hash
from models.artifact import HashData

router = APIRouter()
@router.post("/api/register/artifact")
def register(data: HashData):
    try: return {"status": "success", "tx": store_hash(data.hash)}
    except Exception as e: return {"status": "error", "message": str(e)}
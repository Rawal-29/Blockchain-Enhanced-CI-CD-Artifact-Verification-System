import re
from fastapi import APIRouter, HTTPException
from core.blockchain import store_hash
from models.artifact import HashData

router = APIRouter()

@router.post("/api/register/artifact")
def register(data: HashData):
    # HashData.validate_hash already enforces format; pydantic raises 422 on bad input
    try:
        tx = store_hash(data.hash)
        return {"status": "success", "tx": tx}
    except Exception:
        # L3: never leak exception internals to callers
        raise HTTPException(status_code=500, detail="Registration failed")

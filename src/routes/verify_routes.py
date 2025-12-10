from fastapi import APIRouter
from core.blockchain import verify_hash

router = APIRouter()
@router.get("/api/verify/artifact")
def verify(hash: str):
    try: return {"verified": verify_hash(hash)}
    except Exception as e: return {"status": "error", "message": str(e)}
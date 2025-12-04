from fastapi import APIRouter
from core.blockchain import verify_artifact_hash

router = APIRouter()

@router.get("/api/verify/artifact")
def verify_artifact(hash: str):
    try:
        is_verified = verify_artifact_hash(hash)
        if is_verified:
            return {"status": "verified", "is_verified": True}
        else:
            return {"status": "unverified", "is_verified": False}
    except Exception as e:
        return {"status": "error", "message": str(e)}
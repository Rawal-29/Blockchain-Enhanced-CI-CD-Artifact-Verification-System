from fastapi import APIRouter
from core.blockchain import verify_artifact_hash

router = APIRouter()

@router.get("/api/verify/artifact", tags=["Verification"])
def verify_artifact(hash: str):
    """Handles CD pipeline verification: checks artifact hash against the immutable record."""
    try:
        is_verified = verify_artifact_hash(hash)
        
        if is_verified:
            return {
                "status": "verified",
                "is_verified": True,
                "message": "Artifact hash found on blockchain."
            }
        else:
            return {
                "status": "unverified",
                "is_verified": False,
                "message": "Artifact hash NOT found. Deployment blocked."
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Verification failed due to blockchain error: {str(e)}"
        }
from fastapi import APIRouter
# Fix: Only import the function you actually use in this file
from core.blockchain import verify_artifact_hash 

router = APIRouter()

@router.get("/api/verify/artifact")
def verify_artifact(hash: str):
    """CD Pipeline: Verifies artifact hash against the immutable blockchain record."""
    try:
        is_verified = verify_artifact_hash(hash)
        
        if is_verified:
            return {
                "status": "verified",
                "is_verified": True,
                "message": "Artifact hash found on blockchain."
            }
        else:
            # CRITICAL: This failure blocks deployment of tampered code
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
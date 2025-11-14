from fastapi import APIRouter
from core.blockchain import store_artifact_hash
from models.artifact import HashData

router = APIRouter()

@router.post("/api/register/artifact", tags=["Registration"])
def register_artifact(data: HashData):
    """Handles CI pipeline registration: stores artifact hash immutably on the blockchain."""
    try:
        tx_hash = store_artifact_hash(data.hash)
        return {
            "status": "success",
            "message": "Artifact hash registered on blockchain.",
            "transaction_hash": tx_hash
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to register hash: {str(e)}"
        }
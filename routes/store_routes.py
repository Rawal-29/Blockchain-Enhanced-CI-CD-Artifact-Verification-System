from fastapi import APIRouter
# Fix: Only import the function you actually use in this file
from core.blockchain import store_artifact_hash 
from models.artifact import HashData

router = APIRouter()

@router.post("/api/register/artifact")
def register_artifact(data: HashData):
    """CI Pipeline: Stores artifact hash immutably on the blockchain."""
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
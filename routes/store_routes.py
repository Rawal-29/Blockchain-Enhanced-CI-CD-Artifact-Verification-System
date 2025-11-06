from fastapi import APIRouter, HTTPException
from models.artifact import Artifact
from core.blockchain import contract, send_txn
from core.database import SessionLocal, verification_table

router = APIRouter()
session = SessionLocal()

@router.post("/")
def store_hash(data: Artifact):
    if not data.hash:
        raise HTTPException(status_code=400, detail="Hash required")
    tx_hash = send_txn(contract.functions.storeHash(data.hash))
    session.add({"artifact_hash": data.hash, "status": "stored"})
    session.commit()
    return {"transaction": tx_hash}

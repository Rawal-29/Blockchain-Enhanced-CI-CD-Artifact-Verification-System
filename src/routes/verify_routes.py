import re
from fastapi import APIRouter, HTTPException
from core.blockchain import verify_hash

router = APIRouter()

# H6: validate before calling into Web3 to avoid leaking parse errors
_HEX_RE = re.compile(r'^(0x)?[0-9a-fA-F]{64}$')

@router.get("/api/verify/artifact")
def verify(hash: str):
    if not _HEX_RE.match(hash):
        raise HTTPException(status_code=400, detail="Invalid hash format")
    try:
        return {"verified": verify_hash(hash)}
    except Exception:
        # L3: never leak exception internals to callers
        raise HTTPException(status_code=500, detail="Verification error")

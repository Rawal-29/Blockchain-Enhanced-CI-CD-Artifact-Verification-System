import hashlib
import os

import httpx
from eth_abi import encode
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="BlockCICD Artifact Registration API", version="1.0.0")

GELATO_RELAY_URL = "https://relay.gelato.digital/relays/v2/sponsored-call"
SEPOLIA_CHAIN_ID = 11155111

# storeHash(bytes32) selector
STORE_HASH_SELECTOR = bytes.fromhex("8f7cef42")


class ArtifactRequest(BaseModel):
    artifact_name: str
    artifact_sha256: str | None = None
    artifact_content: str | None = None


class ArtifactResponse(BaseModel):
    artifact_sha256: str
    gelato_task_id: str
    chain_id: int
    status: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/v1/register-artifact", response_model=ArtifactResponse)
async def register_artifact(req: ArtifactRequest):
    gelato_api_key = os.environ.get("GELATO_API_KEY")
    contract_address = os.environ.get("CONTRACT_ADDRESS")

    if not gelato_api_key:
        raise HTTPException(status_code=500, detail="GELATO_API_KEY not configured")
    if not contract_address:
        raise HTTPException(status_code=500, detail="CONTRACT_ADDRESS not configured")

    artifact_hash = req.artifact_sha256
    if artifact_hash is None:
        if req.artifact_content is None:
            raise HTTPException(
                status_code=400,
                detail="Provide artifact_sha256 or artifact_content"
            )
        artifact_hash = hashlib.sha256(req.artifact_content.encode()).hexdigest()

    # Normalize: strip 0x prefix, pad/truncate to 32 bytes
    raw = bytes.fromhex(artifact_hash.removeprefix("0x"))
    if len(raw) > 32:
        raise HTTPException(status_code=400, detail="Hash exceeds 32 bytes")
    hash_bytes32 = raw.rjust(32, b"\x00")

    call_data = STORE_HASH_SELECTOR + encode(["bytes32"], [hash_bytes32])

    payload = {
        "chainId": SEPOLIA_CHAIN_ID,
        "target": contract_address,
        "data": "0x" + call_data.hex(),
        "sponsorApiKey": gelato_api_key,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GELATO_RELAY_URL, json=payload)
        if resp.status_code != 201:
            raise HTTPException(
                status_code=502,
                detail=f"Gelato relay failed: {resp.text}"
            )
        task_id = resp.json().get("taskId", "unknown")

    return ArtifactResponse(
        artifact_sha256=artifact_hash,
        gelato_task_id=task_id,
        chain_id=SEPOLIA_CHAIN_ID,
        status="relayed",
    )

from pydantic import BaseModel

class Artifact(BaseModel):
    artifact_path: str = None
    hash: str = None

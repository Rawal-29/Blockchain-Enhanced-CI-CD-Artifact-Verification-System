from pydantic import BaseModel

class HashData(BaseModel):
    """Pydantic model for validating incoming artifact hash data."""
    hash: str
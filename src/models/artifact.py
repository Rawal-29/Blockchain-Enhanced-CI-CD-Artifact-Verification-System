import re
from pydantic import BaseModel, field_validator

# H6: validate hash format at the model boundary — 64-char hex, optional 0x prefix
_HEX_RE = re.compile(r'^(0x)?[0-9a-fA-F]{64}$')

class HashData(BaseModel):
    hash: str

    @field_validator('hash')
    @classmethod
    def validate_hash(cls, v: str) -> str:
        if not _HEX_RE.match(v):
            raise ValueError('hash must be a 64-character hex string (SHA-256), with optional 0x prefix')
        return v

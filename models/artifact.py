# models/artifact.py

from pydantic import BaseModel

class HashData(BaseModel):
    # This structure is used to validate the JSON body of the POST request
    hash: str
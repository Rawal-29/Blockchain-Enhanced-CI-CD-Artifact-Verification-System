
# 🔌 Verification API (FastAPI)

The backend service running on AWS Lambda. It provides a public interface for external teams/auditors to verify artifacts against the blockchain.

## 🏗️ Structure
* **`main.py`**: The FastAPI application entry point, wrapped with `Mangum` for AWS Lambda compatibility.
* **`routes/`**:
    * `store_routes.py`: Endpoint to register artifacts (Internal use).
    * `verify_routes.py`: Public endpoint to check artifact integrity.
* **`core/`**:
    * `blockchain.py`: Handles Web3 connections and contract calls.
    * `config.py`: Loads environment variables.
* **`models/`**:
    * `artifact.py`: Pydantic models for request validation.

## 📡 Endpoints

### GET /api/verify/artifact
Verifies if a hash exists on-chain.

**Query Parameter:**
* `hash`: The SHA256 hash string (must start with `0x`).

**Response:**
```json
{
  "verified": true
}
````

### POST /api/register/artifact

Registers a new hash (Requires server-side private key access).

**Body:**

```json
{
  "hash": "0x123..."
}
```

## 🐳 Docker Deployment

The API is packaged as a Docker container for Lambda.

```
docker build -f Dockerfile.lambda -t blockchain-api
```

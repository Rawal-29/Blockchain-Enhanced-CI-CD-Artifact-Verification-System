# API Routing Documentation (`routes/`)

This directory defines the public interface of the verification service, mapping REST HTTP requests to the core blockchain functions.

## 🛣️ Public API Endpoints

The endpoints are separated by concern: **Command (Write)** and **Query (Read)**.

### 1. Registration Endpoint (CI Phase)

* **File:** `store_routes.py`
* **Purpose:** Triggers the immutable recording of a new artifact hash.
* **Endpoint:** `POST /api/register/artifact`
* **Core Action:** Calls `core.blockchain.store_artifact_hash()`

### 2. Verification Endpoint (CD Phase)

* **File:** `verify_routes.py`
* **Purpose:** Performs a read-only integrity check before deployment is allowed.
* **Endpoint:** `GET /api/verify/artifact?hash={hash_value}`
* **Core Action:** Calls `core.blockchain.verify_artifact_hash()`
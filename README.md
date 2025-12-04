# 🛡️ Blockchain-Enhanced CI/CD Artifact Verification System

This framework establishes an **immutable security gate** in the software delivery pipeline by using an Ethereum smart contract to verify the integrity of all deployed artifacts. It prevents tampering and unauthorized deployments.

## 💡 System Overview: The Verification Flow

The system operates on a "Command and Query" principle, ensuring the hash of a built artifact is securely logged before deployment is permitted.

| Phase | Action | System Component | Security Goal |
| :--- | :--- | :--- | :--- |
| **1. Register (CI)** | The CI pipeline calculates the final artifact hash (SHA-256) and calls the API's **POST** endpoint. | **`routes/store_routes.py`** &rarr; **`BlockCICD.sol`** | **Immutable Proof of Origin** |
| **2. Verify (CD)** | The deployment system queries the API using the artifact's hash. | **`routes/verify_routes.py`** &rarr; **`BlockCICD.sol`** | **Integrity Check / Deployment Gate** |

***

## 🌐 API Endpoints and Usage

The FastAPI application exposes two primary REST endpoints:

### 1. Registration (Command: Write to Blockchain)

Used by the **CI pipeline** to register the artifact hash after a successful build. This operation requires the `DEPLOYER_PRIVATE_KEY` because it changes the blockchain state.

| Detail | Value |
| :--- | :--- |
| **Method** | `POST` |
| **Route** | `/api/register/artifact` |
| **Input (JSON)** | `{"hash": "eef9b566743a1ead41e5d32ac6ccb2c9fbc35b1a5b102546a7a962ed21282883"}` |
| **Success Response** | Returns the **Ethereum Transaction Hash**. |

### 2. Verification (Query: Read from Blockchain)

Used by the **CD pipeline/Terraform** as a non-mutating integrity check.

| Detail | Value |
| :--- | :--- |
| **Method** | `GET` |
| **Route** | `/api/verify/artifact?hash={hash_value}` |
| **Input (Query)** | `?hash=eef9b566743a1ead41e5d32ac6ccb2c9fbc35b1a5b102546a7a962ed21282883` |
| **Success Response** | `{"is_verified": true}` (Deployment proceeds) **OR** `{"is_verified": false}` (Deployment blocked) |

***

## 🛠️ Local Setup Guide

Use this guide to test the system locally using the minimalist Python approach.

### Prerequisites

* Python 3.10+
* **Ganache CLI** (`npm install -g ganache`)
* **Dependencies:** `pip install -r requirements.txt`

### Testing Sequence

1.  **Start Ganache CLI:** Run `ganache` in a separate terminal and **copy the Private Key** of the first account.
2.  **Configure:** Update **`.env.local`** with the Private Key.
3.  **Deploy Contract:** Run `python deploy_contract.py` (Updates Contract Address in `.env.local`).
4.  **Start API:** `python -m uvicorn main:app --reload`
5.  **Validate:** Run the `POST` and `GET` commands shown above to ensure end-to-end functionality.

***

## 🚀 Automation and Deployment

The system is structured for **GitOps**. The deployment relies on **Terraform** to manage resources securely on OpenShift.

| File Component | Role in Pipeline | Configuration Method |
| :--- | :--- | :--- |
| **`Dockerfile`** | Creates the container image for the FastAPI application. | Image is built and pushed by the CI runner. |
| **`infrastructure/*.tf`** | **Terraform** deploys the Kubernetes Deployment. | Injects **`CONTRACT_ADDRESS`** (config) and **`DEPLOYER_PRIVATE_KEY`** (secret) directly from the CI pipeline's secret manager. |
| **Kubernetes Secret** | **CRITICAL SECURITY.** | Stores the sensitive private key, ensuring it's never exposed in plain text configuration files. |

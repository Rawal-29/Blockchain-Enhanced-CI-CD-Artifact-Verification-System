
# 🛡️ Blockchain-Enhanced CI/CD Artifact Verification System


![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Blockchain](https://img.shields.io/badge/Ethereum-Sepolia-gray)
![AWS](https://img.shields.io/badge/Cloud-AWS-orange)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

> **"Trust, but Verify."** — An immutable security layer for modern DevOps pipelines.

---

## 📖 Project Description

The **Blockchain-Enhanced CI/CD Artifact Verification System** is a security-first DevOps tool designed to prevent **Supply Chain Attacks** and **Insider Threats** in infrastructure deployments.

In traditional CI/CD pipelines, there is a "blind spot" between the moment code is approved (Plan) and the moment it is deployed (Apply). A malicious actor or compromised runner could modify the deployment artifact during this window without detection.

**This project solves that problem** by anchoring the integrity of every Terraform Plan to the **Ethereum Blockchain**. By creating an immutable, tamper-proof "fingerprint" (hash) of our infrastructure code, we ensure that **no unapproved code can ever be deployed to production**.

### 🌟 Key Benefits
* **Immutable Audit Trail:** Every deployment is permanently recorded on the blockchain.
* **Tamper-Proof:** If a single byte of the plan changes post-approval, deployment is strictly blocked.
* **Zero-Knowledge Verification:** Verify file integrity without exposing sensitive file contents.
* **Public Transparency:** External auditors or teams can verify artifacts via a public API.
* **Smart Contract Rewards:** Minters (Deployers) receive **DevOps Trust Tokens (DTT)** upon successful registration.

---

## 🏗️ Architecture Overview

The system follows a strictly defined **"Sign-then-Verify"** workflow using **ChatOps**.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub Actions
    participant BC as Ethereum Blockchain
    participant AWS as AWS Cloud
    
    Note over Dev, AWS: Phase 1: Registration (ChatOps)
    Dev->>GH: Open PR & Comment "/tfplan"
    GH->>GH: Generate Terraform Plan
    GH->>GH: Calculate SHA256 Hash
    GH->>BC: Register Hash (Write Transaction)
    BC-->>GH: Confirmed (Mint DTT Token)
    
    Note over Dev, AWS: Phase 2: Verification (Deploy)
    Dev->>GH: Merge PR to Main
    GH->>GH: Download Plan Artifact
    GH->>GH: Calculate Hash Again
    GH->>BC: Verify Hash (Read Call)
    alt Hash Matches
        BC-->>GH: ✅ Verified
        GH->>AWS: Terraform Apply (Deploy Infra)
    else Hash Mismatch
        BC-->>GH: ❌ Unknown Hash
        GH->>GH: CRITICAL FAILURE (Stop Deploy)
    end
````

-----

## 📂 Folder Structure

```bash
├── .github/workflows/      # CI/CD Pipelines (ChatOps & Deploy)
├── contracts/              # Solidity Smart Contracts (BlockCICD.sol)
├── dashboard/              # Static HTML/JS for Audit Dashboard
├── infrastructure/         # Terraform IaC configurations
│   ├── main.tf             # Core AWS resources (S3, Policies)
│   ├── lambda.tf           # API Function definitions
│   ├── variables.tf        # Input variables
│   └── output.tf           # API URL & Bucket outputs
├── scripts/                # Python Automation Scripts
│   ├── deploy_contract.py  # Deploys contract to Sepolia
│   ├── tf_guard.py         # Handles Register/Verify logic
│   └── simulate_hack.sh    # Integrity attack simulation
├── src/                    # API Source Code (FastAPI)
│   ├── main.py             # App Entry Point
│   ├── routes/             # API Endpoints
│   └── core/               # Blockchain Logic
├── Dockerfile.lambda       # Container definition for API
└── README.md               # Project Documentation
```

-----

## ⚙️ Installation & Setup

### Prerequisites

1.  **AWS Account** with permissions to manage S3, Lambda, and IAM.
2.  **Ethereum Wallet** (MetaMask) with Sepolia Testnet ETH.
3.  **GitHub Repository** for hosting the code.
4.  **Terraform CLI** installed locally (optional).

### 1\. Clone Repository

```bash
git clone [https://github.com/your-username/blockchain-cicd-verification.git](https://github.com/your-username/blockchain-cicd-verification.git)
cd blockchain-cicd-verification
```

### 2\. Configure GitHub Secrets

Add the following secrets to your Repository (**Settings \> Secrets \> Actions**):

| Secret Name | Description |
| :--- | :--- |
| `AWS_ROLE_ARN` | The IAM Role ARN for GitHub Actions to assume. |
| `ETHEREUM_RPC_URL` | Your Infura or Alchemy Sepolia Endpoint. |
| `DEPLOYER_PRIVATE_KEY` | Private Key of the wallet used to deploy contracts. |

### 3\. Deploy

The pipeline is self-bootstrapping. Push to `main` to trigger the initial deployment.

```bash
git push origin main
```

-----

## 🔐 Environment Variables

These variables are used by the Python scripts and Terraform.

  * `ETHEREUM_RPC_URL`: Connection string for the blockchain node.
  * `DEPLOYER_PRIVATE_KEY`: **(Sensitive)** Used to sign transactions.
  * `CONTRACT_ADDRESS`: Automatically populated in `infrastructure/terraform.auto.tfvars`.
  * `TF_STATE_BUCKET`: S3 bucket for Terraform state.

-----

## 🚀 Usage Instructions

### 1\. ChatOps Workflow (Developer)

1.  Create a Pull Request.
2.  Comment: `/tfplan`.
3.  The bot generates a plan and registers the hash on-chain.
4.  Comment: `/create_image` (Optional) to build the Docker image.

### 2\. Deployment

1.  Merge the Pull Request.
2.  The pipeline verifies the plan hash against the blockchain.
3.  If verified, infrastructure is applied.

### 3\. Verification API

External teams can verify artifacts using the public Lambda API:

```bash
curl -X POST https://<your-api-url>/api/verify/artifact \
     -H "Content-Type: application/json" \
     -d '{"hash": "0x..."}'
```

-----

## 🤝 Contributing

1.  Fork the repo.
2.  Create a feature branch.
3.  **Important:** Run `/tfplan` in your PR to register your changes.
4.  Merge.



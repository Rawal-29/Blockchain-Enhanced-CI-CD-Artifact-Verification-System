
# 🤖 CI/CD Pipelines (GitHub Actions)

This directory contains the automation logic that powers our **ChatOps** and **Deployment** workflows.

## 📜 Workflow Definitions

We use three distinct workflows to separate concerns between Planning, Building, and Deploying.

### 1. `chatops-plan.yml` (The Planner)
* **Trigger:** Issue Comment starts with `/tfplan` on a Pull Request.
* **Purpose:** Generates a speculative Terraform Plan for the PR without deploying it.
* **Key Actions:**
    1.  **Checkout:** Pulls the code from the PR branch.
    2.  **Terraform Plan:** Runs `terraform plan` to see what *would* change.
    3.  **Upload:** Saves the binary plan file to S3 (`plans/pr-{id}.tfplan`).
    4.  **Feedback:** Comments on the PR with a summary of the plan changes.

### 2. `chatops-image.yml` (The Builder)
* **Trigger:** Issue Comment starts with `/create_image` on a Pull Request.
* **Purpose:** Builds the Docker container for the Verification API.
* **Key Actions:**
    1.  **Build:** Runs `docker build` using `Dockerfile.lambda`.
    2.  **Push:** Pushes the image to Amazon ECR (`blockchain-api`).
    3.  **Tag:** Uses the Commit SHA as the immutable image tag.
    4.  **Feedback:** Comments on the PR with the new Image Tag to use in Terraform.

### 3. `deploy-apply.yml` (The Deployer)
* **Trigger:** Merge (Push) to the `main` branch.
* **Purpose:** The Production Deployment Pipeline.
* **Key Actions:**
    1.  **Smart Contract:** Deploys a fresh `BlockCICD` contract (or uses existing).
    2.  **Verification:** Downloads the approved plan from S3 and verifies its Hash against the Blockchain registry.
    3.  **Security Gate:** If the hash does not match, the pipeline **fails immediately**.
    4.  **Apply:** Runs `terraform apply` to provision AWS resources.
    5.  **Publish:** Uploads the new Dashboard HTML and ABI files to public buckets.

---

## 🔐 Secrets & Permissions

These workflows require specific GitHub Secrets to function:

| Secret | Used By | Purpose |
| :--- | :--- | :--- |
| `AWS_ROLE_ARN` | All | IAM Role for OIDC Authentication with AWS. |
| `ETHEREUM_RPC_URL` | Deploy | Connection to Sepolia Testnet. |
| `DEPLOYER_PRIVATE_KEY` | Deploy | Wallet key for signing Blockchain transactions. |

**GITHUB_TOKEN Permissions:**
* `id-token: write` (Required for AWS OIDC)
* `pull-requests: write` (Required to post comments)
* `contents: read` (Required to clone code)

---

## 🗣️ ChatOps Commands

Use these commands in any Pull Request comment to trigger workflows manually:

| Command | Action | Output |
| :--- | :--- | :--- |
| `/tfplan` | Runs `terraform plan` | S3 Upload + PR Comment |
| `/create_image` | Builds Docker Image | ECR Push + PR Comment |

> **Note:** ChatOps commands only work for users with **Write** access to the repository.

# Infrastructure Documentation (Terraform / OpenShift)

This directory contains the necessary Terraform files to define, provision, and deploy the Blockchain Verification API onto an OpenShift or standard Kubernetes cluster.

## 🔑 Secure Configuration

The entire deployment relies on reading sensitive configuration from the CI/CD pipeline's environment variables, not from committed files.

| Variable | Description | Source |
| :--- | :--- | :--- |
| `rpc_url` | The RPC endpoint for the target network (e.g., Sepolia Testnet or Mainnet). | CI Pipeline Environment Variable |
| `contract_address` | The address of the pre-deployed `BlockCICD` contract. | CI Pipeline Environment Variable |
| `private_key_secret` | **CRITICAL:** The deployer account's private key. | **CI Secret Manager / Vault** (Injected as a Kubernetes Secret) |

## 🚀 Deployment Steps (CI/CD Runner)

The CI/CD pipeline should execute the following steps after a successful container image build:

1.  **Initialize Terraform:** Authenticate and initialize the Terraform state.
    ```bash
    terraform init infrastructure/
    ```

2.  **Plan Deployment:** Verify the resources that will be created.
    ```bash
    terraform plan infrastructure/ \
      -var="image_tag=$CI_COMMIT_TAG" \
      -var="rpc_url=$SEPOLIA_RPC" \
      -var="contract_address=$CONTRACT_ADDR" \
      -var="private_key_secret=$DEPLOYER_PRIVATE_KEY_SECRET"
    ```

3.  **Apply Deployment:** Apply the changes, creating the secure Deployment and Service on OpenShift.
    ```bash
    terraform apply infrastructure/ -auto-approve
    ```

## 📄 File Definitions

| File | Purpose | Notes |
| :--- | :--- | :--- |
| `variables.tf` | Defines all required input variables. | Ensures secure injection of the `private_key_secret`. |
| `openshift.tf` | Defines the Kubernetes `Deployment`, `Service`, `Secret`, and external `Route`. | The deployment pulls the Docker image and configures environment variables from the injected Secret. |
| `main.tf` | Configures the Kubernetes provider and calls the application module. | Ties the entire infrastructure together. |
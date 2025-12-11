# ☁️ Infrastructure as Code (Terraform)

This directory contains the Terraform configurations to provision the AWS cloud resources required for the Verification System.

## 🏛️ Resources Provisioned

| File | Resource | Description |
| :--- | :--- | :--- |
| `main.tf` | **S3 Buckets** | Creates `blockchain-artifacts` (Private) and `auditor-dashboard` (Public Website). |
| `lambda.tf` | **AWS Lambda** | Deploys the Python FastAPI container to a serverless function. |
| `providers.tf` | **Backend** | Configures the S3 Backend for Terraform state storage. |
| `variables.tf` | **Inputs** | Defines `image_tag` and `contract_address`. |
| `output.tf` | **Outputs** | Exports the Dashboard URL and API Endpoint URL. |

## 🛠️ Usage

This folder is primarily managed by GitHub Actions, but you can run it locally for debugging.

### Initialize
```bash
terraform init
````

### Plan

```bash
terraform plan -var="image_tag=latest" -var="contract_address=0x..."
```

### Apply

```bash
terraform apply -auto-approve
```

## 🔐 Security Configuration

  * **S3 Block Public Access:** Enabled for the artifact bucket to prevent data leaks.
  * **IAM Roles:** The Lambda function runs with a strictly scoped Execution Role.
  * **ECR Policies:** Only the Lambda service is allowed to pull images.

<!-- end list -->


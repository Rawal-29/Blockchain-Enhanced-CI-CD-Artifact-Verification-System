# Infrastructure-as-Code Specification

All AWS infrastructure is defined as Terraform HCL and provisioned exclusively through the blockchain-verified deployment gate. No manual console changes. No drift.

---

## State Backend

Terraform remote state is stored in a dedicated S3 bucket:

```
s3://rawal-cicd-terraform-state-2026/
```

State locking is handled natively by S3. The bucket is private, versioned, and accessible only via the OIDC-assumed IAM role used by GitHub Actions runners.

---

## Plan Binary Archive

During the PR review phase, the `/tfplan` ChatOps command archives approved plan artifacts to the same state bucket under an isolated prefix:

```
s3://rawal-cicd-terraform-state-2026/
  plans/
    <sha256_hash>.json        # serialized plan for hash computation
    <sha256_hash>.binary      # executable plan binary for terraform apply
    pr-<number>.ref           # PR-indexed pointer to the approved plan hash
```

These artifacts are written once and treated as immutable. The deploy gate fetches the exact binary that was reviewed — ensuring the plan executed at deploy time is byte-for-byte identical to the plan anchored to the blockchain.

---

## Provisioned Resources

### `main.tf`

| Resource | Type | Name | Purpose |
|---|---|---|---|
| `aws_s3_bucket.artifact_bucket` | S3 | `blockchain-artifacts-*` | Primary artifact storage with versioning |
| `aws_s3_bucket.website_bucket` | S3 | Static site bucket | Pipeline dashboard hosting |
| `aws_s3_bucket_policy.public_read` | S3 Policy | — | Public read for dashboard static assets |
| `aws_sqs_queue.blockcicd_standard_queue` | SQS | `blockcicd-standard-queue` | Async message buffer for pipeline events |
| `aws_sns_topic.blockcicd_standard_topic` | SNS | `blockcicd-standard-topic` | Fan-out notification channel |

### `lambda.tf`

AWS Lambda functions providing serverless compute for pipeline event processing and artifact verification callbacks.

---

## Variables

| Variable | Description |
|---|---|
| `aws_region` | Target AWS region for all resources |
| `contract_address` | Deployed `BlockCICD.sol` Sepolia contract address (injected via `terraform.auto.tfvars` by `deploy_contract.py`) |

---

## Providers

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}
```

AWS provider credentials are supplied exclusively via OIDC — the runner assumes an IAM role with scoped permissions. No static access keys are stored anywhere in the repository or CI environment.

---

## Deployment

Infrastructure changes follow the full ChatOps approval cycle:

1. Open PR with Terraform changes
2. Comment `/tfplan` — generates and archives the execution plan
3. Comment `/tfregister` — anchors the plan hash to Sepolia
4. Merge PR — triggers `deploy.yml`, which verifies on-chain and runs `terraform apply`

Direct `terraform apply` outside this cycle will not match any on-chain hash and is effectively blocked by design.

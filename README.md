# BlockCI/CD

### Decentralized Artifact Provenance for Zero-Trust Infrastructure Pipelines

<img src="http://googleusercontent.com/image_generation_content/0" width="100%" alt="BlockCI/CD Architecture Diagram">

---

## Overview

**BlockCI/CD** is a blockchain-anchored CI/CD security layer that cryptographically eliminates the possibility of unauthorized infrastructure changes reaching production. Every Terraform execution plan is hashed, anchored to an immutable Ethereum smart contract on Sepolia, and verified on-chain before `terraform apply` is permitted to execute.

No trusted intermediary. No mutable audit log. No attack surface between review and deployment.

---

## How It Works

### 1. The Write Path — Propose & Lock

A developer opens a Pull Request targeting `main`. A reviewer triggers the ChatOps pipeline by commenting directly on the PR:

- **`/tfplan`** — The runner executes `terraform plan`, serializes the binary and JSON output, computes a deterministic SHA256 fingerprint, and archives all artifacts to an isolated S3 state bucket keyed by PR number. The plan hash is posted as a PR comment for audit visibility.
- **`/tfregister`** — The runner invokes `scripts/anchor_hash.py`, which constructs a raw `storeHash(bytes32)` transaction, signs it with the infrastructure wallet's private key, and broadcasts it to the `BlockCICD` smart contract on the Ethereum Sepolia testnet via `eth_sendRawTransaction`. The transaction hash and Etherscan verification link are posted back to the PR.

At this point, the SHA256 of the approved plan is **permanently and immutably recorded on-chain**. It cannot be altered, deleted, or forged.

### 2. The Read Path — Verify & Deploy

When the PR is merged into `main`, the `deploy.yml` pipeline triggers automatically:

1. Resolves the originating PR number from the raw merge commit SHA via `gh api`.
2. Fetches the exact `tfplan.binary` and `tfplan.json` from S3 using the stored plan reference.
3. Recomputes the SHA256 fingerprint of the downloaded plan.
4. Calls `cast call` (Foundry) to invoke `verifyHash(bytes32)` on the on-chain registry.
5. If the contract returns `true` → `terraform apply` proceeds.
6. If the contract returns `false` → the pipeline exits with a `CRITICAL SECURITY FAILURE` and deployment is permanently blocked.

### 3. The Security Guarantee

This architecture eliminates **Time-of-Check to Time-of-Use (TOCTOU)** attacks — the class of vulnerability where infrastructure code is reviewed and approved, then silently modified between approval and execution. Because the gate re-derives the hash from the artifact and verifies it against an immutable on-chain record, no in-flight mutation can survive the verification step.

The system enforces a **Zero-Trust deployment perimeter**: the blockchain is the sole authority. No human, no CI/CD runner, and no privileged process can bypass it without the cryptographic proof of prior approval.

---

## Repository Component Matrix

| Path | Description |
|---|---|
| [`.github/workflows/`](.github/workflows/README.md) | GitOps CI/CD Automation Orchestration |
| [`scripts/`](scripts/README.md) | Web3 Signing & Broadcasting Engine |
| [`contracts/`](contracts/README.md) | Immutable Ledger Smart Contract Spec |
| [`infrastructure/`](infrastructure/README.md) | Infrastructure-as-Code (Terraform) Base & Backends |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Infrastructure | Terraform, AWS (S3, SQS, SNS, Lambda) |
| Blockchain | Solidity 0.8.20, Ethereum Sepolia Testnet |
| Web3 Client | Python `web3.py` |
| On-Chain Verification | Foundry `cast call` |
| CI/CD Orchestration | GitHub Actions (ChatOps + OIDC) |
| State Backend | AWS S3 |

---

## Prerequisites

- AWS account with OIDC role configured for GitHub Actions
- Ethereum Sepolia RPC endpoint (Alchemy or Infura)
- Deployed `BlockCICD.sol` contract address
- GitHub repository secrets: `ETHEREUM_RPC_URL`, `DEPLOYER_PRIVATE_KEY`, `CONTRACT_ADDRESS`, `AWS_ROLE_ARN`

---

## License

MIT

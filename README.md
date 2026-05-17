# BlockCI/CD

### Decentralized Artifact Provenance for Zero-Trust Infrastructure Pipelines

---

## Overview

**BlockCI/CD** is a blockchain-anchored CI/CD security layer that cryptographically eliminates the possibility of unauthorized infrastructure changes reaching production. Every Terraform execution plan is hashed, anchored to an immutable Ethereum smart contract on Sepolia, and verified on-chain before `terraform apply` is permitted to execute.

No trusted intermediary. No mutable audit log. No attack surface between review and deployment.

---

## How It Works

### 1. The Write Path — Propose & Lock

A developer opens a Pull Request targeting `main`. An authorized reviewer triggers the ChatOps pipeline by commenting directly on the PR:

- **`/tfplan`** — The runner executes `terraform plan`, serializes the output to both binary and JSON, computes a deterministic SHA256 fingerprint, and archives all artifacts to an isolated S3 state bucket keyed by PR number. The plan hash is posted as a PR comment for audit visibility.
- **`/tfregister`** — The runner invokes `scripts/anchor_hash.py`, which constructs a raw `storeHash(bytes32)` transaction, signs it with the infrastructure wallet's private key, and broadcasts it to the `BlockCICD` smart contract on the Ethereum Sepolia testnet via `eth_sendRawTransaction`. The transaction hash and Etherscan verification link are posted back to the PR.

At this point, the SHA256 of the approved plan is **permanently and immutably recorded on-chain**. It cannot be altered, deleted, or forged.

### 2. The Read Path — Verify & Deploy

When the PR is merged into `main`, the `deploy.yml` pipeline triggers automatically:

1. Resolves the originating PR number from the raw merge commit SHA via `gh api`.
2. Fetches the exact `tfplan.binary` and `tfplan.json` from S3 using the stored plan reference.
3. Recomputes the SHA256 fingerprint of the downloaded plan.
4. Calls `cast call` (Foundry) to invoke `verifyHash(bytes32)` on the on-chain registry.
5. `true` → `terraform apply` proceeds. `false` → `CRITICAL SECURITY FAILURE`, pipeline exits code 1.

### 3. Core Security Guarantee — Eliminating TOCTOU

This architecture permanently eliminates **Time-of-Check to Time-of-Use (TOCTOU)** attacks — the class of vulnerability where infrastructure code is reviewed and approved, then silently modified between approval and execution.

Because the deploy gate re-derives the hash from the exact artifact stored at review time and verifies it against an immutable on-chain record, **no in-flight mutation can survive the verification step**. The blockchain is the sole authority. No human, CI/CD runner, or privileged process can bypass it without the cryptographic proof of prior approval.

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
| Infrastructure provisioning | Terraform, AWS (S3, SQS, SNS, Lambda) |
| Blockchain registry | Solidity 0.8.20, Ethereum Sepolia Testnet |
| Web3 transaction signing | Python `web3.py` |
| On-chain verification | Foundry `cast call` |
| CI/CD orchestration | GitHub Actions (ChatOps + OIDC) |
| Remote state & plan storage | AWS S3 |

---

## System Requirements

- AWS account with OIDC role configured for GitHub Actions
- Ethereum Sepolia RPC endpoint (Alchemy or Infura)
- Deployed `BlockCICD.sol` contract address on Sepolia
- GitHub repository secrets: `ETHEREUM_RPC_URL`, `DEPLOYER_PRIVATE_KEY`, `CONTRACT_ADDRESS`, `AWS_ROLE_ARN`

---

## License

MIT

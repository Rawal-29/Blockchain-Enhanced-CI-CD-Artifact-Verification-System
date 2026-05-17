# CI/CD Workflow Specifications

This directory contains the two GitHub Actions workflows that implement the complete BlockCI/CD pipeline: a cryptographic locking phase during PR review (`chatops.yml`), and an immutable verification gate on merge to `main` (`deploy.yml`).

---

## `chatops.yml` — PR-Phase Orchestration

**Trigger:** `issue_comment` events on Pull Requests. Restricted to `OWNER`, `MEMBER`, and `COLLABORATOR` author associations. Fork PRs are explicitly rejected at the first step to prevent privilege escalation via untrusted code paths.

### Architecture

The workflow is entirely stateless. It carries no assumptions about prior runner state and derives all context from GitHub event payloads and S3-stored artifacts. All resource access uses short-lived OIDC credentials — no long-lived AWS keys exist in the environment.

---

### `/tfplan` — Plan Snapshot & Archive

| Step | Action |
|---|---|
| Resolve PR branch | `xt0rted/pull-request-comment-branch@v2` extracts the exact head commit SHA |
| Checkout | Pins to that SHA — prevents drift from subsequent commits during execution |
| AWS authentication | OIDC role assumption via `aws-actions/configure-aws-credentials@v4` |
| Terraform init & plan | `terraform plan -out=tfplan.binary` — deterministic binary output |
| JSON serialization | `terraform show -json tfplan.binary > tfplan.json` |
| Hash computation | `sha256sum tfplan.json \| awk '{print $1}'` — canonical plan fingerprint |
| Archive to S3 | `tfplan.json` and `tfplan.binary` stored under `plans/<hash>.*`; PR-indexed pointer stored at `plans/pr-<number>.ref` |
| Post to PR | Plan text and hash posted as a structured review comment |

**S3 key structure:**

```
s3://<TF_STATE_BUCKET>/
  plans/
    <plan_hash>.json         # serialized plan for verification
    <plan_hash>.binary       # executable binary for terraform apply
    pr-<pr_number>.ref       # PR → plan hash pointer for deploy-time lookup
```

---

### `/tfregister` — Blockchain Anchoring

| Step | Action |
|---|---|
| Fetch approved plan | Resolves `plans/pr-<number>.ref` → downloads `tfplan.json` |
| Recompute hash | SHA256 recomputed from downloaded file — must match stored reference |
| Anchor to blockchain | Invokes `scripts/anchor_hash.py` with `ARTIFACT_HASH`, `CONTRACT_ADDRESS`, `GELATO_API_KEY` |
| Post to PR | Posts SHA256, Gelato/Etherscan transaction link as a structured PR comment |

Once `/tfregister` completes successfully, the plan hash is **permanently recorded on-chain**. Any subsequent commit to the branch — however minor — generates a different plan hash that will fail the deploy gate.

---

## `deploy.yml` — Merge Gate

**Trigger:** `push` to `main`, with `paths-ignore` filtering to skip execution on documentation-only commits:

```yaml
paths-ignore:
  - "README.md"
  - "docs/**"
  - "*.md"
```

### Architecture

The deploy workflow trusts nothing from the CI environment. Its sole source of truth is the Ethereum blockchain. The S3-fetched artifact is the identical binary reviewed during the PR phase — not a freshly regenerated plan.

---

### Step 1 — Resolve Merged PR Number

```bash
gh api "repos/${{ github.repository }}/commits/${{ github.sha }}/pulls" \
  --jq '.[0].number'
```

GitHub `push` events carry no PR context. The `gh api` call reverse-maps the merge commit SHA to its originating PR number using the Commits API. This is the key that unlocks the correct S3 plan reference. Pipeline fails immediately if no PR is found.

---

### Step 2 — Fetch Approved Plan from S3

```bash
PLAN_HASH=$(aws s3 cp "s3://<bucket>/plans/pr-<pr_num>.ref" -)
aws s3 cp "s3://<bucket>/plans/${PLAN_HASH}.json" tfplan.json
aws s3 cp "s3://<bucket>/plans/${PLAN_HASH}.binary" ./infrastructure/tfplan.binary
```

Fetches the byte-for-byte identical artifacts archived during the PR review phase. Eliminates non-determinism: the plan executed at deploy time matches the plan anchored to the blockchain.

---

### Step 3 — Hash Integrity Check

The SHA256 of the downloaded `tfplan.json` is recomputed and compared against the S3 reference value. A mismatch indicates S3 object corruption or tampering and fails the pipeline before the blockchain query is attempted.

---

### Step 4 — On-Chain Verification Gate

```bash
cast call "${CONTRACT_ADDRESS}" \
  "verifyHash(bytes32)(bool)" \
  "0x${ARTIFACT_HASH}" \
  --rpc-url "${ETHEREUM_RPC_URL}"
```

Foundry's `cast` CLI makes a single JSON-RPC `eth_call` against the `BlockCICD` contract.

| Result | Outcome |
|---|---|
| `true` | Hash found on-chain. `terraform apply` proceeds. |
| `false` | Hash not registered. `CRITICAL SECURITY FAILURE`. Pipeline exits code 1. |

---

### Step 5 — `terraform apply`

```bash
terraform apply -auto-approve tfplan.binary
```

Executed only after the blockchain gate passes. Applies the S3-fetched binary — not a freshly generated plan.

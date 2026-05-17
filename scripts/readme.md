# Web3 Signing & Broadcasting Engine

This directory contains the Python scripts that implement the blockchain interaction layer. These scripts are invoked directly by GitHub Actions runners and handle all Web3 transaction construction, signing, and broadcasting.

---

## `anchor_hash.py` — On-Chain Plan Registration

The primary signing engine. Invoked during the `/tfregister` ChatOps phase to permanently anchor an approved infrastructure plan hash to the Ethereum Sepolia testnet.

---

### Environment Interface

| Variable | Description |
|---|---|
| `ETHEREUM_RPC_URL` | Sepolia JSON-RPC endpoint (Alchemy or Infura) |
| `DEPLOYER_PRIVATE_KEY` | Infrastructure wallet private key (with or without `0x` prefix) |
| `CONTRACT_ADDRESS` | Deployed `BlockCICD` contract address on Sepolia |
| `ARTIFACT_HASH` | 64-character hex SHA256 fingerprint of the approved `tfplan.json` |

All four variables are required. The script exits with code `1` and a descriptive error if any are missing or malformed.

---

### Execution Flow

```
1. Validate environment variables
2. Establish Web3 HTTP provider connection (fail fast on RPC error)
3. Normalize ARTIFACT_HASH → bytes32 (strip 0x, validate 64 hex chars)
4. Instantiate contract with minimal storeHash ABI
5. Build transaction: storeHash(bytes32)
   - from: infrastructure wallet address
   - nonce: current account nonce (replay protection)
   - gasPrice: live network gas price
   - chainId: dynamically read from RPC (chain-agnostic)
   - gas: 100,000 (sufficient for storeHash + ERC20 mint)
6. Sign transaction with DEPLOYER_PRIVATE_KEY (local — never leaves runner)
7. Broadcast via eth_sendRawTransaction
8. Poll for receipt with 120s timeout
9. Assert receipt.status == 1 (revert detection)
10. Write tx_hash to GITHUB_OUTPUT for downstream step consumption
```

---

### Minimal ABI

The script uses a minimal inline ABI containing only the `storeHash` function signature. This avoids dependencies on external ABI files and reduces the attack surface of the signing environment.

```python
STORE_HASH_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "hashValue", "type": "bytes32"}],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]
```

---

### Security Properties

- **No secrets logged** — private key is used only for local transaction signing; it is never printed, echoed, or transmitted to any endpoint other than the RPC `eth_sendRawTransaction` call as a signed payload.
- **Replay protection** — nonce is fetched live from the network at execution time.
- **Chain isolation** — `chainId` is read from the RPC endpoint, preventing accidental mainnet broadcast.
- **Revert detection** — receipt status is explicitly asserted; a reverted transaction (e.g., duplicate hash) exits with code `1` and blocks the CI step.

---

## Foundry `cast call` — On-Chain Verification (in `deploy.yml`)

The deployment verification gate uses Foundry's `cast` CLI rather than a Python or Node.js script. This is a deliberate architectural choice.

---

### Why `cast call` Over a Runtime Script

| Criterion | `cast call` (Foundry) | Python / Node.js |
|---|---|---|
| **Binary size** | ~10 MB static binary | 200–500 MB runtime install |
| **Installation time** | ~15 seconds (`foundry-rs/foundry-toolchain`) | 45–90 seconds |
| **Dependencies** | Zero | pip/npm dependency tree |
| **Execution model** | Single JSON-RPC `eth_call` | Full runtime initialization |
| **Attack surface** | Minimal — no package manager, no transitive deps | Large — supply chain risk via dependency graph |
| **Output** | Direct `true`/`false` to stdout | Requires parsing, error handling boilerplate |

For a stateless read-only verification call that executes in a production CI gate, the lightweight approach is strictly superior. `cast call` is idempotent, deterministic, and requires no state beyond the RPC URL and contract address.

---

## `deploy_contract.py` — One-Time Contract Deployment

Used for initial deployment of `BlockCICD.sol` to Sepolia. Compiles the contract via `py-solc-x`, connects to the Sepolia RPC, deploys from the infrastructure wallet, and writes the resulting contract address to `infrastructure/terraform.auto.tfvars`.

Requires `DEPLOY_ON_MERGE=true` to execute — guarded against accidental re-deployment on CI runs.

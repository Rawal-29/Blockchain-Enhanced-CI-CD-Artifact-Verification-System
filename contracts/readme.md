# Smart Contract Specification

**Network:** Ethereum Sepolia Testnet
**Compiler:** Solidity `^0.8.20`
**Dependencies:** OpenZeppelin Contracts v5.x (`ERC20`, `Ownable`)

---

## `BlockCICD.sol`

The `BlockCICD` contract is the immutable on-chain registry at the center of the verification architecture. It maintains a permanent, append-only record of every cryptographically approved infrastructure plan.

---

### Contract Interface

```solidity
contract BlockCICD is ERC20, Ownable {
    mapping(bytes32 => uint256) public verifiedHashes;

    event PlanVerified(bytes32 indexed planHash, address indexed auditor, uint256 timestamp);

    function storeHash(bytes32 hashValue) public onlyOwner;
    function verifyHash(bytes32 hashValue) public view returns (bool);
}
```

---

### Data Structure

```solidity
mapping(bytes32 => uint256) public verifiedHashes;
```

Maps a 32-byte plan fingerprint to the Unix timestamp at which it was registered. A value of `0` indicates the hash was never registered. A non-zero value proves the hash was anchored at that exact block time. The mapping is public, allowing permissionless on-chain verification by any external caller.

---

### Write Function — `storeHash`

```solidity
function storeHash(bytes32 hashValue) public onlyOwner
```

| Property | Detail |
|---|---|
| Access | `onlyOwner` — callable exclusively by the infrastructure wallet that deployed the contract |
| Guard | Reverts if `hashValue` already exists — prevents duplicate registration |
| Side effect | Records `block.timestamp` against the hash; mints 10 DTT to the caller as a cryptographic receipt |
| Event | Emits `PlanVerified(planHash, auditor, timestamp)` for off-chain indexing |

The `onlyOwner` restriction ensures that only the authorized infrastructure wallet (whose private key is held as a GitHub Actions secret) can write to the registry. No other address can register a hash.

---

### Read Function — `verifyHash`

```solidity
function verifyHash(bytes32 hashValue) public view returns (bool)
```

| Property | Detail |
|---|---|
| Access | Public, permissionless, read-only |
| Gas cost | Zero (view call — no state mutation) |
| Return | `true` if the hash was previously registered; `false` otherwise |

This is the function invoked by Foundry's `cast call` in `deploy.yml`. It is the single point of truth the deployment gate consults before permitting `terraform apply`.

---

### DevOps Trust Token (DTT)

The contract inherits `ERC20` and mints **10 DTT** per successful `storeHash` call. Each token represents one verified infrastructure plan. The token balance of the owner address provides a real-time, publicly verifiable count of total approved deployments.

---

### Deployment

```bash
python scripts/deploy_contract.py
```

Requires environment variables: `ETHEREUM_RPC_URL`, `DEPLOYER_PRIVATE_KEY`. The deployed contract address must be stored as the `CONTRACT_ADDRESS` GitHub Actions secret.

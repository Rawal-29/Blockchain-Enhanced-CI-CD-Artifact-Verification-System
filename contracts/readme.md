
# 📜 Smart Contracts

This directory contains the Solidity logic for the immutable registry.

## `BlockCICD.sol`

A hybrid **Registry + ERC20** contract.

### Features
* **Registry:** Maps `bytes32` (SHA256 Hash) to `uint256` (Timestamp).
* **Immutability:** Once a hash is stored, it cannot be overwritten or deleted.
* **Ownership:** Only the `owner` (CI/CD Pipeline Wallet) can register new hashes.
* **Rewards:** Mints **10 DTT (DevOps Trust Token)** to the auditor for every successful verification registration.

### Key Functions
```solidity
function storeHash(bytes32 hashValue) public onlyOwner
function verifyHash(bytes32 hashValue) public view returns (bool)
````

### Events

  * `PlanVerified(bytes32 indexed planHash, address indexed auditor, uint256 timestamp)`




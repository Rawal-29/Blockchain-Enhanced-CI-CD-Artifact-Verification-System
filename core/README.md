# Core Application Logic (`core/`)

This directory contains `blockchain.py`, which is the direct interface layer between the FastAPI application and the Ethereum blockchain.

## 🔗 `blockchain.py` Responsibilities

The primary role of this module is to handle secure configuration retrieval and transaction signing.

### Key Logic

1.  **Configuration Management:** All critical variables (`RPC_URL`, `PRIVATE_KEY`, `CONTRACT_ADDRESS`) are sourced from **`os.environ`** (environment variables) for security in the production container.
2.  **Transaction Building:** The `store_artifact_hash` function explicitly constructs the transaction payload, calculates gas, and signs the transaction using the `Account.from_key()` method. This ensures the transaction is correctly authenticated by the **contract owner**.
3.  **Data Encoding:** The module handles the conversion of the hex hash string from the API into **`bytes32`** before sending it to the contract, ensuring efficient and correct data storage.

### Functions

* `get_contract_instance()`: Initializes the `web3` connection and loads the contract ABI.
* `store_artifact_hash(hash_value)`: **WRITE OPERATION.** Signs and sends a transaction to record the hash.
* `verify_artifact_hash(hash_value)`: **READ OPERATION.** Calls the contract's view function to check if the hash exists.

# 🐍 Automation Scripts

This folder contains the Python scripts that bridge the CI/CD pipeline with the Ethereum Blockchain (Sepolia Network), ensuring strict immutable logging for all infrastructure changes.

## 📜 Script Descriptions

### 1. `deploy_contract.py`
* **Purpose:** Deploys the `BlockCICD` smart contract to the Ethereum network.
* **Logic:**
    * Compiles Solidity source code using `py-solc-x`.
    * Checks wallet balance to ensure sufficient gas.
    * Signs a deployment transaction with `DEPLOYER_PRIVATE_KEY`.
    * Updates `infrastructure/terraform.auto.tfvars` with the new address.

### 2. `tf_guard.py`
* **Purpose:** The security enforcer for the pipeline.
* **Usage:**
    ```bash
    python tf_guard.py [register|verify] <path_to_file>
    ```
* **Register:** Hashes the file and sends a transaction to the smart contract.
* **Verify:** Reads the smart contract to check if the file hash exists. Exits with Error 1 if not found.

### 3. `simulate_hack.sh`
* **Purpose:** Demonstrates the security verification failure.
* **Logic:**
    1.  Appends a blank space to the `tfplan.binary` file (altering its hash).
    2.  Runs `tf_guard.py verify`.
    3.  **Expected Result:** The verification should fail, proving the system detected the tampering.

## 📦 Dependencies
* `web3.py`
* `py-solc-x`
* `python-dotenv`
`
import os
import json
import sys
from web3 import Web3, HTTPProvider
# Import 'import_installed_solc' to use the binary we downloaded in CI
from solcx import compile_source, install_solc, set_solc_version, import_installed_solc
from dotenv import load_dotenv

load_dotenv(".env.local")

# --- FIXED: Robust Installation Logic ---
print("🔧 Setting up Solidity Compiler (0.8.0)...")

try:
    # 1. First, try to "import" the binary we installed via GitHub Actions
    # This tells python: "Hey, use the 'solc' at /usr/local/bin/solc"
    try:
        import_installed_solc("/usr/local/bin/solc")
        set_solc_version("0.8.0")
        print("✅ Using system-installed Solc 0.8.0")
    except Exception:
        # Fallback for local development (Mac/Windows)
        print("⚠️ System solc not found (Normal on local). Checking standard install...")
        install_solc("0.8.0")
        set_solc_version("0.8.0")
        print("✅ Using standard Solc 0.8.0")
    
except Exception as e:
    print(f"❌ Critical Error: Could not setup Solc: {e}")
    sys.exit(1)

# 2. Compile Contract
print("Compiling BlockCICD.sol...")
try:
    with open("contracts/BlockCICD.sol", "r") as f:
        contract_source_code = f.read()

    compiled_sol = compile_source(
        contract_source_code,
        output_values=["abi", "bin"],
        solc_version="0.8.0"
    )
except Exception as e:
    print(f"❌ Compilation Failed: {e}")
    sys.exit(1)

contract_interface = compiled_sol.popitem()[1]
abi = contract_interface["abi"]

# 3. Save ABI (Critical for Docker build)
with open("BlockCICD_ABI.json", "w") as f:
    json.dump(abi, f)
print("✅ ABI saved to BlockCICD_ABI.json")

# 4. Attempt Deployment (Only if keys exist)
RPC_URL = os.getenv("ETHEREUM_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

if RPC_URL and PRIVATE_KEY:
    try:
        w3 = Web3(HTTPProvider(RPC_URL))
        if w3.is_connected():
            account = w3.eth.account.from_key(PRIVATE_KEY)
            Contract = w3.eth.contract(abi=abi, bytecode=contract_interface["bin"])
            
            print(f"🚀 Deploying from {account.address}...")
            
            # Simple check to stop if no funds (prevents hard crash)
            balance = w3.eth.get_balance(account.address)
            if balance == 0:
                 print("⚠️  Insufficient funds. Skipping deployment, but ABI is saved.")
                 sys.exit(0)

            deploy_txn = Contract.constructor().build_transaction({
                'chainId': w3.eth.chain_id,
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gasPrice': w3.eth.gas_price
            })
            
            signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"✅ Transaction Sent: {tx_hash.hex()}")
            print("⏳ Waiting for receipt... (Ctrl+C if this takes too long)")
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            contract_address = tx_receipt.contractAddress
            print(f"📌 Contract Address: {contract_address}")

            # --- NEW: Generate Terraform Variables File ---
            tfvars_content = f'contract_address = "{contract_address}"\n'
            
            # Write to infrastructure/terraform.auto.tfvars
            tf_path = os.path.join("infrastructure", "terraform.auto.tfvars")
            with open(tf_path, "w") as tf_file:
                tf_file.write(tfvars_content)
                
            print(f"🔗 Linked Contract to Infrastructure: {tf_path}")

    except Exception as e:
        print(f"⚠️  Deployment skipped/failed: {e}")
        print("✅ ABI was saved successfully. You can proceed with Infrastructure.")
else:
    print("⚠️  Missing RPC_URL or PRIVATE_KEY. Skipping deployment.")
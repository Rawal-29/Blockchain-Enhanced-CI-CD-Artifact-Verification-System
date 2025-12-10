import os
import json
import sys
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc, set_solc_version
from dotenv import load_dotenv

load_dotenv(".env.local")

# 1. Setup Solc
CI_SOLC_PATH = "/usr/local/bin/solc"
compile_args = {"solc_version": "0.8.0"}

if os.path.exists(CI_SOLC_PATH):
    print(f"✅ Found manual CI solc at {CI_SOLC_PATH}")
    compile_args = {"solc_binary": CI_SOLC_PATH}
else:
    print("⚠️ Manual binary not found. Attempting standard install...")
    try:
        install_solc("0.8.0")
        set_solc_version("0.8.0")
    except Exception as e:
        print(f"❌ Solc Setup Error: {e}")
        # Continue, hoping standard install worked

# 2. Compile Contract
print("Compiling BlockCICD.sol...")
try:
    with open("contracts/BlockCICD.sol", "r") as f:
        contract_source_code = f.read()

    # [CRITICAL FIX] Map '@openzeppelin' to the node_modules folder
    compiled_sol = compile_source(
        contract_source_code,
        output_values=["abi", "bin"],
        import_remappings=["@openzeppelin=node_modules/@openzeppelin"],
        base_path=".", 
        allow_paths=".",
        **compile_args 
    )
except Exception as e:
    print(f"❌ Compilation Failed: {e}")
    sys.exit(1)

# Extract Interface
contract_id = "<stdin>:BlockCICD"
if contract_id not in compiled_sol:
    # Fallback if ID is different (sometimes happens with versions)
    contract_id = list(compiled_sol.keys())[0]

contract_interface = compiled_sol[contract_id]
abi = contract_interface["abi"]

# 3. Save ABI
with open("BlockCICD_ABI.json", "w") as f:
    json.dump(abi, f)
print("✅ ABI saved to BlockCICD_ABI.json")

# 4. Deploy
RPC_URL = os.getenv("ETHEREUM_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
SHOULD_DEPLOY = os.getenv("DEPLOY_ON_MERGE", "true").lower() == "true"

if RPC_URL and PRIVATE_KEY and SHOULD_DEPLOY:
    try:
        w3 = Web3(HTTPProvider(RPC_URL))
        if not w3.is_connected():
            raise Exception("Failed to connect to RPC")
            
        account = w3.eth.account.from_key(PRIVATE_KEY)
        Contract = w3.eth.contract(abi=abi, bytecode=contract_interface["bin"])
        
        print(f"🚀 Deploying from {account.address}...")
        
        deploy_txn = Contract.constructor().build_transaction({
            'chainId': w3.eth.chain_id,
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        })
        
        signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"✅ Transaction Sent: {tx_hash.hex()}")
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        print(f"📌 Contract Address: {contract_address}")

        # Save Address for Terraform
        tf_path = os.path.join("infrastructure", "terraform.auto.tfvars")
        with open(tf_path, "w") as tf_file:
            tf_file.write(f'contract_address = "{contract_address}"\n')
            
        print(f"🔗 Linked Contract to Infrastructure: {tf_path}")

    except Exception as e:
        print(f"⚠️  Deployment skipped/failed: {e}")
        # Don't fail the pipeline for network errors, but ensure we verified compilation
        sys.exit(0)
else:
    print("⚠️  Skipping deployment (Config or Keys missing).")
import os
import json
import sys
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc, set_solc_version
from dotenv import load_dotenv

load_dotenv(".env.local")

# 1. Install Solc
CI_SOLC_PATH = "/usr/local/bin/solc"
compile_args = {"solc_version": "0.8.0"}

if os.path.exists(CI_SOLC_PATH):
    print(f"✅ Found manual CI solc at {CI_SOLC_PATH}")
    compile_args = {"solc_binary": CI_SOLC_PATH}
else:
    install_solc("0.8.0")
    set_solc_version("0.8.0")

# 2. Compile
print("Compiling BlockCICD.sol...")
try:
    with open("contracts/BlockCICD.sol", "r") as f:
        source = f.read()

    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        import_remappings=["@openzeppelin=node_modules/@openzeppelin"],
        base_path=".", 
        allow_paths=".",
        **compile_args
    )
except Exception as e:
    print(f"❌ Compilation Failed: {e}")
    sys.exit(1)

contract_id = "<stdin>:BlockCICD"
if contract_id not in compiled:
    contract_id = list(compiled.keys())[0]

abi = compiled[contract_id]["abi"]
bytecode = compiled[contract_id]["bin"]

# Save ABI
with open("BlockCICD_ABI.json", "w") as f:
    json.dump(abi, f)

# 3. Deploy (STRICT MODE)
RPC_URL = os.getenv("ETHEREUM_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

if not RPC_URL or not PRIVATE_KEY:
    print("❌ CRITICAL ERROR: Missing GitHub Secrets (ETHEREUM_RPC_URL or DEPLOYER_PRIVATE_KEY).")
    print("Deployment cannot proceed without a wallet.")
    sys.exit(1)  # Force pipeline failure

try:
    w3 = Web3(HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise Exception("Could not connect to RPC URL")

    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"🚀 Deploying from: {account.address}")

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build Transaction
    tx = Contract.constructor().build_transaction({
        'chainId': w3.eth.chain_id,
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign & Send
    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction Sent: {tx_hash.hex()}")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"📌 Contract Address: {receipt.contractAddress}")

    # 4. Write to File (Crucial Step)
    tf_path = os.path.join("infrastructure", "terraform.auto.tfvars")
    
    # Ensure directory exists
    os.makedirs("infrastructure", exist_ok=True)
    
    with open(tf_path, "w") as f:
        f.write(f'contract_address = "{receipt.contractAddress}"\n')
    
    print(f"✅ Saved address to {tf_path}")

except Exception as e:
    print(f"❌ Deployment Failed: {e}")
    sys.exit(1)
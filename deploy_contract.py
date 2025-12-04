import os
import json
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc
from dotenv import load_dotenv

load_dotenv(".env.local")

# 1. Install Solc (Compiler)
try:
    install_solc("0.8.0")
except Exception:
    pass

# 2. Compile Contract
with open("contracts/BlockCICD.sol", "r") as f:
    contract_source_code = f.read()

compiled_sol = compile_source(
    contract_source_code,
    output_values=["abi", "bin"]
)

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
            Account = w3.eth.account.from_key(PRIVATE_KEY)
            Contract = w3.eth.contract(abi=abi, bytecode=contract_interface["bin"])
            
            print(f"🚀 Deploying from {Account.address}...")
            # Simple check to stop if no funds (prevents hard crash script)
            if w3.eth.get_balance(Account.address) == 0:
                 print("⚠️  Insufficient funds. Skipping deployment, but ABI is saved.")
                 exit(0)

            deploy_txn = Contract.constructor().build_transaction({
                'chainId': w3.eth.chain_id,
                'from': Account.address,
                'nonce': w3.eth.get_transaction_count(Account.address),
                'gasPrice': w3.eth.gas_price
            })
            
            signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"✅ Transaction Sent: {tx_hash.hex()}")
            print("⏳ Waiting for receipt... (Ctrl+C if this takes too long)")
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"📌 Contract Address: {tx_receipt.contractAddress}")
    except Exception as e:
        print(f"⚠️  Deployment skipped/failed: {e}")
        print("✅ ABI was saved successfully. You can proceed with Infrastructure.")
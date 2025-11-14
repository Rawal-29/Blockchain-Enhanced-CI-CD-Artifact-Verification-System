# deploy_contract.py

import os
import json
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv(".env.local")
RPC_URL = os.getenv("ETHEREUM_RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
ABI_FILE = "BlockCICD_ABI.json"

# --- 1. Setup & Connection ---
try:
    install_solc("0.8.0")
except Exception:
    pass # Assume solc is available

w3 = Web3(HTTPProvider(RPC_URL))
if not w3.is_connected():
    print(f"🛑 Error: Cannot connect to Ethereum node at {RPC_URL}")
    exit(1)

# --- 2. Compile Contract ---
with open("contracts/BlockCICD.sol", "r") as f:
    contract_source_code = f.read()

compiled_sol = compile_source(
    contract_source_code,
    output_values=["abi", "bin"]
)

contract_interface = compiled_sol.popitem()[1]
bytecode = contract_interface["bin"]
abi = contract_interface["abi"]

# --- 3. Save ABI (for FastAPI client) ---
with open(ABI_FILE, "w") as f:
    json.dump(abi, f)
print(f"✅ ABI saved to {ABI_FILE}")


# --- 4. Deploy Contract ---
Account = w3.eth.account.from_key(PRIVATE_KEY)
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

print("🚀 Deploying contract...")

deploy_txn = Contract.constructor().build_transaction({
    'chainId': w3.eth.chain_id,
    'from': Account.address,
    'nonce': w3.eth.get_transaction_count(Account.address),
    'gasPrice': w3.eth.gas_price
})

signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress

print("\n✅ Deployment Successful!")
print(f"📌 Contract Address: {contract_address}")
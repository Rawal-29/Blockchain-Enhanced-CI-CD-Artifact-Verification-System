import sys
import os
import hashlib
import json
from web3 import Web3, HTTPProvider
from eth_account import Account

# --- CONFIGURATION ---
RPC_URL = os.getenv("ETHEREUM_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
# Default to Zero Address if not set (Simulated Mode)
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
ABI_PATH = "BlockCICD_ABI.json" # Ensure this file is in your root

def get_contract():
    if not RPC_URL:
        print("❌ Error: Missing RPC URL")
        sys.exit(1)
    
    # Load ABI (or empty if missing during simulation)
    try:
        with open(ABI_PATH, "r") as f: 
            abi = json.load(f)
    except: 
        abi = []
        
    w3 = Web3(HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    return w3, contract

def calculate_file_hash(filepath):
    """Calculates SHA256 of a binary file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in 4KB chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return "0x" + sha256_hash.hexdigest()

def register_plan(filepath):
    print(f"🔒 Hashing plan file: {filepath}...")
    file_hash = calculate_file_hash(filepath)
    print(f"#️⃣  Generated Hash: {file_hash}")

    # SIMULATION CHECK
    if CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000":
        print("⚠️  [SIMULATION] Contract not deployed. Skipping blockchain write.")
        print("✅ Simulated Registration Successful.")
        return

    w3, contract = get_contract()
    account = Account.from_key(PRIVATE_KEY)
    
    # Build Transaction
    txn = contract.functions.storeHash(Web3.to_bytes(hexstr=file_hash)).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign & Send
    signed = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent! Hash: {tx_hash.hex()}")
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("⛓️  Plan successfully anchored to Blockchain.")

def verify_plan(filepath):
    print(f"🔍 Verifying plan file: {filepath}...")
    file_hash = calculate_file_hash(filepath)
    print(f"#️⃣  Calculated Hash: {file_hash}")
    
    # SIMULATION CHECK
    if CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000":
        print("⚠️  [SIMULATION] Contract not deployed. Assuming valid.")
        return

    w3, contract = get_contract()
    
    # Call Smart Contract (Read-Only)
    is_valid = contract.functions.verifyHash(Web3.to_bytes(hexstr=file_hash)).call()
    
    if is_valid:
        print("✅ SUCCESS: Plan verified on blockchain.")
    else:
        print("🚨 CRITICAL ALARM: Plan mismatch! Tampering detected.")
        sys.exit(1) # Fail the Pipeline

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tf_guard.py [register|verify] [filepath]")
        sys.exit(1)
        
    action = sys.argv[1]
    filepath = sys.argv[2]
    
    if action == "register":
        register_plan(filepath)
    elif action == "verify":
        verify_plan(filepath)
    else:
        print("Unknown command. Use 'register' or 'verify'.")
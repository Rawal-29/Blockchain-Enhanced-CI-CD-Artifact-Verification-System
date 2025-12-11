import sys
import os
import hashlib
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        print(f"❌ CRITICAL: File not found: {filepath}")
        sys.exit(1)
        
    with open(filepath, "rb") as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

def get_contract():
    rpc = os.getenv("ETHEREUM_RPC_URL")
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    address = os.getenv("CONTRACT_ADDRESS")

    if not rpc or not private_key or not address:
        print("❌ CRITICAL: Missing Environment Variables (RPC, KEY, or ADDRESS).")
        sys.exit(1)

    if address == "0x0000000000000000000000000000000000000000":
        print("❌ CRITICAL: Invalid Contract Address (Placeholder detected).")
        sys.exit(1)

    w3 = Web3(HTTPProvider(rpc))
    
    if not w3.is_connected():
        print("❌ CRITICAL: Failed to connect to Ethereum Node.")
        sys.exit(1)
        
    abi_path = "BlockCICD_ABI.json"
    if not os.path.exists(abi_path):
        abi_path = "../BlockCICD_ABI.json"
    
    if not os.path.exists(abi_path):
        print("❌ CRITICAL: ABI file (BlockCICD_ABI.json) not found.")
        sys.exit(1)

    with open(abi_path, "r") as f:
        abi = f.read()

    contract = w3.eth.contract(address=address, abi=abi)
    return w3, contract, private_key

def register(filepath):
    print(f"🔒 Registering Plan: {filepath}")
    file_hash = "0x" + get_file_hash(filepath)
    print(f"#️⃣  Hash: {file_hash}")

    try:
        w3, c, pk = get_contract()
        account = w3.eth.account.from_key(pk)
        
        balance = w3.eth.get_balance(account.address)
        if balance == 0:
            print("❌ CRITICAL: Wallet has 0 ETH. Cannot pay gas.")
            sys.exit(1)

        tx = c.functions.storeHash(file_hash).build_transaction({
            'chainId': w3.eth.chain_id,
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        })
        signed = w3.eth.account.sign_transaction(tx, private_key=pk)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Transaction Sent: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("✅ Block Confirmed: Hash Registered Successfully.")
        else:
            print("❌ CRITICAL: Transaction Reverted by EVM.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ CRITICAL ERROR during Registration: {e}")
        sys.exit(1)

def verify(filepath):
    print(f"🛡️ Verifying Plan: {filepath}")
    file_hash = "0x" + get_file_hash(filepath)
    print(f"#️⃣  Hash to Check: {file_hash}")

    try:
        w3, c, _ = get_contract()

        is_verified = c.functions.verifyHash(file_hash).call()
        
        if is_verified:
            print("✅ VERIFIED: Hash matches on-chain record.")
            sys.exit(0)
        else:
            print("🛑 SECURITY ALERT: Hash NOT found on-chain!")
            print("   Possible Reasons:")
            print("   1. File was modified after registration (Tampering).")
            print("   2. You forgot to run /tfplanfinal.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ CRITICAL ERROR during Verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tf_guard.py [register|verify] <tfplan_binary>")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command == "register":
        register(file_path)
    elif command == "verify":
        verify(file_path)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
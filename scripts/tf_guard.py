import sys
import os
import hashlib
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv(".env.local")


def get_file_hash(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()

def get_contract():
    rpc = os.getenv("ETHEREUM_RPC_URL")
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    address = os.getenv("CONTRACT_ADDRESS")

    if not rpc or not private_key or not address:
        raise Exception("Missing config: ETHEREUM_RPC_URL, DEPLOYER_PRIVATE_KEY, CONTRACT_ADDRESS required")

    if address == "0x0000000000000000000000000000000000000000":
        raise Exception("Zero contract address — deployment likely failed")

    w3 = Web3(HTTPProvider(rpc))
    if not w3.is_connected():
        raise Exception("RPC connection failed")

    abi_path = "BlockCICD_ABI.json"
    if not os.path.exists(abi_path):
        abi_path = "../BlockCICD_ABI.json"

    with open(abi_path, "r") as f:
        abi = f.read()

    contract = w3.eth.contract(address=address, abi=abi)
    return w3, contract, private_key

def register(filepath):
    print(f"Registering plan: {filepath}")
    hash_hex = get_file_hash(filepath)
    hash_bytes = bytes.fromhex(hash_hex)
    print(f"Hash: 0x{hash_hex}")

    w3, c, pk = get_contract()
    account = w3.eth.account.from_key(pk)

    if w3.eth.get_balance(account.address) == 0:
        raise Exception("Deployer account has 0 ETH — cannot pay gas")

    tx = c.functions.storeHash(hash_bytes).build_transaction({
        'chainId': w3.eth.chain_id,
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise Exception(f"Transaction reverted (receipt status 0): {tx_hash.hex()}")
    print("Block confirmed — hash registered on-chain")

def verify(filepath):
    print(f"Verifying plan: {filepath}")
    hash_hex = get_file_hash(filepath)
    hash_bytes = bytes.fromhex(hash_hex)
    print(f"Hash: 0x{hash_hex}")

    w3, c, _ = get_contract()
    is_verified = c.functions.verifyHash(hash_bytes).call()

    if is_verified:
        print("VERIFIED: hash exists on-chain")
    else:
        print("FAILED: hash not found on-chain — plan was not registered or has been tampered with")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tf_guard.py [register|verify] <plan_file>")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2]

    try:
        if command == "register":
            register(file_path)
        elif command == "verify":
            verify(file_path)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

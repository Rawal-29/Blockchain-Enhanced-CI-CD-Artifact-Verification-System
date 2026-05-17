import os
import sys
from web3 import Web3

STORE_HASH_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "hashValue", "type": "bytes32"}],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

RPC_URL = os.environ.get("ETHEREUM_RPC_URL")
RAW_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
ARTIFACT_HASH = os.environ.get("ARTIFACT_HASH", "")

if not all([RPC_URL, RAW_KEY, CONTRACT_ADDRESS, ARTIFACT_HASH]):
    print("ERROR: ETHEREUM_RPC_URL, DEPLOYER_PRIVATE_KEY, CONTRACT_ADDRESS, ARTIFACT_HASH all required")
    sys.exit(1)

PRIVATE_KEY = RAW_KEY if RAW_KEY.startswith("0x") else "0x" + RAW_KEY

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("ERROR: RPC connection failed — check ETHEREUM_RPC_URL")
    sys.exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Sender:   {account.address}")
print(f"Contract: {CONTRACT_ADDRESS}")
print(f"Hash:     {ARTIFACT_HASH}")

# Convert 64-char hex string to bytes32
hash_hex = ARTIFACT_HASH.removeprefix("0x")
if len(hash_hex) != 64:
    print(f"ERROR: ARTIFACT_HASH must be 64 hex chars (got {len(hash_hex)})")
    sys.exit(1)
hash_bytes32 = bytes.fromhex(hash_hex)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=STORE_HASH_ABI,
)

tx = contract.functions.storeHash(hash_bytes32).build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gasPrice": w3.eth.gas_price,
    "chainId": w3.eth.chain_id,
    "gas": 100000,
})

signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
print(f"Broadcast: {tx_hash.hex()}")

print("Waiting for receipt...")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
if receipt.status != 1:
    print(f"ERROR: Transaction reverted: {tx_hash.hex()}")
    sys.exit(1)

tx_hash_str = tx_hash.hex()
print(f"Confirmed in block {receipt.blockNumber}")
print(f"TRANSACTION_HASH: {tx_hash_str}")

github_output = os.environ.get("GITHUB_OUTPUT")
if github_output:
    with open(github_output, "a") as f:
        f.write(f"tx_hash={tx_hash_str}\n")

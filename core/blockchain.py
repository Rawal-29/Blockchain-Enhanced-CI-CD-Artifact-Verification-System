# core/blockchain.py

import os
import json
from web3 import Web3, HTTPProvider
from eth_account import Account
from dotenv import load_dotenv

# --- Configuration Loading ---
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

RPC_URL = os.getenv("ETHEREUM_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

# --- ABI Loading ---
try:
    with open("BlockCICD_ABI.json", "r") as f:
        CONTRACT_ABI = json.load(f)
except FileNotFoundError:
    raise RuntimeError("BlockCICD_ABI.json not found. Run deployment script first.")

def get_contract_instance():
    """Initializes and returns the Web3 connection and the Contract instance."""
    if not RPC_URL or not CONTRACT_ADDRESS:
        raise ValueError("Configuration variables (RPC_URL/CONTRACT_ADDRESS) are missing.")
        
    w3 = Web3(HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to Ethereum node at {RPC_URL}")
    
    contract_instance = w3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=CONTRACT_ABI
    )
    return w3, contract_instance

# --- CRITICAL CHANGE: Transaction Logic (Store Hash) ---
def store_artifact_hash(hash_value: str) -> str:
    """
    Registers the hash as bytes32 on the blockchain. 
    Requires PRIVATE_KEY and uses explicit gas parameters.
    """
    w3, contract = get_contract_instance()
    if not PRIVATE_KEY:
        raise ValueError("DEPLOYER_PRIVATE_KEY is required for transactions.")
        
    account = Account.from_key(PRIVATE_KEY)

    # Convert the 64-character hash string into bytes32 format for the contract
    # The hash should be a clean hex string (no 0x prefix) from the API input
    hash_value_bytes32 = Web3.to_bytes(hexstr=hash_value)
    
    # 1. Build the transaction skeleton
    txn_skeleton = contract.functions.storeHash(hash_value_bytes32).build_transaction({
        'from': account.address
    })
    
    # 2. Build the final transaction with explicit parameters
    txn = {
        'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
        'from': account.address,
        'value': 0,
        'gas': w3.eth.estimate_gas(txn_skeleton), # Explicitly estimate gas
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'data': txn_skeleton['data'], 
        'chainId': w3.eth.chain_id,
    }
    
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction) 
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()

# core/blockchain.py (Update verify_artifact_hash function)

def verify_artifact_hash(hash_value: str) -> bool:
    """Reads the blockchain to verify if the hash is registered."""
    w3, contract = get_contract_instance()

    # CRITICAL FIX: Ensure the input hash is treated as a 64-character hex string
    # and padded to 32 bytes with Web3.to_bytes.
    hash_value_bytes32 = Web3.to_bytes(hexstr=hash_value)
    
    # The check should be called exactly as the storage was made.
    is_verified = contract.functions.verifyHash(hash_value_bytes32).call()
    return is_verified

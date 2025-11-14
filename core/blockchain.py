import os
import json
from web3 import Web3, HTTPProvider
from eth_account import Account
from dotenv import load_dotenv # Used for loading .env.local

# --- CRITICAL: Delete or comment out the old, conflicting import ---
# from core.config import INFURA_URL, CONTRACT_ADDRESS, PRIVATE_KEY 

# --- Configuration Loading ---
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

# Variables read directly from the OS environment (in production) or .env.local (locally)
RPC_URL = os.getenv("ETHEREUM_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

# --- ABI Loading ---
try:
    # Assumes the ABI file is in the root directory
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

def store_artifact_hash(hash_value: str) -> str:
    """Registers the hash on the blockchain (CI Phase). Requires PRIVATE_KEY."""
    w3, contract = get_contract_instance()
    if not PRIVATE_KEY:
        raise ValueError("DEPLOYER_PRIVATE_KEY is required for transactions.")
        
    account = Account.from_key(PRIVATE_KEY)
    
    txn = contract.functions.storeHash(hash_value).build_transaction({
        'chainId': w3.eth.chain_id,
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price
    })
    
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction) 
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()

def verify_artifact_hash(hash_value: str) -> bool:
    """Reads the blockchain to verify if the hash is registered (CD Phase)."""
    w3, contract = get_contract_instance()
    is_verified = contract.functions.verifyHash(hash_value).call()
    return is_verified
from web3 import Web3
from core.config import INFURA_URL, CONTRACT_ADDRESS, PRIVATE_KEY
import json, os

web3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

ABI_PATH = os.path.join(os.path.dirname(__file__), "../contracts/abi.json")
with open(ABI_PATH) as f:
    contract_abi = json.load(f)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def send_txn(function):
    nonce = web3.eth.get_transaction_count(account.address)
    txn = function.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": web3.to_wei("10", "gwei")
    })
    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return web3.to_hex(tx_hash)

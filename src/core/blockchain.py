import json
from web3 import Web3, HTTPProvider
from eth_account import Account
from .config import RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY

try:
    with open("BlockCICD_ABI.json", "r") as f: ABI = json.load(f)
except: ABI = []

def get_contract():
    w3 = Web3(HTTPProvider(RPC_URL))
    return w3, w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def store_hash(h):
    w3, c = get_contract()
    acct = Account.from_key(PRIVATE_KEY)
    tx = c.functions.storeHash(Web3.to_bytes(hexstr=h)).build_transaction({
        'from': acct.address, 'nonce': w3.eth.get_transaction_count(acct.address), 'gasPrice': w3.eth.gas_price
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()

def verify_hash(h):
    _, c = get_contract()
    return c.functions.verifyHash(Web3.to_bytes(hexstr=h)).call()
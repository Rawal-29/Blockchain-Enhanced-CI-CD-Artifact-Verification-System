import sys, os, hashlib, json
from web3 import Web3, HTTPProvider
from eth_account import Account

RPC, KEY, ADDR = os.getenv("ETHEREUM_RPC_URL"), os.getenv("DEPLOYER_PRIVATE_KEY"), os.getenv("CONTRACT_ADDRESS")

def get_contract():
    if not RPC: sys.exit(1)
    try:
        with open("BlockCICD_ABI.json", "r") as f: abi = json.load(f)
    except: abi = []
    w3 = Web3(HTTPProvider(RPC))
    return w3, w3.eth.contract(address=ADDR, abi=abi)

def calc_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(4096), b""): h.update(c)
    return "0x" + h.hexdigest()

def register(path):
    h = calc_hash(path)
    w3, c = get_contract()
    acct = Account.from_key(KEY)
    tx = c.functions.storeHash(Web3.to_bytes(hexstr=h)).build_transaction({
        'from': acct.address, 'nonce': w3.eth.get_transaction_count(acct.address), 'gasPrice': w3.eth.gas_price
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=KEY)
    w3.eth.send_raw_transaction(signed.raw_transaction)

def verify(path):
    h = calc_hash(path)
    _, c = get_contract()
    if c.functions.verifyHash(Web3.to_bytes(hexstr=h)).call(): sys.exit(0)
    else: sys.exit(1)

if __name__ == "__main__":
    if sys.argv[1] == "register": register(sys.argv[2])
    elif sys.argv[1] == "verify": verify(sys.argv[2])
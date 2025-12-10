import os, json, sys
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc, set_solc_version
from dotenv import load_dotenv

load_dotenv(".env.local")
CI_SOLC = "/usr/local/bin/solc"
args = {"solc_binary": CI_SOLC} if os.path.exists(CI_SOLC) else {"solc_version": "0.8.0"}

if "solc_version" in args:
    try: install_solc("0.8.0"); set_solc_version("0.8.0")
    except: pass

try:
    with open("contracts/BlockCICD.sol", "r") as f: src = f.read()
    compiled = compile_source(src, output_values=["abi", "bin"], allow_paths=".", **args)
except: sys.exit(1)

abi = compiled["<stdin>:BlockCICD"]["abi"]
bin = compiled["<stdin>:BlockCICD"]["bin"]
with open("BlockCICD_ABI.json", "w") as f: json.dump(abi, f)

RPC, KEY, DEPLOY = os.getenv("ETHEREUM_RPC_URL"), os.getenv("DEPLOYER_PRIVATE_KEY"), os.getenv("DEPLOY_ON_MERGE", "true")
if RPC and KEY and DEPLOY.lower() == "true":
    w3 = Web3(HTTPProvider(RPC))
    acct = w3.eth.account.from_key(KEY)
    Contract = w3.eth.contract(abi=abi, bytecode=bin)
    tx = Contract.constructor().build_transaction({
        'chainId': w3.eth.chain_id, 'from': acct.address, 'nonce': w3.eth.get_transaction_count(acct.address), 'gasPrice': w3.eth.gas_price
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=KEY)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))
    with open("infrastructure/terraform.auto.tfvars", "w") as f:
        f.write(f'contract_address = "{receipt.contractAddress}"\n')
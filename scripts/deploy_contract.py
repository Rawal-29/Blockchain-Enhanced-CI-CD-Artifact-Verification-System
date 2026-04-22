import os
import json
import sys
from web3 import Web3, HTTPProvider
from solcx import compile_source, install_solc, set_solc_version
from dotenv import load_dotenv

load_dotenv(".env.local")

# C10: skip deployment entirely unless explicitly enabled
DEPLOY_ON_MERGE = os.getenv("DEPLOY_ON_MERGE", "false").lower() == "true"
if not DEPLOY_ON_MERGE:
    print("DEPLOY_ON_MERGE is not 'true' — skipping contract deployment.")
    print("Set the DEPLOY_ON_MERGE repository variable to 'true' for a one-time deploy.")
    sys.exit(0)

CI_SOLC_PATH = "/usr/local/bin/solc"
compile_args = {"solc_version": "0.8.20"}

if os.path.exists(CI_SOLC_PATH):
    print(f"Using CI solc at {CI_SOLC_PATH}")
    compile_args = {"solc_binary": CI_SOLC_PATH}
else:
    install_solc("0.8.20")
    set_solc_version("0.8.20")

print("Compiling BlockCICD.sol...")
try:
    with open("contracts/BlockCICD.sol", "r") as f:
        source = f.read()

    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        import_remappings=["@openzeppelin=node_modules/@openzeppelin"],
        base_path=".",
        allow_paths=".",
        **compile_args
    )
except Exception as e:
    print(f"Compilation failed: {e}")
    sys.exit(1)

contract_id = "<stdin>:BlockCICD"
if contract_id not in compiled:
    contract_id = list(compiled.keys())[0]

abi = compiled[contract_id]["abi"]
bytecode = compiled[contract_id]["bin"]

with open("BlockCICD_ABI.json", "w") as f:
    json.dump(abi, f)

RPC_URL = os.getenv("ETHEREUM_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
TF_VAR_PATH = "infrastructure/terraform.auto.tfvars"

if not RPC_URL or not PRIVATE_KEY:
    print("Missing secrets: ETHEREUM_RPC_URL and DEPLOYER_PRIVATE_KEY are required")
    sys.exit(1)

w3 = Web3(HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("RPC connection failed — check ETHEREUM_RPC_URL")
    sys.exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Deploying from: {account.address}")

balance = w3.eth.get_balance(account.address)
if balance == 0:
    print("Insufficient funds (0 ETH) — cannot pay deployment gas")
    sys.exit(1)

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = Contract.constructor().build_transaction({
    'chainId': w3.eth.chain_id,
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gasPrice': w3.eth.gas_price,
})

signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Transaction sent: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# C11: fail loudly if the deploy transaction itself reverted
if receipt.status != 1:
    print(f"Deployment transaction reverted: {tx_hash.hex()}")
    sys.exit(1)

contract_address = receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

with open(TF_VAR_PATH, "w") as f:
    f.write(f'contract_address = "{contract_address}"\n')

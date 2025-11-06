import os

INFURA_URL = os.getenv("INFURA_URL", "https://sepolia.infura.io/v3/929714addbc54cb99e56a6d1ce8f80d1")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0xYOUR_CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "your_private_key")
DB_URL = os.getenv("DB_URL", "sqlite:///blockcicd.db")

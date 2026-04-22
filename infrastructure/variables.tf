variable "image_tag" {
  description = "The docker image tag to deploy"
  type        = string
}

variable "contract_address" {
  description = "The deployed smart contract address"
  type        = string
  default     = "0x0000000000000000000000000000000000000000"
}

# C9: secrets injected from GitHub Actions secrets via TF_VAR_ env vars at plan/apply time
variable "ethereum_rpc_url" {
  description = "Ethereum RPC endpoint for the Lambda"
  type        = string
  sensitive   = true
  default     = ""
}

variable "deployer_private_key" {
  description = "Ethereum deployer private key for the Lambda"
  type        = string
  sensitive   = true
  default     = ""
}


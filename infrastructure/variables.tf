# infrastructure/variables.tf

variable "project_name" {
  description = "Name for the OpenShift project/namespace"
  default     = "blockchain-verifier"
}

variable "image_tag" {
  description = "Docker image tag for the verifier application"
  default     = "latest"
}

variable "contract_address" {
  description = "The deployed Ethereum smart contract address"
  type        = string
}

variable "rpc_url" {
  description = "Ethereum Node RPC URL (Sepolia/Mainnet)"
  type        = string
}
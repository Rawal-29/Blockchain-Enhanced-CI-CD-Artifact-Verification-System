variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "contract_address" {
  description = "Deployed BlockCICD smart contract address on Sepolia"
  type        = string
  default     = "0x0000000000000000000000000000000000000000"
}

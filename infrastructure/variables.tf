variable "image_tag" {
  description = "The docker image tag to deploy"
  type        = string
}

variable "contract_address" {
  description = "The deployed smart contract address"
  type        = string
  default     = "0x0000000000000000000000000000000000000000"
}


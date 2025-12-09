terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket  = "blockchain-state-rawal29-2025" 
    key     = "prod/terraform.tfstate"
    region  = "us-east-2"
  }
}
provider "aws" { region = "us-east-2" }


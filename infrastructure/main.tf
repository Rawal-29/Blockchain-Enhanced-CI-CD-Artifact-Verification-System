terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket  = "blockchain-api-tf-state-rawal" # <--- REPLACE WITH YOUR BUCKET NAME
    key     = "prod/terraform.tfstate"
    region  = "us-east-1"
  }
}
provider "aws" { region = "us-east-1" }
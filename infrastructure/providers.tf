terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  # H3: encrypt state at rest; lock against concurrent runs
  backend "s3" {
    bucket         = "blockchain-state-rawal29-2025"
    key            = "prod/terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
    dynamodb_table = "blockchain-terraform-lock"
  }
}

provider "aws" { region = "us-east-2" }

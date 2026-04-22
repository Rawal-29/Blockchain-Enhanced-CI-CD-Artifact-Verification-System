terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  # H3: encrypt state at rest
  # Note: dynamodb_table locking omitted until the table is created on first apply.
  # After first successful terraform apply (which provisions the DynamoDB table),
  # add: dynamodb_table = "blockchain-terraform-lock"
  # and ensure the IAM role has dynamodb:GetItem/PutItem/DeleteItem on that table.
  backend "s3" {
    bucket  = "blockchain-state-rawal29-2025"
    key     = "prod/terraform.tfstate"
    region  = "us-east-2"
    encrypt = true
  }
}

provider "aws" { region = "us-east-2" }

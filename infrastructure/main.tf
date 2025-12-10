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

resource "aws_s3_bucket" "artifact_bucket" {
  bucket_prefix = "blockchain-artifacts-"
  
  tags = {
    Project = "BlockCICD"
    Environment = "Production"
  }
}


resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.artifact_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.artifact_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}












resource "aws_s3_bucket" "artifact_bucket" {
  bucket_prefix = "blockchain-artifacts-"
  tags          = { Project = "BlockCICD", Type = "Artifacts" }
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.artifact_bucket.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "block_private" {
  bucket                  = aws_s3_bucket.artifact_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "website_bucket" {
  bucket_prefix = "auditor-dashboard-"
  tags          = { Project = "BlockCICD", Type = "Dashboard" }
}

resource "aws_s3_bucket_website_configuration" "website_config" {
  bucket = aws_s3_bucket.website_bucket.id
  index_document { suffix = "index.html" }
}

resource "aws_s3_bucket_public_access_block" "block_public_read" {
  bucket                  = aws_s3_bucket.website_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.website_bucket.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Sid       = "PublicRead",
      Effect    = "Allow",
      Principal = "*",
      Action    = "s3:GetObject",
      Resource  = "${aws_s3_bucket.website_bucket.arn}/*"
    }]
  })
  depends_on = [aws_s3_bucket_public_access_block.block_public_read]
}

resource "aws_s3_bucket" "pipeline_test_bucket" {
  bucket = "rawal-cicd-pipeline-test-2026"

  tags = {
    Environment = "Testing"
    Pipeline    = "ChatOps-End-To-End"
  }
}

resource "aws_s3_bucket" "native_web3_test_bucket" {
  bucket = "rawal-cicd-native-web3-test-bucket-2026"

  tags = {
    Environment    = "Testing"
    Pipeline       = "ChatOps-E2E"
    E2E_Test_Status = "Whitelist_Passed"
  }
}

resource "aws_sqs_queue" "blockcicd_standard_queue" {
  name = "blockcicd-standard-queue"

  tags = {
    Project = "BlockCICD"
  }
}

resource "aws_sns_topic" "blockcicd_standard_topic" {
  name = "blockcicd-standard-topic"

  tags = {
    Project = "BlockCICD"
  }
}

resource "aws_s3_bucket" "malicious_backdoor_bucket" {
  bucket = "blockcicd-data-export-bucket"

  tags = {
    Project = "BlockCICD"
  }
}

resource "aws_s3_bucket_public_access_block" "malicious_backdoor_bucket_public" {
  bucket = aws_s3_bucket.malicious_backdoor_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "malicious_backdoor_bucket_policy" {
  bucket = aws_s3_bucket.malicious_backdoor_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.malicious_backdoor_bucket.arn}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.malicious_backdoor_bucket_public]
}

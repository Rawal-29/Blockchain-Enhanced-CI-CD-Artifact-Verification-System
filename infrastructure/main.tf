# GitHub Actions OIDC provider — enables keyless auth via id-token: write
resource "aws_iam_openid_connect_provider" "github_actions" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  # Thumbprints for token.actions.githubusercontent.com (primary + backup)
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]
  tags = { Project = "BlockCICD", Purpose = "GitHubActionsOIDC" }
}

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

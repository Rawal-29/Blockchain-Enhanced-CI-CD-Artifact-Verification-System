output "artifact_bucket_name" {
  description = "The name of the secure bucket for smart contract artifacts"
  value       = aws_s3_bucket.artifact_bucket.id
}

output "api_url" {
  value = aws_lambda_function_url.api_url.function_url
}
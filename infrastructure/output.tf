output "artifact_bucket_name" { value = aws_s3_bucket.artifact_bucket.id }
output "website_bucket_name" { value = aws_s3_bucket.website_bucket.id }
output "dashboard_url" { value = aws_s3_bucket_website_configuration.website_config.website_endpoint }
output "api_url" { value = aws_lambda_function_url.api_url.function_url }
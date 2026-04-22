resource "aws_lambda_function" "api" {
  function_name = "blockchain-verification-api"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "151462990345.dkr.ecr.us-east-2.amazonaws.com/blockchain-api:${var.image_tag}"
  timeout       = 30
  memory_size   = 512

  environment {
    variables = {
      # C9: secrets passed via TF_VAR_ env vars from GitHub Actions secrets at plan/apply time
      ETHEREUM_RPC_URL     = var.ethereum_rpc_url
      CONTRACT_ADDRESS     = var.contract_address
      DEPLOYER_PRIVATE_KEY = var.deployer_private_key
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "blockchain_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_ecr_repository_policy" "lambda_pull" {
  repository = "blockchain-api"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Sid = "LambdaPull", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" },
      Action = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
    }]
  })
}

# C7: require AWS IAM auth — removes the public unauthenticated endpoint
resource "aws_lambda_function_url" "api_url" {
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "AWS_IAM"
}

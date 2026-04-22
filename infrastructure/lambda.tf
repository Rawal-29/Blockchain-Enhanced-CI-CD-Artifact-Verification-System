# C9: read secrets from SSM Parameter Store rather than hard-coding "placeholder"
data "aws_ssm_parameter" "ethereum_rpc_url" {
  name = "/blockchain-cicd/ethereum-rpc-url"
}

data "aws_ssm_parameter" "deployer_private_key" {
  name            = "/blockchain-cicd/deployer-private-key"
  with_decryption = true
}

resource "aws_lambda_function" "api" {
  function_name = "blockchain-verification-api"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "151462990345.dkr.ecr.us-east-2.amazonaws.com/blockchain-api:${var.image_tag}"
  timeout       = 30
  memory_size   = 512

  environment {
    variables = {
      ETHEREUM_RPC_URL     = data.aws_ssm_parameter.ethereum_rpc_url.value
      CONTRACT_ADDRESS     = var.contract_address
      DEPLOYER_PRIVATE_KEY = data.aws_ssm_parameter.deployer_private_key.value
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

# Allow Lambda to read its SSM secrets
resource "aws_iam_role_policy" "lambda_ssm" {
  name = "lambda_ssm_read"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["ssm:GetParameter"],
      Resource = [
        "arn:aws:ssm:us-east-2:*:parameter/blockchain-cicd/*"
      ]
    }]
  })
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

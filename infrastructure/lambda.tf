resource "aws_lambda_function" "api" {
  function_name = "blockchain-verification-api"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  # REPLACE '123456789' WITH YOUR REAL AWS ACCOUNT ID BELOW
  image_uri     = "123456789.dkr.ecr.us-east-1.amazonaws.com/blockchain-api:${var.image_tag}"
  timeout       = 30
  memory_size   = 512

  lifecycle { ignore_changes = [image_uri] }

  environment {
    variables = {
        # We use placeholders. The real values are injected via GitHub Actions/AWS Console
        ETHEREUM_RPC_URL     = "placeholder"
        CONTRACT_ADDRESS     = "placeholder"
        DEPLOYER_PRIVATE_KEY = "placeholder"
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
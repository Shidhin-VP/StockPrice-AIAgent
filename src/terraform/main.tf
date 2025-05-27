provider "aws" {
  region ="us-east-1"
}

# variable "NeedtoBuild" {
#   description = "Trigger build? Yes or No"
#   type=string
# }

# resource "null_resource" "rebuild_program" {
#   triggers={
#     build=var.NeedtoBuild
#   }
# }

resource "aws_iam_role" "StockLambdaRole" {
  name = "StockAIAgent_LambdaRole"
  description = "Role for Lambda Service for the StockPriceAIAgent Project"
  assume_role_policy = jsonencode({
    Version="2012-10-17",
    Statement=[{
        Effect="Allow",
        Principal={
            Service="lambda.amazonaws.com"
        },
        Action="sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "StockBedrockAccess" {
  name = "StockAIAgent_BedrockAccess"
  description = "Policy for StockAIAgent_LambdaRole to Access Bedrock for StockPriceAIAgent Project"
  policy = jsonencode({
    Version="2012-10-17",
    Statement=[{
        Effect="Allow",
        Action=[
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
        ],
        Resource="*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "StockPolicyAttachment" {
  policy_arn = aws_iam_policy.StockBedrockAccess.arn
  role = aws_iam_role.StockLambdaRole.name
}

resource "aws_iam_role_policy_attachment" "StockPolicyAttachmentforCloudLogging" {
  role = aws_iam_role.StockLambdaRole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_ecr_repository" "ECR_Existing_Repo" {
  name = "stockprice_ai-agent-dockerfile"
}

data "aws_ecr_image" "ECR_Latest_Image" {
  repository_name = data.aws_ecr_repository.ECR_Existing_Repo.name
  image_tag = "latest"
}

resource "aws_lambda_function" "StockLambdaFunction" {
  function_name = "StockAIAgentLambdaFunction"
  description = "Lambda Function for the StockPriceAIAgent Project"
  package_type = "Image"
  //image_uri = "${data.aws_ecr_repository.ECR_Existing_Repo.repository_url}:latest"
  image_uri = data.aws_ecr_image.ECR_Latest_Image.image_uri
  role = aws_iam_role.StockLambdaRole.arn
  timeout = 120
}

#API Gateway

resource "aws_api_gateway_rest_api" "StockAPIGateway" {
  name = "StockAIAgent_APIGatewayREST"
  description = "API Gateway for Accessing the Lambda from any Network"
}

resource "aws_api_gateway_resource" "StockAPIGatewayResource" {
  rest_api_id = aws_api_gateway_rest_api.StockAPIGateway.id
  parent_id = aws_api_gateway_rest_api.StockAPIGateway.root_resource_id
  path_part = "prompt"
}

resource "aws_api_gateway_method" "StockAPIGatewayMethod" {
  rest_api_id = aws_api_gateway_rest_api.StockAPIGateway.id
  resource_id = aws_api_gateway_resource.StockAPIGatewayResource.id
  http_method = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "StockAPIGatewayIntegration" {
  rest_api_id = aws_api_gateway_rest_api.StockAPIGateway.id
  resource_id = aws_api_gateway_resource.StockAPIGatewayResource.id
  http_method = aws_api_gateway_method.StockAPIGatewayMethod.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri=aws_lambda_function.StockLambdaFunction.invoke_arn
}

resource "aws_lambda_permission" "StockAPIGatewayLambdaPermission" {
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.StockLambdaFunction.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.StockAPIGateway.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "StockAPIGatewayDeployment" {
  depends_on = [ aws_api_gateway_integration.StockAPIGatewayIntegration ]
  rest_api_id = aws_api_gateway_rest_api.StockAPIGateway.id
  description = "Deploying API For StockAPIGateway to Lambda"
}

resource "aws_api_gateway_stage" "StockAPIGatewayStage" {
  stage_name = "prod"
  rest_api_id = aws_api_gateway_rest_api.StockAPIGateway.id
  deployment_id = aws_api_gateway_deployment.StockAPIGatewayDeployment.id
}

output "api_gateway_url" {
  value="https://${aws_api_gateway_rest_api.StockAPIGateway.id}.execute-api.us-east-1.amazonaws.com/prod/prompt"
}
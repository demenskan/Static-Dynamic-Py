# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0
# to configure the AWS access thru envinronment variables:
# export AWS_ACCESS_KEY_ID= (Your access key ID)
# export AWS_SECRET_ACCESS_KEY = (your secret)
# ... or via aws config tool


provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      hashicorp-learn = "lambda-api-gateway"
    }
  }

}

resource "random_pet" "lambda_bucket_name" {
  prefix = "demenskan-snas-lambda"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = random_pet.lambda_bucket_name.id
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.lambda_bucket.id
  acl    = "private"
}

data "archive_file" "lambda_page_generator" {
  type = "zip"
  source_dir  = "${path.module}/page-generator"
  output_path = "${path.module}/page-generator.zip"
}

resource "aws_s3_object" "lambda_page_generator" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "page-generator.zip"
  source = data.archive_file.lambda_page_generator.output_path
  etag = filemd5(data.archive_file.lambda_page_generator.output_path)
}

resource "aws_lambda_function" "page_generator" {
  function_name = "PageGenerator"
  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_page_generator.key
  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_page_generator.output_base64sha256
  role = aws_iam_role.lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "page_generator" {
  name = "/aws/lambda/${aws_lambda_function.page_generator.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [ "sts:AssumeRole" ],
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

######

resource "aws_apigatewayv2_api" "lambda" {
  name          = "serverless_lambda_gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id
  name        = "serverless_lambda_stage"
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "page_generator" {
  api_id = aws_apigatewayv2_api.lambda.id
  integration_uri    = aws_lambda_function.page_generator.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "page_generator" {
  api_id = aws_apigatewayv2_api.lambda.id
  route_key = "GET /page"
  target    = "integrations/${aws_apigatewayv2_integration.hello_world.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"
  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.page_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}


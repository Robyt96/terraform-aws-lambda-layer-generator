module "create_python_library_lambda_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.1"

  source_path   = "${path.module}/src"
  handler       = "create_python_library_lambda_layer.lambda_handler"
  function_name = var.lambda_name
  role_name     = "${var.lambda_name}-role"
  description   = "Create Zip with python libraries. Put Zip on S3. Create lambda layer from Zip. Add resource policy to layer"
  runtime       = "python3.12"
  timeout       = 300
  memory_size   = 2048
  tags          = var.tags
  environment_variables = {
    "BUCKET_NAME"        = var.bucket_name
    "BUCKET_PATH_PREFIX" = var.bucket_path_prefix
    "ORGANIZATION_ID"    = var.organization_id
  }

  cloudwatch_logs_retention_in_days = 90
}

data "aws_iam_policy_document" "create_python_library_lambda_layer_s3_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:PutObject",
      "s3:PutObjectAcl"
    ]
    resources = [
      "arn:aws:s3:::${var.bucket_name}/${var.bucket_path_prefix}/*"
    ]
  }
}

data "aws_iam_policy_document" "create_python_library_lambda_layer_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "lambda:PublishLayerVersion",
      "lambda:AddLayerVersionPermission"
    ]
    resources = [
      "arn:aws:lambda:*:${data.aws_caller_identity.current.account_id}:layer:*"
    ]
  }
}

resource "aws_iam_role_policy" "create_python_library_lambda_layer_s3_policy" {
  name   = "lambda-s3-policy"
  role   = module.create_python_library_lambda_layer.lambda_role_name
  policy = data.aws_iam_policy_document.create_python_library_lambda_layer_s3_policy.json
}

resource "aws_iam_role_policy" "create_python_library_lambda_layer_lambda_policy" {
  name   = "lambda-lambda-policy"
  role   = module.create_python_library_lambda_layer.lambda_role_name
  policy = data.aws_iam_policy_document.create_python_library_lambda_layer_lambda_policy.json
}

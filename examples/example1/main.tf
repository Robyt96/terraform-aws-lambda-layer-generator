provider "aws" {
  region = "eu-central-1"
}

module "lambda_layer_generator" {
  source = "./terraform-aws-lambda-layer-generator"

  bucket_name     = "my-bucket-for-layers-zip"
  organization_id = "o-1234xyz"
}

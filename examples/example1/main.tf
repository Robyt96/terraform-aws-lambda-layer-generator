provider "aws" {
  region = "eu-central-1"
}

module "lambda_layer_generator" {
  source  = "Robyt96/lambda-layer-generator/aws"
  version = "x.y.z" # check correct version

  bucket_name     = "my-bucket-for-layers-zip"
  organization_id = "o-1234xyz"
}

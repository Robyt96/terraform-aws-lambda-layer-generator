
variable "bucket_name" {
  description = "Name of an existing S3 bucket where layer zip files will be stored."
  type        = string
}

variable "bucket_path_prefix" {
  description = "Prefix under which layer zip files will be stored inside the bucket."
  type        = string
  default     = "lambda_layers"
}

variable "lambda_name" {
  description = "Name of the lambda function to be created."
  type        = string
  default     = "create-python-library-lambda-layer"
}

variable "organization_id" {
  description = "ID of the AWS organization where layers will be shared."
  type        = string
  default     = ""
}

variable "tags" {
  description = "A map of tags to assign to resources."
  type        = map(string)
  default     = {}
}

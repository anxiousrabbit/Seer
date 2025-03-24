variable "region" {
    type = string
    default = "us-east-2"
}

variable "filename" {
    type = string
    default = "lambda/dynamo/dynamo.zip"
}

variable "function_name" {
  type = string
  default = "seerLambda"
}

variable "handler" {
    type = string
    default = "dynamo.lambda_handler"
}

variable "runtime" {
    type = string
    default = "python3.9"
}

variable "bucket_name" {
  
}
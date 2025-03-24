variable "region" {
    type = string
    default = "us-east-2"
}

variable "filename" {
    type = string
    default = "lambda/init/seerInit.zip"
}

variable "function_name" {
  type = string
  default = "seerInit"
}

variable "handler" {
    type = string
    default = "seerInit.lambda_handler"
}

variable "runtime" {
    type = string
    default = "python3.9"
}

variable "bucket_name" {
  
}
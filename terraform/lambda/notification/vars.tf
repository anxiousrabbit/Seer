variable "region" {
    type = string
    default = "us-east-2"
}

variable "permision_statement" {
    type = string
    default = "AllowExecutionFromS3Bucket"
}

variable "action" {
    type = string
    default = "lambda:InvokeFunction"
}

variable "principal" {
    type = string
    default = "s3.amazonaws.com"
}

variable "s3_bucket" {
    type = string
}
variable "filename" {
    type = string
    default = "lambda/init/seerNotif.zip"
}

variable "function_name" {
  type = string
  default = "seerNotif"
}

variable "handler" {
    type = string
    default = "seerNotif.lambda_handler"
}

variable "runtime" {
    type = string
    default = "python3.9"
}

variable "bucket_id" {
    type = string
}

variable "prefix" {
    type = string
    default = "compromised/"
}
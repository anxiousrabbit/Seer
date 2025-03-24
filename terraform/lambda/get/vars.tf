variable "filename" {
    type = string
    default = "lambda/get/seerGet.zip"
}

variable "function_name" {
  type = string
  default = "seerGet"
}

variable "handler" {
    type = string
    default = "seerGet.lambda_handler"
}

variable "runtime" {
    type = string
    default = "python3.9"
}

variable "bucket_name" {
  
}
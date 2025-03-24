variable "gatewayName" {
    type = string
    default = "seerGateway"
}

variable "path" {
    type = string
    default = "POST"
}

variable "init_path" {
    type = string
    default = "seerInit"
}

variable "get_path" {
    type = string
    default = "seerGet"
}

variable "method" {
    type = string
    default = "POST"
}

variable "authorization" {
    type = string
    default = "NONE"
}

variable "type" {
    type = string
    default = "AWS_PROXY"
}

variable "post_invoke_arn" {
    type = string
}

variable "init_invoke_arn" {
    type = string
}

variable "get_invoke_arn" {
    type = string
}

variable "stage_name" {
    type = string
    default = "prod"
}

variable "usage_plan" {
    type = string
    default = "dynamo_usage_plan"
}

variable "rate_limit" {
    type = number
    default = 5
}

variable "burst_limit" {
    type = number
    default = 10
}

variable "api_key" {
    type = string
    default = "seerGatewayKey"
}

variable "key_type" {
    type = string
    default = "API_KEY"
}

variable "statement_id" {
    type = string
    default = "AllowExecutionFromAPIGateway"
}

variable "action" {
    type = string
    default = "lambda:InvokeFunction"
}

variable "post_function_name" {
    type = string
}

variable "init_function_name" {
    type = string
}

variable "get_function_name" {
    type = string
}

variable "principal" {
    type = string
    default = "apigateway.amazonaws.com"
}

variable "api_gateway_region" {
    type = string
}

variable "api_gateway_account_id" {
    type = string
}

variable "status_code" {
    type = string
    default = "200"
}
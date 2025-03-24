resource "aws_api_gateway_rest_api" "seerGateway" {
    name = var.gatewayName
}

resource "aws_api_gateway_resource" "post_resource" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    parent_id = aws_api_gateway_rest_api.seerGateway.root_resource_id
    path_part = var.path
}

resource "aws_api_gateway_resource" "init_resource" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    parent_id = aws_api_gateway_rest_api.seerGateway.root_resource_id
    path_part = var.init_path
}

resource "aws_api_gateway_resource" "get_resource" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    parent_id = aws_api_gateway_rest_api.seerGateway.root_resource_id
    path_part = var.get_path
}

resource "aws_api_gateway_method" "post_method" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    resource_id = aws_api_gateway_resource.post_resource.id
    http_method = var.method
    api_key_required = true
    authorization = var.authorization
}

resource "aws_api_gateway_method" "init_method" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    resource_id = aws_api_gateway_resource.init_resource.id
    http_method = var.method
    api_key_required = true
    authorization = var.authorization
}

resource "aws_api_gateway_method" "get_method" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    resource_id = aws_api_gateway_resource.get_resource.id
    http_method = var.method
    api_key_required = true
    authorization = var.authorization
}

resource "aws_api_gateway_integration" "integration" {
    http_method = aws_api_gateway_method.post_method.http_method
    integration_http_method = var.method
    resource_id = aws_api_gateway_resource.post_resource.id
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    type = var.type
    uri = var.post_invoke_arn
}

resource "aws_api_gateway_integration" "init_integration" {
    http_method = aws_api_gateway_method.init_method.http_method
    integration_http_method = var.method
    resource_id = aws_api_gateway_resource.init_resource.id
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    type = var.type
    uri = var.init_invoke_arn
}

resource "aws_api_gateway_integration" "get_integration" {
    http_method = aws_api_gateway_method.get_method.http_method
    integration_http_method = var.method
    resource_id = aws_api_gateway_resource.get_resource.id
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    type = var.type
    uri = var.get_invoke_arn
}

resource "aws_api_gateway_usage_plan" "usage_plan" {
    name = var.usage_plan

    api_stages {
        api_id = aws_api_gateway_rest_api.seerGateway.id
        stage = aws_api_gateway_stage.prod.stage_name
    }
    throttle_settings {
        burst_limit = var.burst_limit
        rate_limit = var.rate_limit
    }
}

resource "aws_api_gateway_api_key" "api_key" {
    name = var.api_key
}

resource "aws_api_gateway_usage_plan_key" "usage_plan_key" {
    key_id = aws_api_gateway_api_key.api_key.id
    key_type = var.key_type
    usage_plan_id = aws_api_gateway_usage_plan.usage_plan.id
}

resource "aws_lambda_permission" "lambda_api" {
    statement_id = var.statement_id
    action = var.action
    function_name = var.post_function_name
    principal = var.principal
    source_arn = "arn:aws:execute-api:${var.api_gateway_region}:${var.api_gateway_account_id}:${aws_api_gateway_rest_api.seerGateway.id}/*/${aws_api_gateway_method.post_method.http_method}${aws_api_gateway_resource.post_resource.path}"
}

resource "aws_lambda_permission" "init_api" {
    statement_id = var.statement_id
    action = var.action
    function_name = var.init_function_name
    principal = var.principal
    source_arn = "arn:aws:execute-api:${var.api_gateway_region}:${var.api_gateway_account_id}:${aws_api_gateway_rest_api.seerGateway.id}/*/${aws_api_gateway_method.init_method.http_method}${aws_api_gateway_resource.init_resource.path}"
}

resource "aws_lambda_permission" "get_api" {
    statement_id = var.statement_id
    action = var.action
    function_name = var.get_function_name
    principal = var.principal
    source_arn = "arn:aws:execute-api:${var.api_gateway_region}:${var.api_gateway_account_id}:${aws_api_gateway_rest_api.seerGateway.id}/*/${aws_api_gateway_method.get_method.http_method}${aws_api_gateway_resource.get_resource.path}"
}

resource "aws_api_gateway_deployment" "deployment" {
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
    depends_on = [
      aws_api_gateway_method.post_method,
      aws_api_gateway_method.init_method,
      aws_api_gateway_method.get_method,
      aws_api_gateway_integration.integration,
      aws_api_gateway_integration.init_integration,
      aws_api_gateway_integration.get_integration
    ]
    triggers = {
      "redeployment" = sha1(jsonencode([
        aws_api_gateway_resource.post_resource.id,
        aws_api_gateway_integration.integration.id,
        aws_api_gateway_method.post_method.id,
        aws_api_gateway_resource.init_resource.id,
        aws_api_gateway_resource.get_resource.id,
        aws_api_gateway_integration.init_integration,
        aws_api_gateway_integration.get_integration,
        aws_api_gateway_method.init_method.id,
        aws_api_gateway_method.get_method.id,
      ]))
    }
    lifecycle {
        create_before_destroy = true
    }
}

resource "aws_api_gateway_stage" "prod" {
    stage_name = var.stage_name
    deployment_id = aws_api_gateway_deployment.deployment.id
    rest_api_id = aws_api_gateway_rest_api.seerGateway.id
}
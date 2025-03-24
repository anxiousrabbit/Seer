output "api_post_url" {
    value = "${aws_api_gateway_deployment.deployment.invoke_url}${aws_api_gateway_stage.prod.stage_name}${aws_api_gateway_resource.post_resource.path}"
}

output "api_init_url" {
    value = "${aws_api_gateway_deployment.deployment.invoke_url}${aws_api_gateway_stage.prod.stage_name}${aws_api_gateway_resource.init_resource.path}"
}

output "api_get_url" {
    value = "${aws_api_gateway_deployment.deployment.invoke_url}${aws_api_gateway_stage.prod.stage_name}${aws_api_gateway_resource.get_resource.path}"
}